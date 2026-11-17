# BGE-M3 + XGBoost baseline (initial-study split)

Train: v1 YouTube posts (1,971 incl. 125 synthetic). Test: frozen Reddit + X (2,768). Seeds 42, 2023, 2024, 0, 7.

- `run_bge_m3_xgb.py` – embeds with BAAI/bge-m3 (CPU, 128 tokens), trains XGBoost, runs paired t-tests vs the initial model with BH over the 10-comparison family.
- `bge_m3_xgb_results.json` – all per-seed metrics, summaries, confusion matrix (seed 42), significance.
- `bge_m3_embeddings.npz` – cached embeddings (rerun skips the 23-min embedding step).
- `run.log` – console output of the reported run.

Rerun (environment used: Python 3.12, torch 2.15 CPU, transformers 5.21, xgboost 3.4, scikit-learn 1.9):

    uv venv --python 3.12 ~/.cache/research_v2_bge
    VIRTUAL_ENV=~/.cache/research_v2_bge uv pip install --index-url https://download.pytorch.org/whl/cpu torch
    VIRTUAL_ENV=~/.cache/research_v2_bge uv pip install transformers xgboost scikit-learn scipy numpy
    ~/.cache/research_v2_bge/bin/python run_bge_m3_xgb.py ~/Myfiles/wind/Research_v1/hinglish-mental-health-detection .
