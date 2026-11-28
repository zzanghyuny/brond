# 도시이야기 한 편 만들기 — 런북 (2026.11.27, 충칭 편 기준)

한 도시 = **가로 본편 1 + 쇼츠 2 + 썸네일 3 + 사이트 글 1(배포) + 네이버용 HTML 1**.
사이트 글은 직접 배포하고, 나머지(영상·썸네일·네이버용 HTML·설명란)는 **Google 드라이브 'Aside 작업용 폴더'**에 올린다(GitHub `shorts-upload/`에는 올리지 않는다, Paul 2026.11.27). Aside가 유튜브·네이버에 게시한다.
기준 예시는 `ep2-chongqing/`(대본 `script.py`, 지도 `geo_prep.py`, 글 `make_posts.py`)이고, 공용 코드는 `lib/`다. 스킬 `beodongsan-city-video`가 보이면 함께 따른다.

## 0. 준비
- 작업 폴더: `/home/claude/work/epN/`, 실사: `/home/claude/media/pexels_<key>/`.
- 글꼴: `/tmp/fonts`(Pretendard 5종, NotoSerifKR.ttf), `/tmp/nanum`(NanumGothic Regular/ExtraBold). 없으면 받는다
  (Pretendard: `https://github.com/orioncactus/pretendard` 릴리스, NotoSerifKR: `https://github.com/google/fonts/raw/main/ofl/notoserifkr/NotoSerifKR%5Bwght%5D.ttf`, 나눔고딕: `https://github.com/google/fonts/tree/main/ofl/nanumgothic`).
- `pip install --break-system-packages edge-tts pycairo shapely pyproj pillow numpy playwright`.
- 글꼴이 GitHub raw에서 막히면(예약 실행 세션): Pretendard는 `https://cdn.jsdelivr.net/npm/pretendard@1.3.9/dist/public/static/Pretendard-<굵기>.otf`, 노토 세리프는 `curl https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@400;500;600;700;800`(기본 UA)이 주는 굵기별 TTF를 `/tmp/fonts/NotoSerifKR-<굵기>.ttf`로 받는다(공용 코드가 이 파일을 먼저 쓴다), 나눔고딕은 `https://cdn.jsdelivr.net/gh/google/fonts@main/ofl/nanumgothic/`.
- Natural Earth: `/home/claude/media/geo/`에 `ne_land10.geojson`, `ne_admin1.geojson`, `ne_countries50.geojson`, `ne_rivers10.geojson`이 없으면 `raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/`에서 받는다.
- 서울 경계: `ep2-chongqing/geo.json`의 `seoul`을 그대로 복사해 쓴다.

## 1. 사실 확인 (WebSearch)
면적·인구(공식 통계, 최신 연도), 강·지형, 도시 역사(연도), 주거 중심 이동 3단계(동네 이름·시기), 사람들(도시화율·인구 흐름·생활), 교통(철도 km·공항·특이 교통), 한국과의 연결(역사·한국 기업, 공개 보도 범위), 가는 법(인천 직항 시간·시차·비자·항공권). 모든 숫자에 출처 URL을 붙여 `SOURCES`에 넣는다. 확인 못 한 숫자는 쓰지 않는다. 서울 비교값은 면적 605㎢, 인구 934만 명(통계청 2025).

