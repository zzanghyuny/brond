#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""브동산 네이버 발행본 차트 생성기 — 폰(모바일) 폭 기준 (2026.11.14). 형태는 2026.11.09 Paul 승인 샘플 '광교 자연앤 센트레빌'과 같다.

  모바일 규칙: 캔버스 폭 1000px(네이버가 폰에서 약 390px로 줄여 보여줌) → 이미지 안 모든 글씨 28px 이상(폰에서 약 11px),
  값 32px 이상, 제목 36px 이상. 막대 차트는 항목 이름을 막대 위에 두고 범례는 세로로 쌓는다. 모든 함수는 mobile=True 기본이며
  mobile=False 면 예전 데스크톱 레이아웃(_chart_*_desktop)을 쓴다.

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


def _chart_a_desktop(path, d):
    W, H = 1366, 770
    fig, ax = _canvas(W, H)
    txt(ax, 46, 47, d.get('title', '평점 비교 · 입지 · 브랜드 · 상품성 (100점 만점)'), 29, True)
    names = d['names']
    n = len(names)
    lx = [46, 466, 886][:n]
    for i, (x, nm) in enumerate(zip(lx, names)):
        ax.add_patch(Rectangle((x, 87), 22, 22, fc=SERIES_FILL[i], ec='#333333', lw=1.4))
        txt(ax, x + 34, 98, nm, min(20, 372.0 / max(len(nm), 1)), False, '#111111')
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
def _chart_b_desktop(path, d):
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
        txt(ax, 32, y, label, min(15.5, 268.0 / max(len(label), 1)), False, '#111111')
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


def _chart_map_desktop(path, d):
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
    if not pts:
        pts = [(0, 0), (1, 1)]
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    L, R, T, B = 150, 800, 205, 600
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
    # --- 점선(SITE -> 대표 역) — 거리 라벨은 라벨 배치 뒤에 둔다
    sx, sy = d['site']['_p']
    for e in d.get('stations', []):
        if e.get('line_to_site'):
            x, y = e['_p']
            ax.plot([x, sx], [y, sy], color='#BBBBBB', lw=1.6, ls=(0, (4, 3)), zorder=1)
    # --- 마커 + 라벨(겹치지 않는 방향 선택)
    fig.canvas.draw()
    rend = fig.canvas.get_renderer()
    placed = []

    def bbox_of(t):
        bb = t.get_window_extent(rend)
        return (bb.x0, H - bb.y1, bb.x1, H - bb.y0)

    def overlap(a, b, pad=4):
        return not (a[2] + pad < b[0] or b[2] + pad < a[0] or a[3] + pad < b[1] or b[3] + pad < a[1])

    placed.append((30, 22, 551, 103)); placed.append((900, 20, 945, 112)); placed.append((26, 665, 940, 695))
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
    for e in d.get('stations', []):
        if e.get('line_to_site'):
            x, y = e['_p']; mx, my = (x + sx) / 2, (y + sy) / 2
            for ox, oy, ha in ((14, 0, 'left'), (14, 24, 'left'), (-14, 0, 'right'), (-14, 24, 'right'), (14, -24, 'left'), (0, 34, 'center'), (0, -34, 'center')):
                t = ax.text(mx + ox, my + oy, e['line_to_site'], fontproperties=FP, fontsize=px2pt(16), color='#888888', ha=ha, va='center', zorder=4)
                bb = bbox_of(t)
                if all(not overlap(bb, p) for p in placed) and 0 <= bb[0] and bb[2] <= W:
                    placed.append(bb); break
                t.remove()
    # --- 안내 박스 / N / 범례
    note = d.get('note')
    if note:
        nt = txt(ax, 42, 63, note, 15.5, False, '#555555', va='center', linespacing=1.45, zorder=6)
        fig.canvas.draw()
        bb = nt.get_window_extent(fig.canvas.get_renderer())
        nw = max(521, bb.width + 26)
        nh = max(81, bb.height + 24)
        ax.add_patch(Rectangle((30, 22), nw, nh, fc='white', ec='#DDDDDD', lw=1.4, zorder=5))
        nt.set_position((42, 22 + nh / 2))
    ax.annotate('', xy=(921, 28), xytext=(921, 70), arrowprops=dict(arrowstyle='-|>', color='#000000', lw=2), zorder=5)
    txt(ax, 921, 100, 'N', 16, False, '#555555', ha='center')
    txt(ax, 30, 683, d.get('legend', '■ 검정=SITE · □(회색 테두리)=비교단지 · □(점선 테두리)=학교 · ●(검정)=지하철역 · ●(회색)=생활시설'),
        15.5, False, '#555555')
    fig.savefig(path, facecolor='white'); plt.close(fig)


