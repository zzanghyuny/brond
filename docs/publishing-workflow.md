# 브동산 포스팅 운영 방식 (publishing workflow)

최종 갱신: 2026-10-31

## 1. 역할 분리

| 담당 | 하는 일 |
|---|---|
| **Claude Code** | 글 작성(웹사이트용), 네이버용 HTML 생성, GitHub 커밋·push, 웹사이트 배포 확인 |
| **Aside** | GitHub에 올라온 네이버용 HTML을 읽고, 네이버 블로그 에디터에서 이미지 직접 업로드·카테고리 설정·발행 |
| **Paul** | 단지 선정, 최종 확인, 네이버 로그인(비밀번호·쿠키는 Aside/Claude에 전달하지 않는다) |

## 2. 결과물은 두 종류, 각각 따로 만든다

- **웹사이트용 글** `posts/{slug}.html` — 5단계 고정 양식(핵심요약/입지/상품/공급/결론), SVG 차트·AD카드·관련글 포함.
- **네이버용 글** `naver-html/{slug}.html` — 내용·문체·분량이 웹사이트 글과 **달라도 된다**. 같은 텍스트가 두 도메인에 올라가면 검색에서 중복 문서로 판정될 수 있으므로 제목·한줄평·입지/상품/공급 분석 표현을 재구성한다(사실·수치는 절대 바꾸지 않는다). 광고카드·관련글·SVG는 넣지 않는다.

웹사이트용 글을 그대로 복사해 네이버용으로 쓰지 않는다.

## 3. 네이버용 HTML 규칙

1. 저장 위치: **`naver-html/{slug}.html`** (저장소 루트 기준, 파일명에 `-naver` 접미사 없음). 로컬 PC 폴더에는 저장하지 않는다.
2. 이미지 `src`는 **공개된 절대 URL**: `https://www.brandongsan.com/posts/images/{slug}/{파일명}`. data: URI 금지. 웹사이트 배포 후 `curl -sL -o /dev/null -w "%{http_code}"`로 200 확인한 뒤 push 완료로 본다.
3. HTML 상단(`<head>` 안)에 메타 주석을 반드시 둔다:
   ```html
   <!--
   slug: cheongna-arcone-prugio
   title: 청라 아크원 푸르지오 | 예상프리미엄 +7,780만, 분양가 평면 총정리
   category: 부동산
   naver_category: 부동산이야기
   tags: 청라아크원푸르지오,청라,대우건설,푸르지오,청약,분양가,청약경쟁률,부동산정보
   cover_candidates: cover.jpg, aerial.jpg
   -->
   ```
   같은 값은 `posts-manifest.json`에도 기록한다.
4. `<head>`에 `<meta name="robots" content="noindex,nofollow">`를 넣고, `robots.txt`는 `/naver-html/`을 Disallow한다. `sitemap.xml`에는 넣지 않는다(사이트 글과 중복 문서가 되지 않도록).
5. 제목 형식(지역명 접두 금지, 구분자는 **세로선 ` | `**):
   - 공고 후: `{단지명} | 예상프리미엄 {±금액}, 분양가 평면 총정리`
   - 분양예정: `{단지명} | 브동산 적정가 {X억}, 분양가 공개 전 총정리`
6. 본문 구성: 핵심요약(그대로) → 입지/상품/공급분석(표현 재구성, 표는 그대로) → 결론은 **한줄평 1문장** + 사이트 포스팅 링크 문장 → 면책 문구. 차트(레이더·브릿지)는 넣지 않고, 위치 개략도는 `chart-map.png` 이미지를 쓴다.
7. 한줄평 톤은 프리미엄 크기에 따른다(`docs/content-rules.md` 참고).

## 4. 카테고리 매핑

| 브동산 카테고리 | 네이버 블로그 카테고리 |
|---|---|
| 부동산 (`realestate`) | 부동산이야기 |
| 브랜드 (`brand`) | 브랜드이야기 |
| 호치민 (`vietnam`) | 호치민이야기 |

## 5. 작업 순서 (Claude Code)

1. `posts/{slug}.html` 작성 + 이미지 `posts/images/{slug}/` 저장, `posts-data.js` 등록, `sitemap.xml` 추가.
2. `naver-html/{slug}.html` 생성(위 규칙).
3. `scripts/build-manifest.ps1` 실행 → `posts-manifest.json` 갱신(기존 발행 기록은 보존).
3-1. `scripts/build-feed.ps1` 실행 → `feed.xml` 갱신(RSS 2.0, `posts-data.js` 최신 30개). 새 글을 올릴 때마다 반드시 실행하고 `feed.xml`도 같은 커밋에 포함한다.
4. 커밋·push → 웹사이트 배포 확인(포스팅 URL과 이미지 URL이 200인지).
5. Paul/Aside에게 "naver-html/{slug}.html 준비됨"을 알린다.

## 6. 발행 순서 (Aside) — 자세한 절차는 `docs/aside-handoff.md`

1. HTML을 네이버 에디터에 붙여넣는다.
2. 본문의 **모든 이미지를 내려받아 네이버 에디터의 사진 업로드/사진 교체로 다시 올린다.** (외부 URL 이미지는 네이버가 막거나 나중에 깨질 수 있다.)
3. 이미지 주소가 **네이버 저장소(`pstatic.net`)** 인지 확인한 뒤 발행한다.
4. 카테고리·태그·대표 이미지를 설정하고 발행한다.
5. 발행 후 `posts-manifest.json`에 `naver_published: true`, `naver_post_id`, `published_at`을 기록한다.
6. **이미 발행된 글(`naver_published: true`)은 중복 발행하지 않는다.**

## 7. 비밀 정보

`.env`, API 키, 토큰, 비밀번호, 인증서, 브라우저 쿠키는 GitHub에 올리지 않는다(`.gitignore` 참고). 동기화 스크립트는 커밋 전에 비밀 패턴을 검사하고, 발견되면 중단한다.

## 8. 관련 파일

- `CLAUDE.md` — Claude Code 전용 규칙(이 문서와 충돌 시 이 문서의 네이버 규칙을 따른다)
- `.claude/skills/beodongsan-naver-copy/` — 네이버용 HTML 변환 스킬(최신 규칙 반영)
- `docs/content-rules.md`, `docs/aside-handoff.md`, `docs/skill-changelog.md`
- `posts-manifest.json`, `feed.xml`, `scripts/build-manifest.ps1`, `scripts/build-feed.ps1`, `scripts/sync-workflow.ps1`, `scripts/README.md`

## 9. 자동 동기화
`scripts/sync-workflow.ps1`(Windows 작업 스케줄러, 매일 08:00)이 `CLAUDE.md`, `.claude/skills/`, `docs/`, `templates/`, `posts-manifest.json`의 변경분만 `chore: sync publishing workflow YYYY-MM-DD`로 커밋·push하고 `docs/skill-changelog.md`에 기록한다. 변경이 없으면 아무것도 하지 않는다. 등록 방법은 `scripts/README.md` 참고. `posts/`, `naver-html/` 등 콘텐츠는 이 스크립트가 아니라 Claude Code가 작성 시점에 커밋한다.
