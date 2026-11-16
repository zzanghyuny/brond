# -*- coding: utf-8 -*-
"""랭킹 회차 데이터 로더 — 글·차트·영상 생성기가 같이 쓴다.

환경변수 RID가 없으면 수도권판(result2.json + texts2.py), 있으면 regions/<RID>.json + regions/<RID>-result.json.
제공: D(결과, 순위순), T(key→[설명, 한줄평]), META, LABEL, AREAS, N, NP/B1/B2/B3, SLUG, RANK_DATE, D_DOT, D_SP, D_KO, D_MD,
      IMGJ(key→{aerial,location}), SERIES_NO, HOOK, HOOK_N(네이버 제목용)
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
RID = os.environ.get('RID', '').strip()

if RID:
    _src = json.load(open(os.path.join(HERE, 'regions', f'{RID}.json'), encoding='utf-8'))
    D = json.load(open(os.path.join(HERE, 'regions', f'{RID}-result.json'), encoding='utf-8'))
    T = {k: v for k, v in _src.get('texts', {}).items()}
    META = _src.get('meta', {})
    LABEL = _src.get('label', RID); AREAS = _src.get('areas', LABEL)
    RANK_DATE = os.environ.get('RANK_DATE', _src.get('date', '2026-11-17'))
    SERIES_NO = META.get('series_no', 2)
else:
    D = json.load(open(os.path.join(HERE, 'result2.json'), encoding='utf-8'))
    import sys; sys.path.insert(0, HERE)
    from texts2 import T
    META = {
        'title_hook': '지금 해볼 만한 단지가 있을까?', 'title_hook_naver': '지금 해볼 만한 단지 있을까?',
        'groups': [['지금 볼 만한 곳', '시세 수준 + 입지 요건 좋음', ['오산헤리티지자이', '고촌센트럴자이', '상동역 롯데캐슬 시그니처', '시티오씨엘 9단지 오션파크뷰', '여주역 로제비앙 더센텀', '향남역 그로브 스위첸']],
                   ['조건 확인하면 기회', '페이백·할인 조건', ['힐스테이트 수원파크포레', '오목천역 더리브', '화서역 호수공원 아너스빌', '인하대역 수자인 로이센트']],
                   ['저층·타입이 열쇠', '층·타입별 가격 차 큼', ['힐스테이트 구월아트파크', '영종 디에트르 라 메르Ⅰ', '쌍용 더 플래티넘 한강']]],
        'risk_items': [['판촉 조건', '계약금 정액제·중도금 무이자·페이백이 붙으면 실제 부담은 표보다 낮아집니다'],
                       ['층·타입', '층·타입별 차이가 1억원 넘는 단지는 저층·다른 타입을 고르면 결과가 크게 달라집니다'],
                       ['수원파크포레', '113㎡ 10% 페이백이 84㎡에도 적용되면 +6.6%로 1위가 됩니다'],
                       ['비교 기준', '오남은 2009년식과 비교했고, 브레인시티 상한은 실거래가 아닌 호가 평균입니다']],
    }
    LABEL = '수도권'; AREAS = '서울·경기·인천'
    RANK_DATE = os.environ.get('RANK_DATE', '2026-11-16')
    SERIES_NO = 1

_y, _m, _d = [int(x) for x in RANK_DATE.split('-')]
if RID:
    SLUG = os.environ.get('RANK_SLUG', _src.get('slug') or f"{RID}-firstcome-{_y}{_m:02d}{_d:02d}")
else:
    SLUG = os.environ.get('RANK_SLUG', 'sudogwon-firstcome-top30-202611' if RANK_DATE == '2026-11-16' else f"sudogwon-firstcome-top30-{_y}{_m:02d}{_d:02d}")
D_DOT = f"{_y}.{_m:02d}.{_d:02d}"; D_SP = f"{_y}. {_m}. {_d}"; D_KO = f"{_y}년 {_m}월 {_d}일"; D_MD = f"{_m}월 {_d}일"

N = len(D)
NP = sum(1 for o in D if o['pct'] > 0)
B1 = sum(1 for o in D if -5 < o['pct'] <= 0)
B2 = sum(1 for o in D if -10 < o['pct'] <= -5)
B3 = sum(1 for o in D if o['pct'] <= -10)
HOOK = META.get('title_hook', '지금 해볼 만한 단지가 있을까?')
HOOK_N = META.get('title_hook_naver', HOOK)
IMG_DIR = os.path.join(ROOT, 'posts', 'images', SLUG) + '/'
_ij = os.path.join(IMG_DIR, 'images.json')
if os.path.exists(_ij):
    IMGJ = json.load(open(_ij, encoding='utf-8'))
elif not RID and os.path.exists(os.path.join(HERE, 'images.json')):
    IMGJ = json.load(open(os.path.join(HERE, 'images.json'), encoding='utf-8'))
else:
    IMGJ = {}

CYCLE = '보름마다' if (not RID or RID == 'sudogwon') else '매월'

def prev_result():
    """직전 회차 결과(history/<rid>/YYYY-MM-DD.json 중 이번 기준일보다 앞선 가장 최근 것) → (날짜, 리스트) 또는 (None, None)"""
    hd = os.path.join(HERE, 'history', RID or 'sudogwon')
    if not os.path.isdir(hd): return None, None
    xs = sorted(f for f in os.listdir(hd) if f.endswith('.json') and f[:10] < RANK_DATE)
    if not xs: return None, None
    return xs[-1][:10], json.load(open(os.path.join(hd, xs[-1]), encoding='utf-8'))

def fmt(v, unit=False):
    w = round(v * 1e4 / 10) * 10; s = '+' if w > 0 else '-' if w < 0 else '±'; a = abs(w)
    return f"{s}{a/10000:.2f}억{'원' if unit else ''}" if a >= 10000 else f"{s}{a:,}만{'원' if unit else ''}"
def pct(o): return f"{o['pct']:+.1f}%"
def segments():
    """카운트다운 구간 [(hi, lo)] — 큰 순위부터. TOP3는 따로."""
    segs = []; hi = N
    while hi > 3:
        lo = max(4, ((hi - 1) // 10) * 10 + 1) if hi > 10 else 4
        if hi > 10 and hi - lo < 2: lo = max(4, lo - 10)
        segs.append((hi, lo)); hi = lo - 1
    return segs
def seg_sub(hi, lo):
    xs = [o['pct'] for o in D if lo <= o['rank'] <= hi]
    return f"분양가 대비 {max(xs):+.1f}% ~ {min(xs):+.1f}%"