# ------------------------------------------------------------------ 청약 일정 타임라인
def _chart_c_desktop(path, d):
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



# =====================================================================================
# 모바일(폰 폭) 버전 — 2026.11.14. 캔버스 폭 1000px, 글씨 28px 이상. 기본값(mobile=True)이 이쪽이다.
# =====================================================================================
MW = 1000
M_MIN = 28          # 이미지 안 최소 글씨(px)
M_VAL = 32          # 값 글씨
M_TITLE = 36        # 제목


def _est_w(s, px):
    return sum(px * (1.0 if ord(c) > 0x2E80 or c in '·■□●' else 0.56) for c in s)


def _wrap(s, px, maxw):
    """글자 폭을 어림해 줄바꿈한다. 기존 \\n 은 유지."""
    out = []
    for para in s.split('\n'):
        cur = ''
        for ch in para:
            if _est_w(cur + ch, px) > maxw and cur:
                out.append(cur); cur = ch
            else:
                cur += ch
        out.append(cur)
    return out


def chart_a(path, d, mobile=True):
    if not mobile:
        return _chart_a_desktop(path, d)
    W = MW
    names, scores = d['names'], d['scores']
    title = d.get('title', '평점 비교 (입지·브랜드·상품성, 100점)')
    tl = _wrap(title, M_TITLE, W - 80)
    n = len(names)
    top = 30 + len(tl) * 50
    leg_y0 = top + 20
    cats = [('입지(40)', 40, [s[0] for s in scores]), ('브랜드(20)', 20, [s[1] for s in scores]),
            ('상품성(40)', 40, [s[2] for s in scores]), ('종합평점(100)', 100, [sum(s) for s in scores])]
    y0 = leg_y0 + n * 46 + 34
    gh = 50 + n * 54 + 36
    H = int(y0 + gh * len(cats) + 10)
    fig, ax = _canvas(W, H)
    for i, t in enumerate(tl):
        txt(ax, 40, 48 + i * 50, t, M_TITLE, True)
    for i, nm in enumerate(names):
        y = leg_y0 + 20 + i * 46
        ax.add_patch(Rectangle((40, y - 15), 30, 30, fc=SERIES_FILL[i], ec='#333333', lw=2))
        txt(ax, 86, y, nm, M_MIN + 2 if _est_w(nm, M_MIN + 2) < W - 130 else M_MIN, False, '#111111')
    x0, full = 40, 780
    y = y0
    for label, mx, vals in cats:
        txt(ax, 40, y + 18, label, 32, True)
        for i, v in enumerate(vals):
            by = y + 46 + i * 54
            w = full * v / mx
            ax.add_patch(Rectangle((x0, by), w, 42, fc=SERIES_FILL[i], ec='#333333', lw=2))
            txt(ax, x0 + w + 14, by + 21, str(v), M_VAL, True)
        y += gh
    fig.savefig(path, facecolor='white'); plt.close(fig)


