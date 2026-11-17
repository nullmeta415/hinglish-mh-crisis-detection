"""BGE-M3 + XGBoost baseline on the v1 initial-study split (train YouTube, frozen test Reddit + X).

Two variants, both scored on the same frozen test set as the initial model:
  A  bge_text    : BGE-M3 dense embedding of the post only
  B  bge_signals : BGE-M3 + the initial model's frozen XLM-EMO embedding + its six timestamp features (masked for synthetic rows)

Usage:
  python run_bge_m3_xgb.py <v1_repo_dir> <out_dir>
"""
import json, sys, time
from pathlib import Path

import numpy as np
import torch
from scipy import stats
from sklearn.metrics import (accuracy_score, f1_score, matthews_corrcoef, precision_recall_fscore_support,
                             roc_auc_score, confusion_matrix)
from transformers import AutoModel, AutoTokenizer
from xgboost import XGBClassifier

V1, OUT = Path(sys.argv[1]), Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)
DATA = V1 / "data"
SEEDS = [42, 2023, 2024, 0, 7]                       # same seeds as the initial model
TIERS = ["Neutral", "Stress", "Moderate", "Crisis"]
TEMP_FEATS = ["month_t", "day_t", "hour_t", "weekday_t", "is_working_hour_t", "is_weekend_t"]
MAX_TOKENS, BATCH = 128, 16                           # initial-model token cap
XGB = dict(n_estimators=400, max_depth=6, learning_rate=0.05, subsample=0.9, colsample_bytree=0.8,
           min_child_weight=2, objective="multi:softprob", tree_method="hist", n_jobs=16)
torch.set_num_threads(16)


