# 인수인계서 — 신규 청약 단지: 사이트 글 → 네이버용 → 쇼츠·클립·릴스 영상

작성 2026.11.19 · 대상: 이 저장소(`zzanghyuny/brond`)를 이어받아 작업하는 사람과 Claude 세션
이 문서는 **청약홈에 새 공고가 뜬 단지 하나를 끝까지 처리하는 전체 절차**를 한곳에 모은 것이다. 세부 규칙의 원문은 맨 아래 "기준 문서"에 있고, 충돌하면 `CLAUDE.md`가 이긴다.

---

## 0. 한눈에 보는 흐름

| 단계 | 산출물 | 위치 |
|---|---|---|
| 1. 공고 확인 | 신규 단지·관리번호 | 청약홈, `scripts/applyhome-processed.json` |
| 2. 자료 수집 | 공고문 수치, 공식 이미지 | `posts/images/<slug>/` |
| 3. 비교단지 선정 | 비교단지 2곳 + 후보표 | `scripts/beodongsan/comp_scan.py` |
| 4. 적정가 산출 | 평점·보정·적정가·예상 프리미엄 | `scripts/beodongsan/model.py` |
| 5. 사이트 글 | `posts/<slug>.html` + 등록 4종 | 사이트(brandongsan.com) |
| 6. 네이버용 | `naver-html/<slug>.html`, 차트 PNG | GitHub |
| 7. 영상 | 쇼츠 mp4 + 썸네일 + 제목 | `scripts/shorts/` → 구글 드라이브 '브동산' 단지 폴더 |
| 8. 배포·확인 | main push, URL 200 확인 | Vercel 자동 배포 |

- 사이트는 `main` 브랜치가 Vercel로 자동 배포된다. Paul 지시로 청약 글은 **확인 없이 main에 바로 배포**한다(2026.11.11).
- 네이버 발행은 Aside가 한다. 작성·push·배포 확인까지가 이쪽 일이다.
- slug는 영문 소문자·하이픈(예: `gumi-parkone-desian`). 이미지 폴더·네이버 HTML·키트·영상 이름이 모두 slug를 따른다.

---

## 1. 신규 공고 확인

1. 청약홈 APT 분양공고 목록: https://www.applyhome.co.kr/ai/aia/selectAPTLttotPblancListView.do
   - 1페이지에 최신 공고가 나온다(모집공고일·청약접수기간·당첨자발표). 오피스텔·도시형생활주택은 제외.
2. `scripts/applyhome-processed.json`의 `processed`(주택관리번호 목록)에 없는 단지가 신규다. 처리 후 관리번호를 추가한다.
3. 이미 **"공고 전" 글이 있는 단지**에 공고가 나오면 새 글을 만들지 않고 **기존 글을 갱신**한다(→ 9장).
4. 자동 예약 작업: 매일 09:12·17:12(KST) "청약홈 신규 공고 자동 포스팅"이 돈다. 다만 2026.11.13 공고된 경희궁 에피트·해링턴 플레이스 문래(공고 전 글이 있던 단지)는 자동 작업이 놓쳤다. **수동으로 목록을 한 번씩 확인**하는 게 안전하다.

## 2. 자료 수집

### 2-1. 입주자모집공고문(숫자의 유일한 기준)
- 상세: `https://www.applyhome.co.kr/ai/aia/selectAPTLttotPblancDetail.do?houseManageNo=<번호>&pblancNo=<번호>`
- 첨부 PDF: `static.applyhome.co.kr/ai/aia/getAtchmnfl.do?...` 를 `curl`로 받아 `pdftotext -layout`으로 읽는다.
- 뽑을 것: 위치·시행·시공, 규모(층·동·세대), 타입별 세대수, **타입별 층별 공급금액**(세대수 가중평균을 직접 계산), 특별/일반공급 구성, 일정(공고·특공·1순위·2순위·당첨자 발표·서류·계약·입주), 규제(투기과열·상한제·전매제한·재당첨·거주의무), 납부 조건(계약금·중도금·잔금, 확장비), 주차, 건폐율.
- **숫자는 절대 추정하지 않는다.** 공고문에 없으면 "확인하지 못했다"로 쓰고, 평점은 중립 점수.
- 블로그·기사는 2차 자료. 공고문과 다르면 공고문을 따른다(예: 경희궁 에피트 일반분양 135→134세대 정정).

