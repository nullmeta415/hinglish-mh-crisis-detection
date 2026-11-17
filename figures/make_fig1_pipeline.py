"""Fig. 1 (pipeline version): end-to-end framework, input post -> explained prediction + safe recommendation.
Writes fig1_pipeline.svg; render with render_fig1_pipeline.sh (headless Chromium) to PNG/PDF."""
from pathlib import Path

W, H = 1800, 1192
FONT = "'Liberation Sans', Arial, Helvetica, 'Noto Sans Devanagari', sans-serif"
MONO = "'DejaVu Sans Mono', 'Liberation Mono', monospace"
INK, SUB, LINE = '#1d1d1f', '#4a4a4f', '#3a3a3e'
# phase colours: (stroke, light fill, header fill)
PH = {
    1: ('#2a6fc9', '#eef4fc', '#2a6fc9'),
    2: ('#6a4fb8', '#f3f0fb', '#6a4fb8'),
    3: ('#14946a', '#ebf7f2', '#14946a'),
    4: ('#d2601f', '#fdf1ea', '#d2601f'),
    5: ('#c0303f', '#fcedef', '#c0303f'),
}
out = []
def e(s): out.append(s)

def esc(t): return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def text(x, y, t, size=14, w='normal', fill=INK, anchor='start', fam=FONT, style='normal'):
    size = max(size, 12)  # legibility floor once the figure is scaled to page width
    e(f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{size}" font-weight="{w}" font-style="{style}" '
      f'fill="{fill}" text-anchor="{anchor}">{t}</text>')

def rect(x, y, w, h, fill='#fff', stroke=LINE, sw=1.4, r=8, dash=None, extra=''):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    e(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d} {extra}/>')

def card(x, y, w, h, title, lines, ph, size=13.5, tsize=15, fill='#fff', dash=None, center=False):
    """Box with bold title + sub-lines. lines: list of str (markup allowed)."""
    c = PH[ph][0]
    rect(x, y, w, h, fill=fill, stroke=c, dash=dash)
    ax, an = (x + w / 2, 'middle') if center else (x + 12, 'start')
    n = len(lines) + (1 if title else 0)
    lh = size * 1.32
    y0 = y + h / 2 - (n - 1) * lh / 2 + size * 0.36
    if title:
        text(ax, y0, title, tsize, 'bold', anchor=an); y0 += lh + 1
    for ln in lines:
        text(ax, y0, ln, size, fill=SUB, anchor=an); y0 += lh

