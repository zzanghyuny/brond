#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""브동산 네이버 원고(naver-html/*.html)에 쇼핑커넥트 자리를 넣는다. (2026-11-26 Paul 지시, 항상 적용)

- 대상: naver_category가 부동산·부동산이야기·부동산정보인 청약·미분양 글 (공간·브랜드 글 제외)
- 글 맨 위(바이라인 바로 아래): 회색 작은 대가성 안내 한 줄
- 글 맨 끝(출처 아래): '부동산 공부할 때 곁에 두면 좋은 것' 칸 + 회색 [쇼핑커넥트 상품: ○○] 자리 3개
  → 어사이드가 네이버 글쓰기 창의 쇼핑커넥트로 같은 종류 상품을 넣고 회색 자리 줄은 지운다.
- 상품은 '부동산·청약 투자에 관심 있는 사람이 살 만한 것'. 글 종류(청약/미분양·선착순)별로 PICKS에서 고른다.
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

PICKS = {
    # 청약 글: 청약 준비·모델하우스·계약 단계
    'cheongyak': [
        ('청약·부동산 투자 입문서', '청약 제도와 가점, 투자 기초 공부'),
        ('레이저 거리측정기', '모델하우스·견본주택에서 방 크기 실측'),
        ('A4 서류 보관 파일', '공고문·계약서·분양 서류 모아 두기'),
    ],
    # 미분양·선착순 글: 바로 계약·입주가 가까운 단계
    'firstcome': [
        ('부동산 투자 입문서', '미분양·선착순 계약 전 기초 공부'),
        ('레이저 거리측정기', '현장·사전점검에서 실측'),
        ('사전점검 키트(수평계·마스킹테이프)', '입주 전 하자 체크'),
    ],
}


def kind_of(name, head):
    t = name + ' ' + head
    return 'firstcome' if re.search(r'firstcome|미분양|선착순|줍줍', t) else 'cheongyak'


def bottom(kind):
    rows = ''.join(f'<p style="{GRAY}">[쇼핑커넥트 상품: {n} — {why}]</p>' for n, why in PICKS[kind])
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


def apply(path):
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
    blk = bottom(kind_of(os.path.basename(path), head + s[:3000]))
    s = (s[:end] + blk + '\n' + s[end:]) if end >= 0 else (s.rstrip() + blk + '\n')
    open(path, 'w', encoding='utf-8').write(s)
    return 'ok(' + kind_of(os.path.basename(path), head + s[:3000]) + ')'


if __name__ == '__main__':
    files = [os.path.join(NAVER, a + '.html') for a in sys.argv[1:]] or sorted(glob.glob(os.path.join(NAVER, '*.html')))
    for f in files:
        print(os.path.basename(f), apply(f))
