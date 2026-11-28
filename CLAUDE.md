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
  - ~~완성 영상은 GitHub `shorts-upload/`에 올린다~~ → **2026.11.28부터 구글 드라이브 'Aside 작업용 폴더'에 원본 화질로 올린다**(아래 '어사이드 전달물' 섹션).
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
- 브동산 글 작성을 지시받으면 ① 사이트 글 작성·배포 ② `naver-html/` ③ 쇼츠·클립 영상(mp4 + 썸네일 + 업로드 정보, **구글 드라이브** 단지 폴더)까지 한 번에 끝낸다. 영상은 **1번 시네마틱 '분양가 총정리'**(`scripts/shorts/make_gen.py`, 나레이션 없음·검정 타이틀 썸네일)와 **2번 '가격 맞히기'**(`scripts/shorts/make_quiz.py`, 남자 나레이션) **두 편을 항상 함께** 만든다(2026.11.26 Paul 지시). 두 편 모두 ① 장면을 천천히 넘기고(길어져도 됨, `slow`) ② 적정가 장면은 `scripts/shorts/bridge_anim.py` 브릿지 애니메이션(비교단지 KB → 평점·연령 보정 → 평균 → (오피스텔 감액) → 브동산 적정가 → 분양가와 차이)으로 보여 준다. 기준 예: `make_gen.py`의 `firstworld` CFG, `quiz/firstworld.json`. 절차는 `beodongsan-video-team` 스킬.
- 커밋·push는 Paul에게 묻지 않고 진행한다. 다만 push 직전 `git fetch` → 원격이 바뀌었으면 병합 후 push하는 절차는 그대로 지킨다.

## 네이버 원고 하단 쇼핑커넥트 칸 (2026.11.26, 항상 적용)
- 청약·미분양(부동산·부동산이야기·부동산정보) 네이버 원고에는 **바이라인 바로 아래 회색 대가성 안내 한 줄**과 **맨 끝(출처 아래) '부동산 공부할 때 곁에 두면 좋은 것' 칸**이 항상 들어간다. 칸에는 회색 `[쇼핑커넥트 상품: ○○ — 이유]` 자리 3개만 두고, Aside가 네이버 글쓰기 창의 쇼핑커넥트로 같은 종류 상품을 넣은 뒤 회색 줄을 지운다. 네이버 원고에는 쿠팡 링크를 넣지 않는다. 공간·브랜드 글은 제외.
- 상품은 **부동산·청약 투자에 관심 있는 사람이 살 만한 것**으로, **글마다 같은 상품을 반복하지 않고 글 내용을 보고 다양하게 3개를 고른다**(2026.11.26). 판단 기준은 스킬 `.claude/skills/beodongsan-shopconnect/SKILL.md`, 상품 풀은 스크립트의 `POOL`, 글별로 직접 정한 상품은 `PICKS_BY_SLUG`.
- 새 네이버 원고를 만들면 `python3 scripts/shopconnect/apply_naver_shop.py <slug>`를 실행한다(인자 없이 실행하면 전체 재적용, 여러 번 실행해도 결과 동일). 문구·상품을 바꿀 땐 스크립트의 `TOP`/`POOL`/`PICKS_BY_SLUG`만 고치고 전체 재실행한다.

## 청약 글·네이버 발행본은 저장소 스킬이 기준 (2026.11.26, 항상 적용)
- 청약 사이트 글은 `.claude/skills/beodongsan-realestate-post/SKILL.md`(특히 1-1 섹션 배치·중복 금지, 6-2 예상 프리미엄·판정 분리), 네이버 발행본은 `.claude/skills/beodongsan-naver-copy/SKILL.md`(2026.11.21판)를 따른다. 위의 예전 네이버 규칙과 충돌하면 이 두 스킬이 이긴다. 판정은 금액 뒤에 따로(괄호 또는 별도 문장) 쓴다.
- 사이트 글: 커버 = `chart-map-naver.png`(한 번만), 1번 섹션 = 브리프 → 스탯 박스 → 레이더 → 브릿지 → 평점표 → 점수 근거 → 비교단지 후보 표, `chart-b-price.png`와 일정 표는 넣지 않는다, 청약 일정은 `chart-c-schedule.png` 하나, 공식 평면도는 모든 타입을 싣는다. 레이더·브릿지·평점표는 `scripts/beodongsan/charts.py`의 `radar`/`bridge`/`table`.
- 네이버: 본문 첫 두 문장(검색 미리보기) → 바이라인 → 6섹션. 섹션 1에 `chart-b-price.png`, 섹션 2에 `chart-a-score.png`(둘 다 `make_naver_charts.py`), 섹션 5에 공식 이미지 전부·평면 전 타입·`chart-c-schedule.png`. 표는 `python3 scripts/naver_tables_to_png.py naver-html/<slug>.html posts/images/<slug> <slug>`로 PNG로 바꾼 뒤 `apply_naver_shop.py <slug>`를 실행한다.

