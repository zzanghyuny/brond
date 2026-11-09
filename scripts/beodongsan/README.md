# scripts/beodongsan/ — 적정가 산출·차트 생성 헬퍼

청약·분양 포스팅(`beodongsan-realestate-post`, `beodongsan-naver-copy` 스킬)을 작성할 때 재사용하는 파이썬 헬퍼. 2026.11.09, 15개 포스팅 네이버 리라이트 작업 중 scratchpad에서 만든 것을 저장소에 정식으로 옮겼다 — 매번 새 세션에서 처음부터 다시 만들지 않도록.

## 파일
- `kb.py` — KB부동산(kbland.kr) 내부 API 검색 헬퍼(`search(keyword)`). 응답 캐시(`kbcache.json`, gitignore 대상 — 커밋하지 않는다).
- `kb_detail.py` — `kb.py` 기반 단지 상세 조회(`info(no)`, `types(no)`, `sise(no, seq)`). `kb.py`와 같은 디렉터리에서 `from kb import ...`로 쓰므로, 실행 전 `sys.path.insert(0, 'scripts/beodongsan')` 필요.
- `model.py` — 브동산 모형 점수·보정 계산(`subway()`, `hh()`, `pk()`, `cv()`, `calc()`, `man()`, `man_txt()`). 점수 체계·가중치는 `.claude/skills/beodongsan-realestate-post/SKILL.md` 참고.
- `charts.py` — 사이트용 흑백 SVG 차트(`mapsvg()`, `radar()`, `bridge()`, `table()`).
- `make_naver_charts.py` — 네이버용 matplotlib PNG 차트 3종(`chart_a`/`chart_b`/`chart_c`). 폰트는 이 컨테이너에 NotoSansCJK가 없어 `/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc`(WenQuanYi Zen Hei)로 대체 — 한글 렌더링 확인됨(2026.11.09). 다른 환경에서 NotoSansCJK가 있으면 그쪽을 우선 사용.

## 사용 예
```python
import sys
sys.path.insert(0, 'scripts/beodongsan')
from kb import search
from kb_detail import info, types, sise
from model import subway, hh, pk, cv, calc, man, man_txt
import charts

no, name, addr = search('단지명')[0]
i = info(no)
```

## 주의
- KB시세·실거래 수치는 반드시 실제 API/공식 자료에서 가져온다. 이 스크립트는 계산·시각화 도구일 뿐, 숫자를 추정하거나 지어내지 않는다.
- `kbcache.json`, `geo_cache.json` 같은 캐시 파일은 커밋하지 않는다(`.gitignore` 확인).
