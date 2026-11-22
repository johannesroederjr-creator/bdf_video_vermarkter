"""Rendert das Video "Sales Intelligence Rundgang" aus der Aufnahme.
Aufrufe (im Projektordner):
  python build.py vorschau 1:6.5 3:20.0     Standbilder (Abschnitt:Sekunde) nach temp/ schreiben
  python build.py render                    alle Abschnitte rendern (ca. 4-8 Minuten)
  python build.py render 3                  nur Abschnitt 3 neu rendern
  python build.py zusammenfuegen             ausgabe/Sales_Intelligence_Rundgang_komplett.mp4 (mit Abfrage + Abspann)
  python build.py web                       ausgabe/sales-intelligence_web.mp4 + poster.jpg (ohne Abfrage/Abspann, für die Website)
Abschnitte: 0 Einstieg, 1 Cockpit, 2 Kundenbewegungen, 3 Verkaufschancen, 4 Abfrage, 5 Abspann.
"""
import sys, math, os, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from engine import *
from inhalt import *

SRC = str(ASSETS / 'aufnahme.mp4')
BASE = 1500 / SW             # Darstellungsgröße der Aufnahme in der Grundansicht
HOME = ((SW / 2, SH / 2), (W / 2, 625.0), 1.0)

# ------------------------------------------------------------ source reader
def clip_frames(c):
    n = int(round(c['out'] * FPS))
    if c.get('freeze'):
        r = subprocess.run(['ffmpeg', '-loglevel', 'error', '-ss', str(c['src'][0]), '-i', SRC, '-frames:v', '1', '-vf', f'crop={SW}:{SH}:0:14',
                            '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True)
        im = Image.frombuffer('RGB', (SW, SH), r.stdout, 'raw', 'RGB', 0, 1)
        for _ in range(n): yield im
        return
    s, e = c['src']; sp = (e - s) / c['out']
    p = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-ss', str(s), '-t', str(e - s), '-i', SRC, '-vf',
                          f'crop={SW}:{SH}:0:14,setpts=PTS/{sp},fps={FPS}', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    last = None; sz = SW * SH * 3
    for _ in range(n):
        buf = p.stdout.read(sz)
        if len(buf) == sz: last = Image.frombuffer('RGB', (SW, SH), buf, 'raw', 'RGB', 0, 1)
        yield last
    p.stdout.close(); p.kill(); p.wait()


# ------------------------------------------------------------ card drawing
_sh = None
def shadow_sprite():
    global _sh
    if _sh is None:
        Pd = 90; w0, h0 = int(SW * BASE), int(SH * BASE)
        m = Image.new('L', (w0 + 2 * Pd, h0 + 2 * Pd), 0)
        ImageDraw.Draw(m).rounded_rectangle([Pd, Pd + 26, Pd + w0, Pd + h0 + 26], 24, fill=150)
        _sh = (m.filter(ImageFilter.GaussianBlur(34)), Pd)
    return _sh

def draw_card(img, frame, cam, a=1.0):
    (Hs, T, z) = cam; z = z * (0.955 + 0.045 * a); sc = BASE * z
    x0 = T[0] - Hs[0] * sc; y0 = T[1] - Hs[1] * sc; x1 = x0 + SW * sc; y1 = y0 + SH * sc
    vx0, vy0 = max(0, math.floor(x0)), max(0, math.floor(y0)); vx1, vy1 = min(W, math.ceil(x1)), min(H, math.ceil(y1))
    if vx1 <= vx0 or vy1 <= vy0: return
    edge = x0 > -2 or y0 > -2 or x1 < W + 2 or y1 < H + 2
    base = img.copy() if a < 0.999 else None
    if edge and z < 1.7:
        sm, Pd = shadow_sprite(); cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        k = sc / BASE; sw_, sh_ = round(sm.width * k), round(sm.height * k)
        s2 = sm.resize((sw_, sh_), Image.BILINEAR)
        img.paste(Image.new('RGB', s2.size, (0, 8, 20)), (round(cx - sw_ / 2), round(cy - sh_ / 2)), s2)
    box = (max(0, (vx0 - x0) / sc), max(0, (vy0 - y0) / sc), min(SW, (vx1 - x0) / sc), min(SH, (vy1 - y0) / sc))
    part = frame.resize((vx1 - vx0, vy1 - vy0), Image.LANCZOS if sc < 1 else Image.BICUBIC, box=box)
    if edge:
        ss = 2; m = Image.new('L', ((vx1 - vx0) * ss, (vy1 - vy0) * ss), 0)
        ImageDraw.Draw(m).rounded_rectangle([(x0 - vx0) * ss, (y0 - vy0) * ss, (x1 - vx0) * ss - 1, (y1 - vy0) * ss - 1], 24 * ss * min(1, z), fill=255)
        m = m.resize(part.size, Image.LANCZOS)
        img.paste(part, (vx0, vy0), m)
    else:
        img.paste(part, (vx0, vy0))
    if base is not None: img.paste(Image.blend(base, img, a))

def to_screen(r, cam):
    (Hs, T, z) = cam; sc = BASE * z
    return (T[0] + (r[0] - Hs[0]) * sc, T[1] + (r[1] - Hs[1]) * sc, T[0] + (r[2] - Hs[0]) * sc, T[1] + (r[3] - Hs[1]) * sc)

def cam_for(rect):
    rw, rh = rect[2] - rect[0], rect[3] - rect[1]
    z = min(1560 / (rw * BASE), 600 / (rh * BASE), 2.3); z = max(z, 1.12); sc = BASE * z
    Hs = ctr(rect); Tx, Ty = 960.0, 575.0
    Tx = clamp(Tx, W - 60 - (SW - Hs[0]) * sc, 60 + Hs[0] * sc) if W - 60 - (SW - Hs[0]) * sc <= 60 + Hs[0] * sc else Tx
    Ty = clamp(Ty, 940 - (SH - Hs[1]) * sc, 250 + Hs[1] * sc)
    return (Hs, (Tx, Ty), z)

def cam_state(keys, t):
    if t <= keys[0][0]: return keys[0][1]
    for (ta, sa), (tb, sb) in zip(keys, keys[1:]):
        if ta <= t <= tb:
            p = sstep((t - ta) / (tb - ta)) if tb > ta else 1
            return (lerp2(sa[0], sb[0], p), lerp2(sa[1], sb[1], p), lerp(sa[2], sb[2], p))
    return keys[-1][1]



_logo = {}
def logo(img, cx, cy, h, a=1.0):
    p = str(ASSETS / 'logo.png')
    if a <= 0.01 or not os.path.exists(p): return
    if 'im' not in _logo:
        im = Image.open(p).convert('RGBA'); _logo['im'] = im.crop(im.getchannel('A').point(lambda v: 255 if v > 20 else 0).getbbox())
    im = _logo['im']; k = h / im.height; lg = im.resize((max(1, round(im.width * k)), h), Image.LANCZOS)
    pw, ph = lg.width + int(h * 0.5), int(h * 1.5)
    shape(img, (cx - pw / 2, cy - ph / 2, cx + pw / 2, cy + ph / 2), int(h * 0.3), fill=(255, 255, 255), a=a)
    al = lg.getchannel('A')
    if a < 1: al = al.point(lambda v: int(v * a))
    img.paste(lg.convert('RGB'), (int(cx - lg.width / 2), int(cy - lg.height / 2)), al)

def badge(img, t):
    a = eo((t - 0.9) / 0.6)
    if a <= 0.01: return
    s = T['siegel']; wd = tlen(s, 24, 'Bold') + 4 * 11 + 84; cx, cy = W - 70 - wd / 2, 80
    shape(img, (cx - wd / 2, cy - 27, cx + wd / 2, cy + 27), 27, fill=(8, 26, 42), outline=ACC, width=2, a=a * 0.9)
    pul = 0.55 + 0.45 * math.sin(t * 3.2)
    shape(img, (cx - wd / 2 + 22, cy - 7, cx - wd / 2 + 36, cy + 7), 7, fill=GREEN, a=a * (0.5 + 0.5 * pul))
    text(img, cx - wd / 2 + 52, cy + 1, s, 24, 'Bold', WHITE, a, 'lm', spacing=4)


TR = 1.4   # camera transition (s)

def bubble(img, lines, rs, side, a, t):
    """accent-coloured hint bubble placed next to screen-rect rs with a pointer."""
    if a <= 0.01: return
    f = 'Bold'; size = 54; padx, pady, lh = 46, 28, 66
    bw = max(tlen(l, size, f) for l in lines) + 2 * padx; bh = len(lines) * lh + 2 * pady - 6
    if rs is None or side == 'bottom':
        x = W / 2 - bw / 2; y = H - 70 - bh; ptr = None
    else:
        cx, cy = (rs[0] + rs[2]) / 2, (rs[1] + rs[3]) / 2; gap = 34
        if side == 'below' and rs[3] + gap + bh > 1030: side = 'above'
        if side == 'above' and rs[1] - gap - bh < 20: side = 'below'
        if side == 'right' and rs[2] + gap + bw > W - 30: side = 'left'
        if side == 'left' and rs[0] - gap - bw < 30: side = 'right'
        if side == 'below': x, y = cx - bw / 2, rs[3] + gap
        elif side == 'above': x, y = cx - bw / 2, rs[1] - gap - bh
        elif side == 'right': x, y = rs[2] + gap, cy - bh / 2
        else: x, y = rs[0] - gap - bw, cy - bh / 2
        x = clamp(x, 30, W - 30 - bw); y = clamp(y, 125, H - 30 - bh); ptr = (side, cx, cy)
    pul = 1 + 0.012 * math.sin(t * 5); y += 16 * (1 - a)
    shape(img, (x - 4, y + 10, x + bw + 4, y + bh + 14), 36, fill=(0, 6, 16), a=0.45 * a)
    shape(img, (x - 3, y - 3, x + bw + 3, y + bh + 3), 39, outline=(255, 255, 255), width=3, a=0.9 * a)
    shape(img, (x, y, x + bw, y + bh), 36, fill=BRAND, a=a)
    if ptr:
        sd, cx, cy = ptr; ps = 3; L = Image.new('RGBA', (90 * ps, 90 * ps), BRAND + (0,)); d = ImageDraw.Draw(L)
        if sd in ('below', 'above'):
            px = clamp(cx, x + 50, x + bw - 50); ty = y if sd == 'below' else y + bh
            pts = [(px - 22, ty), (px + 22, ty), (px, ty + (-26 if sd == 'below' else 26))]
        else:
            py = clamp(cy, y + 40, y + bh - 40); tx = x if sd == 'right' else x + bw
            pts = [(tx, py - 22), (tx, py + 22), (tx + (-26 if sd == 'right' else 26), py)]
        mnx = min(p[0] for p in pts) - 4; mny = min(p[1] for p in pts) - 4
        d.polygon([((p[0] - mnx) * ps, (p[1] - mny) * ps) for p in pts], fill=BRAND + (255,))
        L = L.resize((90, 90), Image.LANCZOS); al = L.getchannel('A')
        if a < 1: al = al.point(lambda v: int(v * a))
        img.paste(L.convert('RGB'), (int(mnx), int(mny)), al)
    for i, l in enumerate(lines):
        text(img, x + bw / 2, y + pady + lh * i + lh / 2 - 4, l, size, f, WHITE, a, 'mm')


def data_scene(spec, t, tg, frame):
    dur = spec['dur']; img = bg(tg); beats = spec['beats']
    keys = [(0.0, HOME)]
    for b in beats:
        st = cam_for(b['zoom']) if b.get('zoom') else HOME
        b['state'] = st
        keys.append((b['t0'], keys[-1][1])); keys.append((b['t0'] + TR, st)); keys.append((b['t1'], st))
    keys.append((beats[-1]['t1'] + TR, HOME))
    cam = cam_state(keys, t)
    draw_card(img, frame, cam, eo(t / 0.8))
    ha_home = clamp(1 - (cam[2] - 1.0) / 0.03) * eo((t - 0.2) / 0.5)
    for b in beats:
        ha = eo((t - (b['t0'] + TR - 0.1)) / 0.4) * (1 - eo((t - (b['t1'] - 0.3)) / 0.3))
        if ha <= 0.01 or not b.get('rects'): continue
        col = b.get('col', ACC)
        if b.get('dim', True):
            ov = Image.new('L', (W, H), int(95 * ha)); d = ImageDraw.Draw(ov)
            for r in b['rects']:
                s_ = to_screen(r, cam); d.rounded_rectangle([s_[0] - 6, s_[1] - 6, s_[2] + 6, s_[3] + 6], 14, fill=0)
            img.paste(Image.new('RGB', (W, H), NAVYD), (0, 0), ov)
        pu = 0.75 + 0.25 * math.sin(t * 5)
        for r in b['rects']:
            s_ = to_screen(r, cam); g = 10 * (1 - 0.4 * ha) + 4 * pu
            shape(img, (s_[0] - 6 - g, s_[1] - 6 - g, s_[2] + 6 + g, s_[3] + 6 + g), 18, outline=col, width=10, a=0.25 * ha)
            shape(img, (s_[0] - 6, s_[1] - 6, s_[2] + 6, s_[3] + 6), 14, outline=col, width=5, a=ha)
    a = eo((t - 0.1) / 0.5) * ha_home
    text(img, 110, 50 + 12 * (1 - a), spec['label'], 24, 'SemiBold', ACC, a, 'la', spacing=5)
    a = eo((t - 0.2) / 0.6) * ha_home
    text(img, 110, 88 + 16 * (1 - a), spec['title'], 58, 'ExtraBold', WHITE, a)
    for b in beats:
        if b.get('callout'):
            ba = eo((t - (b['t0'] + 0.3)) / 0.35) * (1 - eo((t - (b['t1'] - 0.3)) / 0.3))
            if ba > 0.01: pill(img, 960, lerp(165, 190, ha_home) + 12 * (1 - ba), b['callout'], 40, (8, 26, 42), WHITE, ba, outline=b.get('col', ACC))
    for b in beats:
        if b.get('say'):
            ba = eo((t - (b['t0'] + b.get('say_d', TR - 0.4))) / 0.4) * (1 - eo((t - (b['t1'] - 0.3)) / 0.3))
            if ba > 0.01:
                rs = to_screen(union(b.get('anchor') or b['rects']), cam) if b.get('rects') else None
                if rs and b.get('dy'): rs = (rs[0], rs[1] + b['dy'], rs[2], rs[3] + b['dy'])
                bubble(img, b['say'], rs, b.get('side', 'below'), ba, t)
    badge(img, t)
    logo(img, 1435, 80, 56, eo((t - 0.6) / 0.6))
    text(img, W - 70, 1056, T['hinweis'], 20, 'Medium', (150, 180, 200), 0.8 * ha_home, 'ra')
    ex = clamp((t - (dur - 0.35)) / 0.35)
    return Image.blend(img, bg(tg), ex) if ex > 0 else img



def clips_dur(clips): return sum(c['out'] for c in clips)


# ------------------------------------------------------------ Einstieg, Abfrage, Abspann
def hook(spec, t, tg, frame=None):
    dur = spec['dur']; img = bg(tg)
    lay = Image.new('RGBA', (W * 2, H * 2), (72, 214, 196, 0)); d = ImageDraw.Draw(lay)
    p = eo((t - 0.2) / 3.6)
    for k, pts in enumerate(LINES):
        n = int(p * (len(pts) - 1)); sel = pts[:n + 1]
        if len(sel) > 1: d.line([(x * 2, y * 2) for x, y in sel], fill=(72, 214, 196, 90 - k * 20), width=5, joint='curve')
        if sel: x, y = sel[-1]; d.ellipse([x * 2 - 9, y * 2 - 9, x * 2 + 9, y * 2 + 9], fill=(72, 214, 196, 150))
    lay = lay.resize((W, H), Image.LANCZOS); img.paste(lay.convert('RGB'), (0, 0), lay.getchannel('A'))
    a = eo((t - 0.3) / 0.5); text(img, W / 2, 330 + 12 * (1 - a), T['eyebrow'], 28, 'SemiBold', ACC, a, 'mm', spacing=8)
    a = eo((t - 0.6) / 0.7); text(img, W / 2, 450 + 40 * (1 - a), T['titel'], 140, 'ExtraBold', WHITE, a, 'mm')
    a = eo((t - 1.8) / 0.7); text(img, W / 2, 585 + 24 * (1 - a), T['claim'], 58, 'Medium', SOFT, a, 'mm')
    a = eo((t - 3.8) / 0.7)
    if a > 0:
        shape(img, (330, 735 + 20 * (1 - a), 1590, 895 + 20 * (1 - a)), 80, fill=(52, 96, 122), a=0.75 * a)
        text(img, W / 2, 790 + 20 * (1 - a), T['frage1'], 42, 'Medium', WHITE, a, 'mm')
        text(img, W / 2, 846 + 20 * (1 - a), T['frage2'], 42, 'Medium', WHITE, a, 'mm')
    logo(img, W / 2, 160, 92, eo((t - 0.3) / 0.6))
    ex = clamp((t - (dur - 0.35)) / 0.35)
    return Image.blend(img, bg(tg), ex) if ex > 0 else img

def ask(spec, t, tg, frame=None):
    return ASK(spec, t, tg)

def cta(spec, t, tg, frame=None):
    dur = spec['dur']; img = bg(tg)
    logo(img, W / 2, 160, 104, eo((t - 0.1) / 0.6))
    a = eo((t - 0.2) / 0.5); text(img, W / 2, 290 + 12 * (1 - a), T['eyebrow'], 28, 'SemiBold', ACC, a, 'mm', spacing=8)
    a = eo((t - 0.5) / 0.7); text(img, W / 2, 395 + 30 * (1 - a), T['cta1'], 92, 'ExtraBold', WHITE, a, 'mm')
    a = eo((t - 0.9) / 0.7); text(img, W / 2, 505 + 30 * (1 - a), T['cta2'], 92, 'ExtraBold', ACC, a, 'mm')
    a = eo((t - 1.8) / 0.6); text(img, W / 2, 610 + 12 * (1 - a), T['cta3'], 46, 'Medium', SOFT, a, 'mm')
    a = eo((t - 2.8) / 0.6)
    if a > 0:
        pul = 1 + 0.012 * math.sin((t - 2.8) * 4)
        s = T['button']; tw = tlen(s, 44, 'Bold'); wd = (tw + 120) * pul; h = 112 * pul; cy = 770 + 20 * (1 - a)
        shape(img, (W / 2 - wd / 2, cy - h / 2, W / 2 + wd / 2, cy + h / 2), h / 2, fill=BRAND, a=a)
        text(img, W / 2, cy + 1, s, 44, 'Bold', WHITE, a, 'mm')
    a = eo((t - 3.6) / 0.6); text(img, W / 2, 900, T['domain'], 34, 'Medium', SOFT, a, 'mm')
    text(img, W - 70, 1048, T['hinweis'], 22, 'Medium', (150, 180, 200), 0.8 * eo((t - 0.6) / 0.5), 'ra')
    ex = clamp((t - (dur - 0.5)) / 0.5)
    return Image.blend(img, bg(tg), ex) if ex > 0 else img




def ASK(spec, t, tg):
    dur = spec['dur']; img = bg(tg)
    logo(img, 1700, 80, 58, eo((t - 0.4) / 0.6))
    a = eo((t - 0.2) / 0.5); text(img, W / 2, 130 + 12 * (1 - a), T['ask_kicker'], 26, 'SemiBold', ACC, a, 'mm', spacing=8)
    a = eo((t - 0.6) / 0.7)
    text(img, W / 2, 235 + 18 * (1 - a), T['ask_q1'], 66, 'ExtraBold', WHITE, a, 'mm')
    text(img, W / 2, 315 + 18 * (1 - a), T['ask_q2'], 66, 'ExtraBold', WHITE, a, 'mm')
    for i, o in enumerate(OPTS):
        t0 = 2.4 + i * 1.1; a = eo((t - t0) / 0.5); y = 430 + i * 118 + 18 * (1 - a)
        shape(img, (330, y - 48, 1590, y + 48), 48, fill=(255, 255, 255), a=0.96 * a)
        shape(img, (344, y - 38, 424, y + 38), 38, fill=BRAND, a=a)
        text(img, 384, y + 1, str(i + 1), 44, 'Bold', WHITE, a, 'mm')
        text(img, 462, y + 1, o, 42, 'SemiBold', (13, 17, 23), a, 'lm')
    # reflection bar: 10 s to think
    a = eo((t - 7.2) / 0.5) * (1 - eo((t - 17.9) / 0.4))
    if a > 0:
        text(img, W / 2, 938, T['ask_warte'], 36, 'Medium', SOFT, a, 'mm')
        p = clamp((t - 7.8) / 10.0)
        shape(img, (560, 978, 1360, 994), 8, fill=(40, 62, 100), a=a)
        if p > 0.005: shape(img, (560, 978, 560 + 800 * p, 994), 8, fill=ACC, a=a)
    # call to answer
    a = eo((t - 18.5) / 0.6)
    if a > 0:
        text(img, W / 2, 928 + 10 * (1 - a), T['ask_antwort'], 34, 'Medium', SOFT, a, 'mm')
        text(img, W / 2, 986 + 10 * (1 - a), T['ask_mail'], 52, 'Bold', WHITE, a, 'mm')
    a = eo((t - 21.0) / 0.6)
    if a > 0:
        text(img, W / 2, 1044 + 8 * (1 - a), T['ask_dank'], 30, 'Medium', ACC, a, 'mm')
    ex = clamp((t - (dur - 0.4)) / 0.4)
    return Image.blend(img, bg(tg), ex) if ex > 0 else img


SCENES = [(dict(dur=DAUER['einstieg']), hook, None), (SPEC_B, data_scene, CL_B), (SPEC_C, data_scene, CL_C), (SPEC_D, data_scene, CL_D), (dict(dur=DAUER['abfrage']), ask, None), (dict(dur=DAUER['abspann']), cta, None)]
for sp, fn, cl in SCENES:
    if cl: sp['dur'] = round(clips_dur(cl), 3)
OFFS = [sum(round(s[0]['dur'] * FPS) for s in SCENES[:i]) / FPS for i in range(len(SCENES))]


def scene_frames(si, only=None):
    spec, fn, cl = SCENES[si]; n = int(round(spec['dur'] * FPS))
    if cl is None:
        for f in range(n):
            if only is None or f / FPS in only: yield f, None
        return
    f = 0; prev = None
    for ci, c in enumerate(cl):
        for k, fr in enumerate(clip_frames(c)):
            if ci > 0 and k < 9 and prev is not None: fr = Image.blend(prev, fr, (k + 1) / 10)
            yield f, fr; f += 1
        prev = fr


def render_scene(si):
    spec, fn, cl = SCENES[si]
    tmp = str(TEMP / f'sz{si}.tmp.mp4'); fin = str(TEMP / f'sz{si}.mp4')
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-crf', '17', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', '-r', str(FPS), tmp], stdin=subprocess.PIPE)
    for f, fr in scene_frames(si):
        p.stdin.write(fn(spec, f / FPS, OFFS[si] + f / FPS, fr).tobytes())
    p.stdin.close()
    if p.wait() == 0: os.rename(tmp, fin)
    else: raise SystemExit(f'scene {si} failed')
    return si


