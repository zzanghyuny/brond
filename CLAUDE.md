# 브동산 — Claude Code 작업 지침

이 저장소에서 작업을 시작하기 전에 **[claude/handoff-master.md](claude/handoff-master.md)를 반드시 전체 읽을 것.** 디자인 기준, 콘텐츠 제작 기준(부동산/브랜드), 적정가 산출법("브동산 모형"), 지도 어노테이션 절차, IT/배포 기준, 반복 실수 노트 등 모든 업무 기준이 그 문서 하나에 정리돼 있다. 이 문서는 그 위에 **Claude Code(로컬 세션) 전용으로 달라지는 부분만** 보충한다.

## Claude Code 세션에서 달라지는 점 (master 문서와의 차이, 2026.09.12 확인)

master 문서는 claude.ai 클라우드 채팅 세션 기준으로 작성돼 일부 제약이 있는데, 이 저장소를 직접 다루는 Claude Code 로컬 세션에서는 아래 사항들이 다르다.

1. **이미지 캡처**: master 3-5는 "Claude가 클라우드 세션에서 임의 웹사이트 이미지를 직접 다운로드/캡처할 수 없다"고 되어 있으나, Claude Code에는 브라우저 도구(`mcp__Claude_Browser__*`)가 있어 공식 홈페이지에 직접 접속해 스크린샷/확대 캡처가 가능하다. Paul과 합의된 방식은 **파일 다운로드보다 스크린샷 캡처 우선** — 매번 다운로드 승인을 받는 대신 화면 캡처로 필요한 영역(조감도·평면도·위치도 등)을 가져와 활용한다.
2. **GitHub 배포**: master 7-1은 "GitHub 자동 업로드는 클라우드 세션에서 불가능(push 차단)"이라고 되어 있으나, 이 로컬 저장소는 `origin`(`zzanghyuny/brond`, main)에 대한 push 권한이 확인됐다(2026.09.12, `git push --dry-run` 성공). 즉 **이 세션에서는 완성된 파일을 직접 커밋·푸시해 배포할 수 있다** — Paul이 GitHub 웹 UI로 수동 업로드할 필요 없이, 커밋 전 반드시 변경 파일과 커밋 메시지를 Paul에게 보여주고 확인받은 뒤 진행한다(일반 git 안전수칙 동일 적용). **다만 이 저장소는 Paul이 GitHub 웹 UI로도 동시에 손댈 수 있다는 뜻이기도 하다 — push 직전 반드시 `git fetch`+`git log origin/main`으로 원격이 그 사이 바뀌지 않았는지 확인하고, 바뀌었다면 `git merge origin/main`으로 반영한 뒤 내용을 실제로 대조하고 나서 다시 push한다(2026.09.12, 이 세션 작업 중 Paul이 GitHub 웹 UI로 posts-data.js/feed.js 피드 시스템을 실제로 올리는 바람에 최초 push가 non-fast-forward로 거절되고 병합이 필요했던 사례 있음 — 아래 3번째 차이 참고).**
3. **포스팅 피드 시스템(`posts-data.js`/`feed.js`) — 이제 실제로 구현되어 있음(2026.09.12 최종 확인)**: master 7-2-A와 위 항목이 한동안 "설계만 있고 미구현"이라고 기록했었으나, 2026.09.12 이 세션 작업 도중 Paul이 GitHub 웹 UI 업로드로 `posts-data.js`·`feed.js`를 실제로 추가하고 `index.html`·`brand.html`을 feed 방식으로 전환했다. 다만 그 업로드에서 `realestate.html`은 동일 파일명 충돌로 덮어써지지 않고 `realestate-1.html`이라는 별도 파일로 남는 사고가 있었다(Paul이 의도한 것은 realestate.html 자체를 feed 방식으로 바꾸는 것이었던 것으로 보임) — 이 세션에서 realestate.html을 feed 방식으로 직접 정정하고 병합했다. **새 포스팅 추가 시 이제부터는 `realestate.html`/`brand.html`에 카드를 직접 추가하지 않고, `posts-data.js`의 `POSTS` 배열에 객체 하나만 추가한다.** `realestate-1.html`은 내용이 이제 중복이라 정리 대상이지만, Paul 업로드 파일이라 이 세션이 임의로 삭제하지 않고 남겨뒀다 — 필요 없으면 Paul이 GitHub에서 직접 삭제하거나 삭제를 요청하면 된다.
4. **이미지 파일 형식**: master 3-2는 "Artifact CSP 때문에 data: URI(base64) 인라인 임베드 필수"라고 되어 있으나, 이는 Artifact 미리보기 환경의 제약이다. 이 저장소는 GitHub+Vercel로 직접 서빙되는 정적 사이트라 이 제약이 없다 — **포스팅 이미지는 `posts/images/<포스팅명>/` 아래 별도 파일로 저장하고 상대경로 `<img src="images/...">`로 참조한다.** base64로 인라인 임베드하면 HTML 파일이 수 MB로 불어나(기존 1·2호 포스팅이 이 방식이라 파일당 2~5MB) git diff·로딩 속도에 불리하므로, 새 포스팅부터는 별도 파일 방식을 기본으로 한다. `style="width:100%;display:block;"` 인라인 스타일은 형식과 무관하게 계속 필수(master 3-2 규칙 그대로 유지).
5. **이미지 처리 도구 없음**: 이 로컬 PC(Paul 컴퓨터)에는 Python/PIL, ImageMagick, Node.js가 설치돼 있지 않다(2026.09.12 확인, Windows Store 스텁만 존재). master 3-2·4-4가 전제하는 "bash+PIL 리사이즈·압축", "PIL+numpy 지도 색 채널 탐지" 절차를 이 세션에서는 그대로 실행할 수 없다. 대안: (a) 이미지 리사이즈·압축 없이 원본 그대로 사용(공식 홈페이지 이미지는 대체로 1~2MB대라 치명적이지 않음), (b) Paul이 마커 찍어준 실제 지도 스크린샷을 그대로 가공하는 대신, 지도에서 관찰한 상대 위치를 바탕으로 **브동산 자체 제작 SVG 개략도**(코드로 직접 좌표 지정)를 그려 대체한다 — 색 규칙(SITE=빨강, 비교단지=초록, 배정초=파랑)은 동일하게 적용하되 "브동산 자체 제작 개략도"임을 캡션에 명시. Paul이 Python 설치를 원하면 그때 다시 PIL 기반 절차로 전환.

