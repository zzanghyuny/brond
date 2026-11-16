#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""지방 권역판 랭킹 글 빌더 — 이미지 수집 · 사이트 글 · 네이버 글 · 등록(posts-data/manifest/sitemap/feed).

사용(저장소 루트에서):
  RID=<rid> python3 scripts/firstcome/region_build.py images     # regions/<rid>.json의 img URL → posts/images/<slug>/<key>-aerial|location.jpg + images.json
  RID=<rid> python3 scripts/firstcome/region_charts.py           # 차트·인포그래픽
  RID=<rid> python3 scripts/firstcome/region_build.py build      # posts/<slug>.html + naver-html/<slug>.html
  RID=<rid> python3 scripts/firstcome/region_build.py register   # posts-data.js · posts-manifest.json · sitemap.xml · feed.xml
수도권판은 build2.py(기존)를 쓴다. 글 구조·서식은 수도권판과 같다.
"""
import os, sys, json, re, io, subprocess, html as H
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import fcdata as F
from fcdata import D, T, META, N, NP, B1, B2, B3, SLUG, LABEL, AREAS, D_DOT, D_SP, D_KO, D_MD, fmt, pct
ROOT = F.ROOT
SRC = json.load(open(os.path.join(HERE, 'regions', f'{F.RID}.json'), encoding='utf-8'))
BASE = f'https://www.brandongsan.com/posts/images/{SLUG}/'
def eok(v): return f"{v:.2f}억"
def size(o): return o.get('size', '84')
def status_word(o): return '준공' if o.get('done') else '입주예정'
top = D[:3]
TITLE_S = f"{LABEL} - 미분양 선착순 단지 TOP{N} | {F.HOOK}, 1위 {top[0]['name']} 예상 프리미엄은 {fmt(top[0]['final'])}"
NT = f"{LABEL} 미분양 선착순 단지 TOP{N} | {F.HOOK_N}"
TAGS = META.get('tags', ['미분양아파트', '선착순분양', '잔여세대', '동호수지정', '예상프리미엄', '브동산'])

# ------------------------------------------------------------------ 이미지
def cmd_images():
    from PIL import Image
    os.makedirs(F.IMG_DIR, exist_ok=True); js = {}; miss = []
    for s in SRC['sites']:
        im = s.get('img') or {}; js[s['key']] = {}
        for kind in ('aerial', 'location'):
            u = im.get(kind)
            if not u: miss.append((s['name'], kind)); continue
            raw = f"/tmp/fc-img-{F.RID}-{s['key']}-{kind}"
            r = subprocess.run(['curl', '-sSL', '-m', '60', '-A', 'Mozilla/5.0', '-o', raw, u])
            try:
                a = Image.open(raw).convert('RGB')
            except Exception:
                miss.append((s['name'], kind + ' 다운로드 실패')); continue
            w, h = a.size
            if kind == 'location' and h > w * 1.45:   # 세로로 긴 홍보물: 지도가 있는 위쪽 구간만
                a = a.crop((0, int(w * 0.05), w, int(w * 1.15)))
            if a.width > 900: a = a.resize((900, round(a.height * 900 / a.width)), Image.LANCZOS)
            fn = f"{s['key']}-{kind}.jpg"; a.save(F.IMG_DIR + fn, 'JPEG', quality=82, optimize=True, progressive=True)
            js[s['key']][kind] = {'file': fn, 'src': im.get('src', '분양 홍보 페이지')}
    json.dump(js, open(F.IMG_DIR + 'images.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('images ok; missing:', miss)

# ------------------------------------------------------------------ 공통 조각
IMG = F.IMGJ
def imgpair(o):
    m = IMG.get(o['key'], {}); cells = []; caps = []
    for kind, lab in (('aerial', '조감도'), ('location', '위치도')):
        x = m.get(kind)
        if not x: continue
        cells.append(f"<td style='width:50%;padding:2px;border:none'><img src='images/{SLUG}/{x['file']}' alt='{H.escape(o['name'])} {lab}' style='width:100%;display:block;'></td>")
        caps.append(f"{lab}: {x['src']}")
    if not cells: return ''
    return f"<table style='border:none'><tbody><tr>{''.join(cells)}</tr></tbody></table><p class='note'>이미지 · {' / '.join(caps)}</p>"
def imgstack(o):
    m = IMG.get(o['key'], {}); h = ''
    for kind, lab in (('aerial', '조감도'), ('location', '위치도')):
        x = m.get(kind)
        if x: h += f"<img src='{BASE}{x['file']}' alt='{H.escape(o['name'])} {lab}' style='width:100%;display:block;'><p class='note'>{lab} · {x['src']}</p>"
    return h
def one(o): return T.get(o['key'], ['', ''])[1]
def desc(o): return T.get(o['key'], ['', ''])[0]
def conf(o): return f" · 데이터 신뢰도 {o['conf']}" if o.get('conf') else ''
def rng(a, b):
    xs = [o['pct'] for o in D[a:b]]
    return max(xs), min(xs)

def summary_sentence():
    if NP:
        return f"분양가보다 적정가격이 높게 나온 곳은 {NP}곳이고, 1위 {top[0]['name']}가 {pct(top[0])}({fmt(top[0]['final'])})다."
    return f"분양가보다 적정가격이 높게 나온 곳은 없었다. 1위 {top[0]['name']}는 분양가와 적정가격 차이가 가장 작은 단지로 {pct(top[0])}({fmt(top[0]['final'])})다."
def dist_sentence():
    return f"0~-5% 구간에 {B1}곳, -5~-10% 구간에 {B2}곳, -10%보다 큰 단지가 {B3}곳이다."

# ------------------------------------------------------------------ 지난 회차 대비
def compare():
    pd, prev = F.prev_result()
    if not prev: return None
    pr = {o['key']: o for o in prev}; cur = {o['key']: o for o in D}
    rows = []
    for o in D:
        p = pr.get(o['key'])
        if p: rows.append((o, p['rank'], p['pct'], 'up' if o['rank'] < p['rank'] else 'down' if o['rank'] > p['rank'] else 'same'))
        else: rows.append((o, None, None, 'new'))
    dropped = [p for k, p in pr.items() if k not in cur]
    return pd, rows, dropped
def compare_html(naver=False):
    c = compare()
    if not c: return ''
    pd, rows, dropped = c
    def mv(r):
        o, pr_, pp, st = r
        if st == 'new': return '신규'
        d = pr_ - o['rank']
        return f"▲{d}" if d > 0 else f"▼{-d}" if d < 0 else '-'
    if naver:
        t = "<table><thead><tr><th>단지(이번 순위)</th><th>변동</th></tr></thead><tbody>" + ''.join(f"<tr><td>{r[0]['rank']}. {H.escape(r[0]['name'])}</td><td>{mv(r)}</td></tr>" for r in rows) + "</tbody></table>"
    else:
        t = "<div class='tblwrap'><table><thead><tr><th>이번 순위</th><th>단지</th><th>지난 순위</th><th>변동</th><th>증감률 변화</th></tr></thead><tbody>" + ''.join(
            f"<tr><td class='num'>{o['rank']}</td><td>{H.escape(o['name'])}</td><td class='num'>{pr_ or '-'}</td><td class='num'>{mv((o, pr_, pp, st))}</td><td class='num'>{(f'{pp:+.1f}% → ' if pp is not None else '')}{pct(o)}</td></tr>" for o, pr_, pp, st in rows) + "</tbody></table></div>"
    new = [r[0]['name'] for r in rows if r[3] == 'new']
    txt = f"지난 회차({pd}) 대비 새로 들어온 단지 {len(new)}곳, 빠진 단지 {len(dropped)}곳" + (f"(빠짐: {', '.join(p['name'] for p in dropped)})" if dropped else '') + '.'
    return t + (f"<p><b>{H.escape(txt)}</b></p>" if naver else f"<p class='note'>{H.escape(txt)} 빠진 단지는 계약 완료·선착순 종료·조건 미확인 등으로 이번 회차 기준에 들지 않은 곳이다.</p>")

# ------------------------------------------------------------------ 사이트 글
def site_html():
    rows = ''.join(f"<tr><td class='num'>{o['rank']}</td><td>{'<b>' if o['rank'] <= 3 else ''}{H.escape(o['name'])}{'</b>' if o['rank'] <= 3 else ''}<br><span class='note'>{H.escape(o['region'])} · {size(o)}㎡</span></td><td class='num'>{eok(o['base'])}</td><td class='num'>{eok(o['fair'])}</td><td class='num'>{fmt(o['final'])}</td><td class='num'><b>{pct(o)}</b></td></tr>" for o in D)
    rank_tbl = f"<div class='tblwrap'><table><thead><tr><th>순위</th><th>단지</th><th>기준 분양가</th><th>적정가격</th><th>예상 프리미엄</th><th>증감률</th></tr></thead><tbody>{rows}</tbody></table></div>"
    cards = ''
    for o in D:
        ct = ''.join(f"{H.escape(c['comp'])} {eok(c['price'])}<span class='note'>({H.escape(c['deal'])}) → 보정 {eok(c['adj'])}</span><br>" for c in o['comps'])
        nt = ''.join(f"<li class='note'>{H.escape(x)}</li>" for k, x in o['notes'])
        extra = f"<li class='note'>원 계산값 {fmt(o['raw'], True)}에 {o['basis']}을 적용</li>" if o['basis'] else ''
        cards += f"""<h3>{o['rank']}위. {H.escape(o['name'])} <span class='note'>{pct(o)}</span></h3>
