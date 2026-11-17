# Notebooks

Read these in order — each one is self-contained, explains what it does, and is saved **with its outputs**
so you can follow it without running anything.

| # | Notebook | In one line |
|:-:|----------|-------------|
| 01 | `01_data_collection` | Collect posts (with timestamps) from YouTube, Reddit, Twitter/X |
| 02 | `02_automated_labeling` | Auto-assign a risk tier to each post (no human labelling) |
| 03 | `03_data_augmentation` | Add training examples for the rare Crisis class |
| 04 | `04_temporal_features` | Build time features and per-user post histories |
| 05 | `05_preprocessing` | Clean text + transliterate Hinglish to Devanagari |
| 06 | `06_text_representation` | Turn text into MuRIL embeddings and validate them |
| 07 | `07_backbone_benchmark` | Compare MuRIL vs XLM-R vs IndicBERT (frozen) |
| 07b | `07b_backbone_finetuning` | Fine-tune the same backbones and compare |
| 08 | `08_linguistic_drift` | Measure how a user's language drifts over time |
| 09 | `09_model_architecture` | The main model (dual-encoder + capsule + attention) |
| 10 | `10_ablation_studies` | Turn each part off to prove it helps |
| 11 | `11_local_explainability` | Explain single predictions (SHAP + LIME + IG) |
| 12 | `12_global_explainability` | Find + sanity-check the model's trigger words |
| 13 | `13_ethics_accountability` | Fairness, privacy, screening-aid disclaimer |
| 14 | `14_statistical_validation` | Seeds, confidence intervals, significance tests |
| 15 | `15_classification_generalization` | Per-class scores + cross-platform result |
| 16 | `16_early_detection` | How early can the model flag risk? + final summary |

**To run them yourself:** install the requirements (`pip install -r ../requirements.txt`), then either
collect data with notebook 01 (needs API keys in `.env`) or adapt the paths to your own data. Without data,
the notebooks are still fully readable thanks to their saved outputs.