### 2-2. 공식 이미지
- 공고문에 공식 분양 홈페이지 주소가 있다. 조감도·투시도, 단지 배치도, 동호수 배치도, 타입별 평면도(대상 타입 먼저), 위치도·입지환경, 커뮤니티·조경을 `curl`로 받는다.
- 저장: `posts/images/<slug>/` (가로 ≤1000px, ≤400KB 권장). 받은 이미지는 **직접 열어서** 내용을 확인한다.
- 공고 직후에는 배치도·평면도가 없는 경우가 많다(견본주택 개관 무렵 올라옴). 없으면 글에 "미게시(날짜 확인)"로 밝히고, 네이버 제목에서 "평면"을 뺀다.
- 기사에 실린 이미지는 저작권 때문에 원칙적으로 쓰지 않는다. 공식 자료가 없으면 출처를 밝힌 언론 게재본만 예외적으로.

## 3. 비교단지 선정 (묻지 말고 직접, 2026.11.14 규칙)

```
python3 scripts/beodongsan/comp_scan.py <시·구> --area 84      # 키워드 여러 개 가능
```
- 해당 지역 **2016년 이후 준공·500세대 이상** 단지를 KB 일반거래가와 함께 전수 스캔한다. KB가 비면 국토부 실거래로 보완.
- 2곳 선정 기준(가격으로 고르거나 빼지 않는다):
  1. 같은 동·생활권 이웃 1곳
  2. 가장 가까운 중심권 신축 대단지 1곳 (연식·규모·브랜드 등급 근접)
- 글의 비교단지 단락에 **선정 기준 + 후보표(탈락 사유 포함)**를 한두 문장과 표로 밝힌다.
- 기준에 맞는 단지가 동 안에 없으면 인접 생활권으로 넓히고 그 사실을 쓴다(예: 고양 행신동 → 토당동·원흥지구).
- KB 헬퍼: `kb.py`(`search`), `kb_detail.py`(`info`/`types`/`sise`). 캐시 파일은 커밋하지 않는다.

## 4. 적정가 산출 (브동산 모형)

- `model.py`의 `calc()` 사용(`sys.path.insert(0,'scripts/beodongsan')`). 점수 체계 원문: `.claude/skills/beodongsan-realestate-post/SKILL.md`.
- 평점 100점 = 입지 40 + 브랜드 20 + 상품성 40.
- **평점 보정:** 점수 1점당 ±1%, 상한·하한 ±20%.
- **연령(연식) 보정:** SITE 입주예정월과 비교단지 준공월 차이로 계산. 상한은 서울·수도권·광역시 ×1.2, **기타지방 ×1.3**.
  - 주의: `model.agef`는 ×1.2 곡선이다. 기타지방(익산·구미·논산·경산 등)은 스크립트에서 기타지방 공식으로 바꿔 계산해야 한다.
- 두 비교단지 보정가격의 평균 = **브동산 분석 적정가격**. 예상 프리미엄 = 적정가격 − 실제 분양가(84㎡ 세대수 가중평균).
- **6-1 마피 조정**(raw가 마이너스일 때):

| raw | 처리 |
|---|---|
| −1.5억보다 더 마이너스 | 조정 없음, 사실대로 |
| −1.5억 ~ −1.0억 | 근거1(계약금 하한)로 약 3천만원 축소 |
| −1.0억 ~ 0 | 근거2(선분양 수요 프리미엄)로 폭을 절반 정도 축소, "실거주로는 무리 없다" 취지 문장 |

  - 조정은 정성 항목(상품수준·조망·주거편의·교육환경)의 재량 범위에서만 한다. KB시세·세대수·브랜드 등급·역 거리 같은 사실 항목은 건드리지 않는다.
  - 조정했으면 **근거 문장을 글에 반드시** 넣는다.
