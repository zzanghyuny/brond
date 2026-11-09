#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""브동산 네이버 발행본 차트 생성기 (2026.11.09 Paul 승인 샘플 '광교 자연앤 센트레빌' 형식)

  chart_a(path, data)   평점 비교 — 항목별(입지/브랜드/상품성/종합평점) 가로 막대, SITE=검정 · 비교1=진회색 · 비교2=연회색
  chart_b(path, data)   적정가격과 분양가 — 보정가격 2개 + 브동산 분석 적정가격(검정) + 실제 분양가(흰색 윤곽) + 예상 프리미엄 박스
  chart_map(path, data) 위치 개략도 — 흰 배경, SITE=검정 사각형, 비교단지=회색 윤곽 사각형, 학교=점선 사각형,
                        지하철역=검정 점, 생활시설=회색 점, 호수·공원=회색 타원, 좌상단 안내 박스, 우상단 N 화살표, 하단 범례
  chart_c(path, data)   청약 일정 타임라인 (공식 일정 이미지가 없을 때만)

폰트: 이 컨테이너엔 NotoSansCJK/맑은 고딕이 없어 WenQuanYi Zen Hei로 대체하고, 굵은 글씨는 stroke로 흉내 낸다.
숫자는 반드시 posts/<slug>.html 의 평점표·보정표에서 그대로 옮긴다(새로 추정 금지).

chart_a data 예:
  {'title':'평점 비교 · 입지 · 브랜드 · 상품성 (100점 만점)',
   'names':['SITE · 광교 자연앤 센트레빌','광교호반베르디움','광교더샵'],
   'scores':[[13,12,25],[17,12,29],[17,20,29]]}        # 각 단지 [입지(40), 브랜드(20), 상품성(40)]
chart_b data 예:
  {'type':'84㎡','comp_names':['광교호반베르디움','광교더샵'],'comp_adjusted':[15.49,14.27],
   'fair':14.88,'actual':9.37,'actual_label':'84㎡ 가중평균','premium_text':'+5.52억원','pct_text':'약 59% 저평가'}
   (분양가 미공개: 'actual':None -> 박스에 적정가격만 표기)
