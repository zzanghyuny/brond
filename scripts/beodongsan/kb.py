import urllib.parse,urllib.request,json,sys
import time,os
_C='kbcache.json'
_cache=json.load(open(_C)) if os.path.exists(_C) else {}
def get(path,**params):
    u='https://api.kbland.kr/'+path+'?'+urllib.parse.urlencode(params)
    if u in _cache: return _cache[u]
    for k in range(5):
        try:
            r=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=25)
            d=json.loads(r.read().decode()); _cache[u]=d; json.dump(_cache,open(_C,'w'),ensure_ascii=False); return d
        except Exception as e:
            time.sleep(2*(k+1))
    raise RuntimeError('kb fail '+u)
def search(k):
    d=get('land-complex/serch/intgraSerch',검색설정명='SRC_HSCM',검색키워드=k,출력갯수='10',콜센터구분='')
    return [(x['COMPLEX_NO'],x['HSCM_NM'],x.get('JUSO_ARNO')) for x in d['dataBody']['data']['data'].get('HSCM',{}).get('data',[])]
if __name__=='__main__':
    for k in sys.argv[1:]: print(k,search(k))
