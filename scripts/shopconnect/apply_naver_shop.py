#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""브동산 네이버 원고(naver-html/*.html)에 쇼핑커넥트 자리를 넣는다. (2026-11-26 Paul 지시, 항상 적용)

- 대상: naver_category가 부동산·부동산이야기·부동산정보인 청약·미분양 글 (공간·브랜드 글 제외)
- 글 맨 위(바이라인 바로 아래): 회색 작은 대가성 안내 한 줄
- 글 맨 끝(출처 아래): '부동산 공부할 때 곁에 두면 좋은 것' 칸 + 회색 [쇼핑커넥트 상품: ○○] 자리 3개
  → 어사이드가 네이버 글쓰기 창의 쇼핑커넥트로 같은 종류 상품을 넣고 회색 자리 줄은 지운다.
- 상품은 '부동산·청약 투자에 관심 있는 사람이 살 만한 것'. 글마다 같은 상품을 반복하지 않고 POOL에서 글 내용 단서로 3개를 고른다
  (PICKS_BY_SLUG에 직접 정한 글은 그대로). 기준은 .claude/skills/beodongsan-shopconnect/SKILL.md.
- 여러 번 실행해도 결과가 같다(표식 주석 사이를 통째로 바꿈). 문구·상품을 바꿀 땐 아래 상수만 고치고 다시 실행.
사용: python3 scripts/shopconnect/apply_naver_shop.py            (대상 전체)
      python3 scripts/shopconnect/apply_naver_shop.py <slug> ...  (특정 글)
