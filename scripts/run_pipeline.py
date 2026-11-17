"""Execute notebooks 02..16 in order, in place, saving real outputs.
"""
import sys
import time
import traceback
from pathlib import Path

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parent.parent
NB_DIR = ROOT / "notebooks"
LOG = Path(__file__).resolve().parent / "run_pipeline.log"

ORDER = [
    "02_automated_labeling",
    "03_data_augmentation",
    "04_temporal_features",
    "05_preprocessing",
    "06_text_representation",
    "07_backbone_benchmark",
    "07b_backbone_finetuning",
    "08_linguistic_drift",
    "09_model_architecture",
    "10_ablation_studies",
    "11_local_explainability",
    "12_global_explainability",
    "13_ethics_accountability",
    "14_statistical_validation",
    "15_classification_generalization",
    "16_early_detection",
]


def log(msg):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def run_one(name):
    path = NB_DIR / f"{name}.ipynb"
    nb = nbformat.read(path, as_version=4)
    client = NotebookClient(
        nb,
        timeout=14400,  # 4h/cell -- CPU-only MuRIL self-training/fine-tuning cells are genuinely slow
        kernel_name="python3",
        resources={"metadata": {"path": str(NB_DIR)}},
    )
    t0 = time.time()
    client.execute()
    dt = time.time() - t0
    nbformat.write(nb, path)
    return dt


def main():
    only = sys.argv[1:] if len(sys.argv) > 1 else ORDER
    log(f"=== RUN START: {only} ===")
    for name in only:
        log(f"START {name}")
        try:
            dt = run_one(name)
            log(f"OK    {name}  ({dt:.1f}s)")
        except Exception as e:
            log(f"FAIL  {name}: {type(e).__name__}: {e}")
            err_path = Path(__file__).resolve().parent / f"error_{name}.txt"
            with open(err_path, "w", encoding="utf-8") as f:
                f.write(traceback.format_exc())
            log("=== RUN STOPPED ON FAILURE ===")
            sys.exit(1)
    log("=== RUN COMPLETE: ALL NOTEBOOKS OK ===")


if __name__ == "__main__":
    main()
