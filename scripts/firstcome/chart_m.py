# 네이버 모바일용 인포그래픽 (캔버스 폭 1000px, 글씨 28px 이상, 황동 포인트 #C8A45C)
#  chart-m-1~3.png 순위(10위씩) · chart-summary.png 1위+분포 · chart-picks.png 한줄평 3묶음 · chart-method.png 계산 흐름
import json, sys, os
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from fcfont import *
d = json.load(open(sys.argv[1] if len(sys.argv) > 1 else 'result2.json'))
out = sys.argv[2] if len(sys.argv) > 2 else '.'
os.makedirs(out, exist_ok=True)
RD = os.environ.get('RANK_DATE', '2026-11-16').replace('-', '.')
def canvas(h, w=1000):
    fig = plt.figure(figsize=(w/100, h/100), dpi=100, facecolor='white')
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, w); ax.set_ylim(h, 0); ax.axis('off'); return fig, ax
def barcolor(v): return ACCENT if v > 0 else ('#5A5A5A' if v > -5 else '#9A9A9A' if v > -10 else '#CFCFCF')
def save(fig, name): p = f"{out}/{name}"; fig.savefig(p, facecolor='white'); plt.close(fig); print(p)

# ---- 순위 3장
lo, hi = min(o['pct'] for o in d), max(o['pct'] for o in d)
for part in range(0, len(d), 10):
    g = d[part:part+10]; RH = 118; H = 170 + RH*len(g) + 90; fig, ax = canvas(H)
    put(ax, 40, 56, f"미분양 선착순 TOP30 · {g[0]['rank']}~{g[-1]['rank']}위", 40, True)
    put(ax, 40, 108, "분양가 대비 예상 프리미엄 · 괄호는 금액", 28, False, SOFT)
    ax.plot([40, 960], [140, 140], color=ACCENT, lw=3)
    x0, x1 = 40, 690                       # 막대 영역(0선은 비율로)
    zero = x0 + (x1-x0)*(0-(lo-1))/((hi+1)-(lo-1)); sc = (x1-x0)/((hi+1)-(lo-1))
    for i, o in enumerate(g):
        y = 170 + RH*i; v = o['pct']
        put(ax, 40, y+26, f"{o['rank']}. {o['name']}", 30, o['rank'] <= 3 or v > 0, INK)
        bx = zero if v >= 0 else zero + v*sc; bw = max(abs(v)*sc, 3)
        ax.add_patch(Rectangle((bx, y+52), bw, 28, fc=barcolor(v), ec='none'))
        lab = f"{v:+.1f}%  ({fmt(o['final'])})"
        if v >= 0: put(ax, bx+bw+12, y+66, lab, 28, True, ACCENT if v > 0 else INK)
        else: put(ax, min(zero+14, 940-0), y+66, lab, 28, True, INK, 'left') if bw < 90 else put(ax, zero+14, y+66, lab, 28, True, INK, 'left')
    ax.plot([zero, zero], [160, 170+RH*len(g)-6], color=MID, lw=1.5)
    put(ax, 40, H-40, f"{RD} 기준 · 브동산 모형 · 막대 황동색은 플러스", 26, False, SOFT)
    save(fig, f"chart-m-{part//10+1}.png")

# ---- 요약: 1위 카드 + 분포
NP = sum(1 for o in d if o['pct'] > 0); b1 = sum(1 for o in d if -5 < o['pct'] <= 0); b2 = sum(1 for o in d if -10 < o['pct'] <= -5); b3 = sum(1 for o in d if o['pct'] <= -10)
fig, ax = canvas(900)
put(ax, 40, 56, "수도권 미분양 선착순 TOP30", 42, True); put(ax, 40, 108, f"{RD} 기준 · 30곳 예상 프리미엄 한눈에", 28, False, SOFT)
ax.plot([40, 960], [140, 140], color=ACCENT, lw=3)
ax.add_patch(Rectangle((40, 175), 920, 270, fc=ACCENT_BG, ec=ACCENT, lw=3))
t = d[0]
put(ax, 80, 222, f"1위 · {t['name']}", 34, True)
put(ax, 80, 320, f"{t['pct']:+.1f}%", 110, True, ACCENT)
put(ax, 500, 292, fmt(t['final']), 54, True); put(ax, 500, 352, f"분양가 {t['base']:.2f}억 · 적정가 {t['fair']:.2f}억", 28, False, MID)
put(ax, 80, 410, "분양가보다 적정가격이 높은 단지는 30곳 중 단 2곳", 28, False, INK)
put(ax, 40, 500, "분양가 대비 증감률 분포 (단지 수)", 34, True)
rows = [("플러스", NP, ACCENT), ("0 ~ -5%", b1, '#5A5A5A'), ("-5 ~ -10%", b2, '#9A9A9A'), ("-10% 이하", b3, '#CFCFCF')]
mx = max(r[1] for r in rows)
for i, (lab, n, c) in enumerate(rows):
    y = 560 + i*76
    put(ax, 40, y+26, lab, 30, True); w = 540*n/mx
    ax.add_patch(Rectangle((290, y+4), w, 46, fc=c, ec='none')); put(ax, 290+w+16, y+28, f"{n}곳", 34, True, ACCENT if c == ACCENT else INK)
