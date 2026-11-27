# -*- coding: utf-8 -*-
"""geo_prep 보충: 알카디아 경계는 행정 경계(boundary=administrative) 결과 중 가장 큰 것을 고르고, 몬테레이 공항·호수 흔적을 다시 받는다."""
import json, time, urllib.request, urllib.parse, os
from shapely.geometry import shape, mapping
from pyproj import Geod
HERE = os.path.dirname(os.path.abspath(__file__)); UA = 'brandongsan-map/1.0 (contact: brandongsan.com)'
geod = Geod(ellps='WGS84'); area = lambda g: abs(geod.geometry_area_perimeter(g)[0]) / 1e6
def nomi(q, poly=False, limit=1):
    u = 'https://nominatim.openstreetmap.org/search?' + urllib.parse.urlencode(dict(q=q, format='json', limit=limit, polygon_geojson=1 if poly else 0, polygon_threshold=0.0003))
    for k in range(6):
        try:
            r = json.load(urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': UA}), timeout=40)); time.sleep(1.3); return r
        except Exception as e: print('retry', q, e); time.sleep(6)
    return []
geo = json.load(open(os.path.join(HERE, 'geo.json')))
ALC = [('alvaro_obregon', 'Álvaro Obregón'), ('azcapotzalco', 'Azcapotzalco'), ('benito_juarez', 'Benito Juárez'), ('coyoacan', 'Coyoacán'),
       ('cuajimalpa', 'Cuajimalpa de Morelos'), ('cuauhtemoc', 'Cuauhtémoc'), ('gam', 'Gustavo A. Madero'), ('iztacalco', 'Iztacalco'),
       ('iztapalapa', 'Iztapalapa'), ('magdalena', 'La Magdalena Contreras'), ('miguel_hidalgo', 'Miguel Hidalgo'), ('milpa_alta', 'Milpa Alta'),
       ('tlahuac', 'Tláhuac'), ('tlalpan', 'Tlalpan'), ('vcarranza', 'Venustiano Carranza'), ('xochimilco', 'Xochimilco')]
for key, nm in ALC:
    best = None
    for q in (f'{nm}, Ciudad de México, México', f'Alcaldía {nm}'):
        for r in nomi(q, True, 6):
            if r.get('class') == 'boundary' and r.get('geojson', {}).get('type') in ('Polygon', 'MultiPolygon'):
                g = shape(r['geojson']); a = area(g)
                if best is None or a > best[0]: best = (a, g)
        if best and best[0] > 5: break
    if best: geo['a_' + key] = mapping(best[1].simplify(0.0006)); print(key, round(best[0], 1))
    else: print('FAIL', key)
for key, q in [('mty', 'Aeropuerto Internacional General Mariano Escobedo'), ('tlatelolco_u', 'Nonoalco Tlatelolco, Cuauhtémoc')]:
    r = nomi(q)
    if r: geo['places'][key] = dict(lon=float(r[0]['lon']), lat=float(r[0]['lat']), name=r[0].get('display_name', '')[:60]); print(key, geo['places'][key])
# 호수 흔적: Overpass로 물 면 폴리곤
def overpass(q):
    u = 'https://overpass-api.de/api/interpreter'
    for k in range(3):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(u, data=urllib.parse.urlencode({'data': q}).encode(), headers={'User-Agent': UA}), timeout=90))
        except Exception as e: print('overpass retry', e); time.sleep(8)
from shapely.geometry import Polygon
from shapely.ops import unary_union
res = overpass('[out:json][timeout:60];(way["natural"="water"](19.35,-99.10,19.62,-98.90);relation["natural"="water"](19.35,-99.10,19.62,-98.90););out geom;')
if res:
    polys = []
    for e in res['elements']:
        try:
            if e['type'] == 'way' and len(e.get('geometry', [])) > 3:
                p = Polygon([(c['lon'], c['lat']) for c in e['geometry']])
                if p.is_valid and area(p) > 0.3: polys.append(p); print('water', e.get('tags', {}).get('name'), round(area(p), 2))
            elif e['type'] == 'relation':
                for m in e.get('members', []):
                    if m.get('role') == 'outer' and len(m.get('geometry', [])) > 3:
                        p = Polygon([(c['lon'], c['lat']) for c in m['geometry']])
                        if p.is_valid and area(p) > 0.3: polys.append(p); print('water(rel)', e.get('tags', {}).get('name'), round(area(p), 2))
        except Exception as ex: pass
    if polys: geo['w_texcoco_now'] = mapping(unary_union(polys).simplify(0.0004)); print('texcoco water total', round(sum(area(p) for p in polys), 1))
json.dump(geo, open(os.path.join(HERE, 'geo.json'), 'w'), ensure_ascii=False); print('saved')
