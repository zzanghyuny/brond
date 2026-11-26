---
name: "beodongsan-naver-copy"
description: "브동산 사이트(zzanghyuny/brond)의 포스팅(posts/*.html)을 네이버 블로그용 HTML로 변환해 naver-html/{slug}.html 로 GitHub에 올릴 때 사용. '네이버에 올리려고', '네이버 블로그용', '네이버용 html', '태그도 뽑아줘' 같은 요청이 단지명·slug·몇 번째 포스팅과 함께 오면 이 스킬을 쓴다. 사이트 원문을 그대로 복사하거나 로컬 PC에 저장하지 말고 이 스킬의 절차를 따른다. (2026-10-31 개정: 저장 위치 GitHub naver-html/, 제목 구분자 ' | ', 차트 PNG 생략, Aside 인수인계)"
---

# 브동산 포스팅 → 네이버 블로그용 HTML (C안 재구성형, 2026-10-31 개정)

> **⚠ 2026.11.20 개정 레이아웃이 최우선이다. 아래 내용과 충돌하면 이 블록을 따른다.**

> ## 2026.11.20 개정 레이아웃 — 현재 기준 (최우선, Paul)
>
> 기준 글: 네이버 `blog.naver.com/bds_unboxing/224483930499`(더샵 천안라크원) · 샘플 파일 `docs/naver-sample/thesharp-cheonan-lac-one-naver.html`. 아래 규칙이 이전 샘플(광교, 2026.11.09/11.15 규칙)과 충돌하면 **이 섹션이 이긴다.**
>
> **원칙: 긴 문장 대신 표와 짧은 문장.** 비교·수치·조건은 표로, 설명은 문단당 1~2문장으로 짧게 요약한다. 4열 이하 표만 쓴다(`table style="width:100%;border-collapse:collapse;word-break:keep-all"`, 셀 `border:1px solid #ccc;padding:6px;text-align:left`). 폰 키트가 표를 이미지로 바꿔 올린다.
>
> 순서(h2는 짧게, 부제 없이):
> 0. **맨 첫 문단 = 요약문**(합니다체 2~3문장): 지역+단지명, 세대수, 84㎡ 가중평균 분양가, 브동산 분석 적정가격, 1순위 날짜. 그다음 바이라인 `브동산 청약 언박싱 · YYYY.MM.DD` (h1 제목은 본문에 넣지 않는다 — 네이버 제목 칸에 입력).
> 1. `1. 결론부터`
>    - 청약 전에 먼저 볼 점 한 문장(실용 조언).
>    - 표 `구분 | 가격`: 브동산 분석 적정가격 / 실제 분양가 · 84㎡ 가중평균 / 예상 프리미엄 · 모형 차이. (스탯 박스 대신)
>    - 굵은 3수치 문장 + "적정가 대비 약 N% 고(저)평가" 한 문장.
>    - 조감도(캡션: 출처 · 단지명 조감도 (CG)) + 개요 표 `항목 | 공고 내용`: 위치 / 규모 / 분양(특별·일반) / 입주 / 시공 / 규제.
> 2. `2. 왜 이 가격이 나왔을까`
>    - 비교단지 선정 이유 1~2문장, 예정 시설·학교는 "예정·확인 필요"로 1문장.
>    - 표 `선정 비교단지 | 동일 전용면적 기준가격` (단지명 + (준공 YYYY.MM · 세대수) | KB 면적 · 가격 · 조회일).
>    - h3 `입지·브랜드·상품성 평점` + 표 `항목 | SITE | 비교1 | 비교2` (입지 x/40, 브랜드 x/20, 상품성 x/40, 합계) + 굵은 한 줄 `종합평점 N점 · 비교단지 N점 / N점.`
>    - h3 `보정가격과 실제 분양가` + 표 `비교단지 | KB 일반가 → 보정가격` (비교1, 비교2, 브동산 적정가격, 실제 분양가, 예상 프리미엄 · 적정가 대비 약 N%).
>    - chart-b(적정가격·분양가 막대, 황동) 1장. **평점 막대(chart-a)·위치 개략도(chart-map)는 넣지 않는다.**
>    - 가정·한계는 짧은 문장 몇 개(연식 보정 기준, 미개통 역 미가산, 중립 점수 항목 등)와 출처 한 줄.
> 3. `3. 브동산 한줄평` — 한 문장(실용 조언형).
> 4. `4. 지역 최근 분양단지` — 표 `단지 | 공고 기준 비교`(공고 월 · 타입별 최고 공급금액) + 기준 설명 한 문장 + 비교 공고 자료 링크.
> 5. `5. 분양 사이트 자료로 한 번에 보기`
>    - 공식 입지환경 → 공식 청약 일정 이미지(캡션: 출처 · 종류).
>    - h3 `정리` + 표 `타입 | 세대 | 공급가(만원)` + 확장비·납부 비율 한 문장 + 공식 세대안내 링크.
>    - 단지배치도 → 동호수 배치도 → 타입별 평면도(캡션: 종류 · 사업주체 공식 분양 홈페이지). 없으면 "미게시".
> 6. `6. 결론 — 접수 일정`
>    - 표 `구분 | 날짜` (특별공급, 1순위, 2순위, 당첨자 발표, 정당계약).
>    - 일정 한 문장 + 해당지역·기타지역 범위와 자격 확인 한 문장.
>    - 링크 한 줄: 청약홈 입주자모집공고 원문 · 공식 분양 일정
>    - 링크 한 줄: `브동산 웹사이트에서 전체 분석 보기`(해당 글 URL).
> - 이미지는 절대경로 URL + `style="width:100%;height:auto;display:block"`, figure `margin:22px 0`.
> - 무순위·공공분양 등 특수 공고도 같은 틀에 맞추고, 무순위 세대 목록·자격·계약금 조건 같은 정보는 표를 하나씩 더한다.