- **표기:** 십만원 단위 반올림. 1억 이상 `-1.03억`, 1억 미만 `-5,290만`.
- **퍼센트 기준 주의:** "약 N% 고평가/저평가"를 글마다 분양가 기준·적정가 기준으로 섞어 쓴 사례가 있다(경희궁 12%/14%, 경산 20%/25%). 영상의 "분양가가 적정가격보다 약 N% 높음/낮음"은 **적정가 기준(차이÷적정가)**이다. 새 글은 한 글 안에서 하나로 통일한다.
- **모형의 한계(사례):** 소규모·중견 브랜드 단지는 평점 감점이 하한(−20%)에 걸려, 분양가가 인근 실거래보다 낮아도 마피로 나올 수 있다(경희궁 에피트). 이럴 때는 숫자는 두고 **인근 실거래와의 비교 문장을 덧붙인다**(Paul 결정 A, 2026.11.16).

## 5. 사이트 글 (`posts/<slug>.html`)

- 최근 글을 틀로 쓴다: `posts/hoban-summit-choryang.html`, `posts/ulsan-hwajeong1-arel.html`, `posts/gumi-parkone-desian.html`.
- 5단계 양식: 1 핵심 요약(01 사업 개요~05 비교 기준, 스탯 박스, 지도·레이더·브릿지, 평점표, 비교단지 선정표) → 2 입지 → 3 상품(개요표·공급금액표·이미지·평면) → 4 공급 → 5 결론(강점·리스크).
- SVG 차트: `charts.py`의 `mapsvg()`·`radar()`·`bridge()`·`table()` (흑백 모노톤). 지도는 자체 제작 개략도이고 캡션에 "실제 지도가 아니다"를 밝힌다.
- **광고 문의 카드(`section#ad`/`.sponsor`)는 넣지 않는다.** 기존 글을 복사했으면 남아 있는지 확인.
- 제목 형식: `지역 - 단지명 | 핵심 한 줄, 84㎡ 평균 분양가 X.XX억, 예상 프리미엄 ±N`
- 이미지는 별도 파일 + 상대경로, **모든 `<img>`에 `style="width:100%;display:block;"`** 유지. `figure.photo-block`에 넣는 차트 PNG(1000px)도 예외 없음 — 빠지면 본문 폭을 넘어 삐져나온다(2026.11.20 산곡역 무순위 글 등 11개 글에서 발생, 페이지 CSS에 `.content img{max-width:100%}`를 추가해 고침).
- 본문 컨테이너가 `class="wrap content"`면 `.content{padding:30px 0 10px}` 단축 속성이 `.wrap`의 좌우 여백을 0으로 덮어쓴다. 새 글 스타일에 `.wrap.content{padding-left:24px;padding-right:24px}`(모바일 20px)가 있는지 확인한다(2026.11.22, 117개 글 일괄 수정).
- **등록 4종 + 1**(빠뜨리면 목록·피드에 안 나온다):
  1. `posts-data.js` — `POSTS` 배열에 객체 하나(id, category "realestate", region, tag "청약 언박싱 No.NNN", title, date, dateLabel, url, preview)
  2. `posts-manifest.json` — number(기존 최대+1), title, naver_html, naver_title, naver_tags, cover_candidates, `naver_published: false`
  3. `sitemap.xml` — url·lastmod
  4. `feed.xml` — 맨 위 item
  5. `scripts/applyhome-processed.json` — 관리번호

## 6. 네이버용 (`naver-html/<slug>.html`)

> **2026.11.20 개정:** 레이아웃 기준이 더샵 천안라크원 글(`docs/naver-sample/thesharp-cheonan-lac-one-naver.html`)로 바뀌었다. 표 중심·짧은 문장·첫 문단 요약문·chart-b만 사용. 규칙 전문은 `docs/naver-sample/README.md` 맨 위 섹션이며, 아래 내용과 충돌하면 그쪽이 이긴다.

