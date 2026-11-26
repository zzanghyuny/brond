#!/usr/bin/env python3
"""랭킹 단지 위성사진 받기 (Mapbox Static Images, satellite-v9, 540×960@2x = 1080×1920).
  MAPBOX_TOKEN=pk... python3 fetch_sat.py rank/<키>.json      → $RANK_IMG/<키>/<순위>.jpg, hook.jpg
위성사진은 저장소에 넣지 않는다(영상 안에 © Mapbox © Maxar 표기)."""
import os, sys, json, math, subprocess
C = json.load(open(sys.argv[1], encoding='utf8'))
KEY = os.path.basename(sys.argv[1])[:-5]
D = os.path.join(os.environ.get('RANK_IMG', '/tmp/rank-img/'), KEY); os.makedirs(D, exist_ok=True)
TOK = os.environ['MAPBOX_TOKEN']
def zoom_for(lat, meters):  # 540 논리 px 폭에 meters가 들어가는 줌
    return round(math.log2(540 * 156543.03 * math.cos(math.radians(lat)) / meters), 2)
def get(path, lon, lat, z):
    url = f'https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static/{lon},{lat},{z}/540x960@2x?access_token={TOK}'
    subprocess.run(['curl', '-s', '-f', '-o', path, url], check=True)
for it in C['items']:
    if it.get('sat_zoom'):                       # 경로 그림 등 좌표 투영이 필요한 경우: 중심·줌을 JSON에 고정
        (lon, lat), z = it['sat_center'], it['sat_zoom']
    else:
        m = it.get('cover_m') or (520 + it.get('hh', 1000) * 0.075); lon, lat, z = it['lon'], it['lat'], zoom_for(it['lat'], m)
    if os.path.exists(f"{D}/{it['rank']}.jpg") and os.environ.get('KEEP') == '1': continue
    get(f"{D}/{it['rank']}.jpg", lon, lat, z); print(it['rank'], it['name'], z)
h = C['hook']
if 'lon' in h: get(f'{D}/hook.jpg', h['lon'], h['lat'], h['zoom']); print('hook')
