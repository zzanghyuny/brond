#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""브동산 아르뮤제자이 예상프리미엄 분석 — 30초 시네마틱 9:16 영상 (코드 렌더링, 외부 AI 없음)"""
import math, os, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS, DUR = 1080, 1920, 30, 30.0
IMG = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'posts', 'images', 'armusee-xi-ansan') + '/'
OUT = os.environ.get('SHORTS_OUT', '/tmp/shorts-out/')
FONT = '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'
BRASS = (200, 164, 92)  # 황동색 포인트(원래 영상 스타일)
WHITE = (244, 241, 234)
GRAY = (150, 148, 142)
BG = (8, 8, 9)
SAFE_L, SAFE_R, SAFE_T, SAFE_B = 54, 885, 288, 1440
CX = (SAFE_L + SAFE_R) // 2  # 469: 플랫폼 버튼을 피한 안전영역 중심

_fonts = {}
def F(px):
    if px not in _fonts:
        _fonts[px] = ImageFont.truetype(FONT, px)
    return _fonts[px]

def ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)

def ease_out(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3

def text_w(s, px, spacing=0):
    f = F(px)
    return sum(f.getlength(c) for c in s) + spacing * (len(s) - 1)

def draw_text(img, xy, s, px, color=WHITE, anchor='c', spacing=0, bold=1, alpha=1.0):
    """anchor 'c': xy[0] = 중심 x. 글자 간격과 굵기(stroke) 지원, alpha로 페이드."""
    if alpha <= 0:
        return
    layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    f = F(px)
    w = text_w(s, px, spacing)
    x = xy[0] - w / 2 if anchor == 'c' else xy[0]
    y = xy[1]
    a = int(255 * min(1.0, alpha))
    for c in s:
        d.text((x, y), c, font=f, fill=color + (a,), stroke_width=bold, stroke_fill=color + (a,))
        x += f.getlength(c) + spacing
    img.paste(layer, (0, 0), layer)

# ---------------------------------------------------------------- 이미지 준비
def load(name):
    return Image.open(IMG + name).convert('RGB')

def grade(im, bright=0.62, tint=(0.88, 0.95, 1.08)):
    a = np.asarray(im).astype(np.float32) / 255.0
    g = a.mean(axis=2, keepdims=True)
    a = a * 0.45 + g * 0.55
    a = a * np.array(tint, dtype=np.float32) * bright
    a = np.clip((a - 0.5) * 1.18 + 0.5 + (bright - 0.5) * 0.15, 0, 1)
    return Image.fromarray((a * 255).astype(np.uint8))

AERIAL = grade(load('aerial-cg.jpg'))           # 1100x545
from PIL import ImageOps
MAPIMG = ImageOps.invert(load('chart-map-naver.png'))  # 개략도를 네이비 톤으로

def kenburns(src, box_w, box_h, t, z0, z1, cx0, cy0, cx1, cy1):
    """src 이미지를 box_w x box_h 창으로 보여주는 느린 줌·이동. 중심좌표는 0~1."""
    k = ease(t)
    z = z0 + (z1 - z0) * k
    cx = (cx0 + (cx1 - cx0) * k) * src.width
    cy = (cy0 + (cy1 - cy0) * k) * src.height
    base = max(box_w / src.width, box_h / src.height)
    sw, sh = box_w / (base * z), box_h / (base * z)
    l = min(max(cx - sw / 2, 0), src.width - sw)
    tp = min(max(cy - sh / 2, 0), src.height - sh)
    return src.crop((l, tp, l + sw, tp + sh)).resize((box_w, box_h), Image.BICUBIC)

# ---------------------------------------------------------------- 비네트·그레인
yy, xx = np.mgrid[0:H, 0:W]
_r = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2)
VIGN = np.clip(1.0 - 0.55 * np.clip(_r - 0.45, 0, 1) ** 1.4, 0.35, 1.0).astype(np.float32)[..., None]
_rng = np.random.default_rng(7)
GRAIN = [(_rng.normal(0, 2.6, (H, W, 1))).astype(np.float32) for _ in range(6)]

def finish(im, fi):
    a = np.asarray(im).astype(np.float32)
    a = a * VIGN + GRAIN[fi % 6]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))

