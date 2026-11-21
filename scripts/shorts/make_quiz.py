#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""브동산 1안 '가격 맞히기 퀴즈' 쇼츠 — 부천대장 하우스토리 디센트 (나레이션 + 시네마틱)
usage: python3 make_quiz.py render            # 전체 렌더 → OUT/bucheon-daejang-quiz.mp4
       python3 make_quiz.py stills 3.1 9.5 …  # 지정 시각 정지 화면 PNG
"""
import os, sys, wave, subprocess, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
IMG = os.environ.get('QUIZ_IMG', os.path.join(REPO, 'posts', 'images', 'bucheon-daejang-haustory-decent') + '/')
TTS = os.environ.get('QUIZ_TTS', '/tmp/quiz-tts/')        # tts_edge.py로 만든 s1~s8.wav (44.1kHz 모노, 앞뒤 무음 제거)
FONTS = os.environ.get('QUIZ_FONTS', '/tmp/nanum/')       # NanumGothic-Regular/Bold/ExtraBold.ttf
OUT = os.environ.get('QUIZ_OUT', '/tmp/shorts-out/')
sys.path.insert(0, HERE)
import audio_orig, sfx

W, H, FPS = 1080, 1920, 30
SAFE_L, SAFE_R = 54, 885
CX = (SAFE_L + SAFE_R) // 2            # 469
BG = (8, 8, 9); INK = (244, 241, 234); SOFT = (185, 181, 172); FAINT = (150, 148, 142)
HAIR = (42, 42, 45); TRACK = (34, 34, 37); DIM = (90, 88, 84)
BRASS = (200, 164, 92); BRASS_TINT = (42, 36, 22)
MINUS = (240, 138, 102); MINUS_TINT = (43, 24, 19)

_f = {}
def F(px, w='B'):
    k = (px, w)
    if k not in _f:
        name = {'R': 'Regular', 'B': 'Bold', 'X': 'ExtraBold'}[w]
        _f[k] = ImageFont.truetype(FONTS + f'NanumGothic-{name}.ttf', px)
    return _f[k]

def ease(x):
    x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def eo(x):
    x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3

def tw(s, px, w='B'): return F(px, w).getlength(s)

def text(img, xy, s, px, color=INK, w='B', anchor='c', alpha=1.0, dy=0.0):
    if alpha <= 0.01: return
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

def load(n): return Image.open(IMG + n).convert('RGB')

def darken(im, k=0.8):
    a = np.asarray(im).astype(np.float32) * k
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))

def kenburns(src, bw, bh, t, z0, z1, cx0, cy0, cx1, cy1):
    k = ease(t); z = z0 + (z1 - z0) * k
    cx = (cx0 + (cx1 - cx0) * k) * src.width; cy = (cy0 + (cy1 - cy0) * k) * src.height
    base = max(bw / src.width, bh / src.height)
    sw, sh = bw / (base * z), bh / (base * z)
    l = min(max(cx - sw / 2, 0), src.width - sw); tp = min(max(cy - sh / 2, 0), src.height - sh)
    return src.crop((l, tp, l + sw, tp + sh)).resize((bw, bh), Image.BICUBIC)

COVER = darken(load('cover.jpg'), 0.92)
SITE = darken(load('site-plan.jpg'), 0.85)
LOC = darken(load('location.jpg'), 0.55)
PLAN = load('plan-84a.jpg')

# 비네트·그레인 (시네마틱 질감)
yy, xx = np.mgrid[0:H, 0:W]
_r = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2)
VIGN = np.clip(1.0 - 0.5 * np.clip(_r - 0.45, 0, 1) ** 1.4, 0.4, 1.0).astype(np.float32)[..., None]
_rng = np.random.default_rng(7)
GRAIN = [(_rng.normal(0, 2.4, (H, W, 1))).astype(np.float32) for _ in range(6)]

# ------------------------------------------------------------------ 타임라인 (나레이션 길이가 기준)
def wav_len(p):
    with wave.open(p) as w: return w.getnframes() / w.getframerate()
NAR = {k: wav_len(TTS + f'{k}.wav') for k in ['s1', 's2', 's3', 's4', 's5', 's6', 's7', 's8']}
LEAD = {'s1': 0.25, 's4': 0.6}        # 정답 공개 직전 멈춤
TAIL = {'s3': 3.0, 's8': 0.7}         # s3: 3초 카운트다운, s8: 마지막 질문 여운
SC = []; t0 = 0.0
for k in ['s1', 's2', 's3', 's4', 's5', 's6', 's7', 's8']:
    lead = LEAD.get(k, 0.18); dur = lead + NAR[k] + TAIL.get(k, 0.26)
    SC.append((k, t0, dur, lead)); t0 += dur
DUR = t0

# ------------------------------------------------------------------ 공통 요소
SRC1 = '출처: 입주자모집공고(2026.11.12) · KB시세(2026.11.13)'
SRC2 = '브동산 모형 추정치 · 84A 가중평균 · 투자 권유 아님'

def chrome(img):
    # 상단 워드마크(장식) + 하단 고지(안전영역 안)
    x = CX - (tw('브', 40, 'X') + tw('동산', 40, 'R')) / 2
    text(img, (x, 210), '브', 40, INK, 'X', anchor='l')
    text(img, (x + tw('브', 40, 'X'), 210), '동산', 40, SOFT, 'R', anchor='l')
    text(img, (CX, 1352), SRC1, 27, FAINT, 'R')
    text(img, (CX, 1390), SRC2, 27, FAINT, 'R')

def band(img, src, t, y0, bh, kb, line=True, a=1.0):
    m = kenburns(src, W, bh, t, *kb)
    if a < 1:
        m = Image.blend(Image.new('RGB', m.size, BG), m, a)
    img.paste(m, (0, y0))
    if line:
        d = ImageDraw.Draw(img)
        d.line((0, y0, W, y0), fill=HAIR, width=2); d.line((0, y0 + bh, W, y0 + bh), fill=HAIR, width=2)

def badge(img, cx, y, s, px, fg, bg, alpha=1.0, scale=1.0):
    px = int(px * scale)
    w = tw(s, px, 'X'); pad = px * 0.7; h = px * 1.75
    rect(img, (cx - w / 2 - pad, y, cx + w / 2 + pad, y + h), fill=bg, alpha=alpha, radius=int(h / 2))
    text(img, (cx, y + (h - px) / 2 - px * 0.08), s, px, fg, 'X', alpha=alpha)

def hbar(img, y, label, val, vmax, p, color, valcol=INK, alpha=1.0, lw='R', sub=None):
    x0, x1 = SAFE_L + 10, SAFE_R - 150
    text(img, (x0, y), label, 38, SOFT if color != BRASS else INK, lw, anchor='l', alpha=alpha)
    if sub: text(img, (x0 + tw(label, 38, lw) + 14, y + 8), sub, 28, FAINT, 'R', anchor='l', alpha=alpha)
    by = y + 58
    rect(img, (x0, by, x1, by + 40), fill=TRACK, alpha=alpha)
    xe = x0 + (x1 - x0) * (val / vmax) * eo(p)
    if xe > x0 + 2: rect(img, (x0, by, xe, by + 40), fill=color, alpha=alpha)
    text(img, (xe + 16, by - 2), f'{val * eo(p):.2f}억' if p < 1 else f'{val:.2f}억', 40, valcol, 'X', anchor='l', alpha=alpha * ease(p * 3))

# ------------------------------------------------------------------ 장면
def s1(t, d, lead):  # 훅
    img = Image.new('RGBA', (W, H), BG + (255,))
    band(img, COVER, t / d, 300, 700, (1.05, 1.22, 0.42, 0.55, 0.47, 0.50))
    text(img, (CX, 1050), '3기 신도시 84m²', 92, INK, 'X', alpha=ease((t - 0.15) / 0.45), dy=18 * (1 - eo((t - 0.15) / 0.6)))
    text(img, (CX, 1165), '얼마일까?', 118, BRASS, 'X', alpha=ease((t - 0.7) / 0.45), dy=18 * (1 - eo((t - 0.7) / 0.6)))
    return img

HINTS = [('1', '부천대장 공공분양 · 548세대', None),
         ('2', '대장역(가칭·예정) 바로 옆', None),
         ('3', '근처 민간 분양가', '11.4~16.4억')]
def s2(t, d, lead):
    img = Image.new('RGBA', (W, H), BG + (255,))
    band(img, SITE, t / d, 330, 520, (1.45, 1.65, 0.79, 0.5, 0.80, 0.42))
    text(img, (CX, 885), 'HINT', 34, BRASS, 'X', alpha=ease(t / 0.3))
    times = [lead + 0.05, lead + 1.25, lead + 2.35]
    for i, (n, s, big) in enumerate(HINTS):
        a = ease((t - times[i]) / 0.3); dx = 40 * (1 - eo((t - times[i]) / 0.4))
        y = 950 + i * 128
        rect(img, (SAFE_L + 10 + dx, y, SAFE_R - 10 + dx, y + 108), fill=(18, 18, 20), outline=HAIR, width=2, alpha=a)
        text(img, (SAFE_L + 44 + dx, y + 30), n, 46, FAINT, 'X', anchor='l', alpha=a)
        if big:
            text(img, (SAFE_L + 100 + dx, y + 34), s, 40, INK, 'B', anchor='l', alpha=a)
            text(img, (SAFE_R - 34 + dx, y + 28), big, 50, INK, 'X', anchor='r', alpha=a)
        else:
            text(img, (SAFE_L + 100 + dx, y + 32), s, 44, INK, 'B', anchor='l', alpha=a)
    return img

OPTS = [('A', '6.9억'), ('B', '8.5억'), ('C', '11.4억')]
def options(img, t_in, t, reveal=None):
    for i, (k, v) in enumerate(OPTS):
        a = ease((t - t_in - i * 0.18) / 0.3)
        y = 640 + i * 175
        on = reveal is not None and k == 'B'
        fade = 1.0 if reveal is None else (1.0 if on else 1 - 0.65 * ease(reveal / 0.4))
        border = BRASS if on else DIM
        rect(img, (SAFE_L + 40, y, SAFE_R - 40, y + 140), fill=(BRASS_TINT if on and ease(reveal / 0.3) > 0.5 else (16, 16, 18)),
             outline=border, width=4 if on else 2, alpha=a * fade)
        text(img, (SAFE_L + 100, y + 34), k, 72, BRASS if on else SOFT, 'X', anchor='l', alpha=a * fade)
        text(img, (SAFE_R - 100, y + 30), v, 80, BRASS if on else INK, 'X', anchor='r', alpha=a * fade)

def s3(t, d, lead):
    img = Image.new('RGBA', (W, H), BG + (255,))
    text(img, (CX, 440), '84m² 평균 분양가는?', 70, INK, 'X', alpha=ease(t / 0.3))
    text(img, (CX, 540), '부천대장 하우스토리 디센트 · 84A', 34, FAINT, 'R', alpha=ease((t - 0.2) / 0.3))
    options(img, 0.15, t)
    cd0 = d - 3.0  # 카운트다운 시작
    if t >= cd0:
        k = t - cd0; n = 3 - int(k); fr = k - int(k)
        n = max(1, n)
        cy = 1215; r = 70
        lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); dd = ImageDraw.Draw(lay)
        dd.ellipse((CX - r, cy - r, CX + r, cy + r), outline=HAIR + (255,), width=6)
        dd.arc((CX - r, cy - r, CX + r, cy + r), -90, -90 + 360 * (1 - k / 3.0), fill=BRASS + (255,), width=6)
        img.alpha_composite(lay)
        sc = 1.0 + 0.25 * (1 - eo(fr / 0.25))
        text(img, (CX, cy - 48 * sc), str(n), int(84 * sc), INK, 'X')
    return img

def s4(t, d, lead):
    img = Image.new('RGBA', (W, H), BG + (255,))
    text(img, (CX, 440), '84m² 평균 분양가는?', 70, INK, 'X')
    rv = t - lead + 0.15
    options(img, -5, t, reveal=max(0, rv))
    if rv > 0:
        a = ease(rv / 0.25); sc = 1 + 0.6 * (1 - eo(rv / 0.35))
        badge(img, CX, 1165, '정답 B', 62, BG, BRASS, alpha=a, scale=sc)
        text(img, (CX, 1290), '84A 8억 281만~8억 5,406만 · 평균 8.47억', 34, SOFT, 'R', alpha=ease((rv - 0.6) / 0.4))
    return img

def s5(t, d, lead):  # 첫 반전: 민간보다 3억 낮다?
    img = Image.new('RGBA', (W, H), BG + (255,))
    text(img, (CX, 420), '근처 민간 분양가와 비교하면', 44, SOFT, 'B', alpha=ease(t / 0.3))
    text(img, (CX, 500), '84m² 최초 분양가', 30, FAINT, 'R', alpha=ease(t / 0.3))
    hbar(img, 640, '상동역 롯데캐슬 시그니처', 16.38, 17.5, (t - 0.1) / 0.7, DIM, sub='2026.8')
    hbar(img, 790, 'e편한세상 부천 어반스퀘어', 11.39, 17.5, (t - 0.35) / 0.7, DIM, sub='2026.5')
    hbar(img, 940, '부천대장 하우스토리 디센트', 8.47, 17.5, (t - 0.6) / 0.7, BRASS, lw='X')
    a = ease((t - lead - 0.2) / 0.35)
    text(img, (CX, 1140), '민간보다 3억 가까이 낮다?', 64, INK, 'X', alpha=a, dy=14 * (1 - eo((t - lead - 0.2) / 0.5)))
    text(img, (CX, 1235), '무조건 이득일까?', 48, SOFT, 'B', alpha=ease((t - lead - 1.4) / 0.35))
    return img

def s6(t, d, lead):  # 비교단지 → 적정가
    img = Image.new('RGBA', (W, H), BG + (255,))
    band(img, LOC, t / d, 330, 300, (1.3, 1.5, 0.5, 0.25, 0.5, 0.32), a=0.85)
    text(img, (CX, 670), '이미 입주한 주변 단지 · 84m² KB시세', 40, SOFT, 'B', alpha=ease(t / 0.3))
    cards = [('부천 아이파크', '2017년 입주', '6.85억'), ('계양효성해링턴플레이스', '2021년 입주', '6.05억')]
    for i, (n, s, v) in enumerate(cards):
        a = ease((t - 0.25 - i * 0.5) / 0.35); y = 750 + i * 150
        rect(img, (SAFE_L + 10, y, SAFE_R - 10, y + 128), fill=(16, 16, 18), outline=HAIR, width=2, alpha=a)
        text(img, (SAFE_L + 44, y + 22), n, 42, INK, 'B', anchor='l', alpha=a)
        text(img, (SAFE_L + 44, y + 78), s, 28, FAINT, 'R', anchor='l', alpha=a)
        text(img, (SAFE_R - 40, y + 30), v, 60, INK, 'X', anchor='r', alpha=a)
    tf = lead + NAR['s6'] * 0.52
    a = ease((t - tf + 0.5) / 0.4)
    text(img, (CX, 1068), '입지·상품·연식 보정 (역·학교 예정 반영)', 30, FAINT, 'R', alpha=a)
    a2 = ease((t - tf) / 0.35)
    rect(img, (SAFE_L + 60, 1118, SAFE_R - 60, 1300), fill=BRASS_TINT, outline=BRASS, width=3, alpha=a2)
    text(img, (CX, 1136), '브동산 적정가', 40, (217, 188, 126), 'B', alpha=a2)
    sc = 1 + 0.25 * (1 - eo((t - tf) / 0.35))
    text(img, (CX, 1192 - 10 * (sc - 1)), '7.91억', int(88 * sc), BRASS, 'X', alpha=a2)
    return img

def s7(t, d, lead):  # 판정
    img = Image.new('RGBA', (W, H), BG + (255,))
    text(img, (CX, 470), '84m² 기준', 40, SOFT, 'B', alpha=ease(t / 0.3))
    hbar(img, 600, '브동산 적정가', 7.91, 9.6, (t - 0.1) / 0.6, BRASS, lw='X')
    hbar(img, 760, '평균 분양가', 8.47, 9.6, (t - 0.35) / 0.6, INK)
    rv = lead + 0.35
    if t > rv:
        a = ease((t - rv) / 0.25); sc = 1 + 0.5 * (1 - eo((t - rv) / 0.35))
        badge(img, CX, 975, '고평가 -5,640만', 58, MINUS, MINUS_TINT, alpha=a, scale=sc)
        text(img, (CX, 1115), '분양가가 적정가보다 약 7% 높다', 40, INK, 'B', alpha=ease((t - rv - 0.3) / 0.3))
        text(img, (CX, 1175), '브동산 모형 계산 기준', 30, FAINT, 'R', alpha=ease((t - rv - 0.3) / 0.3))
    return img

def s8(t, d, lead):  # 조건 + 일정 + 루프
    img = Image.new('RGBA', (W, H), BG + (255,))
    k = t / d
    # 마지막 1.2초는 첫 장면(커버)으로 되돌아가 루프를 잇는다
    loop = ease((t - (d - 1.2)) / 0.9)
    a_info = 1 - loop
    t1 = lead; t2 = lead + NAR['s8'] * 0.30; t3 = lead + NAR['s8'] * 0.62
    text(img, (CX, 430), '대장역(가칭)·학교는 아직 예정', 52, INK, 'X', alpha=ease((t - t1) / 0.3) * a_info)
    text(img, (CX, 505), '개통·개교 전 기준이면', 36, SOFT, 'R', alpha=ease((t - t2) / 0.3) * a_info)
    a = ease((t - t2) / 0.3) * a_info
    text(img, (CX, 560), '적정가 6.01억', 92, INK, 'X', alpha=a)
    text(img, (CX, 680), '예상 프리미엄 -2억 4,550만 (브동산 계산)', 32, FAINT, 'R', alpha=a)
    a3 = ease((t - t3) / 0.3) * a_info
    rect(img, (SAFE_L + 60, 790, SAFE_R - 60, 1010), fill=(16, 16, 18), outline=HAIR, width=2, alpha=a3)
    text(img, (CX, 818), '청약 일정', 34, FAINT, 'B', alpha=a3)
    text(img, (CX, 868), '특별공급 11.23(월)', 46, SOFT, 'B', alpha=a3)
    text(img, (CX, 935), '1순위 11.24(화)', 56, INK, 'X', alpha=a3)
    tq = lead + NAR['s8'] - 1.25
    aq = ease((t - tq) / 0.3)
    if loop > 0:
        band(img, COVER, 0.0, 300, 700, (1.05, 1.22, 0.42, 0.55, 0.47, 0.50))
        cover = Image.new('RGBA', (W, H), BG + (int(255 * (1 - loop)),))
        img.alpha_composite(cover)
    text(img, (CX, 1120), '넣으실 건가요?', 96, BRASS, 'X', alpha=aq, dy=16 * (1 - eo((t - tq) / 0.5)))
    return img

FN = {'s1': s1, 's2': s2, 's3': s3, 's4': s4, 's5': s5, 's6': s6, 's7': s7, 's8': s8}

def frame(T):
    for i, (k, st, d, lead) in enumerate(SC):
        if T < st + d or i == len(SC) - 1:
            t = T - st
            img = FN[k](t, d, lead)
            chrome(img)
            if i > 0 and t < 0.22:  # 장면 사이 짧은 디졸브(검정 경유)
                img.alpha_composite(Image.new('RGBA', (W, H), BG + (int(255 * (1 - t / 0.22)),)))
            return img
    raise ValueError

def finish(img, fi):
    a = np.asarray(img.convert('RGB')).astype(np.float32)
    a = a * VIGN + GRAIN[fi % 6]
    return np.clip(a, 0, 255).astype(np.uint8)

# ------------------------------------------------------------------ 오디오
SR = 44100
def read_wav(p):
    with wave.open(p) as w:
        ch = w.getnchannels(); sr = w.getframerate()
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    x = x.reshape(-1, ch).mean(1)
    assert sr == SR, sr
    return x

def build_audio(path):
    n = int(DUR * SR) + SR
    starts = [st for _, st, _, _ in SC]
    st = dict((k, (s, d, l)) for k, s, d, l in SC)
    reveal = st['s4'][0] + st['s4'][2]
    verdict = st['s7'][0] + st['s7'][2] + 0.35
    tmp = OUT + '_music.wav'
    audio_orig.make_audio(tmp, DUR + 1.0, RISE=tuple(starts[1:]), BOOM=((reveal, 0.7), (verdict, 0.6)))
    with wave.open(tmp) as w:
        m = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32).reshape(-1, 2) / 32768
    mus = np.zeros((n, 2)); L = min(n, len(m)); mus[:L] = m[:L]
    nar = np.zeros(n)
    for k, (s, d, l) in st.items():
        x = read_wav(TTS + f'{k}.wav'); i = int((s + l) * SR)
        nar[i:i + len(x)] += x[:max(0, n - i)]
    nar /= max(1e-6, np.abs(nar).max()); nar *= 0.85
    # 나레이션이 나올 때 음악을 더 낮춘다(덕킹)
    env = np.convolve(np.abs(nar), np.ones(int(0.25 * SR)) / int(0.25 * SR), 'same')
    duck = 1.0 - 0.55 * np.clip(env / 0.08, 0, 1)
    out = mus * 0.16 * duck[:, None] + nar[:, None]
    lib = {'whoosh': sfx.whoosh(), 'lowhit': sfx.lowhit(), 'tick': sfx.tick(), 'shimmer': sfx.shimmer(), 'ping': sfx.ping()}
    ev = [(s - 0.35, 'whoosh', 0.18) for s in starts[1:]]
    cd0 = st['s3'][0] + st['s3'][1] - 3.0
    ev += [(cd0 + i, 'tick', 0.32) for i in range(3)]
    ev += [(reveal, 'ping', 0.32), (reveal, 'lowhit', 0.3)]
    s5 = st['s5'][0] + st['s5'][2] + 0.2; ev += [(s5, 'lowhit', 0.28)]
    ev += [(verdict, 'lowhit', 0.38)]
    ev += [(DUR - 1.6, 'shimmer', 0.22)]
    for t0, name, g in ev:
        i = int(max(0, t0) * SR); x = lib[name] * g; Lx = min(len(x), n - i)
        if Lx > 0: out[i:i + Lx] += x[:Lx, None]
    out = out[:int(DUR * SR)]
    fade = int(0.4 * SR); out[-fade:] *= np.linspace(1, 0, fade)[:, None]
    out = np.tanh(out * 1.05); out /= max(1e-6, np.abs(out).max()) / 0.89
    with wave.open(path, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out * 32767).astype(np.int16).tobytes())

# ------------------------------------------------------------------ 실행
def render(name='bucheon-daejang-quiz'):
    os.makedirs(OUT, exist_ok=True)
    vtmp = OUT + f'_{name}_v.tmp.mp4'
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
           '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', vtmp]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    nf = int(round(DUR * FPS))
    for fi in range(nf):
        p.stdin.write(finish(frame(fi / FPS), fi).tobytes())
        if fi % 150 == 0: print('frame', fi, '/', nf, flush=True)
    p.stdin.close(); assert p.wait() == 0
    build_audio(OUT + f'_{name}.wav')
    final_tmp = OUT + f'_{name}.tmp.mp4'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', vtmp, '-i', OUT + f'_{name}.wav', '-map', '0:v', '-map', '1:a',
                    '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', final_tmp], check=True)
    os.replace(final_tmp, OUT + f'{name}.mp4')
    print('done', OUT + f'{name}.mp4', round(DUR, 2))

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    if sys.argv[1] == 'stills':
        for s in sys.argv[2:]:
            T = float(s); Image.fromarray(finish(frame(T), 0)).save(OUT + f'still_{T:05.2f}.png')
        print([(k, round(st, 2), round(d, 2)) for k, st, d, _ in SC], round(DUR, 2))
    else:
        render()