<p><b>{H.escape(one(o))}</b></p>
<p class='note'>{H.escape(o['region'])} · {H.escape(o['builder'])} · {o['n']:,}세대 · {o['yr']}.{o['mo']:02d} {status_word(o)} · 평점 {o['score']}점{conf(o)}</p>
<table class='kv'><tbody><tr><th>분양가</th><td>{H.escape(o['price_note'])}{f" → 실질 {eok(o['base'])}" if o.get('benefit') else ''}</td></tr><tr><th>비교 기준</th><td>{ct}</td></tr><tr><th>적정가격</th><td>{eok(o['fair'])}</td></tr><tr><th>예상 프리미엄</th><td><b>{fmt(o['final'], True)} ({pct(o)})</b></td></tr></tbody></table>
{imgpair(o)}
<p>{H.escape(desc(o))}</p>
{f"<ul>{nt}{extra}</ul>" if (nt or extra) else ''}
"""
    exc = SRC.get('excluded', [])
    exc_txt = (f" 후보 중 {len(exc)}곳은 선착순 확인이 안 되거나 분양가·비교 거래를 확인하지 못해 뺐다." if exc else '')
    metro_local = ('연령 보정 상한은 1.2배(수도권 기준)다.' if all(o.get('cls', 'metro') == 'metro' for o in D) and F.RID == 'sudogwon' else
                   '광역시 단지는 연령 보정 상한 1.2배, 그 밖의 지방 단지는 1.3배를 썼고, 지하철이 없는 지방 단지는 교통 점수를 터미널·KTX, 배정 초등학교, 중심상권 거리로 매겼다.')
    groups = META.get('groups', [])
    gtbl = "<table><thead><tr><th>구분</th><th>단지</th></tr></thead><tbody>" + ''.join(f"<tr><td><b>{H.escape(a)}</b><br><span class='note'>{H.escape(b)}</span></td><td>{' · '.join(H.escape(x) for x in names)}</td></tr>" for a, b, names in groups) + "</tbody></table>"
    srcs = list(META.get('sources', []))
    seen = {u for _, u in srcs}
    for o in D:
        for c in o['comps']:
            if c.get('src') and c['src'] not in seen: srcs.append((f"{c['comp']} — 비교단지 시세", c['src'])); seen.add(c['src'])
    body = f"""<h2>1. 핵심 요약 — 지금 동·호수를 골라 살 수 있는 {N}곳, 남는 곳이 있나?</h2>
