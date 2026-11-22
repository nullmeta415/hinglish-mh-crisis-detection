# Methodology

The implementation of every step lives in a matching notebook; the notebooks are available from the authors on request (see §6 of the top-level README).

---

## The goal

Detect signs of mental-health distress in **Hinglish** (mixed Hindi–English) social-media text, in a way
that (a) works across **different platforms**, (b) accounts for how a person's language **changes over
time**, and (c) can **explain its decisions** to a human reviewer.

Each post is sorted into one of four **risk tiers**: 0 Neutral · 1 Stress · 2 Moderate · 3 Crisis.

The work is organised into **five objectives**, each a small group of notebooks.

---

## Objective 1 — Build the dataset (notebooks 01–04)

**Collect → label → balance → add time features.**

- **Collection (01).** We gather user posts from **YouTube, Reddit, and Twitter/X**, keeping each post's
  author and timestamp. Every post is normalised into the same set of fields, and each username is
  replaced by a **one-way salted hash**, so we keep "same user" links without ever storing real names.
- **Automatic labelling (02).** Hand-labelling is slow and needs experts, so we label automatically with
  **two independent methods** — a curated word-list and a language model — and measure their agreement
  (Cohen's kappa) as a quality score. No human annotators are used.
- **Augmentation (03).** The **Crisis** class is rare. We carefully generate extra Crisis-style examples
  for *training only*, and keep the **test set 100% real** so evaluation is never inflated.
- **Time features (04).** Timestamps become features (time of day, day of week), and posts are grouped
  into **per-user histories** for the later drift analysis.

**Why this design:** platform diversity + preserved author/time + automatic labelling make the dataset
realistic and reproducible without a costly annotation team.

---

## Objective 2 — Understand the language (notebooks 05–07)

**Clean text → turn it into numbers → pick the best language model.**

- **Preprocessing (05).** Social text is messy. We normalise characters, handle emojis and links, tag
  negations, and **transliterate** known Hinglish words into Devanagari (Hindi script), which the language
  model reads more reliably.
- **Representation (06).** We convert each post into a numeric **embedding** using **MuRIL**, a model built
  for Indian languages. We validate the embeddings by checking that matching Hindi/English phrases land
  close together, and by correlating distress words with the tiers.
- **Backbone comparison (07, 07b).** We compare **MuRIL vs XLM-R vs IndicBERT**, both as fixed feature
  extractors and fine-tuned, and pick the strongest with evidence.

**Why this design:** a multilingual backbone is essential because the data is genuinely multilingual
(English, Hinglish, and Hindi all appear), and transliteration narrows the gap between the two scripts.

---

## Objective 3 — Build the model (notebooks 08–10)

**Measure drift → assemble the model → prove every part matters.**

- **Linguistic drift (08).** For each user with a history, we measure how their language **shifts over
  time** using a scale-free cosine distance ("drift velocity").
- **The model (09).** The detector combines:
  - **two frozen encoders** — one for meaning (MuRIL), one for emotion;
  - a **capsule network** that captures structured patterns in the text;
  - an **attention step** that decides, per post, how much to trust the text vs. the timing signal;
  - a loss function tuned for the rare classes.

  It is **trained on YouTube only** and tested on **unseen Reddit + Twitter** — the realistic
  cross-platform setup.
- **Ablations (10).** We switch each component on/off to confirm it earns its place, run a small
  hyper-parameter search, and record speed and size.

**Why this design:** combining meaning + emotion + timing reflects how people actually express distress;
the ablations keep the model honest by removing anything that does not help.

---

## Objective 4 — Explain the model (notebooks 11–13)

**Explain single predictions → find global triggers → check ethics.**

- **Local explanations (11).** For individual posts we show which words drove the decision, using **three
  independent methods** (SHAP, LIME, Integrated Gradients), and we verify the explanations faithfully match
  the real model.
- **Global triggers (12).** Across all posts we find the model's most influential words per tier and
  cross-check them against a clinical word-list and statistical correlations — confirming the model keys on
  genuine distress words (e.g. *pareshan*, *akelapan*), not surface noise.
- **Ethics (13).** We check fairness across platforms, confirm privacy (no usernames stored), and state the
  responsible-use framing: a **screening aid, never a diagnosis**.

**Why this design:** a mental-health tool must be transparent and accountable; explanations let a human
trust or challenge each decision.

---

## Objective 5 — Validate everything (notebooks 14–16)

**Prove it is stable → report full scores + generalisation → measure early detection.**

- **Statistical validation (14).** We retrain with several random seeds, report **confidence intervals**,
  and run **significance tests** (with multiple-comparison correction) against simple baselines.
- **Classification & generalisation (15).** Full per-tier scores, plus the headline **cross-platform
  generalisation** result — how a model trained on one platform performs on completely different ones.
- **Early detection (16).** Using the standard **ERDE** metric on real user histories, we measure how
  *early* the model can flag an at-risk user. The notebook closes with the overall validity summary.

**Why this design:** a single accuracy number can mislead; confidence intervals, significance tests,
cross-platform testing, and early-detection timing together give an honest picture of real-world value.

---

## Responsible-use note

This system is a **research screening aid**, designed to help a human prioritise attention — it is **not a
diagnostic tool** and must never drive automated decisions about a person. Every flagged case requires
review by a qualified human. See notebook 13 for the full disclaimer and fairness analysis.