## 새 포스팅(부동산) 작업 시작 시 체크
- master 4-6에 따라 필요한 사진(대표사진/교통망·위치도/조감도·배치도·평면도/적정가용 지도)을 Paul에게 요청되어 있는지 확인.
- master 4-3의 적정가 산출 절차, 4-4의 지도 마킹 색 규칙(SITE=빨강, 비교단지=초록, 배정초등학교=파랑)을 그대로 따를 것.
- 작업 중 master 문서와 실제 최신 게시물([posts/](posts/)) 코드가 다르면 실제 코드 쪽을 우선 참고하고 master 문서 업데이트가 필요한지 Paul에게 확인(master 10-1 교훈).

## 포스팅 운영 방식 변경 (2026.10.31) — 네이버용 HTML은 GitHub에 올린다

- **네이버용 HTML은 로컬 PC 폴더(`D:\Paul Kim\네이버용` 등)에 저장하지 않고 `naver-html/{slug}.html`로 저장해 커밋·push한다.** Paul과 Aside가 GitHub에서 내려받아 네이버 블로그에 발행한다(발행은 Aside, 작성·push·배포확인은 Claude Code).
- 네이버 제목 구분자는 **세로선 ` | `** (예: `아크메르 동탄 | 예상프리미엄 +2.9억, 분양가 평면 총정리`). 슬래시(` / `) 아님.
- 네이버용에는 차트(레이더·브릿지) 이미지를 넣지 않는다. 위치 개략도 `chart-map.png`만 쓴다.
- `naver-html/*.html`에는 `<meta name="robots" content="noindex,nofollow">`와 상단 메타 주석(slug/title/category/naver_category/tags/cover_candidates)을 넣고, `posts-manifest.json`을 `scripts/build-manifest.ps1`로 갱신한다.
- 자세한 규칙: `docs/publishing-workflow.md`, `docs/content-rules.md`, `docs/aside-handoff.md`, 스킬 `.claude/skills/beodongsan-naver-copy/SKILL.md`. 이 섹션이 master 문서·스킬의 이전 네이버 규칙(로컬 저장·차트 PNG)과 충돌하면 이 섹션을 따른다.
- 매일 오전 8시 `scripts/sync-workflow.ps1`(Windows 작업 스케줄러)이 CLAUDE.md·`.claude/skills/`·`docs/`·`posts-manifest.json` 변경분만 자동 커밋·push한다(`scripts/README.md`).

