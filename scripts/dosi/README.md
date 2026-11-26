# 도시이야기 영상 스크립트 (2026.11.27)

도시이야기 시리즈(호치민 1편부터)를 만들 때 쓴 코드. 기준 스킬은 `beodongsan-city-video`.

## 디자인 확정 (2026.11.27 Paul)
- 가로 본편: **A안 시네마틱 다큐** — `design/longform_cinematic_A.py`가 기준 구현(2.39:1 화면, 위 띠 0~50px·아래 띠 853~1080px, 명조 자막 y=900, 청록·주황 색보정·필름 질감·천천히 다가가는 줌, 숫자는 금색 세로선 캡션, 0.8초 디졸브, 처음·끝 검은 화면 페이드).
- 쇼츠: **B안 리얼 생생** — `design/shorts_vivid_B.py`가 기준 구현(진한 색, 위치 칩, 미니맵(장소가 확인된 장면만 빨간 점), 숫자 말풍선·스티커 팝 + ping 효과음, 굵은 자막·핵심어 황동색, 옆으로 미는 전환).
- 나레이션: **인준 `ko-KR-InJoonNeural`** (본편 -4%·-2Hz).
- `design/mockups_5.py`: A~E 다섯 안 비교 시안.

## ep1-hcmc (호치민 편 실제 제작 코드, 다음 도시는 복사해서 고친다)
- `script_ep1.py` 장면·대사(자막/읽을 문장) · `tts_ep1.py` 음성 · `revoice.py` 목소리만 바꿀 때(타이밍 유지)
- `graphics.py` 지도·카드 애니메이션(cairo): 서울 겹쳐 보기, 합병, 주거축 3단계, 교통, 한국 기업, 항로, 숫자·주거·사람 카드
- `render_ep1.py` 장면 렌더·자막·오버레이·음악·최종 합치기 (`check k:t`, `timeline`, `audio` 모드)
- `geo_prep.py`·`geocode.py` 경계·강·장소 좌표(OSM Nominatim, Natural Earth) → `geo.json`, `places.json`
- `thumbs_ep1.py` 썸네일 3장 · `make_meta.py` 설명란(챕터·출처)·`credits_log.csv`
- 경로(`/home/claude/work/ep1`, `/home/claude/media/...`)는 작업 폴더에 맞춰 고친다. Natural Earth 원본(geojson)은 용량이 커서 넣지 않았다 — `raw.githubusercontent.com/nvkelso/natural-earth-vector`에서 받는다.
- 이 코드는 A·B 디자인을 반영하기 전(프리텐다드 하단 자막) 버전이다. 다음 편부터는 렌더러의 오버레이·자막·색보정 부분을 `design/` 두 파일 기준으로 바꿔 쓴다.
