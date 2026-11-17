"""Phase figures (Figs. 2-7): each phase of the pipeline as its own landscape flowchart.
Same content as fig1_pipeline.svg, redrawn with flowchart symbols:
  terminator (start/end) · process · predefined process (model) · data/IO parallelogram · decision diamond ·
  stored data (cylinder) · dashed annotation.
Canvas is 582 units wide = 466 pt text width at 0.8 pt/unit, so 12.5-unit text prints at 10 pt.
Writes fig_phase{1..6}.svg/.png (300 dpi, rendered with chromium). Usage: python make_fig_phases.py"""
import re, subprocess, sys, tempfile
from pathlib import Path
from PIL import ImageFont

HERE = Path(__file__).parent
W, PT_PER_UNIT, DPI = 582, 0.8, 300
FONT = "'Times New Roman', 'Liberation Serif', 'Noto Serif Devanagari', 'Noto Sans Devanagari', serif"  # Liberation Serif = metric clone of Times New Roman
MONO = FONT  # all figure text in Times New Roman
INK, SUB, LINE = '#1d1d1f', '#4a4a4f', '#3a3a3e'
ACC, TINT, EDGE = '#2f4b7c', '#eef2f8', '#4d4d52'  # one accent, one tint, one edge colour across all figures (journal style)
PH = {k: ACC for k in range(1, 7)}
LIGHT = {k: TINT for k in range(1, 7)}
BASE = 12.5  # 10 pt in print
_F = {}


def font(size, bold=False, mono=False):
    key = (size, bold, mono)
    if key not in _F:
        name = 'LiberationSerif-Bold.ttf' if bold else 'LiberationSerif-Regular.ttf'
        path = subprocess.run(['fc-match', '-f', '%{file}', name.split('.')[0]], capture_output=True, text=True).stdout
        _F[key] = ImageFont.truetype(path, size)
    return _F[key]


def width(s, size, bold=False, mono=False):  # rendered width of markup (subscripts measured at 10)
    plain = re.sub(r'<tspan[^>]*>([^<]*)</tspan>', lambda m: m.group(1), s)
    plain = plain.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    subs = ''.join(re.findall(r'<tspan[^>]*>([^<]*)</tspan>', s))
    return font(size, bold, mono).getlength(plain) - font(size, bold, mono).getlength(subs) + font(10, bold, mono).getlength(subs)


def S(t):  # subscript
    return f'<tspan baseline-shift="sub" font-size="10">{t}</tspan>'


