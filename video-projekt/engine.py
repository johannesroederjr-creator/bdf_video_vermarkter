"""Grundbausteine: Farben, Schriften, Hintergrund, Text- und Formzeichnung.
Normalerweise muss hier nichts geändert werden (Farben/Schriften ausgenommen)."""
import math, random
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / 'assets'
TEMP = ROOT / 'temp'          # Zwischendateien (darf gelöscht werden)
OUT = ROOT / 'ausgabe'        # fertige Videos
TEMP.mkdir(exist_ok=True); OUT.mkdir(exist_ok=True)

W, H, FPS = 1920, 1080, 30
SW, SH = 1920, 1052           # Aufnahme ohne schwarze Ränder (oben 14 px, unten 14 px)

# ---- Farben (aus der Website betterdecisionsfaster.de) ----
WHITE = (255, 255, 255)
BRAND = (9, 105, 218)         # Website-Akzent #0969da
ACC = (33, 139, 255)          # helleres Blau #218bff
SOFT = (196, 214, 236)
GREEN = (96, 208, 150)
RED = (240, 100, 110)
NAVYD = (8, 14, 28)

# ---- Schriften: Instrument Sans (Überschriften), DM Sans (Fließtext) ----
_FW = {'Regular': 400, 'Medium': 500, 'SemiBold': 600, 'Bold': 700, 'ExtraBold': 700}
_fc = {}
def F(size, w='Regular'):
    k = (size, w)
    if k not in _fc:
        if size >= 40 or w == 'ExtraBold':
            f = ImageFont.truetype(str(ASSETS / 'fonts' / 'InstrumentSans.ttf'), size); f.set_variation_by_axes([100, _FW[w]])
        else:
            f = ImageFont.truetype(str(ASSETS / 'fonts' / 'DMSans.ttf'), size); f.set_variation_by_axes([14, _FW[w]])
        _fc[k] = f
    return _fc[k]

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def sstep(p): p = clamp(p); return p * p * p * (p * (p * 6 - 15) + 10)
def eo(p): p = clamp(p); return 1 - (1 - p) ** 3
def lerp(a, b, t): return a + (b - a) * t
def lerp2(a, b, t): return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)

# ---- Koordinaten-Hilfen: Rechtecke der Aufnahme (x0, y0, x1, y1) ----
def R(x0, y0, x1, y1): return (x0, y0 - 14, x1, y1 - 14)   # Pixel des Original-Frames (1080p) -> zugeschnittenes Bild
def ctr(r): return ((r[0] + r[2]) / 2, (r[1] + r[3]) / 2)
def union(rs): return (min(r[0] for r in rs), min(r[1] for r in rs), max(r[2] for r in rs), max(r[3] for r in rs))

# ---- Hintergrund ----
def _make_bg():
    top = np.array([20, 50, 104], dtype=np.float32); bot = np.array([8, 16, 34], dtype=np.float32)
    col = np.linspace(top, bot, H)[:, None, :]
    arr = np.broadcast_to(col, (H, W, 3)).copy()
    yy, xx = np.mgrid[0:H:48, 0:W:48]
    for y, x in zip(yy.ravel() + 24, xx.ravel() + 24):
        if y < H and x < W: arr[y - 1:y + 1, x - 1:x + 1] += 9
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
BG = _make_bg()

def blob(size, col, amax):
    yy, xx = np.mgrid[0:size, 0:size]; r = np.sqrt((xx - size / 2) ** 2 + (yy - size / 2) ** 2) / (size / 2)
    a = np.clip(1 - r, 0, 1) ** 1.6 * amax
    return Image.new('RGB', (size, size), col), Image.fromarray((a * 255).astype(np.uint8))
B1 = blob(1400, (33, 139, 255), 0.20); B2 = blob(1200, (0, 160, 192), 0.13)

def bg(tg):
    im = BG.copy()
    x1 = 700 + 260 * math.sin(tg * 0.17); y1 = 360 + 120 * math.cos(tg * 0.12)
    im.paste(B1[0], (int(x1 - 700), int(y1 - 700)), B1[1])
    x2 = 1450 + 220 * math.cos(tg * 0.13); y2 = 820 + 100 * math.sin(tg * 0.16)
    im.paste(B2[0], (int(x2 - 600), int(y2 - 600)), B2[1])
    return im

# ---- Zeichnen ----
def text(img, x, y, s, size, w='Regular', fill=WHITE, a=1.0, anchor='la', spacing=0):
    if a <= 0.01 or not s: return
    f = F(size, w)
    if spacing:
        tot = sum(f.getlength(ch) for ch in s) + spacing * (len(s) - 1)
        x0 = x - tot / 2 if anchor[0] == 'm' else x
        for ch in s:
            text(img, x0, y, ch, size, w, fill, a, 'l' + anchor[1]); x0 += f.getlength(ch) + spacing
        return
    bb = f.getbbox(s, anchor=anchor); pad = 3
    m = Image.new('L', (bb[2] - bb[0] + 2 * pad, bb[3] - bb[1] + 2 * pad), 0)
    ImageDraw.Draw(m).text((-bb[0] + pad, -bb[1] + pad), s, font=f, fill=int(255 * clamp(a)), anchor=anchor)
    img.paste(Image.new('RGB', m.size, fill), (int(x + bb[0] - pad), int(y + bb[1] - pad)), m)

def tlen(s, size, w='Regular'): return F(size, w).getlength(s)

def shape(img, box, r, fill=None, outline=None, width=0, a=1.0, ss=3):
    if a <= 0.01: return
    x0, y0, x1, y1 = [int(round(v)) for v in box]
    pad = width + 6; lw, lh = x1 - x0 + 2 * pad, y1 - y0 + 2 * pad
    base = fill if fill else outline
    lay = Image.new('RGBA', (lw * ss, lh * ss), base + (0,))
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle([pad * ss, pad * ss, (pad + x1 - x0) * ss, (pad + y1 - y0) * ss], r * ss,
                        fill=(fill + (255,)) if fill else None, outline=(outline + (255,)) if outline else None, width=int(width * ss))
    lay = lay.resize((lw, lh), Image.LANCZOS)
    al = lay.getchannel('A')
    if a < 1: al = al.point(lambda v: int(v * a))
    img.paste(lay.convert('RGB'), (x0 - pad, y0 - pad), al)

def pill(img, cx, cy, s, size, fill, tcol, a=1.0, outline=None, padx=40, h=None, w='Bold'):
    tw = tlen(s, size, w); h = h or size + 36; wd = tw + 2 * padx
    shape(img, (cx - wd / 2, cy - h / 2, cx + wd / 2, cy + h / 2), h / 2, fill=fill, outline=outline, width=3 if outline else 0, a=a)
    text(img, cx, cy + 1, s, size, w, tcol, a, 'mm')

# ---- Kurven im Einstiegsbild ----
random.seed(5)
def _curve(base, slope, noise, n=49):
    pts = []; y = base
    for i in range(n):
        y = base - slope * i + random.uniform(-noise, noise) * (1 if i else 0)
        pts.append((i * 40, y))
    return pts
LINES = [_curve(900, 7, 28), _curve(980, 9, 34), _curve(820, 5, 22)]
