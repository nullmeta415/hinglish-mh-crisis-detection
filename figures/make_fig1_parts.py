"""Split fig1_pipeline.svg into page-sized parts so every label prints at >= 10 pt (subscripts excepted).
Nothing is redrawn or dropped: parts are crops of the same SVG; panel 6's blocks are re-arranged in a grid.
Scale: 0.8 pt per SVG unit (12.5-unit text = 10 pt); the 12-unit labels are bumped to 12.5.
Writes fig1_part{1..6}.svg/.png. Needs chromium.  Usage: python make_fig1_parts.py"""
import re, subprocess, tempfile
from pathlib import Path

HERE = Path(__file__).parent
src = (HERE / 'fig1_pipeline.svg').read_text(encoding='utf-8').replace('font-size="12"', 'font-size="12.5"')
STUB = '<line x1="1602" y1="792" x2="1602" y2="864" stroke="#3a3a3e" stroke-width="2" marker-end="url(#ah)"/>'
assert src.count(STUB) == 1
src = src.replace(STUB, '')  # phase 5 -> phase 6 link: each phase figure stands alone
src, n = re.subn(r'<path d="M\d+,427 [^>]*/>', '', src)  # the four fat phase-to-phase arrows
assert n == 4, n
inner = src[src.index('>', src.index('<svg')) + 1:src.rindex('</svg>')]
PT = 0.8   # pt per unit
DPI = 300
OPEN = '<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'


def crop(x, y, w, h, dx=0, dy=0):  # nested viewport showing region (x, y, w, h) of the original at (dx, dy)
    return f'<svg x="{dx}" y="{dy}" width="{w}" height="{h}" viewBox="{x} {y} {w} {h}" overflow="hidden">{inner}</svg>'


parts = {}
# panels 1-5: each phase on its own (chevron header + body), no arrows to/from neighbouring phases
for k, (x0, x1) in enumerate([(20, 340), (360, 664), (684, 1068), (1088, 1408), (1428, 1776)], 1):
    w, h = x1 - x0, 802
    parts[k] = (w, h, OPEN.format(w=w, h=h) + '<rect width="100%" height="100%" fill="#fff"/>' + crop(x0, 6, w, h) + '</svg>')

# panel 6: same blocks, grid of rows; elbow arrows keep the left-to-right reading order
C6, BY, BH, G = '#3d4f66', 924, 236, 16
blocks = {'base': (40, 226), 'train': (296, 270), 'perf': (596, 344), 'xai': (970, 214), 'abl': (1214, 214), 'sota': (1458, 172)}
rows = [['base', 'train'], ['perf', 'xai'], ['abl', 'sota', 'END']]
W6 = 582  # 466 pt text width / 0.8
body, y, prev = [], 92, None
for row in rows:
    ws = [96 if b == 'END' else blocks[b][1] for b in row]
    x = (W6 - sum(ws) - G * (len(ws) - 1)) / 2
    assert x >= 3, row
    first = True
    for b, w in zip(row, ws):
        if prev and first:   # elbow from previous row's last block down to this row's first block
            px, py = prev
            mid = y - 13
            body.append(f'<path d="M{px},{py} V{mid} H{x + w / 2} V{y - 3}" fill="none" stroke="#3a3a3e" stroke-width="2" marker-end="url(#ah)"/>')
        elif prev:
            body.append(f'<line x1="{prev[0] + 4}" y1="{y + BH / 2}" x2="{x - 4}" y2="{y + BH / 2}" stroke="#3a3a3e" stroke-width="2" marker-end="url(#ah)"/>')
        if b == 'END':
            body.append(f'<rect x="{x}" y="{y + BH / 2 - 26}" width="{w}" height="52" rx="26" fill="{C6}"/>'
                        f'<text x="{x + w / 2}" y="{y + BH / 2 + 6}" font-family="\'Liberation Sans\', Arial, sans-serif" font-size="16" '
                        f'font-weight="bold" fill="#fff" text-anchor="middle">END</text>')
        else:
            bx, bw = blocks[b]
            body.append(crop(bx - 2, BY - 2, bw + 4, BH + 4, x - 2, y - 2))
        prev = (x + w, y + BH / 2)  # right-middle, for the next arrow in this row
        first = False
        last_cx = x + w / 2
        x += w + G
    prev = (last_cx, y + BH)  # bottom-centre of the row's last block
    y += BH + 26
H6 = y - 26 + 12
head = (f'<rect x="1" y="8" width="{W6 - 2}" height="{H6 - 9}" rx="10" fill="#f4f6f9" stroke="{C6}" stroke-width="1.2" stroke-dasharray="5 4"/>'
        f'<path d="M1,20 L{W6 - 17},20 L{W6 - 1},40 L{W6 - 17},60 L1,60 Z" fill="{C6}"/>'
        f'<circle cx="28" cy="40" r="12" fill="#fff"/>'
        f'<text x="28" y="45.5" font-family="\'Liberation Sans\', Arial, sans-serif" font-size="15" font-weight="bold" fill="{C6}" text-anchor="middle">6</text>'
        f'<text x="48" y="46" font-family="\'Liberation Sans\', Arial, sans-serif" font-size="16.5" font-weight="bold" fill="#fff">Experimental Evaluation &amp; Analysis</text>'
        f'<text x="{W6 / 2}" y="80" font-family="\'Liberation Sans\', Arial, sans-serif" font-size="13.5" font-style="italic" fill="{C6}" text-anchor="middle">train on YouTube → test once on unseen Reddit + X</text>')
defs = re.search(r'<defs>.*?</defs>', inner, re.S).group()
parts[6] = (W6, H6, OPEN.format(w=W6, h=H6) + defs + '<rect width="100%" height="100%" fill="#fff"/>' + head + ''.join(body) + '</svg>')

for k, (w, h, svg) in parts.items():
    p = HERE / f'fig1_part{k}.svg'
    p.write_text(svg, encoding='utf-8')
    scale = PT * DPI / 72 / 1  # device px per unit
    with tempfile.TemporaryDirectory() as td:
        html = Path(td) / 'p.html'
        html.write_text(f'<html><body style="margin:0"><img src="file://{p}" style="display:block;width:{w}px;height:{h}px"></body></html>')
        subprocess.run(['chromium', '--headless', '--no-sandbox', '--disable-gpu', '--hide-scrollbars', f'--force-device-scale-factor={scale}',
                        f'--window-size={w},{h}', f'--screenshot={HERE / f"fig1_part{k}.png"}', f'file://{html}'],
                       check=True, capture_output=True)
    print(f'part {k}: {w}x{h} units -> {w * PT / 72:.2f} x {h * PT / 72:.2f} in')
