# Cross-Platform Hinglish Mental-Health Detection

Detecting signs of mental-health distress in **Hinglish** (mixed Hindi–English) social-media text,
across **three platforms** (YouTube, Reddit, Twitter/X), and explaining *why* the model makes each
decision.

This repository contains the full, runnable methodology — from collecting the data all the way to
validating the final model — split into **16 short, well-commented notebooks** that you can read in
order, top to bottom.

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

The work follows **five objectives**, implemented by the **16 notebooks** in [`notebooks/`](notebooks/).
Read them in numerical order — each one explains what it does, why, and shows its results.

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
├── notebooks/           ← the 16 pipeline notebooks (read these in order)
├── scripts/
│   └── run_pipeline.py  ← re-executes notebooks 02–16 end-to-end (see §4)
├── demo/                ← interactive Streamlit app — try the trained model live (see §4)
├── resources/           ← word lists & lookup tables the notebooks use
├── data/
│   ├── release/          ← post IDs + labels for all 4,614 posts (no post text, see §6)
│   ├── stage3_model/     ← trained checkpoint + config used by the demo
│   └── sample/           ← a tiny synthetic example showing the input format
├── experiments/          ← BGE-M3 + XGBoost baseline and training-curve logging (paper baselines)
├── figures/              ← scripts that draw the paper's figures
├── results/              ← figures and result files produced by the notebooks
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

# 4. Open the notebooks and read/run them in order
jupyter notebook notebooks/
```

Every notebook in [`notebooks/`](notebooks/) is committed **with real, executed output** — so you
do not need to run anything to read through the explanations, code, and results. If you do want to
reproduce them yourself, `scripts/run_pipeline.py` re-executes notebooks 02–16 end-to-end in order
(notebook 01 is excluded — it calls live platform APIs and needs real credentials, see step 3 above):

```bash
python scripts/run_pipeline.py                       # full pipeline, in order
python scripts/run_pipeline.py 09_model_architecture  # or resume from any single notebook
```

### Try the trained model live

```bash
`streamlit run demo/app.py`
```

Loads the trained checkpoint shipped in this repository (`data/stage3_model/model_state.pt`, 3 MB,
seed 42, produced by notebook 09 — no retraining happens in the app) and lets you type a post in English, Hindi, or Hinglish and see, live: the predicted tier,
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

Per-seed numbers: [`results/reports/14_seed_metrics.json`](results/reports/14_seed_metrics.json);
significance tests: [`results/reports/14_significance.json`](results/reports/14_significance.json).

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
- **Post text is not distributed.** The corpus is real users' posts about mental health, so releasing
  the text would breach their privacy and the platforms' terms. Instead,
  [`data/release/corpus_ids_labels.csv`](data/release/corpus_ids_labels.csv) lists every post used in
  the paper with its platform, train/test split, native ID and URL, timestamp, pseudonymous user
  hash, language, and tier label. Reddit rows carry the comment ID and permalink and X rows the
  status ID, so they can be re-collected directly. YouTube comment IDs were not stored at
  collection time, so YouTube rows carry the video ID and the comment's exact `timestamp`, which
  identifies the comment within that video's comment thread. Posts deleted since collection
  cannot be recovered. `scripts/export_release_ids.py` shows how this file was made.
  Notebook 01 re-collects posts; notebooks 02–16 then run on the re-collected corpus.
- **Privacy.** Usernames are never stored — they are replaced by a salted, one-way hash. Example
  outputs inside the notebooks that quoted real posts have been redacted.
- **Credentials** live only in a local `.env` file, which is never committed.
- The full pseudonymized corpus is available from the authors on reasonable request for
  research use, subject to ethics approval.

## 7. License

Released under the [MIT License](LICENSE).