<p>청약통장 없이 동·호수를 골라 계약할 수 있는 {AREAS} 미분양 선착순 단지 {N}곳을 브동산 모형으로 계산했다. <b>{summary_sentence()}</b></p>
<div class='stat'><div class='note'>1위 · {H.escape(top[0]['name'])}</div><div class='big'>{pct(top[0])} ({fmt(top[0]['final'], True)})</div><div>기준 분양가 {eok(top[0]['base'])} · 적정가격 {eok(top[0]['fair'])}</div></div>
<p><b>{' · '.join(f"{o['rank']}위 {H.escape(o['name'])}({pct(o)})" for o in top)}.</b> {dist_sentence()}</p>
<img src='images/{SLUG}/chart-top.png' style='width:100%;display:block;' alt='{LABEL} 미분양 선착순 TOP{N} 예상 프리미엄 증감률 순위 그래프'>
<p class='note'>이미지 01 · 분양가 대비 예상 프리미엄(%) 순위. 괄호 안은 금액.</p>
{rank_tbl}
<p class='note'>기준 분양가는 대표 타입 최고가이며, 확정된 현금 페이백만 뺐다. 84㎡가 없는 단지는 59㎡끼리 비교했다.</p>
{('<h2>지난 회차 대비</h2>' + compare_html()) if compare() else ''}
<h2>2. 어떻게 골랐고, 어떻게 계산했나</h2>
<p>청약홈 무순위·임의공급과 청약 접수 중이거나 예정인 단지는 뺐다. 기사·분양 사이트·블로그에서 후보를 모은 뒤, 공식 분양 사이트에 선착순 동·호 지정이 떠 있거나 최근 한 달 안에 분양 상담사의 블로그·카페 영업 글이 있는 단지만 남겼다.{exc_txt} 이렇게 {N}곳이다.</p>
<p>계산은 수도권판과 같은 브동산 약식 모형이다. 단지마다 평점(입지 40·브랜드 20·상품성 40)을 매기고, 같은 생활권 신축 1곳과 가까운 중심권 신축 대단지 1곳의 시세(KB 일반거래가가 있으면 그 값, 없으면 리치고 시세·최근 실거래)를 평점 보정과 연령 보정으로 고쳐 평균을 냈다. {metro_local} 마이너스 1억원 안쪽은 선분양 수요를 감안해 절반으로, 1억~1.5억원은 계약금 하한을 감안해 3천만원 줄였다(6-1 조정). 이미 준공된 단지는 자기 단지 시세를 적정가로 썼고, 옆에 먼저 나온 미분양 단지가 있으면 그 가격을 상한으로 뒀다. 순위는 금액이 아니라 분양가 대비 증감률로 매겼다.</p>
<p>지방은 최근 신축 거래가 적은 곳이 많아 단지마다 데이터 신뢰도(상·중·하)를 함께 적었다. '하'는 같은 생활권 신축 비교가 없거나 거래가 적어 적정가가 흔들릴 수 있다는 뜻이다.</p>
<h2>3. 순위별 단지 정보</h2>
{cards}
<h2>4. 숫자 뒤에 있는 리스크</h2>
{''.join(f'<p>{H.escape(p)}</p>' for p in META.get('risks', []))}
<h2>5. 결론</h2>
{''.join(f'<p>{"<b>" if i == 0 else ""}{H.escape(p)}{"</b>" if i == 0 else ""}</p>' for i, p in enumerate(META.get('conclusion', [])))}
{gtbl}
<p>선착순 단지는 판촉 조건이 붙는 순간 순위가 바뀐다. 브동산은 이 랭킹을 {F.CYCLE} 다시 계산해 올린다.</p>
<h3>출처</h3>
<ul>{''.join(f"<li class='note'><a href='{H.escape(u)}'>{H.escape(t)}</a></li>" for t, u in srcs)}</ul>
<p class='note'>본 글은 정보 제공 목적이며 투자 권유나 매수·계약 대행이 아니다. 브동산 모형은 공개 시세·실거래와 자체 평점으로 계산한 추정치이며, 실제 계약 전에는 입주자모집공고와 분양 사무실 안내를 확인해야 한다.</p>
"""
    desc_meta = f"{D_KO} 기준 {AREAS} 미분양 선착순 아파트 {N}곳의 예상 프리미엄을 브동산 모형으로 계산해 분양가 대비 증감률 순으로 정리했다. 1위는 {top[0]['name']}({pct(top[0])})."
    ref = open(os.path.join(ROOT, 'posts', 'sudogwon-firstcome-top30-202611.html'), encoding='utf-8').read()
    head = ref[:ref.index('<body')]
    head = head.replace('https://www.brandongsan.com/posts/sudogwon-firstcome-top30-202611.html', f'https://www.brandongsan.com/posts/{SLUG}.html')
    head = re.sub(r'<title>.*?</title>', f'<title>{LABEL} 미분양 선착순 단지 TOP{N} | 브동산</title>', head, count=1, flags=re.S)
    head = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{H.escape(desc_meta)}">', head, count=1)
    foot = ref[ref.index('<footer>'):]
    return head + f"""<body>
