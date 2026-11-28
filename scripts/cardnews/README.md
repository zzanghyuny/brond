# 카드뉴스 생성기

- `cardkit.py` — 공통(1080×1350, dark 테마, 쪽 번호·워드마크·출처 줄, 사진 자르기·글 줄바꿈)
- `city.py` + `city_cfg.py` — 도시이야기 10장 (`python3 scripts/cardnews/city.py brasilia|hcmc|chongqing|mexico-city`)
  - 결과: `/home/claude/work/cardnews/<키>/01~10.png`, `카드뉴스-캡션.txt`(캡션·해시태그·올릴 때 메모·[사진 출처])
  - 사진 재료 경로(`/home/claude/media/...`)는 세션 작업 폴더라 저장소에 없다. 새 세션에선 Pexels 영상·사진을 다시 받아 같은 경로에 둔다.
- 구성·규칙: `docs/cardnews-plan.md`
- 청약·미분양 랭킹·랭킹 쇼츠 틀은 샘플 확인 후 추가한다.
