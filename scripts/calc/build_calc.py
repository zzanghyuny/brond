#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""브동산 계산기 페이지 만들기 (2026.11.28).

scripts/calc/src/<이름>.html 본문을 사이트 공통 머리·메뉴·바닥과 합쳐 calc/<이름>.html로 쓴다.
계산 로직(취득세·조정대상지역 목록)은 calc/calc.js 한 곳에 있다. 규정이 바뀌면 calc.js를 고치고
ADJ_ASOF·ASOF를 바꾼 뒤 이 스크립트를 다시 돌린다.

사용법: python3 scripts/calc/build_calc.py
"""
import os, re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SRC = os.path.join(os.path.dirname(__file__), 'src')
OUT = os.path.join(ROOT, 'calc')
SITE = 'https://www.brandongsan.com'
ADJ_ASOF = '2026.7.1 지정 기준'

PAGES = {
    'index': ('브동산 계산기 — 청약 가점·당첨 자금·취득세', '청약 가점, 청약 당첨 후 필요한 돈, 아파트 취득세를 공식 기준(주택공급에 관한 규칙·지방세법)대로 바로 계산하는 브동산 계산기 모음.'),
    'cheongyak-score': ('청약 가점 계산기 (84점 만점) — 브동산', '무주택 기간·부양가족·청약통장 가입 기간으로 청약 가점을 계산합니다. 주택공급에 관한 규칙 [별표 1] 기준, 배우자 통장 가산 반영.'),
    'cash-plan': ('청약 당첨되면 필요한 돈 계산기 — 브동산', '계약금·중도금·잔금, 취득세, 옵션, 후불 이자까지 더해 청약 당첨 후 계약할 때와 입주할 때 필요한 내 돈을 계산합니다.'),
    'acquisition-tax': ('아파트 취득세 계산기 (2026) — 브동산', '주택 수·조정대상지역·면적에 따른 아파트 취득세, 지방교육세, 농어촌특별세를 계산하고 생애최초 감면을 반영합니다.'),
}
MORE = [('cheongyak-score', '청약 가점 계산기', '84점 만점 가점'), ('cash-plan', '당첨되면 필요한 돈', '계약·입주 자금'),
        ('acquisition-tax', '취득세 계산기', '중과·생애최초 감면'), ('index', '계산기 모음', '전체 보기')]

HEAD = '''<!doctype html>
<html lang="ko">
<head>
<link rel="canonical" href="{canon}">
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-7TD8E3J131"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());

  gtag('config', 'G-7TD8E3J131');
</script>

<meta charset="utf-8">
<meta name="google-adsense-account" content="ca-pub-1191746063892692">
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-1191746063892692"
     crossorigin="anonymous"></script>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<meta property="og:url" content="{canon}">
<link rel="stylesheet" href="/styles.css">
<link rel="stylesheet" href="/calc/calc.css">
</head>
<body>

<header class="site-header">
  <div class="wrap sh-row">
    <a class="brand" href="/"><span class="b">브</span><span class="rest">동산</span></a>
    <nav class="site-nav">
      <a href="/">홈</a>
      <a href="/realestate.html">부동산이야기</a>
      <a href="/jupjup/">줍줍찬스</a>
      <a href="/calc/">계산기</a>
      <a href="/brand.html">브랜드이야기</a>
      <a href="/space-story.html">공간이야기</a>
      <a href="/city-story.html">도시이야기</a>
      <a href="/contact.html">문의</a>
    </nav>
  </div>
</header>
<div class="hairline"></div>
'''

FOOT = '''
<footer>
  <div class="wrap">
    <p>브동산은 부동산 정보와 브랜드 이야기를 담백하게 전하는 공간입니다. 게시된 내용은 정보 제공 목적이며, 투자 판단의 근거로 사용할 수 없습니다.</p>
    <p><a href="/about.html">소개</a> · <a href="/privacy.html">개인정보처리방침</a> · <a href="/contact.html">문의</a> · © 2026 브동산</p>
  </div>
</footer>

</body>
</html>
'''


def more(cur):
    items = ''.join('<a href="/calc/%s">%s<span>%s</span></a>' % ('' if k == 'index' else k + '.html', t, s)
                    for k, t, s in MORE if k != cur)
    return '<nav class="calc-more" aria-label="다른 계산기">%s</nav>' % items


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, (title, desc) in PAGES.items():
        body = open(os.path.join(SRC, name + '.html'), encoding='utf-8').read()
        body = body.replace('__MORE__', more(name)).replace('__ADJ_ASOF__', ADJ_ASOF)
        canon = SITE + '/calc/' + ('' if name == 'index' else name + '.html')
        html = HEAD.format(canon=canon, title=title, desc=desc) + body + FOOT
        open(os.path.join(OUT, name + '.html'), 'w', encoding='utf-8').write(html)
    update_nav()
    update_sitemap()
    print('계산기 %d쪽 생성' % len(PAGES))


def update_nav():
    """루트 페이지와 줍줍찬스 템플릿 상단 메뉴에 '계산기'를 넣는다(줍줍찬스 바로 뒤)."""
    files = [os.path.join(ROOT, f) for f in os.listdir(ROOT) if f.endswith('.html')]
    files.append(os.path.join(ROOT, 'scripts', 'jupjup', 'build_jupjup.py'))
    jj = os.path.join(ROOT, 'jupjup')
    files += [os.path.join(jj, f) for f in os.listdir(jj) if f.endswith('.html')]
    for f in files:
        t = open(f, encoding='utf-8').read()
        if 'class="site-nav"' not in t:
            continue
        nav = t.split('class="site-nav"', 1)[1].split('</nav>', 1)[0]
        if '/calc/' in nav:
            continue
        t2 = re.sub(r'(<a href="/jupjup/">줍줍찬스</a>)(\s*)', lambda m: m.group(1) + m.group(2) + '<a href="/calc/">계산기</a>' + m.group(2), t, count=1)
        if t2 != t:
            open(f, 'w', encoding='utf-8').write(t2)


def update_sitemap():
    p = os.path.join(ROOT, 'sitemap.xml')
    sm = open(p, encoding='utf-8').read()
    add = ''
    for name in PAGES:
        loc = SITE + '/calc/' + ('' if name == 'index' else name + '.html')
        if loc not in sm:
            add += '  <url><loc>%s</loc><changefreq>monthly</changefreq><priority>0.7</priority></url>\n' % loc
    if add:
        sm = sm.replace('</urlset>', add + '</urlset>')
        open(p, 'w', encoding='utf-8').write(sm)


if __name__ == '__main__':
    main()
