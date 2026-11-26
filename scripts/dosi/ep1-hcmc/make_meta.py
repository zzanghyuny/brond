# -*- coding: utf-8 -*-
"""설명란(챕터·출처)과 credits_log.csv 만들기 — 렌더 뒤 실행."""
import json, csv, sys
sys.path.insert(0, '/home/claude/work/ep1')
import script_ep1 as S
D = '/home/claude/work/ep1/'
TODAY = '2026-11-27'
def mmss(t): t = int(round(t)); return f'{t // 60}:{t % 60:02d}'
tl = {w: json.load(open(f'{D}out_{w}/timeline.json')) for w in ('LONG', 'S1', 'S2')}

chap = [(0, '오프닝 — 서울 위에 겹쳐 본 호치민')]
for i, s in enumerate(S.LONG):
    if s.get('chapter'): chap.append((tl['LONG'][i]['start'], s['chapter'].split('  ', 1)[1]))

SOURCES = [
  '면적 6,772㎢·인구 1,400만 명+: VnExpress, 라오동, 사이공타임스(2025)',
  '합병 전 호치민 2,095㎢: B&Company(2025)',
  '서울 인구 934만 명·인구밀도 15,432명/㎢: 통계청 e-나라지표 시도별 인구(2025)',
  '서울 자동차 316만 대: 서울시(2025년 말 등록 대수)',
  '호치민 오토바이 1,130만 대+: 호치민시 건설국(라오동, 2026)',
  '호치민 인구밀도 약 2,070명/㎢: DTiNews(2025)',
  '베트남 한국 동포 19만 2,683명·세계 5위: 재외동포청 「2025 재외동포현황」(2024년 말 기준)',
  '인천→호치민 직항 평균 5시간 34분: KAYAK / 왕복 최저 38만 4,300원: 베트남항공 한국 사이트(조회 시점 기준, 시기별로 다름)',
  '2019년 인구 899만·낀족 852만: citypopulation.de(베트남 인구조사) / 합계출산율 1.39: 베트남 통계총국(GSO)',
  '푸미흥·타오디엔 외국인 거주: Kyoto Review',
  '외국인 주택 소유(한 동 30%, 50년): Viet Nam News / 아파트 한정 개정 논의: The Star(2026.10)',
  '2026년 상반기 신규 분양 79% 옛 빈즈엉: Global Property Guide',
  '메트로 1호선(2024.12, 19.7km·14역), 2호선 벤탄–투티엠 착공(2026.4): VnEconomy, The Investor',
  '롱탄 신공항 2026.12.24 상업 운항 예정: VietnamPlus, The Star(2026.10~11 보도)',
  '남북 고속철도 1,541km·착공 2027.12 연기: DTiNews',
  '롯데 에코스마트시티 투티엠(약 23억 달러, 2026.10 공사 재개): VnExpress, VIR',
  'GS건설 냐베(350ha)·롱빈(91.7ha)·투티엠 사업: 시대일보·스마트투데이(2023), 아시아경제(2025), VietNamNet',
  '삼성전자 HCMC CE 콤플렉스(70ha): VIR, The Investor',
]
desc = f"""호치민은 왜 이런 모양이 됐을까 — 강을 따라 자란 도시 300년 | 도시이야기 1

강 서쪽에서 시작한 도시가 강을 건너 남쪽·동쪽으로, 다시 북쪽으로 주거축을 옮겨 온 이야기. 서울과 같은 축척으로 겹쳐 본 크기, 숫자로 보는 호치민, 사람들이 사는 집, 교통, 한국과의 연결, 한국에서 가는 법까지 담았어요.

[챕터]
""" + '\n'.join(f'{mmss(t)} {n}' for t, n in chap) + """

[숫자 출처]
""" + '\n'.join(f'· {x}' for x in SOURCES) + """

[화면 출처]
· 영상: Pexels (상업 이용 가능 라이선스)
· 위성·3D 화면: Google Earth · 이미지 Airbus (화면에 상시 표기)
· 지도: © OpenStreetMap contributors (ODbL), Natural Earth — 브동산 자체 제작 개략도, 실제 경계·축척과 다를 수 있음
· 음악: 브동산 자체 제작 · 내레이션: AI 음성

※ 공개 자료를 정리한 교육용 콘텐츠이며 특정 단지의 분양·투자를 권유하지 않아요.
브동산 brandongsan.com
#호치민 #베트남 #도시이야기 #호치민부동산 #베트남생활 #브동산
"""
open(D + 'deliver/hcmc-dosi-1-youtube-description.txt', 'w').write(desc)