# ---------------------------------------------------------------- 장면
def hline(img, y, x0, x1, p, color=BRASS, w=3):
    d = ImageDraw.Draw(img)
    xe = x0 + (x1 - x0) * ease(p)
    d.line((x0, y, xe, y), fill=color, width=w)

def disclaimer(img, a):
    draw_text(img, (CX, 1395), '브동산 모형 추정치 · 확정 수익 아님 · 84㎡ 평균 · 2026.11.13 기준', 28, GRAY, bold=0, alpha=a)

def scene_title(t):  # 0~3
    img = Image.new('RGB', (W, H), BG)
    hline(img, 880, CX - 280, CX + 280, ease_out((t - 0.2) / 1.1))
    draw_text(img, (CX, 700), '브동산', 46, BRASS, spacing=18, bold=1, alpha=ease((t - 0.7) / 0.7))
    draw_text(img, (CX, 930 - 14 * (1 - ease_out((t - 1.0) / 0.9))), '아르뮤제자이', 118, WHITE, spacing=6, bold=2, alpha=ease((t - 1.0) / 0.8))
    draw_text(img, (CX, 1090 - 12 * (1 - ease_out((t - 1.5) / 0.9))), '예상프리미엄 분석', 70, WHITE, spacing=10, bold=1, alpha=ease((t - 1.5) / 0.8))
    hline(img, 1010, CX - 280, CX + 280, ease_out((t - 1.9) / 0.9), w=2)
    return img

def scene_aerial(t):  # 3~7 (len 4)
    img = Image.new('RGB', (W, H), BG)
    bh = 640
    band = kenburns(AERIAL, W, bh, t / 4.0, 1.0, 1.35, 0.68, 0.55, 0.70, 0.42)
    img.paste(band, (0, 560))
    d = ImageDraw.Draw(img)
    d.line((0, 560, W, 560), fill=BRASS, width=2); d.line((0, 560 + bh, W, 560 + bh), fill=BRASS, width=2)
    draw_text(img, (CX, 380), '안산 성포동', 66, WHITE, spacing=8, bold=1, alpha=ease((t - 0.3) / 0.8))
    draw_text(img, (CX, 1262), '지하 6층 ~ 지상 49층 · 6개 동', 44, WHITE, spacing=2, bold=0, alpha=ease((t - 1.0) / 0.8))
    draw_text(img, (CX, 1325), '아파트 984세대', 56, BRASS, spacing=4, bold=1, alpha=ease((t - 1.5) / 0.8))
    draw_text(img, (CX, 1400), '조감도는 CG이며 실제와 다를 수 있음 · 출처: 공식 분양 홈페이지', 28, GRAY, bold=0, alpha=ease((t - 1.8) / 0.8))
    return img

def scene_map(t):  # 7~11 (len 4)
    img = Image.new('RGB', (W, H), BG)
    draw_text(img, (CX, 330), '입지', 52, BRASS, spacing=14, bold=1, alpha=ease(t / 0.7))
    m = kenburns(MAPIMG, 800, 800, t / 4.0, 1.0, 1.06, 0.5, 0.5, 0.5, 0.52)
    img.paste(m, (CX - 400, 430))
    draw_text(img, (CX, 1270), '중앙역 직선 약 1km', 58, WHITE, spacing=2, bold=1, alpha=ease((t - 0.9) / 0.8))
    draw_text(img, (CX, 1345), '도보 15~20분 · 노적봉공원이 맞닿음', 38, GRAY, bold=0, alpha=ease((t - 1.4) / 0.8))
    return img

def scene_price(t):  # 11~15 (len 4)
    img = Image.new('RGB', (W, H), BG)
    draw_text(img, (CX, 560), '84㎡ 평균 분양가', 54, BRASS, spacing=10, bold=1, alpha=ease(t / 0.7))
    v = 10.86 * ease_out(t / 2.2)
    draw_text(img, (CX - 40, 760), f'{v:0.2f}', 230, WHITE, spacing=4, bold=3)
    draw_text(img, (CX + 355, 860), '억', 80, WHITE, bold=2, alpha=ease((t - 0.4) / 0.6))
    hline(img, 1090, CX - 280, CX + 280, ease_out((t - 1.0) / 1.0), w=2)
    draw_text(img, (CX, 1130), '층별 10.34 ~ 11.05억 · 세대수 가중평균', 38, GRAY, bold=0, alpha=ease((t - 1.8) / 0.8))
    return img

