# -*- coding: utf-8 -*-
"""도시이야기 쇼츠 렌더러 — B안 '리얼 생생' (1080×1920).
사용: python3 render_shorts.py <에피소드 폴더> S1|S2
진한 색보정, 왼쪽 위 위치 칩(미끄러져 들어옴), 오른쪽 위 미니맵(장소가 확인된 장면만 빨간 점),
숫자 말풍선·스티커 팝 + ping, 굵은 자막(핵심어 황동색, 6% 커졌다 제자리), 옆으로 미는 전환.
안전영역: 자막 중심 x=500, 아래끝 y=1500(아래 20%·오른쪽 버튼 줄 비움).
"""
import os, sys, json, subprocess, wave, math, importlib.util
import numpy as np, cairo
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
LIB = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, LIB)
import dosi_gfx as gfx, sfx
from shapely.geometry import shape

EPD, WHICH = sys.argv[1], sys.argv[2]
spec = importlib.util.spec_from_file_location('script', os.path.join(EPD, 'script.py')); S = importlib.util.module_from_spec(spec); spec.loader.exec_module(S)
EP = S.EP; SC = getattr(S, WHICH); GEO = json.load(open(EP['geo'])); P = GEO['places']
W, H, FPS = 1080, 1920, 30; XF = 0.3; SUB_CX, SUB_B = 500, 1500
OUT = EP['work'] + f'out_{WHICH}/'; os.makedirs(OUT, exist_ok=True)
FP = '/tmp/fonts/'; PXB, PB, PM, PR = FP + 'Pretendard-ExtraBold.otf', FP + 'Pretendard-Bold.otf', FP + 'Pretendard-Medium.otf', FP + 'Pretendard-Regular.otf'
NX, NR = '/tmp/nanum/NanumGothic-ExtraBold.ttf', '/tmp/nanum/NanumGothic-Regular.ttf'
BRASS = (200, 164, 92); INK = (17, 17, 17); CREAM = (244, 241, 234)
_f = {}
def F(p, s):
    if (p, s) not in _f: _f[(p, s)] = ImageFont.truetype(p, s)
    return _f[(p, s)]
def ease_back(x, s=1.7): x = max(0.0, min(1.0, x)); x -= 1; return x * x * ((s + 1) * x + s) + 1
def eout(x): x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3
def probe(p): return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p]))

meta = json.load(open(EP['work'] + f'tts_{WHICH}.json'))
LEAD0, LEAD, GAP, TAIL, HOLD, ENDCARD, HOOK = 0.4, 0.3, 0.28, 0.45, 0.3, 2.2, 0.0
timeline = []; t = 0.0
for i, s in enumerate(SC):
    st = t; c = st + (LEAD0 if i == 0 else LEAD); subs = []
    for m in [m for m in meta if m['scene'] == i]:
        ln = s['lines'][m['line']]; subs.append(dict(text=ln[0], hl=ln[2] if len(ln) > 2 else '', t0=c - st, t1=c - st + m['dur'] + 0.1, wav=m['wav'], abs=c)); c += m['dur'] + GAP
    anim = all(sh[0] == 'anim' for sh in s['shots'])
    Dur = (c - GAP) - st + (HOLD if anim else TAIL) + (ENDCARD if s.get('end') else 0)
    timeline.append(dict(i=i, start=st, dur=Dur, subs=subs, anim=anim)); t = st + Dur
TOTAL = t

# ---------- 고정 그림
def chip_img(text):
    f = F(PB, 34); w = ImageDraw.Draw(Image.new('L', (1, 1))).textlength(text, font=f); h = 62
    im = Image.new('RGBA', (int(w) + 70, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, im.width - 1, h - 1), 31, fill=(255, 255, 255, 245)); d.ellipse((20, h / 2 - 8, 36, h / 2 + 8), fill=BRASS)
    d.text((48, h / 2), text, font=f, fill=INK, anchor='lm'); return im