def chart_b(path, d, mobile=True):
    if not mobile:
        return _chart_b_desktop(path, d)
    W = MW
    tp = d.get('type', '84㎡')
    has_actual = d.get('actual') is not None
    rows = [(f'{nm} 보정가격', v, '#999999', '#222222') for nm, v in zip(d['comp_names'], d['comp_adjusted'])]
    rows.append(('브동산 분석 적정가격 (평균)', d['fair'], '#000000', '#000000'))
    if has_actual:
        rows.append((f"실제 분양가 ({d.get('actual_label', tp + ' 가중평균')})", d['actual'], '#FFFFFF', '#222222'))
    title = f'{tp} 적정가격과 분양가 (억원)'
    tl = _wrap(title, M_TITLE, W - 80)
    ytop = 30 + len(tl) * 50 + 20
    pitch = 118
    box_h = 170
    H = int(ytop + pitch * len(rows) + 30 + box_h + 30)
    fig, ax = _canvas(W, H)
    for i, t in enumerate(tl):
        txt(ax, 40, 48 + i * 50, t, M_TITLE, True)
    mx = max(r[1] for r in rows)
    x0, wmax = 40, 740
    y = ytop
    for label, v, fc, ec in rows:
        txt(ax, 40, y + 14, label, M_MIN + 2 if _est_w(label, M_MIN + 2) < W - 80 else M_MIN, False, '#111111')
        w = wmax * v / mx
        ax.add_patch(Rectangle((x0, y + 40), w, 56, fc=fc, ec=ec, lw=2.5))
        txt(ax, x0 + w + 14, y + 68, f'{v:.2f}억', 36, True)
        y += pitch
    by0 = y + 10
    ax.add_patch(Rectangle((40, by0), W - 80, box_h, fc='#F3F3F3', ec='#333333', lw=2.5))
    if has_actual:
        txt(ax, W / 2, by0 + 52, '예상 프리미엄', 32, False, '#333333', ha='center')
        txt(ax, W / 2, by0 + 118, f"{d['premium_text']} ({d['pct_text']})", 44 if _est_w(f"{d['premium_text']} ({d['pct_text']})", 44) < W - 120 else 38, True, ha='center')
    else:
        txt(ax, W / 2, by0 + 52, f"브동산 분석 적정가격 {d['fair']:.2f}억원", 36, True, ha='center')
        txt(ax, W / 2, by0 + 118, '분양가 공개 후 프리미엄을 산출', 30, False, '#333333', ha='center')
    fig.savefig(path, facecolor='white'); plt.close(fig)


def chart_c(path, d, mobile=True):
    """청약 일정 — 모바일은 세로 타임라인. d={'events':[(날짜,이름,filled)], 'note':..., 'footer':...}"""
    if not mobile:
        return _chart_c_desktop(path, d)
    W = MW
    ev = d['events']
    note = d.get('note', '')
    nl = _wrap(note, M_MIN, W - 80) if note else []
    foot = _wrap(d.get('footer', ''), 26, W - 80) if d.get('footer') else []
    ytop = 30 + 50 + len(nl) * 38 + 20
    pitch = 100
    H = int(ytop + pitch * len(ev) + len(foot) * 36 + 50)
    fig, ax = _canvas(W, H)
    txt(ax, 40, 48, '청약 일정', M_TITLE, True)
    for i, t in enumerate(nl):
        txt(ax, 40, 100 + i * 38, t, M_MIN, False, '#555555')
    lx = 80
    ax.plot([lx, lx], [ytop + 30, ytop + pitch * (len(ev) - 1) + 30], color='#222222', lw=4, zorder=1)
    for i, (dt, nm, filled) in enumerate(ev):
        y = ytop + 30 + i * pitch
        ax.scatter([lx], [y], s=520, zorder=3, facecolor='#111111' if filled else 'white', edgecolor='#111111', linewidth=3)
        txt(ax, 140, y, dt, 38, True)
        txt(ax, 140 + _est_w(dt, 38) + 30, y, nm, 32, False, '#333333')
    for i, t in enumerate(foot):
        txt(ax, 40, H - 40 - (len(foot) - 1 - i) * 36, t, 26, False, '#555555')
    fig.savefig(path, facecolor='white'); plt.close(fig)


