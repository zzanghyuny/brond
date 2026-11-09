import json,urllib.parse,urllib.request,math,time,os
C='geo_cache.json'
cache=json.load(open(C)) if os.path.exists(C) else {}
def geocode(q,cc='kr'):
    if q in cache: return cache[q]
    u='https://nominatim.openstreetmap.org/search?'+urllib.parse.urlencode({'q':q,'format':'json','limit':'5','countrycodes':cc})
    time.sleep(1.1)
    r=json.loads(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'brandongsan-research/1.0'}),timeout=25).read().decode())
    cache[q]=[(x['display_name'][:80],float(x['lat']),float(x['lon']),x.get('class'),x.get('type')) for x in r]
    json.dump(cache,open(C,'w'),ensure_ascii=False); return cache[q]
def hav(a,b):
    R=6371000;p1,p2=math.radians(a[0]),math.radians(b[0]);dp=p2-p1;dl=math.radians(b[1]-a[1])
    h=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*R*math.asin(math.sqrt(h))
if __name__=='__main__':
    import sys
    for q in sys.argv[1:]:
        print(q); [print('  ',x) for x in geocode(q)]