_mm = {}
def minimap(loc):
    w, h = 300, 220; b = EP['minimap_bounds']
    if 'base' not in _mm:
        surf = cairo.ImageSurface(cairo.FORMAT_RGB24, w, h); cr = cairo.Context(surf); cr.set_source_rgb(20 / 255, 22 / 255, 26 / 255); cr.paint()
        pj = gfx.Proj.fit(b, (0, 0, w, h), pad=0.04)
        cr.set_source_rgb(44 / 255, 46 / 255, 50 / 255); gfx.path_geom(cr, gfx.land_frame(pj, w, h), pj); cr.fill()
        for k in EP.get('minimap_layers', []):
            g = shape(GEO[k]); cr.set_source_rgba(200 / 255, 164 / 255, 92 / 255, 0.3); gfx.path_geom(cr, g, pj); cr.fill()
            cr.set_source_rgb(200 / 255, 164 / 255, 92 / 255); cr.set_line_width(1.6); gfx.path_geom(cr, g, pj); cr.stroke()
        cr.set_source_rgb(90 / 255, 115 / 255, 140 / 255); cr.set_line_width(3)
        for k in EP.get('minimap_rivers', []): gfx.path_geom(cr, shape(GEO[k]), pj); cr.stroke()
        a = np.ndarray((h, w, 4), np.uint8, surf.get_data()); im = Image.fromarray(np.ascontiguousarray(a[..., [2, 1, 0]]))
        _mm['base'] = ImageOps.expand(im, border=5, fill='white').convert('RGBA'); _mm['pj'] = pj
    if not loc: return _mm['base'], None
    lon, lat = (P[loc]['lon'], P[loc]['lat']) if isinstance(loc, str) else loc
    x, y = _mm['pj'](lon, lat); return _mm['base'], (x + 5, y + 5)
def bubble_img(t1, t2):
    f1, f2 = F(PXB, 50), F(PB, 32); d0 = ImageDraw.Draw(Image.new('L', (1, 1))); w = max(d0.textlength(t1, font=f1), d0.textlength(t2, font=f2)) + 70
    im = Image.new('RGBA', (int(w), 200), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, 136), 26, fill=(255, 255, 255, 250)); d.polygon([(50, 134), (96, 134), (42, 196)], fill=(255, 255, 255, 250))
    d.text((34, 44), t1, font=f1, fill=BRASS, anchor='lm'); d.text((34, 100), t2, font=f2, fill=INK, anchor='lm'); return im
