#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""수도권 미분양 선착순 TOP30 — 유튜브 가로(1920x1080) 시네마틱 풀영상 생성기.

쇼츠(scripts/shorts)와 같은 톤: 검정 바탕 + 황동 #C8A45C + 크림 흰색 글씨, 비네트·그레인·떠다니는 빛 입자,
저음 드론·패드·펄스 음악(나레이션 없음), 장면 전환 whoosh / 결과 공개 lowhit+ping / 마무리 shimmer / 카운트업 tick.

구성: 오프닝 → 훅 → 한눈에(분포) → 계산 방법 → 30위→1위 카운트다운(구간 구분 카드) → TOP3 → 전체 순위판 →
      브동산 한줄평 3묶음 → 리스크 → 마무리.  단지 데이터는 scripts/firstcome(엔진 result2.json·texts2.py)에서 읽는다.

사용:
  cd scripts/firstcome && python3 firstcome_engine.py          # result2.json 생성
  LONG_OUT=/tmp/long-out/ python3 scripts/longform/make_firstcome_long.py            # 렌더(병렬) + 음악 + 효과음
  LONG_OUT=/tmp/long-out/ python3 scripts/longform/make_firstcome_long.py 5 40 95   # 정지 화면만(초 단위)
출력: <slug>-youtube.mp4, <slug>-youtube-thumbnail.png(1280x720), <slug>-youtube.txt(제목·설명·챕터)
"""
import math, os, sys, subprocess, json, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'scripts', 'shorts'))
sys.path.insert(0, os.path.join(ROOT, 'scripts', 'firstcome'))
import sfx, audio_orig
from texts2 import T

RD = os.environ.get('RANK_DATE', '2026-11-16'); _y, _m, _d = [int(x) for x in RD.split('-')]
SLUG = os.environ.get('RANK_SLUG', 'sudogwon-firstcome-top30-202611' if RD == '2026-11-16' else f"sudogwon-firstcome-top30-{_y}{_m:02d}{_d:02d}")
D_DOT = f"{_y}.{_m:02d}.{_d:02d}"
IMG = os.path.join(ROOT, 'posts', 'images', SLUG) + '/'
OUT = os.environ.get('LONG_OUT', '/tmp/long-out/'); os.makedirs(OUT, exist_ok=True)
D = json.load(open(os.path.join(ROOT, 'scripts', 'firstcome', 'result2.json')))

W, H, FPS = int(os.environ.get('FC_W', 1920)), int(os.environ.get('FC_H', 1080)), 30  # 세로 버전은 FC_W/FC_H로 바꿔 import
FONT = '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'
BRASS = (200, 164, 92); WHITE = (244, 241, 234); GRAY = (150, 148, 142); DIM = (90, 88, 84); BG = (8, 8, 9)
CX = W // 2
DISC = f'브동산 모형 추정치 · 확정 수익 아님 · {D_DOT} 기준'

# ------------------------------------------------------------------ 기본 도구
_fonts = {}
def F(px):
    if px not in _fonts: _fonts[px] = ImageFont.truetype(FONT, px)
    return _fonts[px]
def ease(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def ease_out(x): x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3
def tw(s, px, sp=0): f = F(px); return sum(f.getlength(c) for c in s) + sp * max(0, len(s) - 1)

def text(img, xy, s, px, color=WHITE, anchor='c', sp=0, bold=1, a=1.0):
    """작은 레이어에만 그려 붙인다(1080p 속도). anchor: 'c' 가운데 / 'l' 왼쪽 / 'r' 오른쪽."""
    if a <= 0.01 or not s: return
    w = int(tw(s, px, sp)) + 2 * bold + 4; h = int(px * 1.35) + 2 * bold
    lay = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); f = F(px)
    al = int(255 * min(1.0, a)); x = bold + 1
    for c in s:
        d.text((x, bold), c, font=f, fill=color + (al,), stroke_width=bold, stroke_fill=color + (al,)); x += f.getlength(c) + sp
    X = xy[0] - w / 2 if anchor == 'c' else (xy[0] - w if anchor == 'r' else xy[0])
    img.paste(lay, (int(X), int(xy[1])), lay)

def wrap(s, px, maxw):
    """한글 단어 단위 줄바꿈."""
    out, cur = [], ''
    for wd in s.split(' '):
        t = (cur + ' ' + wd).strip()
        if tw(t, px) <= maxw or not cur: cur = t
        else: out.append(cur); cur = wd
    if cur: out.append(cur)
    return out

def hline(img, y, x0, x1, p, color=BRASS, w=2):
    if p <= 0: return
    ImageDraw.Draw(img).line((x0, y, x0 + (x1 - x0) * ease(p), y), fill=color, width=w)

def grade(im, bright=0.62, tint=(0.88, 0.95, 1.08)):
    a = np.asarray(im).astype(np.float32) / 255.0; g = a.mean(axis=2, keepdims=True)
    a = a * 0.45 + g * 0.55; a = a * np.array(tint, dtype=np.float32) * bright
    a = np.clip((a - 0.5) * 1.18 + 0.5 + (bright - 0.5) * 0.15, 0, 1)
    return Image.fromarray((a * 255).astype(np.uint8))
def darken(im, k=0.85): return Image.fromarray(np.clip(np.asarray(im).astype(np.float32) * k, 0, 255).astype(np.uint8))

def kenburns(src, bw, bh, t, z0, z1, cx0=0.5, cy0=0.5, cx1=0.5, cy1=0.5):
    k = ease(t); z = z0 + (z1 - z0) * k
    cx = (cx0 + (cx1 - cx0) * k) * src.width; cy = (cy0 + (cy1 - cy0) * k) * src.height
    base = max(bw / src.width, bh / src.height); sw, sh = bw / (base * z), bh / (base * z)
    l = min(max(cx - sw / 2, 0), src.width - sw); tp = min(max(cy - sh / 2, 0), src.height - sh)
    return src.crop((l, tp, l + sw, tp + sh)).resize((bw, bh), Image.BICUBIC)

def fitbox(src, bw, bh, t, z0=1.0, z1=1.06):
    """지도처럼 잘리면 안 되는 이미지: 상자 안에 전체가 들어오게(검정 여백) + 아주 느린 줌."""
    z = z0 + (z1 - z0) * ease(t); s = min(bw / src.width, bh / src.height) * z
    im = src.resize((max(1, int(src.width * s)), max(1, int(src.height * s))), Image.BICUBIC)
    box = Image.new('RGB', (bw, bh), BG)
    box.paste(im, ((bw - im.width) // 2, (bh - im.height) // 2)) if im.width <= bw and im.height <= bh else \
        box.paste(im.crop(((im.width - bw) // 2 if im.width > bw else 0, (im.height - bh) // 2 if im.height > bh else 0,
                           (im.width - bw) // 2 + bw if im.width > bw else im.width, (im.height - bh) // 2 + bh if im.height > bh else im.height)),
                  ((bw - min(bw, im.width)) // 2, (bh - min(bh, im.height)) // 2))
    return box

yy, xx = np.mgrid[0:H, 0:W]
_r = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.66)) ** 2)
VIGN = np.clip(1.0 - 0.55 * np.clip(_r - 0.45, 0, 1) ** 1.4, 0.35, 1.0).astype(np.float32)[..., None]
_rng = np.random.default_rng(7)
GRAIN = [(_rng.normal(0, 2.4, (H, W, 1))).astype(np.float32) for _ in range(6)]
_P = [(_rng.uniform(0, W), _rng.uniform(0, H), _rng.uniform(2, 6), _rng.uniform(0.3, 1), _rng.uniform(4, 16), _rng.uniform(0, 6.28)) for _ in range(46)]

def overlay(img, t):
    lay = Image.new('RGBA', (W // 2, H // 2), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for x, y, r, a, v, ph in _P:
        px = ((x + 26 * math.sin(t * 0.5 + ph)) % W) / 2; py = ((y - v * t) % H) / 2
        al = int(255 * 0.06 * a * (0.6 + 0.4 * math.sin(t * 1.3 + ph)))
        d.ellipse((px - r / 2, py - r / 2, px + r / 2, py + r / 2), fill=(255, 250, 240, al))
    lay = lay.filter(ImageFilter.GaussianBlur(3)).resize((W, H), Image.BILINEAR)
    base = img.convert('RGBA'); base.alpha_composite(lay); return base.convert('RGB')

def finish(im, fi, fade=1.0):
    a = np.asarray(im).astype(np.float32) * VIGN * fade + GRAIN[fi % 6]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))

def push(img, lt, L, amt=0.025):
    z = 1.0 + amt * (lt / max(L, 0.1)); cw, ch = W / z, H / z; l, tp = (W - cw) / 2, (H - ch) / 2
    return img.crop((l, tp, l + cw, tp + ch)).resize((W, H), Image.BICUBIC)

def fmt(v):
    w = round(v * 1e4 / 10) * 10; s = '+' if w > 0 else '-' if w < 0 else '±'; a = abs(w)
    return f"{s}{a/10000:.2f}억" if a >= 10000 else f"{s}{a:,}만"
def pct(o): return f"{o['pct']:+.1f}%"
def blank(): return Image.new('RGB', (W, H), BG)
def disc(img, a=1.0): text(img, (CX, 1010), DISC, 24, GRAY, bold=0, a=a)

_cache = {}
def ld(name, mode='grade'):
    k = (name, mode)
    if k not in _cache:
        im = Image.open(IMG + name).convert('RGB')
        _cache[k] = grade(im, 0.66) if mode == 'grade' else darken(im, 0.86)
    return _cache[k]

NP = sum(1 for o in D if o['pct'] > 0); B1 = sum(1 for o in D if -5 < o['pct'] <= 0)
B2 = sum(1 for o in D if -10 < o['pct'] <= -5); B3 = sum(1 for o in D if o['pct'] <= -10)

# ------------------------------------------------------------------ 장면들 (t: 장면 안 경과초, L: 장면 길이)
def s_open(t, L):
    img = blank()
    text(img, (CX, 300), '브동산', 44, BRASS, sp=18, a=ease((t - 0.4) / 0.8))
    hline(img, 390, CX - 420, CX + 420, ease_out((t - 0.2) / 1.2))
    k = ease_out((t - 1.0) / 1.0)
    text(img, (CX, 430 - 16 * (1 - k)), '수도권 미분양 선착순', 92, WHITE, sp=6, bold=2, a=ease((t - 1.0) / 0.9))
    text(img, (CX, 560 - 16 * (1 - ease_out((t - 1.5) / 1.0))), 'TOP 30', 150, BRASS, sp=14, bold=3, a=ease((t - 1.5) / 0.9))
    hline(img, 760, CX - 420, CX + 420, ease_out((t - 2.2) / 1.0), w=1)
    text(img, (CX, 790), '지금 해볼 만한 단지가 있을까?', 50, WHITE, sp=4, bold=1, a=ease((t - 2.6) / 0.9))
    text(img, (CX, 880), f'{D_DOT} 기준 · 브동산 모형으로 30곳을 같은 잣대로 계산했습니다', 28, GRAY, bold=0, a=ease((t - 3.2) / 0.9))
    return img

def s_hook(t, L):
    img = blank()
    lines = [('청약통장 없이,', WHITE), ('원하는 동·호수를,', WHITE), ('시세 수준에.', BRASS)]
    for i, (s, c) in enumerate(lines):
        k = ease((t - 0.3 - i * 0.9) / 0.8)
        text(img, (CX, 300 + i * 140 + 14 * (1 - k)), s, 86, c, sp=4, bold=2, a=k)
    text(img, (CX, 780), '선착순 동·호 지정 계약을 받는 수도권 미분양 아파트, 그 가격은 적정할까요?', 34, GRAY, bold=0, a=ease((t - 3.2) / 0.9))
    return img

def s_glance(t, L):
    img = blank()
    text(img, (CX, 110), '한눈에 보기', 44, BRASS, sp=14, a=ease(t / 0.7))
    hline(img, 180, CX - 300, CX + 300, ease_out((t - 0.2) / 1.0))
    # 왼쪽: 큰 숫자
    k = ease_out((t - 0.6) / 1.4); n = int(round(NP * k))
    text(img, (520, 300), '분양가보다 적정가격이 높은 단지', 36, WHITE, bold=0, a=ease((t - 0.4) / 0.7))
    text(img, (520, 370), f'{n}', 300, BRASS, bold=4, a=ease((t - 0.6) / 0.6))
    text(img, (520, 720), f'30곳 중 단 {NP}곳 · 그마저 +2% 안쪽', 40, WHITE, bold=1, a=ease((t - 2.0) / 0.8))
    # 오른쪽: 분포 막대
    rows = [('플러스', NP, BRASS), ('0 ~ -5%', B1, (225, 222, 214)), ('-5 ~ -10%', B2, (150, 148, 142)), ('-10% 이하', B3, (95, 93, 90))]
    mx = max(r[1] for r in rows)
    text(img, (1060, 300), '분양가 대비 증감률 분포', 34, GRAY, anchor='l', bold=0, a=ease((t - 1.0) / 0.7))
    d = ImageDraw.Draw(img)
    for i, (lab, v, c) in enumerate(rows):
        y = 390 + i * 120; p = ease_out((t - 1.2 - i * 0.35) / 1.0)
        text(img, (1060, y), lab, 36, WHITE, anchor='l', bold=1, a=p)
        w = 430 * v / mx * p
        if p > 0: d.rectangle((1290, y + 6, 1290 + w, y + 46), fill=c)
        if p > 0.6: text(img, (1290 + w + 20, y), f'{v}곳', 40, BRASS if c == BRASS else WHITE, anchor='l', bold=2, a=ease((p - 0.6) / 0.4))
    text(img, (CX, 900), f'0 ~ -5% 구간에 {B1}곳이 몰려 있습니다. 대부분 시세와 크게 다르지 않은 가격입니다.', 34, WHITE, bold=0, a=ease((t - 4.0) / 0.9))
    disc(img, ease((t - 1.0) / 1.0))
    return img

def s_method(t, L):
    img = blank()
    text(img, (CX, 110), '이렇게 계산했습니다', 44, BRASS, sp=10, a=ease(t / 0.7))
    hline(img, 180, CX - 300, CX + 300, ease_out((t - 0.2) / 1.0))
    steps = [('01', '기준 분양가', ['대표 84㎡ 최고가', '확정 페이백만 차감']),
             ('02', '비교단지 2곳', ['같은 동네 신축 실거래', '평점·연식 보정 후 평균']),
             ('03', '적정가격', ['준공 단지는 자기 시세', '옆 미분양 가격이 상한']),
             ('04', '예상 프리미엄', ['적정가격 - 분양가', '순위는 증감률(%)'])]
    d = ImageDraw.Draw(img); bw, gap = 380, 40; x0 = CX - (4 * bw + 3 * gap) // 2
    for i, (n, ttl, ls) in enumerate(steps):
        p = ease((t - 0.6 - i * 0.7) / 0.8); x = x0 + i * (bw + gap); y = 300 + 20 * (1 - p)
        if p <= 0: continue
        last = i == 3; col = BRASS if last else (70, 68, 64)
        d.rectangle((x, y, x + bw, y + 420), outline=col, width=2)
        text(img, (x + 34, y + 34), n, 64, BRASS if last else GRAY, anchor='l', bold=2, a=p)
        text(img, (x + 34, y + 140), ttl, 44, WHITE, anchor='l', bold=2, a=p)
        for j, l in enumerate(ls): text(img, (x + 34, y + 240 + j * 56), l, 30, WHITE if last else (200, 197, 190), anchor='l', bold=0, a=p)
        if i < 3: hline(img, int(y + 210), x + bw + 6, x + bw + gap - 6, p, GRAY, 2)
    text(img, (CX, 800), '16억 단지와 5억 단지를 같은 금액으로 비교할 수 없어, 순위는 분양가 대비 증감률로 매겼습니다.', 32, WHITE, bold=0, a=ease((t - 3.8) / 0.9))
    text(img, (CX, 860), '-1억 ~ 0 구간은 선분양 수요를 감안해 절반으로, -1.5억 ~ -1억은 +3천만원 조정(브동산 6-1 규칙)', 26, GRAY, bold=0, a=ease((t - 4.4) / 0.9))
    return img

def s_divider(lab, sub):
    def f(t, L):
        img = blank()
        hline(img, 470, CX - 360, CX + 360, ease_out((t - 0.1) / 0.9))
        text(img, (CX, 500 - 10 * (1 - ease_out((t - 0.3) / 0.8))), lab, 110, WHITE, sp=10, bold=3, a=ease((t - 0.3) / 0.7))
        text(img, (CX, 650), sub, 36, BRASS, sp=2, bold=1, a=ease((t - 0.8) / 0.7))
        hline(img, 720, CX - 360, CX + 360, ease_out((t - 0.6) / 0.9), w=1)
        return img
    return f

PANEL = (100, 190, 1060, 596)  # x, y, w, h (16:9)
def panel_src(o):
    ae = os.path.exists(IMG + f"{o['key']}-aerial.jpg"); lo = os.path.exists(IMG + f"{o['key']}-location.jpg")
    return ae, lo

def s_complex(o, top=False):
    ae, lo = panel_src(o)
    one = T[o['key']][1]
    def f(t, L):
        img = blank(); d = ImageDraw.Draw(img)
        x, y, bw, bh = PANEL
        # 이미지 패널: 조감도 → (중간부터) 위치도로 디졸브
        cap = ''
        if ae or lo:
            half = L * 0.52
            if ae:
                a_img = kenburns(ld(f"{o['key']}-aerial.jpg"), bw, bh, t / L, 1.0, 1.18, 0.5, 0.55, 0.55, 0.45)
            if lo:
                l_img = fitbox(ld(f"{o['key']}-location.jpg", 'dark'), bw, bh, max(0, t - half) / max(0.1, L - half))
            if ae and lo:
                k = ease((t - half) / 0.7); pimg = Image.blend(a_img, l_img, k) if k > 0 else a_img
                cap = '조감도' if k < 0.5 else '위치도'
            else:
                pimg = a_img if ae else l_img; cap = '조감도' if ae else '위치도'
            img.paste(pimg, (x, y))
            d.line((x, y, x + bw, y), fill=BRASS, width=2); d.line((x, y + bh, x + bw, y + bh), fill=BRASS, width=2)
            text(img, (x, y + bh + 18), f'{cap} · 분양 홍보 페이지(아파트투유) · CG·홍보물로 실제와 다를 수 있음', 22, GRAY, anchor='l', bold=0, a=ease((t - 0.8) / 0.7))
        else:
            d.rectangle((x, y, x + bw, y + bh), outline=(46, 45, 42), width=2)
            text(img, (x + bw / 2, y + 90), f"{o['rank']:02d}", 300, (30, 29, 27), bold=4)
            text(img, (x + bw / 2, y + bh - 120), o['region'], 44, GRAY, bold=1, a=ease((t - 0.4) / 0.8))
            text(img, (x + bw / 2, y + bh + 18), '공식 이미지 확인 중 · 다음 회차에 보완합니다', 22, GRAY, bold=0, a=ease((t - 0.8) / 0.7))
        # 오른쪽 정보
        rx, rw = 1240, 600
        text(img, (rx, 150), f"No. {o['rank']:02d}", 64, BRASS, sp=6, anchor='l', bold=2, a=ease((t - 0.1) / 0.6))
        names = wrap(o['name'], 54, rw)
        ny = 245
        for i, nm in enumerate(names[:2]):
            text(img, (rx, ny + i * 70), nm, 54, WHITE, anchor='l', bold=2, a=ease((t - 0.3) / 0.7))
        ny += 70 * min(2, len(names)) + 10
        meta = f"{o['region']} · {o['n']:,}세대 · {o['yr']}.{o['mo']:02d} {'준공' if o.get('done') else '입주예정'}"
        mpx = 28
        while tw(meta, mpx) > rw and mpx > 20: mpx -= 1
        text(img, (rx, ny), meta, mpx, GRAY, anchor='l', bold=0, a=ease((t - 0.6) / 0.7))
        hline(img, ny + 60, rx, rx + rw, ease_out((t - 0.7) / 0.9), (70, 68, 64), 1)
        # 증감률 카운트업
        k = ease_out((t - 1.0) / 1.2); v = o['pct'] * k
        col = BRASS if o['pct'] > 0 else WHITE
        text(img, (rx, ny + 90), f"{v:+.1f}%", 112, col, anchor='l', bold=3, a=ease((t - 1.0) / 0.5))
        text(img, (rx, ny + 230), f"{fmt(o['final'])}  ·  분양가 {o['base']:.2f}억 → 적정 {o['fair']:.2f}억", 30, WHITE, anchor='l', bold=1, a=ease((t - 1.8) / 0.7))
        # 한줄평
        ls = wrap(one, 32, rw)
        for i, l in enumerate(ls[:3]):
            text(img, (rx, ny + 310 + i * 48), l, 32, BRASS if i == 0 else (225, 222, 214), anchor='l', bold=1 if i == 0 else 0, a=ease((t - 2.4 - i * 0.25) / 0.8))
        if top:  # TOP3: 분양가 vs 적정가 막대
            by = 915; mx = max(o['base'], o['fair']) * 1.08; p1 = ease_out((t - 3.2) / 1.0); p2 = ease_out((t - 3.7) / 1.0)
            if p1 > 0:
                text(img, (x, by - 44), '브동산 적정가격', 26, WHITE, anchor='l', bold=0, a=p1)
                d.rectangle((x + 230, by - 40, x + 230 + 700 * o['fair'] / mx * p1, by - 12), fill=(225, 222, 214))
                text(img, (x + 250 + 700 * o['fair'] / mx * p1, by - 46), f"{o['fair']:.2f}억", 26, WHITE, anchor='l', bold=1, a=p1)
            if p2 > 0:
                text(img, (x, by + 6), '분양가', 26, WHITE, anchor='l', bold=0, a=p2)
                d.rectangle((x + 230, by + 10, x + 230 + 700 * o['base'] / mx * p2, by + 38), fill=BRASS)
                text(img, (x + 250 + 700 * o['base'] / mx * p2, by + 4), f"{o['base']:.2f}억", 26, BRASS, anchor='l', bold=1, a=p2)
        disc(img, ease((t - 0.5) / 0.8))
        return img
    return f

def s_board(t, L):
    img = blank(); d = ImageDraw.Draw(img)
    text(img, (CX, 60), '전체 순위 · 분양가 대비 예상 프리미엄', 40, BRASS, sp=6, a=ease(t / 0.7))
    lo_, hi_ = min(o['pct'] for o in D), max(o['pct'] for o in D)
    for col in range(2):
        for i in range(15):
            o = D[col * 15 + i]; p = ease_out((t - 0.4 - (col * 15 + i) * 0.07) / 0.8)
            if p <= 0: continue
            y = 150 + i * 56; x0 = 80 + col * 920
            text(img, (x0, y), f"{o['rank']:2d}  {o['name'][:16]}{'…' if len(o['name']) > 16 else ''}", 26, WHITE if o['rank'] > 3 else BRASS, anchor='l', bold=1 if o['rank'] <= 3 else 0, a=p)
            zero = x0 + 640; sc = 230 / (hi_ - lo_ + 2)
            v = o['pct'] * p; bx = zero if v >= 0 else zero + v * sc
            d.rectangle((bx, y + 8, bx + max(2, abs(v) * sc), y + 32), fill=BRASS if o['pct'] > 0 else ((200, 197, 190) if o['pct'] > -5 else (120, 118, 112) if o['pct'] > -10 else (75, 73, 70)))
            text(img, (zero + 32 if o['pct'] >= 0 else zero + 14, y), pct(o), 24, WHITE, anchor='l', bold=1, a=p) if o['pct'] < 0 and abs(o['pct']) * sc < 60 else \
                text(img, (bx + abs(v) * sc + 10 if o['pct'] >= 0 else zero + 12, y), pct(o), 24, BRASS if o['pct'] > 0 else WHITE, anchor='l', bold=1, a=p)
        d.line((80 + col * 920 + 640, 150, 80 + col * 920 + 640, 150 + 15 * 56), fill=(70, 68, 64), width=1)
    disc(img, ease((t - 1.0) / 1.0))
    return img

GROUPS = [('지금 볼 만한 곳', '시세 수준 + 입지 요건 좋음', ['오산헤리티지자이', '고촌센트럴자이', '상동역 롯데캐슬 시그니처', '시티오씨엘 9단지', '여주역 로제비앙 더센텀', '향남역 그로브 스위첸']),
          ('조건 확인하면 기회', '페이백·할인 조건', ['힐스테이트 수원파크포레', '오목천역 더리브', '화서역 호수공원 아너스빌', '인하대역 수자인 로이센트']),
          ('저층·타입이 열쇠', '층·타입별 가격 차 큼', ['힐스테이트 구월아트파크', '영종 디에트르 라 메르Ⅰ', '쌍용 더 플래티넘 한강'])]
def s_groups(t, L):
    img = blank(); d = ImageDraw.Draw(img)
    text(img, (CX, 90), '브동산 한줄평 · 이렇게 보세요', 44, BRASS, sp=8, a=ease(t / 0.7))
    hline(img, 160, CX - 300, CX + 300, ease_out((t - 0.2) / 1.0))
    bw, gap = 540, 50; x0 = CX - (3 * bw + 2 * gap) // 2
    for i, (a, b, names) in enumerate(GROUPS):
        p = ease((t - 0.6 - i * 1.0) / 0.9); x = x0 + i * (bw + gap); y = 230 + 16 * (1 - p)
        if p <= 0: continue
        first = i == 0
        d.rectangle((x, y, x + bw, y + 600), outline=BRASS if first else (70, 68, 64), width=2)
        d.rectangle((x, y, x + 10, y + 600), fill=BRASS if first else (90, 88, 84))
        text(img, (x + 44, y + 40), a, 44, BRASS if first else WHITE, anchor='l', bold=2, a=p)
        text(img, (x + 44, y + 110), b, 28, GRAY, anchor='l', bold=0, a=p)
        for j, n in enumerate(names): text(img, (x + 44, y + 190 + j * 62), '· ' + n, 32, WHITE, anchor='l', bold=0, a=ease((t - 1.0 - i * 1.0 - j * 0.15) / 0.6))
    text(img, (CX, 900), '큰 웃돈을 노릴 시장은 아니지만, 살 집을 고르는 실거주자에게는 기회입니다.', 36, WHITE, bold=1, a=ease((t - 4.4) / 0.9))
    return img

def s_risk(t, L):
    img = blank()
    text(img, (CX, 140), '계약 전에 꼭 확인할 것', 44, BRASS, sp=8, a=ease(t / 0.7))
    hline(img, 210, CX - 300, CX + 300, ease_out((t - 0.2) / 1.0))
    items = [('판촉 조건', '계약금 정액제·중도금 무이자·페이백이 붙으면 실제 부담은 표보다 낮아집니다'),
             ('층·타입', '층·타입별 차이가 1억원 넘는 단지는 저층·다른 타입을 고르면 결과가 크게 달라집니다'),
             ('수원파크포레', '113㎡ 10% 페이백이 84㎡에도 적용되면 +6.6%로 1위가 됩니다'),
             ('비교 기준', '오남은 2009년식과 비교했고, 브레인시티 상한은 실거래가 아닌 호가 평균입니다')]
    for i, (a, b) in enumerate(items):
        p = ease((t - 0.6 - i * 0.8) / 0.8); y = 290 + i * 150
        hline(img, y - 24, 260, 1660, p, (70, 68, 64), 1)
        text(img, (260, y + 6), a, 36, BRASS, anchor='l', bold=2, a=p)
        text(img, (620, y + 10), b, 30, WHITE, anchor='l', bold=0, a=p)
    disc(img, 1.0)
    return img

def s_end(t, L):
    img = blank()
    text(img, (CX, 330), '웃돈은 작아도,', 76, WHITE, sp=4, bold=2, a=ease(t / 0.7))
    text(img, (CX, 440), '고를 수 있는 시장', 76, BRASS, sp=4, bold=2, a=ease((t - 0.5) / 0.7))
    hline(img, 590, CX - 260, CX + 260, ease_out((t - 1.1) / 0.8))
    text(img, (CX, 630), '브동산은 이 랭킹을 보름마다 다시 계산합니다', 40, WHITE, sp=2, bold=1, a=ease((t - 1.6) / 0.7))
    text(img, (CX, 700), '더 궁금한 단지는 댓글로 남겨주세요 · 단지별 계산 과정은 brandongsan.com', 30, GRAY, bold=0, a=ease((t - 2.1) / 0.7))
    text(img, (CX, 800), '숫자로 읽는 브동산', 34, BRASS, sp=12, bold=1, a=ease((t - 2.6) / 0.7))
    disc(img, ease(t / 0.7))
    return img

# ------------------------------------------------------------------ 타임라인
def build_scenes():
    sc = [('오프닝', s_open, 6.5, 'open'), (None, s_hook, 6.0, 'hook'), ('한눈에 보기', s_glance, 8.5, 'glance'), ('계산 방법', s_method, 9.0, 'method')]
    order = list(reversed(D))  # 30위 → 1위
    seg = {30: ('30위 ~ 21위', '격차가 큰 구간 · 저층·타입·판촉이 열쇠'), 20: ('20위 ~ 11위', '-3% ~ -6% · 수천만원 차이'),
           10: ('10위 ~ 4위', '-3% 안쪽 · 사실상 시세 수준'), 3: ('TOP 3', '30곳 중 가장 가격이 합리적인 세 곳')}
    for o in order:
        r = o['rank']
        if r in seg: sc.append((seg[r][0], s_divider(*seg[r]), 2.8, 'div'))
        sc.append((None, s_complex(o, top=r <= 3), 8.0 if r <= 3 else 5.2, 'top' if r <= 3 else 'cx'))
    sc += [('전체 순위', s_board, 9.0, 'board'), ('브동산 한줄평', s_groups, 9.5, 'groups'), ('리스크 체크', s_risk, 7.5, 'risk'), ('마무리', s_end, 6.5, 'end')]
    out, cur = [], 0.0
    for ch, fn, ln, kind in sc:
        out.append((cur, cur + ln, fn, kind, ch)); cur += ln
    return out, cur

SC, DUR = build_scenes()
XF = 0.5

def render(i, t):
    s, e, fn, kind, _ = SC[i]; lt = t - s
    img = fn(lt, e - s)
    return push(img, lt, e - s, 0.02 if kind in ('cx', 'top') else 0.03)

def frame(fi):
    t = fi / FPS
    idx = next((i for i, sc in enumerate(SC) if sc[0] <= t < sc[1]), len(SC) - 1)
    img = render(idx, t); e = SC[idx][1]
    if idx + 1 < len(SC) and e - t < XF:
        img = Image.blend(img, render(idx + 1, t), ease(1 - (e - t) / XF))
    img = overlay(img, t)
    fade = 1.0
    if t < 1.0: fade = ease(t / 1.0)
    if DUR - t < 1.4: fade = min(fade, ease((DUR - t) / 1.4))
    return finish(img, fi, fade)

def render_chunk(args):
    a, b, path = args
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
           '-c:v', 'libx264', '-preset', 'medium', '-crf', '22', '-pix_fmt', 'yuv420p', '-an', path]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for fi in range(a, b): p.stdin.write(np.asarray(frame(fi)).tobytes())
    p.stdin.close(); p.wait(); return path

# ------------------------------------------------------------------ 음악(긴 버전): 섹션마다 화음이 바뀌는 드론·패드·펄스
def make_music(path, dur, rises, booms):
    sr = 44100; n = int(sr * dur); t = np.arange(n) / sr; rng = np.random.default_rng(3)
    sine = lambda f, ph=0: np.sin(2 * np.pi * f * t + ph)
    drone = 0.55 * sine(55.0) + 0.35 * sine(55.0 * 1.003, 1.1) + 0.22 * sine(82.41) + 0.10 * sine(110.0)
    chords = [[110.0, 164.81, 220.0, 261.63, 329.63], [87.31, 130.81, 174.61, 220.0, 261.63],
              [130.81, 196.0, 261.63, 329.63, 392.0], [98.0, 146.83, 196.0, 246.94, 293.66]]  # Am F C G
    seglen = 16.0; pad = np.zeros(n)
    for ci in range(int(dur // seglen) + 2):
        t0 = ci * seglen; env = np.clip(1 - np.abs((t - t0 - seglen / 2) / (seglen / 2 + 2.0)), 0, 1) ** 1.2
        if env.max() == 0: continue
        for j, f in enumerate(chords[ci % 4]):
            g = [.22, .18, .15, .11, .08][j]
            pad += env * g * (np.sin(2 * np.pi * f * t) + 0.6 * np.sin(2 * np.pi * f * 1.004 * t + 0.7) + 0.4 * np.sin(2 * np.pi * f * 0.996 * t + 1.9))
    pad *= 0.55 + 0.45 * np.clip(np.sin(np.pi * t / dur) ** 0.6, 0, 1)
    pulse = np.zeros(n); tb = 6.0
    while tb < dur - 4.0:
        i = int(tb * sr); k = np.arange(int(0.28 * sr)) / sr
        thump = np.sin(2 * np.pi * (62 - 22 * k / 0.28) * k) * np.exp(-k * 14)
        amp = 0.25 + 0.45 * (0.5 + 0.5 * math.sin(2 * math.pi * tb / 64.0)) * min(1, (tb - 6) / 20)
        if i + len(thump) <= n: pulse[i:i + len(thump)] += amp * thump
        tb += 0.9
    # 높은 반짝임(아르페지오 아주 약하게, 8마디마다)
    arp = np.zeros(n)
    for ci in range(int(dur // seglen) + 1):
        for j in range(8):
            t0 = ci * seglen + 2 + j * 1.8
            if t0 + 1.5 >= dur - 3: break
            f = chords[ci % 4][j % 5] * 4; i = int(t0 * sr); k = np.arange(int(1.5 * sr)) / sr
            arp[i:i + len(k)] += 0.05 * np.sin(2 * np.pi * f * k) * np.exp(-k * 2.5)
    noise = rng.normal(0, 1, n); rise = np.zeros(n)
    for c in rises:
        i0, i1 = int(max(0, c - 0.9) * sr), int(min(dur, c + 0.15) * sr); seg = noise[i0:i1]
        env = np.sin(np.linspace(0, np.pi / 2, len(seg))) ** 2 * np.linspace(1, 0.1, len(seg)) ** 0.3
        rise[i0:i1] += seg * env * 0.035
    boom = np.zeros(n)
    for c, g in booms:
        i = int(c * sr); k = np.arange(int(2.2 * sr)) / sr
        b = np.sin(2 * np.pi * (48 - 14 * (1 - np.exp(-k * 2.5))) * k) * np.exp(-k * 1.5)
        L = min(len(b), n - i)
        if L > 0: boom[i:i + L] += g * b[:L]
    mono = 0.30 * drone + 0.33 * pad + 0.5 * pulse + arp + rise + 0.6 * boom
    out = mono.copy()
    for d_ms, g in [(97, 0.42), (151, 0.36), (233, 0.30), (359, 0.24)]:
        dd = int(sr * d_ms / 1000); out[dd:] += g * mono[:-dd]
    R = np.concatenate([np.zeros(int(sr * 0.012)), out[:-int(sr * 0.012)]]); st = np.stack([out, R], 1)
    env = np.ones(n); env[:int(sr * 1.5)] = np.linspace(0, 1, int(sr * 1.5)) ** 2; env[-int(sr * 2.5):] = np.linspace(1, 0, int(sr * 2.5)) ** 1.5
    st *= env[:, None]; st = np.tanh(st * 1.1); st /= max(1e-6, np.abs(st).max()) / 0.72
    with wave.open(path, 'wb') as wf:
        wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(sr); wf.writeframes((st * 32767).astype(np.int16).tobytes())

def sfx_events():
    ev = []
    for s, e, fn, kind, _ in SC[1:]: ev.append((s - 0.45, 'whoosh', 0.42 if kind == 'cx' else 0.55))
    for s, e, fn, kind, _ in SC:
        if kind in ('cx', 'top'):
            o_t = s + 1.0 + (0.6 if kind == 'top' else 0)
            ev.append((s + 1.0, 'tick', 0.10))
        if kind == 'top': ev.append((s + 1.9, 'lowhit', 0.6)); ev.append((s + 1.95, 'ping', 0.38))
        if kind == 'glance': ev.append((s + 1.4, 'lowhit', 0.7)); ev.append((s + 1.45, 'ping', 0.4))
        if kind == 'div': ev.append((s + 0.3, 'lowhit', 0.35))
    ev.append((SC[-1][0] - 1.3, 'shimmer', 0.5))
    return ev

# ------------------------------------------------------------------ 썸네일·설명
def thumbnail(path):
    TW, TH = 1280, 720
    top = D[0]
    src = Image.open(IMG + f"{top['key']}-aerial.jpg" if os.path.exists(IMG + f"{top['key']}-aerial.jpg") else IMG + f"{D[1]['key']}-aerial.jpg").convert('RGB')
    src = grade(src, 0.5); s = max(TW / src.width, TH / src.height)
    bg = src.resize((int(src.width * s) + 1, int(src.height * s) + 1), Image.BICUBIC)
    bg = bg.crop(((bg.width - TW) // 2, (bg.height - TH) // 2, (bg.width - TW) // 2 + TW, (bg.height - TH) // 2 + TH)).filter(ImageFilter.GaussianBlur(2))
    a = np.asarray(bg).astype(np.float32); xs = np.linspace(0, 1, TW)[None, :, None]
    a = a * (0.25 + 0.6 * np.clip((xs - 0.35) / 0.65, 0, 1))  # 왼쪽 어둡게
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    text(img, (70, 70), '브동산 · 수도권 미분양 선착순', 34, BRASS, anchor='l', sp=4, bold=1)
    text(img, (64, 140), 'TOP 30', 170, WHITE, anchor='l', sp=6, bold=4)
    hline(img, 360, 70, 640, 1.0, BRASS, 3)
    text(img, (70, 385), '웃돈 남는 곳', 64, WHITE, anchor='l', bold=2)
    text(img, (70, 470), f'단 {NP}곳', 120, BRASS, anchor='l', bold=4)
    text(img, (72, 640), f'1위 {top["name"]} {pct(top)}', 34, WHITE, anchor='l', bold=1)
    img.save(path); return path

def describe(path):
    lines = ['제목: 수도권 미분양 선착순 TOP30 | 웃돈 남는 단지는 단 2곳? 지금 해볼 만한 곳 총정리', '',
             '설명:',
             f'{D_DOT} 기준, 청약통장 없이 동·호수를 골라 계약할 수 있는 수도권 미분양 선착순 아파트 30곳을 브동산 모형으로 계산해 분양가 대비 예상 프리미엄(%) 순으로 정리했습니다.',
             f'플러스는 {NP}곳, 1위 {D[0]["name"]} {pct(D[0])}({fmt(D[0]["final"])}). 단지별 비교단지와 보정 과정은 브동산 홈페이지에서 확인하세요.',
             f'https://www.brandongsan.com/posts/{SLUG}.html', '', '챕터']
    for s, e, fn, kind, ch in SC:
        if ch: lines.append(f"{int(s // 60)}:{int(s % 60):02d} {ch}")
    lines += ['', '브동산 모형 추정치이며 확정 수익이 아닙니다. 분양 조건·잔여 세대는 수시로 바뀌니 계약 전 입주자모집공고와 분양 사무실 안내를 확인하세요. 더 궁금한 단지는 댓글로 남겨주세요.',
              '', '#미분양 #선착순분양 #수도권아파트 #잔여세대 #줍줍 #예상프리미엄 #브동산']
    open(path, 'w', encoding='utf-8').write('\n'.join(lines) + '\n'); return path

if __name__ == '__main__':
    stills = [float(x) for x in sys.argv[1:]]
    if stills:
        for s in stills: frame(int(s * FPS)).save(OUT + f'long_{s}.png'); print(OUT + f'long_{s}.png')
        sys.exit()
    print('duration', round(DUR, 1), 'scenes', len(SC))
    nf = int(DUR * FPS); k = int(os.environ.get('JOBS', os.cpu_count() or 2))
    bounds = [(nf * i // k, nf * (i + 1) // k, OUT + f'_chunk{i}.mp4') for i in range(k)]
    with Pool(k) as p: parts = p.map(render_chunk, bounds)
    open(OUT + '_list.txt', 'w').write(''.join(f"file '{x}'\n" for x in parts))
    silent = OUT + f'{SLUG}-silent.mp4'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', OUT + '_list.txt', '-c', 'copy', silent], check=True)
    rises = [s for s, *_ in SC[1:]]
    booms = [(s + 1.9, 0.7) for s, e, fn, kind, _ in SC if kind == 'top'] + [(SC[-1][0], 0.5)]
    make_music(OUT + 'music.wav', DUR, rises, booms)
    sfx.mix(OUT + 'music.wav', OUT + 'audio.wav', sfx_events())
    final = OUT + f'{SLUG}-youtube.mp4'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', silent, '-i', OUT + 'audio.wav', '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
                    '-c:a', 'aac', '-b:a', '192k', '-t', str(DUR), '-movflags', '+faststart', final], check=True)
    print('video', final); print('thumb', thumbnail(OUT + f'{SLUG}-youtube-thumbnail.png')); print('desc', describe(OUT + f'{SLUG}-youtube.txt'))