def load_jsonl(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


train = load_jsonl(DATA / "stage2_semantic/corpus_preprocessed_train.jsonl")
test = load_jsonl(DATA / "stage2_semantic/corpus_preprocessed_test.jsonl")
assert {r["platform"] for r in train} <= {"youtube", "synthetic"} and {r["platform"] for r in test} <= {"reddit", "twitter"}
y_tr = np.array([int(r["tier"]) for r in train]); y_te = np.array([int(r["tier"]) for r in test])
plat_te = np.array([r["platform"] for r in test])


def texts(rows):  # same text field as the initial-model encoders
    return [str(r.get("text_muril") or r.get("post_text_clean") or "") or "[UNK]" for r in rows]


# ---------- 1. BGE-M3 dense embeddings (CLS pooling, L2-normalised), cached ----------
cache = OUT / "bge_m3_embeddings.npz"
if cache.exists():
    z = np.load(cache); E_tr, E_te = z["train"], z["test"]; embed_s = float(z["seconds"])
else:
    tok = AutoTokenizer.from_pretrained("BAAI/bge-m3")
    model = AutoModel.from_pretrained("BAAI/bge-m3").eval()

    @torch.no_grad()
    def embed(tx):
        out = []
        for i in range(0, len(tx), BATCH):
            enc = tok(tx[i:i + BATCH], padding=True, truncation=True, max_length=MAX_TOKENS, return_tensors="pt")
            cls = model(**enc).last_hidden_state[:, 0]
            out.append(torch.nn.functional.normalize(cls, dim=-1).numpy())
            if (i // BATCH) % 25 == 0: print(f"  embedded {i + len(tx[i:i + BATCH])}/{len(tx)}", flush=True)
        return np.vstack(out).astype(np.float32)

    t0 = time.time()
    E_tr = embed(texts(train)); E_te = embed(texts(test))
    embed_s = time.time() - t0
    np.savez(cache, train=E_tr, test=E_te, seconds=embed_s)
print(f"embeddings {E_tr.shape} {E_te.shape}, {embed_s:.0f} s")


# ---------- 2. initial-model auxiliary signals (frozen XLM-EMO + masked timestamp features) ----------
def temporal(split, rows):
    by_id = {r["record_id"]: r for r in load_jsonl(DATA / f"stage1_temporal/temporal_features_{split}.jsonl")}
    F, M = [], []
    for r in rows:
        t = by_id[r["record_id"]]; m = float(t.get("temporal_mask", 1))
        F.append([float(t[k]) * m for k in TEMP_FEATS]); M.append([m])
    return np.hstack([np.array(F), np.array(M)]).astype(np.float32)


EMO_tr = np.load(DATA / "stage3_model/emo_embeddings_train.npy"); EMO_te = np.load(DATA / "stage3_model/emo_embeddings_test.npy")
VARIANTS = {
    "bge_text": (E_tr, E_te),
    "bge_signals": (np.hstack([E_tr, EMO_tr, temporal("train", train)]), np.hstack([E_te, EMO_te, temporal("test", test)])),
}

# class weights as in the initial model: N / (4 * n_c)
counts = np.bincount(y_tr, minlength=4).astype(float)
sw = (counts.sum() / (4.0 * counts))[y_tr]


def metrics(y, pred, prob):
    P, R, F, S = precision_recall_fscore_support(y, pred, labels=[0, 1, 2, 3], zero_division=0)
    return {"accuracy": accuracy_score(y, pred), "macro_f1": f1_score(y, pred, average="macro", labels=[0, 1, 2, 3]),
            "mcc": matthews_corrcoef(y, pred),
            "roc_auc": roc_auc_score(y, prob, multi_class="ovr", average="macro", labels=[0, 1, 2, 3]),
            "per_tier": {t: {"P": P[i], "R": R[i], "F1": F[i], "support": int(S[i])} for i, t in enumerate(TIERS)}}


def ci(v):
    v = np.asarray(v, float); m, sd = v.mean(), v.std(ddof=1)
    h = stats.t.ppf(0.975, len(v) - 1) * sd / np.sqrt(len(v))
    return {"mean": m, "sd": sd, "ci95_lo": m - h, "ci95_hi": m + h}


# ---------- 3. train / score per seed ----------
results = {}
for name, (Xtr, Xte) in VARIANTS.items():
    runs = []
    for seed in SEEDS:
        clf = XGBClassifier(**XGB, random_state=seed)
        t0 = time.time(); clf.fit(Xtr, y_tr, sample_weight=sw); fit_s = time.time() - t0
        t0 = time.time(); prob = clf.predict_proba(Xte); inf_ms = (time.time() - t0) * 1000 / len(Xte)
        pred = prob.argmax(1)
        m = metrics(y_te, pred, prob)
        m["per_platform"] = {p: metrics(y_te[plat_te == p], pred[plat_te == p], prob[plat_te == p]) for p in ["reddit", "twitter"]}
        m.update(seed=seed, fit_seconds=fit_s, infer_ms_per_post=inf_ms, n_features=int(Xtr.shape[1]))
        if seed == 42: m["confusion"] = confusion_matrix(y_te, pred, labels=[0, 1, 2, 3]).tolist()
        runs.append(m)
        print(f"{name} seed {seed}: acc {m['accuracy']:.3f} mF1 {m['macro_f1']:.3f} MCC {m['mcc']:.3f} "
              f"AUC {m['roc_auc']:.3f} CrisisR {m['per_tier']['Crisis']['R']:.3f} fit {fit_s:.1f}s", flush=True)
    summ = {k: ci([r[k] for r in runs]) for k in ["accuracy", "macro_f1", "mcc", "roc_auc"]}
    summ["per_tier"] = {t: {s: ci([r["per_tier"][t][s] for r in runs]) for s in ["P", "R", "F1"]} for t in TIERS}
    summ["per_platform_macro_f1"] = {p: ci([r["per_platform"][p]["macro_f1"] for r in runs]) for p in ["reddit", "twitter"]}
    summ["fit_seconds"] = ci([r["fit_seconds"] for r in runs]); summ["infer_ms_per_post"] = ci([r["infer_ms_per_post"] for r in runs])
    results[name] = {"per_seed": runs, "summary": summ}

# ---------- 4. paired tests vs the initial model, BH over the extended family ----------
rep = V1 / "results/reports"
full = json.load(open(rep / "14_seed_metrics.json"))["models"]["full"]["per_seed"]
old = json.load(open(rep / "14_significance.json"))["comparisons"]
family = [{"metric": c["metric"], "baseline": c["baseline"], "p_raw": c["p_raw"]} for c in old]
for name in VARIANTS:
    for met in ["macro_f1", "mcc"]:
        a = np.array([r[met] for r in full]); b = np.array([r[met] for r in results[name]["per_seed"]])
        t, p = stats.ttest_rel(a, b)
        d = (a - b).mean() / (a - b).std(ddof=1)
        family.append({"metric": met, "baseline": name, "full_mean": a.mean(), "base_mean": b.mean(),
                       "delta_mean": (a - b).mean(), "t": t, "p_raw": p, "cohens_d": d})
p_bh = stats.false_discovery_control([f["p_raw"] for f in family], method="bh")
for f, q in zip(family, p_bh): f["p_bh"] = q; f["significant_q05"] = bool(q < 0.05)

report = {"setup": {"train": "YouTube real + synthetic (1,971)", "test": "frozen Reddit + X (2,768)",
                    "encoder": "BAAI/bge-m3 dense CLS, L2-normalised, 128 tokens, CPU", "xgboost": XGB,
                    "class_weights": "N/(4 n_c)", "seeds": SEEDS, "embed_seconds_all_4739_posts": embed_s,
                    "torch": torch.__version__},
          "results": results, "significance_family": family}
(OUT / "bge_m3_xgb_results.json").write_text(json.dumps(report, indent=2, default=float))
for f in family:
    print(f"{f['metric']:8s} vs {f['baseline']:12s} p_raw {f['p_raw']:.5f} p_BH {f['p_bh']:.5f} sig {f['significant_q05']}")
