# 브동산 스킬 모음

Claude(클라우드 채팅·Claude Code)에서 쓰는 브동산 작업 스킬의 GitHub 보관본이다. 원본은 Claude 앱의 스킬 저장소에 있고, 여기에는 백업·공유용으로 복사해 둔다. 스킬을 고치면 이 폴더도 같이 갱신한다(`scripts/sync-workflow.ps1`이 매일 08:00에 변경분을 올린다).

| 스킬 | 용도 |
|---|---|
| `beodongsan-realestate-post` | 청약·분양 포스팅 리서치·작성, 적정가("브동산 모형") 산출, 5단계 고정 양식 |
| `beodongsan-naver-copy` | 포스팅 → 네이버용 HTML(`naver-html/{slug}.html`) 변환. 2026-10-31 개정판(GitHub 저장, 제목 ` \| `, 차트 없음, Aside 인수인계) |
| `beodongsan-deploy-handoff` | 사이트 파일 준비·커밋·배포 핸드오프 |
| `beodongsan-brand-post` | 브랜드이야기 포스팅(이미지 삽입, 광고 CTA, 영상 대본) |
| `beodongsan-vietnam-vlog-post` | 호치민 이야기(라이프 브이로그) 포스팅 |
| `beodongsan-author-identity` | 아바타·작성자명 표기 규칙 |
| `beodongsan-design-guideline` | 흑백 모노톤 디자인·BI 규칙 |
| `vietnam-property-site-builder` | 베트남어 호치민 분양 사이트 제작·배포 |

## 참고
- `beodongsan-naver-copy/scripts/`의 `build_naver_copies.py`, `capture_chart_images.js`, `migrate_base64_images.py`는 **이전(2026-10-31 이전) 방식의 잔재**다. 이 PC에는 Python/Node가 없고 현재 절차는 `SKILL.md`(PowerShell·Edge 헤드리스)를 따른다.
- 공통 운영 문서는 `docs/`(`publishing-workflow.md`, `content-rules.md`, `aside-handoff.md`)에 있다. 충돌 시 네이버 관련은 `docs/`와 `CLAUDE.md`의 2026.10.31 섹션을 따른다.
- 비밀 정보(키·토큰·비밀번호·쿠키)는 이 폴더에 두지 않는다.