def bar(img, y, label, val, vmax, p, color, label_alpha=1.0, x0=70, maxw=640):
    d = ImageDraw.Draw(img)
    draw_text(img, (x0, y - 70), label, 40, WHITE, anchor='l', bold=0, alpha=label_alpha)
    w = maxw * (val / vmax) * ease_out(p)
    d.rectangle((x0, y, x0 + w, y + 46), fill=color)
    if p > 0.85:
        draw_text(img, (x0 + w + 20, y - 2), f'{val:0.2f}억', 52, WHITE, anchor='l', bold=1, alpha=ease((p - 0.85) / 0.15))

def scene_comps(t):  # 15~20 (len 5)
    img = Image.new('RGB', (W, H), BG)
    draw_text(img, (CX, 420), '비교단지 KB시세', 54, BRASS, spacing=10, bold=1, alpha=ease(t / 0.7))
    draw_text(img, (CX, 495), '84㎡ 일반거래가 · 2026.11.13', 36, GRAY, bold=0, alpha=ease(t / 0.7))
    bar(img, 760, '힐스테이트중앙 · 고잔 · 2018.11', 9.20, 11.0, (t - 0.8) / 1.4, (225, 222, 214), ease((t - 0.6) / 0.6))
    bar(img, 1000, '안산파크푸르지오 · 성포동 · 2018.09', 7.65, 11.0, (t - 1.8) / 1.4, (150, 148, 142), ease((t - 1.6) / 0.6))
    draw_text(img, (CX, 1200), '신축 입주 시점과 점수 차이를 보정해 평균', 38, WHITE, bold=0, alpha=ease((t - 3.2) / 0.8))
    draw_text(img, (CX, 1260), '= 브동산 적정가격', 50, BRASS, spacing=6, bold=1, alpha=ease((t - 3.6) / 0.8))
    disclaimer(img, ease((t - 1.0) / 1.0))
    return img

def scene_gap(t):  # 20~25 (len 5)
    img = Image.new('RGB', (W, H), BG)
    draw_text(img, (CX, 360), '예상 프리미엄', 54, BRASS, spacing=12, bold=1, alpha=ease(t / 0.7))
    bar(img, 640, '브동산 적정가격', 9.83, 11.5, (t - 0.5) / 1.3, (225, 222, 214), ease((t - 0.4) / 0.6))
    bar(img, 860, '실제 분양가 (84㎡ 평균)', 10.86, 11.5, (t - 1.4) / 1.3, BRASS, ease((t - 1.3) / 0.6))
    k = ease((t - 2.8) / 1.0)
    draw_text(img, (CX, 1010 - 10 * (1 - k)), '-1.03억', 190, WHITE, spacing=2, bold=3, alpha=k)
    draw_text(img, (CX, 1235), '분양가가 적정가격보다 약 10% 높음', 44, WHITE, bold=0, alpha=ease((t - 3.4) / 0.8))
    disclaimer(img, 1.0)
    return img

def scene_info(t):  # 25~28 (len 3)
    img = Image.new('RGB', (W, H), BG)
    draw_text(img, (CX, 440), '청약 체크', 54, BRASS, spacing=14, bold=1, alpha=ease(t / 0.6))
    items = [('청약', '11월 23일 ~ 25일'), ('전매제한', '6개월'), ('계약금', '5%')]
    for i, (a, b) in enumerate(items):
        y = 620 + i * 190
        p = ease((t - 0.35 - i * 0.45) / 0.6)
        hline(img, y - 20, SAFE_L + 20, SAFE_R - 20, p, GRAY, 1)
        draw_text(img, (SAFE_L + 40, y + 10), a, 42, GRAY, anchor='l', bold=0, alpha=p)
        draw_text(img, (SAFE_R - 40 - text_w(b, 62), y - 8), b, 62, WHITE, anchor='l', bold=1, alpha=p)
    disclaimer(img, 1.0)
    return img

