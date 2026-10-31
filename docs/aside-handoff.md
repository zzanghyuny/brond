# Aside 인수인계 — 네이버 블로그 발행 절차

Aside는 Claude Code가 GitHub에 올린 **네이버용 HTML을 읽고**, 네이버 블로그 에디터에서 이미지 업로드·카테고리 설정·발행을 한다.
글 작성·웹사이트 배포는 Claude Code가 한다. Aside는 내용을 임의로 고치지 않는다(오탈자·깨진 표시 발견 시 Paul/Claude Code에 알린다).

## 0. 준비
- 저장소: `https://github.com/zzanghyuny/brond` (공개). 브랜치 `main`.
- 발행 대기 목록: `posts-manifest.json`의 `posts[]` 중 `naver_html`이 있고 `naver_published`가 `true`가 아닌 항목.
- HTML 원본: `https://raw.githubusercontent.com/zzanghyuny/brond/main/naver-html/{slug}.html` (또는 저장소를 clone/pull 한 `naver-html/{slug}.html`).
- 네이버 로그인은 Paul이 직접 한다. 비밀번호·쿠키·토큰을 대화나 저장소에 남기지 않는다.

## 1. 발행 전 확인
1. `posts-manifest.json`에서 해당 slug의 `naver_published`가 `true`이거나 `naver_post_id`가 있으면 **중복 발행하지 않는다**(즉시 중단하고 알린다).
2. HTML 상단 주석의 `title`, `naver_category`, `tags`, `cover_candidates`를 읽는다.
3. 웹사이트 글이 배포됐는지 확인한다: `https://www.brandongsan.com/posts/{slug}.html`이 열리고, HTML 안 이미지 URL(`https://www.brandongsan.com/posts/images/{slug}/...`)이 열려야 한다. 안 열리면 Claude Code에 알린다.

## 2. 네이버 에디터 작업
1. 네이버 블로그 글쓰기를 연다. 카테고리를 `naver_category`로 선택한다.
   - 부동산 → **부동산이야기** / 브랜드 → **브랜드이야기** / 호치민 → **호치민이야기**
2. 제목에 주석의 `title`을 그대로 넣는다.
3. HTML을 브라우저에서 열어 본문 전체를 복사해 에디터에 붙여넣는다(표·소제목 서식 유지 확인).
4. **모든 이미지를 직접 업로드한다.** 붙여넣은 이미지는 외부 주소(brandongsan.com)를 참조하므로, 각 이미지를 내려받아 에디터의 **사진 추가/사진 교체**로 다시 올린다. 이미지 순서·캡션 위치는 원본과 같게 유지한다.
5. 모든 이미지가 네이버 저장소(`pstatic.net`) 주소인지 확인한다(이미지 우클릭 → 주소 확인, 또는 HTML 보기). `brandongsan.com` 주소가 남아 있으면 발행하지 않는다.
6. 대표 이미지는 `cover_candidates` 중 첫 번째(조감도)로 설정한다.
7. 태그는 주석의 `tags`를 입력한다(쉼표 구분, `#` 없이).
8. 본문 맨 아래 사이트 링크 문장("브동산 홈페이지에서 확인…")의 링크가 해당 slug 포스팅을 가리키는지 확인한다.
9. 발행한다(공개 범위: 전체 공개).

## 3. 발행 후 기록
`posts-manifest.json`의 해당 항목에 아래를 기록하고 커밋·push 한다(또는 Paul/Claude Code에 값을 전달한다).
```json
"naver_published": true,
"naver_post_id": "<발행된 글 번호 또는 URL>",
"published_at": "2026-11-01T09:00:00+09:00"
```
- 커밋 메시지: `chore: mark naver published {slug}`
- 이 파일 외에는 수정하지 않는다.

## 4. 금지/주의
- 비밀 정보(비밀번호·쿠키·API 키·토큰)를 문서·커밋·메시지에 남기지 않는다.
- 같은 글을 두 번 발행하지 않는다. 수정은 새 글이 아니라 기존 글 편집으로 한다.
- 웹사이트 소스(`posts/`, `*.html` 루트 파일, 배포 설정)는 수정하지 않는다.
- 사실·수치가 의심스러우면 발행을 멈추고 Claude Code에 확인을 요청한다.