shorts = {
 'S1': ('호치민은 서울보다 얼마나 클까 | 도시이야기 1', '같은 축척으로 겹쳐 보면, 지금의 호치민은 서울의 약 11배예요. (면적 6,772㎢ vs 605㎢)\n출처: VnExpress·라오동(2025), B&Company, 통계청, DTiNews\n지도: © OpenStreetMap contributors, Natural Earth · 영상: Pexels\n#호치민 #서울 #도시이야기 #Shorts'),
 'S2': ('호치민 사람들은 왜 강을 건넜을까 | 도시이야기 1', '강 서쪽 구도심 → 강 건너 푸미흥·타오디엔 → 투티엠·옛 빈즈엉. 호치민 주거축이 움직인 순서예요.\n출처: VietNamNet, Global Property Guide(2026 상반기)\n지도: © OpenStreetMap contributors, Natural Earth · 영상: Pexels\n※ 분양·투자 권유 아님\n#호치민 #베트남부동산 #도시이야기 #Shorts'),
}
for k, (t, d) in shorts.items():
    open(D + f'deliver/hcmc-dosi-1-shorts-{"size" if k == "S1" else "axis"}-description.txt', 'w').write(t + '\n\n' + d + '\n')

# credits_log.csv
rows = []; n = 0
GEMAP = {'g1_overview.png': 'Google Earth · 이미지 Airbus', 'g2_cbd3d.jpg': 'Google Earth', 'g4_phumyhung_hi.png': 'Google Earth · 이미지 Airbus', 'g5_thuthiem3d.jpg': 'Google Earth'}
for w in ('LONG', 'S1', 'S2'):
    for i, s in enumerate(getattr(S, w)):
        st = tl[w][i]['start']; en = st + tl[w][i]['dur']
        for sh in s['shots']:
            n += 1; tc = f'{w} {mmss(st)}–{mmss(en)}'
            if sh[0] == 'clip':
                rows.append([f'A{n:03d}', f'px_{sh[1]}.mp4', '영상', 'Pexels', f'https://www.pexels.com/video/{sh[1]}/', '', 'Pexels License', TODAY, 'Y', 'N', '', tc, s.get('tag', '')])
            elif sh[0] == 'still':
                fn = sh[1].split('/')[-1]
                rows.append([f'A{n:03d}', fn, '위성·3D 캡처', 'Google Earth', 'https://earth.google.com/', 'Google · 데이터 제공자', 'Google Earth 이용 지침', TODAY, 'Y(교육·비홍보)', 'Y', GEMAP.get(fn, 'Google Earth'), tc, '분양·홍보 맥락 금지, 썸네일 금지'])
            else:
                rows.append([f'A{n:03d}', f'anim:{sh[1]}', '지도·도식(자체 제작)', 'OpenStreetMap / Natural Earth', 'https://www.openstreetmap.org/copyright', 'OSM contributors', 'ODbL / Public Domain', TODAY, 'Y', 'Y', '© OpenStreetMap contributors · Natural Earth', tc, s.get('tag', '')])
rows.append(['B001', 'ne_10m_*.geojson', '지도 데이터', 'Natural Earth', 'https://www.naturalearthdata.com/', '', 'Public Domain', TODAY, 'Y', 'N', '', '전체', ''])
rows.append(['B002', 'seoul.json · hcmc.json · 강', '지도 데이터', 'OpenStreetMap(Nominatim)', 'https://www.openstreetmap.org/copyright', 'OSM contributors', 'ODbL', TODAY, 'Y', 'Y', '© OpenStreetMap contributors', '지도 장면', ''])
rows.append(['B003', 'Pretendard', '글꼴', 'orioncactus/pretendard', 'https://github.com/orioncactus/pretendard', '', 'OFL', TODAY, 'Y', 'N', '', '자막·그래픽', ''])
rows.append(['B004', '내레이션', '음성', 'Microsoft Edge 읽기 음성(edge-tts, ko-KR-SunHiNeural, 속도 -10%·톤 +3Hz)', '', '', '확인 필요', TODAY, '확인 필요', 'N', 'AI 음성', '전체', '상업 이용 조건을 따로 확인할 것'])
rows.append(['B005', '배경음악·효과음', '음악', '브동산 자체 합성', '', '', '자체 제작', TODAY, 'Y', 'N', '', '전체', ''])
with open(D + 'deliver/credits_log.csv', 'w', newline='', encoding='utf-8-sig') as f:
    wr = csv.writer(f); wr.writerow(['asset_id', '파일명', '유형', '소스', 'URL', '작가', '라이선스', '확인일', '상업OK', '표기필요', '표기문구', '타임코드', '비고']); wr.writerows(rows)
print(desc[:900])
