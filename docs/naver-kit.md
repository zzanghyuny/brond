# 네이버 폰 발행 키트 (naver-kit)

폰의 네이버 블로그 앱으로 글을 올릴 때 쓰는 페이지. 앱 에디터는 HTML 통째 붙여넣기·표·외부 이미지 URL을 안정적으로 받지 못해서, `naver-html/<slug>.html`을 **순서대로 복사·저장하는 블록**으로 바꿔 둔다.

## 폰에서 쓰는 법 (아이폰·안드로이드 공통)
1. 폰 브라우저에서 `https://www.brandongsan.com/naver-kit/<slug>.html`(목록: `/naver-kit/index.html`)을 연다. 검색엔진에는 노출되지 않는다(noindex, robots 차단).
2. 맨 위 **이미지 전체 받기(zip)** 로 번호 붙은 사진을 폰에 저장한다(파일 앱/갤러리에서 압축 해제). 개별 이미지는 칸마다 [이미지 저장]이나 길게 눌러 저장.
3. 네이버 앱 글쓰기를 열고, 위에서부터 **[복사] → 앱 본문에 붙여넣기**. 제목·태그는 첫 두 칸.
4. 이미지 칸이 나오면 앱의 사진 추가로 **같은 번호의 사진**을 넣는다. 표와 스탯 박스는 이미지로 만들어져 있다.
5. 각 칸의 완료 체크는 폰에 기억된다(상단 진행률). 맨 아래 체크리스트(카테고리 부동산이야기·대표 이미지·발행)로 마무리.

한계: 앱이 붙여넣은 글의 굵게·링크를 일부 지울 수 있다(소제목은 앱에서 굵게/크게 직접 지정). 앱 에디터 동작은 버전마다 달라 실제 폰에서 첫 글로 확인이 필요하다.

## 다시 만들기
```bash
python3 scripts/naver_kit.py <slug> [<slug> ...]   # 글 하나 이상
python3 scripts/naver_kit.py --all                  # 발행 전(naver_published=false) 전체
python3 scripts/naver_kit.py --index-only           # 목록 페이지만
```
결과: `naver-kit/<slug>.html`, `naver-kit/<slug>/NN-*.png|jpg`(발행 순서 번호), `naver-kit/<slug>.zip`, `naver-kit/index.html`. 표가 5열 이상이면 경고를 출력한다(폰에서 글씨가 작아짐 — 글에서 4열 이하로 줄이거나 문장을 짧게). `naver-html` 파일은 바꾸지 않는다. 필요: Python(bs4, Pillow), Node Playwright(표·스탯 박스 렌더).