def chart_map(path, d, mobile=True):
    """위치 개략도(폰용 1000×1000). 데이터 형식은 _chart_map_desktop 독스트링과 같다.
    d = {'note','site','comps','stations','schools','facilities','areas','legend'}. 라벨 개체는 최대 8개(SITE, 비교단지, 역, 학교, 생활시설 순으로 남김)."""
    if not mobile:
        return _chart_map_desktop(path, d)
    W = H = MW
    fig, ax = _canvas(W, H)
    ents = [('site', d['site'])]
    for k, key in (('comp', 'comps'), ('station', 'stations'), ('school', 'schools'), ('fac', 'facilities')):
        ents += [(k, e) for e in d.get(key, [])]
    if len(ents) > 8:
        print(f'[chart_map] 라벨 개체 {len(ents)}개 → 8개만 표시(앞에서부터)')
        ents = ents[:8]
    stations = [e for k, e in ents if k == 'station']
    areas = d.get('areas', [])
    # --- 안내 박스 / 범례 크기
    note = d.get('note') or ''
    nlines = _wrap(note, 26, 820) if note else []
    note_w = (max(_est_w(t, 26) for t in nlines) + 40) if nlines else 0
    note_h = len(nlines) * 38 + 26 if nlines else 0
    legend = d.get('legend', '■ 검정=SITE · □(회색 테두리)=비교단지 · □(점선 테두리)=학교 · ●(검정)=지하철역 · ●(회색)=생활시설')
    llines = _wrap(legend, 26, W - 60)
    leg_h = len(llines) * 36 + 24
    T = 24 + note_h + 110 if note_h else 130
    B = H - leg_h - 110
    L, R = 130, 870
    # --- 좌표 -> 픽셀
    pts = [e['en'] for _, e in ents if 'en' in e] + [a['en'] for a in areas if 'en' in a]
    pts = pts or [(0, 0), (1, 1)]
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    spanx = max(max(xs) - min(xs), 1); spany = max(max(ys) - min(ys), 1)
    s = min((R - L) / spanx, (B - T) / spany)
    cx = (min(xs) + max(xs)) / 2; cy = (min(ys) + max(ys)) / 2
    mid = ((L + R) / 2, (T + B) / 2)
    P = lambda en: (mid[0] + (en[0] - cx) * s, mid[1] - (en[1] - cy) * s)
    for _, e in ents:
        e['_p'] = tuple(e['px']) if 'px' in e else P(e['en'])
    mk = [e for _, e in ents]
    for _ in range(80):
        moved = False
        for i in range(len(mk)):
            for j in range(i + 1, len(mk)):
                if 'px' in mk[i] and 'px' in mk[j]:
                    continue
                ax_, ay_ = mk[i]['_p']; bx, by = mk[j]['_p']
                dx, dy = bx - ax_, by - ay_
                dist = math.hypot(dx, dy)
                if dist < 110:
                    if dist < 1e-6:
                        dx, dy, dist = 1.0, 0.0, 1.0
                    push = (110 - dist) / 2
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
        e['_p'] = (min(max(x, 70), W - 70), min(max(y, T), B))
    # --- 호수/공원
    for a in areas:
        p = tuple(a['px']) if 'px' in a else P(a['en'])
        rx = a.get('rx_px') or a.get('rx', 200) * s
        ry = a.get('ry_px') or a.get('ry', 280) * s
        ax.add_patch(Ellipse(p, 2 * rx, 2 * ry, fc='#EDEDED', ec='#DDDDDD', lw=2, zorder=0))
        txt(ax, p[0], p[1], a['name'], M_MIN, False, '#888888', ha='center', linespacing=1.4)
    sx, sy = d['site']['_p']
    for e in stations:
        if e.get('line_to_site'):
            x, y = e['_p']
            ax.plot([x, sx], [y, sy], color='#AAAAAA', lw=2.4, ls=(0, (4, 3)), zorder=1)
    # --- 라벨 배치(점수 방식: 겹침·화면 밖 최소)
    fig.canvas.draw()
    rend = fig.canvas.get_renderer()
    placed = []

    def bbox_of(t):
        bb = t.get_window_extent(rend)
        return (bb.x0, H - bb.y1, bb.x1, H - bb.y0)

    def ov(a, b, pad=6):
        return not (a[2] + pad < b[0] or b[2] + pad < a[0] or a[3] + pad < b[1] or b[3] + pad < a[1])

    if nlines:
        placed.append((24, 24, 24 + note_w, 24 + note_h))
    placed.append((W - 110, 20, W - 10, 150))
    placed.append((0, H - leg_h - 4, W, H))
    msz = {'site': 56, 'comp': 46, 'station': 24, 'school': 40, 'fac': 20}
    for k, e in ents:
        x, y = e['_p']; hh = msz[k] / 2 + 4
        placed.append((x - hh, y - hh, x + hh, y + hh))
    fs = {'site': 32, 'comp': 30, 'station': 30, 'school': 28, 'fac': 28}
    order = {'site': 0, 'comp': 1, 'station': 2, 'school': 3, 'fac': 4}
    for k, e in sorted(ents, key=lambda t: order[t[0]]):
        x, y = e['_p']; hh = msz[k] / 2
        if k == 'site':
            ax.add_patch(Rectangle((x - hh, y - hh), 2 * hh, 2 * hh, fc='#000000', ec='#000000', zorder=3))
        elif k == 'comp':
            ax.add_patch(Rectangle((x - hh + 3, y - hh + 3), 2 * hh - 6, 2 * hh - 6, fc='white', ec='#555555', lw=5, zorder=3))
        elif k == 'station':
            ax.add_patch(plt.Circle((x, y), 12, fc='#000000', ec='#000000', zorder=3))
        elif k == 'school':
            ax.add_patch(Rectangle((x - hh + 4, y - hh + 4), 2 * hh - 8, 2 * hh - 8, fc='white', ec='#000000', lw=3.4,
                                   ls=(0, (1, 1.2)), zorder=3))
        else:
            ax.add_patch(plt.Circle((x, y), 9, fc='#888888', ec='#888888', zorder=3))
        col = '#888888' if k == 'fac' else '#000000'
        sub = e.get('sub')
        gap = hh + 14
        best = None
        sides = ([e['side']] if e.get('side') else []) + ['right', 'left', 'below', 'above']
        for idx, side in enumerate(sides):
            if side == 'right':
                tx, ha, ty = x + gap, 'left', y
            elif side == 'left':
                tx, ha, ty = x - gap, 'right', y
            elif side == 'below':
                tx, ha, ty = x, 'center', y + hh + 28
            else:
                tx, ha, ty = x, 'center', y - hh - 28 - (38 if sub else 0)
            mt = ax.text(tx, ty - (10 if sub else 0), e['name'], fontproperties=FP, fontsize=px2pt(fs[k]), color=col,
                         ha=ha, va='center', zorder=4)
            bbs = [bbox_of(mt)]
            st = None
            if sub:
                st = ax.text(tx, ty + 24, sub, fontproperties=FP, fontsize=px2pt(M_MIN), color='#777777', ha=ha, va='center', zorder=4)
                bbs.append(bbox_of(st))
            score = idx
            for b in bbs:
                if not (6 <= b[0] and b[2] <= W - 6 and 6 <= b[1] and b[3] <= H - 6):
                    score += 5000
                score += 1000 * sum(1 for p in placed if ov(b, p))
            mt.remove()
            if st is not None:
                st.remove()
            if best is None or score < best[0]:
                best = (score, tx, ha, ty, bbs)
        _, tx, ha, ty, bbs = best
        mt = ax.text(tx, ty - (10 if sub else 0), e['name'], fontproperties=FP, fontsize=px2pt(fs[k]), color=col,
                     ha=ha, va='center', zorder=4)
        if k == 'site':
            mt.set_path_effects([pe.withStroke(linewidth=1.4, foreground=col)])
        if sub:
            ax.text(tx, ty + 24, sub, fontproperties=FP, fontsize=px2pt(M_MIN), color='#777777', ha=ha, va='center', zorder=4)
        placed.extend(bbs)
    for e in stations:
        if e.get('line_to_site'):
            x, y = e['_p']; mx_, my_ = (x + sx) / 2, (y + sy) / 2
            cand = ((16, 0, 'left'), (16, 40, 'left'), (-16, 0, 'right'), (-16, 40, 'right'), (16, -40, 'left'),
                    (-16, -40, 'right'), (0, 50, 'center'), (0, -50, 'center'))
            bestd = None
            for oi, (ox, oy, ha) in enumerate(cand):
                t = ax.text(mx_ + ox, my_ + oy, e['line_to_site'], fontproperties=FP, fontsize=px2pt(M_MIN), color='#777777', ha=ha, va='center', zorder=4)
                b = bbox_of(t); t.remove()
                sc = oi + (5000 if not (6 <= b[0] and b[2] <= W - 6) else 0) + 1000 * sum(1 for p in placed if ov(b, p))
                if bestd is None or sc < bestd[0]:
                    bestd = (sc, ox, oy, ha, b)
            _, ox, oy, ha, b = bestd
            ax.text(mx_ + ox, my_ + oy, e['line_to_site'], fontproperties=FP, fontsize=px2pt(M_MIN), color='#777777', ha=ha, va='center', zorder=4)
            placed.append(b)
    # --- 안내 박스 / N / 범례
    if nlines:
        ax.add_patch(Rectangle((24, 24), note_w, note_h, fc='white', ec='#CCCCCC', lw=2, zorder=5))
        for i, t in enumerate(nlines):
            txt(ax, 44, 24 + 13 + 19 + i * 38, t, 26, False, '#444444', zorder=6)
    ax.annotate('', xy=(W - 60, 30), xytext=(W - 60, 100), arrowprops=dict(arrowstyle='-|>', color='#000000', lw=3), zorder=5)
    txt(ax, W - 60, 130, 'N', 30, True, '#333333', ha='center')
    for i, t in enumerate(llines):
        txt(ax, 30, H - leg_h + 28 + i * 36, t, 26, False, '#555555')
    fig.savefig(path, facecolor='white'); plt.close(fig)


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else '.'
    os.makedirs(out, exist_ok=True)
    # 광교 자연앤 센트레빌 승인 샘플 재현(검증용) — 모바일 버전
    chart_a(os.path.join(out, 'chart-a-score.png'), {
        'names': ['SITE · 광교 자연앤 센트레빌', '광교호반베르디움', '광교더샵'],
        'scores': [[13, 12, 25], [17, 12, 29], [17, 20, 29]]})
    chart_b(os.path.join(out, 'chart-b-price.png'), {
        'type': '84㎡', 'comp_names': ['광교호반베르디움', '광교더샵'], 'comp_adjusted': [15.49, 14.27],
        'fair': 14.88, 'actual': 9.37, 'premium_text': '+5.52억원', 'pct_text': '약 59% 저평가'})
    chart_map(os.path.join(out, 'chart-map-naver.png'), {
        'note': '광교중앙역 거리는 카카오맵 좌표 기준 직선거리이고,\n나머지는 공식 위치도·주소로 어림한 상대 위치다.\n원천역은 예정 노선이라 점수에 반영하지 않았다.',
        'site': {'name': 'SITE · 광교 자연앤 센트레빌', 'sub': '광교 A17블록 · 600세대', 'en': (0, 0)},
        'comps': [{'name': '광교호반베르디움', 'sub': '비교단지1 · 2014.06', 'en': (520, -760)},
                  {'name': '광교더샵', 'sub': '비교단지2 · 2018.08', 'en': (230, -700)}],
        'stations': [{'name': '광교중앙역(신분당선)', 'en': (150, 900), 'line_to_site': '직선 약 1.36km'},
                     {'name': '원천역(예정)', 'en': (200, -920)}],
        'schools': [{'name': '소화초(사립)', 'en': (-420, 330)}, {'name': '매원초', 'en': (440, -450)}],
        'facilities': [{'name': '아주대병원', 'en': (-560, 600)}],
        'areas': [{'name': '원천호수\n(광교호수공원)', 'en': (1300, 250), 'rx': 270, 'ry': 380}]})
    chart_c(os.path.join(out, 'chart-c-schedule.png'), {
        'note': '입주자모집공고 2026.10.30 기준 · 84㎡ 공공분양',
        'events': [('10.30', '입주자모집공고', False), ('11.09', '특별공급', True), ('11.10', '1순위', True),
                   ('11.11', '2순위', True), ('11.17', '당첨자 발표', True)],
        'footer': '접수 시간·자격 요건은 입주자모집공고문에서 반드시 확인한다.'})
    print('done', out)
