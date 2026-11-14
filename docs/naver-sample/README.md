# 네이버 발행본 승인 샘플 (2026.11.09, Paul)

`gwanggyo-jayeon-centreville-naver.html` — 광교 자연앤 센트레빌. 네이버용 HTML은 **이 파일과 똑같은 양식·구조·서식**으로 쓴다.
차트 3종(평점 비교 / 적정가격 / 위치 개략도)은 `scripts/beodongsan/make_naver_charts.py`의 `chart_a`/`chart_b`/`chart_map`으로 같은 형태로 만든다.

핵심 규칙(샘플에서 읽은 것)
- 상단 주석 메타(slug/title/category/tags) + 바이라인 + h1 + 빈 문단 후 섹션 6개(1 결론부터 · 2 왜 이 가격이 나왔을까 · 3 브동산 한줄평 · 4 최근 분양단지 · 5 분양 사이트 자료 · 6 결론).
- 섹션 1: 도입 → 스탯 박스 3개(적정가격 / 분양가 / 예상 프리미엄+%) → 굵은 3수치 문장 → 조감도+캡션 → 어디?/언제?/얼마?/주의(사이 빈 문단).
- 섹션 2: h3 입지(문단 → 개략도+캡션 → 예정 교통·학교 문단), h3 비교단지(문단 → chart-a+캡션 → 굵은 종합평점 문장 → 가격 표+note → 굵은 적정가격 문장 → chart-b+캡션).
- 캡션은 작은 회색 non-bold. `이미지 NN` 번호 캡션은 섹션 5에서만 01부터 연번(섹션 1·2의 이미지 캡션에는 번호 없음).
- 섹션 5는 h3 소제목(입지 정보 / 조감도 / 단지 배치도 / 동호수 배치도와 분양가 / 84㎡ 평면도 / 특수 타입 / 청약 일정과 공급 물량) 순서.

## 모바일 기준 (2026.11.14)
- 이 샘플(`gwanggyo-jayeon-centreville-naver.html`)의 **섹션 구성·문체·서식은 그대로** 따르되, 이미지 크기·배치는 폰 폭 기준(`docs/naver-mobile-spec.md`)으로 만든다. 샘플 차트의 모바일 버전은 `docs/naver-sample/mobile/`(`chart-a-score.png`·`chart-b-price.png`·`chart-map-naver.png`·`chart-c-schedule.png`, 390px 미리보기 `preview390-*.png`)에 있다.