## 2. 실사 모으기 (Pexels, Chrome)
- 셸에서는 pexels.com 검색이 막힌다(403). **Claude in Chrome**으로 `https://www.pexels.com/search/videos/<도시>/`를 열고 `javascript_tool`에서 같은 도메인 `fetch('/search/videos/<q>/?page=N')` → `__NEXT_DATA__` JSON의 `type=='video'` 항목을 모은다. 제목·설명·태그에 도시 이름이 있는 것만 쓴다.
- 결과가 1,000자에서 잘리므로 `id, 파일이름(예: 15333206_1920_1080_60fps.mp4)`만 짧게 꺼낸다. 파일 주소는 `https://videos.pexels.com/video-files/<id>/<파일이름>`이고 **셸 curl로 받을 수 있다**(`px_<id>.mp4`).
- 쿼리: `<도시>`, `<도시> drone`, `<도시> night`, `<도시> aerial`, 대표 명소 이름 3~5개. 앞 120개 중 도시 영상 수를 세어 둔다.
- **실사 양에 맞춰 본편 길이를 정한다**: 도시 영상 60개 이상 → 5~7분, 20~60개 → 4~5분, 그 아래 → 3~4분. 실사 없는 장면으로 길이를 채우지 않는다. 실사가 모자란 꼭지는 줄이거나 합치거나 뺀다.
- 금지: 생성형 이미지, 구글 어스를 썸네일·표지에, 건물 하나를 크게 잡은 사진을 썸네일에, Editorial 전용·CC-NC.
- 받은 클립으로 접촉 시트(장면 40% 지점 프레임 모음)를 만들어 눈으로 고른다.
- Chrome 확장이 끊겨 있으면 같은 PC의 **Claude 데스크톱 앱 내장 브라우저**(`mcp__remote-devices__Claude_Browser__*`, `preview_start`로 pexels 검색 페이지 열고 `javascript_tool`)로도 같은 방법이 된다(2026.11.28 멕시코시티 편). 세로(1080×1920) 원본은 쇼츠용으로만 쓰고 본편에는 가로 원본만 쓴다.
- 태평양을 건너는 지도(인천→아메리카)는 도착지 경도에 360을 더한 장소 키(예: `aicm360`)를 geo.json에 넣어 쓴다. 공용 `land_frame`이 육지를 ±360° 옮겨 함께 그린다.

## 3. 지도 데이터 (`geo_prep.py`)
Natural Earth로 시 경계(`ne_admin1`)·비교 영역(남한 `KOR`)·강, OSM Nominatim(`polygon_geojson=1`)으로 구 경계와 장소 좌표, 강은 OSM `waterway` 관계(필요하면 `viewbox`+`bounded=1`)로 받아 도심 창으로 자른다. Nominatim은 1.2초 간격, 629 오류면 쉬었다 재시도. 결과는 `epN-<city>/geo.json`.
- 강 선은 반드시 구 경계 위에 그린다(레이어 순서: 구 경계 → 강조 구역 → 강).

## 4. 대본 (`script.py`) — `ep2-chongqing/script.py`를 복사해 고친다
- 제목: `{도시}은/는 왜 …` 질문형. 쇼츠 제목도 도시 이름으로 시작하는 질문.
- **본편 순서**: ① 제목 + 도시 실사 → ② 서울과 면적 비교 애니메이션 → ③ 숫자로 보는 도시 → 그 뒤 9꼭지(두 강/지형과 역사 → 주거축 3단계 → 사는 집 → 사람들 → 교통 → 한국과의 연결 → 가는 법).
- **실사 없는 장면은 짧게**: 면적 비교 8초 안팎, 숫자 표 12초 안쪽(표는 줄마다 읽지 않고 핵심 1~2개만 말한다), 다른 지도·카드도 한 장면 12초 이하. `render_long.py <ep> timeline`으로 확인하고 넘으면 문장을 줄인다. 실사 없는 화면이 연달아 12초 넘게 이어지지 않게 한다.
- 나레이션 해요체·담백. 읽을 문장(2번째 값)에서 숫자는 한글로 푼다. 쇼츠 줄은 `(자막, 읽을 문장, 황동 강조어)`.
- 그래픽 이름: `overlay`(면적 비교), `numbers`(표), `map`(강·구역·점·단계), `route`(연도 경로), `flight`(인천→도시), `card`(큰 숫자), `stack`(건물 단면 등 층 구간).