def sticker_img(t1, t2):
    im = Image.new('RGBA', (860, 300), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((20, 20, 840, 280), 40, fill=(255, 255, 255, 245))
    d.text((430, 115), t1, font=F(PXB, 86), fill=INK, anchor='mm'); d.text((430, 212), t2, font=F(PB, 44), fill=BRASS, anchor='mm')
    return im.rotate(-3, resample=Image.BICUBIC, expand=True)
def wrap2(text, f, maxw, d):
    if d.textlength(text, font=f) <= maxw: return [text]
    words = text.split(' '); best = None
    for k in range(1, len(words)):
        a, b = ' '.join(words[:k]), ' '.join(words[k:]); wa, wb = d.textlength(a, font=f), d.textlength(b, font=f)
        if max(wa, wb) > maxw: continue
        sc = max(wa, wb) - (200 if a[-1] in '.,?!' else 0)
        if best is None or sc < best[0]: best = (sc, [a, b])
    return best[1] if best else [text]
def sub_img(text, hl, size=66):
    im = Image.new('RGBA', (W, 300), (0, 0, 0, 0)); d = ImageDraw.Draw(im); f = F(PXB, size); lh = int(size * 1.32)
    lines = wrap2(text, f, 880, d)
    for k, ln in enumerate(lines):
        y = 300 - 30 - lh * (len(lines) - k - 0.5)
        parts = [(ln, (255, 255, 255))]
        if hl and hl in ln: a, b = ln.split(hl, 1); parts = [(a, (255, 255, 255)), (hl, BRASS), (b, (255, 255, 255))]
        tw = sum(d.textlength(p, font=f) for p, _ in parts); x = SUB_CX - tw / 2
        for p, c in parts: d.text((x, y), p, font=f, fill=c, anchor='lm', stroke_width=7, stroke_fill=(0, 0, 0)); x += d.textlength(p, font=f)
    return im   # 아래끝 = SUB_B
def hook_img():
    t1, t2 = EP['shorts'][WHICH]; im = Image.new('RGBA', (W, 420), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle((0, 40, W, 400), fill=(8, 8, 9, 190))
    d.text((W / 2, 120), f"도시이야기 · {EP['city']} 편", font=F(PM, 34), fill=(200, 196, 186), anchor='mm')
    d.text((W / 2, 215), t1, font=F(PXB, 80), fill=CREAM, anchor='mm'); d.text((W / 2, 320), t2, font=F(PXB, 80), fill=BRASS, anchor='mm')
    return im
def wordmark(d, x, y, size):
    fb, fr = F(NX, size), F(NR, size); wb = d.textlength('브', font=fb); wr = d.textlength('동산', font=fr); x0 = x - (wb + wr) / 2
    d.text((x0, y), '브', font=fb, fill=CREAM, anchor='lm'); d.text((x0 + wb + 1, y), '동산', font=fr, fill=(185, 181, 172), anchor='lm')
def end_img():
    im = Image.new('RGBA', (W, H), (8, 8, 9, 228)); d = ImageDraw.Draw(im); wordmark(d, W / 2, 700, 96)
    d.text((W / 2, 820), f"도시이야기 · {EP['city']} 편", font=F(PB, 44), fill=CREAM, anchor='mm')
    d.text((W / 2, 890), '본편은 브동산 채널에서 이어져요', font=F(PM, 36), fill=(185, 181, 172), anchor='mm')
    d.text((W / 2, 960), 'brandongsan.com', font=F(PB, 36), fill=BRASS, anchor='mm')
    d.text((W / 2, 1060), '영상 Pexels · 지도 © OpenStreetMap contributors · Natural Earth', font=F(PR, 24), fill=(150, 148, 142), anchor='mm')
    return im
def attrib_img(text):
    f = F(PR, 22); w = ImageDraw.Draw(Image.new('L', (1, 1))).textlength(text, font=f)
    im = Image.new('RGBA', (int(w) + 24, 36), (0, 0, 0, 150)); ImageDraw.Draw(im).text((12, 18), text, font=f, fill=(220, 216, 206), anchor='lm'); return im
def paste_scaled(base, im, cx, cy, sc, alpha=1.0, anchor=(0.5, 0.5)):
    if sc <= 0.01 or alpha <= 0.01: return
    w, h = max(1, int(im.width * sc)), max(1, int(im.height * sc)); s = im.resize((w, h), Image.BICUBIC) if sc != 1 else im
    if alpha < 1: s = s.copy(); s.putalpha(s.getchannel('A').point(lambda v: int(v * alpha)))
    base.alpha_composite(s, (int(cx - w * anchor[0]), int(cy - h * anchor[1])))

def bg_stream(k, s, L):
    shots = s['shots']; n = len(shots); seg = L / n; procs = []
    for sh in shots:
        if sh[0] == 'clip':
            src = EP['px'] + f'px_{sh[1]}.mp4'; avail = probe(src) - sh[2] - 0.1; f = max(1.0, seg / max(0.5, avail))
            p = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', str(sh[2]), '-i', src, '-t', f'{seg / f + 0.3:.3f}', '-vf',
                                  f'setpts=(PTS-STARTPTS)*{f:.4f},fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},eq=saturation=1.35:contrast=1.08:brightness=0.02',
                                  '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
            procs.append(('p', p, int(round(seg * FPS))))
        else:
            cues = [sb['t0'] for sb in timeline[k]['subs']]
            procs.append(('g', gfx.frames(sh[1], W, H, seg, cues, sh[2], GEO, short=True), int(round(seg * FPS))))
    last = None
    for kind, src, N in procs:
        for _ in range(N):
            if kind == 'p':
                raw = src.stdout.read(W * H * 3)
                if len(raw) < W * H * 3: raw = last
            else:
                raw = next(src, None) or last
            last = raw; yield raw
        if kind == 'p': src.kill()
    while True: yield last

def render_scene(k):
    s = SC[k]; tl = timeline[k]; last = k == len(SC) - 1
    out = f'{OUT}scene_{k:02d}.mp4'
    if os.environ.get('SKIP_EXISTING') and os.path.exists(out): return out
    L = tl['dur'] + (0 if last else XF); N = int(round(L * FPS))
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p', out + '.tmp.mp4'], stdin=subprocess.PIPE)
    clip = s['shots'][0][0] == 'clip'
    chip = chip_img(s['tag']) if s.get('tag') else None
    mm, mdot = minimap(s.get('loc')) if clip else (None, None)
    subs = [sub_img(sb['text'], sb['hl']) for sb in tl['subs']]
    bub = bubble_img(s['bubble']['t1'], s['bubble']['t2']) if 'bubble' in s else None
    stk = sticker_img(s['sticker']['t1'], s['sticker']['t2']) if 'sticker' in s else None
    hook = hook_img() if k == 0 else None; endc = end_img() if s.get('end') else None
    att = attrib_img(s['attrib']) if s.get('attrib') else None
    top = Image.new('RGBA', (W, 150), (0, 0, 0, 0)); wordmark(ImageDraw.Draw(top), W / 2, 92, 40)
    bg = bg_stream(k, s, L)
    for fi in range(N):
        t = fi / FPS; fr = Image.frombytes('RGB', (W, H), next(bg)).convert('RGBA')
        fr.alpha_composite(top)
        if chip is not None:
            kk = eout((t - 0.12) / 0.45)
            if kk > 0: fr.alpha_composite(chip, (int(-chip.width + (40 + chip.width) * kk), 170))
        if mm is not None:
            k2 = eout((t - 0.3) / 0.5)
            if k2 > 0:
                m = mm.copy()
                if mdot:
                    md = ImageDraw.Draw(m); x, y = mdot; r = 9 + 5 * (0.5 + 0.5 * math.sin(t * 6))
                    md.ellipse((x - r - 6, y - r - 6, x + r + 6, y + r + 6), outline=(255, 80, 60, 140), width=3); md.ellipse((x - 9, y - 9, x + 9, y + 9), fill=(255, 80, 60), outline='white', width=3)
                paste_scaled(fr, m, W - 40 - m.width / 2, 250 + m.height / 2 - (1 - k2) * 20, 1.0, k2)
        if att is not None: fr.alpha_composite(att, (20, 1560))
        if hook is not None:
            a = min(1.0, t / 0.25) * (1 - eout((t - 2.6) / 0.4)); paste_scaled(fr, hook, W / 2, 560, 1.0, a)
        if bub is not None:
            t0 = tl['subs'][s['bubble']['line']]['t0'] + 0.4; sc = ease_back((t - t0) / 0.45)
            paste_scaled(fr, bub, 120, 1150, sc, min(1, (t - t0) / 0.15) if t > t0 else 0, anchor=(0.05, 1.0))
        if stk is not None:
            t0 = tl['subs'][s['sticker']['line']]['t0'] + s['sticker']['delay']; sc = ease_back((t - t0) / 0.5)
            paste_scaled(fr, stk, W / 2 - 40, 820, sc, min(1, (t - t0) / 0.15) if t > t0 else 0)
        for sb, im in zip(tl['subs'], subs):
            if sb['t0'] <= t <= sb['t1']:
                sc = 1.0 + 0.06 * (1 - eout((t - sb['t0']) / 0.18)); paste_scaled(fr, im, SUB_CX, SUB_B, sc, 1.0, anchor=(SUB_CX / W, 1.0))
        if endc is not None:
            a = eout((t - (tl['dur'] - ENDCARD + 0.1)) / 0.5)
            if a > 0: paste_scaled(fr, endc, W / 2, H / 2, 1.0, a)
        enc.stdin.write(fr.convert('RGB').tobytes())
    enc.stdin.close(); assert enc.wait() == 0; os.replace(out + '.tmp.mp4', out); return out

SR = 44100
def build_audio(path):
    n = int(SR * (TOTAL + 0.5)); voice = np.zeros(n); fx = np.zeros(n); tt = np.arange(n) / SR
    def add(buf, x, at, g=1.0):
        i = int(at * SR); L = min(len(x), n - i)
        if L > 0: buf[i:i + L] += x[:L] * g
    for tl, s in zip(timeline, SC):
        for sb in tl['subs']:
            with wave.open(sb['wav']) as w: x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
            add(voice, x, sb['abs'])
        if 'bubble' in s: add(fx, sfx.ping(), tl['start'] + tl['subs'][s['bubble']['line']]['t0'] + 0.4, 0.18)
        if 'sticker' in s: add(fx, sfx.ping(), tl['start'] + tl['subs'][s['sticker']['line']]['t0'] + s['sticker']['delay'], 0.18)
    wh = sfx.whoosh()
    for tl in timeline[1:]: add(fx, wh, tl['start'] - 0.3, 0.10)
    music = sum(np.sin(2 * np.pi * f * tt) * a for f, a in [(110, .3), (164.81, .2), (220, .18), (329.63, .1), (55, .25)])
    music *= (0.75 + 0.25 * np.sin(2 * np.pi * tt / 4.0)) * np.clip(tt / 1.2, 0, 1) * np.clip((TOTAL + 0.5 - tt) / 1.8, 0, 1)
    env = np.convolve((np.abs(voice) > 0.02).astype(float), np.ones(int(SR * 0.3)) / int(SR * 0.3), 'same')
    mix = voice / max(1e-6, np.abs(voice).max()) * 0.9 + music / max(1e-6, np.abs(music).max()) * (0.12 - 0.06 * np.clip(env * 3, 0, 1)) + fx
    mix = np.tanh(mix); mix /= max(1e-6, np.abs(mix).max()) / 0.9
    st = np.stack([mix, mix], 1)[:int(SR * TOTAL)]
    with wave.open(path, 'wb') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype(np.int16).tobytes())

if __name__ == '__main__':
    NAME = EP['names'][WHICH]
    if len(sys.argv) > 3 and sys.argv[3] == 'timeline':
        for tl in timeline: print(tl['i'], round(tl['start'], 1), round(tl['dur'], 1), [round(s['t0'], 1) for s in tl['subs']])
        print('total', round(TOTAL, 1)); sys.exit()
    files = [render_scene(k) for k in range(len(SC))]
    build_audio(f'{OUT}audio.wav')
    ins = sum((['-i', f] for f in files), []); fl = []; cur = '0:v'; off = 0.0
    for k in range(1, len(files)):
        off += timeline[k - 1]['dur']; fl.append(f'[{cur}][{k}:v]xfade=transition=slideleft:duration={XF}:offset={off:.3f}[x{k}]'); cur = f'x{k}'
    final = f'{OUT}{NAME}.mp4'; tmp = final[:-4] + '.tmp.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y'] + ins + ['-i', f'{OUT}audio.wav', '-filter_complex', ';'.join(fl), '-map', f'[{cur}]', '-map', f'{len(files)}:a',
                    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '21', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', '-shortest', tmp], check=True)
    os.replace(tmp, final); print('done', final, round(probe(final), 1))