"""
import os, re, sys, glob

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NAVER = os.path.join(ROOT, 'naver-html')
TARGET_CATS = {'부동산', '부동산이야기', '부동산정보'}
GRAY = 'color:#888888;font-size:13px;'

TOP = ('<!-- shopconnect:top --><p style="' + GRAY + '">이 글 하단에는 네이버 쇼핑 커넥트 상품 링크가 있어요. '
       '링크로 구매하면 브동산이 일정액의 수수료를 받아요.</p><!-- /shopconnect:top -->')

# ---------------------------------------------------------------------------
# 상품 풀 (2026-11-26 Paul 지시: 글마다 같은 상품 반복 금지, 글 내용을 보고 다양하게)
#  (id, 상품 종류, 이 글 독자에게 맞는 이유, 종류[book|tool|life], 글에서 찾을 단서(정규식))
#  단서가 많이 맞을수록 우선, 전체 글에서 이미 많이 쓴 상품은 뒤로 밀린다. 한 글에 책은 최대 2개, 도구·생활용품 1개 이상.
# ---------------------------------------------------------------------------
POOL = [
    ('cheongyak-book', '청약 가점·특별공급 가이드북', '가점 계산과 특별공급 자격 정리', 'book', r'가점|특별공급|1순위|청약통장|신혼부부|생애최초|다자녀'),
    ('tax-book', '부동산 세금(취득세·양도세) 절세 책', '취득세·양도세·보유세 미리 계산', 'book', r'취득세|양도세|세금|다주택|오피스텔|분양권|전매'),
    ('auction-book', '부동산 경매·공매 입문서', '시세보다 싸게 사는 또 다른 길', 'book', r'무순위|줍줍|미분양|선착순|할인 분양|잔여'),
    ('rebuild-book', '재건축·재개발 투자 책', '정비사업 단계와 분담금 이해', 'book', r'재건축|재개발|정비사업|조합|리모델링|강남|서초|반포'),
    ('income-book', '오피스텔·수익형 부동산 책', '월세 수익률·공실 따져 보기', 'book', r'오피스텔|임대|월세|수익형|상가|민간임대|뉴스테이'),
    ('location-book', '부동산 입지 분석 책', '역세권·학군·일자리로 단지 고르기', 'book', r'역세권|GTX|지하철|교통|신도시|생활권|입지|일자리'),
    ('contract-book', '부동산 계약·임대차 법률 가이드', '계약서·특약·임대 조건 확인', 'book', r'토지임대부|임대차|분양전환|계약|특약|임대료|공공임대'),
    ('asset-book', '금·자산배분 투자 책', '부동산과 다른 자산 비교', 'book', r'금값|금 투자|자산배분|주식|채권|금과 아파트'),
    ('laser', '레이저 거리측정기', '모델하우스·현장에서 방 크기 실측', 'tool', r'평면|모델하우스|견본주택|타입|㎡|발코니'),
    ('inspect-kit', '사전점검 키트(수평계·마스킹테이프)', '입주 전 하자 체크', 'tool', r'입주|사전점검|준공|하자|입주 예정|첫 입주'),
    ('hygrometer', '디지털 온습도계', '새 아파트 결로·환기 관리', 'tool', r'입주|결로|겨울|환기|신축'),
    ('battery', '대용량 보조배터리', '하루 종일 임장·현장 방문용', 'tool', r'임장|현장|방문|지방|홍보관|모델하우스'),
    ('backpack', '임장용 가벼운 백팩', '단지·동네 둘러볼 때', 'life', r'임장|단지|생활권|동네|둘러'),
    ('file', 'A4 서류 보관 파일', '공고문·계약서·분양 서류 모아 두기', 'life', r'계약|당첨|공고문|서류|중도금'),
    ('planner', '자산관리·가계부 플래너', '계약금·중도금·잔금 일정 관리', 'life', r'중도금|잔금|대출|계약금|자금|DSR|LTV'),
    ('moving-box', '이사 박스·포장 용품', '입주 전 이사 준비', 'life', r'입주|이사|잔금'),
    ('curtain', '암막 커튼', '새 집 입주 첫 준비물', 'life', r'입주|새 아파트|신축|첫 입주'),
    ('kids-safety', '아이 안전용품(모서리 보호대·안전문)', '아이 있는 집 새 아파트 세팅', 'life', r'신혼|아이|육아|자녀|다자녀|어린이|초품아'),
    ('school-prep', '초등 입학 준비물', '학교 가까운 단지로 이사 준비', 'life', r'초등|학군|초품아|학교|입학'),
]
POOL_BY_ID = {x[0]: x for x in POOL}

# 글별로 직접 고른 상품(새 글을 쓸 때 Claude가 글을 읽고 판단해 3개를 정해 넣는다). 없으면 자동 선택.
PICKS_BY_SLUG = {
    'gold-vs-apartment-trading-costs': ['asset-book', 'tax-book', 'planner'],   # 금 vs 아파트 거래비용 비교 글
    'acro-de-seocho': ['rebuild-book', 'cheongyak-book', 'laser'],               # 서초 재건축·만점통장 글
    'gyeongbuk-docheong-prugio-firstion': ['location-book', 'battery', 'planner'],  # 도청신도시 2단계·차량 임장·중도금 일정
    'songdo-logebien-moaelgaa': ['cheongyak-book', 'laser', 'location-book'],     # 인천 50% 우선·특공 398세대, 견본주택 실측, 트램·GTX 예정 입지
}


def _text(s):
    s = re.sub(r'<!--.*?-->|<style.*?</style>|<script.*?</script>', ' ', s, flags=re.S)
    return re.sub(r'<[^>]+>', ' ', s)


def choose(slug, s, usage):
    if slug in PICKS_BY_SLUG:
        return [POOL_BY_ID[i] for i in PICKS_BY_SLUG[slug]]
    text = _text(s)
    jit = lambda pid: (sum(ord(c) for c in slug + pid) % 97) / 97.0  # 같은 점수면 글마다 다르게
    scored = []
    for it in POOL:
        hits = len(re.findall(it[4], text))
        score = min(hits, 8) * 1.0 + (2 if hits else 0) - usage.get(it[0], 0) * 0.35 + jit(it[0])
        scored.append((score, it))
    scored.sort(key=lambda x: -x[0])
    out, books = [], 0
    for _, it in scored:
        if it[3] == 'book' and books >= 2:
            continue
        out.append(it); books += it[3] == 'book'
        if len(out) == 3:
            break
    if all(it[3] == 'book' for it in out[:2]) and out[2][3] == 'book':
        pass
    if not any(it[3] != 'book' for it in out):  # 도구·생활용품 최소 1개
        out[-1] = next(it for _, it in scored if it[3] != 'book')
    for it in out:
        usage[it[0]] = usage.get(it[0], 0) + 1
    return out


def bottom(items):
    rows = ''.join(f'<p style="{GRAY}">[쇼핑커넥트 상품: {it[1]} — {it[2]}]</p>' for it in items)
    return ('<!-- shopconnect:bottom --><p>&nbsp;</p>'
            '<p style="color:#000000;"><b>부동산 공부할 때 곁에 두면 좋은 것</b></p>' + rows +
            '<!-- /shopconnect:bottom -->')


def meta(s):
    for c in re.findall(r'<!--(.*?)-->', s[:4000], re.S):
        if 'slug:' in c or 'title:' in c:
            return c
    return ''


def category(head, s):
    for key in ('naver_category', 'category'):
        m = re.search(key + r':\s*([^|\n]+)', head)
        if m:
            return m.group(1).strip()
    return '부동산' if re.search(r'청약|분양|미분양', s[:6000]) else ''


def apply(path, usage):
    s = open(path, encoding='utf-8').read()
    head = meta(s)
    cat = category(head, s)
    if cat not in TARGET_CATS:
        return 'skip(' + (cat or '분류없음') + ')'
    s = re.sub(r'<!-- shopconnect:top -->.*?<!-- /shopconnect:top -->', '', s, flags=re.S)
    s = re.sub(r'<!-- shopconnect:bottom -->.*?<!-- /shopconnect:bottom -->\n?', '', s, flags=re.S)
    body = s.find('<body')
    body = s.find('>', body) + 1 if body >= 0 else (s.find('-->') + 3 if '-->' in s[:4000] else 0)
    # 바이라인(브동산·서당개 · … 문단)이 본문 앞쪽에 있으면 그 바로 아래, 없으면 본문 맨 앞
    bm = None
    for pm in re.finditer(r'<p[^>]*>(.*?)</p>', s[body:body + 3000], re.S):
        if re.search(r'(브동산|서당개)[^<]{0,30}(·|언박싱)', re.sub(r'<[^>]+>', '', pm.group(1))) and len(pm.group(1)) < 200:
            bm = pm
            break
    pos = body + bm.end() if bm else body
    s = s[:pos] + TOP + s[pos:]
    end = s.rfind('</body>')
    slug = os.path.basename(path)[:-5]
    items = choose(slug, s, usage)
    blk = bottom(items)
    s = (s[:end] + blk + '\n' + s[end:]) if end >= 0 else (s.rstrip() + blk + '\n')
    open(path, 'w', encoding='utf-8').write(s)
    return 'ok ' + ', '.join(it[0] for it in items)


if __name__ == '__main__':
    files = [os.path.join(NAVER, a + '.html') for a in sys.argv[1:]] or sorted(glob.glob(os.path.join(NAVER, '*.html')))
    usage = {}
    for f in files:
        print(os.path.basename(f), apply(f, usage))