## 네이버 원고는 고양 한신더휴 퍼스트원과 똑같이 — 대표사진은 입지 개략도 (2026.11.26, 항상 적용)
- 네이버 원고의 기준 파일은 `naver-html/goyang-hanshin-thehue-firstone.html`이다. 굵은 첫 두 문장 → 회색 바이라인 → h1 제목 → 6섹션. 섹션 1은 chart-b → 공식 조감도 → 단지 개요 표, 섹션 2는 입지 문단 → **입지 개략도(`chart-map-naver.png`)** → 비교단지 → chart-a → 보정 표, 섹션 5는 공식 이미지(위치도·조감도·커뮤니티·단지배치도·동호수배치도·평면 전부)를 쭉 나열하고 맨 끝에 청약 일정 인포그래픽.
- **대표사진은 항상 입지 개략도**다. 메타 주석은 `cover_candidates: chart-map-naver.png (대표사진 = 입지 개략도)`, `posts-manifest.json`의 cover_candidates도 개략도 URL 하나로 둔다. 위의 2026.11.20 '차트는 chart-b 1장만, 개략도는 공식 입지도로 대신' 규칙은 이 규칙으로 대체한다.
- **섹션 5 이미지는 번호를 붙이지 않는다(2026.11.26, 앞으로 새로 쓰는 원고부터).** 홈페이지 공식 이미지를 `이미지 01 ·` 같은 연번 캡션 없이 이미지만 이어 붙이고, 그다음에 청약 일정 인포그래픽(`chart-c-schedule.png`)을 둔다. 이미 발행한 원고는 그대로 둔다.

