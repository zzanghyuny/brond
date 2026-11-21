#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""브동산 1안 '가격 맞히기 퀴즈' 쇼츠 렌더러 (나레이션 + 시네마틱, 단지별 JSON 설정)

  python3 make_quiz.py quiz/<단지>.json tts                 # 나레이션 생성 → $QUIZ_TTS/<out>/s1~s8.wav
  python3 make_quiz.py quiz/<단지>.json stills 3.6 9 16.5    # 정지 화면 확인 → $QUIZ_OUT/still_*.png
  python3 make_quiz.py quiz/<단지>.json render              # 영상 → $QUIZ_OUT/<out>.mp4 (+ <out>-thumbnail.png)

장면: s1 훅(조감도 + 질문 + 단지명·지역) → s2 입지 개략도(SITE 표시 + 힌트 3줄) → s3 A·B·C + 3초 카운트다운
→ s4 정답 → s5 첫 반전(막대) → s6 비교단지 시세 → 적정가 → s7 판정 배지 → s8 조건·일정 → 첫 화면으로 루프.
장면 길이는 나레이션 길이로 정해진다. 설정 예시: quiz/sangok.json. 규칙: beodongsan-video-team 스킬.
"""
import os, sys, json, wave, subprocess, asyncio, ssl
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
import audio_orig, sfx

CFG_PATH = sys.argv[1]
C = json.load(open(CFG_PATH, encoding='utf8'))
IMG = os.path.join(REPO, 'posts', 'images', C['slug']) + '/'
TTS = os.path.join(os.environ.get('QUIZ_TTS', '/tmp/quiz-tts/'), C['out']) + '/'
FONTS = os.environ.get('QUIZ_FONTS', '/tmp/nanum/')        # NanumGothic-Regular/Bold/ExtraBold.ttf
OUT = os.environ.get('QUIZ_OUT', '/tmp/shorts-out/')
VOICE = C.get('voice', ['ko-KR-InJoonNeural', '+16%', '-3Hz'])   # 채널 보이스 (고정)

W, H, FPS = 1080, 1920, 30
SAFE_L, SAFE_R = 54, 885
CX = (SAFE_L + SAFE_R) // 2            # 469 — 오른쪽 플랫폼 버튼을 피한 중심
BG = (8, 8, 9); INK = (244, 241, 234); SOFT = (185, 181, 172); FAINT = (150, 148, 142)
HAIR = (42, 42, 45); TRACK = (34, 34, 37); DIM = (90, 88, 84); CARD = (16, 16, 18)
BRASS = (200, 164, 92); BRASS_TINT = (42, 36, 22); BRASS_INK = (217, 188, 126)
VERDICT = {'minus': ((240, 138, 102), (43, 24, 19)), 'plus': ((95, 184, 156), (18, 38, 31)), 'even': ((185, 181, 172), (26, 26, 28))}

# ------------------------------------------------------------------ 나레이션
def make_tts():
    import edge_tts, edge_tts.communicate as EC
    ca = '/root/.ccr/ca-bundle.crt'
    if os.path.exists(ca):  # 프록시 환경: edge-tts가 certifi를 고정하므로 CCR CA를 신뢰 저장소로 쓴다
        EC._SSL_CTX = ssl.create_default_context(cafile=ca)
    os.makedirs(TTS, exist_ok=True)
    for k, text in C['narration'].items():
        mp3 = TTS + f'{k}.mp3'
        asyncio.run(edge_tts.Communicate(text, VOICE[0], rate=VOICE[1], pitch=VOICE[2]).save(mp3))
        subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', mp3, '-af',
                        'silenceremove=start_periods=1:start_threshold=-45dB,areverse,'
                        'silenceremove=start_periods=1:start_threshold=-45dB,areverse',
                        '-ar', '44100', '-ac', '1', TTS + f'{k}.wav'], check=True)
        print(k, round(wav_len(TTS + f'{k}.wav'), 2), text)

def wav_len(p):
    with wave.open(p) as w: return w.getnframes() / w.getframerate()

if len(sys.argv) > 2 and sys.argv[2] == 'tts':
    make_tts(); sys.exit(0)

# ------------------------------------------------------------------ 그리기 도구
_f = {}
def F(px, w='B'):
    k = (px, w)
    if k not in _f:
        _f[k] = ImageFont.truetype(FONTS + 'NanumGothic-%s.ttf' % {'R': 'Regular', 'B': 'Bold', 'X': 'ExtraBold'}[w], px)
    return _f[k]

def ease(x):
    x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def eo(x):
    x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3
def tw(s, px, w='B'): return F(px, w).getlength(s)

def fit(s, px, w, maxw):
    while px > 20 and tw(s, px, w) > maxw: px -= 2
    return px

def text(img, xy, s, px, color=INK, w='B', anchor='c', alpha=1.0, dy=0.0):
    """나눔고딕에 없는 글자(㎡ − ①)는 쓰지 않는다: m², -, 1."""
    if alpha <= 0.01 or not s: return
    lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    x = xy[0] - tw(s, px, w) / 2 if anchor == 'c' else (xy[0] - tw(s, px, w) if anchor == 'r' else xy[0])
    d.text((x, xy[1] + dy), s, font=F(px, w), fill=color + (int(255 * min(1, alpha)),))
    img.alpha_composite(lay)

def rect(img, box, fill=None, outline=None, width=2, alpha=1.0, radius=0):
    if alpha <= 0.01: return
    lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    a = int(255 * min(1, alpha))
    d.rounded_rectangle(box, radius=radius, fill=(fill + (a,)) if fill else None,
                        outline=(outline + (a,)) if outline else None, width=width)
    img.alpha_composite(lay)

def ring(img, c, r, color, width, alpha):
    if alpha <= 0.01: return
    lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.ellipse((c[0] - r, c[1] - r, c[0] + r, c[1] + r), outline=color + (int(255 * alpha),), width=width)
    img.alpha_composite(lay)

def load(n, k=1.0):
    im = Image.open(IMG + n).convert('RGB')
    if k != 1.0:
        im = Image.fromarray(np.clip(np.asarray(im).astype(np.float32) * k, 0, 255).astype(np.uint8))
    return im

def kb_box(src, bw, bh, t, z0, z1, cx0, cy0, cx1, cy1):
    k = ease(t); z = z0 + (z1 - z0) * k
    cx = (cx0 + (cx1 - cx0) * k) * src.width; cy = (cy0 + (cy1 - cy0) * k) * src.height
    base = max(bw / src.width, bh / src.height)
    sw, sh = bw / (base * z), bh / (base * z)
    l = min(max(cx - sw / 2, 0), src.width - sw); tp = min(max(cy - sh / 2, 0), src.height - sh)
    return (l, tp, l + sw, tp + sh)

def band(img, src, t, y0, bh, kb, a=1.0, x0=0, bw=W, line=True):
    box = kb_box(src, bw, bh, t, *kb)
    m = src.crop(box).resize((bw, bh), Image.BICUBIC)
    if a < 1: m = Image.blend(Image.new('RGB', m.size, BG), m, a)
    img.paste(m, (x0, y0))
    if line:
        d = ImageDraw.Draw(img)
        d.line((0, y0, W, y0), fill=HAIR, width=2); d.line((0, y0 + bh, W, y0 + bh), fill=HAIR, width=2)
    return box

def badge(img, cx, y, s, px, fg, bg, alpha=1.0, scale=1.0):
    px = int(px * scale); w = tw(s, px, 'X'); pad = px * 0.7; h = px * 1.75
    rect(img, (cx - w / 2 - pad, y, cx + w / 2 + pad, y + h), fill=bg, alpha=alpha, radius=int(h / 2))
    text(img, (cx, y + (h - px) / 2 - px * 0.08), s, px, fg, 'X', alpha=alpha)

def hbar(img, y, label, val, vmax, p, color, alpha=1.0, lw='R', sub=None):
    x0, x1 = SAFE_L + 10, SAFE_R - 160
    text(img, (x0, y), label, 36, INK if color == BRASS else SOFT, lw, anchor='l', alpha=alpha)
    if sub: text(img, (x0 + tw(label, 36, lw) + 14, y + 8), sub, 26, FAINT, 'R', anchor='l', alpha=alpha)
    by = y + 54
    rect(img, (x0, by, x1, by + 40), fill=TRACK, alpha=alpha)
    xe = x0 + (x1 - x0) * (val / vmax) * eo(p)
    if xe > x0 + 2: rect(img, (x0, by, xe, by + 40), fill=color, alpha=alpha)
    text(img, (xe + 16, by - 2), f'{val * eo(p):.2f}억' if p < 1 else f'{val:.2f}억', 40, INK, 'X', anchor='l', alpha=alpha * ease(p * 3))

# ------------------------------------------------------------------ 이미지 준비
S1 = C['s1']; S2 = C['s2']; S6 = C['s6']
COVER = load(S1['img'], 0.92)
BAND6 = load(S6['img'], 0.55)

def dark_map(path):
    """밝은 바탕 입지 개략도(chart-map-naver.png)를 영상용 어두운 테마로 바꾼다.
    무채색은 명암을 뒤집고(흰 바탕→#080809, 검정 글씨→크림), 황동 등 유채색은 그대로 둔다.
    SITE 위치는 황동 픽셀의 중심(범례 줄 제외)으로 찾는다."""
    a = np.asarray(Image.open(path).convert('RGB')).astype(np.float32) / 255
    mx, mn = a.max(2), a.min(2); sat = (mx - mn) / np.maximum(mx, 1e-6)
    lum = a @ np.array([0.299, 0.587, 0.114])
    g = np.array(BG) / 255 * lum[..., None] + np.array(INK) / 255 * (1 - lum[..., None])
    wgt = np.clip((sat - 0.15) / 0.25, 0, 1)[..., None]
    out = g * (1 - wgt) + a * wgt
    br = np.array(BRASS) / 255
    m = (np.abs(a - br).sum(2) < 0.25) & (sat > 0.3)
    m[int(a.shape[0] * 0.85):] = False
    ys, xs = np.nonzero(m)
    if len(xs) > 50:
        site = (float(np.median(xs)), float(np.median(ys)))
    else:  # 예전 개략도: SITE가 검정 사각형 → 검정 픽셀이 가장 빽빽한 40px 칸
        k = (a.sum(2) < 0.3)
        k[int(a.shape[0] * 0.85):] = False
        g = 40; hh, ww = k.shape[0] // g, k.shape[1] // g
        cnt = k[:hh * g, :ww * g].reshape(hh, g, ww, g).sum((1, 3))
        iy, ix = np.unravel_index(cnt.argmax(), cnt.shape)
        site = (ix * g + g / 2, iy * g + g / 2)
    return Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8)), site
if S2.get('map_color'):  # 개략도가 없는 글: 공식 위치도를 원래 색 그대로 쓰고 SITE 위치는 site_px로 준다
    MAP = load(S2['map']); MAP_SITE = (MAP.width / 2, MAP.height / 2)
else:
    MAP, MAP_SITE = dark_map(IMG + S2['map'])
if S2.get('site_px'):  # 예전 개략도(SITE가 검정 사각형)는 위치를 직접 준다(1000px 원본 기준)
    MAP_SITE = tuple(S2['site_px'])

yy, xx = np.mgrid[0:H, 0:W]
_r = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2)
VIGN = np.clip(1.0 - 0.5 * np.clip(_r - 0.45, 0, 1) ** 1.4, 0.4, 1.0).astype(np.float32)[..., None]
_rng = np.random.default_rng(7)
GRAIN = [_rng.normal(0, 2.4, (H, W, 1)).astype(np.float32) for _ in range(6)]

# ------------------------------------------------------------------ 타임라인 (나레이션이 기준)
KEYS = ['s1', 's2', 's3', 's4', 's5', 's6', 's7', 's8']
NAR = {k: wav_len(TTS + f'{k}.wav') for k in KEYS}
LEAD = {'s1': 0.25, 's4': 0.6}        # 정답 공개 직전 멈춤
TAIL = {'s3': 3.0, 's8': 0.7}         # s3: 3초 카운트다운, s8: 마지막 질문 여운
SC = []; t0 = 0.0
for k in KEYS:
    lead = LEAD.get(k, 0.18); dur = lead + NAR[k] + TAIL.get(k, 0.26)
    SC.append((k, t0, dur, lead)); t0 += dur
DUR = t0

def chrome(img):
    x = CX - (tw('브', 40, 'X') + tw('동산', 40, 'R')) / 2
    text(img, (x, 210), '브', 40, INK, 'X', anchor='l')
    text(img, (x + tw('브', 40, 'X'), 210), '동산', 40, SOFT, 'R', anchor='l')
    for i, s in enumerate(C['src']):
        text(img, (CX, 1352 + 38 * i), s, fit(s, 27, 'R', SAFE_R - SAFE_L), FAINT, 'R')

def new(): return Image.new('RGBA', (W, H), BG + (255,))

# ------------------------------------------------------------------ 장면
def hook(img, t, alpha=1.0, anim=True, show_q=True):
    """s1과 마지막 루프가 함께 쓰는 첫 화면: 조감도 + 질문 2줄 + 단지명·지역."""
    a = (lambda d0: ease((t - d0) / 0.45) * alpha) if anim else (lambda d0: alpha)
    dy = (lambda d0: 18 * (1 - eo((t - d0) / 0.6))) if anim else (lambda d0: 0)
    # 2026.11.22 확정 형식: '{지역} 신축 {평형} 분양가,' / '맞히면 부동산 고수'(황동) — 가격은 숨긴다
    text(img, (CX, 975), S1['hook1'], fit(S1['hook1'], 84, 'X', 820), INK, 'X', alpha=a(0.15), dy=dy(0.15))
    if show_q: text(img, (CX, 1075), S1.get('hook2', '맞히면 부동산 고수'), fit(S1.get('hook2', '맞히면 부동산 고수'), 100, 'X', 820), BRASS, 'X', alpha=a(0.6), dy=dy(0.6))
    rect(img, (CX - 60, 1212, CX + 60, 1214), fill=HAIR, alpha=a(1.0))
    text(img, (CX, 1228), S1['name'], fit(S1['name'], 44, 'B', 820), INK, 'B', alpha=a(1.0))
    text(img, (CX, 1288), S1['region'], fit(S1['region'], 32, 'R', 820), SOFT, 'R', alpha=a(1.2))

def s1(t, d, lead):
    img = new()
    band(img, COVER, t / d, 300, 640, S1['kb'])
    hook(img, t)
    return img

def s2(t, d, lead):
    """입지 개략도: 지도 전체 → SITE 쪽으로 천천히 다가가며 황동 고리로 표시, 아래에 힌트 3줄이 차례로."""
    img = new()
    y0, bh = 280, 900; bw = 900; x0 = CX - bw // 2      # 정사각 개략도를 자르지 않고 통째로 보여준 뒤 SITE 쪽으로 살짝 다가간다
    k = t / d
    sx, sy = MAP_SITE[0] / MAP.width, MAP_SITE[1] / MAP.height
    box = band(img, MAP, k, y0, bh, (1.0, 1.05, 0.5, 0.5, 0.5, 0.5 + (sy - 0.5) * 0.3) if not S2.get('map_color') else (1.0, 1.25, sx, 0.5, sx, sy),
               x0=x0, bw=bw, line=False)
    rect(img, (x0 - 1, y0 - 1, x0 + bw, y0 + bh), outline=HAIR, width=2)
    # SITE 위치(밴드 좌표)
    px = x0 + (MAP_SITE[0] - box[0]) / (box[2] - box[0]) * bw
    py = y0 + (MAP_SITE[1] - box[1]) / (box[3] - box[1]) * bh
    for i in range(2):
        ph = ((t * 0.9 + i * 0.5) % 1.0)
        ring(img, (px, py), 30 + 60 * ph, BRASS, 4, (1 - ph) * ease(t / 0.4))
    text(img, (CX, y0 + bh + 12), S2.get('caption', '브동산 자체 제작 입지 개략도 · 방향·거리는 개략'), 24, FAINT, 'R', alpha=ease(t / 0.3))
    times = [lead, lead + NAR['s2'] * 0.38, lead + NAR['s2'] * 0.66]
    n = sum(1 for x in times if t >= x) - 1
    if n >= 0:
        s = S2['hints'][n]; tt = t - times[n]
        text(img, (SAFE_L + 10, 1238), f'{n + 1}/3', 30, BRASS, 'X', anchor='l', alpha=ease(tt / 0.25))
        text(img, (SAFE_L + 80, 1230), s, fit(s, 46, 'X', SAFE_R - SAFE_L - 90), INK, 'X', anchor='l',
             alpha=ease(tt / 0.25), dy=12 * (1 - eo(tt / 0.35)))
    return img

S3 = C['s3']
def options(img, t_in, t, reveal=None):
    for i, (k, v) in enumerate(S3['opts']):
        a = ease((t - t_in - i * 0.18) / 0.3)
        y = 640 + i * 175
        on = reveal is not None and k == S3['answer']
        fade = 1.0 if reveal is None else (1.0 if on else 1 - 0.65 * ease(reveal / 0.4))
        rect(img, (SAFE_L + 40, y, SAFE_R - 40, y + 140), fill=(BRASS_TINT if on and ease(reveal / 0.3) > 0.5 else CARD),
             outline=BRASS if on else DIM, width=4 if on else 2, alpha=a * fade)
        text(img, (SAFE_L + 100, y + 34), k, 72, BRASS if on else SOFT, 'X', anchor='l', alpha=a * fade)
        text(img, (SAFE_R - 100, y + 30), v, 80, BRASS if on else INK, 'X', anchor='r', alpha=a * fade)

def s3(t, d, lead):
    img = new()
    text(img, (CX, 440), S3['q'], 70, INK, 'X', alpha=ease(t / 0.3))
    text(img, (CX, 540), S3['sub'], fit(S3['sub'], 34, 'R', 820), FAINT, 'R', alpha=ease((t - 0.2) / 0.3))
    options(img, 0.15, t)
    cd0 = d - 3.0
    if t >= cd0:
        k = t - cd0; n = max(1, 3 - int(k)); fr = k - int(k); cy = 1215; r = 70
        lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); dd = ImageDraw.Draw(lay)
        dd.ellipse((CX - r, cy - r, CX + r, cy + r), outline=HAIR + (255,), width=6)
        dd.arc((CX - r, cy - r, CX + r, cy + r), -90, -90 + 360 * (1 - k / 3.0), fill=BRASS + (255,), width=6)
        img.alpha_composite(lay)
        sc = 1.0 + 0.25 * (1 - eo(fr / 0.25))
        text(img, (CX, cy - 48 * sc), str(n), int(84 * sc), INK, 'X')
    return img

def s4(t, d, lead):
    img = new()
    text(img, (CX, 440), S3['q'], 70, INK, 'X')
    rv = t - lead + 0.15
    options(img, -5, t, reveal=max(0, rv))
    if rv > 0:
        badge(img, CX, 1165, C['s4']['badge'], 62, BG, BRASS, alpha=ease(rv / 0.25), scale=1 + 0.6 * (1 - eo(rv / 0.35)))
        s = C['s4']['sub']
        text(img, (CX, 1290), s, fit(s, 34, 'R', 820), SOFT, 'R', alpha=ease((rv - 0.6) / 0.4))
    return img

def s5(t, d, lead):
    S = C['s5']; img = new()
    text(img, (CX, 420), S['title'], 44, SOFT, 'B', alpha=ease(t / 0.3))
    text(img, (CX, 500), S['subtitle'], 30, FAINT, 'R', alpha=ease(t / 0.3))
    for i, (lab, v, sub) in enumerate(S['bars']):
        last = i == len(S['bars']) - 1
        hbar(img, 640 + 150 * i, lab, v, S['vmax'], (t - 0.1 - 0.25 * i) / 0.7, BRASS if last else DIM,
             lw='X' if last else 'R', sub=sub)
    a = (t - lead - 0.2)
    text(img, (CX, 1140), S['cap1'], fit(S['cap1'], 64, 'X', 820), INK, 'X', alpha=ease(a / 0.35), dy=14 * (1 - eo(a / 0.5)))
    text(img, (CX, 1235), S['cap2'], 48, SOFT, 'B', alpha=ease((t - lead - NAR['s5'] * 0.6) / 0.35))
    return img

def s6(t, d, lead):
    img = new()
    band(img, BAND6, t / d, 300, 320, S6['kb'], a=0.9)
    text(img, (CX, 660), S6['title'], 40, SOFT, 'B', alpha=ease(t / 0.3))
    for i, (n, s, v) in enumerate(S6['cards']):
        a = ease((t - 0.25 - i * 0.5) / 0.35); y = 740 + i * 150
        rect(img, (SAFE_L + 10, y, SAFE_R - 10, y + 128), fill=CARD, outline=HAIR, width=2, alpha=a)
        text(img, (SAFE_L + 40, y + 22), n, fit(n, 40, 'B', 540), INK, 'B', anchor='l', alpha=a)
        text(img, (SAFE_L + 40, y + 78), s, 26, FAINT, 'R', anchor='l', alpha=a)
        text(img, (SAFE_R - 36, y + 30), v, 58, INK, 'X', anchor='r', alpha=a)
    tf = lead + NAR['s6'] * S6.get('fair_at', 0.55)
    text(img, (CX, 1060), S6['note'], 30, FAINT, 'R', alpha=ease((t - tf + 0.6) / 0.4))
    a2 = ease((t - tf) / 0.35)
    rect(img, (SAFE_L + 60, 1110, SAFE_R - 60, 1295), fill=BRASS_TINT, outline=BRASS, width=3, alpha=a2)
    text(img, (CX, 1128), '브동산 적정가', 40, BRASS_INK, 'B', alpha=a2)
    sc = 1 + 0.25 * (1 - eo((t - tf) / 0.35))
    text(img, (CX, 1184 - 10 * (sc - 1)), S6['fair'], int(88 * sc), BRASS, 'X', alpha=a2)
    return img

def s7(t, d, lead):
    S = C['s7']; img = new()
    text(img, (CX, 470), C.get('area', '84m²') + ' 기준', 40, SOFT, 'B', alpha=ease(t / 0.3))
    for i, (lab, v, col) in enumerate(S['bars']):
        hbar(img, 600 + 160 * i, lab, v, S['vmax'], (t - 0.1 - 0.25 * i) / 0.6, BRASS if col == 'brass' else INK,
             lw='X' if col == 'brass' else 'R')
    rv = lead + 0.35
    if t > rv:
        fg, bg = VERDICT[S['kind']]
        badge(img, CX, 975, S['badge'], 58, fg, bg, alpha=ease((t - rv) / 0.25), scale=1 + 0.5 * (1 - eo((t - rv) / 0.35)))
        text(img, (CX, 1115), S['line1'], 40, INK, 'B', alpha=ease((t - rv - 0.3) / 0.3))
        text(img, (CX, 1175), S['line2'], 30, FAINT, 'R', alpha=ease((t - rv - 0.3) / 0.3))
    return img

def s8(t, d, lead):
    S = C['s8']; img = new()
    loop = ease((t - (d - 1.2)) / 0.9); ai = 1 - loop
    n = NAR['s8']; t1 = lead; t2 = lead + n * 0.12; t3 = lead + n * 0.42
    text(img, (CX, 420), S['l1'], 44, SOFT, 'B', alpha=ease((t - t1) / 0.3) * ai)
    text(img, (CX, 490), S['big'], fit(S['big'], 92, 'X', 820), INK, 'X', alpha=ease((t - t2) / 0.3) * ai)
    text(img, (CX, 610), S['note'], 32, FAINT, 'R', alpha=ease((t - t2 - 0.3) / 0.3) * ai)
    text(img, (CX, 656), S.get('note2', ''), 32, FAINT, 'R', alpha=ease((t - t2 - 0.5) / 0.3) * ai)
    a3 = ease((t - t3) / 0.3) * ai
    rect(img, (SAFE_L + 60, 760, SAFE_R - 60, 1000), fill=CARD, outline=HAIR, width=2, alpha=a3)
    text(img, (CX, 788), S['sched_t'], 34, FAINT, 'B', alpha=a3)
    text(img, (CX, 845), S['sched1'], 42, SOFT, 'B', alpha=a3)
    text(img, (CX, 912), S['sched2'], 56, INK, 'X', alpha=a3)
    tq = lead + n - 1.25; aq = ease((t - tq) / 0.3)
    if loop > 0:  # 마지막 1.2초: 첫 화면(조감도·단지명)으로 되돌아가 반복 재생을 잇는다
        band(img, COVER, 0.0, 300, 640, S1['kb'])
        img.alpha_composite(Image.new('RGBA', (W, H), BG + (int(255 * (1 - loop)),)))
        hook(img, 0, alpha=loop, anim=False, show_q=False)
    text(img, (CX, 1080), S['q'], 96, BRASS, 'X', alpha=aq, dy=16 * (1 - eo((t - tq) / 0.5)))
    return img

FN = {'s1': s1, 's2': s2, 's3': s3, 's4': s4, 's5': s5, 's6': s6, 's7': s7, 's8': s8}

def frame(T):
    for i, (k, st, d, lead) in enumerate(SC):
        if T < st + d or i == len(SC) - 1:
            t = T - st; img = FN[k](t, d, lead); chrome(img)
            if i > 0 and t < 0.22:
                img.alpha_composite(Image.new('RGBA', (W, H), BG + (int(255 * (1 - t / 0.22)),)))
            return img

def finish(img, fi):
    a = np.asarray(img.convert('RGB')).astype(np.float32) * VIGN + GRAIN[fi % 6]
    return np.clip(a, 0, 255).astype(np.uint8)

def thumbnail(path):
    img = new()
    band(img, COVER, 0.6, 330, 820, S1['kb'])
    text(img, (CX, 1190), S1['hook1'], fit(S1['hook1'], 96, 'X', 820), INK, 'X')
    q = S1.get('hook2', '맞히면 부동산 고수')
    text(img, (CX, 1310), q, fit(q, 120, 'X', 820), BRASS, 'X')
    s = '   ·   '.join(f'{k} {v}' for k, v in S3['opts'])
    text(img, (CX, 1500), s, fit(s, 56, 'B', 820), INK, 'B')
    text(img, (CX, 1590), S1['name'], fit(S1['name'], 40, 'B', 820), SOFT, 'B')
    x = CX - (tw('브', 44, 'X') + tw('동산', 44, 'R')) / 2
    text(img, (x, 210), '브', 44, INK, 'X', anchor='l'); text(img, (x + tw('브', 44, 'X'), 210), '동산', 44, SOFT, 'R', anchor='l')
    Image.fromarray(finish(img, 0)).save(path)

# ------------------------------------------------------------------ 오디오
SR = 44100
def build_audio(path):
    n = int(DUR * SR) + SR
    st = {k: (s, d, l) for k, s, d, l in SC}
    starts = [s for _, s, _, _ in SC]
    reveal = st['s4'][0] + st['s4'][2]
    verdict = st['s7'][0] + st['s7'][2] + 0.35
    tmp = OUT + '_music.wav'
    audio_orig.make_audio(tmp, DUR + 1.0, RISE=tuple(starts[1:]), BOOM=((reveal, 0.7), (verdict, 0.6)))
    with wave.open(tmp) as w:
        m = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32).reshape(-1, 2) / 32768
    mus = np.zeros((n, 2)); L = min(n, len(m)); mus[:L] = m[:L]
    nar = np.zeros(n)
    for k, (s, d, l) in st.items():
        with wave.open(TTS + f'{k}.wav') as w:
            x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
        i = int((s + l) * SR); nar[i:i + len(x)] += x[:max(0, n - i)]
    nar /= max(1e-6, np.abs(nar).max()); nar *= 0.85
    env = np.convolve(np.abs(nar), np.ones(int(0.25 * SR)) / int(0.25 * SR), 'same')
    duck = 1.0 - 0.55 * np.clip(env / 0.08, 0, 1)
    out = mus * 0.16 * duck[:, None] + nar[:, None]
    lib = {'whoosh': sfx.whoosh(), 'lowhit': sfx.lowhit(), 'tick': sfx.tick(), 'shimmer': sfx.shimmer(), 'ping': sfx.ping()}
    ev = [(s - 0.35, 'whoosh', 0.18) for s in starts[1:]]
    cd0 = st['s3'][0] + st['s3'][1] - 3.0
    ev += [(cd0 + i, 'tick', 0.32) for i in range(3)]
    ev += [(reveal, 'ping', 0.32), (reveal, 'lowhit', 0.3), (st['s5'][0] + st['s5'][2] + 0.2, 'lowhit', 0.28),
           (verdict, 'lowhit', 0.38), (DUR - 1.6, 'shimmer', 0.22)]
    for t0, name, g in ev:
        i = int(max(0, t0) * SR); x = lib[name] * g; Lx = min(len(x), n - i)
        if Lx > 0: out[i:i + Lx] += x[:Lx, None]
    out = out[:int(DUR * SR)]
    fade = int(0.4 * SR); out[-fade:] *= np.linspace(1, 0, fade)[:, None]
    out = np.tanh(out * 1.05); out /= max(1e-6, np.abs(out).max()) / 0.89
    with wave.open(path, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out * 32767).astype(np.int16).tobytes())

def render():
    name = C['out']; os.makedirs(OUT, exist_ok=True)
    vtmp = OUT + f'_{name}_v.tmp.mp4'
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                          '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '23',
                          '-pix_fmt', 'yuv420p', vtmp], stdin=subprocess.PIPE)
    nf = int(round(DUR * FPS))
    for fi in range(nf):
        p.stdin.write(finish(frame(fi / FPS), fi).tobytes())
        if fi % 300 == 0: print('frame', fi, '/', nf, flush=True)
    p.stdin.close(); assert p.wait() == 0
    build_audio(OUT + f'_{name}.wav')
    tmp = OUT + f'_{name}.tmp.mp4'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', vtmp, '-i', OUT + f'_{name}.wav', '-map', '0:v', '-map', '1:a',
                    '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', tmp], check=True)
    os.replace(tmp, OUT + f'{name}.mp4'); os.remove(vtmp)
    thumbnail(OUT + f'{name}-thumbnail.png')
    print('done', OUT + f'{name}.mp4', round(DUR, 2))

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    cmd = sys.argv[2] if len(sys.argv) > 2 else 'render'
    if cmd == 'stills':
        ts = sys.argv[3:]
        if ts == ['auto']:  # 장면마다 정보가 가장 많은 순간(끝나기 직전) + 마지막 루프 프레임
            ts = [f'{st + d - 0.35:.2f}' for _, st, d, _ in SC[:-1]] + [f'{SC[-1][1] + SC[-1][2] * 0.6:.2f}', f'{DUR - 0.05:.2f}']
        for s in ts:
            T = float(s); Image.fromarray(finish(frame(T), 0)).save(OUT + f'still_{T:05.2f}.png')
        print([(k, round(s, 2), round(d, 2)) for k, s, d, _ in SC], round(DUR, 2))
    elif cmd == 'thumb':
        thumbnail(OUT + f"{C['out']}-thumbnail.png")
    else:
        render()