기준: **승인 샘플** `docs/naver-sample/gwanggyo-jayeon-centreville-naver.html` + `docs/naver-sample/README.md` + `docs/naver-mobile-spec.md`. 샘플과 똑같은 구조·서식·문체(평서형)로 쓴다.

- **6섹션:** 1 결론부터(예상 프리미엄) → 2 왜 이 가격이 나왔을까(입지·비교단지) → 3 브동산 한줄평 → 4 지역 최근 분양단지 → 5 분양 사이트 자료로 한 번에 보기 → 6 결론
- **섹션 1:** 도입 → 스탯 박스 3개 → 굵은 3수치 문장 → 조감도 → **단지 개요 2열 표**(위치·규모·시행시공·공급 구성·입주 예정·청약 일정·84㎡ 분양가·규제·주의). 예전의 "어디?/언제?/얼마?/주의" 네 줄은 쓰지 않는다(2026.11.15).
- **섹션 5:** 위치도 → 조감도 → 배치도 → 동호수 배치도 → 평면도 → 청약 일정 이미지를 **설명 없이 연속**으로 붙이고 `이미지 NN · 종류` 캡션만. 설명은 맨 아래 `정리`(타입별 분양가 표 + 한두 문단)에만.
- **모바일 폭:** 이미지 폭 1000px·글씨 28px 이상, 표 4열 이하, 문단 2~3문장.
- **차트:** `scripts/beodongsan/make_naver_charts.py`의 `chart_a`(평점)·`chart_b`(적정가격)·`chart_map`(위치)·`chart_c`(일정). 흑백 + **황동 포인트 `#C8A45C`**(`ACCENT`). `posts/images/<slug>/chart-a-score.png`·`chart-b-price.png`·`chart-map-naver.png`·`chart-c-schedule.png`로 저장하고 `https://www.brandongsan.com/posts/images/<slug>/...` 절대경로로 참조. 만든 PNG는 열어서 겹침·한글 깨짐을 확인하고 390px로 줄여 읽히는지 본다.
- **상단:** `<meta name="robots" content="noindex,nofollow">` + 메타 주석(slug/title/category/naver_category/tags/cover_candidates).
- **네이버 제목:** `단지명 | 예상프리미엄 ±N, 분양가 평면 총정리` (세로선 구분자, 평면도 없으면 "평면" 삭제)
- **폰 키트는 만들지 않는다**(2026.11.26 폐지).
- Aside 전달용 링크: GitHub `naver-html/<slug>.html`.

## 7. 쇼츠·네이버 클립·릴스 영상

생성기: `scripts/shorts/` (`README.md` 참고). 코드 렌더링이라 외부 AI 서비스가 필요 없다(Pillow·numpy·ffmpeg·WQY Zen Hei 폰트).

### 7-1. 스타일 (Paul 확정)
- 1080×1920 세로, 30~33초. 검정 바탕 + **황동 포인트** + 크림 흰색 글씨. 나레이션 없음.
- 음악: `audio_orig.py`(저음 드론·패드·심장박동 펄스). 첫 영상(아르뮤제자이 원본) 스타일.
- **효과음**(`sfx.py`): 장면 전환마다 whoosh, 예상 프리미엄 공개에 lowhit+ping, 마무리 직전 shimmer, 평균 분양가 카운트업에 약한 tick.
- 구성: 오프닝("브동산 / 단지명 / 예상프리미엄 분석") → 조감도 → 평균 분양가 → 비교단지 시세 → 예상 프리미엄 → 단지 정보(배치도·특장점·커뮤니티 등, 있는 공식 이미지만큼) → 입지 → 청약 체크 → 마무리("분양가는 숫자일 뿐, 판단은 청약자의 몫 / 더 궁금한 단지는 댓글로 남겨주세요 / 숫자로 읽는 브동산" + 면책 한 줄).
- 같은 이미지를 두 번 움직이는 장면은 넣지 않는다(조감도 2연속 금지).

