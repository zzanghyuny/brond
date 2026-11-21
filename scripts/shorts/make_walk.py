#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""브동산 4안 '진짜 걸어보면' 쇼츠 렌더러 — Mapbox 정적 지도(dark-v11) 위에 Mapbox 도보 경로를 그린다.

  python3 make_walk.py walk/<단지>.json tts            # 나레이션 → $WALK_TTS/<out>/s1~s5.wav
  python3 make_walk.py walk/<단지>.json stills 2 8 15  # 정지 화면 → $WALK_OUT/still_*.png
  python3 make_walk.py walk/<단지>.json render         # 영상 → $WALK_OUT/<out>.mp4 (+ -thumbnail.png)

입력
  walk/<단지>.json         — 문구·나레이션·라벨 (예: walk/mullae.json)
  walk/<단지>.routes.json  — SITE·역 좌표, Mapbox Directions(walking, geojson full) 경로, 지도 center/zoom
  $WALK_MAPS/<단지>.png    — Mapbox Static Images dark-v11 1280×1280 (routes.json의 map 값 그대로).
                             지도 이미지는 저장소에 넣지 않는다. 지도 하단 Mapbox 로고·저작권 표기는 자르지 않는다.
장면: s1 훅(조감도 + 홍보 문구 + 질문) → s2 지도(SITE·역 2곳) → s3 1번 역 경로 + 타이머 → s4 2번 역 경로 + 타이머
→ s5 정리 카드(홍보 문구 vs 실제 도보) + 일정 + 질문 → 첫 화면으로 루프. 장면 길이는 나레이션 길이로 정해진다.
구도심·기존 시가지 단지에만 쓴다(신규 택지는 지도에 새 길·예정역이 없다).
"""
import os, sys, json, math, wave, subprocess, asyncio, ssl
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
import audio_orig, sfx

CFG_PATH = sys.argv[1]
C = json.load(open(CFG_PATH, encoding='utf8'))
KEY = os.path.basename(CFG_PATH).replace('.json', '')
R = json.load(open(os.path.join(os.path.dirname(CFG_PATH), KEY + '.routes.json')))
IMG = os.path.join(REPO, 'posts', 'images', C['slug']) + '/'
TTS = os.path.join(os.environ.get('WALK_TTS', '/tmp/walk-tts/'), C['out']) + '/'
MAPS = os.environ.get('WALK_MAPS', '/tmp/walk-maps/')
FONTS = os.environ.get('QUIZ_FONTS', '/tmp/nanum/')
OUT = os.environ.get('WALK_OUT', '/tmp/shorts-out/')
VOICE = C.get('voice', ['ko-KR-InJoonNeural', '+16%', '-3Hz'])
SCENES = ['s1', 's2', 's3', 's4', 's5']

def wav_len(p):
    with wave.open(p) as w: return w.getnframes() / w.getframerate()

def make_tts():
    import edge_tts, edge_tts.communicate as EC
    ca = '/root/.ccr/ca-bundle.crt'
    if os.path.exists(ca): EC._SSL_CTX = ssl.create_default_context(cafile=ca)
    os.makedirs(TTS, exist_ok=True)
    for k in SCENES:
        text = C['narration'][k]; mp3 = TTS + f'{k}.mp3'
        asyncio.run(edge_tts.Communicate(text, VOICE[0], rate=VOICE[1], pitch=VOICE[2]).save(mp3))
        subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', mp3, '-af',
                        'silenceremove=start_periods=1:start_threshold=-45dB,areverse,'
                        'silenceremove=start_periods=1:start_threshold=-45dB,areverse',
                        '-ar', '44100', '-ac', '1', TTS + f'{k}.wav'], check=True)
        print(k, round(wav_len(TTS + f'{k}.wav'), 2), text)

if len(sys.argv) > 2 and sys.argv[2] == 'tts':
    make_tts(); sys.exit(0)

W, H, FPS = 1080, 1920, 30
SAFE_L, SAFE_R = 54, 885; CX = (SAFE_L + SAFE_R) // 2
BG = (8, 8, 9); INK = (244, 241, 234); SOFT = (185, 181, 172); FAINT = (150, 148, 142)
HAIR = (42, 42, 45); CARD = (16, 16, 18); BRASS = (200, 164, 92); DIMBRASS = (120, 100, 62)

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
def text(img, xy, s, px, color=INK, w='B', anchor='c', alpha=1.0, stroke=0):
    if alpha <= 0.01 or not s: return
    lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    x = xy[0] - tw(s, px, w) / 2 if anchor == 'c' else (xy[0] - tw(s, px, w) if anchor == 'r' else xy[0])
    a = int(255 * min(1, alpha))
    d.text((x, xy[1]), s, font=F(px, w), fill=color + (a,), stroke_width=stroke, stroke_fill=BG + (a,))
    img.alpha_composite(lay)
def rect(img, box, fill=None, outline=None, width=2, alpha=1.0, radius=0):
    if alpha <= 0.01: return
    lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay); a = int(255 * min(1, alpha))
    d.rounded_rectangle(box, radius=radius, fill=(fill + (a,)) if fill else None, outline=(outline + (a,)) if outline else None, width=width)
    img.alpha_composite(lay)

# ---------------- 지도 좌표 (Web Mercator, Mapbox 512px 타일)
MY0, MS = 300, 1080
M = R['map']
def proj(lon, lat):
    lon0, lat0 = M['center']; z = M['zoom']; S = M['size']; k = 512 * 2 ** z
    mx = lambda lo: (lo + 180) / 360 * k
    my = lambda la: (1 - math.log(math.tan(math.pi / 4 + math.radians(la) / 2)) / math.pi) / 2 * k
    return (S / 2 + mx(lon) - mx(lon0)) * MS / S, MY0 + (S / 2 + my(lat) - my(lat0)) * MS / S
MAP = Image.open(MAPS + KEY + '.png').convert('RGB').resize((MS, MS), Image.LANCZOS)
S1 = C['s1']; COVER = Image.open(IMG + S1['img']).convert('RGB')
SITE = proj(*R['site'])
RT = []
for r, rc in zip(R['routes'], C['routes']):
    pts = [proj(*p) for p in r['coords']]; c = [0.0]
    for a, b in zip(pts, pts[1:]): c.append(c[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    RT.append(dict(pts=pts, cum=c, dest=proj(*r['dest']), dist=r['distance'], dur=r['duration'], **rc))

def partial(rt, f):
    pts, c = rt['pts'], rt['cum']; L = c[-1] * f; out = [pts[0]]
    for i in range(1, len(pts)):
        if c[i] <= L: out.append(pts[i])
        else:
            q = (L - c[i - 1]) / max(1e-6, c[i] - c[i - 1]); a, b = pts[i - 1], pts[i]
            out.append((a[0] + (b[0] - a[0]) * q, a[1] + (b[1] - a[1]) * q)); break
    return out

def kb(src, bw, bh, t, z0, z1, cx0, cy0, cx1, cy1):
    k = ease(t); z = z0 + (z1 - z0) * k
    cx = (cx0 + (cx1 - cx0) * k) * src.width; cy = (cy0 + (cy1 - cy0) * k) * src.height
    base = max(bw / src.width, bh / src.height); sw, sh = bw / (base * z), bh / (base * z)
    l = min(max(cx - sw / 2, 0), src.width - sw); tp = min(max(cy - sh / 2, 0), src.height - sh)
    return src.crop((l, tp, l + sw, tp + sh)).resize((bw, bh), Image.BICUBIC)

def new(): return Image.new('RGBA', (W, H), BG + (255,))
def chrome(img):
    x = CX - (tw('브', 40, 'X') + tw('동산', 40, 'R')) / 2
    text(img, (x, 210), '브', 40, INK, 'X', anchor='l'); text(img, (x + tw('브', 40, 'X'), 210), '동산', 40, SOFT, 'R', anchor='l')
    s1 = '지도 © Mapbox © OpenStreetMap · 도보 경로·시간: Mapbox 도보(현재 도로 기준)'
    s2 = C['foot']
    text(img, (CX, 1395), s1, fit(s1, 26, 'R', 830), FAINT, 'R'); text(img, (CX, 1430), s2, fit(s2, 26, 'R', 830), FAINT, 'R')

def map_base(img):
    img.paste(MAP, (0, MY0)); d = ImageDraw.Draw(img)
    d.line((0, MY0, W, MY0), fill=HAIR, width=2); d.line((0, MY0 + MS, W, MY0 + MS), fill=HAIR, width=2)

def marker(img, p, label, sub=None, kind='stn', alpha=1.0, t=0.0, side='r'):
    if alpha <= 0.01: return
    lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay); a = int(255 * alpha); x, y = p
    if kind == 'site':
        d.rectangle((x - 16, y - 16, x + 16, y + 16), fill=BRASS + (a,), outline=INK + (a,), width=3)
        for i in range(2):
            ph = (t * 0.9 + i * 0.5) % 1.0; r = 26 + 60 * ph
            d.ellipse((x - r, y - r, x + r, y + r), outline=BRASS + (int(a * (1 - ph)),), width=4)
    else:
        d.ellipse((x - 14, y - 14, x + 14, y + 14), fill=INK + (a,), outline=BG + (a,), width=3)
    img.alpha_composite(lay)
    ox = {'r': 30, 'l': -30, 'u': 0, 'd': 0}[side]; oy = {'r': 0, 'l': 0, 'u': -64, 'd': 54}[side]
    anc = {'r': 'l', 'l': 'r', 'u': 'c', 'd': 'c'}[side]
    text(img, (x + ox, y - 26 + oy), label, 40, BRASS if kind == 'site' else INK, 'X', anchor=anc, alpha=alpha, stroke=5)
    if sub: text(img, (x + ox, y + 20 + oy), sub, 28, SOFT, 'B', anchor=anc, alpha=alpha, stroke=4)

def caption(img, s, alpha=1.0, y=MY0 + 28, px=60, color=INK):
    if alpha <= 0.01: return
    p = fit(s, px, 'X', 900); w = tw(s, p, 'X')
    rect(img, (CX - w / 2 - 28, y - 14, CX + w / 2 + 28, y + p + 18), fill=BG, alpha=0.84 * alpha, radius=10)
    text(img, (CX, y), s, p, color, 'X', alpha=alpha)

def draw_route(img, rt, f, color=BRASS, width=10, head=True, alpha=1.0):
    if f <= 0: return
    seg = partial(rt, f)
    if len(seg) < 2: return
    lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.line(seg, fill=BG + (int(200 * alpha),), width=width + 8, joint='curve')
    d.line(seg, fill=color + (int(255 * alpha),), width=width, joint='curve')
    if head:
        hx, hy = seg[-1]; d.ellipse((hx - 15, hy - 15, hx + 15, hy + 15), fill=INK + (255,), outline=BRASS + (255,), width=5)
    img.alpha_composite(lay)

def timer_box(img, sec, meters, alpha=1.0, done=False):
    mm, ss = int(sec // 60), int(sec % 60); y = MY0 + MS - 190
    rect(img, (SAFE_L + 20, y, SAFE_L + 420, y + 150), fill=BG, outline=BRASS if done else HAIR, width=3, alpha=0.9 * alpha, radius=8)
    text(img, (SAFE_L + 46, y + 18), '도보', 30, SOFT, 'B', anchor='l', alpha=alpha)
    text(img, (SAFE_L + 46, y + 58), f'{mm:02d}:{ss:02d}', 70, BRASS if done else INK, 'X', anchor='l', alpha=alpha)
    text(img, (SAFE_L + 400, y + 82), f'{meters / 1000:.2f}km', 40, INK, 'X', anchor='r', alpha=alpha)

def site_marker(img, t, alpha=1.0, sub=None):
    marker(img, SITE, C['site_label'], sub, 'site', alpha, t, side=C.get('site_side', 'r'))
def stn(img, i, alpha=1.0, sub=True):
    rc = RT[i]; marker(img, rc['dest'], rc['label'], rc.get('sub') if sub else None, 'stn', alpha, side=rc.get('side', 'r'))

# ---------------- 타임라인 (나레이션 기준)
NAR = {k: wav_len(TTS + f'{k}.wav') for k in SCENES}
LEAD = 0.2
ANIM = {k: max(3.5, NAR[k] - 0.6) for k in ('s3', 's4')}
DUR_S = {'s1': 0.25 + NAR['s1'] + 0.35, 's2': LEAD + NAR['s2'] + 0.45,
         's3': LEAD + max(NAR['s3'], ANIM['s3'] + 0.5) + 1.0, 's4': LEAD + max(NAR['s4'], ANIM['s4'] + 0.5) + 1.0,
         's5': LEAD + NAR['s5'] + 1.5}
SC = []; t0 = 0
for k in SCENES: SC.append((k, t0, DUR_S[k])); t0 += DUR_S[k]
DUR = t0

def s1(t, d, loop=False):
    img = new(); img.paste(kb(COVER, W, 640, 0 if loop else t / d, *S1['kb']), (0, 300))
    a = (lambda d0: 1.0) if loop else (lambda d0: ease((t - d0) / 0.4))
    text(img, (CX, 975), C['hook1'], fit(C['hook1'], 76, 'X', 820), INK, 'X', alpha=a(0.15))
    if not loop: text(img, (CX, 1072), C['hook2'], fit(C['hook2'], 100, 'X', 840), BRASS, 'X', alpha=a(0.6))
    rect(img, (CX - 60, 1212, CX + 60, 1214), fill=HAIR, alpha=a(1.0))
    text(img, (CX, 1228), C['name'], 44, INK, 'B', alpha=a(1.0))
    text(img, (CX, 1288), C['region'], fit(C['region'], 30, 'R', 820), SOFT, 'R', alpha=a(1.2))
    return img

def s2(t, d):
    img = new(); map_base(img)
    site_marker(img, t, ease(t / 0.4), C.get('site_sub'))
    n = NAR['s2']
    stn(img, 0, ease((t - 0.25 * n) / 0.4)); stn(img, 1, ease((t - 0.6 * n) / 0.4))
    caption(img, C['s2_caption'], ease((t - 0.2) / 0.4))
    return img

def walk_scene(t, d, i):
    img = new(); map_base(img)
    if i == 1: draw_route(img, RT[0], 1.0, DIMBRASS, 7, head=False, alpha=0.9)
    a0, a1 = 0.5, 0.5 + ANIM[f's{3 + i}']
    f = eo((t - a0) / (a1 - a0)) if t > a0 else 0
    draw_route(img, RT[i], f)
    for j in range(2): stn(img, j, 1.0, sub=(j == i))
    site_marker(img, t)
    rt = RT[i]; done = f >= 0.999
    timer_box(img, rt['dur'] * f, rt['dist'] * f, ease(t / 0.3), done=done)
    if not done: caption(img, rt['caption'])
    else: caption(img, rt['result'], ease((t - a1) / 0.3), color=BRASS, px=72)
    return img

def s5(t, d):
    img = new(); P = C['s5']
    loop = ease((t - (d - 1.2)) / 0.9); ai = 1 - loop
    a = lambda d0: ease((t - d0) / 0.35) * ai
    text(img, (CX, 380), '정리하면', 40, SOFT, 'B', alpha=a(0))
    for i, (k, v) in enumerate(P['rows']):
        y = 470 + i * 150
        rect(img, (SAFE_L + 20, y, SAFE_R - 20, y + 120), fill=CARD, outline=HAIR, width=2, alpha=a(0.2 + i * 0.4))
        text(img, (SAFE_L + 50, y + 42), k, fit(k, 32, 'B', 330), FAINT, 'B', anchor='l', alpha=a(0.2 + i * 0.4))
        text(img, (SAFE_R - 50, y + 32), v, fit(v, 48, 'X', 450), SOFT if i == 0 else INK, 'X', anchor='r', alpha=a(0.2 + i * 0.4))
    text(img, (CX, 945), P['note'], fit(P['note'], 40, 'B', 820), INK, 'B', alpha=a(1.5))
    text(img, (CX, 1002), P['note2'], fit(P['note2'], 30, 'R', 820), FAINT, 'R', alpha=a(1.7))
    tq = LEAD + NAR['s5'] - 1.6; aq = ease((t - tq) / 0.3) * ai
    rect(img, (CX - 300, 1170, CX + 300, 1250), fill=CARD, outline=BRASS, width=2, alpha=a(2.0), radius=8)
    text(img, (CX, 1190), P['sched'], fit(P['sched'], 36, 'B', 560), BRASS, 'B', alpha=a(2.0))
    text(img, (CX, 1068), P['q'], fit(P['q'], 84, 'X', 840), BRASS, 'X', alpha=aq)
    if loop > 0:
        lo = s1(0, 1, loop=True)
        lo.alpha_composite(Image.new('RGBA', (W, H), BG + (int(255 * (1 - loop)),)))
        img = Image.blend(img, lo, loop)
    return img

FN = {'s1': s1, 's2': s2, 's3': lambda t, d: walk_scene(t, d, 0), 's4': lambda t, d: walk_scene(t, d, 1), 's5': s5}
yy, xx = np.mgrid[0:H, 0:W]
_r = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2)
VIGN = np.clip(1.0 - 0.45 * np.clip(_r - 0.5, 0, 1) ** 1.4, 0.45, 1.0).astype(np.float32)[..., None]
def frame(T):
    for i, (k, st, d) in enumerate(SC):
        if T < st + d or i == len(SC) - 1:
            t = T - st; img = FN[k](t, d); chrome(img)
            if i > 0 and t < 0.22: img.alpha_composite(Image.new('RGBA', (W, H), BG + (int(255 * (1 - t / 0.22)),)))
            return np.clip(np.asarray(img.convert('RGB')).astype(np.float32) * VIGN, 0, 255).astype(np.uint8)

SR = 44100
def build_audio(path):
    n = int(DUR * SR) + SR; st = {k: (s, d) for k, s, d in SC}; starts = [s for _, s, _ in SC]
    done = [st['s3'][0] + 0.5 + ANIM['s3'], st['s4'][0] + 0.5 + ANIM['s4']]
    tmp = OUT + '_walk_music.wav'
    audio_orig.make_audio(tmp, DUR + 1, RISE=tuple(starts[1:]), BOOM=tuple((x, 0.6) for x in done))
    with wave.open(tmp) as w: m = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32).reshape(-1, 2) / 32768
    mus = np.zeros((n, 2)); L = min(n, len(m)); mus[:L] = m[:L]
    nar = np.zeros(n)
    for k, (s, d) in st.items():
        with wave.open(TTS + f'{k}.wav') as w: x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
        i = int((s + (0.25 if k == 's1' else LEAD)) * SR); nar[i:i + len(x)] += x[:max(0, n - i)]
    nar /= max(1e-6, np.abs(nar).max()); nar *= 0.85
    env = np.convolve(np.abs(nar), np.ones(int(0.25 * SR)) / int(0.25 * SR), 'same')
    out = mus * 0.16 * (1 - 0.55 * np.clip(env / 0.08, 0, 1))[:, None] + nar[:, None]
    lib = {'whoosh': sfx.whoosh(), 'ping': sfx.ping(), 'tick': sfx.tick(), 'shimmer': sfx.shimmer()}
    ev = [(s - 0.35, 'whoosh', 0.18) for s in starts[1:]] + [(x, 'ping', 0.3) for x in done] + [(DUR - 1.6, 'shimmer', 0.22)]
    for k in ('s3', 's4'):
        ev += [(st[k][0] + 0.5 + j * 0.5, 'tick', 0.12) for j in range(int(ANIM[k] / 0.5))]
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
    Image.fromarray(frame(min(SC[0][2] - 0.1, 1.9))).save(OUT + f'{name}-thumbnail.png')
    print('done', OUT + f'{name}.mp4', round(DUR, 2))

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    if sys.argv[2] == 'stills':
        for s in sys.argv[3:]: Image.fromarray(frame(float(s))).save(OUT + f'still_{KEY}_{float(s):05.2f}.png')
        print([(k, round(s, 2), round(d, 2)) for k, s, d in SC], round(DUR, 2))
    elif sys.argv[2] == 'render': render()
