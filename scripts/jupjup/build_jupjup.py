#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""브동산 '줍줍찬스'(전국 미분양 줍줍) 코너 생성기.

사용(저장소 루트에서):  python3 scripts/jupjup/build_jupjup.py

입력
  scripts/firstcome/regions/*.json   권역 회차 데이터(선착순 확정 단지)
  posts/images/<회차 slug>/images.json  단지별 조감도·위치도
  scripts/jupjup/points.json         단지별 장점 2~3줄(사실만, 긍정 어투)
  jupjup/data.json                   지난번 결과(빠진 단지를 '마감'으로 남기기 위해)
출력
  jupjup/index.html                  전국 목록(권역·지역·입주·분양가 필터)
  jupjup/<key>.html                  단지 상세(맨 아래 상담사 카드 칸)
  jupjup/data.json                   단지 목록(결제 서버가 단지 키 검증에 사용)
  sitemap.xml, 상단 메뉴              코너 링크 자동 반영(여러 번 실행해도 결과 동일)

원칙: 적정가·예상 프리미엄·비교단지 시세는 쓰지 않는다. 장점은 확인된 사실만 긍정 어투로 쓴다.
권역 회차(region_build.py register)가 끝날 때 자동으로 다시 실행된다.
"""
import os, sys, json, glob, re, html as H, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True
sys.path.insert(0, HERE)
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.join(ROOT, 'jupjup')
REG = os.path.join(ROOT, 'scripts', 'firstcome', 'regions')
SITE = 'https://www.brandongsan.com'

RIDS = ['sudogwon', 'chungcheong', 'busan-ulsan', 'daegu-gyeongbuk-gangwon', 'gyeongnam-honam-jeju']
SHORT = {'sudogwon': '수도권', 'chungcheong': '충청권', 'busan-ulsan': '부산·울산',
         'daegu-gyeongbuk-gangwon': '대구·경북·강원', 'gyeongnam-honam-jeju': '경남·호남·제주'}

# 사업자 정보 — 사업자등록·통신판매업 신고 후 채운다(카드결제 가맹 심사에 필요).
BUSINESS = {
    '상호': '브동산',
    '대표자': '[등록 후 기재]',
    '사업자등록번호': '[등록 후 기재]',
    '통신판매업 신고번호': '[신고 후 기재]',
    '주소': '[등록 후 기재]',
    '이메일': 'seodangdog81@gmail.com',
}

e = lambda s: H.escape(str(s), quote=True)
PLANS = json.load(open(os.path.join(OUT, 'plans.json'), encoding='utf-8'))
POINTS = json.load(open(os.path.join(HERE, 'points.json'), encoding='utf-8'))
_NP = os.path.join(HERE, 'notices.json')
NOTICES = json.load(open(_NP, encoding='utf-8')) if os.path.exists(_NP) else {}


def notice_links(key):
    n = NOTICES.get(key)
    if not n:
        return ''
    btns = ''.join(
        f'<a class="jj-btn solid" href="{e(x["pdf"])}" target="_blank" rel="noopener nofollow">모집공고 보기{(" · " + e(x["label"])) if x.get("label") else ""}</a>'
        for x in n.get('notices', []) if x.get('pdf'))
    home = (f'<a class="jj-btn" href="{e(n["home"])}" target="_blank" rel="noopener nofollow">분양 홈페이지</a>' if n.get('home') else '')
    if not (btns or home):
        return ''
    return (f'<div class="jj-links">{btns}{home}</div>'
            '<p class="jj-note">모집공고는 청약홈(한국부동산원)에 올라온 입주자모집공고문이고, 분양 홈페이지는 청약홈에 등록된 주소입니다.</p>')


def eok(v):
    return f"{v:.2f}억" if v >= 1 else f"{round(v * 10000):,}만"


def comma(n):
    return f"{n:,}"


def region_slug(rid, d):
    if d.get('slug'):
        return d['slug']
    ymd = d['date'].replace('-', '')
    if rid == 'sudogwon':
        if d['date'] == '2026-11-16':
            return 'sudogwon-firstcome-top30-202611'
        cands = [f'sudogwon-firstcome-top30-{ymd}', f'sudogwon-firstcome-{ymd}']
    else:
        cands = [f'{rid}-firstcome-{ymd}']
    for c in cands:
        if os.path.isdir(os.path.join(ROOT, 'posts', 'images', c)):
            return c
    found = sorted(glob.glob(os.path.join(ROOT, 'posts', 'images', f'{rid}-firstcome*')))
    return os.path.basename(found[-1]) if found else cands[0]


def load_images(slug):
    p = os.path.join(ROOT, 'posts', 'images', slug, 'images.json')
    if os.path.exists(p):
        return json.load(open(p, encoding='utf-8'))
    if slug == 'sudogwon-firstcome-top30-202611':
        return json.load(open(os.path.join(ROOT, 'scripts', 'firstcome', 'images.json'), encoding='utf-8'))
    return {}


def first_url(s):
    m = re.search(r'https?://[^\s)·,]+', s or '')
    return m.group(0) if m else ''


def src_label(url, fallback=''):
    if not url:
        return fallback
    host = re.sub(r'^https?://(www\.)?', '', url).split('/')[0]
    names = {'apttoyou.kr': '아파트투유 단지 페이지', 'brandhome.kr': '분양홈', 'listup24.com': '리스트업24'}
    return names.get(host, host)


def move_in(s):
    if s.get('done'):
        return '바로 입주', f"{s['yr']}년 {s['mo']}월 준공 · 바로 입주"
    return f"{s['yr']}.{s['mo']:02d} 입주", f"{s['yr']}년 {s['mo']}월 입주 예정"


def default_points(s):
    pts = [f"{s['region']} {comma(s['n'])}세대"]
    if s.get('builder'):
        pts.append(f"{s['builder']} 시공")
    return pts


def collect():
    sites, regions = [], []
    for rid in RIDS:
        p = os.path.join(REG, f'{rid}.json')
        if not os.path.exists(p):
            continue
        d = json.load(open(p, encoding='utf-8'))
        slug = region_slug(rid, d)
        imgs = load_images(slug)
        regions.append({'rid': rid, 'label': SHORT.get(rid, d.get('label', rid)), 'areas': d.get('areas', ''),
                        'date': d['date'], 'count': len(d['sites'])})
        for s in d['sites']:
            im = imgs.get(s['key'], {})
            def img(kind):
                x = im.get(kind)
                if not x:
                    return None
                return {'url': f"/posts/images/{slug}/{x['file']}", 'src': x.get('src', '')}
            size = str(s.get('size', '84'))
            badge, mi = move_in(s)
            psrc = first_url(s.get('price_src', '')) or first_url(s.get('firstcome_src', ''))
            benefit = ''
            if s.get('benefit') and s.get('benefit_src'):
                benefit = re.sub(r'\s*\([^)]*\)\s*$', '', s['benefit_src']).strip()
            sites.append({
                'key': s['key'], 'name': s['name'], 'rid': rid, 'rlabel': SHORT.get(rid, rid),
                'sido': s.get('sido') or s['region'].split()[0], 'area': s['region'],
                'n': s['n'], 'builder': s.get('builder', ''), 'yr': s['yr'], 'mo': s['mo'],
                'done': bool(s.get('done')), 'badge': badge, 'movein': mi,
                'size': size, 'price': round(float(s['price']), 3), 'range': s.get('price_note', ''),
                'benefit': benefit, 'points': POINTS.get(s['key']) or default_points(s),
                'aerial': img('aerial'), 'location': img('location'),
                'psrc': psrc, 'psrc_label': src_label(psrc), 'date': d['date'], 'status': 'open',
            })
    # 광고 레이더 등으로 먼저 확인한 단지(권역 회차에 아직 없는 것)
    xp = os.path.join(HERE, 'extra_sites.json')
    have = {s['key'] for s in sites}
    if os.path.exists(xp):
        for s in json.load(open(xp, encoding='utf-8')).get('sites', []):
            if s['key'] in have:
                continue
            badge, mi = move_in(s)
            psrc = first_url(s.get('price_src', ''))
            sites.append({
                'key': s['key'], 'name': s['name'], 'rid': s['rid'], 'rlabel': SHORT.get(s['rid'], s['rid']),
                'sido': s.get('sido') or s['region'].split()[0], 'area': s['region'],
                'n': s['n'], 'builder': s.get('builder', ''), 'yr': s['yr'], 'mo': s['mo'],
                'done': bool(s.get('done')), 'badge': badge, 'movein': mi,
                'size': str(s.get('size', '84')), 'price': round(float(s['price']), 3), 'range': s.get('price_note', ''),
                'benefit': s.get('benefit', ''), 'points': POINTS.get(s['key']) or default_points(s),
                'aerial': s.get('aerial'), 'location': s.get('location'),
                'psrc': psrc, 'psrc_label': '청약홈 입주자모집공고' if 'applyhome' in psrc else src_label(psrc),
                'date': s['date'], 'status': 'open', 'extra': True,
            })
            for r in regions:
                if r['rid'] == s['rid']:
                    r['count'] += 1
    return sites, regions


def merge_closed(sites):
    """지난번 data.json에 있었는데 이번 회차에 빠진 단지는 '마감'으로 남긴다(페이지·상담사 카드 유지)."""
    p = os.path.join(OUT, 'data.json')
    now = {s['key'] for s in sites}
    closed = []
    if os.path.exists(p):
        old = json.load(open(p, encoding='utf-8'))
        today = dt.date.today().isoformat()
        for o in old.get('sites', []):
            if o['key'] in now:
                continue
            o = dict(o)
            if o.get('status') != 'closed':
                o['status'] = 'closed'
                o['closed'] = today
            closed.append(o)
    return closed


# ------------------------------------------------------------------ 공통 조각
HEAD = '''<!doctype html>
<html lang="ko">
<head>
<link rel="canonical" href="{canon}">
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
{og_img}{robots}<link rel="stylesheet" href="/styles.css">
<link rel="stylesheet" href="/jupjup/jupjup.css">
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


def head(title, desc, canon, og_img='', robots=''):
    og = f'<meta property="og:image" content="{e(SITE + og_img)}">\n' if og_img else ''
    rb = '<meta name="robots" content="noindex,nofollow">\n' if robots else ''
    return HEAD.format(title=e(title), desc=e(desc), canon=e(canon), og_img=og, robots=rb)


def footer(scripts=('/jupjup/jupjup.js',)):
    biz = ' · '.join(f'{k} {e(v)}' for k, v in BUSINESS.items() if not str(v).startswith('['))
    sc = ''.join(f'<script src="{s}"></script>\n' for s in scripts)
    return f'''
<footer>
  <div class="wrap">
    <p>브동산은 분양 정보를 모아 보여 줄 뿐 분양을 중개하거나 대행하지 않습니다. 분양 조건은 수시로 바뀌므로 계약 전 분양 홈페이지·견본주택에서 최신 조건을 꼭 확인하세요. 게시된 내용은 투자 판단의 근거로 사용할 수 없습니다.</p>
    <p class="jj-biz">{biz}</p>
    <p><a href="/about.html">소개</a> · <a href="/privacy.html">개인정보처리방침</a> · <a href="/jupjup/terms.html">상담사 광고 약관</a> · <a href="/contact.html">문의</a> · © 2026 브동산</p>
  </div>
</footer>
{sc}
</body>
</html>
'''


def price_bucket(p):
    for lo, hi, k in [(0, 4, 'p0'), (4, 6, 'p1'), (6, 8, 'p2'), (8, 10, 'p3')]:
        if lo <= p < hi:
            return k
    return 'p4'


def card(s, lazy=True):
    img = s['aerial'] or s['location']
    pic = (f'<img src="{e(img["url"])}" alt="{e(s["name"])} 조감도" loading="{"lazy" if lazy else "eager"}">'
           if img else f'<span class="jj-noimg">{e(s["name"])}<small>조감도 준비 중</small></span>')
    order = 0 if s['done'] else s['yr'] * 12 + s['mo']
    badge_cls = 'jj-badge solid' if s['done'] else 'jj-badge'
    return f'''<a class="jj-card" href="/jupjup/{e(s['key'])}.html" data-key="{e(s['key'])}" data-r="{s['rid']}" data-sido="{e(s['sido'])}" data-done="{int(s['done'])}" data-p="{price_bucket(s['price'])}" data-price="{s['price']}" data-n="{s['n']}" data-move="{order}" data-img="{1 if img else 0}">
  <span class="jj-thumb">{pic}<span class="{badge_cls}">{e(s['badge'])}</span></span>
  <span class="jj-cbody">
    <span class="jj-cregion">{e(s['area'])}</span>
    <span class="jj-cname">{e(s['name'])}</span>
    <span class="jj-cfacts">{comma(s['n'])}세대 · {e(s['builder'])}</span>
    <span class="jj-cprice"><span class="lbl">{e(s['size'])}㎡ 최고</span> <b>{eok(s['price'])}</b></span>
    <span class="jj-cpoint">{e(s['points'][0])}</span>
    <span class="jj-cagents" data-agents hidden></span>
  </span>
</a>'''


def build_index(sites, regions, closed):
    dates = sorted({r['date'] for r in regions})
    dtxt = dates[0].replace('-', '.') if len(dates) == 1 else f"{dates[0].replace('-', '.')}~{dates[-1][5:].replace('-', '.')}"
    n_done = sum(1 for s in sites if s['done'])
    sidos = []
    for s in sites:
        if s['sido'] not in sidos:
            sidos.append(s['sido'])
    pills = '<button class="jj-pill on" data-f-r="">전체 <span>{}</span></button>'.format(len(sites)) + ''.join(
        f'<button class="jj-pill" data-f-r="{r["rid"]}">{e(r["label"])} <span>{r["count"]}</span></button>' for r in regions)
    sido_opts = '<option value="">시·도 전체</option>' + ''.join(f'<option>{e(x)}</option>' for x in sidos)
    cards = '\n'.join(card(s, lazy=i > 5) for i, s in enumerate(sites))
    closed_html = ''
    if closed:
        li = ''.join(f'<li><a href="/jupjup/{e(c["key"])}.html">{e(c["name"])}</a> <small>{e(c["area"])} · {e(c.get("closed", "").replace("-", "."))} 확인</small></li>' for c in closed)
        closed_html = f'<details class="jj-closed"><summary>최근 선착순이 마감된 단지 {len(closed)}곳</summary><ul>{li}</ul></details>'
    plan0 = PLANS['plans'][0]
    title = '줍줍찬스 — 전국 미분양 줍줍 현황, 선착순 동·호 지정 아파트 한눈에 | 브동산'
    desc = f'청약통장 없이 원하는 동·호수를 고르는 전국 미분양 선착순 아파트 {len(sites)}곳. 권역·지역·입주 시기·분양가로 골라 보세요.'
    out = head(title, desc, f'{SITE}/jupjup/', og_img=(sites[0]['aerial'] or {}).get('url', '') if sites else '')
    out += f'''
<div class="wrap-jj jj-hero">
  <p class="jj-eyebrow">브동산 줍줍찬스 · 전국 미분양 줍줍 현황</p>
  <h1>청약통장 없이, 원하는 동·호수를<br>직접 고르는 아파트</h1>
  <p class="jj-hero-sub">전국에서 지금 선착순 동·호 지정 계약을 받는 미분양 아파트를 모았습니다. 권역마다 보름에 한 번 다시 확인합니다.</p>
  <dl class="jj-stats">
    <div><dt>지금 줍줍 가능</dt><dd>{len(sites)}<small>곳</small></dd></div>
    <div><dt>바로 입주</dt><dd>{n_done}<small>곳</small></dd></div>
    <div><dt>정보 기준일</dt><dd class="sm">{dtxt}</dd></div>
  </dl>
</div>

<div class="wrap-jj jj-filters" role="region" aria-label="단지 거르기">
  <div class="jj-pills" data-pills>{pills}</div>
  <div class="jj-selects">
    <label><span class="sr">시·도</span><select data-f-sido>{sido_opts}</select></label>
    <label><span class="sr">입주</span><select data-f-done><option value="">입주 시기 전체</option><option value="1">바로 입주</option><option value="0">입주 예정</option></select></label>
    <label><span class="sr">분양가</span><select data-f-p><option value="">분양가 전체</option><option value="p0">4억 미만</option><option value="p1">4억~6억</option><option value="p2">6억~8억</option><option value="p3">8억~10억</option><option value="p4">10억 이상</option></select></label>
    <label><span class="sr">정렬</span><select data-sort><option value="move">입주 빠른 순</option><option value="n">세대수 많은 순</option><option value="pa">분양가 낮은 순</option><option value="pd">분양가 높은 순</option></select></label>
  </div>
  <p class="jj-count" data-count aria-live="polite">{len(sites)}곳</p>
</div>

<div class="wrap-jj">
  <div class="jj-grid" data-grid>
{cards}
  </div>
  <p class="jj-empty" data-empty hidden>조건에 맞는 단지가 없습니다. 조건을 넓혀 보세요.</p>
  {closed_html}
</div>

<div class="wrap-jj jj-guide">
  <section>
    <h2>줍줍, 이렇게 보세요</h2>
    <ul class="jj-steps">
      <li><b>선착순 동·호 지정</b> 청약 접수가 끝난 뒤 남은 세대를 먼저 온 순서대로 계약합니다. 청약통장과 당첨 이력이 필요 없습니다.</li>
      <li><b>원하는 집을 직접</b> 남은 동·호수 가운데 층·향·타입을 직접 골라 계약할 수 있습니다.</li>
      <li><b>조건은 수시로 바뀝니다</b> 계약금 정액제·중도금 무이자·페이백 같은 조건과 남은 세대는 매일 달라집니다. 계약 전 분양 홈페이지·견본주택에서 꼭 확인하세요.</li>
    </ul>
  </section>
  <section class="jj-cta-agent">
    <h2>분양 상담사이신가요?</h2>
    <p>단지 페이지 맨 아래 상담사 카드 칸에 연락처 카드를 올릴 수 있습니다. 단지당 {PLANS['slotsPerSite']}칸, {e(plan0['label'])} {comma(plan0['price'])}원부터, {'계좌이체 확인 후 ' + str(PLANS['transfer']['postHours']) + '시간 안에' if PLANS.get('payment') == 'transfer' else '카드결제 즉시'} 게재됩니다.</p>
    <p><a class="jj-btn solid" href="/jupjup/agent.html">상담사 카드 신청하기</a> <a class="jj-btn" href="/jupjup/terms.html">광고 약관 보기</a></p>
    <p class="jj-note">상담사 카드는 유료 광고이며, 단지 목록의 순서·내용과 관계없습니다.</p>
  </section>
</div>
'''
    out += footer()
    open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(out)


def kv_rows(s):
    rows = [('위치', s['area']), ('규모', f"{comma(s['n'])}세대"), ('시공', s['builder']), ('입주', s['movein']),
            (f"{s['size']}㎡ 분양가", f"대표 타입 최고 {eok(s['price'])}"), ('타입별 가격', s['range']),
            ('계약 방식', '선착순 동·호 지정 계약 (청약통장 필요 없음)')]
    if s.get('benefit'):
        rows.append(('확인된 혜택', s['benefit'] + ' · 조건 변동 가능'))
    out = ''
    for k, v in rows:
        if v:
            out += f'<tr><th scope="row">{e(k)}</th><td>{e(v)}</td></tr>'
    return out


def build_detail(s, same_region, plans):
    closed = s.get('status') == 'closed'
    img = s['aerial']
    photo = ''
    if img:
        photo = f'''<figure class="photo-block jj-photo"><img src="{e(img['url'])}" alt="{e(s['name'])} 조감도" style="width:100%;display:block;"><figcaption>조감도 · 출처: {e(img['src'])}</figcaption></figure>'''
    loc = ''
    if s['location']:
        loc = f'''<section class="wrap jj-sec"><h2>위치</h2><figure class="photo-block jj-photo"><img src="{e(s['location']['url'])}" alt="{e(s['name'])} 위치도" loading="lazy" style="width:100%;display:block;"><figcaption>위치도 · 출처: {e(s['location']['src'])}</figcaption></figure></section>'''
    pts = ''.join(f'<li>{e(p)}</li>' for p in s['points'])
    src = ''
    if s['psrc']:
        src = f' · 가격 출처: <a href="{e(s["psrc"])}" target="_blank" rel="noopener nofollow">{e(s["psrc_label"])}</a>'
    rel = ''.join(card(x) for x in same_region[:4])
    status_badge = ('<span class="jj-badge">선착순 마감 확인</span>' if closed else '<span class="jj-badge solid">선착순 동·호 지정</span>')
    move_badge = f'<span class="jj-badge">{e(s["badge"])}</span>'
    closed_note = ''
    if closed:
        closed_note = f'<p class="jj-closed-note">{e(s.get("closed", "").replace("-", "."))} 회차 확인에서 선착순 분양 목록에 더 이상 보이지 않았습니다. 남은 세대가 있는지는 분양 홈페이지에서 확인하세요.</p>'
    plan0 = plans['plans'][0]
    title = f"{s['name']} 선착순 분양 | {s['area']} {comma(s['n'])}세대, {s['size']}㎡ 최고 {eok(s['price'])} — 브동산 줍줍찬스"
    desc = f"{s['area']} {s['name']}({comma(s['n'])}세대, {s['builder']}) 선착순 동·호 지정 계약 정보. {', '.join(s['points'][:2])}."
    out = head(title, desc, f"{SITE}/jupjup/{s['key']}.html", og_img=(img or {}).get('url', ''))
    out += f'''
<div class="wrap jj-crumb"><a href="/jupjup/">줍줍찬스</a> <span aria-hidden="true">›</span> <a href="/jupjup/?r={s['rid']}">{e(s['rlabel'])}</a></div>
<div class="wrap jj-head">
  <div class="jj-badges">{status_badge}{move_badge}</div>
  <h1>{e(s['name'])}</h1>
  <p class="jj-sub">{e(s['area'])} · {comma(s['n'])}세대 · {e(s['builder'])}</p>
  {closed_note}
</div>
<div class="wrap">{photo}</div>
<div class="wrap">
  <div class="jj-pricebox">
    <div class="lbl">{e(s['size'])}㎡ 대표 타입 최고 분양가</div>
    <div class="big">{eok(s['price'])}</div>
    <div class="rng">{e(s['range'])}</div>
  </div>
</div>
<section class="wrap jj-sec">
  <h2>이런 점이 좋아요</h2>
  <ul class="jj-points">{pts}</ul>
  <p class="jj-lead">청약통장 없이, 남은 동·호수 가운데 원하는 층과 향을 직접 골라 계약할 수 있습니다.</p>
</section>
<section class="wrap jj-sec">
  <h2>단지 정보</h2>
  <table class="jj-kv"><tbody>{kv_rows(s)}</tbody></table>
  {notice_links(s['key'])}
  <p class="jj-note">정보 기준일 {e(s['date'].replace('-', '.'))}{src} · 분양가·혜택·남은 세대는 수시로 바뀝니다.</p>
</section>
{loc}
<section class="wrap jj-sec jj-agents" id="agents" data-site="{e(s['key'])}" data-site-name="{e(s['name'])}" data-open="{0 if closed else 1}" data-slots="{plans['slotsPerSite']}">
  <h2>이 단지 분양 상담</h2>
  <p class="jj-adnote"><span class="jj-ad">AD</span> 아래 상담사 카드는 상담사가 직접 등록한 유료 광고입니다. 브동산은 상담 내용과 계약에 관여하지 않습니다.</p>
  <div class="jj-agent-list" data-agent-list>
    {f'<a class="jj-slot" href="/jupjup/agent.html?site={e(s["key"])}"><b>상담사 카드 자리 <em data-free>{plans["slotsPerSite"]}칸 중 {plans["slotsPerSite"]}칸 비어 있음</em></b><span>이 단지를 상담하시나요? {e(plan0["label"])} {comma(plan0["price"])}원부터 연락처 카드를 올릴 수 있습니다. {'계좌이체 후 메일로 신청합니다.' if plans.get('payment') == 'transfer' else '카드결제 즉시 게재됩니다.'}</span></a>' if not closed else '<p class="jj-note">선착순 마감이 확인된 단지라 새 상담사 카드를 받지 않습니다.</p>'}
  </div>
</section>
<section class="wrap jj-sec">
  <h2>{e(s['rlabel'])} 다른 줍줍 단지</h2>
  <div class="jj-grid jj-grid-rel">{rel}</div>
  <p><a class="jj-btn" href="/jupjup/?r={s['rid']}">{e(s['rlabel'])} 전체 보기</a></p>
</section>
'''
    out += footer()
    open(os.path.join(OUT, f"{s['key']}.html"), 'w', encoding='utf-8').write(out)


def build_agent_transfer(sites, regions):
    """계좌이체 + 메일 신청 방식 상담사 등록 페이지(Paul 2026-11-26)."""
    T = PLANS['transfer']
    groups = ''
    for r in regions:
        opts = ''.join(f'<option value="{e(s["key"])}">{e(s["name"])}</option>'
                       for s in sorted([x for x in sites if x['rid'] == r['rid']], key=lambda x: x['name']))
        groups += f'<optgroup label="{e(r["label"])}">{opts}</optgroup>'
    radios = ''.join(
        f'<label class="jj-plan"><input type="radio" name="plan" value="{e(p["id"])}"{" checked" if i == 0 else ""}><b>{e(p["label"])} 게재</b><span>{comma(p["price"])}원</span></label>'
        for i, p in enumerate(PLANS['plans']))
    acct = f'{T["bank"]} {T["account"]} (예금주 {T["holder"]})'
    out = head('상담사 카드 신청 — 브동산 줍줍찬스', '줍줍찬스 단지 페이지 맨 아래에 분양 상담사 연락처 카드를 올립니다. 계좌이체 후 메일로 신청.',
               f'{SITE}/jupjup/agent.html')
    out += f'''
<div class="wrap jj-crumb"><a href="/jupjup/">줍줍찬스</a> <span aria-hidden="true">›</span> 상담사 카드 신청</div>
<div class="wrap jj-head">
  <h1>상담사 카드 신청</h1>
  <p class="jj-sub">단지 페이지 맨 아래 '이 단지 분양 상담' 칸에 연락처 카드를 올립니다. 단지당 {PLANS['slotsPerSite']}칸입니다.</p>
  <ol class="jj-steps jj-howto">
    <li><b>1. 정보 입력</b> 아래 양식을 채우고 '메일로 신청 보내기'를 누르면 메일 앱이 열립니다. 그대로 보내 주세요. 사진은 그 메일에 첨부하면 됩니다(선택).</li>
    <li><b>2. 계좌이체</b> 신청 후 {T['depositHours']}시간 안에 아래 계좌로 입금해 주세요. 입금자명은 신청 뒤 화면에 나오는 이름으로 해 주세요.</li>
    <li><b>3. 게재</b> 입금이 확인되면 {T['postHours']}시간 안에 카드를 올립니다. 신청 메일이 접수되면 입금 기한까지 그 칸을 맡아 둡니다.</li>
  </ol>
  <div class="jj-banner"><b>입금 계좌</b> {e(acct)}</div>
</div>
<form class="wrap jj-form" data-transfer-form data-email="{e(T['applyEmail'])}" data-hours="{T['depositHours']}" data-acct="{e(acct)}" novalidate>
  <div class="jj-field"><span>단지</span><select name="site" required><option value="">단지를 골라 주세요</option>{groups}</select><p class="jj-note" data-slots-msg></p></div>
  <label class="jj-field"><span>이름 <small>카드에 공개</small></span><input type="text" name="name" maxlength="20" autocomplete="name" required></label>
  <label class="jj-field"><span>소속 <small>예: ○○분양 · 카드에 공개</small></span><input type="text" name="company" maxlength="30" autocomplete="organization" required></label>
  <label class="jj-field"><span>휴대폰 번호 <small>카드에 공개 · 전화·문자 버튼으로 연결</small></span><input type="tel" name="phone" inputmode="numeric" maxlength="13" placeholder="010-0000-0000" autocomplete="tel" required></label>
  <label class="jj-field"><span>카카오톡 오픈채팅 링크 <small>선택</small></span><input type="url" name="kakao" maxlength="120" placeholder="https://open.kakao.com/o/..."></label>
  <label class="jj-field"><span>한 줄 소개 <small>40자 이내 · 수익·가격 보장 표현 금지</small></span><input type="text" name="intro" maxlength="40" placeholder="예: 남은 동·호수와 계약 조건 바로 안내해 드립니다" required></label>
  <div class="jj-field"><span>게재 기간</span><div class="jj-plans">{radios}</div></div>
  <div class="jj-preview-wrap"><p>카드 미리보기</p><div data-preview></div></div>
  <div class="jj-field">
    <label class="jj-check"><input type="checkbox" name="agree_public"> <span>입력한 이름·소속·휴대폰 번호·카카오톡 링크·사진이 단지 페이지에 공개되는 것에 동의합니다.</span></label>
    <label class="jj-check"><input type="checkbox" name="agree_role"> <span>이 단지의 분양 상담 업무를 하고 있으며, 사실과 다르거나 과장된 내용을 쓰지 않겠습니다.</span></label>
    <label class="jj-check"><input type="checkbox" name="agree_terms"> <span><a href="/jupjup/terms.html" target="_blank">상담사 광고 약관·환불 규정</a>과 <a href="/privacy.html" target="_blank">개인정보처리방침</a>에 동의합니다.</span></label>
  </div>
  <div class="jj-total"><span>입금 금액</span><b data-total>{comma(PLANS['plans'][0]['price'])}원</b></div>
  <p class="jj-msg" data-msg aria-live="polite"></p>
  <button class="jj-btn solid" type="submit" style="width:100%">메일로 신청 보내기</button>
  <p class="jj-note">현재 세금계산서·현금영수증은 발급되지 않습니다. 상담사 카드는 유료 광고로 표시되며, 단지 목록의 순서·내용과 관계없습니다.</p>
</form>
<div class="wrap jj-done" data-done hidden></div>
'''
    out += footer(('/jupjup/jupjup.js', '/jupjup/agent.js'))
    open(os.path.join(OUT, 'agent.html'), 'w', encoding='utf-8').write(out)
    for fn in ('agent-success.html', 'agent-fail.html'):
        fp = os.path.join(OUT, fn)
        if os.path.exists(fp):
            os.remove(fp)


def build_agent_pages(sites, regions):
    TRANSFER = PLANS.get('payment') == 'transfer'
    if TRANSFER:
        build_agent_transfer(sites, regions)
    else:
        groups = ''
        for r in regions:
            opts = ''.join(f'<option value="{e(s["key"])}">{e(s["name"])}</option>'
                           for s in sorted([x for x in sites if x['rid'] == r['rid']], key=lambda x: x['name']))
            groups += f'<optgroup label="{e(r["label"])}">{opts}</optgroup>'
        radios = ''.join(
            f'<label class="jj-plan"><input type="radio" name="plan" value="{e(p["id"])}"{" checked" if i == 0 else ""}><b>{e(p["label"])} 게재</b><span>{comma(p["price"])}원</span></label>'
            for i, p in enumerate(PLANS['plans']))
        out = head('상담사 카드 등록 — 브동산 줍줍찬스', '줍줍찬스 단지 페이지 맨 아래에 분양 상담사 연락처 카드를 올립니다. 카드결제 즉시 게재.',
                   f'{SITE}/jupjup/agent.html')
        out += f'''
    <div class="wrap jj-crumb"><a href="/jupjup/">줍줍찬스</a> <span aria-hidden="true">›</span> 상담사 카드 등록</div>
    <div class="wrap jj-head">
      <h1>상담사 카드 등록</h1>
      <p class="jj-sub">단지 페이지 맨 아래 '이 단지 분양 상담' 칸에 연락처 카드를 올립니다. 단지당 {PLANS['slotsPerSite']}칸이며, 카드결제가 끝나면 1~2분 안에 자동으로 게재됩니다.</p>
      <div class="jj-banner" data-mode hidden></div>
    </div>
    <form class="wrap jj-form" data-agent-form novalidate>
      <div class="jj-field"><span>단지</span><select name="site" required><option value="">단지를 골라 주세요</option>{groups}</select><p class="jj-note" data-slots-msg></p></div>
      <label class="jj-field"><span>이름 <small>카드에 공개</small></span><input type="text" name="name" maxlength="20" autocomplete="name" required></label>
      <label class="jj-field"><span>소속 <small>예: ○○분양 · 카드에 공개</small></span><input type="text" name="company" maxlength="30" autocomplete="organization" required></label>
      <label class="jj-field"><span>휴대폰 번호 <small>카드에 공개 · 전화·문자 버튼으로 연결</small></span><input type="tel" name="phone" inputmode="numeric" maxlength="13" placeholder="010-0000-0000" autocomplete="tel" required></label>
      <label class="jj-field"><span>카카오톡 오픈채팅 링크 <small>선택</small></span><input type="url" name="kakao" maxlength="120" placeholder="https://open.kakao.com/o/..."></label>
      <label class="jj-field"><span>한 줄 소개 <small>40자 이내 · 수익·가격 보장 표현 금지</small></span><input type="text" name="intro" maxlength="40" placeholder="예: 남은 동·호수와 계약 조건 바로 안내해 드립니다" required></label>
      <label class="jj-field"><span>사진 <small>선택 · 얼굴이나 명함 사진, 자동으로 줄여서 올립니다</small></span><input type="file" name="photo" accept="image/*"></label>
      <div class="jj-field"><span>게재 기간</span><div class="jj-plans">{radios}</div></div>
      <div class="jj-preview-wrap"><p>카드 미리보기</p><div data-preview></div></div>
      <div class="jj-field">
        <label class="jj-check"><input type="checkbox" name="agree_public"> <span>입력한 이름·소속·휴대폰 번호·카카오톡 링크·사진이 단지 페이지에 공개되는 것에 동의합니다.</span></label>
        <label class="jj-check"><input type="checkbox" name="agree_role"> <span>이 단지의 분양 상담 업무를 하고 있으며, 사실과 다르거나 과장된 내용을 쓰지 않겠습니다.</span></label>
        <label class="jj-check"><input type="checkbox" name="agree_terms"> <span><a href="/jupjup/terms.html" target="_blank">상담사 광고 약관·환불 규정</a>과 <a href="/privacy.html" target="_blank">개인정보처리방침</a>에 동의합니다.</span></label>
      </div>
      <div class="jj-total"><span>결제 금액 <small>부가세 포함</small></span><b data-total>{comma(PLANS['plans'][0]['price'])}원</b></div>
      <p class="jj-msg" data-msg aria-live="polite"></p>
      <button class="jj-btn solid" type="submit" data-pay style="width:100%" disabled>카드로 결제하고 게재하기</button>
      <p class="jj-note">결제는 토스페이먼츠 카드결제로 처리됩니다. 상담사 카드는 유료 광고로 표시되며, 단지 목록의 순서·내용과 관계없습니다.</p>
    </form>
    '''
        out += footer(('https://js.tosspayments.com/v2/standard', '/jupjup/jupjup.js', '/jupjup/agent.js'))
        open(os.path.join(OUT, 'agent.html'), 'w', encoding='utf-8').write(out)

        for fn, attr, title in [('agent-success.html', 'data-success', '게재 확인 중'), ('agent-fail.html', 'data-fail', '결제 미완료')]:
            out = head(f'{title} — 브동산 줍줍찬스', '상담사 카드 결제 결과', f'{SITE}/jupjup/{fn}', robots=True)
            out += f'''
    <div class="wrap jj-head" {attr} aria-live="polite"><h1>{'결제를 확인하고 있습니다' if attr == 'data-success' else '결제가 완료되지 않았습니다'}</h1><p class="jj-sub">{'창을 닫지 말고 잠시만 기다려 주세요.' if attr == 'data-success' else ''}</p></div>
    '''
            out += footer(('/jupjup/jupjup.js', '/jupjup/agent.js'))
            open(os.path.join(OUT, fn), 'w', encoding='utf-8').write(out)

    plan_rows = ''.join(f'<tr><th scope="row">{e(p["label"])}</th><td>{comma(p["price"])}원 · {p["days"]}일 게재</td></tr>' for p in PLANS['plans'])
    biz_rows = ''.join(f'<tr><th scope="row">{e(k)}</th><td>{e(v)}</td></tr>' for k, v in BUSINESS.items() if not str(v).startswith('['))
    out = head('상담사 광고 약관·환불 규정 — 브동산 줍줍찬스', '브동산 줍줍찬스 상담사 카드 광고의 이용 조건과 환불 규정', f'{SITE}/jupjup/terms.html')
    out += f'''
<!-- 초안: 오픈 전 법률 검토를 받아 확정한다. -->
<div class="wrap page jj-terms">
  <h1>상담사 광고 약관·환불 규정</h1>
  <p class="page-sub">시행일 {dt.date.today().strftime('%Y.%m.%d')}</p>
  <section><h2>1. 상품</h2>
    <p>브동산 '줍줍찬스'(전국 미분양 줍줍 현황)의 단지 페이지 맨 아래 '이 단지 분양 상담' 칸에 상담사가 입력한 이름·소속·연락처·소개·사진으로 만든 카드(이하 '상담사 카드')를 게재합니다. 단지당 {PLANS['slotsPerSite']}칸이며 먼저 신청한 순서로 채워집니다.</p>
    <table class="jj-kv"><tbody>{plan_rows}</tbody></table>
  </section>
  <section><h2>2. 게재</h2>
    <ul class="plain">
      {('<li>신청 메일 접수 후 ' + str(PLANS['transfer']['depositHours']) + '시간 안에 입금해 주세요. 그동안 신청한 칸을 맡아 두며, 기한 안에 입금되지 않으면 신청이 취소되고 칸이 다시 열립니다.</li><li>입금이 확인되면 ' + str(PLANS['transfer']['postHours']) + '시간 안에 게재하며, 게재 기간은 게재일(한국 시간)부터 계산합니다.</li>') if TRANSFER else '<li>카드결제가 승인되면 자동으로 게재되며, 보통 1~2분 안에 보입니다. 게재 기간은 결제일(한국 시간)부터 계산합니다.</li>'}
      <li>상담사 카드에는 '광고(AD)' 표시가 붙습니다. 상담사 카드는 단지 목록의 순서·단지 정보와 관계없으며, 브동산은 결제 여부에 따라 단지 정보를 바꾸지 않습니다.</li>
      <li>브동산은 분양을 중개·대행하지 않으며 상담 내용과 계약에 관여하지 않습니다. 상담과 계약에 대한 책임은 상담사와 분양 주체에 있습니다.</li>
    </ul>
  </section>
  <section><h2>3. 쓸 수 없는 내용</h2>
    <ul class="plain">
      <li>수익·시세 차익·가격을 보장하거나 사실과 다른 조건(분양가·혜택·남은 세대 등)을 적는 내용</li>
      <li>다른 사람·회사를 사칭하거나 상담하지 않는 단지에 카드를 올리는 경우</li>
      <li>욕설·비방, 다른 사이트로 유도하는 링크(카카오톡 오픈채팅 링크는 허용)</li>
    </ul>
    <p>위 내용이 확인되거나 신고가 들어오면 브동산은 사전 통지 없이 카드를 내릴 수 있으며, 이 경우 환불하지 않습니다.</p>
  </section>
  <section><h2>4. 환불</h2>
    <ul class="plain">
      {'<li>칸 마감 등으로 게재하지 못하면 입금액 전액을 입금하신 계좌로 돌려드립니다.</li>' if TRANSFER else '<li>칸 마감·시스템 오류로 게재되지 못한 결제는 자동으로 전액 취소됩니다.</li>'}
      <li>게재가 시작된 뒤 상담사가 중단을 요청하면 남은 기간을 날짜 단위로 계산해 환불합니다.</li>
      <li>단지의 선착순 분양 마감이 확인되면 카드는 남은 기간 동안 그대로 두며, 상담사가 원하면 남은 기간을 날짜 단위로 환불합니다.</li>
      <li>환불·수정 요청은 <a href="/contact.html">문의 페이지</a>로 주문 번호와 함께 보내 주세요. {'환불은 요청하신 계좌로 이체합니다.' if TRANSFER else '카드결제 취소는 카드사 사정에 따라 3~7영업일이 걸릴 수 있습니다.'}</li>
    </ul>
  </section>
  <section><h2>5. 개인정보</h2>
    <p>상담사 카드에 입력한 정보는 카드 게재와 결제 처리에만 쓰며, 이름·소속·휴대폰 번호·카카오톡 링크·사진은 게재 기간 동안 단지 페이지에 공개됩니다. 게재가 끝난 카드는 요청 시 지체 없이 삭제합니다. {'신청 정보는 상담사가 보낸 메일로 받으며, 입금 확인과 환불에 필요한 범위에서만 씁니다.' if TRANSFER else '결제는 토스페이먼츠가 처리하며 브동산은 카드 번호를 받거나 저장하지 않습니다.'} 자세한 내용은 <a href="/privacy.html">개인정보처리방침</a>을 따릅니다.</p>
  </section>
  <section><h2>6. 사업자 정보</h2>
    <table class="jj-kv"><tbody>{biz_rows}</tbody></table>
  </section>
</div>
'''
    out += footer(())
    open(os.path.join(OUT, 'terms.html'), 'w', encoding='utf-8').write(out)


def update_privacy():
    p = os.path.join(ROOT, 'privacy.html')
    t = open(p, encoding='utf-8').read()
    t = re.sub(r'\n  <section id="jupjup-agents">.*?</section>\n', '\n', t, flags=re.S)
    block = '''
  <section id="jupjup-agents">
    <h2>8. 줍줍찬스 상담사 카드(유료 광고)</h2>
    <ul class="plain">
      <li>수집 항목: 분양 상담사가 직접 입력한 이름, 소속, 휴대폰 번호, 카카오톡 오픈채팅 링크(선택), 한 줄 소개, 사진(선택), 신청 메일 주소''' + (', 입금자명' if PLANS.get('payment') == 'transfer' else '') + '''</li>
      <li>이용 목적: 단지 페이지의 상담사 카드 게재, 결제·환불 처리, 문의 응대. 이름·소속·휴대폰 번호·링크·사진은 상담사의 동의에 따라 게재 기간 동안 공개됩니다.</li>
      <li>결제: ''' + ('계좌이체로 받으며, 상담사가 보낸 신청 메일과 입금 내역은 입금 확인·환불에만 씁니다.' if PLANS.get('payment') == 'transfer' else '카드결제는 토스페이먼츠(주)가 처리하며, 사이트는 카드 번호를 받거나 저장하지 않습니다.') + '''</li>
      <li>보유 기간: 게재 기간이 끝나면 화면에서 내리고, 요청 시 지체 없이 삭제합니다. 다만 전자상거래 등에서의 소비자보호에 관한 법률에 따라 대금 결제 기록은 5년간 보관합니다.</li>
    </ul>
  </section>
'''
    t = t.replace('</div>\n\n<footer>', block + '</div>\n\n<footer>', 1)
    open(p, 'w', encoding='utf-8').write(t)


def update_sitemap(keys):
    p = os.path.join(ROOT, 'sitemap.xml')
    sm = open(p, encoding='utf-8').read()
    sm = re.sub(r'\s*<url><loc>https://www\.brandongsan\.com/jupjup/[^<]*</loc>.*?</url>', '', sm)
    today = dt.date.today().isoformat()
    urls = [f'{SITE}/jupjup/'] + [f'{SITE}/jupjup/{k if k.endswith(".html") else k + ".html"}' for k in keys]
    block = ''.join(f'\n  <url><loc>{u}</loc><lastmod>{today}</lastmod><changefreq>weekly</changefreq><priority>0.7</priority></url>' for u in urls)
    body = sm.rstrip()
    if body.endswith('</urlset>'):
        body = body[:-len('</urlset>')].rstrip()
    sm = body + block + '\n</urlset>\n'
    open(p, 'w', encoding='utf-8').write(sm)


def update_nav():
    """사이트 상단 메뉴(카테고리·소개 페이지)에 '미분양 줍줍' 링크('줍줍찬스')를 넣는다."""
    pat = re.compile(r'(<a href="(?:/)?realestate\.html">부동산이야기</a>)(\s*)(?!<a href="/jupjup/">)')
    for f in glob.glob(os.path.join(ROOT, '*.html')):
        t = open(f, encoding='utf-8').read()
        if 'class="site-nav"' not in t:
            continue
        t1 = t.replace('<a href="/jupjup/">미분양 줍줍</a>', '<a href="/jupjup/">줍줍찬스</a>').replace('<a href="/jupjup/">줍줍몰</a>', '<a href="/jupjup/">줍줍찬스</a>')
        if t1 != t:
            open(f, 'w', encoding='utf-8').write(t1)
            continue
        if '/jupjup/' in t.split('class="site-nav"', 1)[1].split('</nav>', 1)[0]:
            continue
        t2 = pat.sub(lambda m: m.group(1) + m.group(2) + '<a href="/jupjup/">줍줍찬스</a>' + m.group(2), t, count=1)
        if t2 != t:
            open(f, 'w', encoding='utf-8').write(t2)


def main():
    os.makedirs(OUT, exist_ok=True)
    sites, regions = collect()
    closed = merge_closed(sites)
    # 기본 정렬: 바로 입주 → 입주 빠른 순 (목록 화면 기본값과 같게)
    sites.sort(key=lambda s: (0 if s['done'] else 1, s['yr'] * 12 + s['mo'], 0 if (s['aerial'] or s['location']) else 1, -s['n']))
    build_index(sites, regions, closed)
    by_r = {}
    for s in sites:
        by_r.setdefault(s['rid'], []).append(s)
    for s in sites + closed:
        others = [x for x in by_r.get(s['rid'], []) if x['key'] != s['key']]
        others.sort(key=lambda x: (x['sido'] != s['sido'], -x['n']))
        build_detail(s, others, PLANS)
    json.dump({'updated': dt.date.today().isoformat(), 'regions': regions, 'sites': sites + closed},
              open(os.path.join(OUT, 'data.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    build_agent_pages(sites, regions)
    # 줍줍에 들어온 단지의 청약 분석 글 중 예상 프리미엄이 분양가 대비 -3%보다 낮은 글은 내리고 줍줍 페이지로 연결
    import takedown
    taken = takedown.run(sites)
    update_sitemap([s['key'] for s in sites + closed] + ['agent.html', 'terms.html'])
    update_nav()
    update_privacy()
    print(f'jupjup: {len(sites)} open, {len(closed)} closed, {len(regions)} regions, {len(taken)} 청약 글 리다이렉트')


if __name__ == '__main__':
    main()
