# Skill / workflow changelog

`scripts/sync-workflow.ps1`가 대상 파일 변경 시 자동으로 항목을 추가한다(최신이 위).

## 2026-10-31 (auto-sync)
- docs/publishing-workflow.md

## 2026-10-31
- CLAUDE.md
- .claude/skills/
- docs/
- posts-manifest.json

## 2026-10-31
- 네이버용 HTML 저장 위치를 로컬 PC 폴더에서 GitHub `naver-html/{slug}.html`로 변경(Paul·Aside가 GitHub에서 내려받아 발행)
- 네이버 제목 구분자를 ` / `에서 ` | `(세로선)로 변경
- 네이버용에서 차트(레이더·브릿지) 이미지 제거, 위치 개략도 PNG만 사용
- HTML 상단 메타 주석 + `posts-manifest.json`(slug/제목/카테고리/태그/대표이미지 후보/발행 기록) 도입, `noindex` + `robots.txt` Disallow
- 역할 분리: Claude Code(작성·네이버용 HTML·커밋/push·배포 확인) / Aside(네이버 에디터 이미지 업로드·카테고리·발행)
- 추가: `docs/publishing-workflow.md`, `docs/content-rules.md`, `docs/aside-handoff.md`, `.claude/skills/beodongsan-naver-copy/`, `scripts/`

## 2026-11-06
- `beodongsan-realestate-post`: 비교단지 시세 사용 순서 확정 — KB시세 → 리치고 → 아실·네이버·호갱노노 최근 3개월 실거래 평균(앞 순위에 값이 있으면 뒤는 쓰지 않음, 해제 거래 제외)
- "산정 보류"는 모든 출처를 시도한 뒤의 마지막 수단으로 한정(시도 출처·실패 사유를 본문에 명시)
- 신도시·신규 택지 단지는 동네·인접 생활권의 다른 신축 단지를 비교단지로 산정
- 이미지: 공식 홈페이지 우선, 없거나 막히면 보도자료·기사 등의 조감도·배치도·평면도도 출처 표기 후 최대한 수집
- 무순위·사후 공급 글도 정상 청약 글과 동일한 풀 정보(입지·배치도·평면도·커뮤니티·공급금액·평점표·적정가)로 작성
