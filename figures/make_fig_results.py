"""Results charts (Figs. 8-10) in Times New Roman, drawn at their printed size so nothing is stretched.
Values are the ones printed on the original charts / reported in Section 5.1:
  Fig. 8  confusion matrix, seed 42 (row sums = test supports 1,581 / 545 / 596 / 46)
  Fig. 9  in- vs cross-platform macro-F1, mean with 95% CI (cross-platform CI 0.435-0.495 from the text; the other three
          CIs were read off the original chart's error-bar caps, checked against the known cross-platform CI to +/-0.001)
  Fig. 10 ablation: change in cross-platform macro-F1 per single-component change
Writes fig8_confusion.png, fig9_generalisation.png, fig10_ablation.png (300 dpi). Usage: python make_fig_results.py"""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).parent
plt.rcParams.update({'font.family': 'serif', 'font.serif': ['Times New Roman', 'Liberation Serif'],  # Liberation Serif = metric clone
                     'mathtext.fontset': 'stix', 'font.size': 9, 'axes.edgecolor': '#444', 'axes.labelcolor': '#222',
                     'xtick.color': '#333', 'ytick.color': '#333', 'axes.spines.top': False, 'axes.spines.right': False})
BLUE, ORANGE = '#2a78d6', '#eb6834'
TIERS = ['Neutral', 'Stress', 'Moderate', 'Crisis']

# ---- Fig. 8: confusion matrix ----
cm = np.array([[1491, 20, 63, 7], [294, 207, 40, 4], [333, 9, 241, 13], [20, 4, 17, 5]])
assert cm.sum(1).tolist() == [1581, 545, 596, 46]
rn = cm / cm.sum(1, keepdims=True)
fig, ax = plt.subplots(figsize=(4.97, 3.27))
im = ax.imshow(rn, cmap='Blues', vmin=0, vmax=1, aspect='auto')
for i in range(4):
    for j in range(4):
        ax.text(j, i, f'{cm[i, j]}\n({rn[i, j]:.2f})', ha='center', va='center', fontsize=8.5,
                color='white' if rn[i, j] > 0.5 else '#111')
ax.set_xticks(range(4), TIERS); ax.set_yticks(range(4), TIERS)
ax.set_xlabel('Predicted tier')
for s in ax.spines.values(): s.set_visible(False)
cb = fig.colorbar(im, ax=ax, fraction=0.05, pad=0.03)
cb.set_label('Row-normalised recall'); cb.outline.set_visible(False)
fig.tight_layout(); fig.savefig(HERE / 'fig8_confusion.png', dpi=300); plt.close(fig)

# ---- Fig. 9: in- vs cross-platform macro-F1 ----
labels = ['In-platform\n(YouTube, 5-fold CV)', 'Cross-platform\n(Reddit + X, pooled)', 'Reddit only', 'X (Twitter) only']
mean = np.array([0.834, 0.465, 0.442, 0.389])
lo = np.array([0.774, 0.435, 0.411, 0.366])
hi = np.array([0.891, 0.495, 0.472, 0.411])
fig, ax = plt.subplots(figsize=(5.8, 2.88))
x = np.arange(4)
ax.bar(x, mean, width=0.55, color=[BLUE, ORANGE, ORANGE, ORANGE], zorder=2)
ax.errorbar(x, mean, yerr=[mean - lo, hi - mean], fmt='none', ecolor='#333', elinewidth=1, capsize=4, zorder=3)
for xi, m, h in zip(x, mean, hi): ax.text(xi, h + 0.025, f'{m:.3f}', ha='center', va='bottom', fontsize=9.5)
ax.set_xticks(x, labels); ax.set_ylim(0, 1.0); ax.set_ylabel('Macro-F1 (mean, 95% CI)')
ax.yaxis.grid(True, color='#e3e3e3', zorder=0); ax.set_axisbelow(True)
fig.tight_layout(); fig.savefig(HERE / 'fig9_generalisation.png', dpi=300); plt.close(fig)

# ---- Fig. 10: ablation ----
abl = [('Routing: dynamic', 0.039), ('Gate: none', 0.101), ('Gate: sigmoid', -0.056), ('Fusion: concat', 0.067),
       ('Fusion: text_only', -0.088), ('Loss: focal', 0.083), ('Loss: ce', 0.094), ('Augmentation: original_only', 0.059),
       ('Augmentation: +CSS', -0.005), ('Augmentation: +EDA', -0.048)]
fig, ax = plt.subplots(figsize=(6.2, 3.15))
y = np.arange(len(abl))[::-1]
v = np.array([d for _, d in abl])
ax.barh(y, v, height=0.5, color=[BLUE if d > 0 else ORANGE for d in v], zorder=2)
for yi, d in zip(y, v):
    ax.text(d + (0.004 if d > 0 else -0.004), yi, f'{d:+.3f}'.replace('+-', '-'), va='center', ha='left' if d > 0 else 'right', fontsize=8.5)
ax.set_yticks(y, [n for n, _ in abl]); ax.axvline(0, color='#555', lw=0.9, zorder=3)
ax.set_xlim(-0.13, 0.14); ax.set_xlabel('Δ macro-F1 relative to reference configuration')
ax.xaxis.grid(True, color='#e3e3e3', zorder=0); ax.set_axisbelow(True)
fig.tight_layout(); fig.savefig(HERE / 'fig10_ablation.png', dpi=300); plt.close(fig)
print('wrote fig8_confusion.png, fig9_generalisation.png, fig10_ablation.png')
