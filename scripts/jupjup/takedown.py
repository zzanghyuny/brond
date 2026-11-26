#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""줍줍 코너에 들어온 단지의 청약 분석 글 정리 (Paul 2026-11-26).

규칙: 줍줍 단지와 짝지어진 '부동산이야기' 청약 단지 글 가운데
      예상 프리미엄이 분양가 대비 -3%보다 낮은 글(고평가)은 사이트에서 내리고, 그 주소로 들어오면 줍줍 단지 페이지로 보낸다.
      -3% 이내(적정)이거나 플러스(저평가)인 글은 그대로 둔다.
      상담사 결제 여부와는 관계없다(줍줍에 들어온 단지 전부에 같은 기준).

내리는 방법(여러 번 실행해도 결과 동일):
  vercel.json 영구 리다이렉트 /posts/<slug>.html → /jupjup/<key>.html
  posts-data.js(목록·홈), sitemap.xml, feed.xml, realestate.html·archive.html 정적 목록에서 제거
  글 HTML 파일은 지우지 않는다(되살릴 때는 기록과 위 변경을 되돌린다).
기록: scripts/jupjup/takedown.json   짝: scripts/jupjup/post_map.json
"""
import os, re, json, glob, html as H, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
SITE = 'https://www.brandongsan.com'
THRESHOLD = -3.0  # 예상 프리미엄 ÷ 분양가(%)가 이보다 낮으면 내린다

MAP_F = os.path.join(HERE, 'post_map.json')
REC_F = os.path.join(HERE, 'takedown.json')


def _load(p, default):
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else default


def _norm(s):
    return re.sub(r'[^가-힣a-z0-9]', '', s.lower())


def post_ratio(slug):
    """글의 핵심 요약 박스(stat-pair)에서 적정가·분양가를 읽어 (적정가-분양가)/분양가 %를 돌려준다."""
    p = os.path.join(ROOT, 'posts', f'{slug}.html')
    if not os.path.exists(p):
        return None
    t = open(p, encoding='utf-8').read()
    i = t.find('class="stat-pair"')
    if i < 0:
        return None
    svs = re.findall(r'class="sv">\s*([0-9.,]+)', t[i:i + 2500])
    if len(svs) < 2:
        return None
    fair, sale = float(svs[0].replace(',', '')), float(svs[1].replace(',', ''))
    if sale <= 0:
        return None
    return {'fair': fair, 'sale': sale, 'pct': round((fair - sale) / sale * 100, 1)}


def realestate_posts():
    pd = open(os.path.join(ROOT, 'posts-data.js'), encoding='utf-8').read()
    out = {}
    for m in re.finditer(r'id:\s*"([^"]+)"[^{}]*?category:\s*"([^"]+)"[^{}]*?title:\s*"([^"]+)"', pd, flags=re.S):
        if m.group(2) == 'realestate' and 'firstcome' not in m.group(1):
            out[m.group(1)] = m.group(3)
    return out


def update_map(sites):
    """새 줍줍 단지는 글 제목의 단지명이 정확히 같을 때만 자동으로 짝짓는다. 비슷한 후보는 출력만 한다."""
    data = _load(MAP_F, {'_note': '', 'map': {}, 'none': []})
    m, none = data['map'], set(data.get('none', []))
    posts = realestate_posts()
    names = {slug: t.split(' - ', 1)[-1].split(' | ')[0] for slug, t in posts.items()}
    for s in sites:
        if s['key'] in m or s['key'] in none:
            continue
        n = _norm(s['name'])
        exact = [slug for slug, nm in names.items() if _norm(nm) == n]
        if len(exact) == 1:
            m[s['key']] = exact[0]
            print(f'  post_map: {s["key"]} → {exact[0]} (단지명 일치)')
            continue
        fuzzy = [slug for slug, nm in names.items() if len(_norm(nm)) >= 4 and (_norm(nm) in n or n in _norm(nm))]
        if fuzzy:
            print(f'  post_map 확인 필요: {s["key"]}({s["name"]}) 후보 {fuzzy} — 맞으면 post_map.json "map"에, 아니면 "none"에 넣는다')
    data['map'] = dict(sorted(m.items()))
    json.dump(data, open(MAP_F, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    return data['map']


# ------------------------------------------------------------------ 파일별 제거
def _remove_js_object(src, slug):
    """posts-data.js에서 id가 slug인 객체 하나를 지운다(문자열·템플릿 리터럴 안의 괄호는 건너뜀)."""
    m = re.search(r'id:\s*"' + re.escape(slug) + r'"', src)
    if not m:
        return src
    start = src.rfind('{', 0, m.start())
    if start < 0 or src[start + 1:m.start()].strip():
        return src
    i, depth, q = start, 0, None
    while i < len(src):
        c = src[i]
        if q:
            if c == '\\':
                i += 2
                continue
            if c == q:
                q = None
        elif c in '"\'`':
            q = c
        elif c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                break
        i += 1
    end = i + 1
    rest = src[end:]
    mm = re.match(r'\s*,?[ \t]*\n?', rest)
    end += mm.end() if mm else 0
    line_start = src.rfind('\n', 0, start) + 1
    if src[line_start:start].strip() == '':
        start = line_start
    return src[:start] + src[end:]


def _edit(path, fn):
    p = os.path.join(ROOT, path)
    if not os.path.exists(p):
        return
    t = open(p, encoding='utf-8').read()
    t2 = fn(t)
    if t2 != t:
        open(p, 'w', encoding='utf-8').write(t2)


def _recount_archive(t):
    parts = re.split(r'(?=<section class="archive-group">)', t)
    total = 0
    for i, p in enumerate(parts):
        if not p.startswith('<section class="archive-group">'):
            continue
        n = p.split('</section>', 1)[0].count('<li')
        total += n
        parts[i] = re.sub(r'(<h2>[^<(]*\()\d+(\)</h2>)', lambda x: f'{x.group(1)}{n}{x.group(2)}', p, count=1)
    t = ''.join(parts)
    return re.sub(r'(공개 글 )\d+(개)', lambda x: f'{x.group(1)}{total}{x.group(2)}', t, count=1)


def apply(slug, key):
    url = f'/posts/{slug}.html'
    # 1) 리다이렉트 (호스트 리다이렉트 규칙보다 앞에)
    vp = os.path.join(ROOT, 'vercel.json')
    v = json.load(open(vp, encoding='utf-8'))
    reds = v.setdefault('redirects', [])
    want = {'source': url, 'destination': f'{SITE}/jupjup/{key}.html', 'permanent': True}
    reds[:] = [r for r in reds if r.get('source') != url]
    pos = next((i for i, r in enumerate(reds) if r.get('has')), len(reds))
    reds.insert(pos, want)
    open(vp, 'w', encoding='utf-8').write(json.dumps(v, ensure_ascii=False, indent=2) + '\n')
    # 2) 목록·피드·사이트맵
    _edit('posts-data.js', lambda t: _remove_js_object(t, slug))
    _edit('sitemap.xml', lambda t: re.sub(r'\n?[ \t]*<url>\s*<loc>' + re.escape(SITE + url) + r'</loc>.*?</url>', '', t, flags=re.S))
    _edit('feed.xml', lambda t: re.sub(r'\n?[ \t]*<item>(?:(?!<item>).)*?' + re.escape(SITE + url) + r'</link>(?:(?!<item>).)*?</item>', '', t, flags=re.S))
    li = r'\n?[ \t]*<li[^>]*><a href="/?' + re.escape(url.lstrip('/')) + r'"[^\n]*?</li>'
    _edit('realestate.html', lambda t: re.sub(li, '', t))
    _edit('archive.html', lambda t: _recount_archive(re.sub(li, '', t)))


def run(sites):
    """자동 짝짓기는 하지 않는다(Paul 2026-11-26). takedown.json에 기록된 글만 내린 상태로 유지한다."""
    rec = _load(REC_F, {})
    for slug, r in rec.items():
        apply(slug, r['key'])
    return rec
