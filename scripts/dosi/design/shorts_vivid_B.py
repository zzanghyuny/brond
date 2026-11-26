# -*- coding: utf-8 -*-
"""B안 '리얼 생생' 움직이는 샘플(약 18초): 벤탄 시장 장면 + 출근길 장면."""
import sys, os, subprocess, wave, math, numpy as np
sys.path.insert(0, '/home/claude/work/ep1'); sys.path.insert(0, '/home/claude/src/brond/scripts/shorts')
from PIL import Image, ImageDraw, ImageFont, ImageOps
import graphics as G, cairo, sfx
W, H, FPS = 1920, 1080, 30
D = '/home/claude/work/ep1/'; OUT = D + 'sampleB/'; os.makedirs(OUT, exist_ok=True)
FP = '/tmp/fonts/'; PXB, PB, PM = FP + 'Pretendard-ExtraBold.otf', FP + 'Pretendard-Bold.otf', FP + 'Pretendard-Medium.otf'
BRASS = (200, 164, 92); INK = (17, 17, 17)
F = lambda p, s: ImageFont.truetype(p, s)
def ease_back(x, s=1.7):
    x = max(0.0, min(1.0, x)); x -= 1; return x * x * ((s + 1) * x + s) + 1
def eout(x): x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3
def wav_dur(p): return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p]))

TT = D + 'tts_LONG_sunhi/'
SCENES = [
  dict(clip='35527318', start=0.0, tag='옛 1군 · 벤탄 시장', loc='ben_thanh', lines=[
      (TT + 's05_0_raw.wav', ['도시 모양을 크게 바꾼 건', '프랑스였어요.'], '프랑스'),
      (TT + 's05_1_raw.wav', ['1862년, 프랑스 장교 코팽은 이곳에', '50만 명이 살 도시 계획을 그렸어요.'], '50만 명')],
      bubble=dict(line=1, xy=(1150, 300), t1='1862년', t2='코팽의 도시 계획 · 50만 명', tail=(1210, 470))),
  dict(clip='31149203', start=3.0, tag='호치민 출근길', loc=None, lines=[
      (TT + 's25_0_raw.wav', ['그래도 아직 가장 많이 타는 건', '오토바이예요.'], '오토바이'),
      (TT + 's25_1_raw.wav', ['출퇴근 시간이면 다리와 교차로가', '오토바이로 가득 차요.'], '오토바이')],
      sticker=dict(line=0, delay=0.9, t1='오토바이 1,130만 대', t2='서울 자동차의 세 배 반')),
]
LEAD, GAP, TAIL, XF = 0.45, 0.35, 0.7, 0.3
# 타임라인
t = 0.0
for s in SCENES:
    s['t0'] = t; c = LEAD; s['subs'] = []
    for wav, lines, hl in s['lines']:
        d = wav_dur(wav); s['subs'].append(dict(wav=wav, lines=lines, hl=hl, a=c, b=c + d + 0.1)); c += d + GAP
    s['dur'] = c - GAP + TAIL; t += s['dur']
TOTAL = t; print('total', round(TOTAL, 2))

# ---------- 고정 그림
def chip_img(text):
    f = F(PB, 34); d0 = ImageDraw.Draw(Image.new('L', (1, 1))); w = d0.textlength(text, font=f); h = 62
    im = Image.new('RGBA', (int(w) + 70, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, im.width - 1, h - 1), 31, fill=(255, 255, 255, 245)); d.ellipse((20, h / 2 - 8, 36, h / 2 + 8), fill=BRASS)
    d.text((48, h / 2), text, font=f, fill=INK, anchor='lm'); return im
def minimap(loc):
    w, h = 360, 240; surf = cairo.ImageSurface(cairo.FORMAT_RGB24, w, h); cr = cairo.Context(surf)
    cr.set_source_rgb(20 / 255, 22 / 255, 26 / 255); cr.paint()
    bounds = (106.25, 10.33, 107.62, 11.52); pj = G.Proj.fit(bounds, w, h, pad=0.06)
    cr.set_source_rgb(44 / 255, 46 / 255, 50 / 255); G.path_geom(cr, G.land_for(bounds), pj); cr.fill()
    cr.set_source_rgb(90 / 255, 110 / 255, 130 / 255); cr.set_line_width(1.6)
    for r in G.RIV: G.path_geom(cr, r, pj); cr.stroke()
    cr.set_source_rgba(200 / 255, 164 / 255, 92 / 255, 0.25); G.path_geom(cr, G.HC_NEW_M, pj); cr.fill()
    cr.set_source_rgb(200 / 255, 164 / 255, 92 / 255); cr.set_line_width(2); G.path_geom(cr, G.HC_NEW_M, pj); cr.stroke()
    a = np.ndarray((h, w, 4), np.uint8, surf.get_data()); im = Image.fromarray(np.ascontiguousarray(a[..., [2, 1, 0]]))
    im = ImageOps.expand(im, border=5, fill='white').convert('RGBA')
    if loc is None: return im, None
    x, y = pj(*G.ll(loc)); return im, (x + 5, y + 5)
