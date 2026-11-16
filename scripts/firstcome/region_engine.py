#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""브동산 미분양 선착순 랭킹 — 지역판 공용 엔진 (2026.11.17). 수도권판 firstcome_engine.py와 같은 모형·규칙(L1~L5, 6-1).

사용:  python3 scripts/firstcome/region_engine.py scripts/firstcome/regions/<rid>.json
출력:  scripts/firstcome/regions/<rid>-result.json (+ 콘솔에 계산 과정)

지역 구분(브동산 모형 6번): 'metro' = 서울·수도권·광역시(부산·대구·광주·대전·울산) → 연령보정 맥스 1.2
                           'local' = 기타지방(충남·충북·세종·경북·경남·전북·전남·강원·제주) → 연령보정 맥스 1.3
연령보정은 SITE의 cls를 따른다. 교통(trans, 20점) 채점도 cls에 따라 A(지하철)/B(기타지방: 터미널·KTX 3 + 배정초 9 + 중심상권 8).

데이터 파일(JSON) 형식:
{
 "rid": "chungcheong", "label": "충청권", "areas": "충남·대전·충북·세종", "date": "2026-11-17",
 "comps": { "<ckey>": {"name","yr","mo","n","brand","trans","conv","edu","price"(억, 84㎡ 또는 같은 크기),"deal"(근거·날짜),"src"(URL), "view"(선택, 기본6)} },
 "ceil":  { "<key>": {"name","yr","mo","n","brand","trans","conv","edu","price","src"} },     # L3 주변 미분양 상한(선택)
 "sites": [ {"key","name","region"(시군구 동),"sido","cls":"metro|local","yr","mo"(입주 예정·준공),"n","brand","builder",
             "trans","conv","edu","price"(대표 타입 최고가, 억),"price_note","comps":[ck1,ck2],
             선택: "size"("84" 기본/"59"),"benefit"(억),"benefit_src","own"(준공 단지 자기 시세, 억),"own_src","done"(준공 true),
                   "ceil"(ceil 키),"l5"(비교단지 교체 사유),"warn"(주의 문구),"conf"("상"|"중"|"하" 데이터 신뢰도),
                   "firstcome_src"(선착순 근거 URL·날짜),"price_src"(분양가 근거 URL),
                   "img": {"aerial": "<이미지 URL>", "location": "<이미지 URL>", "src": "출처 이름"} } ],
 "excluded": [ {"name","reason"} ],
 "texts": { "<key>": ["단지 설명 2~3문장(사이트, -다 체)", "한줄평 1~2문장(긍정 톤, 숫자는 정직)"] },
 "meta":  { "title_hook": "...", "groups": [[제목, 설명, [단지명...]], ...3개], "risks": ["문단", ...],
            "conclusion": ["문단", ...], "sources": [[제목, URL], ...], "tags": ["태그", ...] }
}
"""
import json, sys, os

def months(y1, m1, y2, m2): return (y2 - y1) * 12 + (m2 - m1)

def age_mult(diff, cls='metro'):
    if diff < 0: return 1 / age_mult(-diff, cls)
    if cls == 'local':
        if diff <= 120: return 1 + diff / 120 * 0.12
        if diff <= 240: return 1.12 + (diff - 120) / 120 * 0.18
        return 1.3
    if diff <= 120: return 1 + diff / 120 * 0.08
    if diff <= 240: return 1.08 + (diff - 120) / 120 * 0.12
    return 1.2

def score_mult(site, comp): return max(0.8, min(1.2, 1 + (site - comp) * 0.01))
def hh(n): return 10 if n >= 2000 else 9 if n >= 1500 else 8 if n >= 1000 else 7 if n >= 700 else 6 if n >= 500 else 5 if n >= 300 else 3
def prod(year, n, view=6):
    lvl = 8 if year >= 2027 else 7 if year >= 2020 else 6 if year >= 2015 else 5 if year >= 2008 else 4
    park = 5 if year >= 2027 else 4 if year >= 2015 else 3
    bcr = 4 if year >= 2015 else 3
    return lvl + hh(n) + view + park + bcr
def tot(x): return x['trans'] + x['conv'] + x['edu'] + x['brand'] + prod(x['yr'], x['n'], x.get('view', 6))

def adjust61(raw):
    if raw <= -1.5: return raw, None
    if raw < -1.0: return raw + 0.3, '6-1 근거1(계약금 하한)'
    if raw < 0: return raw / 2, '6-1 근거2(선분양 수요)'
    return raw, None

def run(path):
    D = json.load(open(path, encoding='utf-8'))
    comps, CEIL = D['comps'], D.get('ceil', {})
    out = []
    for s in D['sites']:
        ss = tot(s); notes = []; rows = []; cls = s.get('cls', 'metro')
        for ck in s['comps']:
            c = comps[ck]; cs = tot(c); sm = score_mult(ss, cs)
            dm = months(c['yr'], c['mo'], s['yr'], s['mo']); am = age_mult(dm, cls)
            rows.append(dict(comp=c['name'], yr=c['yr'], mo=c['mo'], n=c['n'], score=cs, price=c['price'], deal=c['deal'],
                             src=c.get('src', ''), sm=round(sm, 3), diff=dm, am=round(am, 3), adj=round(c['price'] * sm * am, 4)))
        fair = sum(r['adj'] for r in rows) / len(rows); model_fair = fair
        base = s['price'] - s.get('benefit', 0)
        if s.get('benefit'): notes.append(('L1', f"실질 분양가 {base:.2f}억 = 분양가 {s['price']:.2f}억 − {s['benefit_src']}"))
        if s.get('own'):
            fair = s['own']; notes.append(('L2', f"준공 단지: 자기 단지 시세 {s['own']:.2f}억을 적정가로 사용({s['own_src']}). 모형값 {model_fair:.2f}억은 참고"))
        if s.get('ceil'):
            c = CEIL[s['ceil']]; m = score_mult(ss, tot(c)); cap = c['price'] * m
            if fair > cap:
                notes.append(('L3', f"주변 미분양 상한: {c['name']} {c['price']:.2f}억 × 평점보정 {m:.2f} = {cap:.2f}억으로 제한(모형값 {fair:.2f}억). 근거: {c['src']}"))
                fair = cap
            else:
                notes.append(('L3', f"주변 미분양 상한 {cap:.2f}억 이내라 조정 없음"))
        if s.get('l5'): notes.append(('L5', s['l5']))
        if s.get('warn'): notes.append(('주의', s['warn']))
        raw = fair - base
        fin, basis = (raw, None) if s.get('done') else adjust61(raw)
        capped = False
        if fin > 0 and not s.get('done'):
            lim = base * 0.10
            if fin > lim:
                notes.append(('L4', f"미분양 상한: 계산값 +{fin:.2f}억이 계약금(분양가 10%, {lim:.2f}억)을 넘어 {lim:.2f}억으로 제한"))
                fin = lim; capped = True
        pct = fin / base * 100
        keep = {k: v for k, v in s.items() if k not in ('comps',)}
        out.append(dict(**keep, score=ss, comps=rows, model_fair=round(model_fair, 4), fair=round(fair, 4), base=round(base, 4),
                        raw=round(raw, 4), final=round(fin, 4), basis=basis, capped=capped, pct=round(pct, 1), notes=notes, v1=None))
    out.sort(key=lambda x: -x['pct'])
    for i, o in enumerate(out, 1): o['rank'] = i
    rp = path[:-5] + '-result.json'
    json.dump(out, open(rp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    return out, rp

def fmt(v):
    w = round(v * 1e4 / 10) * 10; sign = '+' if w > 0 else '-' if w < 0 else '±'; a = abs(w)
    return f"{sign}{a/10000:.2f}억" if a >= 10000 else f"{sign}{a:,}만원"

if __name__ == '__main__':
    out, rp = run(sys.argv[1])
    for o in out:
        flag = '  <<재검토(+5% 초과 또는 -20% 미만)' if (o['pct'] > 5 or o['pct'] < -20) else ''
        print(o['rank'], o['name'], '|', o.get('cls'), '|점', o['score'], '|기준', o['base'], '|모형', round(o['model_fair'], 2), '|적정', round(o['fair'], 2),
              '|raw', fmt(o['raw']), '|final', fmt(o['final']), o['basis'] or '', '|', o['pct'], '%', flag)
        for r in o['comps']: print('     ', r['comp'], r['score'], r['price'], 'x', r['sm'], 'x', r['am'], f"({r['diff']}m)", '=', round(r['adj'], 2))
        for n in o['notes']: print('      *', n[0], n[1])
    print('->', rp)