## 5. 만들기
```
cd scripts/dosi/lib
python3 dosi_tts.py ../epN-<city> LONG S1 S2      # 인준(본편 -4% -2Hz, 쇼츠 기본)
python3 render_long.py ../epN-<city> timeline      # 그래픽 장면 길이 확인
python3 preview_gfx.py ../epN-<city> LONG          # 그래픽 마지막 프레임 모아 보기(잘린 글자·강 위치 확인)
python3 render_long.py ../epN-<city> check 0:4 5:8 # 장면 몇 개 미리 렌더해 프레임 확인
python3 render_long.py ../epN-<city> render        # 본편(A안)
python3 render_shorts.py ../epN-<city> S1; python3 render_shorts.py ../epN-<city> S2   # 쇼츠(B안)
python3 thumbs.py ../epN-<city>                    # 썸네일 3장
python3 make_meta.py ../epN-<city>                 # 제목·설명(챕터·출처)·태그, credits_log.csv
python3 ../epN-<city>/make_posts.py                # 사이트 글 + 네이버용 HTML + 이미지
```
- 2코어라 본편 렌더는 15~25분 걸린다. 백그라운드로 돌리고 그동안 글을 쓴다.
- 검수: 프레임 샘플, `ffprobe` 길이, `ffmpeg -af volumedetect`(max -1dB 안팎), 그래픽 글자 잘림, 자막이 아래 띠(본편)·안전영역(쇼츠) 안인지.

## 6. 글 (`make_posts.py`)
- 사이트 글: 평서문(~다), 장 순서는 영상 흐름. 표지는 실사(구글 어스 금지). 지도 이미지는 1920×804, 사진은 1600px.
- 네이버용 HTML: 해요체, **구성을 사이트 글과 절반 이상 다르게**(굵은 첫 두 문장 → 바이라인 → 제목 → 한눈에 표 → '○○이 이렇게 된 이유 3가지' → 꼭 보는 장면 4곳 → 주거 이동 표 → 숫자 표 → 한국과의 인연 → 가는 법 체크리스트 → 마무리·출처·태그). 이미지는 모바일 폭(지도 1000×1400 세로·글자 배율 1.35, 사진 1000px·400KB 이하), 사이트 이미지 절대 주소로 넣는다. 쇼핑커넥트·쿠팡 칸은 넣지 않는다.
- 사이트 등록: `posts-data.js`에 `category: "city"`, 태그 `도시이야기 No.00N`(영상 번호와 같게), `city-story.html` 정적 목록 맨 위에 한 줄, `sitemap.xml`, `feed.xml` 맨 위 item, `archive.html` '도시이야기' 묶음. **이전 도시 글들의 '도시이야기의 다른 포스팅' 목록도 새 글을 넣어 고친다**(최신순 최대 5개, 하드코딩).
- Playwright 390px로 열어 가로 넘침·깨진 이미지가 없는지 확인(외부 요청은 막고 `wait_until='domcontentloaded'`).

## 7. 배포·전달
- 커밋 → push 직전 `git fetch origin main`, 바뀌었으면 병합 → push → 1~3분 뒤 글·이미지 URL 200 확인.
- Google 드라이브: 'Aside 작업용 폴더'(id `1_JKxY2Q9wIX0o3e_xXMtNhc5CsRhzbd-`) 안 '브동산 도시이야기'(id `1v1ySIq0dpNMCwkg8SIlAZ4G7wHeqTHpV`)에 `NN 도시명` 폴더를 만들고 썸네일 3장(png·jpg), 네이버용 HTML, 설명란 txt 3개, credits_log.csv, `README.txt`(제목·업로드 순서)를 올린다. 연결 도구는 파일당 약 3MB까지라 `create_file`의 `base64Content`에 `sha256:<hex>:<절대경로>` 참조를 쓴다(작업 폴더 아래 파일만).
- 영상(mp4): 드라이브 연결 도구는 파일당 10MB까지라(2026.11.28 확인) 영상은 못 올린다. Paul 컴퓨터의 드라이브 폴더가 이 세션에 연결돼 있으면(`get_device_info` connectedFolders) 그 안 같은 폴더에 쓴다. 없으면 `SendUserFile`로 대화에 올려 Paul이 받게 하고, 보고에 그렇게 적는다.
- **본편은 줄이지 않는다(Paul 2026.11.28):** 렌더 원본(`out_LONG/<이름>.mp4`)을 그대로 전달한다. 스킬의 '2-pass 5Mbps로 줄여서'보다 이 규칙이 우선한다.
- 보고: SendUserMessage + PushNotification — 도시, 본편 길이·제목, 쇼츠 제목 2개, 사이트 글 주소, 드라이브 폴더 주소, 확인이 필요한 것.
