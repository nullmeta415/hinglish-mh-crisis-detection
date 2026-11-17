"""Fig. 1 (proposed methodology) in the style of reference-sources/author_1 Fig. 1 ("Data Flow Diagram"):
pastel stage bands with a dashed border and a serif stage tab; left-to-right flow inside each band;
icon + bold title + regular detail in each box; two-part cards (tinted header with icon, white body) for the
signal and expert blocks; branches merging into one centred box; orthogonal dark arrows.
Content = the original Stage 1-5 figure. Canvas 582 units = 466 pt text width at 0.8 pt/unit (12.5 units = 10 pt).
Writes fig1_bands.svg/.png (300 dpi via chromium). Usage: python make_fig1_bands.py"""
import re, subprocess, sys, tempfile
from pathlib import Path
from PIL import ImageFont

HERE = Path(__file__).parent
W = int(sys.argv[1]) if len(sys.argv) > 1 else 790   # wide canvas, printed at the 466 pt text width
PT, DPI, BASE, LH = 466 / W, 300, 12.5, 15.5         # 12.5-unit text prints at 12.5 * 466 / W pt
SANS = "'Times New Roman', 'Liberation Serif', 'Noto Serif Devanagari', 'Noto Sans Devanagari', serif"  # all figure text in Times New Roman (Liberation Serif = metric clone)
SERIF = "'Liberation Serif', 'Times New Roman', serif"
INK, SUB, LINE = '#1d1d1f', '#3c3c41', '#2e2e33'
# band: fill, dashed edge, tab fill, box border, icon colour, header tint
BAND = {1: ('#eef5fc', '#a9c9ea', '#cfe2f6', '#6b9bd1', '#2f6db3', '#dde9f8'),
        2: ('#eff8f0', '#acd7b1', '#d3ecd6', '#6fae76', '#2f8a3b', '#dff0e1'),
        3: ('#fffaeb', '#ecd393', '#f7e7b8', '#d1a53c', '#a87a12', '#fbefcc'),
        4: ('#f4f0fb', '#c7b8e8', '#e0d7f4', '#9581cc', '#5f45a8', '#e9e2f7'),
        5: ('#fdf0f0', '#ebb3b3', '#f6d3d3', '#cf7b7b', '#b03a3a', '#f9e0e0')}
CLS = {'Depression': ('#4e79a7', '#dfe8f3'), 'Anxiety': ('#e8892b', '#fbe9d6'),
       'Suicide-Risk': ('#d1495b', '#f8dde1'), 'Normal': ('#59a14f', '#e1f0df')}
_F = {}
o, overflow = [], []


def width(s, size, bold=False, serif=False):
    key = (size, bold, serif)
    if key not in _F:
        name = 'LiberationSerif' + ('-Bold' if bold else '-Regular')
        _F[key] = ImageFont.truetype(subprocess.run(['fc-match', '-f', '%{file}', name], capture_output=True, text=True).stdout, size)
    subs = ''.join(re.findall(r'<tspan baseline[^>]*>([^<]*)</tspan>', s))
    plain = re.sub(r'<[^>]+>', '', s).replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    return _F[key].getlength(plain) - _F[key].getlength(subs) + (width(subs, 10, bold, serif) if subs else 0)


def S(t): return f'<tspan baseline-shift="sub" font-size="10">{t}</tspan>'
def B(t): return f'<tspan font-weight="bold" fill="{INK}">{t}</tspan>'
def e(s): o.append(s)