chart_map data 예: 아래 chart_map 독스트링 참고.
"""
import math, os, sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.patches import Rectangle, Ellipse
from matplotlib.font_manager import FontProperties

FONT = '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'
if not os.path.exists(FONT):  # 다른 환경: 한글 폰트 자동 탐색
    import matplotlib.font_manager as fm
    for f in fm.findSystemFonts():
        if any(k in f for k in ('NotoSansCJK', 'Malgun', 'NanumGothic', 'wqy')):
            FONT = f
            break
FP = FontProperties(fname=FONT)
DPI = 100


def px2pt(px):
    return px * 72.0 / DPI


def txt(ax, x, y, s, px=16, bold=False, color='#000000', ha='left', va='center', **kw):
    t = ax.text(x, y, s, fontproperties=FP, fontsize=px2pt(px), color=color, ha=ha, va=va, **kw)
    if bold:
        t.set_path_effects([pe.withStroke(linewidth=px * 0.045, foreground=color)])
    return t


def _canvas(w, h):
    fig = plt.figure(figsize=(w / DPI, h / DPI), dpi=DPI, facecolor='white')
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, w); ax.set_ylim(h, 0); ax.axis('off')
    return fig, ax


# ------------------------------------------------------------------ 차트 A
SERIES_FILL = ['#000000', '#777777', '#BBBBBB']


def chart_a(path, d):
    W, H = 1366, 770
    fig, ax = _canvas(W, H)
    txt(ax, 46, 47, d.get('title', '평점 비교 · 입지 · 브랜드 · 상품성 (100점 만점)'), 29, True)
    names = d['names']
    n = len(names)
    lx = [46, 466, 886][:n]
    for i, (x, nm) in enumerate(zip(lx, names)):
        ax.add_patch(Rectangle((x, 87), 22, 22, fc=SERIES_FILL[i], ec='#333333', lw=1.4))
        txt(ax, x + 34, 98, nm, 20, False, '#111111')
    totals = [sum(s) for s in d['scores']]
    cats = [('입지(40)', 40, [s[0] for s in d['scores']]),
            ('브랜드(20)', 20, [s[1] for s in d['scores']]),
            ('상품성(40)', 40, [s[2] for s in d['scores']]),
            ('종합평점(100)', 100, totals)]
    x0, full = 254, 841
    y = 150
    for label, mx, vals in cats:
        txt(ax, 46, y + 18, label, 24, True)
        for i, v in enumerate(vals):
            by = y + i * 36
            ax.add_patch(Rectangle((x0, by), full * v / mx, 28, fc=SERIES_FILL[i], ec='#333333', lw=1.6))
            txt(ax, x0 + full * v / mx + 12, by + 14, str(v), 21, True)
        y += 150
    fig.savefig(path, facecolor='white'); plt.close(fig)


# ------------------------------------------------------------------ 차트 B
def chart_b(path, d):
    W, H = 960, 490
    fig, ax = _canvas(W, H)
    tp = d.get('type', '84㎡')
    txt(ax, 34, 36, f'{tp} 적정가격과 분양가 (억원)', 22, True)
    rows = []
    for nm, v in zip(d['comp_names'], d['comp_adjusted']):
        rows.append((f'{nm} 보정가격', v, '#999999', '#222222'))
    rows.append(('브동산 분석 적정가격 (평균)', d['fair'], '#000000', '#000000'))
    has_actual = d.get('actual') is not None
    if has_actual:
        rows.append((f"실제 분양가 ({d.get('actual_label', tp + ' 가중평균')})", d['actual'], '#FFFFFF', '#222222'))
    mx = max(r[1] for r in rows)
    x0, wmax = 310, 520
    y = 98
    pitch = 78 if has_actual else 92
    for label, v, fc, ec in rows:
        txt(ax, 32, y, label, 15.5, False, '#111111')
        w = wmax * v / mx
        ax.add_patch(Rectangle((x0, y - 19), w, 38, fc=fc, ec=ec, lw=2))
        txt(ax, x0 + w + 10, y, f'{v:.2f}억', 20, True)
        y += pitch
    by0 = 402
    ax.add_patch(Rectangle((32, by0), 903, 68, fc='#F3F3F3', ec='#333333', lw=2))
    if has_actual:
        box = f"예상 프리미엄 {d['premium_text']} ({d['pct_text']})"
    else:
        box = f"브동산 분석 적정가격 {d['fair']:.2f}억원 (분양가 공개 후 프리미엄 산출)"
    txt(ax, 483, by0 + 34, box, 26, True, ha='center')
    fig.savefig(path, facecolor='white'); plt.close(fig)


# ------------------------------------------------------------------ 위치 개략도
def latlon_to_en(lat, lon, lat0, lon0):
    """위경도 -> (동쪽 m, 북쪽 m), 기준점 lat0/lon0."""
    return ((lon - lon0) * 111320 * math.cos(math.radians(lat0)), (lat - lat0) * 110574)


def chart_map(path, d):
    """d = {
      'note': '좌상단 안내문(줄바꿈 \\n)',
      'site': {'name':'광교 자연앤 센트레빌','sub':'광교 A17블록, 원천동 633 일원, 600세대','en':(0,0)},
      'comps': [{'name':'광교호반베르디움','sub':'비교단지1 · 원천동(2014.06)','en':(x,y)}, ...],
      'stations': [{'name':'광교중앙역(신분당선)','en':(x,y),'line_to_site':'직선 약 1.36km'},   # line_to_site: 점선+거리 라벨
                   {'name':'원천역(인덕원~동탄선, 예정)','en':(x,y)}],
      'schools': [{'name':'매원초','en':(x,y)}],
      'facilities': [{'name':'아주대병원','en':(x,y)}],
      'areas': [{'name':'원천호수\\n(광교호수공원)','en':(x,y),'rx':m,'ry':m}],   # 호수·공원 등(타원)
      'legend': '■ 검정=SITE · □(회색 테두리)=비교단지 · □(점선 테두리)=학교 · ●(검정)=지하철역 · ●(회색)=생활시설'
    }
    en = 임의 기준(m) 동쪽·북쪽 좌표. 위경도는 latlon_to_en 으로 변환. 'px':(x,y) 를 주면 픽셀 좌표를 직접 지정한다.
    """
    W, H = 967, 695
    fig, ax = _canvas(W, H)
    ents = []  # (kind, dict)
    ents.append(('site', d['site']))
    for k, key in (('comp', 'comps'), ('station', 'stations'), ('school', 'schools'), ('fac', 'facilities')):
        for e in d.get(key, []):
            ents.append((k, e))
    areas = d.get('areas', [])
    # --- 좌표 -> 픽셀 (종횡비 유지, 실제 위치 관계를 최대한 보존)
    pts = [e['en'] for _, e in ents if 'en' in e] + [a['en'] for a in areas if 'en' in a]
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    L, R, T, B = 150, 800, 170, 600
    spanx = max(max(xs) - min(xs), 1); spany = max(max(ys) - min(ys), 1)
    s = min((R - L) / spanx, (B - T) / spany)
    cx = (min(xs) + max(xs)) / 2; cy = (min(ys) + max(ys)) / 2
    mid = ((L + R) / 2, (T + B) / 2)

    def P(en):
        return (mid[0] + (en[0] - cx) * s, mid[1] - (en[1] - cy) * s)
    for _, e in ents:
        e['_p'] = tuple(e['px']) if 'px' in e else P(e['en'])
    # --- 마커 간 최소 간격 확보(반복 밀어내기)
    mk = [e for _, e in ents]
    for _ in range(60):
        moved = False
        for i in range(len(mk)):
            for j in range(i + 1, len(mk)):
                if 'px' in mk[i] and 'px' in mk[j]:
                    continue
                ax_, ay_ = mk[i]['_p']; bx, by = mk[j]['_p']
                dx, dy = bx - ax_, by - ay_
                dist = math.hypot(dx, dy)
                if dist < 70:
                    if dist < 1e-6:
                        dx, dy, dist = 1.0, 0.0, 1.0
                    push = (70 - dist) / 2
                    ux, uy = dx / dist, dy / dist
                    if 'px' not in mk[i]:
                        mk[i]['_p'] = (ax_ - ux * push, ay_ - uy * push)
                    if 'px' not in mk[j]:
                        mk[j]['_p'] = (bx + ux * push, by + uy * push)
                    moved = True
        if not moved:
            break
    for _, e in ents:
        x, y = e['_p']
        e['_p'] = (min(max(x, 60), W - 60), min(max(y, 140), H - 75))
    # --- 호수/공원 타원
    for a in areas:
        p = tuple(a['px']) if 'px' in a else P(a['en'])
        rx = a.get('rx_px') or a.get('rx', 200) * s
        ry = a.get('ry_px') or a.get('ry', 280) * s
        ax.add_patch(Ellipse(p, 2 * rx, 2 * ry, fc='#EDEDED', ec='#DDDDDD', lw=1.5, zorder=0))
        txt(ax, p[0], p[1], a['name'], 17, False, '#888888', ha='center', linespacing=1.4)
    # --- 점선(SITE -> 대표 역)
    sx, sy = d['site']['_p']
    for e in d.get('stations', []):
        if e.get('line_to_site'):
            x, y = e['_p']
            ax.plot([x, sx], [y, sy], color='#BBBBBB', lw=1.6, ls=(0, (4, 3)), zorder=1)
            ax.text((x + sx) / 2 + 12, (y + sy) / 2, e['line_to_site'], fontproperties=FP, fontsize=px2pt(16),
                    color='#888888', ha='left', va='center')
    # --- 마커 + 라벨(겹치지 않는 방향 선택)
    fig.canvas.draw()
    rend = fig.canvas.get_renderer()
    placed = []

    def bbox_of(t):
        bb = t.get_window_extent(rend)
        return (bb.x0, H - bb.y1, bb.x1, H - bb.y0)

    def overlap(a, b, pad=4):
        return not (a[2] + pad < b[0] or b[2] + pad < a[0] or a[3] + pad < b[1] or b[3] + pad < a[1])

    # 마커 bbox 선등록
    msz = {'site': 40, 'comp': 32, 'station': 16, 'school': 28, 'fac': 12}
    for k, e in ents:
        x, y = e['_p']; h = msz[k] / 2 + 3
        placed.append((x - h, y - h, x + h, y + h))
    order = {'site': 0, 'comp': 1, 'station': 2, 'school': 3, 'fac': 4}
    for k, e in sorted(ents, key=lambda t: order[t[0]]):
        x, y = e['_p']
        h = msz[k] / 2
        if k == 'site':
            ax.add_patch(Rectangle((x - h, y - h), 2 * h, 2 * h, fc='#000000', ec='#000000', zorder=3))
        elif k == 'comp':
            ax.add_patch(Rectangle((x - h + 2, y - h + 2), 2 * h - 4, 2 * h - 4, fc='white', ec='#555555', lw=3.4, zorder=3))
        elif k == 'station':
            ax.add_patch(plt.Circle((x, y), 7, fc='#000000', ec='#000000', zorder=3))
        elif k == 'school':
            ax.add_patch(Rectangle((x - h + 3, y - h + 3), 2 * h - 6, 2 * h - 6, fc='white', ec='#000000', lw=2.4,
                                   ls=(0, (1, 1.2)), zorder=3))
        else:
            ax.add_patch(plt.Circle((x, y), 5.5, fc='#888888', ec='#888888', zorder=3))
        px_main = {'site': 21, 'comp': 20, 'station': 19, 'school': 17.5, 'fac': 16.5}[k]
        col_main = {'fac': '#888888'}.get(k, '#000000')
        sub = e.get('sub')
        cands = []
        gap = h + 12
        for side in (e.get('side') and [e['side']] or []) + ['right', 'left', 'below', 'above']:
            cands.append(side)
        for side in cands:
            if side == 'right':
                tx, ha, ty = x + gap, 'left', y
            elif side == 'left':
                tx, ha, ty = x - gap, 'right', y
            elif side == 'below':
                tx, ha, ty = x, 'center', y + h + 20
            else:
                tx, ha, ty = x, 'center', y - h - 20 - (22 if sub else 0)
            mt = ax.text(tx, ty - (6 if sub else 0), e['name'], fontproperties=FP, fontsize=px2pt(px_main), color=col_main,
                         ha=ha, va='center', zorder=4)
            if k == 'site':
                mt.set_path_effects([pe.withStroke(linewidth=1.0, foreground=col_main)])
            bbs = [bbox_of(mt)]
            st = None
            if sub:
                st = ax.text(tx, ty + 17, sub, fontproperties=FP, fontsize=px2pt(16), color='#888888', ha=ha, va='center', zorder=4)
                bbs.append(bbox_of(st))
            ok = all(0 <= b[0] and b[2] <= W and 0 <= b[1] and b[3] <= H for b in bbs) and \
                all(not overlap(b, p) for b in bbs for p in placed)
            if ok or side == cands[-1]:
                placed.extend(bbs)
                break
            mt.remove()
            if st is not None:
                st.remove()
    # --- 안내 박스 / N / 범례
    note = d.get('note')
    if note:
        ax.add_patch(Rectangle((30, 22), 521, 81, fc='white', ec='#DDDDDD', lw=1.4, zorder=5))
        txt(ax, 42, 63, note, 15.5, False, '#555555', va='center', linespacing=1.45, zorder=6)
    ax.annotate('', xy=(921, 28), xytext=(921, 70), arrowprops=dict(arrowstyle='-|>', color='#000000', lw=2), zorder=5)
    txt(ax, 921, 100, 'N', 16, False, '#555555', ha='center')
    txt(ax, 30, 683, d.get('legend', '■ 검정=SITE · □(회색 테두리)=비교단지 · □(점선 테두리)=학교 · ●(검정)=지하철역 · ●(회색)=생활시설'),
        15.5, False, '#555555')
    fig.savefig(path, facecolor='white'); plt.close(fig)


# ------------------------------------------------------------------ 청약 일정 타임라인
def chart_c(path, d):
    ev = d['events']
    W, H = 960, 330
    fig, ax = _canvas(W, H)
    txt(ax, 34, 38, '청약 일정', 22, True)
    txt(ax, 926, 40, d.get('note', ''), 14, False, '#777777', ha='right')
    x0, x1, ly = 120, 840, 170
    ax.plot([x0, x1], [ly, ly], color='#DDDDDD', lw=3, zorder=1)
    ax.plot([x0 + 70, x1], [ly, ly], color='#111111', lw=3, zorder=1)
    step = (x1 - x0) / max(len(ev) - 1, 1)
    for i, (dt, nm, filled) in enumerate(ev):
        x = x0 + i * step
        ax.scatter([x], [ly], s=260, zorder=3, facecolor='#111111' if filled else 'white', edgecolor='#111111', linewidth=2)
        txt(ax, x, ly - 58, dt, 24, True, ha='center')
        txt(ax, x, ly + 56, nm, 16, False, '#555555', ha='center')
    txt(ax, 34, H - 26, d.get('footer', ''), 14, False, '#777777')
    fig.savefig(path, facecolor='white'); plt.close(fig)


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else '.'
    os.makedirs(out, exist_ok=True)
    # 광교 자연앤 센트레빌 승인 샘플 재현(검증용)
    chart_a(os.path.join(out, 'demo-a.png'), {
        'names': ['SITE · 광교 자연앤 센트레빌', '광교호반베르디움', '광교더샵'],
        'scores': [[13, 12, 25], [17, 12, 29], [17, 20, 29]]})
    chart_b(os.path.join(out, 'demo-b.png'), {
        'type': '84㎡', 'comp_names': ['광교호반베르디움', '광교더샵'], 'comp_adjusted': [15.49, 14.27],
        'fair': 14.88, 'actual': 9.37, 'premium_text': '+5.52억원', 'pct_text': '약 59% 저평가'})
    chart_map(os.path.join(out, 'demo-map.png'), {
        'note': '광교중앙역 거리는 분양 정보 사이트의 카카오맵 좌표 기준 직선거리이고,\n나머지는 공식 위치도·주소로 어림한 상대 위치다(실제 지도·축척 아님).\n원천역은 예정 노선이라 점수에 반영하지 않았다.',
        'site': {'name': 'SITE · 광교 자연앤 센트레빌', 'sub': '(광교 A17블록, 원천동 633 일원, 600세대)', 'en': (0, 0)},
        'comps': [{'name': '광교호반베르디움', 'sub': '비교단지1 · 원천동(2014.06)', 'en': (520, -760)},
                  {'name': '광교더샵', 'sub': '비교단지2 · 원천동(2018.08)', 'en': (230, -700)}],
        'stations': [{'name': '광교중앙역(신분당선)', 'en': (150, 900), 'line_to_site': '직선 약 1.36km'},
                     {'name': '원천역(인덕원~동탄선, 예정)', 'en': (200, -920)}],
        'schools': [{'name': '소화초(사립)', 'en': (-420, 330)}, {'name': '매원초', 'en': (440, -450)}],
        'facilities': [{'name': '아주대병원', 'en': (-560, 600)}, {'name': '갤러리아백화점·롯데몰', 'en': (830, 700)}],
        'areas': [{'name': '원천호수\n(광교호수공원)', 'en': (1300, 250), 'rx': 270, 'ry': 380}]})
    print('done', out)