> ## ⚠ 모바일 기준 (2026.11.14, 최우선 — 아래 PC 기준 크기·차트 스크립트(13번)보다 이 섹션이 이긴다)
> 네이버 글·이미지는 **폰 폭 기준**으로 만든다. 전문: `docs/naver-mobile-spec.md`.
> - 차트 이미지: 캔버스 폭 1000px, 글씨 28px 이상(값 32px, 제목 36px). 생성은 저장소의 `scripts/beodongsan/make_naver_charts.py`(`chart_a`/`chart_b`/`chart_map`/`chart_c`, 기본 `mobile=True`)만 쓴다. 이 문서 13번의 스크립트는 구버전이니 쓰지 않는다. 만든 PNG는 390px로 줄여 읽히는지 확인한다.
> - 표는 4열 이하, 아니면 이미지로. 문단은 2~3문장. 공식 사진은 가로 ≤1000px·≤400KB.
> - 폰 발행용으로 글마다 `naver-kit/<slug>.html`(블록별 복사·이미지 저장 버튼)을 함께 만든다(`scripts/naver_kit.py <slug>`).
> - 섹션 구성·문체·굵은 3수치 문장·`이미지 NN` 번호 규칙은 승인 샘플(`docs/naver-sample/`) 그대로.


공통 문서: `docs/publishing-workflow.md`(전체 흐름), `docs/content-rules.md`(공통 규칙), `docs/aside-handoff.md`(Aside 발행 절차). 이 스킬은 그중 **네이버용 HTML 생성** 부분의 실행 규칙이다.

## 무엇이 바뀌었나 (2026-10-31)
| 항목 | 이전 | 현재 |
|---|---|---|
| 저장 위치 | 로컬 PC 폴더/scratchpad | **저장소 `naver-html/{slug}.html`** 에 커밋·push (Paul·Aside가 GitHub에서 내려받음) |
| 파일명 | `{slug}-naver.html` 등 | **`{slug}.html`** (접미사 없음) |
| 제목 구분자 | ` / ` | **` | `** (세로선) |
| 차트 A/B PNG(막대) | 별도 PNG 제공 + 자리표시 | **만들지 않는다** (Paul 요청). 위치 개략도 `chart-map.png`만 쓴다 |
| 메타 정보 | 없음 | HTML 상단 주석 + `posts-manifest.json` 에 title/category/tags/slug/대표이미지 후보 기록 |
| 색인 | - | `<meta name="robots" content="noindex,nofollow">` + `robots.txt` Disallow `/naver-html/` |
| 발행 | Paul 수작업 | **Aside**가 이미지 직접 업로드·카테고리·발행 후 manifest 기록 |

## 왜 원문 복사 금지인가
1. `#ad`(광고카드)·`#related`(관련글)는 사이트 전용 요소다.
2. 인라인 SVG(레이더·브릿지·지도)는 네이버 에디터가 보존하지 못한다. 지도는 PNG로 캡처해 쓰고 나머지 차트는 넣지 않는다.
3. 같은 텍스트가 두 도메인에 올라가면 검색에서 중복 문서로 판정될 수 있다(2026.10.02 Paul과 논의, C안). 그래서 제목·결론은 다르게, 입지/상품/공급분석은 표현을 재구성한다. **수치·사실은 절대 바꾸지 않는다.**
4. 이미지는 실제 `https://` 절대 URL만 쓴다(`data:` URI 금지).

## 절차
### 0. 입력 확인
`posts/{slug}.html`을 읽는다. 이미지가 `src="images/{slug}/..."`(파일)인지 확인한다. 위치 개략도 PNG `posts/images/{slug}/chart-map.png`가 있어야 한다. 없으면 `.map-wrap`의 SVG만 담은 임시 HTML을 Edge 헤드리스로 캡처해 만든다(1280×920):
```
& "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --headless --disable-gpu --hide-scrollbars --window-size=1280,920 "--screenshot=<절대경로>\chart-map.png" "file:///<절대경로>/tmp-map.html"
```
이 PC에는 Python/Node가 없다(PowerShell·curl·Edge 사용).