## 네이버 발행본은 승인 샘플과 똑같이 (2026.11.09, 항상 적용)
- 네이버용 HTML은 `docs/naver-sample/gwanggyo-jayeon-centreville-naver.html`과 **똑같은 양식·구조·서식**으로 쓴다(README 참고). 차트 3종은 `scripts/beodongsan/make_naver_charts.py`의 `chart_a`/`chart_b`/`chart_map`(샘플과 같은 그래프 형태)로 만들고 `posts/images/<slug>/chart-a-score.png`·`chart-b-price.png`·`chart-map-naver.png`로 저장해 절대경로 URL로 참조한다. 스킬 문서(.claude/skills)와 충돌하면 이 샘플이 이긴다.

## 청약 포스팅 맨 아래 "광고 문의" 카드는 쓰지 않는다 (2026.11.13, 항상 적용)
- 청약(부동산) 포스팅 하단의 `section#ad`(`.sponsor` 광고 문의 카드·"광고 문의하기" 버튼)는 의미가 없어 94개 포스팅에서 모두 제거했다. **앞으로 새로 만드는 포스팅과 기존 글을 복제한 템플릿에도 넣지 않는다.** 기존 글을 스캐폴드로 복사할 때는 이 블록이 남아 있지 않은지 확인한다. 네이버용 HTML에는 원래 없다.

## 비교단지 시세는 직접 넓게 검색해서 고른다 — 묻지 말고 작성·배포까지 (2026.11.14, 항상 적용)
- 새 글을 쓸 때도, 이미 쓴 글을 고칠 때도 비교단지 시세는 Paul에게 묻지 않고 직접 찾는다. `scripts/beodongsan/comp_scan.py <시·구> --area 84`로 해당 지역의 2016년 이후 준공·500세대 이상 단지를 KB 일반거래가와 함께 전수 스캔(키워드 여러 개 가능)하고, KB가 비어 있는 최근 입주 단지는 국토부 실거래 신고로 보완한다.
- 후보 중 2곳은 **정해진 기준**(같은 동·생활권 이웃 1곳 + 가장 가까운 중심권 신축 대단지 1곳, 연식·규모·브랜드 등급 근접)으로 고르고, 가격이 높거나 낮다는 이유로 고르거나 빼지 않는다. 선정 기준과 후보 표(탈락 사유 포함)를 글의 비교단지 단락에 한두 문장으로 밝힌다.
- 고른 뒤에는 결과가 어떻게 나오든 사실대로 쓰고, 사이트 글·네이버용·등록 파일을 맞춰 push까지 끝낸다.

## 네이버 발행본은 모바일 폭 기준 (2026.11.14, 항상 적용)
- 네이버 글·이미지는 **폰 폭 기준**으로 만든다. 규칙 전문은 `docs/naver-mobile-spec.md`: 이미지 캔버스 폭 1000px·글씨 28px 이상(차트는 `scripts/beodongsan/make_naver_charts.py` 기본 `mobile=True`), 표는 4열 이하이거나 이미지로, 문단은 2~3문장, 공식 사진은 가로 ≤1000px·≤400KB. 만든 차트는 390px로 줄여 읽히는지 확인한다.
- 승인 샘플의 섹션 구성·문체는 그대로, 크기·배치만 이 규칙이 우선한다.
- **폰 키트(`naver-kit/`)는 만들지 않는다(2026.11.26 Paul 지시, 기존 키트·`scripts/naver_kit.py` 삭제).** 네이버 발행은 `naver-html/<slug>.html`만으로 한다.