def arrow(x1, y1, x2, y2, color=LINE, sw=1.6, dash=None, head=True):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    m = ' marker-end="url(#ah)"' if head else ''
    e(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{sw}"{d}{m}/>')

def poly(pts, color=LINE, sw=1.6, head=True, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    m = ' marker-end="url(#ah)"' if head else ''
    p = ' '.join(f'{a},{b}' for a, b in pts)
    e(f'<polyline points="{p}" fill="none" stroke="{color}" stroke-width="{sw}" stroke-linejoin="round"{d}{m}/>')

def chip(x, y, w, h, t, fill, stroke, size=13, tc=INK, w8='bold', fam=FONT):
    rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.2, r=h / 2)
    text(x + w / 2, y + h / 2 + size * 0.36, t, size, w8, fill=tc, anchor='middle', fam=fam)

def bar(x, y, w, h, frac, color, bg='#e9e9ec'):
    rect(x, y, w, h, fill=bg, stroke='none', sw=0, r=2)
    rect(x, y, max(w * frac, 1), h, fill=color, stroke='none', sw=0, r=2)

e(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
e('<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
  f'<path d="M0,0 L10,5 L0,10 z" fill="{LINE}"/></marker>'
  '<marker id="ahr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
  f'<path d="M0,0 L10,5 L0,10 z" fill="{PH[5][0]}"/></marker></defs>')
rect(0, 0, W, H, fill='#ffffff', stroke='none', sw=0, r=0)

# ---------------- panels + chevron headers ----------------
PX = {1: (24, 320), 2: (364, 644), 3: (688, 1048), 4: (1092, 1388), 5: (1432, 1772)}  # 44-px gutters carry the flow arrows
TITLES = {1: 'Data Collection', 2: 'Pre-processing', 3: 'Feature Extraction', 4: 'Multi-Expert Classification',
          5: 'Explanation &amp; Recommendation'}
PT, PB = 64, 804  # panel top/bottom
for k, (x0, x1) in PX.items():
    c, lf, hf = PH[k]
    rect(x0, PT, x1 - x0, PB - PT, fill=lf, stroke=c, sw=1.2, r=10, dash='5 4')
    tip = 0 if k == 5 else 16
    notch = 0 if k == 1 else 16
    e(f'<path d="M{x0},14 L{x1 + tip - 14 if tip else x1},14 L{x1 + tip},34 L{x1 + tip - 14 if tip else x1},54 L{x0},54 '
      f'L{x0 + notch},34 Z" fill="{hf}"/>')
    e(f'<circle cx="{x0 + notch + 20}" cy="34" r="12" fill="#fff"/>')
    text(x0 + notch + 20, 39.5, str(k), 15, 'bold', fill=hf, anchor='middle')
    text(x0 + notch + 40, 40, TITLES[k], 16.5, 'bold', fill='#fff')

# fat inter-panel arrows
for k in (1, 2, 3, 4):
    gx0, gx1 = PX[k][1], PX[k + 1][0]
    cy = 434
    e(f'<path d="M{gx0 + 7},{cy - 7} L{gx1 - 22},{cy - 7} L{gx1 - 22},{cy - 16} L{gx1 - 6},{cy} L{gx1 - 22},{cy + 16} '
      f'L{gx1 - 22},{cy + 7} L{gx0 + 7},{cy + 7} Z" fill="{PH[k][0]}"/>')

# ---------------- 1. Data collection ----------------
x, w = 40, 264
text(x, 88, 'SOURCES', 12, 'bold', fill=PH[1][0])
card(x, 96, w, 72, 'Newly collected Hinglish posts', ['YouTube · Reddit · X (public)', 'keyword &amp; community seeding'], 1)
card(x, 176, w, 56, 'Hinglish suicide-risk corpus', ['Agarwal &amp; Dhingra [14]'], 1)
card(x, 240, w, 56, 'English condition corpora', ['label-mapped to the 4 classes'], 1)
for yy in (132, 204, 268):  # side bus merging the three sources
    poly([(x + w, yy), (x + w + 8, yy)], head=False)
poly([(x + w + 8, 132), (x + w + 8, 304), (x + w / 2, 304), (x + w / 2, 318)])
card(x, 320, w, 74, 'De-identification', ['mask URL · @user · e-mail · phone', 'author ID → salted HMAC-SHA256'], 1)
arrow(x + w / 2, 394, x + w / 2, 408)
card(x, 410, w, 74, 'Dual automatic labelling', ['distress lexicon ⊕ MuRIL semi-sup.', "agreement Cohen's κ = 0.84"], 1)
arrow(x + w / 2, 484, x + w / 2, 498)
card(x, 500, w, 74, 'Filter &amp; de-duplicate', ['EN / HI / Hinglish, ≥ 3 tokens', 'near-duplicates (cos &gt; 0.95) removed'], 1)
# record schema
rect(x, 588, w, 124, fill='#fff', stroke=PH[1][0], dash='4 3')
text(x + 12, 608, 'Stored record', 14, 'bold')
for i, f in enumerate(['text · label · source', 'platform · lang + CMI', 'timestamp · user_hash · post_seq']):
    text(x + 12, 632 + i * 22, f, 12, fill=SUB, fam=MONO)
text(x + 12, 700, 'no usernames ever stored', 12.5, fill=PH[5][0], style='italic')
text(x, 734, 'TARGET CLASSES', 12, 'bold', fill=PH[1][0])
for i, (lab, col) in enumerate([('Depression', '#2a6fc9'), ('Anxiety', '#d2601f'), ('Suicide-Risk', '#c0303f'), ('Normal', '#14946a')]):
    cx, cy = x + (i % 2) * 136, 744 + (i // 2) * 28
    chip(cx, cy, 128, 24, lab, '#fff', col, 12.5, tc=col)

# ---------------- 2. Pre-processing ----------------
x, w = 380, 248
# example input bubble
e(f'<path d="M{x},{96} h{w} a8,8 0 0 1 8,8 v62 a8,8 0 0 1 -8,8 h-{w - 40} l-12,12 l0,-12 h-{28} a8,8 0 0 1 -8,-8 v-62 a8,8 0 0 1 8,-8 z" '
  f'transform="translate(-8,0)" fill="#fff" stroke="{PH[2][0]}" stroke-width="1.6"/>')
text(x + 4, 116, 'INPUT · post x<tspan baseline-shift="sub" font-size="10">k</tspan> of user u', 12, 'bold', fill=PH[2][0])
text(x + 4, 140, '“Kuch acha nahi lagta, bahuuut', 14, style='italic')
text(x + 4, 160, 'akela feel hota hai 😞”', 14, style='italic')
steps = [
    ('Unicode norm. + lowercase', 'Kuch → kuch'),
    ('Elongation fix', 'bahuuut → bahut'),
    ('Emoji → text', '😞 → :disappointed:'),
    ('Negation marking', 'nahi → NEG_nahi'),
    ('Spelling normalisation', 'acha → accha'),
    ('Distress term → Devanagari', 'akela → अकेला'),
    ('Truncate', '≤ 128 sub-word tokens'),
]
y = 202
for i, (a, b) in enumerate(steps):
    e(f'<circle cx="{x + 9}" cy="{y + 9}" r="9" fill="{PH[2][0]}"/>')
    text(x + 9, y + 13.5, str(i + 1), 11.5, 'bold', fill='#fff', anchor='middle')
    text(x + 26, y + 14, a, 14, 'bold')
    text(x + 26, y + 33, b, 13, fill=SUB, fam=MONO)
    if i < len(steps) - 1:
        e(f'<line x1="{x + 9}" y1="{y + 19}" x2="{x + 9}" y2="{y + 44}" stroke="{PH[2][0]}" stroke-width="1.5"/>')
    y += 46
card(x, 526, w, 62, 'Language tag + CMI score', ['CMI = 100·[1 − max<tspan baseline-shift="sub" font-size="9">l</tspan> w<tspan baseline-shift="sub" font-size="9">l</tspan> / (n − u)]'], 2, size=13.5, tsize=14)
card(x, 598, w, 74, 'Timestamp → 6 features', ['month · day · hour · weekday ·', 'workday · weekend (min–max)'], 2, tsize=14)
card(x, 682, w, 110, 'User-disjoint split', ['source platforms Π<tspan baseline-shift="sub" font-size="9">s</tspan> → train / val', '(stratified 85 / 15)',
                                             'target platforms Π<tspan baseline-shift="sub" font-size="9">t</tspan> → frozen test,', 'scored once'], 2, tsize=14, size=13)

# ---------------- 3. Feature extraction ----------------
x, w = 704, 300
bus = 1026
def lane(y, h, tag, title, sub):
    rect(x, y, w, h, fill='#fff', stroke=PH[3][0])
    rect(x, y, 6, h, fill=PH[3][0], stroke='none', sw=0, r=2)
    text(x + 16, y + 21, title, 14.5, 'bold')
    text(x + w - 10, y + 21, tag, 14.5, 'bold', fill=PH[3][0], anchor='end', fam=MONO)
    for i, s in enumerate(sub):
        text(x + 16, y + 42 + i * 18, s, 13, fill=SUB)
    poly([(x + w, y + h / 2), (bus, y + h / 2)], head=False)

# text lane with token blocks -> mean pool -> vector
lane(84, 140, 'h_text', 'Text signal', ['MuRIL (Indian-language BERT)'])
tok = ['kuch', 'accha', 'NEG', 'bahut', 'अकेला', '…']
tx = x + 16
for t in tok:
    tw = 8 + len(t) * 6.6 if t != 'अकेला' else 44
    rect(tx, 140, tw, 22, fill='#ebf7f2', stroke=PH[3][0], sw=1, r=4)
    text(tx + tw / 2, 155.5, t, 11.5, anchor='middle', fam=MONO if t != 'अकेला' else FONT)
    arrow(tx + tw / 2, 162, tx + tw / 2, 175, sw=1.1)
    tx += tw + 5
rect(x + 16, 177, 166, 20, fill=PH[3][0], stroke='none', sw=0, r=4)
text(x + 99, 191.5, 'MuRIL encoder + MeanPool', 12, 'bold', fill='#fff', anchor='middle')
arrow(x + 184, 187, x + 200, 187, sw=1.2)
for i in range(8):
    op = 0.25 + 0.09 * ((i * 5) % 8)
    rect(x + 203 + i * 9, 180, 8, 14, fill=PH[3][0], stroke='none', sw=0, r=1, extra=f'opacity="{op:.2f}"')
text(x + 240, 214, '∈ ℝ⁷⁶⁸', 13, fill=SUB, anchor='middle')

lane(234, 96, 's_lex', 'Sentiment / lexicon', ['class-wise distress-lexicon hits', 'emotion distribution (XLM-EMO)'])
for i, (lab, f) in enumerate([('sad', .8), ('fear', .3), ('joy', .1)]):
    bar(x + 246, 266 + i * 18, 40, 9, f, PH[3][0])
    text(x + 241, 274 + i * 18, lab, 11, fill=SUB, anchor='end')
lane(340, 82, 's_beh', 'Behavioural', ['posting rate · night-time share', 'mean gap between posts'])
lane(432, 152, 's_tmp', 'Temporal (recency-weighted)', [])
# timeline of earlier posts, fading with age
ty = 482
arrow(x + 20, ty, x + 274, ty, sw=1.3)
for i, xi in enumerate([40, 82, 118, 170, 210]):
    e(f'<circle cx="{x + xi}" cy="{ty}" r="7" fill="{PH[3][0]}" opacity="{0.2 + 0.18 * i:.2f}"/>')
e(f'<circle cx="{x + 248}" cy="{ty}" r="8" fill="#fff" stroke="{PH[5][0]}" stroke-width="2.2"/>')
text(x + 40, ty + 22, 'h₁', 12, fill=SUB, anchor='middle'); text(x + 210, ty + 22, 'h<tspan baseline-shift="sub" font-size="9">k−1</tspan>', 12, fill=SUB, anchor='middle')
text(x + 248, ty + 22, 'x<tspan baseline-shift="sub" font-size="9">k</tspan>', 12, 'bold', fill=PH[5][0], anchor='middle')
text(x + 24, ty - 13, 'older', 11, fill=SUB, style='italic'); text(x + 206, ty - 13, 'now', 11, fill=PH[5][0], style='italic', anchor='end')
text(x + 16, 534, 's<tspan baseline-shift="sub" font-size="9">tmp</tspan> = Σ<tspan baseline-shift="sub" font-size="9">j&lt;k</tspan> α<tspan baseline-shift="sub" font-size="9">j</tspan>h<tspan baseline-shift="sub" font-size="9">j</tspan>,  α<tspan baseline-shift="sub" font-size="9">j</tspan> ∝ exp(−λ(t<tspan baseline-shift="sub" font-size="9">k</tspan> − t<tspan baseline-shift="sub" font-size="9">j</tspan>))', 13.5)
text(x + 16, 556, '+ drift velocity v: mean cosine distance', 13, fill=SUB)
text(x + 16, 574, '   between successive post embeddings', 13, fill=SUB)
# leakage note
rect(x, 594, w, 34, fill='#fff7e0', stroke='#c99a10', sw=1.1, r=6)
text(x + w / 2, 616, 'Only past posts (t<tspan baseline-shift="sub" font-size="9">j</tspan> &lt; t<tspan baseline-shift="sub" font-size="9">k</tspan>) used → no future leakage', 12.5, 'bold', fill='#7a5c00', anchor='middle')
# bus down to fusion
poly([(bus, 154), (bus, 652), (x + w / 2 + 60, 652), (x + w / 2 + 60, 664)])
# fusion box
rect(x, 666, bus - x + 12, 126, fill='#fff', stroke=PH[3][0], sw=1.8)
text(x + 12, 690, 'Feature fusion', 15, 'bold')
text(x + 12, 714, 'z = [ h_text ; W<tspan baseline-shift="sub" font-size="9">a</tspan>(s_lex, s_beh, s_tmp, v) ]', 13.5, fam=FONT)
segs = [(150, PH[3][0], 'h_text (768)'), (36, '#6fc4a4', 's_lex'), (30, '#9bd5bf', 's_beh'), (36, '#c4e6d9', 's_tmp, v')]
sx = x + 12
for sw_, col, lab in segs:
    rect(sx, 730, sw_, 22, fill=col, stroke='#fff', sw=1, r=2)
    sx += sw_
text(x + 12 + 75, 745.5, 'h_text (768-d)', 12, 'bold', fill='#fff', anchor='middle')
text(x + 12 + 150 + 51, 745.5, 'projected aux.', 11.5, fill=INK, anchor='middle')
text(sx + 10, 746, '→ z', 15, 'bold')
text(x + 12, 778, 'text embedding ⊕ projected auxiliary signals', 12.5, fill=SUB, style='italic')

# ---------------- 4. Multi-expert classification ----------------
x, w = 1108, 264
chip(x + w / 2 - 50, 82, 100, 28, 'input z', '#fff', PH[4][0], 14, tc=PH[4][0])
arrow(x + w / 2, 110, x + w / 2, 124)
card(x, 126, w, 58, 'Gating network', ['g = softmax(W<tspan baseline-shift="sub" font-size="9">g</tspan> z)'], 4, center=True)
EXP = [('E₁  Depression', '#2a6fc9', .61), ('E₂  Anxiety', '#d2601f', .14), ('E₃  Suicide-Risk', '#c0303f', .17), ('E₄  Normal', '#14946a', .08)]
ey = 222
# z skip line to experts (left), gate weights (right)
poly([(x + w / 2 - 50, 96), (x + 8, 96), (x + 8, ey + 4 * 54 - 30)], head=False)
for i, (lab, col, g) in enumerate(EXP):
    yy = ey + i * 54
    arrow(x + 8, yy + 21, x + 20, yy + 21, sw=1.3)
    rect(x + 22, yy, 150, 42, fill='#fff', stroke=col, sw=1.6)
    text(x + 32, yy + 18, lab, 13.5, 'bold', fill=col)
    text(x + 32, yy + 35, '2-layer FFN', 11.5, fill=SUB)
    # multiply node
    e(f'<circle cx="{x + 200}" cy="{yy + 21}" r="10" fill="#fff" stroke="{LINE}" stroke-width="1.4"/>')
    text(x + 200, yy + 26, '×', 15, 'bold', anchor='middle')
    arrow(x + 172, yy + 21, x + 189, yy + 21, sw=1.3)
    text(x + 222, yy + 14, f'g{i + 1}', 11.5, fill=SUB)
    bar(x + 218, yy + 22, 36, 8, g, col)
poly([(x + w - 4, 184), (x + w - 4, 200), (x + 200, 200), (x + 200, ey + 10)], sw=1.3, dash='4 3')
text(x + w - 8, 214, 'weights g', 11, fill=SUB, anchor='end', style='italic')
for i in range(4):  # gate fan-out between multiply nodes
    if i: arrow(x + 200, ey + (i - 1) * 54 + 31, x + 200, ey + i * 54 + 10, sw=1.0, dash='3 3', head=False)
# sum
sy = ey + 4 * 54 + 10
poly([(x + 210, ey + 3 * 54 + 21), (x + 242, ey + 3 * 54 + 21), (x + 242, sy - 8), (x + w / 2 + 14, sy - 8)], sw=1.3, head=False)
e(f'<circle cx="{x + w / 2}" cy="{sy}" r="14" fill="#fff" stroke="{PH[4][0]}" stroke-width="1.8"/>')
text(x + w / 2, sy + 6, 'Σ', 17, 'bold', fill=PH[4][0], anchor='middle')
text(x + w / 2 + 22, sy + 5, 'o = Σ g<tspan baseline-shift="sub" font-size="9">m</tspan> E<tspan baseline-shift="sub" font-size="9">m</tspan>(z)', 13)
arrow(x + w / 2, sy + 14, x + w / 2, sy + 30)
card(x, sy + 32, w, 40, None, ['p = softmax(W<tspan baseline-shift="sub" font-size="9">o</tspan> o)'], 4, size=14, center=True)
# class probability output
py = sy + 84
text(x, py + 4, 'Class probabilities p', 13.5, 'bold')
for i, (lab, col, pv) in enumerate([('Depression', '#2a6fc9', .71), ('Anxiety', '#d2601f', .12), ('Suicide-Risk', '#c0303f', .11), ('Normal', '#14946a', .06)]):
    yy = py + 16 + i * 21
    text(x + 92, yy + 12, lab, 12.5, fill=SUB, anchor='end')
    bar(x + 98, yy + 2, 124, 12, pv, col)
    text(x + 230, yy + 12.5, f'{pv:.2f}', 12, 'bold' if i == 0 else 'normal')
# training objective (dashed = training only)
rect(x, 694, w, 98, fill='#fff', stroke=PH[4][0], dash='6 4', sw=1.5)
text(x + 12, 714, 'Training objective', 14.5, 'bold')
text(x + w - 10, 714, 'train only', 11.5, fill=PH[4][0], anchor='end', style='italic')
text(x + 12, 736, 'class-weighted focal loss (γ = 2)', 13, fill=SUB)
text(x + 12, 755, '+ η · load-balancing on gate g', 13, fill=SUB)
text(x + 12, 774, 'AdamW · early stop on val macro-F1', 13, fill=SUB)

# ---------------- 5. Explanation & recommendation ----------------
x, w = 1448, 308
rect(x, 82, w, 52, fill='#fff', stroke=PH[5][0], sw=1.8)
text(x + 12, 104, 'Prediction', 13, 'bold', fill=PH[5][0])
text(x + 12, 125, 'ŷ = Depression,  confidence p = 0.71', 14.5, 'bold')
# IG tokens
rect(x, 144, w, 130, fill='#fff', stroke=PH[5][0])
text(x + 12, 164, 'Token attribution · Integrated Gradients', 13.5, 'bold')
toks = [('kuch', .05), ('accha', .25), ('NEG_nahi', .55), ('lagta', .05), ('bahut', .35), ('अकेला', .95), ('feel', .1), ('hota', .02), ('hai', .02), (':disappointed:', .6)]
tx, ty = x + 12, 176
for t, a in toks:
    tw = (len(t) * 7.2 + 10) if t != 'अकेला' else 48
    if tx + tw > x + w - 10: tx, ty = x + 12, ty + 27
    rect(tx, ty, tw, 22, fill=PH[5][0], stroke='none', sw=0, r=4, extra=f'fill-opacity="{0.08 + 0.8 * a:.2f}"')
    text(tx + tw / 2, ty + 15.5, t, 12.5, 'bold' if a > .5 else 'normal', fill='#fff' if a > .5 else INK, anchor='middle')
    tx += tw + 4
text(x + 12, 266, 'darker = stronger evidence for ŷ', 11.5, fill=SUB, style='italic')
# SHAP aux
rect(x, 282, w, 100, fill='#fff', stroke=PH[5][0])
text(x + 12, 302, 'Signal attribution · SHAP', 13.5, 'bold')
for i, (lab, v) in enumerate([('s_lex', .21), ('s_tmp', .14), ('s_beh', .06), ('v (drift)', .03)]):
    yy = 310 + i * 17
    text(x + 82, yy + 11, lab, 12.5, fill=SUB, anchor='end', fam=MONO)
    rect(x + 90, yy + 2, v * 600, 11, fill=PH[5][0], stroke='none', sw=0, r=2, extra='fill-opacity="0.75"')
    text(x + 96 + v * 600, yy + 12, f'+{v:.2f}', 11.5)
# guard-rail decision
dy, dcx = 410, x + w / 2
arrow(dcx, 382, dcx, dy - 2)
e(f'<polygon points="{dcx},{dy} {dcx + 136},{dy + 44} {dcx},{dy + 88} {dcx - 136},{dy + 44}" fill="#fff" stroke="{PH[5][0]}" stroke-width="2"/>')
text(dcx, dy + 32, 'Safety guard-rail', 12, 'bold', fill=PH[5][0], anchor='middle')
text(dcx, dy + 50, 'ŷ = Suicide-Risk or', 13, 'bold', anchor='middle')
text(dcx, dy + 67, 'p(Suicide-Risk) ≥ τ<tspan baseline-shift="sub" font-size="9">s</tspan> ?', 13, 'bold', anchor='middle')
# YES -> helpline
arrow(dcx, dy + 88, dcx, 516)
text(dcx + 8, 512, 'Yes', 13, 'bold', fill=PH[5][0])
rect(x, 518, w, 86, fill=PH[5][0], stroke=PH[5][0], sw=1.5)
text(x + 12, 540, '⚠ Crisis helpline shown first', 15, 'bold', fill='#fff')
text(x + 12, 561, 'Tele-MANAS 14416 + safety message', 13, fill='#fff')
text(x + 12, 579, '+ option to contact a trusted person', 13, fill='#fff')
text(x + 12, 597, 'fixed rule — no score can override it', 12, fill='#ffe3e6', style='italic')
# NO -> resources
poly([(dcx + 136, dy + 44), (x + w + 8, dy + 44), (x + w + 8, 650), (x + w - 2, 650)])
text(dcx + 144, dy + 38, 'No', 13, 'bold', fill=SUB)
rect(x, 616, w, 116, fill='#fff', stroke=PH[5][0], sw=1.5)
text(x + 12, 637, 'Confidence-matched resources', 14.5, 'bold')
for i, (a, b) in enumerate([('Dep./Anx., high conf.', 'professional-support info'),
                            ('Dep./Anx., low conf.', 'self-care · check in later'),
                            ('Normal', 'optional well-being info')]):
    yy = 660 + i * 23
    text(x + 12, yy, a, 12.5, 'bold', fill=INK)
    text(x + w - 10, yy, b, 12.5, fill=SUB, anchor='end')
text(x + 12, 727, 'non-diagnostic wording', 12, fill=PH[5][0], style='italic')
rect(x, 742, w, 50, fill='#fff', stroke=SUB, dash='4 3', sw=1.1)
text(x + 12, 762, 'OUTPUT = (ŷ, p, explanation e, action a)', 13.5, 'bold')
text(x + 12, 782, "in the post's language · user can dispute", 12.5, fill=SUB)

# ---------------- 6. experimental evaluation (block style, flows left -> right to END) ----------------
C6 = '#3d4f66'
by = 852
rect(24, by, 1748, H - by - 16, fill='#f4f6f9', stroke=C6, sw=1.2, r=10, dash='5 4')
arrow(1602, 792, 1602, by + 12, sw=2)  # framework output enters the evaluation stage
e(f'<path d="M24,{by + 12} L1756,{by + 12} L1772,{by + 32} L1756,{by + 52} L24,{by + 52} Z" fill="{C6}"/>')
e(f'<circle cx="44" cy="{by + 32}" r="12" fill="#fff"/>')
text(44, by + 37.5, '6', 15, 'bold', fill=C6, anchor='middle')
text(64, by + 38, 'Experimental Evaluation &amp; Analysis', 16.5, 'bold', fill='#fff')
text(1580, by + 38, 'train on YouTube → test once on unseen Reddit + X', 13.5, fill='#dfe6ef', anchor='end', style='italic')

BY, BH = by + 72, H - by - 104  # block top / height
GAP = 30                         # gutter between blocks, wide enough for a clear arrow

def block(x, w, title, col, bullets, size=12.5):
    rect(x, BY, w, BH, fill='#fff', stroke=col, sw=1.5)
    e(f'<path d="M{x},{BY + 32} v-24 a8,8 0 0 1 8,-8 h{w - 16} a8,8 0 0 1 8,8 v24 z" fill="{col}"/>')
    text(x + w / 2, BY + 21, title, 14, 'bold', fill='#fff', anchor='middle')
    for i, b in enumerate(bullets):
        if b.startswith('  '):
            text(x + 24, BY + 56 + i * 20, b.strip(), size, fill=SUB)
        else:
            text(x + 12, BY + 56 + i * 20, '•', size, 'bold', fill=col)
            text(x + 24, BY + 56 + i * 20, b, size, fill=INK)

def flow(x1):  # arrow across the gutter that starts at x1
    arrow(x1 + 4, BY + BH / 2, x1 + GAP - 4, BY + BH / 2, sw=2)

xs, w = 40, 226
block(xs, w, 'Baseline Models', '#2a6fc9', ['Majority class', 'Linear probe (frozen MuRIL)', 'Text-only variant',
      'BGE-M3 + XGBoost', 'BGE-M3 + emotion + time', '  + XGBoost', 'Backbones: MuRIL / XLM-R /', '  IndicBERT v2 (probe, fine-tune)'])
flow(xs + w); xs += w + GAP

# training protocol with mini platform graphic
w = 270
block(xs, w, 'Training Protocol', '#6a4fb8', [])
chip(xs + 16, BY + 46, w - 32, 28, 'Train: YouTube (Π<tspan baseline-shift="sub" font-size="9">s</tspan>)', '#eef4fc', PH[1][0], 13, tc=PH[1][0])
arrow(xs + w / 2, BY + 74, xs + w / 2, BY + 96, sw=1.6)
text(xs + w / 2 + 8, BY + 90, 'test once', 12, fill=SUB, style='italic')
chip(xs + 16, BY + 98, w - 32, 28, 'Test: Reddit + X (Π<tspan baseline-shift="sub" font-size="9">t</tspan>, frozen)', '#fcedef', PH[5][0], 13, tc=PH[5][0])
for i, b in enumerate(['5 seeds · 95 % CI', '5-fold in-platform CV → gap', 'paired t-test + Benjamini–Hochberg', '4,614 real posts, user-disjoint']):
    text(xs + 12, BY + 152 + i * 20, '•', 12.5, 'bold', fill='#6a4fb8')
    text(xs + 24, BY + 152 + i * 20, b, 12.5)
flow(xs + w); xs += w + GAP

# performance evaluation measures: stacked category boxes
w = 344
block(xs, w, 'Performance Evaluation Measures', '#d2601f', [])
cats = [('Classification', 'Macro-F1 · MCC · Crisis recall · P/R/F1'), ('Probabilistic', 'macro one-vs-rest ROC-AUC'),
        ('Early risk (user)', 'ERDE₅ · ERDE₅₀ · precision / recall'), ('Visualisations', 'confusion matrix · gap plot · ablation')]
for i, (a, b) in enumerate(cats):
    yy = BY + 44 + i * 46
    rect(xs + 12, yy, w - 24, 38, fill='#fdf1ea', stroke='#e9a27c', sw=1.1, r=5)
    text(xs + 22, yy + 16, a, 12, 'bold', fill='#a1450f')
    text(xs + 22, yy + 32, b, 12.5)
flow(xs + w); xs += w + GAP

w = 214
block(xs, w, 'Explainability Analysis', '#c0303f', ['Global SHAP token ranking', 'Overlap with distress lexicon',
      'SHAP / LIME / IG agreement', '  (top-token Jaccard)', 'Per-post case inspection', 'Signal vs text contribution'])
flow(xs + w); xs += w + GAP

w = 214
block(xs, w, 'Ablation Study', '#14946a', ['Text-only fusion (no aux.)', 'ELU gate removed', 'Concat vs attention fusion',
      'Dynamic vs static routing', 'CE vs focal + contrastive', 'Real vs synthetic training'])
flow(xs + w); xs += w + GAP

w = 172
block(xs, w, 'SOTA Comparison', '#7a6a2a', ['Closest published', '  settings (Table 10)', 'Cross-platform drop', '  44 % vs 41 % [7]',
      'Not a ranking:', '  data / labels differ'])
flow(xs + w); xs += w + GAP
# END terminal
ew = 1756 - xs
rect(xs, BY + BH / 2 - 26, ew, 52, fill=C6, stroke=C6, r=26)
text(xs + ew / 2, BY + BH / 2 + 6, 'END', 16, 'bold', fill='#fff', anchor='middle')
e('</svg>')

Path(__file__).with_name('fig1_pipeline.svg').write_text('\n'.join(out), encoding='utf-8')
print('wrote fig1_pipeline.svg')