def scene_end(t):  # 26.4~30 (len 3.6)
    img = Image.new('RGB', (W, H), BG)
    draw_text(img, (CX, 640), '분양가는 숫자일 뿐,', 68, WHITE, spacing=4, bold=2, alpha=ease(t / 0.6))
    draw_text(img, (CX, 745), '판단은 청약자의 몫', 68, WHITE, spacing=4, bold=2, alpha=ease((t - 0.35) / 0.6))
    hline(img, 900, CX - 200, CX + 200, ease_out((t - 0.9) / 0.8))
    draw_text(img, (CX, 950), '더 궁금한 단지는 댓글로 남겨주세요', 44, BRASS, spacing=3, bold=1, alpha=ease((t - 1.3) / 0.7))
    draw_text(img, (CX, 1050), '숫자로 읽는 브동산', 40, GRAY, spacing=12, bold=0, alpha=ease((t - 1.8) / 0.7))
    disclaimer(img, ease(t / 0.6))
    return img


SITE = load('site-layout.jpg')
_a = np.asarray(SITE).astype(np.float32) * 0.82
SITE = Image.fromarray(np.clip(_a, 0, 255).astype(np.uint8))

def scene_tilt(t):  # 원래 길이 3
    img = Image.new('RGB', (W, H), BG)
    bh = 1000
    band = kenburns(AERIAL, W, bh, t / 3.0, 1.32, 1.55, 0.63, 0.78, 0.62, 0.36)
    img.paste(band, (0, 470))
    d = ImageDraw.Draw(img)
    d.line((0, 470, W, 470), fill=BRASS, width=2); d.line((0, 470 + bh, W, 470 + bh), fill=BRASS, width=2)
    draw_text(img, (CX, 360), '지상 49층', 72, WHITE, spacing=10, bold=2, alpha=ease((t - 0.2) / 0.7))
    return img

def scene_layout(t):  # 원래 길이 3
    img = Image.new('RGB', (W, H), BG)
    draw_text(img, (CX, 330), '단지 배치', 52, BRASS, spacing=14, bold=1, alpha=ease(t / 0.6))
    m = kenburns(SITE, 820, 860, t / 3.0, 1.0, 1.55, 0.5, 0.30, 0.52, 0.42)
    img.paste(m, (CX - 410, 420))
    d = ImageDraw.Draw(img)
    d.rectangle((CX - 410, 420, CX + 410, 1280), outline=GRAY, width=1)
    draw_text(img, (CX, 1330), '6개 동 · 중정형 조경 설계', 50, WHITE, spacing=3, bold=1, alpha=ease((t - 0.7) / 0.7))
    return img

# (시작, 끝, 함수, 원래길이)
_T = [(2.6, scene_title, 3.0), (3.6, scene_aerial, 4.0), (3.2, scene_price, 4.0),
      (3.9, scene_comps, 4.4), (4.3, scene_gap, 4.8), (3.4, scene_layout, 3.0), (3.4, scene_map, 4.0),
      (2.6, scene_info, 2.0), (3.0, scene_end, 3.6)]
SCENES = []
_c = 0.0
for _len, _fn, _l0 in _T:
    SCENES.append((_c, _c + _len, _fn, _l0)); _c += _len
assert abs(_c - DUR) < 1e-6, _c
XF = 0.45  # 크로스페이드 길이

# ---- 먼지(보케) 파티클 + 빛줄기
_prng = np.random.default_rng(11)
_P = [(_prng.uniform(0, W), _prng.uniform(0, H), _prng.uniform(10, 38), _prng.uniform(0.2, 0.8), _prng.uniform(6, 22), _prng.uniform(0, 6.28)) for _ in range(26)]

def overlay(img, t):
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for x, y, r, a, v, ph in _P:
        px = (x + 18 * math.sin(t * 0.5 + ph)) % W
        py = (y - v * t) % H
        al = int(255 * 0.05 * a * (0.6 + 0.4 * math.sin(t * 1.3 + ph)))
        d.ellipse((px - r, py - r, px + r, py + r), fill=(255, 250, 240, al))
    lay = lay.filter(ImageFilter.GaussianBlur(6))
    base = img.convert('RGBA'); base.alpha_composite(lay)
    return base.convert('RGB')

