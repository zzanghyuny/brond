# -*- coding: utf-8 -*-
"""geo 보충 2: 쿠아우테목 알카디아(시 경계 안 결과만), 아스테카 둑길(개략 직선), 태평양 횡단 지도용 +360° 좌표"""
import json, time, urllib.request, urllib.parse, os
from shapely.geometry import shape, mapping, LineString
from pyproj import Geod
HERE = os.path.dirname(os.path.abspath(__file__)); UA = 'brandongsan-map/1.0 (contact: brandongsan.com)'
geod = Geod(ellps='WGS84'); area = lambda g: abs(geod.geometry_area_perimeter(g)[0]) / 1e6
geo = json.load(open(os.path.join(HERE, 'geo.json'))); cdmx = shape(geo['cdmx']); P = geo['places']
u = 'https://nominatim.openstreetmap.org/search?' + urllib.parse.urlencode(dict(q='Cuauhtémoc, Ciudad de México', format='json', limit=10, polygon_geojson=1, polygon_threshold=0.0003))
for r in json.load(urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': UA}), timeout=40)):
    if r.get('class') == 'boundary' and r.get('geojson', {}).get('type') in ('Polygon', 'MultiPolygon'):
        g = shape(r['geojson'])
        if cdmx.contains(g.centroid) and 10 < area(g) < 60: geo['a_cuauhtemoc'] = mapping(g.simplify(0.0006)); print('cuauhtemoc', round(area(g), 1)); break
for k in list(geo):
    if k.startswith('a_'):
        g = shape(geo[k])
        if not cdmx.contains(g.centroid): print('outside', k)
tm = (P['templo_mayor']['lon'], P['templo_mayor']['lat'])
for key, dest in (('c_tepeyac', 'tepeyac'), ('c_tacuba', 'tacuba'), ('c_iztapalapa', 'iztapalapa_c')):
    geo[key] = mapping(LineString([tm, (P[dest]['lon'], P[dest]['lat'])]))
for k in ('aicm', 'salina_cruz', 'progreso', 'merida', 'mty'):
    P[k + '360'] = dict(P[k], lon=P[k]['lon'] + 360)
json.dump(geo, open(os.path.join(HERE, 'geo.json'), 'w'), ensure_ascii=False); print('saved', sorted(k for k in geo if not k.startswith('a_')))
