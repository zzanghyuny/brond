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

# 1안 '가격 맞히기 퀴즈' 쇼츠 (2026.11.21, 나레이션 포함)

기존 시네마틱 쇼츠(나레이션 없음)를 대신하는 새 포맷. 첫 편: 부천대장 하우스토리 디센트(40.5초). 기획·검수 절차는 `beodongsan-video-team` 스킬.

- `make_quiz.py` — 렌더러. 장면 s1~s8(훅 → 힌트 3개 → A·B·C 3초 카운트다운 → 정답 → 첫 반전 → 비교단지·적정가 → 판정 배지 → 조건·일정·루프). **장면 길이는 나레이션 길이로 자동 결정**된다. 나눔고딕, dark 테마(디자인 가이드라인 영상 규칙), 음악 `audio_orig.py` + 효과음 `sfx.py` + 나레이션 덕킹.
- `tts_edge.py` — 나레이션 TTS. 채널 보이스 `ko-KR-InJoonNeural`, 속도 `+16%`, 피치 `-3Hz`.
- `quiz/<단지>.txt` — 장면별 나레이션 원고(`s1|문장` 형식).

```
pip install edge-tts
mkdir -p /tmp/nanum /tmp/quiz-tts
for w in Regular Bold ExtraBold; do curl -sSL -o /tmp/nanum/NanumGothic-$w.ttf https://raw.githubusercontent.com/google/fonts/main/ofl/nanumgothic/NanumGothic-$w.ttf; done
cd scripts/shorts
while IFS='|' read k t; do
  python3 tts_edge.py ko-KR-InJoonNeural +16% -3Hz "$t" /tmp/quiz-tts/$k.mp3 </dev/null
  ffmpeg -nostdin -v error -y -i /tmp/quiz-tts/$k.mp3 -af "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse" -ar 44100 -ac 1 /tmp/quiz-tts/$k.wav
done < quiz/bucheon-daejang.txt
python3 make_quiz.py stills 3.6 13.2 16.5 30.5   # 정지 화면 확인
python3 make_quiz.py render                      # → /tmp/shorts-out/bucheon-daejang-quiz.mp4 (약 1분 30초)
ffmpeg -i /tmp/shorts-out/bucheon-daejang-quiz.mp4 -c:v libx264 -preset veryfast -crf 23 -c:a copy -movflags +faststart out.mp4  # 업로드용 압축(약 4MB)
```

주의
- 나눔고딕에는 `㎡`·`−`(U+2212)·`①` 글자가 없다. 화면 글자는 `m²`, `-`, `1`로 쓴다.
- 새 단지는 `make_quiz.py`의 장면 함수 안 숫자·문구(HINTS, OPTS, s5~s8)와 `IMG`, 원고 파일을 바꾼다. 다음 편부터는 단지별 설정을 `CFG`로 빼는 것이 좋다.
- Edge 음성은 브라우저 '소리 내어 읽기' 서비스라 수익 채널의 상업적 사용 조건이 불분명하다. 수익화하면 같은 목소리를 Azure TTS(유료)로 다시 만들거나 Higgsfield 음성으로 바꾼다.
- 영상 파일(mp4)은 저장소에 올리지 않는다(2026.11.20 Paul 요청으로 `shorts-upload/` 제거).
