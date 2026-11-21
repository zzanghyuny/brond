# 쇼츠·클립·릴스 영상 생성기 (2026.11.15)

단지 하나당 9:16(1080×1920) 30~33초 시네마틱 영상을 코드로 렌더링한다. 외부 AI 서비스 없음.

```
SHORTS_OUT=/tmp/shorts-out/ python3 scripts/shorts/make_gen.py <키>      # 렌더 + 음악 + 효과음 믹스 → <out>-shorts.mp4
SHORTS_OUT=/tmp/shorts-out/ python3 scripts/shorts/make_gen.py <키> 4.5 17  # 정지 화면만 (시각 확인용)
```
- 키는 `make_gen.py`의 `CFG`(armusee / ulsan / choryang / daejang). **새 단지는 `CFG`에 항목 하나를 추가한다**(이미지 파일명·가격·비교단지·청약 정보·장면 목록).
- 의존: Python, Pillow, numpy, ffmpeg, 폰트 WQY Zen Hei(`/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc`).
- 스타일: 검정 바탕 + 황동 `#C8A45C` 포인트 + 크림 흰색 글씨. 음악은 `audio_orig.py`(저음 드론·패드·펄스, 나레이션 없음).
- **효과음(`sfx.py`, 2026.11.15부터 새 영상에 적용)**: 장면 전환마다 whoosh, 예상 프리미엄 공개에 lowhit+ping, 마무리 직전 shimmer, 평균 분양가 카운트업에 tick(약하게).
- 구성: 오프닝 → 조감도 → 평균 분양가 → 비교단지 KB시세 → 예상 프리미엄 → 단지 배치도/특징 → 입지 → 청약 체크 → 마무리. 단지별로 쓸 수 있는 공식 이미지에 따라 장면을 가감한다(`scenes`).
- 영상을 줄 때는 항상 **제목**도 함께 준다(`단지명 | 예상프리미엄 -N, 분양가 총정리` 형식 기본).
- 효과음 적용 전 4편(아르뮤제자이·울산 아르엘·부천대장·초량)은 효과음 없이 발행됨.
- 영상과 함께 썸네일 `<out>-thumbnail.png`도 항상 생성·전달한다.

---

# 1안 '가격 맞히기 퀴즈' 쇼츠 (2026.11.22 개정, 나레이션 포함)

기존 시네마틱 쇼츠(나레이션 없음)를 대신하는 기본 포맷. 기획·검수 절차는 `beodongsan-video-team` 스킬.

- `make_quiz.py` — 렌더러. **단지마다 `quiz/<단지>.json` 하나만 쓰면 된다**(예: `quiz/sangok.json`). 장면 s1~s8:
  s1 훅(조감도 + 질문 2줄 + **단지명·지역**) → s2 **입지 개략도**(`chart-map-naver.png`를 어두운 테마로 바꿔 SITE에 황동 고리, 아래 힌트 3줄) → s3 A·B·C + 3초 카운트다운 → s4 정답 → s5 첫 반전(막대) → s6 비교단지 시세 → 적정가 → s7 판정 배지(plus·minus·even) → s8 조건·일정 → 첫 화면으로 루프.
  장면 길이는 나레이션 길이로 자동 결정. 나눔고딕, dark 테마, 음악 `audio_orig.py` + 효과음 `sfx.py` + 나레이션 덕킹.
- 채널 보이스 `ko-KR-InJoonNeural`, 속도 `+16%`, 피치 `-3Hz`(edge-tts). `tts` 명령이 JSON의 `narration`으로 s1~s8.wav를 만든다.
- `quiz/bucheon-daejang.txt` — 첫 편(2026.11.21, 개정 전 구성) 원고 기록.

```
pip install edge-tts
mkdir -p /tmp/nanum
for w in Regular Bold ExtraBold; do curl -sSL -o /tmp/nanum/NanumGothic-$w.ttf https://raw.githubusercontent.com/google/fonts/main/ofl/nanumgothic/NanumGothic-$w.ttf; done
cd scripts/shorts
python3 make_quiz.py quiz/sangok.json tts                    # 나레이션(장면별 길이 출력) — 합계 34초 안팎이면 영상 40초대
python3 make_quiz.py quiz/sangok.json stills 4.5 8 13 22.6   # 정지 화면 확인 → /tmp/shorts-out/still_*.png
python3 make_quiz.py quiz/sangok.json render                 # → /tmp/shorts-out/sangok-quiz.mp4 + -thumbnail.png (약 2분)
```

주의
- 나눔고딕에는 `㎡`·`−`(U+2212)·`①` 글자가 없다. 화면 글자는 `m²`, `-`, `1`로 쓴다(나레이션은 '제곱미터').
- 입지 개략도는 포스팅마다 만드는 `posts/images/<slug>/chart-map-naver.png`를 그대로 쓴다. SITE는 황동 사각형 위치로 자동으로 찾는다.
- Edge 음성은 브라우저 '소리 내어 읽기' 서비스라 수익 채널의 상업적 사용 조건이 불분명하다. 수익화하면 같은 목소리를 Azure TTS(유료)로 다시 만들거나 Higgsfield 음성으로 바꾼다.
- 완성 영상·썸네일은 `shorts-upload/<YYYY-MM>/`에 올리고 그 폴더 README에 제목·설명·해시태그를 적는다. Aside가 유튜브 업로드를 마치면 Paul이 삭제를 요청하고, 그때 지운다(2026.11.21).
