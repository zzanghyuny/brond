#!/usr/bin/env python3
"""지역 랭킹 데이터: KB 통합검색으로 구·시 단위 아파트 단지를 전수 수집해 세대수 순위 또는 84㎡ KB 일반거래가 순위를 만든다.
  python3 kb_rank.py hh  out.json "강남구 아파트" "송파구 아파트" ...        # 세대수 순위 (주소 필터: --addr 서울)
  python3 kb_rank.py p84 out.json --addr 인천 "연수구 아파트" ...           # 84㎡ KB 일반거래가 순위 (300세대 이상)
"""
import sys, os, json, argparse
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'beodongsan'))
import kb, kb_detail as k
import urllib.parse, urllib.request, time
_mem = {}
def _get(path, **params):  # 디스크 캐시 없이(대량 수집 시 kb.py의 매 호출 캐시 저장이 병목)
    u = 'https://api.kbland.kr/' + path + '?' + urllib.parse.urlencode(params)
    if u in _mem: return _mem[u]
    for i in range(4):
        try:
            d = json.loads(urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'}), timeout=20).read().decode())
            _mem[u] = d; return d
        except Exception: time.sleep(1.5 * (i + 1))
    raise RuntimeError('kb fail')
kb.get = _get; k.get = _get
_done = [0]

def collect(kws, addr):
    seen = {}
    for kw in kws:
        r = kb.get('land-complex/serch/intgraSerch', 검색설정명='SRC_HSCM', 검색키워드=kw, 출력갯수='300', 콜센터구분='')['dataBody']['data']['data']['HSCM']['data']
        for x in r:
            if x.get('SLND_PERTY_NM') != '아파트' or (addr and addr not in (x.get('BUBADDR') or '') + (x.get('TOTALADDRESS') or '')): continue
            seen[x['COMPLEX_NO']] = dict(no=x['COMPLEX_NO'], name=x['HSCM_NM'], hh=int(x['THS_NUM'] or 0), ym=x['MVIHS_DATE'],
                                         addr=x.get('BUBADDR') or x.get('TOTALADDRESS'), lat=float(x['WGS84_LAT'] or 0), lon=float(x['WGS84_LNG'] or 0))
    return list(seen.values())

def p84(c):
    try:
        best = None
        for seq, ex, sup, n in k.types(c['no']):
            if 83.0 <= float(ex) <= 85.99:
                s = k.sise(c['no'], seq)
                if s and s[0][1]:
                    v = s[0][1] / 10000
                    if best is None or v > best[0]: best = (v, s[0][3], float(ex))
        if best: c.update(p=round(best[0], 2), date=best[1], ex=best[2])
    except Exception as e:
        c['err'] = str(e)[:60]
    _done[0] += 1
    if _done[0] % 50 == 0: print('..', _done[0], flush=True)
    return c

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('mode'); ap.add_argument('out'); ap.add_argument('kw', nargs='+')
    ap.add_argument('--addr', default=''); ap.add_argument('--min-hh', type=int, default=300)
    a = ap.parse_args()
    cs = collect(a.kw, a.addr)
    if a.mode == 'hh':
        cs.sort(key=lambda c: -c['hh'])
    else:
        cs = [c for c in cs if c['hh'] >= a.min_hh]
        with ThreadPoolExecutor(8) as ex: cs = list(ex.map(p84, cs))
        cs = sorted([c for c in cs if c.get('p')], key=lambda c: -c['p'])
    json.dump(cs, open(a.out, 'w'), ensure_ascii=False, indent=0)
    for i, c in enumerate(cs[:15], 1): print(i, c['name'], c['hh'], c['ym'], c.get('p'), c.get('date'), c.get('ex'), c['addr'])
