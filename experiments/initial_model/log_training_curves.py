"""Per-epoch training log for the initial model (v1 notebook 09), for the training-curve figure.

Runs notebook 09's own setup / data / model / loss cells unchanged (cells 2-12), then trains with 15 % of the
real YouTube posts held out (stratified) as validation. The frozen Reddit + X test set is never used here.
Writes history.csv: epoch,train_loss,val_loss,val_macro_f1 (losses = class-weighted focal loss, same weights).

Usage: python log_training_curves.py <v1_repo_dir>
"""
import csv, json, os, sys
from pathlib import Path

V1 = Path(sys.argv[1]).resolve()
OUT = Path(__file__).with_name('history.csv')
os.chdir(V1)  # notebook finds data/ from cwd
nb = json.load(open(V1 / 'notebooks/09_model_architecture.ipynb'))
for i in (2, 4, 6, 8, 10, 12):  # setup, config, data, emotion cache, model, losses
    exec(''.join(nb['cells'][i]['source']), globals())

from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score
from torch.utils.data import DataLoader, TensorDataset

yt = np.array([i for i, r in enumerate(train_rows) if r['platform'] == 'youtube'])
fit_yt, val = train_test_split(yt, test_size=0.15, stratify=y_train[yt], random_state=SEED)
fit = np.sort(np.concatenate([fit_yt, np.where([r['platform'] != 'youtube' for r in train_rows])[0]]))  # synthetic stays in train
assert not set(fit) & set(val)


def tensors(ix):
    return [torch.tensor(a[ix]) for a in (MURIL_TR, EMO_TR, TEMP_TR, MASK_TR)] + [torch.tensor(y_train[ix]).long()]


g = torch.Generator(); g.manual_seed(SEED)
dl = DataLoader(TensorDataset(*tensors(fit)), batch_size=BATCH, shuffle=True, generator=g)
Xv = tensors(val)
counts = np.bincount(y_train[fit], minlength=4).astype(float)
cls_w = torch.tensor(counts.sum() / (4.0 * np.clip(counts, 1, None)), dtype=torch.float)
torch.manual_seed(SEED)
model = DriftCapsNet(MURIL_TR.shape[1], EMO_DIM)
focal = FocalLoss(cls_w)
opt = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=WEIGHT_DECAY)

rows = []
for ep in range(1, EPOCHS + 1):
    model.train(); tot, n = 0.0, 0
    for xt, xe, xtau, m, yb in dl:
        opt.zero_grad()
        logits, z = model(xt, xe, xtau, m, return_z=True)
        fl = focal(logits, yb)
        (fl + CONTRAST_W * supervised_contrastive(z, yb)).backward(); opt.step()
        tot += float(fl) * len(yb); n += len(yb)
    model.eval()
    with torch.no_grad():
        lv = model(*Xv[:4])
        vl = float(focal(lv, Xv[4]))
        vf1 = f1_score(Xv[4].numpy(), lv.argmax(-1).numpy(), average='macro', zero_division=0)
    rows.append((ep, round(tot / n, 5), round(vl, 5), round(vf1, 5)))
    print(*rows[-1], flush=True)

with OUT.open('w', newline='') as fh:
    w = csv.writer(fh); w.writerow(['epoch', 'train_loss', 'val_loss', 'val_macro_f1']); w.writerows(rows)
print('fit', len(fit), 'val', len(val), '->', OUT)
