# -*- coding: utf-8 -*-
"""Live inference for DriftCapsNet, reusing the exact preprocessing (notebook 05) and
architecture (notebook 09) code already validated and executed in this repo's pipeline.
Loads the trained checkpoint from data/stage3_model/ -- no retraining happens here.
"""
import json
import math
import re
import unicodedata
from pathlib import Path
from collections import Counter

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel

ROOT = Path(__file__).resolve().parent.parent
MODEL_DIR = ROOT / "data" / "stage3_model"
RESOURCES = ROOT / "resources"

TIER_NAMES = {0: "Neutral", 1: "Stress", 2: "Moderate", 3: "Crisis"}
TIER_COLORS = {0: "#3a9d3a", 1: "#c9a227", 2: "#e07b28", 3: "#c0392b"}

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# ============================================================
# Preprocessing (identical logic to notebooks/05_preprocessing.ipynb)
# ============================================================
TRANSLIT = json.loads((RESOURCES / "translit_map_hi_v1.json").read_text(encoding="utf-8"))
TR_PHRASES = sorted(TRANSLIT["phrases"].items(), key=lambda kv: -len(kv[0].split()))
TR_WORDS = TRANSLIT["words"]

URL_RE = re.compile(r"https?://\S+|www\.\S+")
USER_RE = re.compile(r"@\w+")
HASHTAG_RE = re.compile(r"#\w+")
WS_RE = re.compile(r"\s+")

EMOJI_SENT = {}
for ch in "😭😢😞😔😟😥😪😓💔🥀😩😫":
    EMOJI_SENT[ch] = "<EMO_SAD>"
for ch in "😡😠🤬😤":
    EMOJI_SENT[ch] = "<EMO_ANGRY>"
for ch in "😨😰😱😬":
    EMOJI_SENT[ch] = "<EMO_FEAR>"
for ch in "😀😃😄😁😊🙂😍🥰😂🤣❤️":
    EMOJI_SENT[ch] = "<EMO_HAPPY>"


def nfc_clean(t):
    t = unicodedata.normalize("NFC", str(t or ""))
    t = t.replace("‍", "").replace("️", "")
    return WS_RE.sub(" ", t).strip()


def apply_placeholders(t):
    t = URL_RE.sub(" <URL> ", t)
    t = USER_RE.sub(" <USER> ", t)
    t = HASHTAG_RE.sub(" <HASHTAG> ", t)
    return WS_RE.sub(" ", t).strip()


def map_emoji(t):
    out = []
    for ch in t:
        out.append(" " + EMOJI_SENT[ch] + " " if ch in EMOJI_SENT else ch)
    return WS_RE.sub(" ", "".join(out)).strip()


def transliterate(t):
    s = t
    for ph, dev in TR_PHRASES:
        pat = re.compile(r"\b" + re.escape(ph) + r"\b", re.IGNORECASE)
        s = pat.sub(dev, s)
    out = []
    for tok in s.split():
        m = re.match(r"^([^\w<]*)([\w']+)([^\w>]*)$", tok)
        if m and m.group(2).lower() in TR_WORDS:
            out.append(m.group(1) + TR_WORDS[m.group(2).lower()] + m.group(3))
        else:
            out.append(tok)
    return WS_RE.sub(" ", " ".join(out)).strip()


def preprocess_for_muril(raw_text):
    """Same chain as notebook 05: NFC -> placeholders -> emoji -> transliteration."""
    c = nfc_clean(raw_text)
    c = apply_placeholders(c)
    c = map_emoji(c)
    muril_text = transliterate(c)
    return muril_text


# ============================================================
# Architecture (identical to notebooks/09_model_architecture.ipynb)
# ============================================================
CONFIG = json.loads((MODEL_DIR / "model_config.json").read_text(encoding="utf-8"))
PRIM_CAPS = CONFIG["prim_caps"]
PRIM_DIM = CONFIG["prim_dim"]
CLASS_DIM = CONFIG["class_dim"]
FUSION_DIM = CONFIG["fusion_dim"]
N_CLASSES = 4


