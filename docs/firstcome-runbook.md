# 미분양 선착순 랭킹 — 정기 운영 런북 (2026-11-17)

수도권은 **보름마다(매월 1일·16일)**, 지방 4개 권역은 **매월 1회** 새 회차를 만들어 사이트에 배포하고, 네이버용 원고와 영상 2종(가로 본편 = 유튜브 + 네이버 클립 롱폼, 세로 쇼츠 = 유튜브 쇼츠 + 클립)까지 구글 드라이브로 어사이드에게 넘긴다. 정기 작업(scheduled task)이 이 문서를 따라 실행한다.

## 권역과 일정

| RID | 권역(label) | 포함 지역 | cls | 일정(KST) |
|---|---|---|---|---|
| `sudogwon` | 수도권 | 서울·경기·인천 | 전부 metro | 매월 1일·16일 |
| `chungcheong` | 충청권 | 충남·대전·충북·세종 | 대전 metro, 나머지 local | 매월 8일 |
| `busan-ulsan` | 부산·울산 | 부산·울산 | metro | 매월 12일 |
| `daegu-gyeongbuk-gangwon` | 대구·경북·강원 | 대구·경북·강원 | 대구 metro, 나머지 local | 매월 20일 |
| `gyeongnam-honam-jeju` | 경남·호남·제주 | 경남·광주·전북·전남·제주 | 광주 metro, 나머지 local | 매월 24일 |

`cls`: metro = 서울·수도권·광역시(연령보정 맥스 1.2, 교통 A안), local = 기타지방(맥스 1.3, 교통 B안). 세종은 local.

## 파일

- `scripts/firstcome/regions/<RID>.json` — 회차 데이터(단지·비교단지·상한·문장·메타). 형식은 `region_engine.py` 맨 위 docstring.
- `scripts/firstcome/region_engine.py` — 계산(→ `<RID>-result.json`, 커밋하지 않음).
- `scripts/firstcome/region_charts.py` — 사이트 순위 차트 + 네이버 황동 인포그래픽.
- `scripts/firstcome/region_build.py images|build|register|history` — 이미지 수집, 사이트·네이버 글, 등록, 회차 기록.
- `scripts/firstcome/history/<RID>/YYYY-MM-DD.json` — 회차 결과 기록(다음 회차 '지난 회차 대비' 표에 쓰임).
- `scripts/longform/make_firstcome_long.py`(가로 1920×1080) · `make_firstcome_shorts.py`(세로 1080×1920) — 영상·썸네일·제목/설명.
- 조사 규칙(후보 수집·선착순 확정·분양가·비교단지·점수·이미지·문장 톤): 아래 "회차 절차" + `docs/handoff-firstcome-ranking.md` 3~6장.

## 회차 절차

1. **최신화**: `git fetch origin main && git checkout main && git merge --ff-only origin/main`. `CLAUDE.md`, 이 문서, `docs/handoff-firstcome-ranking.md`를 읽는다.
2. **데이터 갱신** (`regions/<RID>.json`):
   - `date`를 오늘(KST)로, `slug` 키는 지운다(기본 slug = `<RID>-firstcome-YYYYMMDD`). `meta.series_no`는 이 권역의 기존 값 유지.
   - 직전 회차 단지마다 선착순이 아직 진행 중인지 다시 확인(공식 홈페이지 선착순 표기, 또는 최근 1개월 내 분양 상담 블로그·카페 글 — 다음 블로그 최신순 `https://search.daum.net/search?w=fusion&col=blog&q=<단지명 선착순>&sort=recency`). 끝난 단지는 `excluded`로.
   - 새 후보: 아파트투유 권역 페이지(`https://apttoyou.kr/<지역>-apt`), 분양노트, 기사('선착순 동호지정', '잔여세대'). 청약홈 무순위·임의공급, 오피스텔·도생, 청약 접수 중·예정 단지는 제외.
   - 분양가(대표 84㎡ 최고가, 없으면 59㎡ `size:"59"`), 확정 페이백만 `benefit`. 비교단지 2곳은 고정 기준(같은 동·생활권 이웃 1 + 가까운 중심권 신축 대단지 1)으로 고르고, 가격은 KB 일반거래가(`scripts/beodongsan/kb.py`) → 리치고 → 최근 3개월 실거래 순으로 **최신값으로 갱신**. 숫자를 지어내지 않는다.
   - 점수(brand/trans/conv/edu)는 `.claude/skills/beodongsan-realestate-post/SKILL.md` 5장. 준공 단지 `done`/`own`, 주변 미분양 상한 `ceil`, 재선정 사유 `l5`, 주의 `warn`, 데이터 신뢰도 `conf`.
   - 이미지 URL `img.aerial`·`img.location`(공식 홈페이지 우선, 없으면 아파트투유 `/<slug>/img/hero.jpg`·`lo.jpg` 등 — 일러스트·문구만 있는 그림은 쓰지 않는다, 지도 서비스 캡처 금지).
   - `texts`(설명 2~3문장 "-다" 체 + 한줄평), `meta`(title_hook, groups 3묶음, risks, risk_items 4개(영상용: [짧은 제목, 한 줄]), conclusion, sources, tags). 숫자는 정직하게, 평가는 긍정적으로, 실거주 요건이 좋으면 "실거주자에게 기회". 내부 모형 용어(L1~L5, 6-1, 레슨런) 금지. 광고 문의 카드 금지.
