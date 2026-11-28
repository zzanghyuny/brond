#!/usr/bin/env python3
"""1분 총정리 재료 모으기 — Mapbox 위성사진 + 사이트 글의 공식 이미지를 C['img'] 폴더로.
  MAPBOX_TOKEN=pk... python3 brief_assets.py brief/<키>.json
JSON에 필요한 것: slug, img, site_ll [lon, lat], views {이름: {center [lon, lat], zoom}}.
  views 기본값(없으면 site_ll 기준으로 채워 JSON에 다시 저장):
    open  z14.4  오프닝·썸네일·마무리 배경(단지 위치 깜빡임)  → open.jpg
    dist  z13.5  거리 지도(역·터미널·학교 선)                 → dist.jpg
    city  z12.2  도시 전경(Google Earth 캡처가 없을 때 대신)   → city.jpg
    area  z15.4  단지 주변(유의사항 위성 컷·배경 대신)        → area.jpg
위성사진은 저장소에 넣지 않는다(영상에 © Mapbox © Maxar). 토큰은 Mapbox MCP list_public_tokens_tool.
공식 이미지(posts/images/<slug>/의 siteplan·community-*·plan-*·aerial*·landscape·location)는 그대로 복사한다."""
import os, sys, json, shutil, subprocess, glob
p = sys.argv[1]; C = json.load(open(p, encoding='utf8'))
IMG = C['img']; os.makedirs(IMG, exist_ok=True)
lon, lat = C['site_ll']
ZD = {'open': 14.4, 'dist': 13.5, 'city': 12.2, 'area': 15.4}
V = C.setdefault('views', {})
for k, z in ZD.items(): V.setdefault(k, {'center': [lon, lat], 'zoom': z})
json.dump(C, open(p, 'w', encoding='utf8'), ensure_ascii=False, indent=1)
tok = os.environ['MAPBOX_TOKEN']
for k, v in V.items():
    out = IMG + f'{k}.jpg'
    if os.path.exists(out) and os.environ.get('KEEP') == '1': continue
    (x, y), z = v['center'], v['zoom']
    url = f'https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static/{x},{y},{z}/540x960@2x?access_token={tok}'
    subprocess.run(['curl', '-s', '-f', '-o', out, url], check=True); print(k, z)
root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'posts', 'images', C['slug'])
for f in sorted(glob.glob(root + '/*.jpg')):
    b = os.path.basename(f)
    if b.split('.')[0].split('-')[0] in ('siteplan', 'community', 'plan', 'aerial', 'landscape', 'location', 'overview', 'dongho'):
        shutil.copy(f, IMG + b); print('copy', b)
