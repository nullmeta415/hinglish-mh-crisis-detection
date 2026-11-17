"""Alternative Fig. 1 in block style (pastel boxes, bullet lists, serpentine flow, END terminal).
Writes fig1_blocks.svg; PNG/PDF are rendered with headless Chromium."""
from pathlib import Path

W, H = 1600, 1100
FONT = "'Liberation Sans', Arial, Helvetica, 'Noto Sans Devanagari', sans-serif"
INK, LINE = '#1d1d1f', '#2b2b2e'
out = []
e = out.append

def text(x, y, t, size=13.5, w='normal', anchor='start', fill=INK, style='normal'):
    e(f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" font-weight="{w}" font-style="{style}" '
      f'fill="{fill}" text-anchor="{anchor}">{t}</text>')

def rect(x, y, w, h, fill, stroke, sw=1.4, r=6):
    e(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')

def box(x, y, w, h, title, bullets, fill, stroke, size=13.5):
    """Pastel box, bold centred title, bullets; a line starting with two spaces continues the previous bullet."""
    rect(x, y, w, h, fill, stroke)
    text(x + w / 2, y + 27, title, 16, 'bold', 'middle')
    e(f'<line x1="{x + 14}" y1="{y + 38}" x2="{x + w - 14}" y2="{y + 38}" stroke="{stroke}" stroke-width="1" opacity=".6"/>')
    for i, b in enumerate(bullets):
        yy = y + 60 + i * 19.5
        if not b.startswith('  '):
            text(x + 16, yy, '•', size, 'bold', fill=stroke)
        text(x + 30, yy, b.strip(), size)

def arrow(pts, label=None, lx=0, ly=0):
    p = ' '.join(f'{a},{b}' for a, b in pts)
    e(f'<polyline points="{p}" fill="none" stroke="{LINE}" stroke-width="1.8" stroke-linejoin="round" marker-end="url(#ah)"/>')
    if label:
        text(lx, ly, label, 12, anchor='middle', fill='#555', style='italic')

def sub(t, size=11.5):  # subscript
    return f'<tspan baseline-shift="sub" font-size="{size}">{t}</tspan>'

e(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
e(f'<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
  f'<path d="M0,0 L10,5 L0,10 z" fill="{LINE}"/></marker></defs>')
e(f'<rect width="{W}" height="{H}" fill="#ffffff"/>')

C = [45, 435, 825, 1215]   # column x
BW = 340                    # column box width
R1, R1H = 40, 230           # row 1
R2 = 310                    # row 2
R3, R3H = 570, 230          # row 3
R4, R4H = 850, 220          # row 4

# ---- row 1: left -> right ----
box(C[0], R1, BW, R1H, 'Data Collection', [
    'Newly collected Hinglish posts', '  (YouTube, Reddit, X; keyword seeding)',
    'Hinglish suicide-risk corpus', '  (Agarwal &amp; Dhingra [14])',
    'English condition corpora', '  (label-mapped to 4 classes)',
    'Classes: Depression, Anxiety,', '  Suicide-Risk, Normal'], '#d3e5f6', '#3f78b5')
box(C[1], R1, BW, R1H, 'De-identification &amp; Labelling', [
    'Mask URL, @user, e-mail, phone', 'Author ID → salted HMAC-SHA256',
    'Dual auto-labelling: distress', '  lexicon + MuRIL (κ = 0.84)',
    'Language filter: EN / HI / Hinglish', 'Near-duplicates removed', '  (cosine &gt; 0.95)'], '#e7f0cb', '#7f9a35')
box(C[2], R1, BW, R1H, 'Text Pre-processing', [
    'Unicode normalisation, lowercase', 'Elongation fix (bahuuut → bahut)', 'Spelling norm. (acha → accha)',
    'Emoji → text, negation tagging', 'Distress terms → Devanagari', 'Language tag + CMI score',
    'Truncate to 128 sub-word tokens'], '#f8d9e1', '#bf5a78')
box(C[3], R1, BW, R1H, 'User-Disjoint Split', [
    'No author in both train and test', f'Train / val: YouTube (Π{sub("s")}),', '  stratified 85 / 15',
    f'Frozen test: Reddit + X (Π{sub("t")}),', '  scored once', '4,614 posts (EN 67.6 %,', '  Hinglish 30.2 %, HI 2.2 %)'],
    '#e6e6ea', '#666673')
mid1 = R1 + R1H / 2
for i in range(3):
    arrow([(C[i] + BW, mid1), (C[i + 1] - 2, mid1)])

# ---- row 2: side branches feeding feature extraction ----
r2h = 108
box(C[1], R2, BW, r2h, 'Timestamp Features', ['month, day, hour, weekday,', '  workday, weekend (min–max, train-only)'],
    '#cdeef0', '#33959f', size=13)
box(C[2], R2, BW, r2h, 'Per-user Posting History', ['posts ordered by time (post_seq)', f'only earlier posts t{sub("j")} &lt; t{sub("k")} used'],
    '#cdeef0', '#33959f', size=13)
FH = 212
box(C[3], R2, BW, FH, 'Multi-Signal Feature Extraction', [
    f'Text: MuRIL mean-pool h{sub("text")} ∈ ℝ⁷⁶⁸', f'Sentiment / lexicon s{sub("lex")} (XLM-EMO)',
    f'Behavioural s{sub("beh")}: post rate,', '  night-time share, mean gap',
    f'Temporal s{sub("tmp")}: recency-weighted', '  history + drift velocity v',
    f'Fusion z = [h{sub("text")} ; W{sub("a")}(s{sub("lex")}, s{sub("beh")}, s{sub("tmp")}, v)]'], '#f3dfca', '#ad7442', size=13)
arrow([(C[1] + BW / 2, R1 + R1H), (C[1] + BW / 2, R2 - 2)])
arrow([(C[2] + BW / 2, R1 + R1H), (C[2] + BW / 2, R2 - 2)])
arrow([(C[3] + BW / 2, R1 + R1H), (C[3] + BW / 2, R2 - 2)])
arrow([(C[1] + BW, R2 + r2h / 2), (C[2] - 2, R2 + r2h / 2)])
arrow([(C[2] + BW, R2 + r2h / 2), (C[3] - 2, R2 + r2h / 2)])

# ---- row 3: right -> left ----
box(C[3], R3, BW, R3H, 'Proposed Model: Gated Multi-Expert', [
    f'Gating network g = softmax(W{sub("g")} z)', '4 condition experts (2-layer FFN):', '  Depression, Anxiety, Suicide-Risk, Normal',
    f'p = softmax(W{sub("o")} Σ g{sub("m")} E{sub("m")}(z))', 'Class-weighted focal loss (γ = 2)', '  + gate load-balancing term',
    'AdamW, early stop on val macro-F1'], '#e2dbf2', '#6f5cab', size=13)
box(C[2], R3, BW, R3H, 'Explanation &amp; Recommendation', [
    'Integrated Gradients: token attribution', 'SHAP: auxiliary-signal attribution',
    f'Guard-rail: Suicide-Risk or p ≥ τ{sub("s")}', '  → crisis helpline first (Tele-MANAS)',
    'Otherwise confidence-matched resources', 'Non-diagnostic, in the post’s language'], '#d5efe4', '#3a9672', size=13)
box(C[1], R3, BW, R3H, 'Baseline Models', [
    'Majority class', 'Linear probe on frozen MuRIL', 'Text-only variant of the model',
    'BGE-M3 + XGBoost', 'BGE-M3 + emotion + time + XGBoost', 'Backbones: MuRIL, XLM-R,', '  IndicBERT v2 (probe / fine-tune)'],
    '#fad3ad', '#cc7326', size=13)
box(C[0], R3, BW, R3H, 'Training &amp; Experimental Protocol', [
    'Train on YouTube, test once', '  on unseen Reddit + X', 'Initial model: frozen MuRIL + XLM-EMO,',
    '  capsule-routing fusion head', '5 random seeds, 95 % CI', '5-fold in-platform CV → generalisation gap',
    'Paired t-test + Benjamini–Hochberg'], '#fbf1cc', '#ab9230', size=13)
arrow([(C[3] + BW / 2, R2 + FH), (C[3] + BW / 2, R3 - 2)])
mid3 = R3 + R3H / 2
for i in (3, 2, 1):
    arrow([(C[i], mid3), (C[i - 1] + BW + 2, mid3)])

# ---- row 4: left -> right, ending at END ----
PW = 410
rect(C[0], R4, PW, R4H, '#d8eedf', '#459060')
text(C[0] + PW / 2, R4 + 27, 'Performance Evaluation Measures', 16, 'bold', 'middle')
for i, (a, b) in enumerate([('Classification', 'Macro-F1 · MCC · Crisis recall · P / R / F1'),
                            ('Probabilistic', 'macro one-vs-rest ROC-AUC'),
                            ('Early risk (user-level)', 'ERDE₅ · ERDE₅₀ · precision / recall'),
                            ('Visualisations', 'confusion matrix · gap plot · ablation chart')]):
    yy = R4 + 42 + i * 43
    rect(C[0] + 14, yy, PW - 28, 36, '#f5d3e3', '#ad5d88', sw=1.1, r=4)
    text(C[0] + PW / 2, yy + 23, f'<tspan font-weight="bold">{a}:</tspan> {b}', 13, anchor='middle')
arrow([(C[0] + BW / 2, R3 + R3H), (C[0] + BW / 2, R4 - 2)])

X2, W2 = 500, 262
box(X2, R4, W2, R4H, 'Explainability Analysis', [
    'Global SHAP token ranking', 'Overlap with distress lexicon', 'SHAP / LIME / IG agreement',
    '  (top-token Jaccard)', 'Case-level inspection'], '#d0e1ef', '#3f78b5', size=13)
X3, W3 = 812, 262
box(X3, R4, W3, R4H, 'Ablation Study', [
    'Text-only fusion (no aux. signals)', 'ELU gate removed', 'Concat vs attention fusion',
    'Dynamic vs static routing', 'CE vs focal + contrastive', 'Real vs synthetic training'], '#e8e8ea', '#666673', size=13)
X4, W4 = 1124, 240
box(X4, R4, W4, R4H, 'SOTA Comparison', [
    'Closest published settings', '  (Table 10)', 'Cross-platform drop:', '  44 % vs 41 % (Nguyen et al.)',
    'Context, not a ranking'], '#ffffff', '#c0303f', size=13)
mid4 = R4 + R4H / 2
arrow([(C[0] + PW, mid4), (X2 - 2, mid4)])
arrow([(X2 + W2, mid4), (X3 - 2, mid4)])
arrow([(X3 + W3, mid4), (X4 - 2, mid4)])
EX, EW = 1414, 141
arrow([(X4 + W4, mid4), (EX - 2, mid4)])
rect(EX, mid4 - 30, EW, 60, '#2f9aa3', '#1f6f76', sw=1.6, r=30)
text(EX + EW / 2, mid4 + 7, 'END', 20, 'bold', 'middle', fill='#fff')
e('</svg>')

Path(__file__).with_name('fig1_blocks.svg').write_text('\n'.join(out), encoding='utf-8')
print('wrote fig1_blocks.svg')