def squash(s, dim=-1, eps=1e-8):
    n2 = (s * s).sum(dim=dim, keepdim=True)
    return (n2 / (1.0 + n2)) * (s / torch.sqrt(n2 + eps))


class CapsuleRouting(nn.Module):
    def __init__(self, n_in, d_in, n_out, d_out, routing="static", iters=3):
        super().__init__()
        self.n_in, self.n_out, self.routing, self.iters = n_in, n_out, routing, iters
        self.W = nn.Parameter(0.01 * torch.randn(1, n_in, n_out, d_out, d_in))
        self.b_static = nn.Parameter(torch.zeros(1, n_in, n_out))

    def forward(self, u):
        B = u.size(0)
        u_hat = torch.matmul(self.W, u.unsqueeze(2).unsqueeze(-1)).squeeze(-1)
        if self.routing == "static":
            c = torch.softmax(self.b_static, dim=2).unsqueeze(-1)
            s = (c * u_hat).sum(dim=1)
            return squash(s)
        b = torch.zeros(B, self.n_in, self.n_out, device=u.device)
        for it in range(self.iters):
            c = torch.softmax(b, dim=2).unsqueeze(-1)
            s = (c * u_hat).sum(dim=1)
            v = squash(s)
            if it < self.iters - 1:
                b = b + (u_hat * v.unsqueeze(1)).sum(-1)
        return v


class DriftCapsNet(nn.Module):
    def __init__(self, text_dim, emo_dim, temp_dim=6, d=FUSION_DIM, gate="elu", fusion="attention",
                 routing="static", dropout=0.3):
        super().__init__()
        self.gate_kind, self.fusion = gate, fusion
        self.text_proj = nn.Linear(text_dim, PRIM_CAPS * PRIM_DIM)
        self.gate_lin = nn.Linear(PRIM_CAPS * PRIM_DIM, PRIM_CAPS * PRIM_DIM)
        self.caps = CapsuleRouting(PRIM_CAPS, PRIM_DIM, N_CLASSES, CLASS_DIM, routing=routing)
        self.q_proj = nn.Linear(N_CLASSES * CLASS_DIM, d)
        self.e_proj = nn.Linear(emo_dim, d)
        self.t_proj = nn.Sequential(nn.Linear(temp_dim, 64), nn.ReLU(), nn.Linear(64, d))
        self.drop = nn.Dropout(dropout)
        self.norm = nn.LayerNorm(d)
        head_in = d if fusion in ("attention", "text_only") else 3 * d
        self.head = nn.Linear(head_in, N_CLASSES)
        self.d = d

    def gate(self, H):
        if self.gate_kind == "none":
            return H
        if self.gate_kind == "sigmoid":
            return H * torch.sigmoid(self.gate_lin(H))
        return H * (F.elu(self.gate_lin(H)) + 1.0)

    def temporal_rep(self, x_t, mask):
        return self.t_proj(x_t) * mask.unsqueeze(-1)

    def forward(self, x_text, x_emo, x_temp, mask):
        H = self.drop(F.elu(self.text_proj(x_text)))
        H_g = self.gate(H)
        U = squash(H_g.view(-1, PRIM_CAPS, PRIM_DIM))
        V = self.caps(U).reshape(x_text.size(0), -1)
        q = self.q_proj(V)
        e = self.e_proj(x_emo)
        tau = self.temporal_rep(x_temp, mask)
        if self.fusion == "attention":
            kv = torch.stack([tau, e], dim=1)
            att = torch.softmax(torch.matmul(q.unsqueeze(1), kv.transpose(1, 2)) / math.sqrt(self.d), dim=-1)
            ctx = torch.matmul(att, kv).squeeze(1)
            z = self.norm(q + ctx)
        elif self.fusion == "concat":
            z = torch.cat([q, tau, e], dim=-1)
        else:
            z = q
        return self.head(z)