### 1. 파일 만들기
`assets/copy-template.html`의 `{{TITLE}} {{BYLINE}} {{BODY}} {{DISCLAIMER}}`를 채워 **`naver-html/{slug}.html`** 로 저장한다(UTF-8, BOM 없음). `<head>`에 아래 두 가지를 반드시 넣는다.
```html
<meta name="robots" content="noindex,nofollow">
<!--
slug: {slug}
title: {네이버 제목}
category: 부동산            (부동산 / 브랜드 / 호치민)
naver_category: 부동산이야기 (부동산이야기 / 브랜드이야기 / 호치민이야기)
tags: 단지명붙여쓰기,역명,시공사,브랜드,지역구,청약,분양가,청약경쟁률,부동산정보 ... (12~15개, 쉼표, # 없이)
cover_candidates: cover.jpg, aerial.jpg
-->
```

### 2. 제목 (지역명 접두 금지, 구분자 ` | `)
- 공고 후: `{단지명} | 예상프리미엄 {±금액}, 분양가 평면 총정리`
- 분양예정: `{단지명} | 브동산 적정가 {X억}, 분양가 공개 전 총정리`
- 금액은 본문에 이미 명시된 값을 그대로 쓴다(새로 계산 금지).

### 3. 본문
- **1. 핵심요약**: 텍스트·표·stat-box 그대로. 위치 개략도는 `https://www.brandongsan.com/posts/images/{slug}/chart-map.png`. **레이더·브릿지 차트 자리에는 아무것도 넣지 않는다**(평가표 `<table>`·해석 리스트는 유지).
- **2 입지 / 3 상품 / 4 공급분석**: 분량·사실·수치 유지, **표현만 재구성**(문장 순서·서술 방식을 새로 소화해 쓰기. 단순 동의어 치환 금지). 표·스펙표는 그대로.
- **5. 결론 → 한줄평 1문장**으로 교체(톤은 `docs/content-rules.md` §5). 바로 아래에:
  `<p>자세한 평가표와 적정가 산출 과정은 <a href="https://www.brandongsan.com/posts/{slug}.html">브동산 홈페이지</a>에서 확인하실 수 있습니다.</p>`
- 이미지: `https://www.brandongsan.com/posts/images/{slug}/{파일명}` 절대 URL. 평면도는 사이트 글에 실린 타입을 모두 포함한다.
- 표는 진짜 `<table>`, `<dl class="spec">`는 헤더 없는 2열 `<table>`, `.stat-box`는 템플릿의 `<div class="stat">`.
- 제외: `#ad`, `#related`, 광고카드 언급 문장, 팀장 연락처 안내문. 면책 문구만 남긴다.

- **쇼핑커넥트 칸(2026.11.26~ 항상)**: 파일을 다 쓴 뒤 `python3 scripts/shopconnect/apply_naver_shop.py {slug}`를 실행해 바이라인 아래 회색 대가성 안내와 맨 끝 '부동산 공부할 때 곁에 두면 좋은 것' 칸(회색 상품 자리 3개)을 넣는다. 손으로 쓰지 않는다. 쿠팡 링크는 넣지 않는다.

### 4. 검증
- 이미지 URL이 모두 배포 후 200인지(`curl -sL -o /dev/null -w "%{http_code}"`), `{{`가 남지 않았는지, `data:image`/`<svg` 가 없는지 확인한다.
- 웹사이트 글이 먼저 배포돼 있어야 한다(이미지 URL이 열려야 함).

### 5. manifest·커밋
- `scripts/build-manifest.ps1` 실행 → `posts-manifest.json` 갱신(기존 `naver_published` 기록 보존).
- 사이트 글·이미지와 함께 `naver-html/{slug}.html`을 커밋·push(push 직전 `git fetch`로 원격 변경 확인).
- Paul/Aside에게 `naver-html/{slug}.html` 준비됨을 알린다. 발행은 Aside가 한다(`docs/aside-handoff.md`).

## 여러 편을 한 번에
`posts-data.js`의 `tag`(청약 언박싱 No.)로 대상 목록을 뽑아 한 편씩 재구성한다(입지/상품/공급 문단은 자동화하지 않고 매번 새로 쓴다). 마지막에 manifest를 한 번 갱신하고 한 커밋으로 올린다.

## 태그 (항상 포함)
12~15개, 쉼표 구분, `#` 없음: 단지명(붙여쓰기), 역명, 브랜드/시공사, 지역구, 청약, 분양가, 청약경쟁률 등, 부동산정보.