<div class="top-eyebrow"><div class="wrap"><a class="brand-mark" href="https://brandongsan.com/"><span class="bm-b">브</span><span class="bm-rest">동산</span></a><a class="list-btn" href="https://brandongsan.com/realestate.html">☰ 목록</a></div></div>
<div class="wrap">
<div class="titleblock"><h1>{H.escape(TITLE_S)}</h1></div>
<div class="byline"><span class="avatar">브</span><span class="who">브동산</span><span class="dot">·</span><span class="when">{D_SP}</span><span class="tag">미분양 랭킹 No.{F.SERIES_NO:03d}</span></div>
</div>
<div class="hairline"></div>
<div class="wrap content">
{body}
</div>
""" + foot

# ------------------------------------------------------------------ 네이버 글
NSTYLE = "body{font-family:'Malgun Gothic','Apple SD Gothic Neo',sans-serif;line-height:1.8;font-size:16px;color:#000;max-width:720px;margin:0 auto;padding:24px}h1{font-size:25px}h2{font-size:21px}h3{font-size:17px}table{width:100%;border-collapse:collapse;margin:12px 0;font-size:14px}th,td{border:1px solid #D8D8D8;padding:7px;vertical-align:top}th{background:#F5F5F5}.note{font-size:13px;color:#8A8A8A}.stat{border:1px solid #111;padding:14px;margin:12px 0}img{max-width:100%}"
BL = "<p>&nbsp;</p>"
def naver_html():
    ntop = ''.join(f"<tr><td>{o['rank']}. {H.escape(o['name'])}</td><td style='white-space:nowrap'><b>{pct(o)}</b><br>{fmt(o['final'])}</td></tr>" for o in D)
    parts = ''
    for gi, a in enumerate(range(0, N, 10), 1):
        b = min(N, a + 10); hi, lo = rng(a, b); title = f"{a + 1}~{b}위"
        parts += f"<h3>{title}</h3>\n<img src='{BASE}chart-m-{gi}.png' alt='{title} 예상 프리미엄 순위' style='width:100%;display:block;'>\n<p class='note'>{title} · 분양가 대비 예상 프리미엄(%), 괄호는 금액</p>\n{BL}"
        for o in D[a:b]:
            parts += f"""<p><b>{o['rank']}위 {H.escape(o['name'])} · {pct(o)} ({fmt(o['final'])})</b></p>
