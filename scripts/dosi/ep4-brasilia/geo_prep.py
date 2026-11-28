# -*- coding: utf-8 -*-
"""브라질리아 편 지도 데이터: Natural Earth(연방구 경계) + OSM Nominatim(행정구역·파라노아 호수·장소 좌표) → geo.json"""
import json, time, urllib.request, urllib.parse, os
from shapely.geometry import shape, mapping
from pyproj import Geod
HERE = os.path.dirname(os.path.abspath(__file__))
G = '/home/claude/media/geo/'; UA = 'brandongsan-map/1.0 (contact: brandongsan.com)'
geod = Geod(ellps='WGS84'); area = lambda g: abs(geod.geometry_area_perimeter(g)[0]) / 1e6
def nomi(q, poly=False, limit=1):
    u = 'https://nominatim.openstreetmap.org/search?' + urllib.parse.urlencode(dict(q=q, format='json', limit=limit, polygon_geojson=1 if poly else 0, polygon_threshold=0.0003))
    for k in range(6):
        try:
            r = json.load(urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': UA}), timeout=40)); time.sleep(1.3); return r
        except Exception as e: print('retry', q, e); time.sleep(6)
    return []
def best_poly(qs, minkm=0.5):
    best = None
    for q in qs:
        for r in nomi(q, True, 6):
            if r.get('geojson', {}).get('type') in ('Polygon', 'MultiPolygon'):
                g = shape(r['geojson']); a = area(g)
                if (r.get('class') in ('boundary', 'place', 'natural', 'water', 'landuse')) and (best is None or a > best[0]): best = (a, g, r.get('display_name', '')[:60])
        if best and best[0] > minkm: break
    return best
out = {}
out['seoul'] = json.load(open(os.path.join(HERE, '..', 'ep2-chongqing', 'geo.json')))['seoul']
ne = [f for f in json.load(open(G + 'ne_admin1.geojson'))['features'] if f['properties'].get('iso_3166_2') == 'BR-DF'][0]
df = shape(ne['geometry']); out['ne_df'] = mapping(df); print('DF NE', round(area(df)))
b = best_poly(['Distrito Federal, Brasil'], 3000)
if b: out['df'] = mapping(b[1].simplify(0.0008)); print('DF OSM', round(b[0]), b[2])
else: out['df'] = out['ne_df']
RA = [('plano_piloto', 'Plano Piloto'), ('ceilandia', 'Ceilândia'), ('taguatinga', 'Taguatinga'), ('aguas_claras', 'Águas Claras'),
      ('samambaia', 'Samambaia'), ('gama', 'Gama'), ('planaltina', 'Planaltina'), ('lago_sul', 'Lago Sul'), ('lago_norte', 'Lago Norte'),
      ('sobradinho', 'Sobradinho'), ('guara', 'Guará'), ('cruzeiro', 'Cruzeiro'), ('sudoeste', 'Sudoeste/Octogonal'), ('recanto', 'Recanto das Emas'), ('santa_maria', 'Santa Maria')]
for key, nm in RA:
    b = best_poly([f'Região Administrativa {nm}, Distrito Federal', f'{nm}, Distrito Federal, Brasil'], 3)
    if b: out['r_' + key] = mapping(b[1].simplify(0.0005)); print(key, round(b[0], 1), b[2])
    else: print('no poly', key)
b = best_poly(['Lago Paranoá, Brasília', 'Lago Paranoá'], 10)
if b: out['w_paranoa'] = mapping(b[1].simplify(0.0003)); print('paranoa', round(b[0], 1), b[2])
P = {}
for key, q in [('tres_poderes', 'Praça dos Três Poderes, Brasília'), ('congresso', 'Congresso Nacional, Brasília'), ('catedral', 'Catedral Metropolitana de Brasília'),
               ('esplanada', 'Esplanada dos Ministérios, Brasília'), ('rodoviaria', 'Rodoviária do Plano Piloto, Brasília'), ('torre_tv', 'Torre de TV de Brasília'),
               ('mane', 'Estádio Nacional Mané Garrincha'), ('ponte_jk', 'Ponte Juscelino Kubitschek, Brasília'), ('alvorada', 'Palácio da Alvorada'),
               ('sqs308', 'SQS 308, Asa Sul, Brasília'), ('asa_norte', 'Asa Norte, Brasília'), ('asa_sul', 'Asa Sul, Brasília'),
               ('ceilandia_c', 'Ceilândia Centro, Distrito Federal'), ('taguatinga_c', 'Praça do Relógio, Taguatinga'), ('aguas_claras_c', 'Estação Águas Claras, Distrito Federal'),
               ('bsb', 'Aeroporto Internacional de Brasília'), ('gru', 'Aeroporto Internacional de Guarulhos'), ('doh', 'Hamad International Airport'),
               ('icn', 'Incheon International Airport'), ('rio', 'Rio de Janeiro, Brasil'), ('santos', 'Porto de Santos'), ('busan', 'Busan Port'),
               ('jk_memorial', 'Memorial JK, Brasília'), ('itamaraty', 'Palácio Itamaraty'), ('gama_c', 'Estádio Bezerrão, Gama'), ('korea_emb', 'Embaixada da Coreia do Sul, Brasília')]:
    r = nomi(q)
    if r: r = r[0]; P[key] = dict(lon=float(r['lon']), lat=float(r['lat']), name=r.get('display_name', '')[:60]); print(key, round(P[key]['lon'], 4), round(P[key]['lat'], 4), P[key]['name'][:50])
    else: print('MISSING', key)
out['places'] = P
json.dump(out, open(os.path.join(HERE, 'geo.json'), 'w'), ensure_ascii=False)
print('saved')
# 좌표 보정: catedral·bsb·santos·busan·rio·asa_sul은 Nominatim이 다른 곳을 줘서 손으로 고침(geo.json에 반영)