## 줍줍찬스(미분양 줍줍 코너) `/jupjup/` (2026.11.26, 항상 적용)
- 코너 이름은 **줍줍찬스**(Paul 2026.11.26 확정, 줍줍몰에서 변경). 이름·문구에 수익을 약속하는 표현("돈 버는" 등)은 쓰지 않는다. 메뉴·제목에 줍줍찬스을 쓰고, 검색용 설명에는 "전국 미분양 줍줍 현황"을 함께 둔다.
- 전국 선착순 동·호 지정 미분양 단지를 한눈에 보여 주는 코너다. 데이터는 권역 회차(`scripts/firstcome/regions/*.json`)를 그대로 쓰고, `python3 scripts/jupjup/build_jupjup.py`가 `jupjup/index.html`·단지별 `jupjup/<key>.html`·`jupjup/data.json`·sitemap·상단 메뉴를 만든다. `region_build.py register`가 끝나면 자동으로 다시 실행된다.
- **적정가·예상 프리미엄·비교단지 시세는 코너에 쓰지 않는다.** 단지 장점은 `scripts/jupjup/points.json`에 확인된 사실만 긍정 어투로 2~3줄 쓴다. 회차에서 새 단지가 들어오면 이 파일에 키를 추가하고 빌더를 다시 돌린다(없으면 '지역·세대수·시공사' 기본 문구가 들어간다). 회차에서 빠진 단지는 '선착순 마감 확인'으로 페이지가 남는다.
- 단지 정보 표 아래에 **'모집공고 보기'(청약홈 입주자모집공고문 PDF)와 '분양 홈페이지'(청약홈 공고에 등록된 주소)** 버튼을 둔다(Paul 2026.11.26). 링크는 `scripts/jupjup/notices.json`에 있고, 새 단지는 `python3 scripts/jupjup/applyhome.py <단지명 키워드>`로 청약홈 공고를 찾아 세대수·지역을 대조한 뒤 추가한다(여러 단지·블록·회차면 공고마다 버튼). 공고를 못 찾으면 버튼 없이 둔다.
- **광고 레이더(2026.11.27)**: 네이버 배너·검색광고·분양 광고 기사에 나오는 단지는 미분양 선착순 후보다. 권역 회차의 후보 출처와 확정 기준 (c)'최근 30일 분양 광고 집행'에 추가하고, 랭킹 전이라도 `scripts/jupjup/extra_sites.json`으로 줍줍찬스에 먼저 올린다. 절차는 `docs/ad-radar.md`. **매주 수요일 9:41(베트남 시간) 정기 작업이 전국 광고 레이더를 돌려 줍줍찬스를 갱신·push하고 보고한다**(Paul 2026.11.27).
- 단지 페이지 맨 아래는 **상담사 카드(유료 광고)** 칸이다(단지당 3칸, 2주 5만원·4주 7만원, `jupjup/plans.json`).
- **지금은 계좌이체 + 메일 신청 방식(Paul 2026.11.26)**: 상담사가 `/jupjup/agent.html`에서 정보를 입력하면 메일 앱이 열려 `seodangdog81@gmail.com`으로 '[줍줍찬스 신청]' 메일을 보내고, 24시간 안에 입금한다. 정기 확인 작업(하루 2번)이 Gmail에서 새 신청을 찾아 `scripts/jupjup/agents_cli.py hold`로 칸을 맡기고(holds.json, 개인정보 없음), 카드를 검증해 둔 뒤 Paul에게 입금 여부를 묻는다. **Paul이 입금됐다고 답한 신청만** `agents_cli.py card`로 게재한다. 24시간 안에 입금 확인이 안 되면 `release`로 칸을 푼다. 상담사에게 메일을 보내지 않는다. 은행 입금 내역은 직접 확인하지 않는다(Paul 답변이 기준).
- 카드결제(토스) 코드(`api/jupjup-*.js`, plans.json `payment: "card"`)는 사업자등록·가맹 후 쓰려고 남겨 둔 것이다. 상담사 카드는 단지 정보·순서에 영향을 주지 않는다.
- **줍줍에 들어온 단지의 청약 분석 글 정리(Paul 2026.11.26)**: 같은 단지의 '부동산이야기' 청약 글 중 예상 프리미엄이 **분양가 대비 −3%보다 낮은 글은 사이트에서 내리고** `vercel.json` 영구 리다이렉트로 `/jupjup/<key>.html`에 연결한다(posts-data.js·sitemap·feed·realestate/archive 목록에서 제거, 글 파일은 남김). −3% 이내·플러스 글은 그대로 둔다. 상담사 결제 여부와 무관하게 같은 기준. 이번에 내린 9편은 `scripts/jupjup/takedown.json`에 기록돼 있고 빌더가 그 상태를 유지한다. **단지와 글을 자동으로 짝짓지 않는다** — 새 단지는 Paul이 지시할 때만 기록에 추가한다. 미분양 랭킹 글·홈 권역별 1위는 이 규칙 대상이 아니다.
- `jupjup/agents.json`·`holds.json`·`jupjup/agents/*.jpg`를 고칠 때는 push 직전 fetch·병합 규칙을 그대로 지킨다.