3. **계산**: `python3 scripts/firstcome/region_engine.py scripts/firstcome/regions/<RID>.json`. `<<재검토`(+5% 초과·−20% 미만) 단지는 비교단지부터 다시 본다.
4. **글**: 저장소 루트에서
   ```
   RID=<RID> python3 scripts/firstcome/region_build.py images
   RID=<RID> python3 scripts/firstcome/region_charts.py
   RID=<RID> python3 scripts/firstcome/region_build.py build
   ```
   이미지는 `posts/images/<slug>/`에서 직접 열어 확인한다(위치도가 잘렸거나 홍보 그림이면 손으로 잘라 다시 저장). 사이트 글은 Playwright로 390px 폭 가로 넘침이 없는지 확인.
5. **영상**: `RID=<RID> LONG_OUT=/tmp/long-out/ python3 scripts/longform/make_firstcome_long.py` 와 `... make_firstcome_shorts.py`. 정지 화면(인자로 초 지정)으로 먼저 확인. 결과 mp4·썸네일·txt와 네이버 원고, `README.txt`(제목·설명·태그)를 구글 드라이브 'Aside 작업용 폴더/브동산 미분양 랭킹'(id `1-B7fZLBvDR51oPn3o8zBL19fk-bqSpzG`) 안 `YYYY-MM-DD 권역 미분양 랭킹 (slug)` 폴더에 올린다(2026.11.28~, `shorts-upload/`에는 올리지 않음. 방법·3MB 한도는 `CLAUDE.md` 맨 아래 섹션). `README.txt`의 올릴 순서에 **가로 본편은 유튜브와 같은 날 네이버 클립에도 롱폼으로 올린다(AI 활용 설정 켜기, 클립 제목·설명은 유튜브와 조금 다르게, 정보 스티커 → 같은 회차 네이버 블로그 글)**를 넣는다(2026.11.28 Paul).
6. **등록·기록**: `RID=<RID> python3 scripts/firstcome/region_build.py register` 후 `... history`.
7. **배포**: 커밋 → `git fetch origin main` → 바뀌었으면 `git merge origin/main`(등록 파일 충돌은 손으로 합침) → `git push origin HEAD:main`. 배포 후 글·이미지·네이버 HTML URL이 200인지 확인(처음 404면 잠시 후 재시도).
8. **보고**: 1위와 플러스 단지 수, 지난 회차 대비 변화, 재검토한 단지, 이미지 못 구한 단지, 확인 필요 사항, 영상 제목.

## 주의

- 지방은 거래가 적다. 같은 생활권 신축 비교가 없으면 `warn`에 하향 편향 가능성을 적고 `conf: "하"`.
- 수도권 1회차(`sudogwon-firstcome-top30-202611`)는 `build2.py`로 만든 글이다. 2회차부터는 `regions/sudogwon.json`을 갱신해 위 공용 절차로 만든다.
- 영상 mp4는 50MB를 넘으면 GitHub 경고가 뜬다(100MB 한도). 가로 영상이 크면 `make_firstcome_long.py`의 crf를 올린다.