# ============================================================
# Loaded once, reused across requests
# ============================================================
class DriftCapsNetPipeline:
    def __init__(self):
        self.muril_tok = AutoTokenizer.from_pretrained("google/muril-base-cased")
        self.muril_model = AutoModel.from_pretrained("google/muril-base-cased").to(DEVICE).eval()
        self.emo_tok = AutoTokenizer.from_pretrained(CONFIG["emo_model"])
        self.emo_model = AutoModel.from_pretrained(CONFIG["emo_model"]).to(DEVICE).eval()

        self.model = DriftCapsNet(
            text_dim=CONFIG["text_dim"], emo_dim=CONFIG["emo_dim"],
            gate=CONFIG["gate"], fusion=CONFIG["fusion"], routing=CONFIG["routing"],
        ).to(DEVICE)
        ckpt = MODEL_DIR / "model_state.pt"
        if not ckpt.exists():  # not shipped for privacy reasons (README §6)
            raise FileNotFoundError(f"{ckpt} not found: run notebook 09 to train it, or request it from the authors.")
        state = torch.load(ckpt, map_location=DEVICE)
        self.model.load_state_dict(state)
        self.model.eval()
        for p in list(self.muril_model.parameters()) + list(self.emo_model.parameters()) + list(self.model.parameters()):
            p.requires_grad_(False)

        lex = json.loads((RESOURCES / "lexicon_mh_v1.json").read_text(encoding="utf-8"))
        # term (lowercased) -> tier int, longest-term-first so multi-word phrases match before substrings
        self.lexicon_by_term = {}
        for tier_str, tier_obj in lex.get("tiers", {}).items():
            for term in tier_obj.get("terms", []):
                self.lexicon_by_term[term.lower()] = int(tier_str)
        self.lexicon_terms_sorted = sorted(self.lexicon_by_term, key=len, reverse=True)

    @torch.no_grad()
    def _mean_pool(self, model, tok, texts, max_len=128):
        enc = tok(texts, padding=True, truncation=True, max_length=max_len, return_tensors="pt").to(DEVICE)
        hs = model(**enc).last_hidden_state
        m = enc["attention_mask"].unsqueeze(-1).float()
        return ((hs * m).sum(1) / m.sum(1).clamp(min=1e-9)).cpu().numpy().astype(np.float32)

    def _current_temporal_features(self, dt=None):
        """dt: an optional datetime (naive or aware) representing the post's timestamp. Defaults to
        the current wall-clock time (UTC) when not given -- pass one explicitly to let a caller (e.g.
        the demo's time-of-posting field) simulate posting at a chosen date/time instead."""
        import datetime
        if dt is None:
            dt = datetime.datetime.now(datetime.timezone.utc)
        month_t = (dt.month - 1) / 11.0
        day_t = (dt.day - 1) / 30.0
        hour_t = dt.hour / 23.0
        weekday_t = dt.weekday() / 6.0
        is_working_hour_t = 1.0 if 9 <= dt.hour < 18 else 0.0
        is_weekend_t = 1.0 if dt.weekday() >= 5 else 0.0
        return np.array([[month_t, day_t, hour_t, weekday_t, is_working_hour_t, is_weekend_t]], dtype=np.float32)

    @torch.no_grad()
    def predict_raw_text(self, raw_text, dt=None):
        muril_text = preprocess_for_muril(raw_text)
        text_emb = self._mean_pool(self.muril_model, self.muril_tok, [muril_text])
        # training's texts_of() prefers text_muril over post_text_clean for BOTH backbones
        emo_emb = self._mean_pool(self.emo_model, self.emo_tok, [muril_text])
        temp = self._current_temporal_features(dt)
        mask = np.array([1.0], dtype=np.float32)

        logits = self.model(
            torch.tensor(text_emb).to(DEVICE),
            torch.tensor(emo_emb).to(DEVICE),
            torch.tensor(temp).to(DEVICE),
            torch.tensor(mask).to(DEVICE),
        )
        probs = torch.softmax(logits, dim=-1).cpu().numpy()[0]
        pred_tier = int(probs.argmax())
        return {
            "muril_text": muril_text,
            "pred_tier": pred_tier,
            "pred_label": TIER_NAMES[pred_tier],
            "probs": {TIER_NAMES[i]: float(probs[i]) for i in range(4)},
        }

    def lexicon_matches(self, raw_text):
        """Find every clinical-lexicon term (Section 3.10 / notebook 12's validated, more decisive
        explanation signal) present in the text, with its tier. Word-boundary, case-insensitive,
        longest-phrase-first -- same matching convention as the automated labeler (notebook 02)."""
        muril_text = preprocess_for_muril(raw_text)
        hay = " " + muril_text.lower() + " "
        matches = []
        covered = [False] * len(hay)
        for term in self.lexicon_terms_sorted:
            pat = re.compile(r"(?<!\w)" + re.escape(term) + r"(?!\w)")
            for m in pat.finditer(hay):
                if any(covered[m.start():m.end()]):
                    continue
                for i in range(m.start(), m.end()):
                    covered[i] = True
                matches.append({"term": term, "tier": self.lexicon_by_term[term]})
        matches.sort(key=lambda x: -x["tier"])
        return matches

    @torch.no_grad()
    def stream_contributions(self, raw_text, dt=None):
        """How much did each of the three fused signal streams (text, emotion, temporal) actually
        drive THIS prediction? Word-level attribution only explains the text stream's own internal
        behaviour; it says nothing about how much that stream mattered relative to the other two
        going into the final fusion + classification head. Computed by zeroing one stream at a time
        (holding the others at their real values) and measuring the resulting shift in the predicted
        tier's logit -- the same counterfactual-ablation idea as the project's own Section 3.3 (D1)
        ablation study, applied per-instance instead of corpus-wide.
        """
        muril_text = preprocess_for_muril(raw_text)
        text_emb = self._mean_pool(self.muril_model, self.muril_tok, [muril_text])
        emo_emb = self._mean_pool(self.emo_model, self.emo_tok, [muril_text])
        temp = self._current_temporal_features(dt)
        mask = np.array([1.0], dtype=np.float32)

        def logit(t, e, tm):
            lo = self.model(torch.tensor(t), torch.tensor(e), torch.tensor(tm), torch.tensor(mask))
            return lo.numpy()[0]

        l_full = logit(text_emb, emo_emb, temp)
        target = int(l_full.argmax())

        zero_text = np.zeros_like(text_emb)
        zero_emo = np.zeros_like(emo_emb)
        zero_temp = np.zeros_like(temp)

        d_text = abs(l_full[target] - logit(zero_text, emo_emb, temp)[target])
        d_emo = abs(l_full[target] - logit(text_emb, zero_emo, temp)[target])
        d_temp = abs(l_full[target] - logit(text_emb, emo_emb, zero_temp)[target])

        total = d_text + d_emo + d_temp
        if total < 1e-9:
            return {"Text (your words)": 0.0, "Emotion signal": 0.0, "Time of posting": 0.0}, target
        return {
            "Text (your words)": float(d_text / total),
            "Emotion signal": float(d_emo / total),
            "Time of posting": float(d_temp / total),
        }, target

    def explain_integrated_gradients(self, raw_text, target_tier=None, steps=32, dt=None):
        """Real Integrated Gradients (Sundararajan et al., 2017), word-level, zero-embedding
        baseline, 32 Riemann steps -- the exact method notebook 11 runs offline against the frozen
        TEST set, applied here live against whatever the panel types in. Unlike occluding whole
        words at the mean-pooled-embedding level (which this saturated classification head barely
        reacts to), IG differentiates through MuRIL's own token embeddings, so it reliably produces
        a signed, per-word score: positive = pushed the predicted tier's logit up, negative = pushed
        it down. Subword pieces are summed back onto their parent word.
        """
        muril_text = preprocess_for_muril(raw_text)
        words = muril_text.split()
        if not words:
            return [], None, muril_text

        base = self.predict_raw_text(raw_text, dt=dt)
        if target_tier is None:
            target_tier = base["pred_tier"]

        enc = self.muril_tok(words, is_split_into_words=True, return_tensors="pt",
                              truncation=True, max_length=128)
        input_ids = enc["input_ids"].to(DEVICE)
        attn = enc["attention_mask"].to(DEVICE)
        word_ids = enc.word_ids(0)
        emb_layer = self.muril_model.get_input_embeddings()
        with torch.no_grad():
            emb_full = emb_layer(input_ids)
        baseline = torch.zeros_like(emb_full)

        emo_single = self._mean_pool(self.emo_model, self.emo_tok, [muril_text])
        ex = torch.tensor(emo_single).to(DEVICE)
        temp = torch.tensor(self._current_temporal_features(dt)).to(DEVICE)
        mask = torch.tensor(np.array([1.0], dtype=np.float32)).to(DEVICE)

        total_grad = torch.zeros_like(emb_full)
        for step in range(1, steps + 1):
            alpha = step / steps
            emb_a = (baseline + alpha * (emb_full - baseline)).clone().requires_grad_(True)
            hs = self.muril_model(inputs_embeds=emb_a, attention_mask=attn).last_hidden_state
            m = attn.unsqueeze(-1).float()
            mvec = (hs * m).sum(1) / m.sum(1).clamp(min=1e-9)
            logits = self.model(mvec, ex, temp, mask)
            score = logits[0, target_tier]
            grad = torch.autograd.grad(score, emb_a)[0]
            total_grad = total_grad + grad.detach()
        avg_grad = total_grad / steps
        ig_tok = ((emb_full - baseline) * avg_grad).sum(-1).squeeze(0).detach().cpu().numpy()

        word_attr = np.zeros(len(words), np.float32)
        for ti, wid in enumerate(word_ids):
            if wid is not None and wid < len(words):
                word_attr[wid] += float(ig_tok[ti])

        return list(zip(words, word_attr.tolist())), target_tier, muril_text

    @torch.no_grad()
    def explain_occlusion(self, raw_text, top_k=8):
        """Leave-one-token-out occlusion: kept for reference/comparison only. This trained head is
        often saturated enough (confident, low-capacity classification head over frozen, anisotropic
        mean-pooled embeddings -- Section 3.6.2's own anisotropy finding) that single-token removal
        barely moves the softmax output. `explain_integrated_gradients` above is the primary,
        legible per-word signal shown in the UI.
        """
        muril_text = preprocess_for_muril(raw_text)
        tokens = muril_text.split()
        if len(tokens) < 2:
            return []
        base = self.predict_raw_text(raw_text)
        base_prob = base["probs"][base["pred_label"]]
        target_tier = base["pred_tier"]

        variants = []
        for i in range(len(tokens)):
            variants.append(" ".join(tokens[:i] + tokens[i + 1:]))
        text_embs = self._mean_pool(self.muril_model, self.muril_tok, variants)
        # emotion representation held constant across variants -- isolates the marginal effect of each
        # token on the TEXT/capsule pathway specifically, rather than conflating it with an emotion-embedding shift
        emo_single = self._mean_pool(self.emo_model, self.emo_tok, [muril_text])
        emo_emb = np.repeat(emo_single, len(variants), axis=0)
        temp = np.repeat(self._current_temporal_features(), len(variants), axis=0)
        mask = np.ones(len(variants), dtype=np.float32)
        logits = self.model(
            torch.tensor(text_embs).to(DEVICE),
            torch.tensor(emo_emb).to(DEVICE),
            torch.tensor(temp).to(DEVICE),
            torch.tensor(mask).to(DEVICE),
        )
        probs = torch.softmax(logits, dim=-1).cpu().numpy()[:, target_tier]
        importance = base_prob - probs  # positive = removing this token hurt the predicted tier's confidence

        scored = list(zip(tokens, importance.tolist()))
        scored.sort(key=lambda x: -x[1])
        return scored[:top_k]


_PIPELINE = None


def get_pipeline():
    global _PIPELINE
    if _PIPELINE is None:
        _PIPELINE = DriftCapsNetPipeline()
    return _PIPELINE
