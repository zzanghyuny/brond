# -*- coding: utf-8 -*-
"""멕시코시티 편 지도 데이터: Natural Earth(시 경계·멕시코주) + OSM Nominatim(알카디아 16곳·호수 흔적·장소 좌표) → geo.json"""
import json, time, urllib.request, urllib.parse, os
from shapely.geometry import shape, mapping
from pyproj import Geod
HERE = os.path.dirname(os.path.abspath(__file__))
G = '/home/claude/media/geo/'; UA = 'brandongsan-map/1.0 (contact: brandongsan.com)'
geod = Geod(ellps='WGS84'); area = lambda g: abs(geod.geometry_area_perimeter(g)[0]) / 1e6
def nomi(q, poly=False):
    u = 'https://nominatim.openstreetmap.org/search?' + urllib.parse.urlencode(dict(q=q, format='json', limit=1, polygon_geojson=1 if poly else 0, polygon_threshold=0.0003))
    for k in range(5):
        try:
            r = json.load(urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': UA}), timeout=40)); time.sleep(1.2); return r[0] if r else None
        except Exception as e: print('retry', q, e); time.sleep(5)
out = {}
out['seoul'] = json.load(open(os.path.join(HERE, '..', 'ep2-chongqing', 'geo.json')))['seoul']
ne = [f for f in json.load(open(G + 'ne_admin1.geojson'))['features'] if f['properties'].get('iso_3166_2') == 'MX-DIF'][0]
mx = shape(ne['geometry']); out['ne_cdmx'] = mapping(mx); print('CDMX NE', round(area(mx)))
r = nomi('Ciudad de México, México', True)
if r and r.get('geojson', {}).get('type') in ('Polygon', 'MultiPolygon'):
    g = shape(r['geojson']); out['cdmx'] = mapping(g.simplify(0.0008)); print('CDMX OSM', round(area(g)))
else: out['cdmx'] = out['ne_cdmx']
ALC = [('alvaro_obregon', 'Álvaro Obregón'), ('azcapotzalco', 'Azcapotzalco'), ('benito_juarez', 'Benito Juárez'), ('coyoacan', 'Coyoacán'),
       ('cuajimalpa', 'Cuajimalpa de Morelos'), ('cuauhtemoc', 'Cuauhtémoc'), ('gam', 'Gustavo A. Madero'), ('iztacalco', 'Iztacalco'),
       ('iztapalapa', 'Iztapalapa'), ('magdalena', 'La Magdalena Contreras'), ('miguel_hidalgo', 'Miguel Hidalgo'), ('milpa_alta', 'Milpa Alta'),
       ('tlahuac', 'Tláhuac'), ('tlalpan', 'Tlalpan'), ('vcarranza', 'Venustiano Carranza'), ('xochimilco', 'Xochimilco')]
for key, nm in ALC:
    r = nomi(f'Alcaldía {nm}, Ciudad de México', True) or nomi(f'{nm}, Ciudad de México', True)
    if r and r.get('geojson', {}).get('type') in ('Polygon', 'MultiPolygon'):
        g = shape(r['geojson']); out['a_' + key] = mapping(g.simplify(0.0006)); print(key, round(area(g)))
    else: print('no poly', key)
for key, q in [('w_nabor', 'Lago Nabor Carrillo'), ('w_texcoco', 'Parque Ecológico Lago de Texcoco'), ('w_xochimilco', 'Parque Ecológico de Xochimilco'),
               ('w_zumpango', 'Laguna de Zumpango'), ('w_chalco', 'Lago de Chalco, Estado de México')]:
    r = nomi(q, True)
    if r and r.get('geojson', {}).get('type') in ('Polygon', 'MultiPolygon'):
        g = shape(r['geojson']); out[key] = mapping(g.simplify(0.0005)); print(key, round(area(g), 1), r.get('display_name', '')[:60])
    else: print('no poly', key, r and r.get('display_name'))
P = {}
for key, q in [('zocalo', 'Zócalo, Ciudad de México'), ('templo_mayor', 'Templo Mayor, Ciudad de México'), ('tlatelolco', 'Plaza de las Tres Culturas, Ciudad de México'),
               ('tepeyac', 'Basílica de Santa María de Guadalupe, Ciudad de México'), ('tacuba', 'Tacuba, Miguel Hidalgo, Ciudad de México'),
               ('iztapalapa_c', 'Cerro de la Estrella, Iztapalapa'), ('chapultepec', 'Castillo de Chapultepec'), ('roma', 'Roma Norte, Cuauhtémoc, Ciudad de México'),
               ('condesa', 'Condesa, Cuauhtémoc, Ciudad de México'), ('polanco', 'Polanco, Miguel Hidalgo, Ciudad de México'), ('santafe', 'Centro Santa Fe, Ciudad de México'),
               ('angel', 'Ángel de la Independencia'), ('bellas_artes', 'Palacio de Bellas Artes'), ('aicm', 'Aeropuerto Internacional de la Ciudad de México'),
               ('aifa', 'Aeropuerto Internacional Felipe Ángeles'), ('chalco', 'Chalco de Díaz Covarrubias'), ('zonarosa', 'Zona Rosa, Juárez, Ciudad de México'),
               ('xochimilco_c', 'Embarcadero Nuevo Nativitas, Xochimilco'), ('coyoacan_c', 'Jardín Centenario, Coyoacán'), ('cathedral', 'Catedral Metropolitana de la Ciudad de México'),
               ('tlatelolco_u', 'Conjunto Urbano Nonoalco Tlatelolco'), ('reforma', 'Paseo de la Reforma, Ciudad de México'), ('icn', 'Incheon International Airport'),
               ('mty', 'Aeropuerto Internacional de Monterrey'), ('seoul_c', 'Seoul City Hall'), ('progreso', 'Progreso, Yucatán'), ('salina_cruz', 'Salina Cruz, Oaxaca'),
               ('merida', 'Mérida, Yucatán')]:
    r = nomi(q)
    if r: P[key] = dict(lon=float(r['lon']), lat=float(r['lat']), name=r.get('display_name', '')[:60]); print(key, round(P[key]['lon'], 4), round(P[key]['lat'], 4), P[key]['name'][:50])
    else: print('MISSING', key)
out['places'] = P
json.dump(out, open(os.path.join(HERE, 'geo.json'), 'w'), ensure_ascii=False)
print('saved')
