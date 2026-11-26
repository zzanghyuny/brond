import json
from shapely.geometry import shape, mapping, MultiPolygon, Polygon
from shapely.ops import unary_union, transform
from pyproj import Geod, Transformer
G = '/home/claude/media/geo/'
geod = Geod(ellps='WGS84')
def area(g): return abs(geod.geometry_area_perimeter(g)[0]) / 1e6
ne = {f['properties']['iso_3166_2']: shape(f['geometry']) for f in json.load(open(G + 'ne_admin1.geojson'))['features'] if f['properties'].get('iso_3166_2') in ('VN-SG', 'VN-57', 'VN-43', 'KR-41', 'KR-28', 'KR-11')}
osm_seoul = shape(json.load(open(G + 'seoul.json'))['features'][0]['geometry'])
osm_hcmc = shape(json.load(open(G + 'hcmc.json'))['features'][0]['geometry'])
out = {}
def add(k, g, note):
    out[k] = mapping(g); print(f'{k:12s} {area(g):9.1f} km2  {note}')
add('seoul', osm_seoul, 'OSM')
add('seoul_ne', ne['KR-11'], 'NE')
add('hcmc_new', osm_hcmc, 'OSM (merged)')
add('hcmc_old', ne['VN-SG'], 'NE old HCMC')
add('binhduong', ne['VN-57'], 'NE')
add('brvt', ne['VN-43'], 'NE (with islands)')
add('gyeonggi', ne['KR-41'], 'NE')
add('incheon', ne['KR-28'], 'NE')
union3 = unary_union([ne['VN-SG'], ne['VN-57'], ne['VN-43']]); print('NE union3', round(area(union3), 1))
cap = unary_union([osm_seoul, ne['KR-41'], ne['KR-28']]); print('capital region', round(area(cap), 1)); out['capital'] = mapping(cap)
# rivers
def lines(p):
    d = json.load(open(G + p)); return [shape(f['geometry']) for f in d['features'][:1]]
out['saigon_river'] = mapping(lines('saigon_river.json')[0])
out['nhabe_river'] = mapping(shape(json.load(open(G + 'nhabe_river.json'))['features'][0]['geometry']))
out['dongnai_river'] = mapping(lines('dongnai_river.json')[0])
json.dump(out, open('geo.json', 'w'))
b = osm_hcmc.bounds; print('hcmc bounds', b); print('seoul bounds', osm_seoul.bounds)