def t(x, y, s, size=BASE, wt='normal', fill=INK, anchor='start', fam=SANS):
    e(f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{size}" font-weight="{wt}" fill="{fill}" text-anchor="{anchor}">{s}</text>')


def arrow(*pts, head=True):
    m = ' marker-end="url(#ah)"' if head else ''
    e(f'<polyline points="{" ".join(f"{a},{b}" for a, b in pts)}" fill="none" stroke="{LINE}" stroke-width="1.2" stroke-linejoin="round"{m}/>')


def dot(x, y): e(f'<circle cx="{x}" cy="{y}" r="2.4" fill="{LINE}"/>')


ICON = {  # line icons on an 18x18 grid
    'chat': '<path d="M2,3 h14 a1,1 0 0 1 1,1 v8 a1,1 0 0 1 -1,1 h-8 l-4,3 v-3 h-2 a1,1 0 0 1 -1,-1 v-8 a1,1 0 0 1 1,-1 z"/><path d="M5,7 h8 M5,10 h5"/>',
    'db': '<ellipse cx="9" cy="3.5" rx="7" ry="2.5"/><path d="M2,3.5 v11 a7,2.5 0 0 0 14,0 v-11 M2,9 a7,2.5 0 0 0 14,0"/>',
    'book': '<path d="M9,4 C7,2.5 4,2.5 1.5,3 v12 C4,14.5 7,14.5 9,16 C11,14.5 14,14.5 16.5,15 v-12 C14,2.5 11,2.5 9,4 z M9,4 v12"/>',
    'shield': '<path d="M9,1.5 L16,4 v5 c0,4 -3,6.5 -7,8 c-4,-1.5 -7,-4 -7,-8 v-5 z"/><path d="M6,9 l2,2 l4,-4"/>',
    'text': '<path d="M1.5,3 h9 M6,3 v12 M10,8 h6.5 M13.25,8 v7"/>',
    'clock': '<circle cx="9" cy="9" r="7.5"/><path d="M9,4.5 v4.5 l3,2"/>',
    'net': '<circle cx="3" cy="4" r="2"/><circle cx="3" cy="14" r="2"/><circle cx="15" cy="9" r="2"/><circle cx="9" cy="9" r="2"/><path d="M5,4.5 L7.2,8 M5,13.5 L7.2,10 M11,9 h2"/>',
    'bars': '<path d="M1.5,16.5 h15"/><rect x="3" y="9" width="3" height="7.5"/><rect x="7.5" y="5" width="3" height="11.5"/><rect x="12" y="2" width="3" height="14.5"/>',
    'user': '<circle cx="6.5" cy="5" r="3"/><path d="M1,16 c0,-4 2.5,-6 5.5,-6 s5.5,2 5.5,6"/><circle cx="13.5" cy="6" r="2.2"/><path d="M12.5,10.3 c2.5,0 4.5,1.8 4.5,5"/>',
    'merge': '<path d="M1.5,3 h4 l5,6 h6 M1.5,15 h4 l5,-6"/><path d="M13.5,6.5 l3,2.5 l-3,2.5"/>',
    'gear': '<circle cx="9" cy="9" r="2.8"/><circle cx="9" cy="9" r="5.5"/><path d="M9,1 v2.5 M9,14.5 v2.5 M1,9 h2.5 M14.5,9 h2.5 M3.3,3.3 l1.8,1.8 M12.9,12.9 l1.8,1.8 M3.3,14.7 l1.8,-1.8 M12.9,5.1 l1.8,-1.8"/>',
    'search': '<path d="M3,1.5 h7 l3,3 v4 M3,1.5 v15 h6"/><circle cx="12" cy="13" r="2.8"/><path d="M14,15 l2.5,2.5"/>',
    'bulb': '<path d="M6,13 c0,-2 -3.5,-3.5 -3.5,-7 a6.5,6.5 0 0 1 13,0 c0,3.5 -3.5,5 -3.5,7 z M6.5,15.5 h5 M7.5,17.5 h3"/>',
}


def icon(kind, x, y, c, s=22, tile=False):
    if tile:  # filled rounded tile with a white glyph (the reference's source "logo" tiles)
        e(f'<rect x="{x}" y="{y}" width="{s}" height="{s}" rx="{s * 0.22}" fill="{c}"/>')
        x, y, s, c = x + s * 0.18, y + s * 0.18, s * 0.64, '#fff'
    k = s / 18
    e(f'<g fill="none" stroke="{c}" stroke-width="{1.6 / k:.2f}" stroke-linecap="round" stroke-linejoin="round" '
      f'transform="translate({x},{y}) scale({k:.3f})">{ICON[kind]}</g>')


def lines_at(x, y0, avail, lines, center=False):
    for i, (s, bold) in enumerate(lines):
        wd = width(s, BASE, bold) * 1.06  # chromium sets text ~5% wider than PIL measures
        if wd > avail + 0.5: overflow.append((round(wd), round(avail), re.sub('<[^>]+>', '', s)))
        t(x + avail / 2 if center else x, y0 + i * LH, s, BASE, 'bold' if bold else 'normal', INK if bold else SUB, 'middle' if center else 'start')


def bh(n): return 12 + LH * n
def ty(y, h, n): return y + (h - LH * n) / 2 + LH * 0.74  # first baseline of n centred lines


def box(x, y, w, h, lines, band, ic, fill='#fff', top=False):
    """Process box: thin coloured border, icon at left (or on top), bold title + regular detail."""
    col, icol = BAND[band][3], BAND[band][4]
    e(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{fill}" stroke="{col}" stroke-width="1.1"/>')
    if top:
        icon(ic, x + w / 2 - 11, y + 8, icol)
        lines_at(x + 7, ty(y + 32, bh(len(lines)), len(lines)), w - 14, lines, center=True)  # text directly under the icon
    else:
        icon(ic, x + 9, y + h / 2 - 11, icol)
        lines_at(x + 40, ty(y, h, len(lines)), w - 52, lines)


def card(x, y, w, hh, hb, head, body, col, tint, ic=None):
    """Two-part card: tinted header (icon + bold title), white body (centred detail)."""
    e(f'<rect x="{x}" y="{y}" width="{w}" height="{hh + hb}" rx="4" fill="#fff" stroke="{col}" stroke-width="1.1"/>')
    e(f'<path d="M{x},{y + hh} v{-(hh - 4)} a4,4 0 0 1 4,-4 h{w - 8} a4,4 0 0 1 4,4 v{hh - 4} z" fill="{tint}" stroke="{col}" stroke-width="1.1"/>')
    if ic:
        icon(ic, x + 8, y + hh / 2 - 10, col, 20)
        lines_at(x + 34, ty(y, hh, len(head)), w - 40, head)
    else:
        lines_at(x + 6, ty(y, hh, len(head)), w - 12, head, center=True)
    lines_at(x + 6, ty(y + hh, hb, len(body)), w - 12, body, center=True)


X0, TABW = 4, 82
XC, XR = X0 + TABW + 14, W - 10
CW = XR - XC
G, PAD = 9, 10


def band(k, y, h, label):
    fill, edge, tab = BAND[k][:3]
    e(f'<rect x="{X0}" y="{y}" width="{W - 2 * X0}" height="{h}" rx="6" fill="{fill}" stroke="{edge}" stroke-width="1" stroke-dasharray="5 3"/>')
    e(f'<rect x="{X0 + 6}" y="{y + 8}" width="{TABW}" height="40" rx="2" fill="{tab}" stroke="{edge}" stroke-width="0.8"/>')
    for i, s in enumerate(label):
        t(X0 + 13, y + 24 + i * 16, s, 13.5, 'bold', INK, fam=SERIF)
        if width(s, 13.5, True, True) > TABW - 10: overflow.append(('tab', s))
    return y + h


y = 4
# ---- Stage 1: data sources (icon tiles + label) merged by a bracket bus ----
h1 = bh(3)
y_end = band(1, y, PAD + h1 + 18, ['Stage 1', 'Data'])
src = [('chat', [('Newly collected', 1), ('Hinglish posts', 1), ('(YouTube, Reddit, X)', 0)]),
       ('db', [('Existing Hinglish', 1), ('suicidal-ideation corpus', 1), ('(Agarwal &amp; Dhingra)', 0)]),
       ('book', [('Existing English', 1), ('condition corpora', 1), ('(label-mapped)', 0)])]
sw_ = CW / 3
ys = y + PAD
cx_src = []
for i, (ic, ln) in enumerate(src):
    x = XC + i * sw_
    icon(ic, x + 2, ys + h1 / 2 - 15, BAND[1][4], 30, tile=True)
    lines_at(x + 40, ty(ys, h1, len(ln)), sw_ - 44, ln)
    cx_src.append(x + 17)
bus1 = ys + h1 + 9
for cx in cx_src: arrow((cx, ys + h1 / 2 + 17), (cx, bus1), head=False)
arrow((cx_src[0], bus1), (cx_src[2], bus1), head=False)
y = y_end + G

# ---- Stage 2: one row, De-identification -> Text normalisation, and -> Timestamp features (over the top) ----
h2 = bh(4)
y_end = band(2, y, PAD + 6 + h2 + PAD, ['Stage 2', 'Preparation'])
ya = y + PAD + 6
gp = 10
wa, wt = 250, 200  # sized to their longest lines
xa, xt = XC, XC + wa + gp
xh = xt + wt + gp
wh = XR - xh
arrow((cx_src[0], bus1), (cx_src[0], ya - 1))
box(xa, ya, wa, h2, [('De-identification ·', 1), ('label mapping · de-duplication', 1), ('user-disjoint, platform-', 0), ('tagged split', 0)], 2, 'shield')
box(xt, ya, wt, h2, [('Text normalisation,', 1), ('CMI tagging,', 1), ('roman→Devanagari', 0), ('transliteration', 0)], 2, 'text')
box(xh, ya, wh, h2, [('Timestamp features', 1), ('&amp; per-user posting', 1), ('history (post_seq)', 0)], 2, 'clock')
arrow((xa + wa, ya + h2 / 2), (xt - 1, ya + h2 / 2))
yo2 = ya - 7
arrow((xa + wa - 24, ya), (xa + wa - 24, yo2), (xh + wh / 2, yo2), (xh + wh / 2, ya - 1))
y_b2 = ya + h2
y = y_end + G

# ---- Stage 3: signal cards merging into the fusion box ----
hh3, hb3, hf = bh(1), bh(1), bh(1)
h3 = hh3 + hb3 + 26 + hf
y_end = band(3, y, PAD + h3 + PAD, ['Stage 3', 'Signals'])
yc = y + PAD
gap = 12
ws = [0.29 * CW, 0.31 * CW]
ws.append(CW - sum(ws) - 2 * gap)
xs = [XC, XC + ws[0] + gap, XC + ws[0] + ws[1] + 2 * gap]
cxs = [x_ + w_ / 2 for x_, w_ in zip(xs, ws)]
c3, tint3 = BAND[3][3], BAND[3][5]
card(xs[0], yc, ws[0], hh3, hb3, [('Language encoder MuRIL', 1)], [('→ h_text', 0)], c3, tint3, 'net')
card(xs[1], yc, ws[1], hh3, hb3, [('Sentiment / lexicon signal', 1)], [('→ s_lex', 0)], c3, tint3, 'bars')
card(xs[2], yc, ws[2], hh3, hb3, [('Behavioural + temporal signal', 1)], [('(recency-weighted) → s_beh, s_tmp', 0)], c3, tint3, 'user')
# Stage 2 -> Stage 3: text box feeds encoder + lexicon, timestamps/history feed behavioural + temporal
assert xt < cxs[1] < xt + wt and xh < cxs[2] < xh + wh, (xt, cxs, xh)
ymid = (y_b2 + yc) / 2
arrow((xt + 16, y_b2), (xt + 16, ymid), (cxs[0], ymid), (cxs[0], yc - 1))
arrow((cxs[1], y_b2), (cxs[1], yc - 1))
arrow((cxs[2], y_b2), (cxs[2], yc - 1))
yb3 = yc + hh3 + hb3
xf_w = 380
xf = XC + (CW - xf_w) / 2
yf = yb3 + 26
for cx in cxs: arrow((cx, yb3), (cx, yb3 + 12), head=False)
arrow((cxs[0], yb3 + 12), (cxs[2], yb3 + 12), head=False)
arrow((XC + CW / 2, yb3 + 12), (XC + CW / 2, yf - 1))
box(xf, yf, xf_w, hf, [(B('Fusion') + '  z = [h_text ; W(s_lex, s_beh, s_tmp)]', 0)], 3, 'merge', fill=tint3)
y_fus = yf + hf
y = y_end + G

# ---- Stage 4: gating network fans out to four expert cards ----
hg, hh4, hb4 = bh(1), 27, 27
h4 = hg + 24 + hh4 + hb4 + 14
y_end = band(4, y, PAD + h4 + PAD, ['Stage 4', 'Model'])
yg = y + PAD
gw = 320
gx = XC + (CW - gw) / 2
arrow((XC + CW / 2, y_fus), (XC + CW / 2, yg - 1))
box(gx, yg, gw, hg, [(B('Gating network') + '  g = softmax(W' + S('g') + ' z)', 0)], 4, 'gear', fill=BAND[4][5])
ye = yg + hg + 24
ew = (CW - 3 * 16) / 4
cxe = [XC + i * (ew + 16) + ew / 2 for i in range(4)]
arrow((XC + CW / 2, yg + hg), (XC + CW / 2, yg + hg + 12), head=False)
arrow((cxe[0], yg + hg + 12), (cxe[3], yg + hg + 12), head=False)
bus4 = ye + hh4 + hb4 + 12
for cx, (c, (col, tint)) in zip(cxe, CLS.items()):
    arrow((cx, yg + hg + 12), (cx, ye - 1))
    card(cx - ew / 2, ye, ew, hh4, hb4, [(c, 1)], [('expert', 0)], col, tint)
    arrow((cx, ye + hh4 + hb4), (cx, bus4), head=False)
arrow((cxe[0], bus4), (cxe[3], bus4), head=False)
y = y_end + G

# ---- Stage 5: output, left to right ----
ho = bh(3)
y_end = band(5, y, PAD + ho + PAD, ['Stage 5', 'Output'])
yo = y + PAD
wp = 0.42 * CW
wq = CW - wp - 30
xq = XC + wp + 30
dot(XC + CW / 2, bus4)
arrow((XC + CW / 2, bus4), (XC + CW / 2, (bus4 + yo) / 2), (XC + wp / 2, (bus4 + yo) / 2), (XC + wp / 2, yo - 1))
box(XC, yo, wp, ho, [('Prediction ŷ, confidence p,', 1), ('SHAP / IG explanation', 0), ('(focal loss, imbalance-aware)', 0)], 5, 'search')
arrow((XC + wp, yo + ho / 2), (xq - 1, yo + ho / 2))
box(xq, yo, wq, ho, [('Recommendation layer', 1), ('Suicide-Risk ⇒ helpline first (fixed rule),', 0), ('else confidence-matched resource', 0)], 5, 'bulb')
H = int(y_end + 5)  # chromium needs an integer window size

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
       f'<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerUnits="userSpaceOnUse" markerWidth="7" markerHeight="7" orient="auto">'
       f'<path d="M0,0 L10,5 L0,10 z" fill="{LINE}"/></marker></defs><rect width="{W}" height="{H}" fill="#fff"/>' + ''.join(o) + '</svg>')
p = HERE / 'fig1_bands.svg'
p.write_text(svg, encoding='utf-8')
with tempfile.TemporaryDirectory() as td:
    html = Path(td) / 'p.html'
    html.write_text(f'<html><body style="margin:0"><img src="file://{p}" style="display:block;width:{W}px;height:{H}px"></body></html>')
    subprocess.run(['chromium', '--headless', '--no-sandbox', '--disable-gpu', '--hide-scrollbars', f'--force-device-scale-factor={PT * DPI / 72}',
                    f'--window-size={W},{H}', f'--screenshot={HERE / "fig1_bands.png"}', f'file://{html}'], check=True, capture_output=True)
print(f'fig1: {W}x{H} units -> {W * PT / 72:.2f} x {H * PT / 72:.2f} in, text {BASE * PT:.1f} pt', 'OVERFLOW ' + str(overflow) if overflow else 'ok')
sys.exit(1 if overflow else 0)