put(ax, 40, 880, "브동산 모형 · 84㎡ 기준(59·60㎡ 단지 예외)", 26, False, SOFT)
save(fig, "chart-summary.png")

# ---- 한줄평 3묶음
groups = [("지금 볼 만한 곳", "시세 수준 + 입지 요건 좋음", ["오산헤리티지자이", "고촌센트럴자이", "상동역 롯데캐슬 시그니처", "시티오씨엘 9단지", "여주역 로제비앙 더센텀", "향남역 그로브 스위첸"]),
          ("조건 확인하면 기회", "페이백·할인 조건", ["힐스테이트 수원파크포레", "오목천역 더리브", "화서역 호수공원 아너스빌", "인하대역 수자인 로이센트"]),
          ("저층·타입이 열쇠", "층·타입별 가격 차 큼", ["힐스테이트 구월아트파크", "영종 디에트르 라 메르Ⅰ", "쌍용 더 플래티넘 한강"])]
H = 170 + sum(120 + 52*len(g[2]) for g in groups) + 70; fig, ax = canvas(H)
put(ax, 40, 56, "브동산 한줄평 · 이렇게 보세요", 40, True); put(ax, 40, 108, "통장 없이, 원하는 동·호수를, 시세 수준에 고른다", 28, False, SOFT)
ax.plot([40, 960], [140, 140], color=ACCENT, lw=3); y = 170
for k, (t1, t2, names) in enumerate(groups):
    hh = 100 + 52*len(names)
    ax.add_patch(Rectangle((40, y), 920, hh, fc=ACCENT_BG if k == 0 else 'white', ec=ACCENT if k == 0 else '#CFCFCF', lw=3))
    ax.add_patch(Rectangle((40, y), 14, hh, fc=ACCENT if k == 0 else '#5A5A5A', ec='none'))
    put(ax, 80, y+36, t1, 36, True); put(ax, 80, y+76, t2, 28, False, MID)
    for j, n in enumerate(names): put(ax, 80, y+122+52*j-10, f"· {n}", 30, False, INK)
    y += hh + 20
put(ax, 40, H-36, "순위·금액은 본문 표와 같은 기준입니다", 26, False, SOFT)
save(fig, "chart-picks.png")

# ---- 계산 흐름
steps = [("1. 기준 분양가", "대표 84㎡ 최고가\n확정 페이백만 차감"), ("2. 비교단지 2곳", "같은 동네 신축 실거래\n평점·연식 보정 후 평균"), ("3. 적정가격", "준공 단지는 자기 시세\n옆 미분양 가격이 상한"), ("4. 예상 프리미엄", "적정가격 − 분양가\n순위는 증감률(%)")]
fig, ax = canvas(960)
put(ax, 40, 56, "이렇게 계산했습니다", 42, True); put(ax, 40, 108, "브동산 모형 · 30곳 모두 같은 순서", 28, False, SOFT)
ax.plot([40, 960], [140, 140], color=ACCENT, lw=3)
for i, (a, b) in enumerate(steps):
    y = 175 + i*180; last = i == 3
    ax.add_patch(Rectangle((40, y), 920, 150, fc=ACCENT_BG if last else 'white', ec=ACCENT if last else '#CFCFCF', lw=3))
    put(ax, 80, y+46, a, 36, True, ACCENT if last else INK)
    for j, ln in enumerate(b.split('\n')): put(ax, 80, y+92+j*40-10, ln, 30, False, INK)
put(ax, 40, 925, "-1억~0 구간은 선분양 수요를 감안해 절반으로, -1.5억~-1억은 +3천만원 조정", 24, False, SOFT)
save(fig, "chart-method.png")