### 7-2. 만드는 법
1. `scripts/shorts/make_gen.py`의 `CFG`에 단지 항목 하나를 추가한다. 주요 키:
   - `dir`(이미지 폴더), `out`(파일 이름), `name`, `name_px`(단지명이 길면 52~76)
   - `avg`(평균 분양가), `rng`(층별 범위 문구), `fair`, `prem`, `pct`, `gapword`(플러스면 `'낮음'`), `thumb_sub`
   - `comps`[(이름·동·준공, 기준가)], `cvmax`·`gvmax`(막대 최대값)
   - 실거래 기준이면 `ctitle`·`csub`, 59㎡ 등이면 `plabel`·`glabel`
   - `info`[(항목, 값)×3], `disc`
   - `scenes`[(종류, 초)] — 종류는 `title`·`aerial`·`price`·`comps`·`gap`·`layout`·`feature`·`place`·`loc`·`map`·`info`·`end`
   - 장면별 이미지 설정 `aerial`/`layout`/`feature`/`place`(img·title·cap·cap2·c0·c1·z·box)
2. 정지 화면으로 먼저 확인:
   ```
   cd scripts/shorts && SHORTS_OUT=/tmp/shorts-out/ python3 make_gen.py <키> 4.5 15 22 26
   ```
   글자 잘림·겹침·이미지 크롭을 열어서 본다.
3. 본 렌더(약 2~3분): `SHORTS_OUT=<출력폴더>/ python3 make_gen.py <키>` → `<out>-shorts.mp4` + `<out>-thumbnail.png`
4. 확인: `ffprobe`로 길이, `ffmpeg -af volumedetect`로 음량(평균 약 −15dB, 최대 약 −1dB면 정상), 몇 장면 캡처.

### 7-3. 전달 규칙
> **2026.11.28 변경:** 영상·썸네일·네이버 원고·README는 `shorts-upload/`·GitHub 링크가 아니라 구글 드라이브 'Aside 작업용 폴더/브동산'(id `1RXISeTG40Mgr79ZE7S11EgwVZhIzGmDw`)의 단지 폴더에 올린다. 방법·크기 한도는 `CLAUDE.md` 맨 아래 섹션. 아래 `shorts-upload/` 안내는 예전 방식이다.
- **영상을 줄 때는 항상 제목 + 썸네일을 같이 준다.** 제목 기본형: `단지명 | 예상프리미엄 ±N, 분양가 총정리`.
- 설명 공통 문구: "브동산 모형 추정치이며 확정 수익이 아닙니다. 청약 자격·일정은 청약홈 입주자모집공고를 확인하세요. 더 궁금한 단지는 댓글로 남겨주세요."
- Aside 배포용으로 `shorts-upload/<YYYY-MM>/`에 `<slug>.mp4`·`<slug>-thumbnail.png`를 올리고 같은 폴더 `README.md`에 순서·제목·설명·해시태그를 적는다. 이 폴더는 `.vercelignore`로 사이트 배포에서 빠진다. Aside가 유튜브 업로드를 마치면 Paul이 삭제를 요청하고, 그때 지운다(2026.11.21).
- 수치가 바뀌면(글 갱신) 영상도 다시 만든다.

## 8. 배포와 확인

1. 커밋 메시지 끝에 공동작성 줄을 넣는다(세션 지침의 Co-Authored-By).
2. push 직전 `git fetch origin main`. 원격이 바뀌었으면 rebase/merge하고 등록 파일(`posts-data.js`·`posts-manifest.json`·`feed.xml`·`sitemap.xml`) 충돌은 **양쪽 내용을 모두 보존**한다.
3. `git push origin HEAD:main`
4. 배포 후 글 URL·이미지 URL·키트 URL이 200인지 확인. Vercel 반영까지 1~4분 걸리고 그 사이에는 404가 날 수 있다.
5. Vercel 프로젝트가 두 개("brond", "brond81") 연결돼 있고 번갈아 실패하는 경우가 있다. 사이트가 정상으로 나오면 문제없지만, 정리가 필요하다(Paul 확인 사항).

## 9. "공고 전" 글을 공고 후 갱신할 때