## 네이버 발행본 섹션 1·5 구성 변경 + 인포그래픽 포인트색 (2026.11.15, 항상 적용)
- **섹션 1**: 조감도 아래 `어디?/언제?/얼마?/주의` 네 줄을 쓰지 않고, **단지 개요 표(2열)**를 넣는다(위치·규모·시행시공·공급 구성·입주 예정·청약 일정·84㎡ 분양가·규제·주의). 예전 섹션 5의 개요 표를 여기로 옮긴 것이다.
- **섹션 5**: 위치도·조감도·배치도·동호수 배치도·평면도(특수 타입 포함)·**청약 일정 이미지**까지 **이미지를 한 번에 이어 붙인다**. 중간의 h3 제목·설명 문단·표는 없애고 `이미지 NN · 종류` 캡션만 둔다. 설명은 맨 아래 `정리` 한 곳에 간단히(타입별 분양가 표 + 한두 문단).
- **인포그래픽 색**: 흑백 심플 모던 + **포인트 색 황동 `#C8A45C`**(쇼츠·클립·릴스 영상과 통일). `make_naver_charts.py`의 `ACCENT`. 승인 샘플·`docs/naver-sample/`이 기준.
- **쇼츠·클립·릴스 영상**: 검정 배경 + 황동 포인트 + 드론/펄스 앰비언트 음악(원래 스타일), 구성은 최근 구성(조감도 → 가격 분석 → 단지 정보 → 마무리). 나레이션 없음.
  - **2026.11.21 개정:** 새 쇼츠는 **1안 '가격 맞히기 퀴즈' + 남자 나레이션**(`scripts/shorts/make_quiz.py`, 채널 보이스 `ko-KR-InJoonNeural` +16% −3Hz, 30~40초)으로 만든다. 기획·검수 절차는 `beodongsan-video-team` 스킬, 렌더 방법은 `scripts/shorts/README.md`. 위의 '나레이션 없음' 시네마틱 형식은 더 이상 기본이 아니다.
  - **완성 영상은 GitHub `shorts-upload/<YYYY-MM>/`에 올린다**(mp4 + `-thumbnail.png` + README의 제목·설명·해시태그). Aside가 유튜브 업로드를 마치면 Paul이 삭제를 요청하고, 그때 해당 파일을 지운다.
- **효과음(2026.11.15 확정, 다음 영상부터)**: 장면 전환마다 whoosh, 예상 프리미엄 공개에 lowhit+ping, 마무리 직전 shimmer, 평균 분양가 카운트업에 tick(약하게). 생성기는 `scripts/shorts/`(`README.md` 참고). 영상을 줄 때는 항상 제목도 함께 준다.
- **영상을 줄 때는 항상 썸네일(커버) 이미지도 함께 준다**(2026.11.16). `make_gen.py`가 영상과 함께 `<out>-thumbnail.png`(1080×1920, 대표 이미지 + 단지명 + 황동 예상 프리미엄)를 만든다.

## 신규 청약 단지 전체 절차 인수인계서 (2026.11.19)
- 공고 확인 → 사이트 글 → 네이버용 → 쇼츠 영상·썸네일 → 배포 확인까지 한 단지를 끝내는 전체 절차는 `docs/handoff-cheongyak-pipeline.md`에 정리돼 있다. 새 세션은 이 문서부터 읽는다.

## 네이버 발행본 레이아웃 개정 (2026.11.20, 항상 적용 — 이전 네이버 규칙보다 우선)
- 기준 글은 네이버 `bds_unboxing/224483930499`(더샵 천안라크원), 샘플 파일은 `docs/naver-sample/thesharp-cheonan-lac-one-naver.html`, 규칙 전문은 `docs/naver-sample/README.md` 맨 위 섹션이다.
- **긴 문장 대신 표와 짧은 문장**: 가격·개요·비교단지·평점·보정·최근 분양·타입별 공급가·접수 일정은 4열 이하 표로, 설명은 문단당 1~2문장.
- 맨 첫 문단은 **요약문**(지역·단지명·세대수·84㎡ 분양가·적정가격·1순위 날짜), 그 아래 바이라인. h2는 짧게(`1. 결론부터` … `6. 결론 — 접수 일정`).
- 차트는 적정가격 막대(chart-b) 1장만. 평점 막대(chart-a)·위치 개략도(chart-map)는 표·공식 입지도로 대신한다.