def push(img, lt, L):
    """장면 전체에 아주 느린 카메라 푸시(1.0→1.035)."""
    z = 1.0 + 0.035 * (lt / max(L, 0.1))
    cw, ch = W / z, H / z
    l, tp = (W - cw) / 2, (H - ch) / 2
    return img.crop((l, tp, l + cw, tp + ch)).resize((W, H), Image.BICUBIC)

def render_scene(i, t):
    s, e, fn, l0 = SCENES[i]
    lt = t - s
    img = fn(lt * l0 / (e - s))
    if fn not in (scene_aerial, scene_tilt):
        img = push(img, lt, e - s)
    return img

def frame(fi):
    t = fi / FPS
    idx = next((i for i, sc in enumerate(SCENES) if sc[0] <= t < sc[1]), len(SCENES) - 1)
    img = render_scene(idx, t)
    s, e = SCENES[idx][0], SCENES[idx][1]
    if idx + 1 < len(SCENES) and e - t < XF:   # 다음 장면으로 크로스페이드
        nxt = render_scene(idx + 1, t)
        img = Image.blend(img, nxt, ease(1 - (e - t) / XF))
    if idx > 0 and t - s < 0:  # (미사용)
        pass
    img = overlay(img, t)
    fade = 1.0
    if t < 0.8:
        fade = ease(t / 0.8)
    if DUR - t < 0.9:
        fade = min(fade, ease((DUR - t) / 0.9))
    if fade < 1.0:
        a = np.asarray(img).astype(np.float32) * fade
        img = Image.fromarray(a.astype(np.uint8))
    return finish(img, fi)

# ---------------------------------------------------------------- 오디오 (직접 합성한 시네마틱 앰비언트)
RISE = [2.6, 6.2, 9.4, 13.3, 17.6, 21.0, 24.4, 27.0]
BOOM = [(15.8, 0.8), (27.0, 0.5)]

