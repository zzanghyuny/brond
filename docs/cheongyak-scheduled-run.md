# 브동산 청약 예약 회차 지시서 (매일 8:47·14:47 베트남 시간)

2026.11.28 Paul 결정: 청약 자동 글 배포는 클라우드 새 세션이 아니라 **Paul과의 브동산 대화 세션 안에서** 예약 메시지(send_later)로 돈다. 결과 보고는 그 대화로 오고, 결과물은 Paul 컴퓨터(`jhi`)의 구글 드라이브 동기화 폴더에 바로 저장한다. 예약 메시지는 "이 문서를 읽고 그대로 하라"만 담고, 절차는 이 문서가 기준이다. 충돌하면 `CLAUDE.md`가 이긴다.

## 0. 다음 회차 예약 (가장 먼저)
- `mcp__claude-code-remote__send_later`로 다음 회차를 건다: 지금이 오전 회차면 같은 날 14:47, 오후 회차면 다음 날 08:47 (`YYYY-MM-DDTHH:MM:00[Asia/Ho_Chi_Minh]`), `initiation: human_schedule`, 이름 `브동산 청약 회차 (MM.DD 오전|오후)`, 메시지는 받은 예약 메시지와 같은 문장.
- 이미 같은 시각 예약이 걸려 있으면(`list_triggers`) 새로 걸지 않는다. Paul이 "청약 예약 멈춰"라고 하면 더 걸지 않는다.

## 1. 저장소 준비
- 작업 폴더 `/home/claude/brond-wt`(없으면 `/home/claude/brond`, 둘 다 없으면 `add_repo` owner zzanghyuny repo brond access push → clone → `register_repo_root`).
- `git fetch origin main` 후 깨끗하면 `git merge --ff-only origin/main`. 작업 중인 변경이 있으면 건드리지 말고 보고한다.
- 읽기: `CLAUDE.md` 전체, `docs/handoff-cheongyak-pipeline.md`, `.claude/skills/beodongsan-realestate-post/SKILL.md`, `.claude/skills/beodongsan-naver-copy/SKILL.md`, `scripts/shorts/README.md`.

## 2. 새 공고 찾기
- 청약홈 APT 분양정보 목록을 브라우저 UA로 받는다: `curl -s -A 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36' ...` → `<tr data-pbno data-hmno data-honm>` 행.
- `scripts/applyhome-processed.json`의 `processed`에 없는 아파트 입주자모집공고가 후보(도생·민간임대·무순위·임의공급 제외).
- **오피스텔도 본다**: `selectOtherLttotPblancListView.do` 목록의 '오피스텔' 행(같은 UA curl). 처리 방법은 CLAUDE.md 오피스텔 규칙(아파트 59㎡ 비교 후 ×0.9). 같은 단지의 아파트 글이 이미 있으면(예: 청라 아크원 푸르지오·중화역 라온프라이빗 센트로·아르뮤제자이) 새 글 없이 processed에만 넣는다. 이미 '공고 전' 글이 있는 단지는 새 글 대신 그 글을 공고 기준으로 갱신(폴더 이름 끝 ` — 수정 발행`).
- 한 회차 최대 2단지(접수일이 빠른 순). 나머지는 processed에 넣지 않고 다음 회차로 넘긴다.
- 새 공고가 없으면 아무것도 바꾸지 않고 6단계 한 줄 보고만 한다.