<p><b>{H.escape(one(o))}</b></p>
{imgstack(o)}
<p>{H.escape(o['region'])} · {H.escape(o['builder'])} · {o['n']:,}세대 · {o['yr']}.{o['mo']:02d} {status_word(o)} · {H.escape(o['price_note'])}</p>
{BL}"""
        parts += f"<p><b>{title}는 분양가 대비 {hi:+.1f}% ~ {lo:+.1f}% 구간입니다.</b></p>\n{BL}"
    groups = META.get('groups', [])
    gt = "<table><thead><tr><th>구분</th><th>단지</th></tr></thead><tbody>" + ''.join(f"<tr><td><b>{H.escape(a)}</b><br>{H.escape(b)}</td><td>{' · '.join(H.escape(x) for x in names)}</td></tr>" for a, b, names in groups) + "</tbody></table>"
    concl = META.get('conclusion_naver') or META.get('conclusion', [])
    lead = (f"플러스는 {NP}곳이었습니다." if NP else "분양가보다 적정가격이 높은 곳은 없었고, 1위는 시세와의 차이가 가장 작은 곳입니다.")
    meta = f"""<meta name="robots" content="noindex,nofollow">
<!--
slug: {SLUG}
title: {NT}
category: 부동산
naver_category: 부동산이야기
tags: {','.join(TAGS)}
cover_candidates: chart-summary.png
-->"""
    return f"""<!doctype html><html lang='ko'><head><meta charset='utf-8'>
{meta}
<title>{H.escape(NT)} — 네이버 블로그 복사용</title><style>{NSTYLE}</style></head><body>
<p class='note'>브동산 · {LABEL} 미분양 선착순 랭킹 · {D_SP} 기준</p>
<h1>{H.escape(NT)}</h1>
{BL}
<h2>1. 결론부터 — {N}곳 중 1위는 {H.escape(top[0]['name'])}</h2>
<p>청약통장 없이 동·호수를 골라 살 수 있는 {AREAS} 미분양 선착순 단지 {N}곳을 브동산 방식으로 계산했습니다. <b>{lead}</b></p>
<img src='{BASE}chart-summary.png' alt='{LABEL} 미분양 선착순 TOP{N} 요약 인포그래픽' style='width:100%;display:block;'>
<p class='note'>이미지 01 · 1위 단지와 증감률 분포</p>
<p>1위 {H.escape(top[0]['name'])}의 브동산 분석 적정가격은 <b>{eok(top[0]['fair'])}원</b>, 분양가는 <b>{eok(top[0]['base'])}원</b>입니다.</p>
{BL}
<table><thead><tr><th>순위·단지</th><th>프리미엄</th></tr></thead><tbody>{ntop}</tbody></table>
<p><b>순위는 금액이 아니라 분양가 대비 증감률입니다. 0~-5% 구간에 {B1}곳, -10%보다 큰 곳이 {B3}곳입니다.</b></p>
<p class='note'>분양가는 대표 타입 최고가, 확정된 현금 페이백만 차감. 84㎡가 없는 단지는 59㎡ 기준.</p>
{BL}
{('<h2>지난 회차 대비</h2>' + compare_html(True) + BL) if compare() else ''}
<h2>2. 이렇게 계산했습니다</h2>
<img src='{BASE}chart-method.png' alt='브동산 모형 계산 순서' style='width:100%;display:block;'>
<p class='note'>이미지 02 · 계산 순서</p>
<table><tbody><tr><th>대상</th><td>{D_MD} 현재 선착순 동·호 지정 중인 {AREAS} 아파트 {N}곳(청약홈 무순위·청약 예정 제외)</td></tr><tr><th>확정 기준</th><td>분양 홈페이지에 선착순이 떠 있거나, 최근 한 달 안에 분양 상담 글이 있는 단지</td></tr><tr><th>기준 평형</th><td>84㎡ 최고가(없으면 59㎡)</td></tr><tr><th>적정가격</th><td>같은 생활권 신축 2곳의 시세를 평점·연식으로 보정해 평균. 준공 단지는 자기 단지 시세, 옆 단지가 미분양이면 그 가격을 상한으로</td></tr><tr><th>순위</th><td>분양가 대비 증감률(%)</td></tr></tbody></table>
<p><b>지방은 거래가 적은 곳이 많아, 단지마다 데이터 신뢰도(상·중·하)를 홈페이지 글에 함께 적었습니다.</b></p>
{BL}
<h2>3. 순위별 단지 정보</h2>
{parts}
<h2>4. 브동산 한줄평</h2>
<img src='{BASE}chart-picks.png' alt='브동산 한줄평 3묶음' style='width:100%;display:block;'>
<p class='note'>이미지 · 한줄평 3묶음</p>
{gt}
{BL}
<h2>5. 결론</h2>
{''.join(f'<p><b>{H.escape(p)}</b></p>' if i == 0 else f'<p>{H.escape(p)}</p>' for i, p in enumerate(concl))}
<p>단지별 비교단지와 보정 과정은 <a href='https://www.brandongsan.com/posts/{SLUG}.html'>브동산 홈페이지</a>에서 확인하실 수 있습니다. 브동산은 이 랭킹을 {F.CYCLE} 다시 계산해 올립니다.</p>
<p class='note'>본 글은 정보 제공 목적이며 투자 권유가 아닙니다. 계약 전에는 입주자모집공고와 분양 사무실 안내를 반드시 확인하세요.</p>
</body></html>"""

def cmd_build():
    open(os.path.join(ROOT, 'posts', f'{SLUG}.html'), 'w', encoding='utf-8').write(site_html())
    open(os.path.join(ROOT, 'naver-html', f'{SLUG}.html'), 'w', encoding='utf-8').write(naver_html())
    print('built', SLUG, N, NP)

# ------------------------------------------------------------------ 등록
def cmd_register():
    pd = os.path.join(ROOT, 'posts-data.js'); p = open(pd, encoding='utf-8').read()
    if f'id: "{SLUG}"' not in p:
        prev = f"<p>청약통장 없이 동·호수를 골라 계약할 수 있는 {AREAS} 미분양 선착순 단지 {N}곳을 브동산 모형으로 계산해 분양가 대비 증감률 순으로 정리했다. 1위는 {top[0]['name']}({pct(top[0])}, {fmt(top[0]['final'])})다.</p>"
        y, m, d = F.RANK_DATE.split('-')
        entry = f'  {{ id: "{SLUG}", category: "realestate", region: "{LABEL}", tag: "미분양 랭킹 No.{F.SERIES_NO:03d}", title: "{TITLE_S}", date: "{F.RANK_DATE}", dateLabel: "{int(y)}. {int(m)}. {int(d)}", url: "posts/{SLUG}.html", preview: `{prev}` }},\n'
        p = p.replace("const POSTS = [\n", "const POSTS = [\n" + entry, 1); open(pd, 'w', encoding='utf-8').write(p)
    sm = os.path.join(ROOT, 'sitemap.xml'); s = open(sm, encoding='utf-8').read()
    if f'posts/{SLUG}.html' not in s:
        new = f"  <url>\n    <loc>https://www.brandongsan.com/posts/{SLUG}.html</loc>\n    <lastmod>{F.RANK_DATE}</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>0.8</priority>\n  </url>\n"
        i = s.index("  <url>\n    <loc>https://www.brandongsan.com/posts/"); s = s[:i] + new + s[i:]; open(sm, 'w', encoding='utf-8').write(s)
    fx = os.path.join(ROOT, 'feed.xml'); f = open(fx, encoding='utf-8').read()
    if f'posts/{SLUG}.html</link>' not in f:
        import datetime
        dt = datetime.datetime.strptime(F.RANK_DATE, '%Y-%m-%d') + datetime.timedelta(hours=12 + F.SERIES_NO)
        pub = dt.strftime('%a, %d %b %Y %H:%M:%S +0900')
        item = f"""    <item>
      <title>{H.escape(TITLE_S)}</title>
      <link>https://www.brandongsan.com/posts/{SLUG}.html</link>
      <guid isPermaLink="true">https://www.brandongsan.com/posts/{SLUG}.html</guid>
      <pubDate>{pub}</pubDate>
      <category>부동산이야기</category>
      <category>{LABEL}</category>
      <description>{H.escape(D_KO + ' 기준 ' + AREAS + ' 미분양 선착순 아파트 ' + str(N) + '곳의 예상 프리미엄을 브동산 모형으로 계산해 분양가 대비 증감률 순으로 정리했다. 1위는 ' + top[0]['name'] + '(' + pct(top[0]) + ')다.')}</description>
    </item>
