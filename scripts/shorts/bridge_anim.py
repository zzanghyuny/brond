# -*- coding: utf-8 -*-
"""브동산 적정가 '브릿지' 애니메이션 — 쇼츠 두 스타일(make_gen 시네마틱, make_quiz 퀴즈)이 함께 쓴다.

비교단지 KB 시세 막대 → 평점·연령 보정(×배수)으로 늘었다 줄었다 → 두 보정가격이 한 점으로 모여 평균
→ (오피스텔이면 10% 감액) → 브동산 적정가 → 분양가 막대와 비교 → 예상 프리미엄 (판정)

spec (설정 JSON/CFG의 'bridge'):
  title, sub, vmax,
  comps: [{name, meta, kb, mult, adj}, {…}]          # adj = kb × mult (글의 브릿지 표 숫자 그대로)
  avg, avg_label,                                     # 두 보정가격 평균
  disc: {label, mult} | 없음                          # 오피스텔 10% 감액 등 마지막 단계
  fair, fair_label, price, price_label, prem, judge, kind('plus'|'minus'|'even')
draw(img, t, T): T = phase_times(...)가 돌려준 단계별 시작 시각(초). 화면 좌표는 1080×1920, 안전영역 x 54~885.
"""
from PIL import ImageDraw

BG = (8, 8, 9); INK = (244, 241, 234); SOFT = (185, 181, 172); FAINT = (150, 148, 142)
TRACK = (30, 30, 33); KBC = (120, 118, 112); BRASS = (200, 164, 92)
KIND = {'plus': (95, 184, 156), 'minus': (240, 138, 102), 'even': (185, 181, 172)}

def ease(x):
    x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def eo(x):
    x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3
def lerp(a, b, k): return a + (b - a) * k
def mix(c1, c2, k): return tuple(int(lerp(a, b, k)) for a, b in zip(c1, c2))

GAP = dict(adj=2.2, avg=2.8, disc=3.0, price=2.6, prem=2.0)   # 단계 사이 최소 간격(초) — 다 읽고 넘어가도록

def phase_times(spec, t0, length):
    """length 초 안에 단계를 배분(spec['phase'] 비율로 조정). 단계 사이는 GAP 초 이상 벌린다 — 나레이션보다 화면이 길어질 수 있다."""
    fr = dict(kb=0.0, adj=0.16, avg=0.40, disc=0.56, price=0.70, prem=0.82)
    if not spec.get('disc'): fr.update(price=0.60, prem=0.75)
    fr.update(spec.get('phase', {}))
    keys = ['kb', 'adj', 'avg'] + (['disc'] if spec.get('disc') else []) + ['price', 'prem']
    T = {}; prev = None
    for k in keys:
        v = t0 + fr[k] * length
        if prev is not None: v = max(v, T[prev] + GAP[k])
        T[k] = v; prev = k
    T.setdefault('disc', T['avg'])
    T['end'] = T['prem'] + 3.2           # 예상 프리미엄을 보여 주고 머무는 시간
    return T