## 어사이드 전달물은 구글 드라이브에 올린다 — GitHub 아님 (2026.11.28 Paul 지시, 항상 적용 — 이 문서·docs·스킬의 이전 'GitHub naver-html/·shorts-upload/로 전달' 규칙보다 우선)
- 공통 지침: 드라이브 'Aside 작업용 폴더'의 문서 「배포 지침 — 배포 자료는 'Aside 작업용 폴더'로」(원본 https://claude.ai/artifact/LLrfMY7iFbBSB61rRDxDMU). 사이트 글·이미지만 GitHub(main push)로 배포하고, 네이버 원고·쇼츠/클립 영상·썸네일·업로드 정보는 GitHub에 올리지 않는다(`naver-html/`·`shorts-upload/`에 새 파일 커밋 금지, 옛 파일은 그대로).
- 'Aside 작업용 폴더'(id `1_JKxY2Q9wIX0o3e_xXMtNhc5CsRhzbd-`, Paul 컴퓨터 `G:\내 드라이브\Aside 작업용 폴더`) 안 **종류별 폴더**: '브동산 청약'(id `1s1qEU2ykR2P8UCC25OLgbu0foKssSEoX`), '브동산 미분양 랭킹'(id `1-B7fZLBvDR51oPn3o8zBL19fk-bqSpzG`), **'브동산 랭킹 쇼츠'(id `1AzhWaYbE7bNvD-rRIWu1A73KWl6Bafzh`) — '가장 ○○한 곳' 통계 랭킹 쇼츠는 배포일마다 `YYYY-MM-DD 랭킹 쇼츠 3편` 폴더(`00_읽어주세요.txt` + `NN_<slug>.mp4`·`NN_<slug>-thumbnail.png`), 하루 3편 묶음을 미리 만들어 두고 GitHub `shorts-queue`/`release_queue.sh`는 더 쓰지 않는다(2026.11.28 Paul)**. ('브동산' id `1RXIS…`는 휴지통 폴더라 쓰지 않는다.) 청약·미분양은 그 안에 콘텐츠마다 폴더 하나(`YYYY-MM-DD 단지명 (slug)`, 미분양은 `YYYY-MM-DD 권역 미분양 랭킹 (slug)`, 공고 전 글 갱신이면 끝에 ` — 수정 발행`). 도시이야기는 '브동산 도시이야기'(id `1v1ySIq0dpNMCwkg8SIlAZ4G7wHeqTHpV`), 절차는 `scripts/dosi/RUNBOOK.md`. 게시를 마치면 어사이드가 폴더 이름 앞에 [게시완료]를 붙인다.
- 파일 이름·구성(청약): `00_읽어주세요.txt`(올릴 순서·네이버 제목·태그·대표사진), `01_네이버원고.html` + `이미지/NN_<파일명>`, `02_쇼츠1-가격퀴즈.mp4`·`02_쇼츠1-썸네일.png`, `03_쇼츠2-숨은한줄.mp4`·`03_쇼츠2-썸네일.png`, `04_쇼츠-업로드-정보.txt`(제목·설명·해시태그·고정 댓글). 세부는 `docs/cheongyak-scheduled-run.md`(청약 예약 회차 지시서)가 기준.
- 올리는 법: Google Drive 커넥터 `create_file`(폴더는 `application/vnd.google-apps.folder`, 파일은 `disableConversionToGoogleType: true` + `base64Content`에 `sha256:<hex>:<절대경로>` — 작업 폴더나 scratchpad 아래 파일만, /tmp는 안 됨).
- **크기 한도:** 클라우드 예약 세션에서는 이 커넥터 호출 한 번에 약 3.1MB까지만 실린다(세션 쪽 한도라 Paul 설정으로 바뀌지 않음, 2026.11.28 확인 — 세션 종류에 따라 더 클 수 있으니 실패하면 같은 파일을 다시 보내지 않는다). 3MB 넘는 영상은 ① 세션에 Paul 컴퓨터(`jhi`)의 `G:\내 드라이브\Aside 작업용 폴더`가 연결돼 있으면 `device_commit_files`로 원본을 같은 폴더에 쓰고, ② 연결이 없으면 공통 지침대로 3MB 이하로 다시 인코딩해 올리고(정지 화면으로 화질 확인), 원본은 `SendUserFile`로 대화에도 남긴다.
- 보고에는 GitHub 링크 대신 드라이브 폴더 주소를 적는다. `naver-html/<slug>.html`은 manifest·쇼핑커넥트·표 PNG 스크립트가 읽는 작업 원본이라 저장소에 남아 있을 수 있지만 어사이드 전달은 드라이브 사본으로 한다.

## 청약 자동 글 배포는 Paul 대화 세션 안에서 돈다 (2026.11.28 Paul 지시)
- 매일 8:47·14:47(베트남 시간) 예약 메시지가 Paul과의 브동산 대화로 들어와 `docs/cheongyak-scheduled-run.md` 절차대로 새 공고를 처리하고, 결과물은 Paul 컴퓨터의 `G:\내 드라이브\Aside 작업용 폴더\브동산 청약\` 아래 단지 폴더에 바로 저장한다(원본 화질). 보고도 그 대화로 한다. 각 회차가 다음 회차를 예약한다.

## 글 목록 카드에는 대표사진(썸네일)을 붙인다 (2026.11.28 Paul 지시)
- 모든 글은 `posts/images/<slug>/thumb.jpg`(가로 720px)와 `posts-data.js`의 `thumb` 필드를 가진다. `feed.js`가 카드 오른쪽(폰은 위쪽)에 사진으로 보여 준다.
- **새 글을 posts-data.js에 등록한 뒤 `python3 scripts/build_thumbs.py`를 실행한다**(썸네일 없는 글만 만듦, 특정 글만 다시 만들 땐 slug 인자). 청약 글은 공식 조감도·투시도를 고르고, 없으면 커버(입지 개략도)를 쓴다. 다른 사진을 쓰고 싶으면 그 글의 thumb.jpg만 바꿔 넣으면 된다.