class Fig:
    def __init__(self, k, title, h):
        self.k, self.h, self.o, self.overflow = k, h, [], []
        self.c = PH[k]
        self.e(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}">')
        self.e('<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerUnits="userSpaceOnUse" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
               f'<path d="M0,0 L10,5 L0,10 z" fill="{LINE}"/></marker></defs>')
        self.e(f'<rect width="{W}" height="{h}" fill="#fff"/>')
        self.e(f'<rect x="12" y="12" width="22" height="22" rx="3" fill="{self.c}"/>')
        self.t(23, 28, str(k), 14, 'bold', '#fff', 'middle')
        self.t(42, 29, title, 15, 'bold', INK)
        self.e(f'<line x1="12" y1="42" x2="{W - 12}" y2="42" stroke="#b9c3d3" stroke-width="0.8"/>')

    def e(self, s): self.o.append(s)

    def t(self, x, y, s, size=BASE, w='normal', fill=SUB, anchor='start', mono=False, style='normal'):
        fam = MONO if mono else FONT
        self.e(f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{size}" font-weight="{w}" font-style="{style}" '
               f'fill="{fill}" text-anchor="{anchor}">{s}</text>')

    # lines: list of (markup, kind); kinds: T title, s sub, m mono, i italic, b bold, r red italic, w white, wb white bold, wi
    STY = {'T': (13.5, 'bold', INK, False, 'normal'), 's': (BASE, 'normal', SUB, False, 'normal'),
           'm': (BASE, 'normal', SUB, True, 'normal'), 'i': (BASE, 'normal', SUB, False, 'italic'),
           'b': (BASE, 'bold', INK, False, 'normal'), 'r': (BASE, 'normal', '#d1495b', False, 'italic'),
           'w': (BASE, 'normal', '#fff', False, 'normal'), 'wb': (14, 'bold', '#fff', False, 'normal'),
           'wi': (BASE, 'normal', '#ffe3e6', False, 'italic'), 'c': (BASE, 'bold', None, False, 'normal')}

    def block(self, x, y, w, lines, center=False, pad=10, top=None, h=None):
        """Text lines inside box (x, y, w, h); vertically centred unless top is given."""
        lh = lambda kd: self.STY[kd][0] * 1.3
        total = sum(lh(kd) for _, kd in lines)
        cy = y + (top if top is not None else (h - total) / 2)
        for s, kd in lines:
            size, wt, fill, mono, st = self.STY[kd]
            fill = fill or self.c
            cy += lh(kd)
            if width(s, size, wt == 'bold', mono) > w - 2 * pad + 0.5:
                self.overflow.append((round(width(s, size, wt == 'bold', mono)), round(w - 2 * pad), s[:40]))
            ax = x + w / 2 if center else x + pad
            self.t(ax, cy - lh(kd) * 0.28, s, size, wt, fill, 'middle' if center else 'start', mono, st)
        return total

    # ---- flowchart symbols ----
    def process(self, x, y, w, h, lines, col=None, fill=TINT, center=False, sw=1.0, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ''
        self.e(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{fill}" stroke="{col or EDGE}" stroke-width="{sw}"{d}/>')
        self.block(x, y, w, lines, center, h=h)

    def predefined(self, x, y, w, h, lines, col=None, fill='#fff', center=True):
        col = col or EDGE
        self.e(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="2" fill="{fill}" stroke="{col}" stroke-width="1.0"/>')
        for xx in (x + 7, x + w - 7):
            self.e(f'<line x1="{xx}" y1="{y}" x2="{xx}" y2="{y + h}" stroke="{col}" stroke-width="1.0"/>')
        self.block(x + 7, y, w - 14, lines, center, pad=6, h=h)

    def io(self, x, y, w, h, lines, col=None, fill='#fff', center=False, sk=12):
        col = col or EDGE
        self.e(f'<polygon points="{x + sk},{y} {x + w},{y} {x + w - sk},{y + h} {x},{y + h}" fill="{fill}" stroke="{col}" stroke-width="1.0"/>')
        self.block(x + sk / 2, y, w - sk, lines, center, pad=sk / 2 + 6, h=h)

    def term(self, x, y, w, h, label, col=None):
        col = col or EDGE
        self.e(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h / 2}" fill="#fff" stroke="{col}" stroke-width="1.2"/>')
        self.block(x, y, w, [(label, 'b')], True, pad=8, h=h)

    def decision(self, cx, cy, w, h, lines, col=None):
        col = col or EDGE
        self.e(f'<polygon points="{cx},{cy - h / 2} {cx + w / 2},{cy} {cx},{cy + h / 2} {cx - w / 2},{cy}" fill="#fff8e8" stroke="{col}" stroke-width="1.2"/>')
        self.block(cx - w / 4 - 16, cy - h / 2, w / 2 + 32, lines, True, pad=0, h=h)

    def store(self, x, y, w, h, lines, col=None, ry=7):
        col = col or EDGE
        self.e(f'<path d="M{x},{y + ry} A{w / 2},{ry} 0 0 1 {x + w},{y + ry} V{y + h - ry} A{w / 2},{ry} 0 0 1 {x},{y + h - ry} Z" '
               f'fill="{TINT}" stroke="{col}" stroke-width="1.0"/>')
        self.e(f'<path d="M{x},{y + ry} A{w / 2},{ry} 0 0 0 {x + w},{y + ry}" fill="none" stroke="{col}" stroke-width="1.0"/>')
        self.block(x, y + 2 * ry, w, lines, False, h=h - 2 * ry)

    def note(self, x, y, w, h, lines, col='#7a7a80', fill='#fff', center=False):
        self.e(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{fill}" stroke="{col}" stroke-width="1.0" stroke-dasharray="4 3"/>')
        self.block(x, y, w, lines, center, h=h)

    def chip(self, x, y, w, h, s, col, fill='#fff', tc=None, bold=True, mono=False, size=BASE):
        self.e(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{min(h / 2, 4)}" fill="{fill}" stroke="{col}" stroke-width="1.0"/>')
        if width(s, size, bold, mono) > w - 4: self.overflow.append((round(width(s, size, bold, mono)), w - 4, s))
        self.t(x + w / 2, y + h / 2 + size * 0.36, s, size, 'bold' if bold else 'normal', tc or col, 'middle', mono)

    def bar(self, x, y, w, h, frac, col):
        self.e(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="2" fill="#e6e6ea"/>')
        self.e(f'<rect x="{x}" y="{y}" width="{max(w * frac, 1.5)}" height="{h}" rx="2" fill="{col}"/>')

    def arrow(self, *pts, dash=None, head=True, sw=1.1, col=LINE):
        d = f' stroke-dasharray="{dash}"' if dash else ''
        m = ' marker-end="url(#ah)"' if head else ''
        p = ' '.join(f'{a},{b}' for a, b in pts)
        self.e(f'<polyline points="{p}" fill="none" stroke="{col}" stroke-width="{sw}" stroke-linejoin="round"{d}{m}/>')

    def label(self, x, y, s, anchor='start', fill=SUB, w='bold', style='normal'):
        self.t(x, y, s, BASE, w, fill, anchor, style=style)

    def save(self):
        self.e('</svg>')
        p = HERE / f'fig_phase{self.k}.svg'
        p.write_text('\n'.join(self.o), encoding='utf-8')
        scale = PT_PER_UNIT * DPI / 72
        with tempfile.TemporaryDirectory() as td:
            html = Path(td) / 'p.html'
            html.write_text(f'<html><body style="margin:0"><img src="file://{p}" style="display:block;width:{W}px;height:{self.h}px"></body></html>')
            subprocess.run(['chromium', '--headless', '--no-sandbox', '--disable-gpu', '--hide-scrollbars',
                            f'--force-device-scale-factor={scale}', f'--window-size={W},{self.h}',
                            f'--screenshot={HERE / f"fig_phase{self.k}.png"}', f'file://{html}'], check=True, capture_output=True)
        print(f'phase {self.k}: {W}x{self.h} units -> {W * PT_PER_UNIT / 72:.2f} x {self.h * PT_PER_UNIT / 72:.2f} in',
              'OVERFLOW ' + str(self.overflow) if self.overflow else '')
        return not self.overflow


# =============================== 1. Data collection ===============================
def phase1():
    f = Fig(1, 'Data Collection', 456)
    f.term(251, 54, 80, 26, 'Start')
    f.label(14, 100, 'SOURCES', fill=f.c)
    xs, ws = [12, 202, 392], 178
    src = [[('Newly collected', 'T'), ('Hinglish posts', 'T'), ('YouTube · Reddit ·', 's'), ('X (public) · keyword &amp;', 's'), ('community seeding', 's')],
           [('Hinglish suicide-risk', 'T'), ('corpus', 'T'), ('Agarwal &amp; Dhingra [14]', 's')],
           [('English condition', 'T'), ('corpora', 'T'), ('label-mapped to the', 's'), ('4 classes', 's')]]
    f.arrow((291, 80), (291, 92), head=False)
    f.arrow((xs[0] + ws / 2, 92), (xs[2] + ws / 2, 92), head=False)
    for x, s in zip(xs, src):
        f.arrow((x + ws / 2, 92), (x + ws / 2, 106))
        f.io(x, 108, ws, 90, s, center=True)
    for x in xs: f.arrow((x + ws / 2, 198), (x + ws / 2, 207), head=False)
    f.arrow((xs[0] + ws / 2, 207), (xs[2] + ws / 2, 207), head=False)
    f.arrow((xs[0] + ws / 2, 207), (xs[0] + ws / 2, 220))
    y, h = 222, 104
    f.process(12, y, 172, h, [('De-identification', 'T'), ('mask URL · @user ·', 's'), ('e-mail · phone', 's'), ('author ID → salted', 's'), ('HMAC-SHA256', 's')])
    f.arrow((184, y + h / 2), (203, y + h / 2))
    f.process(205, y, 172, h, [('Dual automatic labelling', 'T'), ('distress lexicon ⊕', 's'), ('MuRIL semi-sup.', 's'), ("agreement Cohen's", 's'), ('κ = 0.84', 's')])
    f.arrow((377, y + h / 2), (396, y + h / 2))
    f.process(398, y, 172, h, [('Filter &amp; de-duplicate', 'T'), ('EN / HI / Hinglish,', 's'), ('≥ 3 tokens', 's'), ('near-duplicates', 's'), ('(cos &gt; 0.95) removed', 's')])
    f.arrow((484, y + h), (484, 342))
    f.store(300, 344, 270, 100, [('Stored record', 'T'), ('text · label · source', 'm'), ('platform · lang + CMI', 'm'), ('timestamp · user_hash · post_seq', 'm'), ('no usernames ever stored', 'r')])
    f.arrow((300, 394), (284, 394))
    f.term(222, 381, 60, 26, 'End')
    # target classes = label set used by the labelling step
    f.note(12, 344, 200, 100, [], col=f.c, fill='#fff')
    f.label(22, 364, 'TARGET CLASSES', fill=f.c)
    for i, (lab, col) in enumerate([('Depression', '#4e79a7'), ('Anxiety', '#e8892b'), ('Suicide-Risk', '#d1495b'), ('Normal', '#59a14f')]):
        f.chip(22 + (i % 2) * 92, 376 + (i // 2) * 32, 86, 24, lab, col)
    f.arrow((112, 344), (112, 335), (291, 335), (291, 328), dash='4 3', sw=1.2)
    return f.save()


# =============================== 2. Pre-processing ===============================
def step(f, x, y, w, h, n, title, ex):
    exl = [ex] if width(ex, BASE, mono=True) <= w - 20 else ex.rsplit(' ', 1)
    f.process(x, y, w, h, [(t, 'T') for t in title] + [(e_, 'm') for e_ in exl], center=False)
    f.e(f'<circle cx="{x + w - 13}" cy="{y + 13}" r="9" fill="{f.c}"/>')
    f.t(x + w - 13, y + 17.5, str(n), 12, 'bold', '#fff', 'middle')


def phase2():
    f = Fig(2, 'Pre-processing', 480)
    X, Wc, G = [12, 205, 398], 172, 21
    f.term(12, 76, 56, 26, 'Start')
    f.arrow((68, 89), (82, 89))
    f.io(84, 56, 290, 66, [('INPUT · post x' + S('k') + ' of user u', 'c'), ('“Kuch acha nahi lagta, bahuuut', 'i'), ('akela feel hota hai 😞”', 'i')])
    f.arrow((374, 89), (396, 89))
    rows = [[(1, ['Unicode norm. +', 'lowercase'], 'Kuch → kuch')],
            [(2, ['Elongation fix'], 'bahuuut → bahut'), (3, ['Emoji → text'], '😞 → :disappointed:'), (4, ['Negation marking'], 'nahi → NEG_nahi')],
            [(5, ['Spelling', 'normalisation'], 'acha → accha'), (6, ['Distress term →', 'Devanagari'], 'akela → अकेला'), (7, ['Truncate'], '≤ 128 sub-word tokens')]]
    step(f, X[2], 56, Wc, 66, *rows[0][0])
    ys, h = [56, 148, 240], 66
    for r in (1, 2):
        y = ys[r]
        prev_x = X[2] if r == 1 else X[2]
        f.arrow((prev_x + Wc / 2, ys[r - 1] + h), (prev_x + Wc / 2, y - 13), (X[0] + Wc / 2, y - 13), (X[0] + Wc / 2, y - 2))
        for i, (n, ti, ex) in enumerate(rows[r]):
            step(f, X[i], y, Wc, h, n, ti, ex)
            if i: f.arrow((X[i - 1] + Wc, y + h / 2), (X[i] - 2, y + h / 2))
    y = 332
    f.arrow((X[2] + Wc / 2, ys[2] + h), (X[2] + Wc / 2, y - 13), (X[0] + Wc / 2, y - 13), (X[0] + Wc / 2, y - 2))
    w3 = [214, 160, 160]; x3 = [12, 12 + 214 + 12, 12 + 214 + 12 + 160 + 12]
    f.process(x3[0], y, w3[0], 100, [('Language tag + CMI score', 'T'), ('CMI = 100·[1 − max' + S('l') + ' w' + S('l') + ' / (n − u)]', 's')])
    f.arrow((x3[0] + w3[0], y + 50), (x3[1] - 2, y + 50))
    f.process(x3[1], y, w3[1], 100, [('Timestamp →', 'T'), ('6 features', 'T'), ('month · day · hour ·', 's'), ('weekday · workday ·', 's'), ('weekend (min–max)', 's')])
    f.arrow((x3[1] + w3[1], y + 50), (x3[2] - 2, y + 50))
    f.process(x3[2], y, w3[2], 100, [('User-disjoint split', 'T'), ('source platforms Π' + S('s') + ' →', 's'), ('train / val (stratified', 's'), ('85 / 15); target Π' + S('t') + ' →', 's'), ('frozen test, scored once', 's')])
    f.arrow((x3[2] + w3[2] / 2, y + 100), (x3[2] + w3[2] / 2, 446))
    f.term(x3[2] + w3[2] / 2 - 30, 448, 60, 24, 'End')
    return f.save()


# =============================== 3. Feature extraction ===============================
def lane_head(f, x, y, w, title, tag):
    f.t(x + 10, y + 19, title, 13.5, 'bold', INK)
    f.t(x + w - 10, y + 19, tag, 13.5, 'bold', f.c, 'end', mono=True)


def phase3():
    f = Fig(3, 'Feature Extraction', 536)
    c = f.c
    f.term(12, 56, 56, 26, 'Start')
    f.arrow((68, 69), (82, 69))
    f.io(84, 54, 300, 30, [('post x' + S('k') + ' + earlier posts of user u', 's')], center=True)
    # four signal lanes: bus from the input
    f.arrow((234, 84), (234, 94), head=False)
    f.arrow((90, 94), (450, 94), head=False)
    f.arrow((90, 94), (90, 104)); f.arrow((450, 94), (450, 104))
    # text signal
    x, y, w, h = 12, 106, 300, 140
    f.process(x, y, w, h, [])
    lane_head(f, x, y, w, 'Text signal', 'h_text')
    f.t(x + 10, y + 38, 'MuRIL (Indian-language BERT)', BASE, fill=SUB)
    tx = x + 10
    for t in ['kuch', 'accha', 'NEG', 'bahut', 'अकेला', '…']:
        tw = width(t, BASE, mono=t not in ('अकेला', '…')) + 10
        f.chip(tx, y + 48, tw, 22, t, c, fill='#fff', tc=INK, bold=False, mono=t not in ('अकेला', '…'))
        f.arrow((tx + tw / 2, y + 70), (tx + tw / 2, y + 82), sw=1.1)
        tx += tw + 5
    f.predefined(x + 10, y + 84, 208, 26, [('MuRIL encoder + MeanPool', 'wb')], fill=c, col=c)
    f.arrow((x + 218, y + 97), (x + 226, y + 97), sw=1.2)
    for i in range(8):
        f.e(f'<rect x="{x + 228 + i * 8.5}" y="{y + 90}" width="7.5" height="14" rx="1" fill="{c}" opacity="{0.25 + 0.09 * ((i * 5) % 8):.2f}"/>')
    f.t(x + 256, y + 128, '∈ ℝ' + '<tspan baseline-shift="super" font-size="10">768</tspan>', BASE, fill=SUB, anchor='middle')
    # sentiment / lexicon
    x, y, w, h = 330, 106, 240, 140
    f.process(x, y, w, h, [])
    lane_head(f, x, y, w, 'Sentiment / lexicon', 's_lex')
    f.t(x + 10, y + 40, 'class-wise distress-lexicon hits', BASE)
    f.t(x + 10, y + 57, 'emotion distribution (XLM-EMO)', BASE)
    for i, (lab, v) in enumerate([('sad', .8), ('fear', .3), ('joy', .1)]):
        f.t(x + 46, y + 84 + i * 18, lab, BASE, anchor='end')
        f.bar(x + 52, y + 75 + i * 18, 120, 10, v, c)
    # second row: behavioural + temporal
    x, y, w, h = 12, 270, 200, 96
    f.process(x, y, w, h, [])
    lane_head(f, x, y, w, 'Behavioural', 's_beh')
    for i, s in enumerate(['posting rate ·', 'night-time share ·', 'mean gap between posts']):
        f.t(x + 10, y + 40 + i * 17, s, BASE)
    x, y, w, h = 226, 270, 344, 156
    f.process(x, y, w, h, [])
    lane_head(f, x, y, w, 'Temporal (recency-weighted)', 's_tmp')
    ty = y + 52
    f.arrow((x + 20, ty), (x + 300, ty), sw=1.3)
    for i, xi in enumerate([40, 86, 126, 184, 228]):
        f.e(f'<circle cx="{x + xi}" cy="{ty}" r="7" fill="{c}" opacity="{0.2 + 0.18 * i:.2f}"/>')
    f.e(f'<circle cx="{x + 268}" cy="{ty}" r="8" fill="#fff" stroke="#d1495b" stroke-width="2.2"/>')
    f.t(x + 22, ty - 13, 'older', BASE, style='italic'); f.t(x + 228, ty - 13, 'now', BASE, fill='#d1495b', anchor='middle', style='italic')
    f.t(x + 40, ty + 24, 'h' + S('1'), BASE, anchor='middle'); f.t(x + 228, ty + 24, 'h' + S('k−1'), BASE, anchor='middle')
    f.t(x + 268, ty + 24, 'x' + S('k'), BASE, 'bold', '#d1495b', 'middle')
    f.t(x + 10, y + 108, 's' + S('tmp') + ' = Σ' + S('j&lt;k') + ' α' + S('j') + 'h' + S('j') + ',  α' + S('j') + ' ∝ exp(−λ(t' + S('k') + ' − t' + S('j') + '))', 13.5, fill=INK)
    f.t(x + 10, y + 128, '+ drift velocity v: mean cosine distance', BASE)
    f.t(x + 10, y + 145, '   between successive post embeddings', BASE)
    # lanes from the bus: text + sentiment in row 1, behavioural + temporal reached by side rails
    f.arrow((321, 94), (321, 258), (112, 258), (112, 268))
    f.arrow((321, 258), (398, 258), (398, 268))
    # leakage annotation tied to the history-based lanes
    f.note(12, 378, 200, 48, [('Only past posts (t' + S('j') + ' &lt; t' + S('k') + ') used', 'b'), ('→ no future leakage', 'b')])
    f.arrow((112, 378), (112, 366), dash='3 3', sw=1.1, head=False)
    # fusion
    y = 444
    rail = 576
    f.arrow((570, 176), (rail, 176), (rail, 434), head=False)
    f.arrow((570, 348), (rail, 348), head=False)
    f.arrow((12, 176), (6, 176), (6, 434), head=False)
    f.arrow((12, 318), (6, 318), head=False)
    f.arrow((6, 434), (rail, 434), head=False)
    f.arrow((180, 434), (180, y - 2))
    f.process(12, y, 330, 82, [])
    f.t(22, y + 19, 'Feature fusion', 13.5, 'bold', INK)
    f.t(22, y + 39, 'z = [ h_text ; W' + S('a') + '(s_lex, s_beh, s_tmp, v) ]', BASE, fill=INK)
    sx = 22
    for sw_, col in [(150, c), (36, '#b4c5df'), (30, '#cbd7ea'), (36, '#dde6f2')]:
        f.e(f'<rect x="{sx}" y="{y + 46}" width="{sw_}" height="16" rx="2" fill="{col}" stroke="#fff"/>'); sx += sw_
    f.t(97, y + 58.5, 'h_text (768-d)', BASE, 'bold', '#fff', 'middle')
    f.t(223, y + 58.5, 'projected aux.', BASE, fill=INK, anchor='middle')
    f.t(22, y + 76, 'text embedding ⊕ projected auxiliary signals', BASE, style='italic')
    f.arrow((342, y + 41), (360, y + 41))
    f.io(362, y + 22, 110, 38, [('z', 'T')], center=True)
    f.arrow((472, y + 41), (490, y + 41))
    f.term(492, y + 28, 60, 26, 'End')
    return f.save()


# =============================== 4. Multi-expert classification ===============================
def phase4():
    f = Fig(4, 'Multi-Expert Classification', 500)
    c = f.c
    f.term(12, 58, 56, 26, 'Start')
    f.arrow((68, 71), (82, 71))
    f.io(84, 56, 96, 30, [('input z', 'c')], center=True)
    f.arrow((132, 86), (132, 102))
    f.predefined(30, 104, 190, 50, [('Gating network', 'T'), ('g = softmax(W' + S('g') + ' z)', 's')])
    EXP = [('E₁  Depression', '#4e79a7', .61), ('E₂  Anxiety', '#e8892b', .14), ('E₃  Suicide-Risk', '#d1495b', .17), ('E₄  Normal', '#59a14f', .08)]
    ex, ew, ey0, st = 244, 144, 104, 52
    mx, bus, sx = ex + ew + 22, 470, 504          # multiply nodes, output bus, sum node
    f.arrow((180, 71), (230, 71), (230, ey0 + 3 * st + 21), head=False)   # z goes to every expert
    for i, (lab, col, g) in enumerate(EXP):
        yy = ey0 + i * st
        f.arrow((230, yy + 21), (ex - 2, yy + 21), sw=1.3)
        f.predefined(ex, yy, ew, 42, [(lab, 'b'), ('2-layer FFN', 's')], col=col, center=False)
        f.arrow((ex + ew, yy + 21), (mx - 12, yy + 21), sw=1.3)
        f.e(f'<circle cx="{mx}" cy="{yy + 21}" r="10" fill="#fff" stroke="{LINE}" stroke-width="1.4"/>')
        f.t(mx, yy + 26, '×', 15, 'bold', INK, 'middle')
        f.t(mx + 16, yy + 14, f'g{i + 1}', BASE)
        f.bar(mx + 16, yy + 20, 34, 8, g, col)
        f.arrow((mx + 10, yy + 21), (mx + 14, yy + 21), head=False, sw=1.3)
        f.arrow((mx + 52, yy + 21), (bus, yy + 21), head=False, sw=1.3)
    f.arrow((bus, ey0 + 21), (bus, ey0 + 3 * st + 21), head=False, sw=1.3)
    scy = ey0 + 3 * st / 2 + 21
    f.arrow((bus, scy), (sx - 16, scy), sw=1.3)
    f.e(f'<circle cx="{sx}" cy="{scy}" r="14" fill="#fff" stroke="{c}" stroke-width="1.8"/>')
    f.t(sx, scy + 6, 'Σ', 17, 'bold', c, 'middle')
    f.t(574, scy - 22, 'o = Σ g' + S('m') + ' E' + S('m') + '(z)', BASE, fill=INK, anchor='end')
    # gate weights (dashed) to the multiply nodes
    f.arrow((125, 154), (125, 332), (mx, 332), (mx, ey0 + 3 * st + 33), dash='4 3', sw=1.3)
    for i in range(1, 4):
        f.arrow((mx, ey0 + i * st + 11), (mx, ey0 + (i - 1) * st + 31), dash='3 3', sw=1.0, head=False)
    f.label(133, 326, 'weights g', style='italic', w='normal')
    f.arrow((sx, scy + 14), (sx, 288))
    f.process(430, 290, 140, 32, [('p = softmax(W' + S('o') + ' o)', 's')], center=True)
    f.arrow((500, 322), (500, 346))
    f.io(296, 348, 274, 104, [], fill='#fff')
    f.t(318, 368, 'Class probabilities p', 13.5, 'bold', INK)
    for i, (lab, col, pv) in enumerate([('Depression', '#4e79a7', .71), ('Anxiety', '#e8892b', .12), ('Suicide-Risk', '#d1495b', .11), ('Normal', '#59a14f', .06)]):
        yy = 376 + i * 18.5
        f.t(396, yy + 11, lab, BASE, anchor='end')
        f.bar(402, yy + 2, 100, 11, pv, col)
        f.t(508, yy + 12, f'{pv:.2f}', BASE, 'bold' if i == 0 else 'normal', INK)
    f.arrow((433, 452), (433, 466))
    f.term(403, 468, 60, 24, 'End')
    # training objective: dashed annotation (training only)
    f.note(12, 348, 268, 104, [], col=c, fill='#fff')
    f.t(22, 368, 'Training objective', 13.5, 'bold', INK)
    f.t(270, 368, 'train only', BASE, fill=c, anchor='end', style='italic')
    for i, s in enumerate(['class-weighted focal loss (γ = 2)', '+ η · load-balancing on gate g', 'AdamW · early stop on val macro-F1']):
        f.t(22, 390 + i * 19, s, BASE)
    return f.save()


# =============================== 5. Explanation & recommendation ===============================
def phase5():
    f = Fig(5, 'Explanation &amp; Recommendation', 556)
    c = f.c
    f.term(12, 60, 56, 26, 'Start')
    f.arrow((68, 73), (82, 73))
    f.io(84, 52, 300, 44, [('Prediction', 'c'), ('ŷ = Depression,  confidence p = 0.71', 'b')])
    f.arrow((234, 96), (234, 106), head=False)
    f.arrow((150, 106), (420, 106), head=False)
    f.arrow((150, 106), (150, 116)); f.arrow((420, 106), (420, 116))
    x, y, w, h = 12, 118, 300, 110
    f.process(x, y, w, h, [])
    f.t(x + 10, y + 19, 'Token attribution · Integrated Gradients', 13.5, 'bold', INK)
    toks = [('kuch', .05), ('accha', .25), ('NEG_nahi', .55), ('lagta', .05), ('bahut', .35), ('अकेला', .95), ('feel', .1), ('hota', .02), ('hai', .02), (':disappointed:', .6)]
    tx, ty = x + 10, y + 28
    for t, a in toks:
        tw = width(t, BASE, a > .5) + 12
        if tx + tw > x + w - 8: tx, ty = x + 10, ty + 27
        f.e(f'<rect x="{tx}" y="{ty}" width="{tw}" height="22" rx="4" fill="{c}" fill-opacity="{0.08 + 0.8 * a:.2f}"/>')
        f.t(tx + tw / 2, ty + 15.5, t, BASE, 'bold' if a > .5 else 'normal', '#fff' if a > .5 else INK, 'middle')
        tx += tw + 4
    f.t(x + 10, y + h - 9, 'darker = stronger evidence for ŷ', BASE, style='italic')
    x, y, w, h = 330, 118, 240, 110
    f.process(x, y, w, h, [])
    f.t(x + 10, y + 19, 'Signal attribution · SHAP', 13.5, 'bold', INK)
    for i, (lab, v) in enumerate([('s_lex', .21), ('s_tmp', .14), ('s_beh', .06), ('v (drift)', .03)]):
        yy = y + 30 + i * 19
        f.t(x + 82, yy + 12, lab, BASE, anchor='end', mono=True)
        f.e(f'<rect x="{x + 88}" y="{yy + 2}" width="{v * 520}" height="12" rx="2" fill="{c}" fill-opacity="0.75"/>')
        f.t(x + 94 + v * 520, yy + 12.5, f'+{v:.2f}', BASE, fill=INK)
    f.arrow((162, 228), (162, 240), head=False); f.arrow((450, 228), (450, 240), head=False)
    f.arrow((162, 240), (450, 240), head=False)
    f.arrow((291, 240), (291, 250))
    dcx, dcy = 291, 294
    f.decision(dcx, dcy, 290, 86, [('Safety guard-rail', 'c'), ('ŷ = Suicide-Risk or', 'b'), ('p(Suicide-Risk) ≥ τ' + S('s') + ' ?', 'b')])
    hx, hw, rx, rw = 12, 250, 274, 296
    f.arrow((dcx - 145, dcy), (dcx - 145, 352))
    f.label(dcx - 152, dcy - 8, 'Yes', fill=c, anchor='end')
    f.arrow((dcx + 145, dcy), (dcx + 145, 352))
    f.label(dcx + 152, dcy - 8, 'No', anchor='start')
    f.process(hx, 354, hw, 92, [('⚠ Crisis helpline shown first', 'wb'), ('Tele-MANAS 14416 + safety message', 'w'), ('+ option to contact a trusted person', 'w'), ('fixed rule — no score can override it', 'wi')], col='#c23b4e', fill='#c23b4e')
    f.process(rx, 354, rw, 92, [], col=c)
    f.t(rx + 10, 373, 'Confidence-matched resources', 13.5, 'bold', INK)
    for i, (a, b) in enumerate([('Dep./Anx., high conf.', 'professional-support info'), ('Dep./Anx., low conf.', 'self-care · check in later'), ('Normal', 'optional well-being info')]):
        f.t(rx + 10, 392 + i * 16, a, BASE, 'bold', INK)
        f.t(rx + rw - 10, 392 + i * 16, b, BASE, 'normal', SUB, 'end')
        if width(a, BASE, True) + width(b, BASE) + 6 > rw - 20: f.overflow.append(('resources row', a))
    f.t(rx + 10, 440, 'non-diagnostic wording', BASE, fill=c, style='italic')
    f.arrow((hx + hw / 2, 446), (hx + hw / 2, 460), head=False); f.arrow((rx + rw / 2, 446), (rx + rw / 2, 460), head=False)
    f.arrow((hx + hw / 2, 460), (rx + rw / 2, 460), head=False)
    f.arrow((291, 460), (291, 472))
    f.io(110, 474, 362, 44, [('OUTPUT = (ŷ, p, explanation e, action a)', 'T'), ("in the post's language · user can dispute", 's')], center=True)
    f.arrow((291, 518), (291, 524))
    f.term(261, 526, 60, 24, 'End')
    return f.save()


# =============================== 6. Experimental evaluation ===============================
LH6 = 15.5


def bullets(f, x, y, w, items, col):
    yy = y
    for b in items:
        if b.startswith('  '):
            f.t(x + 22, yy, b.strip(), BASE, fill=SUB)
        else:
            f.t(x + 10, yy, '•', BASE, 'bold', col); f.t(x + 22, yy, b, BASE, fill=INK)
        if width(b.strip(), BASE) > w - 28: f.overflow.append((round(width(b.strip(), BASE)), w - 28, b))
        yy += LH6
    return yy


def block6(f, x, y, w, h, title, col):  # title: str or list of lines
    lines = [title] if isinstance(title, str) else title
    hh = 24 + 16 * (len(lines) - 1)
    f.e(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="#fff" stroke="{EDGE}" stroke-width="1.0"/>')
    f.e(f'<path d="M{x},{y + hh} v{-(hh - 4)} a4,4 0 0 1 4,-4 h{w - 8} a4,4 0 0 1 4,4 v{hh - 4} z" fill="{ACC}" stroke="{EDGE}" stroke-width="1.0"/>')
    for i, t in enumerate(lines):
        f.t(x + w / 2, y + 17 + 16 * i, t, 13.5, 'bold', '#fff', 'middle')
        if width(t, 13.5, True) > w - 8: f.overflow.append((round(width(t, 13.5, True)), w - 8, t))


def phase6():
    f = Fig(6, 'Experimental Evaluation &amp; Analysis', 566)
    f.term(12, 52, 56, 24, 'Start')
    f.t(78, 69, 'train on YouTube → test once on unseen Reddit + X', BASE, fill=f.c, style='italic')
    X, Wc = [12, 205, 398], 172
    y1, h1 = 84, 248
    f.arrow((40, 76), (40, 82))
    block6(f, X[0], y1, Wc, h1, 'Baseline Models', '#4e79a7')
    bullets(f, X[0], y1 + 42, Wc, ['Majority class', 'Linear probe', '  (frozen MuRIL)', 'Text-only variant', 'BGE-M3 + XGBoost', 'BGE-M3 + emotion', '  + time + XGBoost',
                                  'Backbones: MuRIL /', '  XLM-R / IndicBERT v2', '  (probe, fine-tune)'], ACC)
    f.arrow((X[0] + Wc, y1 + h1 / 2), (X[1] - 2, y1 + h1 / 2))
    block6(f, X[1], y1, Wc, h1, 'Training Protocol', '#6a4fb8')
    f.chip(X[1] + 4, y1 + 32, Wc - 8, 24, 'Train: YouTube (Π' + S('s') + ')', '#4e79a7', fill='#fff', bold=False)
    f.arrow((X[1] + 40, y1 + 56), (X[1] + 40, y1 + 74), sw=1.4)
    f.t(X[1] + 48, y1 + 70, 'test once', BASE, style='italic')
    f.chip(X[1] + 4, y1 + 76, Wc - 8, 24, 'Test: Reddit + X (Π' + S('t') + ', frozen)', '#d1495b', fill='#fff', bold=False)
    bullets(f, X[1], y1 + 122, Wc, ['5 seeds · 95 % CI', '5-fold in-platform CV', '  → gap', 'paired t-test +', '  Benjamini–Hochberg', '4,614 real posts,', '  user-disjoint'], ACC)
    f.arrow((X[1] + Wc, y1 + h1 / 2), (X[2] - 2, y1 + h1 / 2))
    block6(f, X[2], y1, Wc, h1, ['Performance', 'Evaluation Measures'], '#e8892b')
    cats = [('Classification', ['Macro-F1 · MCC ·', 'Crisis recall · P/R/F1']), ('Probabilistic', ['macro one-vs-rest', 'ROC-AUC']),
            ('Early risk (user)', ['ERDE₅ · ERDE₅₀ ·', 'precision / recall']), ('Visualisations', ['confusion matrix ·', 'gap plot · ablation'])]
    yy = y1 + 46
    for a, bs in cats:
        hh = 17 + 15 * len(bs)
        f.e(f'<rect x="{X[2] + 6}" y="{yy}" width="{Wc - 12}" height="{hh}" rx="4" fill="{TINT}" stroke="#b9c3d3" stroke-width="0.8"/>')
        f.t(X[2] + 13, yy + 14, a, BASE, 'bold', ACC)
        for j, b in enumerate(bs):
            f.t(X[2] + 13, yy + 29 + j * 15, b, BASE, fill=INK)
            if width(b, BASE) > Wc - 26: f.overflow.append((round(width(b, BASE)), Wc - 26, b))
        yy += hh + 3
    assert yy <= y1 + h1, yy
    y2, h2 = 354, 200
    f.arrow((X[2] + Wc / 2, y1 + h1), (X[2] + Wc / 2, y1 + h1 + 11), (X[0] + Wc / 2, y1 + h1 + 11), (X[0] + Wc / 2, y2 - 2))
    block6(f, X[0], y2, Wc, h2, 'Explainability Analysis', '#d1495b')
    bullets(f, X[0], y2 + 42, Wc, ['Global SHAP token', '  ranking', 'Overlap with distress', '  lexicon', 'SHAP / LIME / IG', '  agreement (top-token', '  Jaccard)', 'Per-post case inspection', 'Signal vs text', '  contribution'], ACC)
    f.arrow((X[0] + Wc, y2 + h2 / 2), (X[1] - 2, y2 + h2 / 2))
    block6(f, X[1], y2, Wc, h2, 'Ablation Study', '#59a14f')
    bullets(f, X[1], y2 + 42, Wc, ['Text-only fusion (no aux.)', 'ELU gate removed', 'Concat vs attention', '  fusion', 'Dynamic vs static routing', 'CE vs focal + contrastive', 'Real vs synthetic training'], ACC)
    f.arrow((X[1] + Wc, y2 + h2 / 2), (X[2] - 2, y2 + h2 / 2))
    block6(f, X[2], y2, Wc, 142, 'SOTA Comparison', '#7a6a2a')
    bullets(f, X[2], y2 + 42, Wc, ['Closest published', '  settings (Table 10)', 'Cross-platform drop', '  44 % vs 41 % [7]', 'Not a ranking:', '  data / labels differ'], ACC)
    f.arrow((X[2] + Wc / 2, y2 + 142), (X[2] + Wc / 2, y2 + 166))
    f.term(X[2] + Wc / 2 - 30, y2 + 168, 60, 26, 'End')
    return f.save()


ok = all([phase1(), phase2(), phase3(), phase4(), phase5(), phase6()])
sys.exit(0 if ok else 1)
