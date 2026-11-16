# -*- coding: utf-8 -*-
"""랭킹 차트·인포그래픽(사이트 1장 + 네이버 모바일 황동 인포그래픽) — fcdata(RID)로 수도권·지방 공용.
사용: RID=<rid> python3 scripts/firstcome/region_charts.py [출력폴더(기본 posts/images/<slug>)]
출력: chart-top.png(사이트) · chart-m-1..k.png(10위씩) · chart-summary.png · chart-picks.png · chart-method.png
"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from fcfont import FP, ACCENT, ACCENT_BG, INK, MID, SOFT, put, fmt
import fcdata as F

D, N, NP = F.D, F.N, F.NP
out = sys.argv[1] if len(sys.argv) > 1 else F.IMG_DIR
os.makedirs(out, exist_ok=True)
RD = F.D_DOT
def canvas(h, w=1000):
    fig = plt.figure(figsize=(w / 100, h / 100), dpi=100, facecolor='white')
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, w); ax.set_ylim(h, 0); ax.axis('off'); return fig, ax
def barcolor(v): return ACCENT if v > 0 else ('#5A5A5A' if v > -5 else '#9A9A9A' if v > -10 else '#CFCFCF')
def save(fig, name): p = os.path.join(out, name); fig.savefig(p, facecolor='white'); plt.close(fig); print(p)
TITLE = f"{F.LABEL} 미분양 선착순 TOP{N}"

# ---- 사이트용 순위 차트 1장
def site_chart():
    n = N; H = 0.40 * n + 1.7
    fig = plt.figure(figsize=(7.75, H), dpi=200, facecolor='white')
    ax = fig.add_axes([0.43, 0.62 / H, 0.53, 1 - 1.55 / H])
    vals = [o['pct'] for o in D]; y = list(range(n))[::-1]
    ax.barh(y, vals, color=[ACCENT if v > 0 else '#C4C4C4' for v in vals], height=0.62, zorder=3)
    ax.axvline(0, color=MID, lw=1)
    lo, hi = min(min(vals) - 12, -12), max(max(vals) + 10, 8); ax.set_xlim(lo, hi); ax.set_ylim(-0.7, n - 0.3)
    for yy, v, o in zip(y, vals, D):
        f = FP.copy(); f.set_size(8.6)
        ax.text(v + (0.5 if v >= 0 else -0.5), yy, f"{v:+.1f}%  ({fmt(o['final'])})", fontproperties=f, va='center', ha='left' if v >= 0 else 'right', color=INK)
        ax.text(lo - 1.2, yy, f"{o['rank']}. {o['name']}", fontproperties=f, va='center', ha='right', color=INK if v > 0 or o['rank'] <= 3 else MID, clip_on=False)
    ax.set_yticks([]); ax.set_xticks([])
    for s in ax.spines.values(): s.set_visible(False)
    t = FP.copy(); t.set_size(14); fig.text(0.03, 1 - 0.40 / H, f'{TITLE} · 예상 프리미엄(분양가 대비 %)', fontproperties=t, color=INK)
    s2 = FP.copy(); s2.set_size(8); fig.text(0.03, 1 - 0.70 / H, f'브동산 모형 · 84㎡ 기준(일부 59㎡) · {RD} 기준', fontproperties=s2, color=SOFT)
    fig.text(0.03, 0.24 / H, '괄호 안은 금액. 분양가는 대표 타입 최고가, 확정된 현금 페이백만 차감.', fontproperties=s2, color=SOFT)
    p = os.path.join(out, 'chart-top.png'); fig.savefig(p, facecolor='white'); plt.close(fig); print(p)

def rank_charts():
    lo, hi = min(o['pct'] for o in D), max(o['pct'] for o in D)
    lo2, hi2 = min(lo, -1) - 1, max(hi, 1) + 1
    k = 0
    for part in range(0, N, 10):
        g = D[part:part + 10]; RH = 118; H = 170 + RH * len(g) + 90; fig, ax = canvas(H); k += 1
        put(ax, 40, 56, f"{TITLE} · {g[0]['rank']}~{g[-1]['rank']}위", 40 if len(TITLE) < 16 else 34, True)
        put(ax, 40, 108, "분양가 대비 예상 프리미엄 · 괄호는 금액", 28, False, SOFT)
        ax.plot([40, 960], [140, 140], color=ACCENT, lw=3)
        x0, x1 = 40, 690
        zero = x0 + (x1 - x0) * (0 - lo2) / (hi2 - lo2); sc = (x1 - x0) / (hi2 - lo2)
        for i, o in enumerate(g):
            y = 170 + RH * i; v = o['pct']
            put(ax, 40, y + 26, f"{o['rank']}. {o['name']}", 30, o['rank'] <= 3 or v > 0, INK)
            bx = zero if v >= 0 else zero + v * sc; bw = max(abs(v) * sc, 3)
            ax.add_patch(Rectangle((bx, y + 52), bw, 28, fc=barcolor(v), ec='none'))
            lab = f"{v:+.1f}%  ({fmt(o['final'])})"
            put(ax, (bx + bw + 12) if v >= 0 else zero + 14, y + 66, lab, 28, True, ACCENT if v > 0 else INK)
        ax.plot([zero, zero], [160, 170 + RH * len(g) - 6], color=MID, lw=1.5)
        put(ax, 40, H - 40, f"{RD} 기준 · 브동산 모형 · 막대 황동색은 플러스", 26, False, SOFT)
        save(fig, f"chart-m-{k}.png")

def summary():
    fig, ax = canvas(900)
    put(ax, 40, 56, TITLE, 42, True); put(ax, 40, 108, f"{RD} 기준 · {N}곳 예상 프리미엄 한눈에", 28, False, SOFT)
    ax.plot([40, 960], [140, 140], color=ACCENT, lw=3)
    ax.add_patch(Rectangle((40, 175), 920, 270, fc=ACCENT_BG, ec=ACCENT, lw=3))
    t = D[0]; nm = t['name'] if len(t['name']) <= 16 else t['name'][:15] + '…'
    put(ax, 80, 222, f"1위 · {nm}", 34, True)
    put(ax, 80, 320, f"{t['pct']:+.1f}%", 110 if abs(t['pct']) < 10 else 96, True, ACCENT)
    put(ax, 520, 292, fmt(t['final']), 54, True); put(ax, 520, 352, f"분양가 {t['base']:.2f}억 · 적정가 {t['fair']:.2f}억", 28, False, MID)
    put(ax, 80, 410, f"분양가보다 적정가격이 높은 단지는 {N}곳 중 {NP}곳" if NP else f"{N}곳 모두 분양가가 적정가격보다 높음 · 1위는 차이가 가장 작은 곳", 28, False, INK)
    put(ax, 40, 500, "분양가 대비 증감률 분포 (단지 수)", 34, True)
    rows = [("플러스", NP, ACCENT), ("0 ~ -5%", F.B1, '#5A5A5A'), ("-5 ~ -10%", F.B2, '#9A9A9A'), ("-10% 이하", F.B3, '#CFCFCF')]
    mx = max(1, max(r[1] for r in rows))
    for i, (lab, n, c) in enumerate(rows):
        y = 560 + i * 76
        put(ax, 40, y + 26, lab, 30, True); w = 540 * n / mx
        if n: ax.add_patch(Rectangle((290, y + 4), w, 46, fc=c, ec='none'))
        put(ax, 290 + w + 16, y + 28, f"{n}곳", 34, True, ACCENT if c == ACCENT else INK)
    put(ax, 40, 880, "브동산 모형 · 84㎡ 기준(일부 59㎡)", 26, False, SOFT)
    save(fig, "chart-summary.png")

def picks():
    groups = F.META.get('groups', [])
    H = 170 + sum(136 + 52 * len(g[2]) for g in groups) + 20 * len(groups) + 60; fig, ax = canvas(H)
    put(ax, 40, 56, "브동산 한줄평 · 이렇게 보세요", 40, True); put(ax, 40, 108, "통장 없이, 원하는 동·호수를 고를 수 있는 선착순", 28, False, SOFT)
    ax.plot([40, 960], [140, 140], color=ACCENT, lw=3); y = 170
    for k, (t1, t2, names) in enumerate(groups):
        hh = 116 + 52 * len(names)
        ax.add_patch(Rectangle((40, y), 920, hh, fc=ACCENT_BG if k == 0 else 'white', ec=ACCENT if k == 0 else '#CFCFCF', lw=3))
        ax.add_patch(Rectangle((40, y), 14, hh, fc=ACCENT if k == 0 else '#5A5A5A', ec='none'))
        put(ax, 80, y + 36, t1, 36, True); put(ax, 80, y + 76, t2, 28, False, MID)
        for j, n in enumerate(names): put(ax, 80, y + 132 + 52 * j, f"· {n}", 30, False, INK)
        y += hh + 20
    put(ax, 40, H - 36, "순위·금액은 본문 표와 같은 기준입니다", 26, False, SOFT)
    save(fig, "chart-picks.png")

def method():
    steps = [("1. 기준 분양가", "대표 84㎡ 최고가\n확정 페이백만 차감"), ("2. 비교단지 2곳", "같은 생활권 신축 시세\n평점·연식 보정 후 평균"),
             ("3. 적정가격", "준공 단지는 자기 시세\n옆 미분양 가격이 상한"), ("4. 예상 프리미엄", "적정가격 - 분양가\n순위는 증감률(%)")]
    fig, ax = canvas(960)
    put(ax, 40, 56, "이렇게 계산했습니다", 42, True); put(ax, 40, 108, f"브동산 모형 · {N}곳 모두 같은 순서", 28, False, SOFT)
    ax.plot([40, 960], [140, 140], color=ACCENT, lw=3)
    for i, (a, b) in enumerate(steps):
        y = 175 + i * 180; last = i == 3
        ax.add_patch(Rectangle((40, y), 920, 150, fc=ACCENT_BG if last else 'white', ec=ACCENT if last else '#CFCFCF', lw=3))
        put(ax, 80, y + 46, a, 36, True, ACCENT if last else INK)
        for j, ln in enumerate(b.split('\n')): put(ax, 80, y + 92 + j * 40 - 10, ln, 30, False, INK)
    put(ax, 40, 925, "-1억~0 구간은 선분양 수요를 감안해 절반으로, -1.5억~-1억은 +3천만원 조정", 24, False, SOFT)
    save(fig, "chart-method.png")

if __name__ == '__main__':
    site_chart(); rank_charts(); summary(); picks(); method()
