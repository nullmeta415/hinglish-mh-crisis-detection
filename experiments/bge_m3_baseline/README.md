# BGE-M3 + XGBoost baseline (initial-study split)

Train: v1 YouTube posts (1,971 incl. 125 synthetic). Test: frozen Reddit + X (2,768). Seeds 42, 2023, 2024, 0, 7.

- `run_bge_m3_xgb.py` – embeds with BAAI/bge-m3 (CPU, 128 tokens), trains XGBoost, runs paired t-tests vs the initial model with BH over the 10-comparison family.
- `bge_m3_xgb_results.json` – all per-seed metrics, summaries, confusion matrix (seed 42), significance.
- `run.log` – console output of the reported run.

Rerun (environment used: Python 3.12, torch 2.15 CPU, transformers 5.21, xgboost 3.4, scikit-learn 1.9):

    pip install torch transformers xgboost scikit-learn scipy numpy
    # run from the repository root, after the pipeline has produced data/stage1_* to data/stage3_model
    python experiments/bge_m3_baseline/run_bge_m3_xgb.py . experiments/bge_m3_baseline