class Bridge:
    def __init__(self, spec, text, x0=54, x1=885, cx=469):
        """text(img, (x, y), s, px, color, anchor('l'|'c'|'r'), alpha, weight('R'|'B'|'X'), maxw=None)"""
        self.s, self.text, self.x0, self.x1, self.cx = spec, text, x0, x1, cx
    def X(self, v): return self.x0 + (self.x1 - self.x0) * v / self.s['vmax']

    def bar(self, img, y, v, color, alpha=1.0, h=48):
        if alpha <= 0.01 or v <= 0: return
        d = ImageDraw.Draw(img, 'RGBA'); a = int(255 * alpha)
        d.rectangle((self.x0, y, self.x1, y + h), fill=TRACK + (a,))
        d.rectangle((self.x0, y, self.X(v), y + h), fill=color + (a,))

    def draw(self, img, t, T):
        s, tx = self.s, self.text; d = ImageDraw.Draw(img, 'RGBA')
        tx(img, (self.cx, 300), s.get('title', '브동산 적정가는 이렇게'), 52, BRASS, 'c', ease((t - T['kb']) / 0.5), 'X')
        tx(img, (self.cx, 370), s.get('sub', ''), 28, FAINT, 'c', ease((t - T['kb'] - 0.2) / 0.5), 'R', 840)
        ends = []
        for i, c in enumerate(s['comps']):
            y = 440 + 200 * i
            a = ease((t - T['kb'] - 0.35 * i) / 0.45)
            g = eo((t - T['kb'] - 0.35 * i) / 1.0)                      # KB 막대가 자라는 정도
            k = eo((t - T['adj'] - 0.45 * i) / 1.3)                     # 보정 진행도 0→1
            v = lerp(c['kb'] * g, c['adj'], k) if k > 0 else c['kb'] * g
            col = mix(KBC, BRASS, k)
            tx(img, (self.x0, y), c['name'], 36, INK, 'l', a, 'B', 520)
            tx(img, (self.x0, y + 46), c.get('meta', ''), 26, FAINT, 'l', a, 'R', 520)
            tx(img, (self.x1, y + 2), f'{v:.2f}억', 44, mix(INK, BRASS, k), 'r', a, 'X')
            tx(img, (self.x1, y + 52), f"KB {c['kb']:.2f}억", 24, FAINT, 'r', a * k, 'R')
            self.bar(img, y + 90, v, col, a)
            if k > 0:   # 원래 KB 위치 표시
                xk = self.X(c['kb']); d.line((xk, y + 84, xk, y + 144), fill=INK + (int(200 * a),), width=3)
                ac = ease((t - T['adj'] - 0.45 * i) / 0.4)
                tx(img, (self.x0, y + 150), f"평점·연령 보정 ×{c['mult']:.3f}", 28, BRASS, 'l', ac, 'B')
            ends.append((self.X(c['adj']), y + 114))
        # 두 보정가격이 한 점으로 모여 평균
        ya = 860; m = eo((t - T['avg']) / 1.1)
        fo = 1 - ease((t - T['avg'] - 1.9) / 0.6)     # 평균 막대가 서면 모이는 선은 사라진다
        if t > T['avg'] and fo > 0:
            xa = self.X(s['avg'])
            for (xe, ye) in ends:
                px, py = lerp(xe, xa, m), lerp(ye, ya + 114, m)
                d.line((xe, ye, px, py), fill=BRASS + (int(150 * (1 - 0.5 * m) * fo),), width=3)
                d.ellipse((px - 9, py - 9, px + 9, py + 9), fill=BRASS + (int(255 * fo),))
        disc = s.get('disc'); kd = eo((t - T['disc']) / 1.2) if disc else 0
        ab = ease((t - T['avg'] - 0.8) / 0.5)
        if ab > 0:
            va = lerp(s['avg'], s['fair'], kd) if disc else s['fair']
            col = mix(INK, BRASS, kd) if disc else BRASS
            lab0 = s.get('avg_label', '두 보정가격 평균'); lab1 = s.get('fair_label', '브동산 적정가')
            if disc:
                tx(img, (self.x0, ya), lab0, 36, INK, 'l', ab * (1 - kd), 'B', 520)
                tx(img, (self.x0, ya), lab1, 40, BRASS, 'l', ab * kd, 'X', 520)
            else:
                tx(img, (self.x0, ya), lab1, 40, BRASS, 'l', ab, 'X', 520)
            tx(img, (self.x1, ya - 4), f'{va:.2f}억', 52, col, 'r', ab, 'X')
            self.bar(img, ya + 88, va, col, ab, h=52)
            if disc and t > T['disc']:
                tx(img, (self.x0, ya + 152), f"{disc['label']} ×{disc['mult']}", 28, BRASS, 'l', ease((t - T['disc']) / 0.4), 'B')
        # 분양가 비교 → 예상 프리미엄
        yp = 1075; ap = ease((t - T['price']) / 0.5); gp = eo((t - T['price']) / 1.0)
        if ap > 0:
            tx(img, (self.x0, yp + 10), s.get('price_label', '평균 분양가'), 34, SOFT, 'l', ap, 'B', 520)
            tx(img, (self.x1, yp + 4), f"{s['price']:.2f}억", 48, INK, 'r', ap, 'X')
            self.bar(img, yp + 76, s['price'] * gp, SOFT, ap, h=44)
        kp = ease((t - T['prem']) / 0.5)
        if kp > 0:
            kc = KIND.get(s.get('kind', 'plus'), BRASS)
            xf, xp = self.X(s['fair']), self.X(s['price'])
            lo, hi = sorted((xf, xp))
            d.rectangle((lo, yp + 76, lo + (hi - lo) * eo((t - T['prem']) / 0.8), yp + 120), fill=kc + (int(200 * kp),))
            d.line((xf, ya + 88, xf, yp + 120), fill=kc + (int(230 * kp),), width=3)
            big = s['prem']; px = 84
            tx(img, (self.cx, 1212), '예상 프리미엄', 30, SOFT, 'c', kp, 'B')
            tx(img, (self.cx, 1246), f"{big} {s.get('judge', '')}".strip(), px, kc, 'c', kp, 'X', 840)
