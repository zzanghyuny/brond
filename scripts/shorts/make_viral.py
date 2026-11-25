#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""브동산 '조회수형' 쇼츠 렌더러 — 장면 목록(JSON)으로 5가지 기획(가격 대결·이번 주 로또·당첨 현금·옆 단지 격차·공고문 탐정)을 만든다.

  python3 make_viral.py viral/<키>.json tts            # 장면별 나레이션 → $VIRAL_TTS/<out>/<장면id>.wav
  python3 make_viral.py viral/<키>.json stills [초…]    # 시간표 출력 / 정지 화면
  python3 make_viral.py viral/<키>.json render         # $VIRAL_OUT/<out>.mp4 + -thumbnail.png

장면 type: hook · cards · bars · pay · rank · floors · table · close (설정 예: viral/duel-yeonsan-wangsuk.json)
장면 길이 = lead + 나레이션 + tail. 첫 장면(hook)이 첫 화면·썸네일이고, close 장면 끝에서 첫 화면으로 루프한다.
"""
import os, sys, json, math, wave, subprocess, asyncio, ssl
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
import audio_orig, sfx

C = json.load(open(sys.argv[1], encoding='utf8'))
KEY = os.path.basename(sys.argv[1])[:-5]
TTS = os.path.join(os.environ.get('VIRAL_TTS', '/tmp/viral-tts/'), C['out']) + '/'
OUT = os.environ.get('VIRAL_OUT', '/tmp/viral-out/')
MAPS = os.environ.get('WALK_MAPS', '/tmp/walk-maps/')
FONTS = os.environ.get('QUIZ_FONTS', '/tmp/nanum/')
VOICE = C.get('voice', ['ko-KR-InJoonNeural', '+16%', '-3Hz'])
SC_CFG = C['scenes']

def wav_len(p):
    with wave.open(p) as w: return w.getnframes() / w.getframerate()

if sys.argv[2] == 'tts':
    import edge_tts, edge_tts.communicate as EC
    ca = '/root/.ccr/ca-bundle.crt'
    if os.path.exists(ca): EC._SSL_CTX = ssl.create_default_context(cafile=ca)
    os.makedirs(TTS, exist_ok=True)
    for S in SC_CFG:
        mp3 = TTS + S['id'] + '.mp3'
        asyncio.run(edge_tts.Communicate(S['narr'], VOICE[0], rate=VOICE[1], pitch=VOICE[2], proxy=os.environ.get('HTTPS_PROXY') or None).save(mp3))
        subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', mp3, '-af',
                        'silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse',
                        '-ar', '44100', '-ac', '1', TTS + S['id'] + '.wav'], check=True)
        print(S['id'], round(wav_len(TTS + S['id'] + '.wav'), 2), S['narr'])
    sys.exit(0)

W, H, FPS = 1080, 1920, 30
SAFE_L, SAFE_R = 54, 885; CX = (SAFE_L + SAFE_R) // 2
BG = (8, 8, 9); INK = (244, 241, 234); SOFT = (185, 181, 172); FAINT = (150, 148, 142)
HAIR = (42, 42, 45); CARD = (16, 16, 18); BRASS = (200, 164, 92); PLUS = (95, 184, 156); MINUS = (240, 138, 102)
COL = {'ink': INK, 'soft': SOFT, 'faint': FAINT, 'brass': BRASS, 'plus': PLUS, 'minus': MINUS}
def col(c): return COL[c] if isinstance(c, str) else tuple(c)

_f = {}
def F(px, w='B'):
    if (px, w) not in _f:
        _f[(px, w)] = ImageFont.truetype(FONTS + 'NanumGothic-%s.ttf' % {'R': 'Regular', 'B': 'Bold', 'X': 'ExtraBold'}[w], px)
    return _f[(px, w)]
def ease(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def eo(x): x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3
def tw(s, px, w='B'): return F(px, w).getlength(s)
def fit(s, px, w, maxw):
    while px > 20 and tw(s, px, w) > maxw: px -= 2
    return px
def text(img, xy, s, px, color=INK, w='B', anchor='c', alpha=1.0, stroke=0, maxw=None):
    if alpha <= 0.01 or not s: return
    if maxw: px = fit(s, px, w, maxw)
    lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    x = xy[0] - tw(s, px, w) / 2 if anchor == 'c' else (xy[0] - tw(s, px, w) if anchor == 'r' else xy[0])
    a = int(255 * min(1, alpha))
    d.text((x, xy[1]), s, font=F(px, w), fill=col(color) + (a,), stroke_width=stroke, stroke_fill=BG + (a,))
    img.alpha_composite(lay)
def rect(img, box, fill=None, outline=None, width=2, alpha=1.0, radius=0):
    if alpha <= 0.01: return
    lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay); a = int(255 * min(1, alpha))
    d.rounded_rectangle(box, radius=radius, fill=(col(fill) + (a,)) if fill else None, outline=(col(outline) + (a,)) if outline else None, width=width)
    img.alpha_composite(lay)

_img = {}
def load(path):
    if path not in _img:
        p = path if path.startswith('/') else (MAPS + path[5:] if path.startswith('maps/') else os.path.join(REPO, 'posts', 'images', path))
        _img[path] = Image.open(p).convert('RGB')
    return _img[path]
def kb(src, bw, bh, t, z0, z1, cx0, cy0, cx1, cy1):
    k = ease(t); z = z0 + (z1 - z0) * k
    cx = (cx0 + (cx1 - cx0) * k) * src.width; cy = (cy0 + (cy1 - cy0) * k) * src.height
    base = max(bw / src.width, bh / src.height); sw, sh = bw / (base * z), bh / (base * z)
    l = min(max(cx - sw / 2, 0), src.width - sw); tp = min(max(cy - sh / 2, 0), src.height - sh)
    return src.crop((l, tp, l + sw, tp + sh)).resize((bw, bh), Image.BICUBIC)
def paste_band(img, spec, box, t, dim=0.0):
    x0, y0, x1, y1 = box
    band = kb(load(spec['img']), x1 - x0, y1 - y0, t, *spec.get('kb', [1.0, 1.12, 0.5, 0.5, 0.5, 0.5])).convert('RGBA')
    if dim: band.alpha_composite(Image.new('RGBA', band.size, BG + (int(255 * dim),)))
    img.alpha_composite(band, (x0, y0))

def new(): return Image.new('RGBA', (W, H), BG + (255,))
def chrome(img):
    x = CX - (tw('브', 40, 'X') + tw('동산', 40, 'R')) / 2
    text(img, (x, 210), '브', 40, INK, 'X', anchor='l'); text(img, (x + tw('브', 40, 'X'), 210), '동산', 40, SOFT, 'R', anchor='l')
    for i, s in enumerate(C['src']): text(img, (CX, 1395 + 35 * i), s, 26, FAINT, 'R', maxw=830)
def badge(img, s, kind, y, alpha=1.0, px=58):
    c = {'plus': PLUS, 'minus': MINUS}.get(kind, BRASS); p = fit(s, px, 'X', 780); w = tw(s, p, 'X')
    rect(img, (CX - w / 2 - 34, y - 16, CX + w / 2 + 34, y + p + 22), fill=BG, outline=c, width=4, alpha=alpha, radius=10)
    text(img, (CX, y), s, p, c, 'X', alpha=alpha)
def num(v, unit='억'):
    return f'{v:.2f}{unit}'

# ---------------- 장면
def at(S, t, i, n):  # i번째(0..n-1) 요소가 나레이션 길이에 맞춰 나타나는 투명도
    d0 = S['_lead'] + S['_nar'] * 0.85 * i / max(1, n)
    return ease((t - d0) / 0.35)

def sc_hook(img, S, t, d, still=False):
    L = S.get('layout', 'single'); k = 0 if still else t / max(d, 1e-3)
    if L == 'single':
        paste_band(img, S['imgs'][0], (0, 300, W, 940), k)
    elif L == 'split':
        for j, (sp, box) in enumerate(zip(S['imgs'], [(0, 300, W, 612), (0, 628, W, 940)])):
            paste_band(img, sp, box, k)
            lab = sp['label']; p = 40; w = tw(lab, p, 'X')
            rect(img, (SAFE_L, box[1] + 22, SAFE_L + w + 44, box[1] + 22 + p + 26), fill=BG, alpha=0.86, radius=8)
            text(img, (SAFE_L + 22, box[1] + 34), lab, p, BRASS if j == 0 else INK, 'X', anchor='l')
    elif L == 'grid':
        tiles = S['imgs']; cw, ch = W // 4, 320
        for j in range(8):
            x0, y0 = (j % 4) * cw, 300 + (j // 4) * ch
            if j < len(tiles):
                paste_band(img, tiles[j], (x0 + 3, y0 + 3, x0 + cw - 3, y0 + ch - 3), k * 0.5, dim=0.55)
                text(img, (x0 + cw / 2, y0 + ch / 2 - 60), '?', 110, INK, 'X')
                text(img, (x0 + cw / 2, y0 + ch - 58), tiles[j]['label'], 30, SOFT, 'B', maxw=cw - 20)
            else:
                rect(img, (x0 + 3, y0 + 3, x0 + cw - 3, y0 + ch - 3), fill=CARD, outline=BRASS, width=4)
                text(img, (x0 + cw / 2, y0 + ch / 2 - 70), '1억+', 64, BRASS, 'X')
                text(img, (x0 + cw / 2, y0 + ch / 2 + 10), '단 1곳', 44, BRASS, 'X')
    elif L == 'map':
        m = load(S['map']).resize((W, W), Image.LANCZOS); top = S.get('map_top', 220)
        img.paste(m.crop((0, top, W, top + 640)), (0, 300))
        for j, p in enumerate(S['pins']):
            x, y = p['xy'][0] * W / 1280, p['xy'][1] * W / 1280 - top + 300
            a = ease((t - 0.3 - 0.5 * j) / 0.4) if not still else 1
            lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); dd = ImageDraw.Draw(lay)
            c = col(p.get('color', 'ink'))
            dd.rectangle((x - 15, y - 15, x + 15, y + 15), fill=c + (int(255 * a),), outline=BG + (int(255 * a),), width=3)
            img.alpha_composite(lay)
            anc = p.get('side', 'r'); ox = 30 if anc == 'r' else -30
            text(img, (x + ox, y - 50), p['label'], 40, c, 'X', anchor='l' if anc == 'r' else 'r', alpha=a, stroke=5)
            text(img, (x + ox, y + 2), p['sub'], 34, INK, 'X', anchor='l' if anc == 'r' else 'r', alpha=a, stroke=5)
        if S.get('dist'):
            (x1, y1), (x2, y2) = [(p['xy'][0] * W / 1280, p['xy'][1] * W / 1280 - top + 300) for p in S['pins'][:2]]
            a = ease((t - 1.3) / 0.4) if not still else 1
            lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); dd = ImageDraw.Draw(lay)
            n_ = 14
            for q in range(n_):
                if q % 2 == 0:
                    f0, f1 = q / n_, (q + 1) / n_
                    dd.line((x1 + (x2 - x1) * f0, y1 + (y2 - y1) * f0, x1 + (x2 - x1) * f1, y1 + (y2 - y1) * f1), fill=SOFT + (int(255 * a),), width=4)
            img.alpha_composite(lay)
            text(img, ((x1 + x2) / 2 - 40, (y1 + y2) / 2 - 20), S['dist'], 36, SOFT, 'X', anchor='r', alpha=a, stroke=5)
        text(img, (W - 16, 300 + 600), '지도 © Mapbox © OpenStreetMap', 22, FAINT, 'R', anchor='r', stroke=3)
    elif L == 'doc':
        rect(img, (90, 330, 990, 910), fill=(226, 222, 212))
        rng = np.random.default_rng(7)
        lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); dd = ImageDraw.Draw(lay)
        for r in range(15):
            y = 380 + r * 34; xw = 140 + rng.integers(0, 120)
            for q in range(int(rng.integers(4, 8))):
                ww = int(rng.integers(50, 150))
                if xw + ww > 940: break
                dd.rectangle((xw, y, xw + ww, y + 12), fill=(150, 146, 138, 255)); xw += ww + 14
        img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(1.2)))
        hy = S.get('hl_y', 668); f = eo((t - 0.5) / 0.9) if not still else 1
        rect(img, (130, hy - 8, 130 + 820 * f, hy + 40), fill=(232, 196, 92), alpha=0.85)
        if f > 0.6: text(img, (150, hy - 4), S['hl'], 34, (20, 20, 20), 'X', anchor='l', alpha=ease((f - 0.6) / 0.4) if not still else 1, maxw=780)
        text(img, (CX, 920), S.get('doc_cap', ''), 24, FAINT, 'R')
    a = (lambda d0: 1.0) if still else (lambda d0: ease((t - d0) / 0.4))
    y = 975
    for j, ln in enumerate(S['lines']):
        px = ln.get('px', 76 if j == 0 else 100)
        text(img, (CX, y), ln['t'], px, ln.get('c', 'ink' if j == 0 else 'brass'), 'X', alpha=a(0.15 + 0.45 * j), maxw=860)
        y += px + 22
    if S.get('name'):
        rect(img, (CX - 60, 1212, CX + 60, 1214), fill=HAIR, alpha=a(1.0))
        text(img, (CX, 1228), S['name'], 44, INK, 'B', alpha=a(1.0), maxw=820)
        text(img, (CX, 1288), S.get('region', ''), 30, SOFT, 'R', alpha=a(1.2), maxw=820)

def sc_cards(img, S, t, d):
    if S.get('band'): paste_band(img, S['band'], (0, 300, W, 620), t / d, dim=0.15)
    y = 660 if S.get('band') else 360
    if S.get('title'): text(img, (CX, y - 10), S['title'], 54, INK, 'X', alpha=ease(t / 0.3), maxw=840); y += 90
    n = len(S['items'])
    for i, it in enumerate(S['items']):
        a = at(S, t, i, n); h = it.get('h', 132)
        rect(img, (SAFE_L, y, SAFE_R, y + h), fill=CARD, outline=col(it.get('oc', 'hair')) if it.get('oc') else HAIR, width=3 if it.get('oc') else 2, alpha=a, radius=10)
        if it.get('k'): text(img, (SAFE_L + 30, y + 24), it['k'], 32, it.get('kc', 'faint'), 'B', anchor='l', alpha=a, maxw=780)
        text(img, (SAFE_L + 30, y + (66 if it.get('k') else 40)), it['v'], it.get('px', 48), it.get('c', 'ink'), 'X', anchor='l', alpha=a, maxw=780)
        y += h + 22
    if S.get('note'): text(img, (CX, y + 10), S['note'], 32, SOFT, 'B', alpha=at(S, t, n, n), maxw=820)
    cd = S.get('countdown')
    if cd:
        t0 = S['_lead'] + S['_nar']; k = (t - t0) / cd
        if 0 <= k <= 1.05:
            r = 90; cxx, cyy = CX, 1180
            lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); dd = ImageDraw.Draw(lay)
            dd.ellipse((cxx - r, cyy - r, cxx + r, cyy + r), outline=HAIR + (255,), width=10)
            dd.arc((cxx - r, cyy - r, cxx + r, cyy + r), -90, -90 + 360 * (1 - min(1, k)), fill=BRASS + (255,), width=10)
            img.alpha_composite(lay)
            text(img, (cxx, cyy - 52), str(max(1, int(math.ceil(cd * (1 - k))))), 96, BRASS, 'X')

def sc_bars(img, S, t, d):
    if S.get('title'): text(img, (CX, 360), S['title'], 54, INK, 'X', alpha=ease(t / 0.3), maxw=840)
    if S.get('subtitle'): text(img, (CX, 430), S['subtitle'], 32, SOFT, 'B', alpha=ease(t / 0.3), maxw=840)
    y = 520; n = len(S['bars']); vmax = S['vmax']; x0, x1 = SAFE_L + 10, SAFE_R - 10
    for i, b in enumerate(S['bars']):
        if b.get('gap'): y += 30
        a = at(S, t, i, n); g = eo((t - (S['_lead'] + S['_nar'] * 0.85 * i / n)) / 0.8)
        text(img, (x0, y), b['label'], 34, b.get('lc', 'soft'), 'B', anchor='l', alpha=a, maxw=600)
        rect(img, (x0, y + 50, x1, y + 104), fill=CARD, alpha=a)
        wv = (x1 - x0) * b['v'] / vmax * g
        if wv > 2: rect(img, (x0, y + 50, x0 + wv, y + 104), fill=b.get('c', 'ink'), alpha=a)
        vt = b.get('txt', num(b['v'] * g if g < 1 else b['v']))
        text(img, (x1, y), vt, 44, b.get('c', 'ink'), 'X', anchor='r', alpha=a)
        y += 150
    if S.get('badge'):
        tb = S['_lead'] + S['_nar'] * S.get('badge_at', 0.75); badge(img, S['badge'], S.get('kind', 'brass'), y + 20, ease((t - tb) / 0.3))
        y += 130
    for j, ln in enumerate(S.get('lines', [])):
        text(img, (CX, y + 20 + j * 48), ln, 32 if j == 0 else 28, SOFT if j == 0 else FAINT, 'B' if j == 0 else 'R', alpha=at(S, t, n + 1, n + 1), maxw=840)

def sc_pay(img, S, t, d):
    text(img, (CX, 350), S['title'], 44, SOFT, 'B', alpha=ease(t / 0.3), maxw=840)
    g = eo((t - S['_lead']) / 1.2); v = S['big'] * g
    text(img, (CX, 430), S.get('fmt', '{:.2f}억').format(v), 150, BRASS, 'X', maxw=840)
    text(img, (CX, 610), S.get('sub', ''), 36, INK, 'B', alpha=ease((t - 0.6) / 0.3), maxw=840)
    x0, x1, y0 = SAFE_L, SAFE_R, 720; tot = sum(s['p'] for s in S['segs']); x = x0
    for i, s in enumerate(S['segs']):
        w = (x1 - x0) * s['p'] / tot; on = i in S.get('on', [])
        rect(img, (x + 2, y0, x + w - 2, y0 + 90), fill=s.get('c', 'brass') if on else CARD, outline=HAIR, width=2)
        text(img, (x + w / 2, y0 + 24), f"{s['p']}%", 36, BG if on else FAINT, 'X')
        text(img, (x + w / 2, y0 + 110), s['k'], 28, INK if on else FAINT, 'B', maxw=w - 6)
        x += w
    for j, ln in enumerate(S.get('lines', [])):
        text(img, (CX, 900 + j * 56), ln, 36 if j == 0 else 30, INK if j == 0 else SOFT, 'B', alpha=ease((t - S['_lead'] - S['_nar'] * (0.3 + 0.25 * j)) / 0.35), maxw=840)

def sc_rank(img, S, t, d):
    a = ease(t / 0.25)
    text(img, (SAFE_L, 300), S['rank'], 120, BRASS if S.get('top') else INK, 'X', anchor='l', alpha=a)
    text(img, (SAFE_L + tw(S['rank'], 120, 'X') + 24, 360), S.get('of', ''), 36, FAINT, 'B', anchor='l', alpha=a)
    paste_band(img, S['img'], (0, 470, W, 900), t / d, dim=0.05)
    text(img, (CX, 930), S['name'], 54, INK, 'X', alpha=ease((t - 0.15) / 0.3), maxw=840)
    text(img, (CX, 1005), S['region'], 32, SOFT, 'B', alpha=ease((t - 0.2) / 0.3), maxw=840)
    kc = {'plus': PLUS, 'minus': MINUS}.get(S['kind'], BRASS)
    ap = ease((t - S['_lead'] - S['_nar'] * 0.45) / 0.3)
    text(img, (CX, 1070), '예상 프리미엄', 30, FAINT, 'B', alpha=ap)
    text(img, (CX, 1110), S['prem'], 96 if S.get('top') else 84, kc, 'X', alpha=ap, maxw=840)
    text(img, (CX, 1230), S['judge'], 32, kc, 'B', alpha=ap)
    if S.get('note'): text(img, (CX, 1290), S['note'], 28, FAINT, 'R', alpha=ap, maxw=840)

def sc_floors(img, S, t, d):
    text(img, (CX, 340), S['title'], 50, INK, 'X', alpha=ease(t / 0.3), maxw=840)
    nf = S.get('nf', 20); fx0, fx1 = 330, 610; fy1 = 1260; fh = (fy1 - 420) / nf
    lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); dd = ImageDraw.Draw(lay)
    for f in range(nf):
        y = fy1 - (f + 1) * fh
        dd.rectangle((fx0, y + 2, fx1, y + fh - 2), fill=CARD + (255,), outline=HAIR + (255,), width=1)
    img.alpha_composite(lay)
    a1 = ease((t - S['_lead'] - S['_nar'] * 0.35) / 0.5)
    for grp in S['groups']:
        lo, hi = grp['floors']; y_top = fy1 - hi * fh; y_bot = fy1 - (lo - 1) * fh
        ag = a1 if grp.get('main') else ease((t - S['_lead'] - S['_nar'] * 0.6) / 0.4)
        if grp.get('main'): rect(img, (fx0, y_top + 2, fx1, y_bot - 2), fill=grp.get('c', 'brass'), alpha=ag * 0.9)
        else:
            rect(img, (fx0, y_top + 2, fx1, y_bot - 2), outline=grp.get('c', 'soft'), width=3, alpha=ag)
            cy = (y_top + y_bot) / 2; rect(img, (fx0 + 40, cy - 14, fx0 + 68, cy + 14), fill=grp.get('c', 'soft'), alpha=ag)
        text(img, (fx1 + 30, (y_top + y_bot) / 2 - 50), grp['big'], grp.get('px', 76), grp.get('c', 'brass'), 'X', anchor='l', alpha=ag)
        text(img, (fx1 + 30, (y_top + y_bot) / 2 + 36), grp['k'], 32, SOFT, 'B', anchor='l', alpha=ag)
    text(img, (fx0 - 20, fy1 - fh * 0.8), '1층', 26, FAINT, 'B', anchor='r'); text(img, (fx0 - 20, fy1 - nf * fh), f'{nf}층', 26, FAINT, 'B', anchor='r')
    text(img, (CX, 1300), S.get('cap', ''), 26, FAINT, 'R', maxw=840)

def sc_table(img, S, t, d):
    text(img, (CX, 340), S['title'], 50, INK, 'X', alpha=ease(t / 0.3), maxw=840)
    cols = S['cols']; x_k, xs = SAFE_L + 10, [560, 800]
    y = 450
    for j, c in enumerate(cols): text(img, (xs[j], y), c, 32, BRASS if j == 0 else INK, 'X', maxw=220)
    y += 70; n = len(S['rows'])
    for i, r in enumerate(S['rows']):
        a = at(S, t, i, n)
        rect(img, (SAFE_L, y - 12, SAFE_R + 60, y + 70), fill=CARD, alpha=a, radius=8)
        text(img, (x_k + 14, y + 10), r[0], 32, FAINT, 'B', anchor='l', alpha=a, maxw=300)
        for j in range(2): text(img, (xs[j], y + 4), r[j + 1], 42, (BRASS if j == 0 else INK) if not (len(r) > 3 and r[3] == j) else PLUS, 'X', alpha=a, maxw=230)
        y += 100
    for j, ln in enumerate(S.get('lines', [])):
        text(img, (CX, y + 20 + j * 50), ln, 34 if j == 0 else 28, INK if j == 0 else FAINT, 'B' if j == 0 else 'R', alpha=at(S, t, n, n), maxw=860)

def sc_close(img, S, t, d):
    loop = ease((t - (d - 1.2)) / 0.9); ai = 1 - loop
    a = lambda d0: ease((t - d0) / 0.35) * ai
    y = 360
    for j, ln in enumerate(S.get('lines', [])):
        px = ln.get('px', 44); text(img, (CX, y), ln['t'], px, ln.get('c', 'ink'), ln.get('w', 'X'), alpha=a(0.1 + 0.35 * j), maxw=860); y += px + 26
    if S.get('sched'):
        rect(img, (CX - 340, 1150, CX + 340, 1236), fill=CARD, outline=BRASS, width=2, alpha=a(1.0), radius=8)
        text(img, (CX, 1172), S['sched'], 36, BRASS, 'B', alpha=a(1.0), maxw=640)
    tq = S['_lead'] + S['_nar'] - 1.7
    text(img, (CX, 1030), S['q'], 84, BRASS, 'X', alpha=ease((t - tq) / 0.3) * ai, maxw=860)
    if loop > 0:
        lo = new(); sc_hook(lo, SC_CFG[0], 0, 1, still=True); chrome(lo)
        lo.alpha_composite(Image.new('RGBA', (W, H), BG + (int(255 * (1 - loop)),)))
        img.alpha_composite(Image.blend(img, lo, loop))

DRAW = {'hook': sc_hook, 'cards': sc_cards, 'bars': sc_bars, 'pay': sc_pay, 'rank': sc_rank, 'floors': sc_floors, 'table': sc_table, 'close': sc_close}

# ---------------- 타임라인
T0 = 0
for i, S in enumerate(SC_CFG):
    S['_nar'] = wav_len(TTS + S['id'] + '.wav'); S['_lead'] = 0.25 if i == 0 else 0.18
    S['_dur'] = S['_lead'] + S['_nar'] + S.get('tail', 0.35) + (S.get('countdown') or 0) + (1.4 if S['type'] == 'close' else 0)
    S['_t0'] = T0; T0 += S['_dur']
DUR = T0

yy, xx = np.mgrid[0:H, 0:W]
_r = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2)
VIGN = np.clip(1.0 - 0.45 * np.clip(_r - 0.5, 0, 1) ** 1.4, 0.45, 1.0).astype(np.float32)[..., None]
def frame(T):
    for i, S in enumerate(SC_CFG):
        if T < S['_t0'] + S['_dur'] or i == len(SC_CFG) - 1:
            t = T - S['_t0']; img = new(); DRAW[S['type']](img, S, t, S['_dur']); chrome(img)
            if i > 0 and t < 0.2: img.alpha_composite(Image.new('RGBA', (W, H), BG + (int(255 * (1 - t / 0.2)),)))
            return np.clip(np.asarray(img.convert('RGB')).astype(np.float32) * VIGN, 0, 255).astype(np.uint8)

SR = 44100
def build_audio(path):
    n = int(DUR * SR) + SR; starts = [S['_t0'] for S in SC_CFG]
    hits = [S['_t0'] + S['_lead'] + S['_nar'] * S.get('hit_at', 0.5) for S in SC_CFG if S.get('hit')]
    tmp = OUT + '_viral_music.wav'
    audio_orig.make_audio(tmp, DUR + 1, RISE=tuple(starts[1:]), BOOM=tuple((x, 0.6) for x in hits))
    with wave.open(tmp) as w: m = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32).reshape(-1, 2) / 32768
    mus = np.zeros((n, 2)); L = min(n, len(m)); mus[:L] = m[:L]
    nar = np.zeros(n)
    for S in SC_CFG:
        with wave.open(TTS + S['id'] + '.wav') as w: x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
        i = int((S['_t0'] + S['_lead']) * SR); nar[i:i + len(x)] += x[:max(0, n - i)]
    nar /= max(1e-6, np.abs(nar).max()); nar *= 0.85
    env = np.convolve(np.abs(nar), np.ones(int(0.25 * SR)) / int(0.25 * SR), 'same')
    out = mus * 0.16 * (1 - 0.55 * np.clip(env / 0.08, 0, 1))[:, None] + nar[:, None]
    lib = {'whoosh': sfx.whoosh(), 'ping': sfx.ping(), 'tick': sfx.tick(), 'shimmer': sfx.shimmer(), 'lowhit': sfx.lowhit()}
    ev = [(s - 0.3, 'whoosh', 0.16) for s in starts[1:]] + [(DUR - 1.7, 'shimmer', 0.22)]
    for S in SC_CFG:
        if S.get('hit'): ev.append((S['_t0'] + S['_lead'] + S['_nar'] * S.get('hit_at', 0.5), S['hit'], 0.3))
        if S.get('countdown'):
            c0 = S['_t0'] + S['_lead'] + S['_nar']
            ev += [(c0 + j * 0.5, 'tick', 0.16) for j in range(int(S['countdown'] / 0.5))]
    for t0, nm, g in ev:
        i = int(max(0, t0) * SR); x = lib[nm] * g; Lx = min(len(x), n - i)
        if Lx > 0: out[i:i + Lx] += x[:Lx, None]
    out = out[:int(DUR * SR)]; fd = int(0.4 * SR); out[-fd:] *= np.linspace(1, 0, fd)[:, None]
    out = np.tanh(out * 1.05); out /= max(1e-6, np.abs(out).max()) / 0.89
    with wave.open(path, 'wb') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out * 32767).astype(np.int16).tobytes())

def render():
    name = C['out']; os.makedirs(OUT, exist_ok=True); v = OUT + f'_{name}_v.tmp.mp4'
    p = subprocess.Popen(['ffmpeg', '-nostdin', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '23', '-pix_fmt', 'yuv420p', v], stdin=subprocess.PIPE)
    for fi in range(int(round(DUR * FPS))): p.stdin.write(frame(fi / FPS).tobytes())
    p.stdin.close(); assert p.wait() == 0
    build_audio(OUT + f'_{name}.wav'); tmp = OUT + f'_{name}.tmp.mp4'
    subprocess.run(['ffmpeg', '-nostdin', '-y', '-loglevel', 'error', '-i', v, '-i', OUT + f'_{name}.wav', '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
                    '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', tmp], check=True)
    os.replace(tmp, OUT + f'{name}.mp4'); os.remove(v); os.remove(OUT + f'_{name}.wav')
    th = new(); sc_hook(th, SC_CFG[0], 0, 1, still=True); chrome(th)
    th.convert('RGB').save(OUT + f'{name}-thumbnail.png')
    print('done', OUT + f'{name}.mp4', round(DUR, 2))

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    if sys.argv[2] == 'stills':
        print([(S['id'], round(S['_t0'], 2), round(S['_dur'], 2)) for S in SC_CFG], round(DUR, 2))
        for s in sys.argv[3:]: Image.fromarray(frame(float(s))).save(OUT + f'still_{KEY}_{float(s):05.2f}.png')
    elif sys.argv[2] == 'render': render()