"""
        f = f.replace("    <item>\n", item + "    <item>\n", 1)
        f = re.sub(r"<lastBuildDate>.*?</lastBuildDate>", f"<lastBuildDate>{pub}</lastBuildDate>", f, count=1)
        open(fx, 'w', encoding='utf-8').write(f)
    mf = os.path.join(ROOT, 'posts-manifest.json'); m = json.load(open(mf, encoding='utf-8'))
    if not any(x['slug'] == SLUG for x in m['posts']):
        m['posts'].insert(0, {"slug": SLUG, "number": F.SERIES_NO, "title": TITLE_S, "category": "부동산", "naver_category": "부동산이야기", "date": F.RANK_DATE,
                              "site_url": f"https://www.brandongsan.com/posts/{SLUG}.html", "naver_html": f"naver-html/{SLUG}.html", "naver_title": NT,
                              "naver_tags": TAGS, "cover_candidates": [BASE + "chart-summary.png"], "naver_published": False, "naver_post_id": None, "published_at": None})
        json.dump(m, open(mf, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print('registered', SLUG)

def cmd_history():
    hd = os.path.join(HERE, 'history', F.RID); os.makedirs(hd, exist_ok=True)
    json.dump(D, open(os.path.join(hd, f'{F.RANK_DATE}.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('history', os.path.join(hd, f'{F.RANK_DATE}.json'))

if __name__ == '__main__':
    {'images': cmd_images, 'build': cmd_build, 'register': cmd_register, 'history': cmd_history}[sys.argv[1]]()