- 새 글을 만들지 않는다. **번호 유지**, 사이트 글·네이버용·키트를 공고 기준으로 다시 쓴다(분양가·프리미엄·일정·이미지·비교단지 KB 재조회).
- 이미 네이버에 발행된 글이면 manifest에 `naver_republish_needed: true`(+사유)를 넣는다. `naver_published`는 true 유지, 기존 `naver_post_id` 보존. Aside가 **수정 발행**하고 제목도 새 제목으로 바꾼다.
- 키트 다시 만들기, 영상 다시 만들기.

## 10. 여러 단지를 동시에 처리할 때

- 단지별로 작업(에이전트)을 나눠 병렬로 돌릴 수 있다. 글 번호를 미리 나눠 주고(예: 107·108·109), push 직전 manifest에서 번호가 비었는지 다시 확인한다.
- 같은 작업 트리를 쓰면 **자기 파일만 골라 `git add`**한다. 등록 파일은 HEAD에 자기 항목만 더해 스테이징한다.
- 미완성 초안은 push하지 않는다(사이트에 공개된다). 필요하면 저장소 밖으로 옮겨 둔다.

## 11. 반복 실수·주의 목록

- 숫자 추정 금지. 공고문·KB·국토부 외 출처는 2차 자료로만.
- 비교단지 기준 이전에 쓴 글(제일풍경채 광주 포에듀·시흥 거모 아테라 등)은 2005·2011년 준공 단지를 비교단지로 쓰고 있다. 현재 기준으로 재계산이 필요하다(Paul 결정 대기).
- 브랜드 등급 점수가 글마다 들쭉날쭉한 사례가 있다(한신더휴 12점, 동일하이빌 16점, 데시앙 12점). 통일 기준은 Paul 확인 사항.
- 같은 차이를 % 두 가지로 쓰지 않는다(4장).
- 키트는 manifest 수정 후 재생성(6장).
- 개략도·평면도 없음·예정 노선·배정 학교는 단정하지 않고 "개략", "미게시", "예정", "확인하지 못했다"로 쓴다.
- 이 컨테이너의 Python에는 playwright 모듈이 없다(2026.11.16 확인). 페이지 화면 확인이 필요하면 환경에 설치된 Chromium(`/opt/pw-browsers/`)을 헤드리스로 쓴다.
- 폰트는 `/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc`(WQY Zen Hei). 유니코드 마이너스(−)는 이 폰트에 없어서 하이픈(-)을 쓴다.

## 12. 최종 체크리스트 (단지 하나당)

- [ ] 공고문 PDF로 분양가 가중평균·일정·규제 확인
- [ ] 공식 이미지 저장·확인(없으면 "미게시")
- [ ] 비교단지 2곳 기준대로 선정, 후보표 포함
- [ ] 적정가·예상 프리미엄(6-1 적용 여부와 근거 문장)
- [ ] 사이트 글(광고 카드 없음) + 등록 4종 + processed
- [ ] 네이버 HTML(섹션1 개요표, 섹션5 이미지 연속, 황동 차트 4종) + manifest naver_title·tags
- [ ] push 후 URL 200 확인
- [ ] 영상 + 썸네일 + 네이버 원고 + README.txt를 드라이브 단지 폴더에 업로드(3MB 넘는 영상은 CLAUDE.md 방식)
- [ ] Paul 보고: 핵심 수치, 링크(사이트·GitHub 네이버 HTML·키트), 확인 못 한 항목

---

## 기준 문서
- `CLAUDE.md` — 최상위 규칙(충돌 시 우선)
- `claude/handoff-master.md` — 전체 업무 기준
- `.claude/skills/beodongsan-realestate-post/SKILL.md` — 사이트 글·모형·6-1
- `docs/naver-sample/` — 네이버 승인 샘플과 README
- `docs/naver-mobile-spec.md` — 모바일 규격
- `docs/publishing-workflow.md`, `docs/aside-handoff.md` — 발행 흐름, Aside 절차
- `scripts/beodongsan/README.md`, `scripts/shorts/README.md` — 스크립트 사용법