def make_audio(path):
    """차분하고 고급스러운 시네마틱 음악: 피아노 아르페지오 + 스트링 패드 + 서브 베이스 + 홀 리버브."""
    sr = 44100
    n = int(sr * DUR)
    rng = np.random.default_rng(5)
    mid = lambda m: 440.0 * 2 ** ((m - 69) / 12)
    beat = 60.0 / 64            # 64bpm
    bar_len = beat * 4          # 3.75s
    # Am - F - C - G - Am - F - C/G - Am
    chords = [(45, [57, 60, 64, 67]), (41, [53, 57, 60, 65]), (48, [55, 60, 64, 67]), (43, [55, 59, 62, 67]),
              (45, [57, 60, 64, 69]), (41, [53, 57, 60, 65]), (48, [55, 60, 64, 72]), (45, [57, 60, 64, 69])]
    piano = np.zeros(n); pad = np.zeros(n); bass = np.zeros(n)
    def add(buf, f, t0, dur, amp, harm, dec, att=0.005):
        i0 = int(t0 * sr)
        if i0 >= n: return
        L = min(int(dur * sr), n - i0)
        k = np.arange(L) / sr
        env = np.minimum(1.0, k / att) * np.exp(-k * dec)
        w = np.zeros(L)
        for h, g in harm:
            w += g * np.sin(2 * np.pi * f * h * k * (1 + 0.0004 * h * h))
        buf[i0:i0 + L] += amp * env * w
    PH = [(1, 1.0), (2, 0.45), (3, 0.22), (4, 0.10), (5, 0.05)]
    for ci, (root, tones) in enumerate(chords):
        t0 = ci * bar_len
        grow = 0.55 + 0.45 * min(1.0, t0 / 22)
        # 피아노: 8분음표 아르페지오 (위로 올라갔다 내려옴)
        seq = [tones[0], tones[1], tones[2], tones[3], tones[2], tones[1], tones[2], tones[3]]
        for k_, m in enumerate(seq):
            vel = (0.75 if k_ % 4 == 0 else 0.5) * grow
            add(piano, mid(m + 12), t0 + k_ * beat / 2, 2.2, 0.20 * vel, PH, 2.6)
        # 피아노 저음 한 음 + 서브
        add(bass, mid(root), t0, bar_len + 0.4, 0.35, [(1, 1.0), (2, 0.25)], 0.9, 0.04)
        add(bass, mid(root - 12), t0, bar_len + 0.6, 0.30, [(1, 1.0)], 0.6, 0.12)
        # 스트링 패드: 느린 어택, 살짝 디튠
        for m in tones:
            for dt in (-0.0035, 0.0, 0.0035):
                add(pad, mid(m) * (1 + dt), max(0.0, t0 - 0.4), bar_len + 1.2, 0.055 * grow, [(1, 1.0), (2, 0.35), (3, 0.18)], 0.0, 1.4)
    # 장면 전환 라이저 (아주 부드러운 노이즈) + 공개 순간 저음 임팩트
    noise = rng.normal(0, 1, n)
    rise = np.zeros(n)
    for c in RISE:
        i0, i1 = int((c - 1.0) * sr), int((c + 0.1) * sr)
        seg = noise[i0:i1]
        env = np.sin(np.linspace(0, np.pi / 2, len(seg))) ** 2
        rise[i0:i1] += seg * env * 0.012
    boom = np.zeros(n)
    for c, g in BOOM:
        i = int(c * sr); k = np.arange(int(2.6 * sr)) / sr
        b = np.sin(2 * np.pi * (46 - 12 * (1 - np.exp(-k * 2.5))) * k) * np.exp(-k * 1.4)
        L = min(len(b), n - i); boom[i:i + L] += g * b[:L]
    dry = piano + pad + bass * 0.9 + rise + boom * 0.5
    # 홀 리버브 (FFT 컨볼루션, 합성 임펄스)
    irn = int(2.8 * sr)
    kk = np.arange(irn) / sr
    ir = rng.normal(0, 1, irn) * np.exp(-kk / 0.95)
    ir[:int(0.02 * sr)] *= np.linspace(0, 1, int(0.02 * sr))
    ir /= np.abs(ir).sum() ** 0.5 * 18
    m = 1 << int(np.ceil(np.log2(n + irn)))
    wet = np.fft.irfft(np.fft.rfft(dry, m) * np.fft.rfft(ir, m), m)[:n]
    # 스테레오: 좌우 다른 리버브 꼬리 + 건음 약간
    irn2 = int(2.6 * sr); ir2 = rng.normal(0, 1, irn2) * np.exp(-np.arange(irn2) / sr / 0.9); ir2 /= np.abs(ir2).sum() ** 0.5 * 18
    wet2 = np.fft.irfft(np.fft.rfft(dry, m) * np.fft.rfft(ir2, m), m)[:n]
    L_ = 0.75 * dry + 1.6 * wet
    R_ = 0.75 * np.roll(dry, int(sr * 0.011)) + 1.6 * wet2
    st = np.stack([L_, R_], 1)
    env = np.ones(n)
    env[:int(sr * 1.5)] = np.linspace(0, 1, int(sr * 1.5)) ** 2
    env[-int(sr * 2.2):] = np.linspace(1, 0, int(sr * 2.2)) ** 1.6
    st *= env[:, None]
    st = np.tanh(st * 1.0)
    st /= max(1e-6, np.abs(st).max()) / 0.8
    pcm = (st * 32767).astype(np.int16)
    with wave.open(path, 'wb') as wf:
        wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(sr); wf.writeframes(pcm.tobytes())

def main():
    os.makedirs(OUT, exist_ok=True)
    only = [int(x) for x in sys.argv[1:]]
    if only:  # 시험 정지 화면
        for s in only:
            frame(int(s * FPS)).save(OUT + f'still_{s}.png')
        return
    make_audio(OUT + 'audio_music.wav')
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
           '-i', '-', '-i', OUT + 'audio_music.wav', '-c:v', 'libx264', '-preset', 'medium', '-crf', '21', '-maxrate', '10M', '-bufsize', '20M', '-pix_fmt', 'yuv420p',
           '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', OUT + 'armusee-xi-ansan-cinematic-30s-v5.mp4']
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for fi in range(int(DUR * FPS)):
        p.stdin.write(np.asarray(frame(fi)).tobytes())
    p.stdin.close(); p.wait()
    print('done')

if __name__ == '__main__':
    main()