## 쿠팡 파트너스 상품 카드 (2026.11.21, 항상 적용)
- 청약 언박싱 등 `realestate` 글(미분양 랭킹 제외)과 `space` 글에는 **결론 섹션 바로 아래 흑백 상품 카드 1칸**(입주청소 용품·이사박스·암막커튼 쿠팡 검색 링크)과 **바이라인 바로 아래 대가성 문구**가 들어간다. brand·vietnam·미분양 랭킹 글과 네이버용 HTML에는 넣지 않는다.
- 새 글을 발행할 때는 `posts-data.js`에 등록한 뒤 `python3 scripts/coupang/apply_coupang.py posts/<slug>.html`을 실행한다(인자 없이 실행하면 대상 글 전체에 다시 적용, 여러 번 실행해도 결과 동일).
- 링크·문구를 바꿀 때는 스크립트의 `LINKS`/`DISCLOSURE`만 고치고 전체 재실행한다. 링크에는 `rel="sponsored nofollow noopener"`를 유지한다.

## 홈 대문 개편 (2026.11.21, 항상 적용)
- `index.html`은 브랜드 가이드라인(https://claude.ai/artifact/XbzLGmuWNj2MSeKoBXPon9) 기준의 새 대문이다: 히어로(텍스트) + 황동 박스 '이번 주 가장 큰 저평가' → 최근 청약 판정 카드 6개(분양가·적정가격 막대) → 미분양 랭킹 권역별 1위 → 이야기 3칸 → 최근 포스팅 피드.
- 숫자는 모두 `home.js`가 `posts-data.js` 제목에서 자동으로 계산한다. **새 글 제목에 `NN㎡ (평균) 분양가 X.XX억`과 `예상 프리미엄 ±N`을 지키면 홈에 자동으로 실린다**(적정가격 = 분양가 + 예상 프리미엄, ±3% 안은 '적정'). 미분양 랭킹은 제목의 `TOPn`과 `1위 단지 예상 프리미엄은 ±N`을 읽는다. `index.html`을 손으로 고칠 필요 없다.
- 홈 전용 스타일은 `styles.css` 맨 아래 '홈 대문 개편' 블록(`.wrap-home` 최대 960px, `.home-*`, `.jc-*`, `.rk*`, `.story*`).

## 오피스텔 적정가 — 아파트 59㎡로 비교하고 마지막에 10% 감액 (2026.11.26, 항상 적용)
- 오피스텔 전용 84㎡는 실사용 면적이 아파트 59㎡와 비슷하므로 **주변 아파트 59㎡ KB 시세로 비교단지를 잡는다**(비교단지 선정 기준·평점·연식 보정은 아파트와 같다). 다른 면적의 오피스텔도 실사용 면적이 비슷한 아파트 평형으로 맞춘다.
- 그렇게 낸 아파트 기준 적정가에 **마지막 단계로 ×0.9(10% 감액)**를 한 값이 브동산 적정가다. 이유: 취득세 부담, 작은 대지지분, 좁은 투자 수요(환금성). 글의 계산식에 `아파트 59㎡ 기준 적정가 → 오피스텔 10% 감액`을 그대로 밝힌다.
- 단지별 실제 대지지분이 아파트와 비슷하거나 크면 감액은 그대로 하되 그 사실을 글에 한 줄로 적는다(첫 적용: `posts/thesharp-firstworld-seoul-officetel.html`).
- 오피스텔 공고는 청약홈 APT 목록이 아니라 `오피스텔/생활숙박시설/도시형생활주택/민간임대` 목록(`selectOtherLttotPblancListView.do`)에 올라온다. 분양가는 공고문 층별 공급금액을 실수로 가중평균한다.

## 글 작성 지시 = 한 세트 + 묻지 않고 push (2026.11.26, 항상 적용 — 위 2번 '커밋 전 확인' 규칙보다 우선)
- 브동산 글 작성을 지시받으면 ① 사이트 글 작성·배포 ② `naver-html/` ③ 쇼츠·클립 영상(`shorts-upload/<YYYY-MM>/` mp4 + 썸네일 + README)까지 한 번에 끝낸다. 영상은 반응이 좋은 **'가격 맞히기'**(`scripts/shorts/make_quiz.py`)와 **'공고문 속 숨은 한 줄'**(`scripts/shorts/make_viral.py`, detective 형식) 시리즈로 만든다.
- 커밋·push는 Paul에게 묻지 않고 진행한다. 다만 push 직전 `git fetch` → 원격이 바뀌었으면 병합 후 push하는 절차는 그대로 지킨다.

## 네이버 원고 하단 쇼핑커넥트 칸 (2026.11.26, 항상 적용)
- 청약·미분양(부동산·부동산이야기·부동산정보) 네이버 원고에는 **바이라인 바로 아래 회색 대가성 안내 한 줄**과 **맨 끝(출처 아래) '부동산 공부할 때 곁에 두면 좋은 것' 칸**이 항상 들어간다. 칸에는 회색 `[쇼핑커넥트 상품: ○○ — 이유]` 자리 3개만 두고, Aside가 네이버 글쓰기 창의 쇼핑커넥트로 같은 종류 상품을 넣은 뒤 회색 줄을 지운다. 네이버 원고에는 쿠팡 링크를 넣지 않는다. 공간·브랜드 글은 제외.
- 상품은 **부동산·청약 투자에 관심 있는 사람이 살 만한 것**(투자 입문서, 레이저 거리측정기, 서류 보관 파일 / 미분양·선착순 글은 사전점검 키트)으로, 글 종류별 목록은 `scripts/shopconnect/apply_naver_shop.py`의 `PICKS`에 있다.
- 새 네이버 원고를 만들면 `python3 scripts/shopconnect/apply_naver_shop.py <slug>`를 실행한다(인자 없이 실행하면 전체 재적용, 여러 번 실행해도 결과 동일). 문구·상품을 바꿀 땐 스크립트의 `TOP`/`PICKS`만 고치고 전체 재실행한다.

## 청약 글·네이버 발행본은 저장소 스킬이 기준 (2026.11.26, 항상 적용)
- 청약 사이트 글은 `.claude/skills/beodongsan-realestate-post/SKILL.md`(특히 1-1 섹션 배치·중복 금지, 6-2 예상 프리미엄·판정 분리), 네이버 발행본은 `.claude/skills/beodongsan-naver-copy/SKILL.md`(2026.11.21판)를 따른다. 위의 예전 네이버 규칙과 충돌하면 이 두 스킬이 이긴다. 판정은 금액 뒤에 따로(괄호 또는 별도 문장) 쓴다.
- 사이트 글: 커버 = `chart-map-naver.png`(한 번만), 1번 섹션 = 브리프 → 스탯 박스 → 레이더 → 브릿지 → 평점표 → 점수 근거 → 비교단지 후보 표, `chart-b-price.png`와 일정 표는 넣지 않는다, 청약 일정은 `chart-c-schedule.png` 하나, 공식 평면도는 모든 타입을 싣는다. 레이더·브릿지·평점표는 `scripts/beodongsan/charts.py`의 `radar`/`bridge`/`table`.
- 네이버: 본문 첫 두 문장(검색 미리보기) → 바이라인 → 6섹션. 섹션 1에 `chart-b-price.png`, 섹션 2에 `chart-a-score.png`(둘 다 `make_naver_charts.py`), 섹션 5에 공식 이미지 전부·평면 전 타입·`chart-c-schedule.png`. 표는 `python3 scripts/naver_tables_to_png.py naver-html/<slug>.html posts/images/<slug> <slug>`로 PNG로 바꾼 뒤 `apply_naver_shop.py <slug>`를 실행한다.
