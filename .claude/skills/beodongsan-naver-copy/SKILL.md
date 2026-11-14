---
name: "beodongsan-naver-copy"
description: "브동산 사이트(zzanghyuny/brond)의 포스팅(posts/*.html)을 네이버 블로그용 HTML로 변환해 naver-html/{slug}.html 로 GitHub에 올릴 때 사용. '네이버에 올리려고', '네이버 블로그용', '네이버용 html', '태그도 뽑아줘' 같은 요청이 단지명·slug·몇 번째 포스팅과 함께 오면 이 스킬을 쓴다. 사이트 원문을 그대로 복사하거나 로컬 PC에 저장하지 말고 이 스킬의 절차를 따른다. (2026-10-31 개정: 저장 위치 GitHub naver-html/, 제목 구분자 ' | ', 차트 PNG 생략, Aside 인수인계)"
---

# 브동산 포스팅 → 네이버 블로그용 HTML (C안 재구성형, 2026-10-31 개정)

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