## 3. 단지마다 한 세트 (빠지면 그 단지는 미완성 — push하지 않는다)
1. **사이트 글** `posts/<slug>.html`: realestate-post 스킬 1-1번 배치. 비교단지는 `scripts/beodongsan/comp_scan.py`로 전수 스캔 후 고정 기준(같은 생활권 이웃 1 + 가까운 중심권 신축 대단지 1), 후보 표 포함. 오피스텔 84는 아파트 59와 비교 후 ×0.9. 커버 = `chart-map-naver.png`(입지 개략도). 공식 홈페이지 이미지(조감도·위치도·배치도·동호수·평면 전부·커뮤니티) 최대한. 광고 문의 카드 금지. 등록: `posts-data.js`, `posts-manifest.json`(cover_candidates = 개략도 URL), `sitemap.xml`, `feed.xml`, `apply_coupang.py`, `apply_naver_shop.py`.
2. **네이버 원고**: `naver-html/goyang-hanshin-thehue-firstone.html`과 똑같은 양식. 대표사진은 입지 개략도. 섹션 5는 공식 이미지를 **번호 없이** 쭉 나열한 뒤 청약 일정 인포그래픽. 예상 프리미엄은 금액 먼저, 판정은 괄호(`+5,960만 (저평가)`). 표는 `scripts/naver_tables_to_png.py`로 PNG.
3. **쇼츠 2편**: ① 가격 맞히기 `scripts/shorts/make_quiz.py quiz/<키>.json` (tts → stills 확인 → render), ② 공고문 속 숨은 한 줄 `scripts/shorts/make_viral.py viral/detective-<키>.json`. 각각 썸네일 포함. ffprobe 길이, `-af volumedetect` 음량, 정지 화면을 직접 본다.
4. 모든 이미지·정지 화면은 Read로 열어 글자 잘림·겹침을 확인하고, 사이트 글은 390px 폭 스크린샷으로 순서를 확인한다.

## 4. 어사이드 전달물 저장 (Paul 컴퓨터 우선)
- 위치: `G:\내 드라이브\Aside 작업용 폴더\브동산 청약\YYYY-MM-DD 단지명 (slug)\` (드라이브 상 '브동산' 폴더, id `1RXISeTG40Mgr79ZE7S11EgwVZhIzGmDw`).
- 파일: `00_읽어주세요.txt`(올릴 순서·네이버 제목·카테고리·태그·대표사진), `01_네이버원고.html` + `이미지\NN_<파일명>`(원고 img src도 `이미지/NN_<파일명>`), `02_쇼츠1-가격퀴즈.mp4`·`02_쇼츠1-썸네일.png`, `03_쇼츠2-숨은한줄.mp4`·`03_쇼츠2-썸네일.png`, `04_쇼츠-업로드-정보.txt`(영상별 제목·설명·해시태그·고정 댓글).
- 방법: 결과물을 `/mnt/user-data/outputs/<slug>/`에 위 이름으로 모으고 `device_commit_files`로 쓴다(폴더는 자동 생성, 원본 화질 그대로). 쓴 뒤 `device_list_dir`로 파일 수·크기를 대조한다.
- 컴퓨터가 응답하지 않으면(한 번 재시도 후) Google Drive 커넥터 `create_file`로 같은 구조를 만든다(파일당 약 3.1MB 한도 — 넘는 영상은 3MB 이하로 다시 인코딩해 올리고 원본은 `SendUserFile`로 대화에 남긴다).
- `naver-html/`·`shorts-upload/`에 새 파일을 커밋하지 않는다(작업 원본으로 `naver-html/<slug>.html`이 필요하면 CLAUDE.md 규칙대로).

## 5. 배포 (회차당 push 한 번)
- 완성된 단지만 커밋, 관리번호를 `scripts/applyhome-processed.json`에 추가. `~/.secrets/`, `scripts/beodongsan/kbcache.json` 등 캐시, `*-result.json`, `__pycache__` 커밋 금지.
- 커밋 trailer는 이 세션의 저자 표기를 따른다. push 직전 `git fetch origin main` → 바뀌었으면 merge 후 등록 파일 4종을 대조 → `git push origin HEAD:main`.
- 1~4분 뒤 글·이미지 URL 200 확인. Vercel 'rate limited'면 다시 push하지 않고 보고한다.

## 6. 보고 (이 대화로, 한국어 존댓말, 짧게)
- 새 공고 없음: `MM.DD 오전|오후 청약 확인 — 신규 공고 없음` 한 줄.
- 있으면 단지마다: 단지명·지역, 84㎡ 평균 분양가, 예상 프리미엄(금액 먼저, 판정 괄호), 1순위 날짜, 사이트 글 주소, 컴퓨터 폴더 경로, 확인 필요 사항(미공개 평면 등). 다음 회차로 넘긴 공고가 있으면 그 이름.
