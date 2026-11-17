"""Training-curve figure (two panels, like Sardari et al. Fig. 5): (a) train vs val focal loss, (b) val macro-F1.
Needs a real per-epoch log (experiments/initial_model/log_training_curves.py writes it); it never invents data.
Usage: python make_fig_training_curves.py [history.csv]
CSV columns: epoch,train_loss,val_loss,val_macro_f1  (one row per epoch, from the training loop)."""
import csv, sys
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

src = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).parents[1] / 'experiments/initial_model/history.csv')
if not src.exists():
    sys.exit(f'No training log at {src}. Log epoch,train_loss,val_loss,val_macro_f1 each epoch, then rerun.')
rows = list(csv.DictReader(src.open()))
ep = [int(r['epoch']) for r in rows]
col = {k: [float(r[k]) for r in rows] for k in ('train_loss', 'val_loss', 'val_macro_f1')}


def smooth(y, k=5):  # centred moving average; shorter window at the ends
    h = k // 2
    return [sum(y[max(0, i - h):i + h + 1]) / len(y[max(0, i - h):i + h + 1]) for i in range(len(y))]


# reported model uses all 60 epochs; the dashed lines only mark where validation was best
lo = min(range(len(ep)), key=lambda i: col['val_loss'][i])
hi = max(range(len(ep)), key=lambda i: col['val_macro_f1'][i])
BLUE, ORANGE, GREEN, GREY = '#2a78d6', '#eb6834', '#138a5f', '#8a8984'

plt.rcParams.update({'font.family': 'serif', 'font.serif': ['Times New Roman', 'Liberation Serif'], 'mathtext.fontset': 'stix', 'font.size': 9})  # Times New Roman (Liberation Serif = metric clone)
fig, (a, b) = plt.subplots(1, 2, figsize=(7.2, 2.9))
a.plot(ep, col['train_loss'], color=BLUE, lw=1.6, label='train')
a.plot(ep, col['val_loss'], color=ORANGE, lw=.9, alpha=.35)
a.plot(ep, smooth(col['val_loss']), color=ORANGE, lw=1.8, label='validation (5-epoch mean)')
a.axvline(ep[lo], color=GREY, ls='--', lw=1, label=f'lowest val. loss (epoch {ep[lo]})')
a.set(title='(a) Class-weighted focal loss', xlabel='epoch', ylabel='loss')
b.plot(ep, col['val_macro_f1'], color=GREEN, lw=.9, alpha=.35)
b.plot(ep, smooth(col['val_macro_f1']), color=GREEN, lw=1.8, label='validation macro-F1 (5-epoch mean)')
b.axvline(ep[hi], color=GREY, ls='--', lw=1, label=f'best val. macro-F1 (epoch {ep[hi]})')
b.set(title='(b) Validation macro-F1', xlabel='epoch', ylabel='macro-F1')
for ax in (a, b):
    ax.set_xlim(1, ep[-1]); ax.grid(alpha=.3); ax.legend(frameon=False, fontsize=7.5)
    ax.spines[['top', 'right']].set_visible(False)
fig.tight_layout()
out = Path(__file__).with_name('fig_training_curves.png')
fig.savefig(out, dpi=300); fig.savefig(out.with_suffix('.pdf'))
print('wrote', out, '| lowest val loss epoch', ep[lo], '| best val macro-F1 epoch', ep[hi])