def bubble_img(t1, t2):
    f1, f2 = F(PXB, 46), F(PB, 32); d0 = ImageDraw.Draw(Image.new('L', (1, 1))); w = max(d0.textlength(t1, font=f1), d0.textlength(t2, font=f2)) + 64
    im = Image.new('RGBA', (int(w), 190), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, 128), 24, fill=(255, 255, 255, 250)); d.polygon([(48, 126), (92, 126), (40, 186)], fill=(255, 255, 255, 250))
    d.text((32, 40), t1, font=f1, fill=BRASS, anchor='lm'); d.text((32, 94), t2, font=f2, fill=INK, anchor='lm'); return im
def sticker_img(t1, t2):
    im = Image.new('RGBA', (900, 300), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((20, 20, 880, 280), 40, fill=(255, 255, 255, 245))
    d.text((450, 112), t1, font=F(PXB, 84), fill=INK, anchor='mm'); d.text((450, 210), t2, font=F(PB, 46), fill=BRASS, anchor='mm')
    return im.rotate(-3, resample=Image.BICUBIC, expand=True)
def sub_img(lines, hl, size=64):
    im = Image.new('RGBA', (W, 260), (0, 0, 0, 0)); d = ImageDraw.Draw(im); f = F(PXB, size); lh = int(size * 1.3)
    for k, ln in enumerate(lines):
        y = 260 - 30 - lh * (len(lines) - k - 0.5)
        parts = [(ln, (255, 255, 255))]
        if hl in ln: a, b = ln.split(hl, 1); parts = [(a, (255, 255, 255)), (hl, BRASS), (b, (255, 255, 255))]
        tw = sum(d.textlength(p, font=f) for p, _ in parts); x = W / 2 - tw / 2
        for p, col in parts:
            d.text((x, y), p, font=f, fill=col, anchor='lm', stroke_width=7, stroke_fill=(0, 0, 0)); x += d.textlength(p, font=f)
    return im   # 아래끝 = 화면 y 932
def paste_scaled(base, im, cx, cy, sc, alpha=1.0, anchor=(0.5, 0.5)):
    if sc <= 0.01 or alpha <= 0.01: return
    w, h = max(1, int(im.width * sc)), max(1, int(im.height * sc)); s = im.resize((w, h), Image.BICUBIC)
    if alpha < 1: a = s.getchannel('A').point(lambda v: int(v * alpha)); s.putalpha(a)
    base.alpha_composite(s, (int(cx - w * anchor[0]), int(cy - h * anchor[1])))

# ---------- 장면 렌더
def render_scene(i, s):
    L = s['dur'] + (XF if i < len(SCENES) - 1 else 0); N = int(round(L * FPS))
    src = f'/home/claude/media/pexels/px_{s["clip"]}.mp4'
    dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', str(s['start']), '-i', src, '-t', f'{L + 0.2:.3f}', '-vf',
                            f'fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},eq=saturation=1.35:contrast=1.08:brightness=0.02', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    out = f'{OUT}scene_{i}.mp4'
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    chip = chip_img(s['tag']); mm, dot = minimap(s['loc']); subs = [sub_img(sb['lines'], sb['hl']) for sb in s['subs']]
    bub = bubble_img(s['bubble']['t1'], s['bubble']['t2']) if 'bubble' in s else None
    stk = sticker_img(s['sticker']['t1'], s['sticker']['t2']) if 'sticker' in s else None
    last = None
    for fi in range(N):
        t = fi / FPS; raw = dec.stdout.read(W * H * 3)
        if len(raw) < W * H * 3: raw = last
        last = raw
        fr = Image.frombytes('RGB', (W, H), raw).convert('RGBA')
        # 위치 칩: 왼쪽에서 밀려 들어옴
        k = eout((t - 0.15) / 0.45); fr.alpha_composite(chip, (int(-chip.width + (50 + chip.width) * k), 44)) if k > 0 else None
        # 미니맵 + 깜박이는 점
        k2 = eout((t - 0.35) / 0.5)
        if k2 > 0:
            m = mm.copy(); md = ImageDraw.Draw(m); r = 9 + 5 * (0.5 + 0.5 * math.sin(t * 6))
            if dot: x, y = dot; md.ellipse((x - r - 6, y - r - 6, x + r + 6, y + r + 6), outline=(255, 80, 60, 120), width=3); md.ellipse((x - 9, y - 9, x + 9, y + 9), fill=(255, 80, 60), outline='white', width=3)
            paste_scaled(fr, m, W - 60 - m.width / 2, 40 + m.height / 2 - (1 - k2) * 20, 1.0, k2)
        # 말풍선 / 스티커: 튀어나오듯
        if bub is not None:
            t0 = s['subs'][s['bubble']['line']]['a'] + 0.4; sc = ease_back((t - t0) / 0.45)
            paste_scaled(fr, bub, s['bubble']['xy'][0], s['bubble']['xy'][1] + bub.height, sc, min(1, (t - t0) / 0.15) if t > t0 else 0, anchor=(0.1, 1.0))
        if stk is not None:
            t0 = s['subs'][s['sticker']['line']]['a'] + s['sticker']['delay']; sc = ease_back((t - t0) / 0.5)
            paste_scaled(fr, stk, W / 2, 360, sc, min(1, (t - t0) / 0.15) if t > t0 else 0)
        # 자막: 살짝 커졌다 제자리
        for sb, im in zip(s['subs'], subs):
            if sb['a'] <= t <= sb['b']:
                sc = 1.0 + 0.06 * (1 - eout((t - sb['a']) / 0.18)); paste_scaled(fr, im, W / 2, 932 - 130 + 130, sc, 1.0, anchor=(0.5, 1.0))
        enc.stdin.write(fr.convert('RGB').tobytes())
    enc.stdin.close(); enc.wait(); dec.kill(); return out

files = [render_scene(i, s) for i, s in enumerate(SCENES)]
# ---------- 소리: 나레이션 + 잔잔한 음악 + 장면 전환 whoosh + 말풍선 pop
SR = 44100; n = int(SR * (TOTAL + 0.5)); voice = np.zeros(n); fx = np.zeros(n)
def add(buf, x, at, g=1.0):
    i = int(at * SR); L = min(len(x), n - i)
    if L > 0: buf[i:i + L] += x[:L] * g
for s in SCENES:
    for sb in s['subs']:
        with wave.open(sb['wav']) as w: x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
        add(voice, x, s['t0'] + sb['a'])
    if 'bubble' in s: add(fx, sfx.ping(), s['t0'] + s['subs'][s['bubble']['line']]['a'] + 0.4, 0.18)
    if 'sticker' in s: add(fx, sfx.ping(), s['t0'] + s['subs'][s['sticker']['line']]['a'] + s['sticker']['delay'], 0.18)
add(fx, sfx.whoosh(), SCENES[1]['t0'] - 0.35, 0.10)
t = np.arange(n) / SR; music = sum(np.sin(2 * np.pi * f * t) * a for f, a in [(110, .3), (164.81, .2), (220, .18), (329.63, .1)])
music *= np.clip(t / 1.5, 0, 1) * np.clip((TOTAL + 0.5 - t) / 2, 0, 1)
env = np.convolve((np.abs(voice) > 0.02).astype(float), np.ones(int(SR * 0.3)) / int(SR * 0.3), 'same')
mix = voice / max(1e-6, np.abs(voice).max()) * 0.9 + music / max(1e-6, np.abs(music).max()) * (0.12 - 0.06 * np.clip(env * 3, 0, 1)) + fx
mix = np.tanh(mix); mix /= max(1e-6, np.abs(mix).max()) / 0.9
with wave.open(OUT + 'audio.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.stack([mix, mix], 1) * 32767).astype(np.int16).tobytes())
off = SCENES[0]['dur']
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', files[0], '-i', files[1], '-i', OUT + 'audio.wav', '-filter_complex', f'[0:v][1:v]xfade=transition=slideleft:duration={XF}:offset={off:.3f}[v]',
                '-map', '[v]', '-map', '2:a', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', '-shortest', '-movflags', '+faststart', OUT + 'design-B-sample.mp4'], check=True)
print('done')
