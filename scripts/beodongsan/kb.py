import urllib.parse,urllib.request,json,sys
import time,os
_C=os.environ.get('KB_CACHE','kbcache.json')
try: _cache=json.load(open(_C,encoding='utf-8')) if os.path.exists(_C) else {}
except Exception: _cache={}
def get(path,**params):
    u='https://api.kbland.kr/'+path+'?'+urllib.parse.urlencode(params)
    if u in _cache: return _cache[u]
    for k in range(5):
        try:
            r=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=25)
            d=json.loads(r.read().decode()); _cache[u]=d; _t=_C+'.%d.tmp'%os.getpid(); json.dump(_cache,open(_t,'w',encoding='utf-8'),ensure_ascii=False); os.replace(_t,_C); return d
        except Exception as e:
            time.sleep(2*(k+1))
    raise RuntimeError('kb fail '+u)
def search(k):
    d=get('land-complex/serch/intgraSerch',검색설정명='SRC_HSCM',검색키워드=k,출력갯수='10',콜센터구분='')
    return [(x['COMPLEX_NO'],x['HSCM_NM'],x.get('JUSO_ARNO')) for x in d['dataBody']['data']['data'].get('HSCM',{}).get('data',[])]
if __name__=='__main__':
    for k in sys.argv[1:]: print(k,search(k))
