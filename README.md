# Cross-Platform Hinglish Mental-Health Detection

Detecting signs of mental-health distress in **Hinglish** (mixed Hindi–English) social-media text,
across **three platforms** (YouTube, Reddit, Twitter/X), and explaining *why* the model makes each
decision.

This repository documents the methodology — from collecting the data all the way to validating the
final model — and ships the demo, the baseline and figure scripts, the word lists, and all result
files. The **16 pipeline notebooks** that implement each step are **not published**; they are
available from the authors on request (see §6).

> ⚕️ **Important:** This is a **research screening aid, not a diagnostic tool.** It produces risk
> *signals* to help a human prioritise attention. It must never be used to make automated decisions
> about a person. Every flagged case requires review by a qualified human.

---

## 1. The problem in one paragraph

People in India often express distress in **code-mixed Hinglish** ("akelapan ho raha hai", "bahut
pareshan hoon"), and they post across **different platforms** with very different writing styles.
Most models are trained and tested on a single platform in a single language, so they look good in
the lab but fail in the real world. This project builds a model that (a) understands code-mixed
multilingual text, (b) is **trained on one platform and tested on completely different ones** to
measure real-world generalisation, (c) tracks how a person's language **changes over time**, and
(d) **explains its predictions** so a human can trust or challenge them.

### The four risk levels (tiers)

| Tier | Name | Meaning |
|:----:|------|---------|
| 0 | Neutral | No distress signal |
| 1 | Stress | Everyday stress / mild distress |
| 2 | Moderate | Clear, sustained distress |
| 3 | Crisis | Severe distress / self-harm signals |

---

## 2. How the pipeline fits together

The work follows **five objectives**, implemented by **16 notebooks** (available from the authors on request, see §6).
The table lists what each one does.

| # | Notebook | What it does |
|:-:|----------|--------------|
| **Objective 1 — Build the dataset** | | |
| 01 | `01_data_collection` | Collect user posts (with timestamps) from YouTube, Reddit, Twitter/X |
| 02 | `02_automated_labeling` | Assign a tier to each post automatically (no human labelling) |
| 03 | `03_data_augmentation` | Create extra examples for the rare, important Crisis class |
| 04 | `04_temporal_features` | Turn timestamps into features and build per-user post histories |
| **Objective 2 — Understand the language** | | |
| 05 | `05_preprocessing` | Clean text, handle emojis/negation, transliterate Hinglish to Devanagari |
| 06 | `06_text_representation` | Turn text into numbers (embeddings) with MuRIL; validate them |
| 07 | `07_backbone_benchmark` | Compare language models (MuRIL vs XLM-R vs IndicBERT) |
| **Objective 3 — Build the model** | | |
| 08 | `08_linguistic_drift` | Measure how a user's language drifts over time |
| 09 | `09_model_architecture` | The main model: dual-encoder + capsule network + attention fusion |
| 10 | `10_ablation_studies` | Remove each part to prove it earns its place |
| **Objective 4 — Explain the model** | | |
| 11 | `11_local_explainability` | Explain single predictions (SHAP + LIME + Integrated Gradients) |
| 12 | `12_global_explainability` | Find the model's overall trigger words; sanity-check them |
| 13 | `13_ethics_accountability` | Fairness across platforms, privacy, and the screening-aid disclaimer |
| **Objective 5 — Validate everything** | | |
| 14 | `14_statistical_validation` | Multiple random seeds, confidence intervals, significance tests |
| 15 | `15_classification_generalization` | Per-class scores + the cross-platform generalisation result |
| 16 | `16_early_detection` | How early can the model flag an at-risk user? (ERDE) |

A plain-English walk-through of the whole methodology is in [`docs/methodology.md`](docs/methodology.md),
and the measured results are in [`docs/results.md`](docs/results.md).

---

## 3. Folder structure

```
hinglish-mental-health-detection/
├── README.md            ← you are here
├── requirements.txt     ← Python packages to install
├── .env.example         ← template for your API keys (copy to .env)
├── notebooks/           ← README only; the 16 pipeline notebooks are available on request (§6)
├── scripts/
│   └── run_pipeline.py  ← re-executes notebooks 02–16 end-to-end (see §4)
├── demo/                ← interactive Streamlit app — try the trained model live (see §4)
├── resources/           ← word lists & lookup tables the notebooks use
├── data/
│   ├── release/          ← de-identified labels for all 4,614 posts (see §6)
│   ├── stage3_model/     ← model config + classification report (checkpoint on request, see §6)
│   └── sample/           ← a tiny synthetic example showing the input format
├── experiments/          ← BGE-M3 + XGBoost baseline and training-curve logging (paper baselines)
├── figures/              ← scripts that draw the paper's figures
└── docs/                 ← methodology & results write-ups
```

---

## 4. Quick start

```bash
# 1. Create a fresh virtual environment (Python 3.10+) and activate it
python -m venv .venv
# Windows:        .venv\Scripts\activate
# macOS / Linux:  source .venv/bin/activate

# 2. Install the dependencies
pip install -r requirements.txt
#    …or, to reproduce the exact versions used to produce the results:
#    pip install -r requirements.lock.txt

# 3. (Only if you want to collect fresh data) add your API keys
cp .env.example .env      # then edit .env with your own keys
```

The pipeline notebooks (and `scripts/run_pipeline.py`, which re-executes notebooks 02–16 in order)
need the notebooks themselves, which are available from the authors on request (see §6). The
results summary in [`docs/results.md`](docs/results.md) can be read
without running anything.

### Try the trained model live

```bash
streamlit run demo/app.py
```

Needs the trained checkpoint `data/stage3_model/model_state.pt` (seed 42, produced by notebook 09).
It is **not shipped** because it was trained on real users' posts: request it from the authors (see §6). No retraining happens in the app. With the checkpoint in place, it lets you type a post in English, Hindi, or Hinglish and see, live: the predicted tier,
a word-by-word Integrated Gradients explanation, a cross-check against the clinical lexicon, and a
breakdown of how much the text vs. the emotion signal vs. the time of posting actually drove that
specific prediction.

---

## 5. Headline results

The model is trained on **YouTube** and tested on **completely unseen Reddit + Twitter/X** data
(the hardest, most realistic setup). Corpus: **4,614 posts** (1,846 YouTube train; 2,768 Reddit + X test).
Scores are the **mean of 5 random seeds** (42, 2023, 2024, 0, 7) with 95% confidence intervals,
as reported in the paper:

| Metric | Score (5-seed mean) | 95% CI |
|--------|:-----:|:-----:|
| Macro-F1 (cross-platform test) | **0.465** | 0.435 – 0.495 |
| MCC (cross-platform test) | **0.429** | 0.385 – 0.473 |
| ROC-AUC | **0.827** | 0.817 – 0.837 |
| Crisis (Tier-3) recall | **0.100** | 0.044 – 0.156 |
| In-platform validation (5-fold) | **0.834** macro-F1 | |

Per-seed numbers and significance tests are in [`docs/results.md`](docs/results.md); the full result
files are available from the authors on request.

The explainability checks confirm the model keys on **meaningful distress words** (e.g. *pareshan*,
*akelapan*), not on surface cues — and it stays accurate **within each language** (English, Hinglish,
Hindi), so it is genuinely multilingual, not just a language detector. Full numbers in
[`docs/results.md`](docs/results.md); the live demo also reads these numbers directly out of
`data/stage3_model/classification_report.json`, so they always match whatever is currently on disk.

**An honest limitation surfaced by building the interactive demo:** for a number of inputs, the
trained model's text/capsule pathway contributes close to 0% of the signal behind its prediction —
the emotion-embedding and time-of-posting streams end up dominating almost regardless of the words
typed. The demo measures and discloses this per-prediction rather than hiding it.

---

## 6. Ethics & data

- **Screening aid, not a diagnosis.**
- **No post text, links or user identifiers are distributed.** The corpus is real users' posts about
  mental health. Publishing the text, or anything that points back to a post (URL, platform post ID,
  exact timestamp, user hash), would let a reader find the person and see their mental-health label.
  Instead, [`data/release/corpus_ids_labels.csv`](data/release/corpus_ids_labels.csv) lists every post
  used in the paper with only an internal random `record_id`, platform, train/test split, posting
  month, language and tier label, enough to check the class balance, splits and per-platform counts
  reported in the paper. `scripts/export_release_ids.py` shows how this file was made.
- **Trained model.** The checkpoint is not published, because a model trained on real posts can
  memorise parts of them. Its configuration and test-set report are in `data/stage3_model/`.
- **Privacy.** Usernames are never stored — they are replaced by a salted, one-way hash.
- **Credentials** live only in a local `.env` file, which is never committed.
- The pseudonymized corpus, the post-level identifiers, the pipeline notebooks and the trained
  checkpoint are available from
  the authors on reasonable request for research use, subject to ethics approval and a data-use agreement.

## 7. Citation

If you use this code or the released labels, please cite the paper:

> *An Explainable Multi-Signal Framework for Early Detection of Mental-Health Crisis in Hindi–English
> Code-Mixed Social Media Posts.* (Under review.)

---

## 8. License

Released under the [MIT License](LICENSE).
