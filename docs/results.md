# Results

> **Evaluation setup.** The model is trained on **YouTube** and tested on **completely unseen Reddit +
> Twitter** posts. This cross-platform setup is deliberately hard — it measures real-world generalisation,
> not lab performance.

---

## 1. The dataset

| | |
|---|---|
| Total posts | **4,614** (1,846 YouTube train · 2,768 Reddit + X test) |
| Platforms | YouTube (train) · Reddit + Twitter (test) |
| Languages | English 67.6% · **Hinglish 30.2%** · Hindi 2.2% |
| Risk tiers | Neutral · Stress · Moderate · Crisis |
| Automatic-labelling agreement (Cohen's κ) | **0.82** ("almost perfect") |

The corpus is genuinely **multilingual**, and — importantly — Hinglish is the *majority* language in the
distress tiers (84% of Stress posts), reflecting that users code-switch into Hindi/Hinglish when expressing
distress.

---

## 2. Main model — cross-platform performance

| Metric | Score (5-seed mean) |
|--------|:-----:|
| Macro-F1 | **0.465** |
| MCC (Matthews correlation) | **0.429** |
| ROC-AUC | **0.827** |
| In-platform reference (5-fold CV) | **0.83** macro-F1 |

Per-tier F1 (5-seed mean): Neutral 0.79 · Stress 0.49 · Moderate 0.47 · Crisis 0.10.

**Statistical robustness (notebook 14).** Across 5 random seeds the scores are stable (tight confidence
intervals), and the full model **significantly beats all five baselines** (majority-class, a frozen MuRIL probe, a
text-only version, BGE-M3 + XGBoost on text, and BGE-M3 + XGBoost on text + signals) on **all 10
comparisons** (macro-F1 and MCC; paired t-test, Benjamini–Hochberg q = 0.05). The BGE-M3 baselines
are in [`../experiments/bge_m3_baseline/`](../experiments/bge_m3_baseline/).

---

## 3. Does the model truly understand the language? (Objective 4)

- **Faithful explanations.** The SHAP / LIME / Integrated-Gradients explanations are verified to reflect the
  real model exactly.
- **Sensible triggers.** The model's top words for distress tiers are genuine distress terms — e.g.
  *pareshan* (troubled) for Stress, *akelapan* (loneliness) for Moderate — and the negative control is clean
  (Neutral posts trigger no distress words).
- **It is not just a language detector.** Broken down by language, the model keeps **positive,
  chance-corrected accuracy within *every* language** (English, Hinglish, Hindi). A model that merely
  detected "Hinglish = distress" would collapse here; instead it discriminates risk *within* each language,
  confirming it keys on **meaning, not script**.

---

## 4. Fairness, privacy, ethics (notebook 13)

- **Per-platform fairness:** the macro-F1 gap between platforms is small, and both platforms reach positive
  MCC.
- **Privacy:** usernames are never stored — only a one-way salted hash.
- **Framing:** a **screening aid, not a diagnosis**; Crisis recall is modest, so the system is explicitly
  *not* suitable for crisis triage on its own.

---

## 5. Early detection (notebook 16)

On real user histories (49 users with enough posts, 17 genuinely at-risk), the model flags at-risk users
**early in their history** with solid accuracy (precision ≈ 0.81, recall ≈ 0.76; ERDE₅ ≈ 0.13). It typically
raises an alert at the first clearly-distressed post.

---

## 6. Honest limitations

Good science states what *doesn't* work:

1. **Augmentation can hurt cross-platform transfer.** Training on the original data alone generalises *better*
   than training on the augmented set. Synthetic examples help balance the classes but drift away from the
   real test distribution — so the augmentation strategy is reported as an ablation finding, not a default.
2. **A multi-week "lead time" could not be measured.** Most collected user histories are short, same-session
   bursts, so the model alerts on the first distressed post rather than days/weeks ahead. Measuring a true
   lead time needs users with posts spread over longer periods.
3. **Crisis precision is low.** The model catches a fair share of Crisis cases but also over-flags — another
   reason it is a *screening aid* requiring human review, not an automated decision-maker.

---

## Figures

Key figures are in [`../results/figures/`](../results/figures/), including the confusion matrix
(`confusion_consolidated.png`), per-tier triggers (`global_triggers_*.png`), the cross-method explanation
agreement (`method_agreement.png`), per-platform fairness (`platform_parity.png`), the seed confidence
intervals (`seed_ci.png`), and the early-detection curve (`erde_curve.png`).
