#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""브동산 청약단지 네이버 발행본용 차트 생성 (모노톤, beodongsan-design-guideline 준수)
  chart-a-score.png    : 평점 비교표 이미지 (입지/브랜드/상품성/종합, SITE vs 비교단지 2곳)
  chart-b-price.png    : 비교단지 보정가격 + SITE 적정가격(+실제 분양가) 막대그래프
  chart-c-schedule.png : 청약 일정 타임라인 (공식 분양 사이트에 일정 이미지가 없을 때만)

사용법: python3 make_naver_charts.py <out_dir>  (DATA 딕셔너리를 포스팅 값으로 교체해서 사용)
이 리포의 컨테이너에는 NotoSansCJK가 없어 WenQuanYi Zen Hei로 대체했다
(/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc, 한글 렌더링 확인됨, 2026.11.09).
숫자는 반드시 posts/<slug>.html의 평점표·보정표에서 그대로 옮긴다(새로 추정 금지).
"""
import sys, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.font_manager import FontProperties

DATA = {
    'site': {'name': '단지명', 'note': 'SITE · YYYY.MM 입주예정', 'scores': [0, 0, 0]},
    'comps': [
        {'name': '비교단지1', 'note': '비교단지 · YYYY.MM 입주', 'scores': [0, 0, 0], 'short': '비교1', 'mult': 1.0},
        {'name': '비교단지2', 'note': '비교단지 · YYYY.MM 입주', 'scores': [0, 0, 0], 'short': '비교2', 'mult': 1.0},
    ],
    'price': {
        'comp_adjusted': [0.0, 0.0],
        'fair': 0.0,
        'actual': None,  # 분양가 미공개면 None
        'premium_text': '',
        'pct_text': '',
        'type': '84㎡',
    },
}

FONT = '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'
BOLD = FontProperties(fname=FONT)
REG = FontProperties(fname=FONT)
INK, MID, SOFT, HAIR, PANEL = '#111111', '#555555', '#8A8A8A', '#E3E3E3', '#F5F5F5'
DPI = 200


def T(ax, x, y, s, size=10, bold=False, color=INK, ha='left', va='center', **kw):
    fp = (BOLD if bold else REG).copy()
    fp.set_size(size)
    ax.text(x, y, s, fontproperties=fp, color=color, ha=ha, va=va, **kw)


def _wrap_name(a, max_len=7):
    if len(a) <= max_len:
        return a
    mid = len(a) // 2
    return a[:mid] + '\n' + a[mid:]


def chart_a(path, data=DATA):
    W, H = 7.75, 5.75
    fig = plt.figure(figsize=(W, H), dpi=DPI, facecolor='white')
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(H, 0); ax.axis('off')
    lx = 0.35
    cols = [(1.95, 3.78), (3.78, 5.61), (5.61, 7.44)]
    cen = [(a + b) / 2 for a, b in cols]
    T(ax, lx, 0.38, '평점 비교표', 14, True)
    T(ax, 7.44, 0.38, '100점 만점 · 브동산 모형 자체 산정', 8.2, False, SOFT, ha='right')
    ax.add_patch(Rectangle((cols[0][0], 0.75), cols[0][1] - cols[0][0], H - 1.3, fc=PANEL, ec='none', zorder=0))
    ents = [data['site']] + data['comps']
    for i, (c, e) in enumerate(zip(cen, ents)):
        site = i == 0
        T(ax, c, 1.12, e['name'], 10.6 if site else 10.2, True, INK if site else MID, ha='center')
        T(ax, c, 1.43, e['note'], 7.8, False, MID if site else SOFT, ha='center')
    ax.plot([lx, 7.44], [1.70, 1.70], color=INK, lw=1.3)
    y, bar_w = 1.70, 1.15
    for name, mx, k in [('입지', 40, 0), ('브랜드', 20, 1), ('상품성', 40, 2)]:
        h = 0.80; yc = y + h / 2
        T(ax, lx, yc - 0.10, name, 11.5, True)
        T(ax, lx, yc + 0.17, str(mx) + '점 만점', 7.8, False, SOFT)
        for i, (c, e) in enumerate(zip(cen, ents)):
            v, site = e['scores'][k], i == 0
            T(ax, c - 0.06, yc - 0.12, str(v), 20, True, INK if site else MID, ha='right')
            T(ax, c - 0.02, yc - 0.06, '/' + str(mx), 8.5, False, SOFT, ha='left')
            bx, by = c - bar_w / 2, yc + 0.17
            ax.add_patch(Rectangle((bx, by), bar_w, 0.07, fc=HAIR, ec='none'))
            ax.add_patch(Rectangle((bx, by), bar_w * v / mx, 0.07, fc=INK if site else SOFT, ec='none'))
        y += h
        ax.plot([lx, 7.44], [y, y], color=HAIR, lw=0.8)
    h = 1.25
    ax.plot([lx, 7.44], [y, y], color=INK, lw=1.3)
    yc = y + h / 2
    T(ax, lx, yc - 0.08, '종합평점', 12.5, True)
    T(ax, lx, yc + 0.2, '입지 + 브랜드 + 상품성', 7.8, False, SOFT)
    totals = [sum(e['scores']) for e in ents]
    for i, (c, v) in enumerate(zip(cen, totals)):
        site = i == 0
        T(ax, c - 0.07, yc - 0.06, str(v), 28, True, INK if site else MID, ha='right')
        T(ax, c - 0.02, yc + 0.02, '/100', 9, False, SOFT, ha='left')
        bx, by = c - bar_w / 2, yc + 0.30
        ax.add_patch(Rectangle((bx, by), bar_w, 0.07, fc=HAIR, ec='none'))
        ax.add_patch(Rectangle((bx, by), bar_w * v / 100, 0.07, fc=INK if site else SOFT, ec='none'))
    y += h
    ax.plot([lx, 7.44], [y, y], color=HAIR, lw=0.8)
    c1, c2 = data['comps']
    foot = '점수 차이에 따라 비교단지 시세를 보정한다 (SITE %d점 기준: %s ×%.3f, %s ×%.3f).' % (
        totals[0], c1['short'], c1['mult'], c2['short'], c2['mult'])
    T(ax, lx, H - 0.22, foot, 7.8, False, SOFT)
    fig.savefig(path, facecolor='white'); plt.close(fig)


def chart_b(path, data=DATA):
    P = data['price']; c1, c2 = data['comps']; tp = P['type']
    has_actual = P.get('actual') is not None
    W, H = 7.75, 5.6
    fig = plt.figure(figsize=(W, H), dpi=DPI, facecolor='white')
    ax = fig.add_axes([0.04, 0.17, 0.92, 0.66])
    if has_actual:
        xs = [0.0, 1.0, 2.35, 3.35]
        vals = P['comp_adjusted'] + [P['fair'], P['actual']]
        names = [c1['name'], c2['name'], 'SITE', 'SITE']
        subs = ['보정가격', '보정가격', '브동산 분석 적정가격', '실제 분양가']
        colors = [MID, SOFT, INK, '#C4C4C4']
    else:
        xs = [0.0, 1.0, 2.35]
        vals = P['comp_adjusted'] + [P['fair']]
        names = [c1['name'], c2['name'], 'SITE']
        subs = ['보정가격', '보정가격', '브동산 분석 적정가격']
        colors = [MID, SOFT, INK]
    top = max(vals) * 1.28; u = top / 19.0
    ax.bar(xs, vals, width=0.62, color=colors, zorder=3)
    for x, v in zip(xs, vals):
        T(ax, x, v + u * 0.35, '%.2f억' % v, 13, True, INK, ha='center', va='bottom')
    ax.set_xlim(-0.6, (5.35 if has_actual else 3.35)); ax.set_ylim(0, top)
    ax.set_xticks(xs); ax.set_xticklabels([])
    for x, a, b in zip(xs, names, subs):
        a2 = _wrap_name(a)
        if '\n' in a2:
            T(ax, x, -1.35 * u, a2, 8.6, True, INK, ha='center', va='center', clip_on=False, linespacing=1.3)
        else:
            T(ax, x, -0.9 * u, a2, 9.4, True, INK, ha='center', clip_on=False)
        T(ax, x, -2.75 * u, b, 9.4, False, MID, ha='center', clip_on=False)
    ax.set_yticks([])
    for s in ['top', 'right', 'left']: ax.spines[s].set_visible(False)
    ax.spines['bottom'].set_color(HAIR); ax.tick_params(axis='x', length=0)
    if has_actual:
        ax.plot([1.68, 1.68], [0, 17.2 * u], color=HAIR, lw=1, ls=(0, (4, 3)), zorder=1)
        T(ax, 0.5, 17.9 * u, '비교단지 (%s 실거래 → 보정)' % tp, 8.6, False, SOFT, ha='center')
        T(ax, 2.85, 17.9 * u, 'SITE (%s 기준)' % tp, 8.6, False, SOFT, ha='center')
        ax.plot([2.66, 4.35], [P['fair']] * 2, color=SOFT, lw=1, ls=(0, (2, 2)), zorder=2)
        ax.plot([3.66, 4.35], [P['actual']] * 2, color=SOFT, lw=1, ls=(0, (2, 2)), zorder=2)
        ax.annotate('', xy=(4.35, P['fair']), xytext=(4.35, P['actual']),
                    arrowprops=dict(arrowstyle='<->', color=INK, lw=1.6, shrinkA=0, shrinkB=0), zorder=4)
        mid = (P['fair'] + P['actual']) / 2
        T(ax, 4.55, mid + 1.15 * u, '예상 프리미엄', 9.5, False, MID)
        T(ax, 4.55, mid, P['premium_text'], 17, True, INK)
        T(ax, 4.55, mid - 1.1 * u, P['pct_text'], 8.6, False, SOFT)
    f1 = BOLD.copy(); f1.set_size(14)
    f2 = REG.copy(); f2.set_size(8.2)
    fig.text(0.045, 0.93, '적정가격 산출 비교', fontproperties=f1, color=INK, ha='left', va='center')
    fig.text(0.955, 0.93, '단위: 억원 · 전용 %s 총액 기준' % tp, fontproperties=f2, color=SOFT, ha='right', va='center')
    fig.savefig(path, facecolor='white'); plt.close(fig)


def chart_c(path, schedule):
    ev = schedule['events']
    W, H = 7.75, 2.9
    fig = plt.figure(figsize=(W, H), dpi=DPI, facecolor='white')
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(H, 0); ax.axis('off')
    T(ax, 0.35, 0.40, '청약 일정', 14, True)
    T(ax, 7.40, 0.40, schedule['note'], 8.2, False, SOFT, ha='right')
    x0, x1, ly = 0.95, 6.80, 1.65
    ax.plot([x0, x1], [ly, ly], color=HAIR, lw=2.2, zorder=1)
    ax.plot([x0 + 0.6, x1], [ly, ly], color=INK, lw=2.2, zorder=1)
    step = (x1 - x0) / (len(ev) - 1)
    for i, (d, n, filled) in enumerate(ev):
        x = x0 + i * step
        ax.scatter([x], [ly], s=170, zorder=3, facecolor=INK if filled else 'white', edgecolor=INK, linewidth=1.8)
        T(ax, x, ly - 0.52, d, 17, True, INK, ha='center')
        T(ax, x, ly + 0.50, n, 10.5, False, MID, ha='center')
    T(ax, 0.35, H - 0.22, schedule['footer'], 7.8, False, SOFT)
    fig.savefig(path, facecolor='white'); plt.close(fig)


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else '.'
    os.makedirs(out, exist_ok=True)
    chart_a(os.path.join(out, 'chart-a-score.png'))
    chart_b(os.path.join(out, 'chart-b-price.png'))
    print('done', out, '-- replace the DATA dict with the real posting values before using for publishing')
