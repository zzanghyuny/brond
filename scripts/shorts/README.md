# 쇼츠·클립·릴스 영상 생성기 (2026.11.15)

단지 하나당 9:16(1080×1920) 30~33초 시네마틱 영상을 코드로 렌더링한다. 외부 AI 서비스 없음.

```
SHORTS_OUT=/tmp/shorts-out/ python3 scripts/shorts/make_gen.py <키>      # 렌더 + 음악 + 효과음 믹스 → <out>-shorts.mp4
SHORTS_OUT=/tmp/shorts-out/ python3 scripts/shorts/make_gen.py <키> 4.5 17  # 정지 화면만 (시각 확인용)
```
- 키는 `make_gen.py`의 `CFG`(armusee / ulsan / choryang / daejang). **새 단지는 `CFG`에 항목 하나를 추가한다**(이미지 파일명·가격·비교단지·청약 정보·장면 목록).
- 의존: Python, Pillow, numpy, ffmpeg, 폰트 WQY Zen Hei(`/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc`).
- 스타일: 검정 바탕 + 황동 `#C8A45C` 포인트 + 크림 흰색 글씨. 음악은 `audio_orig.py`(저음 드론·패드·펄스, 나레이션 없음).
- **효과음(`sfx.py`, 2026.11.15부터 새 영상에 적용)**: 장면 전환마다 whoosh, 예상 프리미엄 공개에 lowhit+ping, 마무리 직전 shimmer, 평균 분양가 카운트업에 tick(약하게).
- 구성: 오프닝 → 조감도 → 평균 분양가 → 비교단지 KB시세 → 예상 프리미엄 → 단지 배치도/특징 → 입지 → 청약 체크 → 마무리. 단지별로 쓸 수 있는 공식 이미지에 따라 장면을 가감한다(`scenes`).
- 영상을 줄 때는 항상 **제목**도 함께 준다(`단지명 | 예상프리미엄 -N, 분양가 총정리` 형식 기본).
- 효과음 적용 전 4편(아르뮤제자이·울산 아르엘·부천대장·초량)은 효과음 없이 발행됨.
- 영상과 함께 썸네일 `<out>-thumbnail.png`도 항상 생성·전달한다.
