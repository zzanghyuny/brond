# -*- coding: utf-8 -*-
"""충칭 편 지도 데이터: Natural Earth(시 경계·강·한국) + OSM Nominatim(구 경계·장소 좌표) → geo.json"""
import json, time, urllib.request, urllib.parse
from shapely.geometry import shape, mapping
from shapely.ops import unary_union
from pyproj import Geod
G = '/home/claude/media/geo/'; UA = 'brandongsan-map/1.0 (contact: brandongsan.com)'
geod = Geod(ellps='WGS84'); area = lambda g: abs(geod.geometry_area_perimeter(g)[0]) / 1e6
def nomi(q, poly=False):
    u = 'https://nominatim.openstreetmap.org/search?' + urllib.parse.urlencode(dict(q=q, format='json', limit=1, polygon_geojson=1 if poly else 0, polygon_threshold=0.0004))
    for k in range(4):
        try:
            r = json.load(urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': UA}), timeout=40)); time.sleep(1.2); return r[0] if r else None
        except Exception as e: print('retry', q, e); time.sleep(4)
out = {}
out['seoul'] = json.load(open('/home/claude/work/ep1/geo.json'))['seoul']
ne = [f for f in json.load(open(G + 'ne_admin1.geojson'))['features'] if f['properties'].get('iso_3166_2') == 'CN-CQ'][0]
cq = shape(ne['geometry']); out['cq'] = mapping(cq); print('CQ NE', round(area(cq)))
kor = [f for f in json.load(open(G + 'ne_countries50.geojson'))['features'] if f['properties'].get('ADM0_A3') == 'KOR'][0]
k = shape(kor['geometry']); out['kor'] = mapping(k); print('KOR', round(area(k)))
for f in json.load(open(G + 'ne_rivers10.geojson'))['features']:
    n = f['properties'].get('name_en') or ''
    if n in ('Yangtze', 'Jialing'): out['riv_' + n.lower()] = f['geometry']
for key, q in [('yuzhong', '渝中区, 重庆市'), ('jiangbei', '江北区, 重庆市'), ('nanan', '南岸区, 重庆市'), ('shapingba', '沙坪坝区, 重庆市'), ('jiulongpo', '九龙坡区, 重庆市'), ('yubei', '渝北区, 重庆市'), ('dadukou', '大渡口区, 重庆市'), ('beibei', '北碚区, 重庆市'), ('banan', '巴南区, 重庆市')]:
    r = nomi(q, True)
    if r and r.get('geojson', {}).get('type') in ('Polygon', 'MultiPolygon'):
        g = shape(r['geojson']); out['d_' + key] = mapping(g.simplify(0.001)); print(key, round(area(g)))
    else: print('no poly', key)
P = {}
for key, q in [('jiefangbei', '解放碑, 渝中区'), ('chaotianmen', '朝天门, 渝中区'), ('hongyadong', '洪崖洞, 渝中区'), ('liziba', '李子坝站'), ('guanyinqiao', '观音桥, 江北区'),
               ('nanping', '南坪, 南岸区'), ('sanxia', '三峡广场, 沙坪坝区'), ('yangjiaping', '杨家坪, 九龙坡区'), ('jiangbeizui', '江北嘴, 重庆'), ('lijia', '礼嘉, 重庆'),
               ('yuelai', '悦来, 重庆'), ('daxuecheng', '重庆大学城'), ('ckg', '重庆江北国际机场'), ('ciqikou', '磁器口, 沙坪坝区'), ('lianhuachi', '大韩民国临时政府旧址, 重庆'),
               ('shanghai', 'Shanghai, China'), ('hangzhou', 'Hangzhou, China'), ('zhenjiang', 'Zhenjiang, Jiangsu'), ('changsha', 'Changsha, China'), ('guangzhou', 'Guangzhou, China'),
               ('liuzhou', 'Liuzhou, China'), ('qijiang', '綦江区, 重庆'), ('icn', 'Incheon International Airport'), ('seoul_c', 'Seoul City Hall')]:
    r = nomi(q)
    if r: P[key] = dict(lon=float(r['lon']), lat=float(r['lat']), name=r.get('display_name', '')[:60]); print(key, round(P[key]['lon'], 3), round(P[key]['lat'], 3), P[key]['name'][:40])
    else: print('MISSING', key)
out['places'] = P
json.dump(out, open('geo.json', 'w'), ensure_ascii=False)