def preview(picks):
    for si, tt in picks:
        spec, fn, cl = SCENES[si]
        fr = None
        if cl:
            # find source frame at scene time tt
            acc = 0
            for c in cl:
                if tt < acc + c['out'] or c is cl[-1]:
                    k = tt - acc; s, e = c['src']; ts = s + k * (e - s) / c['out'] if not c.get('freeze') else s
                    r = subprocess.run(['ffmpeg', '-loglevel', 'error', '-ss', str(ts), '-i', SRC, '-frames:v', '1', '-vf', f'crop={SW}:{SH}:0:14',
                                        '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True)
                    fr = Image.frombuffer('RGB', (SW, SH), r.stdout, 'raw', 'RGB', 0, 1); break
                acc += c['out']
        fn(spec, tt, OFFS[si] + tt, fr).save(str(TEMP / f'vorschau_{si}_{tt}.png'))




def _run(cmd): 
    r = subprocess.run(cmd)
    if r.returncode != 0: raise SystemExit('ffmpeg-Fehler: ' + ' '.join(map(str, cmd)))

def _liste(ids, name):
    p = TEMP / name
    p.write_text(''.join(f"file 'sz{i}.mp4'\n" for i in ids), encoding='utf-8'); return p

def zusammenfuegen():
    l = _liste(range(len(SCENES)), 'liste_komplett.txt')
    _run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', str(l), '-c', 'copy', str(OUT / 'Sales_Intelligence_Rundgang_komplett.mp4')])

def web():
    l = _liste(range(4), 'liste_web.txt'); mp4 = OUT / 'sales-intelligence_web.mp4'
    _run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', str(l), '-c:v', 'libx264', '-crf', '24', '-preset', 'slow',
          '-pix_fmt', 'yuv420p', '-movflags', '+faststart', '-an', str(mp4)])
    _run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', '6.9', '-i', str(mp4), '-frames:v', '1', '-q:v', '3', str(OUT / 'poster.jpg')])


if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else ''
    if mode == 'vorschau':
        preview([(int(a.split(':')[0]), float(a.split(':')[1])) for a in sys.argv[2:]])
    elif mode == 'render':
        from multiprocessing import Pool
        ids = [int(x) for x in sys.argv[2:]] or list(range(len(SCENES)))
        with Pool(max(1, min(2, os.cpu_count() or 1))) as pool:
            for r in pool.imap_unordered(render_scene, ids): print('fertig: Abschnitt', r, flush=True)
    elif mode == 'zusammenfuegen': zusammenfuegen()
    elif mode == 'web': web()
    else: print(__doc__)
