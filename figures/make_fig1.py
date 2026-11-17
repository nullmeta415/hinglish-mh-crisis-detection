"""Fig. 1 with orthogonal connectors only (straight drops, one merge bus)."""
import sys, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
plt.rcParams.update({'font.family': 'DejaVu Sans'})  # sans stays legible when the figure is scaled down
B, OR, AQ, GY = '#2a78d6', '#eb6834', '#1baf7a', '#8a8984'
TXT, LN = '#000000', '#333333'
fig = plt.figure(figsize=(7.2, 8.6)); ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 100); ax.set_ylim(0, 120); ax.axis('off')

def box(x0, x1, ytop, h, t, fc='#eaf2fc', ec=B):
    ax.add_patch(FancyBboxPatch((x0, ytop - h), x1 - x0, h, boxstyle='round,pad=0,rounding_size=1.2', fc=fc, ec=ec, lw=1.5))
    ax.text((x0 + x1) / 2, ytop - h / 2, t, ha='center', va='center', fontsize=9.2, color=TXT, linespacing=1.25)
    return ytop - h  # bottom edge

def down(x, y1, y2):  # vertical arrow ending on the next box's top edge
    ax.annotate('', xy=(x, y2), xytext=(x, y1),
                arrowprops=dict(arrowstyle='-|>,head_length=0.5,head_width=0.22', color=LN, lw=1.3, shrinkA=0, shrinkB=0))

def line(xs, ys):
    ax.plot(xs, ys, color=LN, lw=1.3, solid_capstyle='butt')

G = 3.2  # vertical gap between rows
stages = []  # (top, bottom, label) of each stage band, drawn at the end

# Stage 1 -> merge box
y = 119
t0 = y; b = box(13, 37, y, 8, 'Newly collected\nHinglish posts\n(YouTube, Reddit, X)')
box(40, 66, y, 8, 'Existing Hinglish\nsuicidal-ideation corpus\n(Agarwal & Dhingra)')
box(69, 95, y, 8, 'Existing English\ncondition corpora\n(label-mapped)')
stages.append((t0, b, 'Stage 1\nData'))
y = b - G
for x in (25, 53, 82): down(x, b, y)
t0 = y
b = box(13, 95, y, 6.5, 'De-identification · label mapping · de-duplication\nuser-disjoint, platform-tagged split', fc='#f3f3f1', ec=GY)

# Stage 2
y = b - G
for x in (32, 77): down(x, b, y)
b = box(13, 54, y, 6.5, 'Text normalisation, CMI tagging,\nroman→Devanagari transliteration', fc='#f3f3f1', ec=GY)
box(57, 95, y, 6.5, 'Timestamp features & per-user\nposting history (post_seq)', fc='#f3f3f1', ec=GY)

stages.append((t0, b, 'Stage 2\nPreparation'))
# Stage 3
y = b - G; t1 = y
for x in (22.5, 44.25, 77): down(x, b, y)
b = box(13, 32, y, 9, 'Language encoder\nMuRIL\n→ h_text', fc='#fdeee6', ec=OR)
box(34.5, 54, y, 9, 'Sentiment / lexicon\nsignal\n→ s_lex', fc='#e6f6f0', ec=AQ)
box(57, 95, y, 9, 'Behavioural + temporal\nsignal (recency-weighted)\n→ s_beh, s_tmp', fc='#e6f6f0', ec=AQ)

# Fusion -> gate
y = b - G
for x in (22.5, 44.25, 77): down(x, b, y)
b = box(13, 95, y, 5.5, 'Fusion  z = [h_text ; W(s_lex, s_beh, s_tmp)]', fc='#f3f3f1', ec=GY)
stages.append((t1, b, 'Stage 3\nSignals'))
y = b - G; down(54, b, y); t1 = y
b = box(13, 95, y, 5.5, 'Gating network  g = softmax(W_g z)')

# Experts: straight drops from the gate
y = b - G
xs = [(13, 30), (34.7, 51.7), (56.3, 73.3), (78, 95)]
for (x0, x1), n in zip(xs, ['Depression\nexpert', 'Anxiety\nexpert', 'Suicide-Risk\nexpert', 'Normal\nexpert']):
    down((x0 + x1) / 2, b, y); box(x0, x1, y, 6.5, n)
b = y - 6.5
stages.append((t1, b, 'Stage 4\nModel'))

# Merge bus: each expert drops to one horizontal bus, a single arrow goes on to the prediction box
bus = b - 3; cx = [(x0 + x1) / 2 for x0, x1 in xs]
for x in cx: line([x, x], [b, bus])
line([cx[0], cx[-1]], [bus, bus])
pc = 32.5
ax.plot(pc, bus, 'o', ms=3, color=LN)
y = bus - 3.5; down(pc, bus, y)
b = box(13, 52, y, 10, 'Prediction ŷ, confidence p,\nSHAP / IG explanation\n(focal loss, imbalance-aware)', fc='#fdeee6', ec=OR)
box(58, 95, y, 10, 'Recommendation layer\nSuicide-Risk ⇒ helpline first (fixed rule)\nelse confidence-matched resource', fc='#fdeee6', ec=OR)
ax.annotate('', xy=(58, y - 5), xytext=(52, y - 5),
            arrowprops=dict(arrowstyle='-|>,head_length=0.5,head_width=0.22', color=LN, lw=1.3, shrinkA=0, shrinkB=0))
stages.append((y, b, 'Stage 5\nOutput'))
for i, (top, bot, lab) in enumerate(stages):
    ax.text(1, (top + bot) / 2, lab, fontsize=8.3, color=TXT, va='center', weight='bold')
    if i: ax.plot([1, 97], [top + 1.6] * 2, color='#d9d8d4', lw=0.7, ls=(0, (4, 3)), zorder=0)
lo = b - 1.5  # crop to content, keeping the x scale (and so the font size) unchanged
ax.set_ylim(lo, 120); fig.set_size_inches(7.2, 8.6 * (120 - lo) / 120)
plt.savefig(sys.argv[1], dpi=220)
