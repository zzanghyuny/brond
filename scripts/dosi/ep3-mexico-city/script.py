# -*- coding: utf-8 -*-
"""도시이야기 3편 — 멕시코시티는 왜 가라앉을까. 가로 본편(LONG, A안) + 쇼츠 2편(S1 호수, S2 침하, B안).
shot: ('clip', pexels_id, start) | ('anim', name, {opts})
line: (자막, 읽을 문장 또는 None)  — 숫자는 읽을 문장에서 한글로 푼다.
2026.11.28 다시 제작: 나레이션 약 1.2배(lib 기본값), 구글 어스 장면 추가(('ge', 캡처, 시작배율, 끝배율, 가로이동, 세로이동)).
오프닝 순서(2026.11.27 확정): 제목+실사 → 서울과 면적 비교 → 숫자로 보는 도시 → 나머지 꼭지.
실사 없는 장면은 짧게(면적 비교 8초 안팎, 숫자 12초 안쪽, 그 밖의 그래픽 12초 이하).
"""
EP = dict(
    no=3, city='멕시코시티', slug='mexico-city', key='mx',
    title='멕시코시티는 왜 가라앉을까', subtitle='호수를 메워 세운 도시 700년',
    yt_title='멕시코시티는 왜 가라앉을까 — 호수를 메워 세운 도시 700년 | 도시이야기 3',
    shorts={'S1': ('멕시코시티는 왜', '호수 위에 세워졌을까'), 'S2': ('멕시코시티는 왜', '해마다 가라앉을까')},
    shorts_title={'S1': '멕시코시티는 왜 호수 위에 세워졌을까 | 도시이야기', 'S2': '멕시코시티는 왜 해마다 가라앉을까 | 도시이야기'},
    px='/home/claude/media/pexels_mx/', geo='/home/claude/brond/scripts/dosi/ep3-mexico-city/geo.json',
    work='/home/claude/work/ep3/', center=(-99.133, 19.433),
    minimap_bounds=(-99.31, 19.23, -98.97, 19.52), minimap_layers=['a_cuauhtemoc'], minimap_rivers=[],
    names={'LONG': 'mexico-city-dosi-3-youtube', 'S1': 'mexico-city-dosi-3-shorts-lake', 'S2': 'mexico-city-dosi-3-shorts-sinking'},
    credits_map='지도  © OpenStreetMap contributors · Natural Earth', credits_ge='위성·3D 화면  Google Earth', ge_attrib='Google Earth',
    site_url='https://www.brandongsan.com/posts/mexico-city-city-structure.html',
    yt_intro='1325년 텍스코코 호수 위 작은 섬에 세운 테노치티틀란. 스페인이 그 폐허 위에 새 수도를 짓고 호수의 물을 빼면서, 멕시코시티는 옛 호수 바닥 진흙 위에 선 도시가 됐어요. 빠른 곳은 해마다 50cm까지 가라앉는 이유, 주거 중심이 센트로에서 로마·폴랑코, 산타페로 옮겨 간 순서, 1905년 제물포에서 떠난 한인 이민, 한국에서 가는 법까지 지도와 실사로 정리했어요.',
    shorts_desc={'S1': '멕시코 국기의 독수리는 도시가 태어난 이야기예요. 아스테카 사람들은 1325년 텍스코코 호수 위 작은 섬에 테노치티틀란을 세웠고, 물 위에 흙을 쌓은 밭(치남파)으로 도시를 넓혔어요. 남쪽 소치밀코에는 그 물길이 지금도 남아 있어요.\n출처: UNAM Global(2025), 멕시코 데스코노시도, INAH(소치밀코 · 유네스코 세계유산)',
                 'S2': '1910년에 세운 멕시코시티 독립기념탑(천사상)은 주변 땅이 꺼지면서 받침에 계단 14개를 더 붙였어요. 옛 호수 바닥 진흙층에서 지하수를 퍼 올리면서 빠른 곳은 연 50cm까지 가라앉아요.\n출처: NASA JPL(2026.4), Scientific Reports(2024)'},
    thumbs=dict(LONG=dict(clip='11690475', t=6, cx=0.45, lines=['멕시코시티는', '왜 땅이', '가라앉을까'], sub='호수를 메워 세운 도시 ', accent='700년'),
                S1=dict(kind='photo', clip='32058674', t=4, cx=0.5, cy=0.45, big='1325년', small='호수 위 작은 섬에 세운 도시'),
                S2=dict(kind='photo', clip='35614829', t=8, cx=0.5, cy=0.45, big='+14계단', small='땅이 꺼지며 늘어난 천사상 계단')),
)
GE = '/home/claude/media/gearth_mx/'
GEA = 'Google Earth · 2013 이미지'
OSM = '© OpenStreetMap contributors · Natural Earth'
SELF = '브동산 자체 제작 개략도 · 실제 경계·축척과 다를 수 있음'
ALC = ['a_alvaro_obregon', 'a_azcapotzalco', 'a_benito_juarez', 'a_coyoacan', 'a_cuajimalpa', 'a_cuauhtemoc', 'a_gam', 'a_iztacalco', 'a_iztapalapa',
       'a_magdalena', 'a_miguel_hidalgo', 'a_tlahuac', 'a_tlalpan', 'a_vcarranza', 'a_xochimilco']
HAIR = [dict(g=k, color='hair', width=1.2, at=0) for k in ALC]
CDMX_LINE = dict(g='cdmx', color='soft', width=1.8, alpha=0.7, at=0)

def lake_map(short=False):
    return ('anim', 'map', dict(bounds=(-99.22, 19.33, -99.0, 19.505), layers=HAIR + [CDMX_LINE] + [
        dict(g=k, color='brass', width=4, at=1, d=0.2 + 0.25 * i, dash=(10, 8)) for i, k in enumerate(('c_tepeyac', 'c_tacuba', 'c_iztapalapa'))],
        zones=[dict(p='templo_mayor', rkm=1.6, label='테노치티틀란', off=(2.3, 0.15), at=0, color='brass')],
        markers=[dict(p='tlatelolco', label='틀라텔롤코', at=0, d=0.4, off=(-1, 0), anchor='rm', color='soft', lcolor='soft'),
                 dict(p='tepeyac', label='테페약', at=1, d=0.3, off=(1, 0), color='ink'), dict(p='tacuba', label='타쿠바', at=1, d=0.55, off=(-1, 0), anchor='rm', color='ink'),
                 dict(p='iztapalapa_c', label='이스타팔라파', at=1, d=0.8, off=(1, 0), color='ink')],
        texts=[dict(s='옛 텍스코코 호수', p=(-99.05, 19.475), at=0, size=34, color='soft', alpha=0.9), dict(s='(지금은 대부분 시가지)', p=(-99.05, 19.458), at=0, size=24, color='faint')],
        side=None if short else dict(title=('테노치티틀란', 0), big=('1325', 0), sub=('호수 위 작은 섬에 세운 도시', 0), sub2=('둑길(점선)은 개략 위치', 1))))

def sink_map(short=False):
    return ('anim', 'map', dict(bounds=(-99.24, 19.22, -98.86, 19.52), layers=HAIR + [CDMX_LINE],
        zones=[dict(p='aicm', rkm=2.6, label='공항 주변', off=(0, -1), at=0 if short else 1, color='brass'),
               dict(p='chalco', rkm=3.0, label='찰코', off=(0, 1), at=0 if short else 1, d=0.3, color='brass')],
        markers=[dict(p='angel', label='천사상', at=0, off=(-1, 0), anchor='rm'), dict(p='zocalo', label='소칼로', at=0, d=0.3, off=(1, 0.9))],
        side=None if short else dict(title=('빠른 곳은', 0), big=('연 50cm', 0), sub=('위성 관측 최대치(2024 논문)', 0), sub2=('공항 주변 한 달 2cm 넘게(NISAR, 2025.10~2026.1)', 1))))

def axis(stage):
    lay = HAIR + [CDMX_LINE]
    zn, mk = [], []
    c1 = 'brass' if stage == 1 else 'soft'
    zn.append(dict(p='zocalo', rkm=1.1, label='센트로', off=(0, -1), at=0, color=c1))
    if stage >= 2:
        c2 = 'brass' if stage == 2 else 'soft'
        zn += [dict(p='roma', rkm=0.75, label='로마 1902', off=(0.3, 1.1), at=0 if stage > 2 else 1, color=c2),
               dict(p='condesa', rkm=0.65, label='콘데사', off=(-1.6, 0.2), at=0 if stage > 2 else 1, d=0.2, color=c2),
               dict(p='polanco', rkm=0.9, label='폴랑코 1937', off=(0, -1), at=0 if stage > 2 else 1, d=0.4, color=c2)]
    if stage == 3:
        zn += [dict(p='santafe', rkm=1.5, label='산타페', off=(0, -1), at=1, color='brass')]
    mk += [dict(p='angel', label='천사상', at=0, off=(1, 0), color='ink')] if stage >= 2 else []
    stg = {1: ('①', '옛 섬 자리, 센트로', '~1900년'), 2: ('②', '서쪽 새 동네 로마·폴랑코', '1902년~'), 3: ('③', '서쪽 언덕 산타페', '1980년대~')}[stage]
    bnd = {1: (-99.205, 19.385, -99.075, 19.47), 2: (-99.235, 19.37, -99.1, 19.465), 3: (-99.31, 19.33, -99.1, 19.47)}[stage]
    return ('anim', 'map', dict(bounds=bnd, layers=lay, zones=zn, markers=mk, stage=stg))

LONG = [
  # ── Ⅰ 오프닝: 제목 + 실사 → 서울과 면적 비교
  dict(chap='Ⅰ   오프닝', loc=(-99.13, 19.43), title=True, shots=[('clip', '35691533', 0)], lines=[
    ('해발 2,240m, 산과 화산에 둘러싸인 분지에 멕시코시티가 있어요.', '해발 이천이백사십 미터, 산과 화산에 둘러싸인 분지에 멕시코시티가 있어요.'),
    ('그런데 이 도시는 해마다 조금씩 가라앉고 있어요. 왜일까요?', None)]),
  dict(chap='Ⅰ   오프닝', attrib=GEA, loc=(-99.10, 19.42), shots=[('ge', GE + 'g1_valley.jpg', 1.0, 1.2, 0.0, 0.0)], lines=[
    ('위에서 보면 산 사이 평평한 바닥을 도시가 가득 채우고 있어요.', None)]),
  dict(chap='Ⅰ   오프닝', chapter='01  멕시코시티는 얼마나 클까', attrib=OSM, note=SELF, shots=[('anim', 'overlay', dict(
      city='cdmx', compare=None, city_label='멕시코시티', city_label_at=(-99.02, 19.57), seoul_at=(-99.13, 19.34),
      side=dict(title=('멕시코시티 면적', 0), big=('1,494㎢', 0), sub=('서울의 약 2.5배', 0), sub2=('알카디아(구) 16곳', 0))))], lines=[
    ('멕시코시티는 1,494㎢, 서울의 2.5배쯤이에요.', '멕시코시티는 천사백구십사 제곱킬로미터, 서울의 두 배 반쯤이에요.')]),
  # ── Ⅱ 숫자로 보는 멕시코시티
  dict(chap='Ⅱ   숫자로 보는 멕시코시티', chapter='02  숫자로 보는 멕시코시티', shots=[('anim', 'numbers', dict(title='숫자로 보는 멕시코시티', head=('멕시코시티', '서울'), rows=[
      ('면적', '1,494㎢', '605㎢', True), ('인구(2025)', '922만 명', '934만 명', False), ('광역권 인구(2020)', '2,140만 명', '', False),
      ('해발 고도', '2,240m', '', False), ('구', '알카디아 16곳', '자치구 25곳', False), ('인천에서', '직항 약 14시간 · 시차 15시간', '', False)],
      src='출처: INEGI 2025 인구조사·2020 센서스 · 메트로폴리스 데 멕시코 2020 · 멕시코시티 관광청 · 통계청(2025) · 항공편 조회(2026.11)'))], lines=[
    ('인구는 922만 명으로 서울과 비슷한데, 주변 도시까지 합치면 2,100만 명이 넘어요.', '인구는 구백이십이만 명으로 서울과 비슷한데, 주변 도시까지 합치면 이천백만 명이 넘어요.')]),
  # ── Ⅲ 호수 위의 섬 도시
  dict(chap='Ⅲ   호수 위의 섬 도시', chapter='03  호수 위의 섬 도시', loc='zocalo', shots=[('clip', '4044986', 2)], lines=[
    ('도시 한가운데, 소칼로 광장이에요.', None),
    ('7백 년 전 이곳은 텍스코코 호수 위의 작은 섬이었어요.', '칠백 년 전 이곳은 텍스코코 호수 위의 작은 섬이었어요.')]),
  dict(chap='Ⅲ   호수 위의 섬 도시', attrib=GEA, loc='zocalo', shots=[('ge', GE + 'g2_centro3d.jpg', 1.0, 1.15, 0.0, 0.0)], lines=[
    ('지금은 빈틈없이 건물이 들어찬 구시가지 한가운데예요.', None)]),
  dict(chap='Ⅲ   호수 위의 섬 도시', attrib=OSM, note=SELF, shots=[lake_map()], lines=[
    ('아스테카 사람들은 1325년, 이 섬에 테노치티틀란을 세웠어요.', '아스테카 사람들은 천삼백이십오년, 이 섬에 테노치티틀란을 세웠어요.'),
    ('섬에서 둑길을 놓아 호숫가와 이었어요.', None)]),
  dict(chap='Ⅲ   호수 위의 섬 도시', loc='tepeyac', shots=[('clip', '34795249', 1)], lines=[
    ('북쪽 둑길이 닿던 테페약 언덕에는 지금 과달루페 성모 대성당이 서 있어요.', None)]),
  dict(chap='Ⅲ   호수 위의 섬 도시', loc='xochimilco_c', shots=[('clip', '40140926', 2), ('clip', '31986191', 6)], lines=[
    ('물 위에 흙을 쌓아 밭을 만들었는데, 이걸 치남파라고 해요.', None),
    ('남쪽 소치밀코에는 그 물길과 밭이 지금도 남아 있어요.', None)]),
  dict(chap='Ⅲ   호수 위의 섬 도시', loc='cathedral', shots=[('clip', '3562640', 0)], caption=dict(line=0, t1='1521', t2='테노치티틀란 함락'), lines=[
    ('1521년, 스페인군이 이 도시를 무너뜨렸어요.', '천오백이십일년, 스페인군이 이 도시를 무너뜨렸어요.'),
    ('그리고 그 폐허 위에 새 수도를 짓고, 호수의 물을 빼기 시작했어요.', None)]),
  dict(chap='Ⅲ   호수 위의 섬 도시', loc=(-99.165, 19.43), shots=[('clip', '28730770', 1)], caption=dict(line=1, t1='1900', t2='대운하 개통 · 47.5km'), lines=[
    ('호숫가 도시라 홍수가 잦았어요. 1607년엔 첫 배수로를 팠고,', '호숫가 도시라 홍수가 잦았어요. 천육백칠년엔 첫 배수로를 팠고,'),
    ('1900년엔 47.5km 대운하를 열었어요.', '천구백년엔 사십칠 점 오 킬로미터 대운하를 열었어요.')]),
  dict(chap='Ⅲ   호수 위의 섬 도시', loc=None, attrib=GEA, shots=[('ge', GE + 'g1_valley.jpg', 1.25, 1.45, 0.1, 0.0)], lines=[
    ('그렇게 호수는 거의 다 말라 사라졌고, 그 바닥 위로 시가지가 퍼졌어요.', None)]),
  # ── Ⅳ 가라앉는 도시
  dict(chap='Ⅳ   가라앉는 도시', chapter='04  가라앉는 도시', loc='angel', shots=[('clip', '13638459', 0)], caption=dict(line=1, t1='+14계단', t2='독립기념탑 · 1910년 이후'), lines=[
    ('1910년에 세운 독립기념탑, 천사상이에요.', '천구백십년에 세운 독립기념탑, 천사상이에요.'),
    ('주변 땅이 내려앉으면서 받침에 계단을 14개나 더 붙였어요.', '주변 땅이 내려앉으면서 받침에 계단을 열네 개나 더 붙였어요.')]),
  dict(chap='Ⅳ   가라앉는 도시', loc='angel', shots=[('clip', '15809156', 2)], lines=[
    ('도시 아래는 옛 호수 바닥의 무른 진흙층이에요.', None),
    ('여기서 지하수를 퍼 올리자 진흙이 눌리면서 땅이 꺼지기 시작했어요.', None)]),
  dict(chap='Ⅳ   가라앉는 도시', attrib=OSM, note=SELF, shots=[sink_map()], lines=[
    ('빠른 곳은 1년에 50cm까지 내려앉아요.', '빠른 곳은 일 년에 오십 센티미터까지 내려앉아요.'),
    ('나사 위성은 공항 주변이 한 달에 2cm 넘게 꺼지는 걸 잡아냈어요.', '나사 위성은 공항 주변이 한 달에 이 센티미터 넘게 꺼지는 걸 잡아냈어요.')]),
  dict(chap='Ⅳ   가라앉는 도시', attrib=GEA, loc='aicm', shots=[('ge', GE + 'g7_aicm.jpg', 1.0, 1.18, 0.0, 0.0)], lines=[
    ('옛 호수 바닥 한복판에 놓인 공항 주변이 가장 빨리 꺼지는 곳 중 하나예요.', None)]),
  dict(chap='Ⅳ   가라앉는 도시', loc=None, shots=[('clip', '30056250', 4)], lines=[
    ('그래도 펌프를 멈추기는 어려워요. 수돗물 절반 이상을 땅속 우물에서 뽑아 쓰거든요.', None)]),
  dict(chap='Ⅳ   가라앉는 도시', loc=(-99.135, 19.35), shots=[('clip', '27053435', 8)], lines=[
    ('땅이 꺼지면서 길과 건물, 수도관이 갈라지고 지하철도 피해를 입어요.', None)]),
  # ── Ⅴ 주거축 이동 3단계
  dict(chap='Ⅴ   주거축 이동 3단계', chapter='05  주거축 이동 3단계', attrib=OSM, note=SELF, shots=[axis(1)], lines=[
    ('사람들이 사는 중심도 옮겨 갔어요. 처음은 옛 섬 자리, 지금의 센트로예요.', None)]),
  dict(chap='Ⅴ   주거축 이동 3단계', loc='zocalo', shots=[('clip', '30138329', 3)], lines=[
    ('스페인 시대부터 쌓인 건물이 빽빽한 구시가지예요.', None)]),
  dict(chap='Ⅴ   주거축 이동 3단계', attrib=OSM, note=SELF, shots=[axis(2)], lines=[
    ('1902년엔 서쪽에 상하수도를 처음 갖춘 로마 지구가 생겼어요.', '천구백이년엔 서쪽에 상하수도를 처음 갖춘 로마 지구가 생겼어요.'),
    ('1937년엔 더 서쪽, 폴랑코가 개발됐어요.', '천구백삼십칠년엔 더 서쪽, 폴랑코가 개발됐어요.')]),
  dict(chap='Ⅴ   주거축 이동 3단계', loc='roma', attrib=GEA, shots=[('ge', GE + 'g3_roma3d.jpg', 1.0, 1.15, 0.0, 0.0)], caption=dict(line=0, t1='472채', t2='1985년 지진 · 로마 지구'), lines=[
    ('1985년 대지진 때는 로마 지구에서만 건물 472채가 무너지거나 부서졌어요.', '천구백팔십오년 대지진 때는 로마 지구에서만 건물 사백칠십이 채가 무너지거나 부서졌어요.')]),
  dict(chap='Ⅴ   주거축 이동 3단계', loc='polanco', shots=[('clip', '12943393', 2)], lines=[
    ('폴랑코는 지금 고급 상점과 빌딩이 늘어선 동네가 됐어요.', None)]),
  dict(chap='Ⅴ   주거축 이동 3단계', attrib=OSM, note=SELF, shots=[axis(3)], lines=[
    ('세 번째는 서쪽 언덕의 산타페예요.', None),
    ('모래 채굴장과 쓰레기 매립지였던 땅이 1980년대부터 업무지구로 바뀌었어요.', '모래 채굴장과 쓰레기 매립지였던 땅이 천구백팔십년대부터 업무지구로 바뀌었어요.')]),
  dict(chap='Ⅴ   주거축 이동 3단계', attrib=GEA, loc='santafe', shots=[('ge', GE + 'g4_santafe3d.jpg', 1.0, 1.15, 0.0, 0.0)], lines=[
    ('위에서 보면 골짜기 사이 언덕에 빌딩이 모여 있어요.', None)]),
  dict(chap='Ⅴ   주거축 이동 3단계', loc='santafe', shots=[('clip', '28833289', 2)], lines=[
    ('지금은 고층 빌딩과 대형 쇼핑몰, 대학이 모인 신도심이에요.', None)]),
  # ── Ⅵ 사는 집
  dict(chap='Ⅵ   멕시코시티 사람들이 사는 집', chapter='06  멕시코시티 사람들이 사는 집', loc='tlatelolco_u', shots=[('clip', '38659251', 0)], lines=[
    ('1960년대 정부는 거대한 아파트 단지를 지었어요. 틀라텔롤코예요.', '천구백육십년대 정부는 거대한 아파트 단지를 지었어요. 틀라텔롤코예요.')]),
  dict(chap='Ⅵ   멕시코시티 사람들이 사는 집', loc='tlatelolco_u', attrib=GEA, shots=[('ge', GE + 'g6_tlatelolco3d.jpg', 1.0, 1.12, 0.0, 0.0)], caption=dict(line=0, t1='102동', t2='틀라텔롤코 · 1960~1965년'), lines=[
    ('처음엔 아파트가 102동, 멕시코에서 가장 큰 단지였어요.', '처음엔 아파트가 백두 동, 멕시코에서 가장 큰 단지였어요.')]),
  dict(chap='Ⅵ   멕시코시티 사람들이 사는 집', loc='xochimilco_c', attrib=GEA, shots=[('ge', GE + 'g5_xochimilco.jpg', 1.0, 1.2, 0.0, 0.0)], lines=[
    ('도시 바깥쪽으로는 낮은 집이 끝없이 이어져요.', None)]),
  dict(chap='Ⅵ   멕시코시티 사람들이 사는 집', loc=None, shots=[('clip', '37796402', 0)], lines=[
    ('2020년 멕시코시티의 집은 276만 채, 한 집에 3.3명꼴로 살아요.', '이천이십년 멕시코시티의 집은 이백칠십육만 채, 한 집에 삼 점 삼 명꼴로 살아요.')]),
  # ── Ⅶ 사람들
  dict(chap='Ⅶ   멕시코시티 사람들', chapter='07  멕시코시티 사람들', loc='zocalo', shots=[('clip', '30138330', 2)], lines=[
    ('가장 많이 사는 구는 동쪽 이스타팔라파, 188만 명이에요.', '가장 많이 사는 구는 동쪽 이스타팔라파, 백팔십팔만 명이에요.'),
    ('시민 다섯 명 중 한 명이 이 구에 살아요.', None)]),
  dict(chap='Ⅶ   멕시코시티 사람들', loc='zocalo', shots=[('clip', '30138479', 4)], lines=[
    ('구시가지 골목에는 시장과 노점이 줄지어 있어요.', None),
    ('망자의 날 무렵이면 거리가 종이 장식과 꽃으로 물들어요.', None)]),
  # ── Ⅷ 교통 인프라
  dict(chap='Ⅷ   교통 인프라', chapter='08  교통 인프라', loc=None, shots=[('clip', '39928082', 0)], caption=dict(line=1, t1='450만 명', t2='지하철 하루 승객'), lines=[
    ('지하철은 1969년에 처음 달렸어요.', '지하철은 천구백육십구년에 처음 달렸어요.'),
    ('지금은 12개 노선, 195개 역에 하루 450만 명이 타요.', '지금은 열두 개 노선, 백구십오 개 역에 하루 사백오십만 명이 타요.')]),
  dict(chap='Ⅷ   교통 인프라', shots=[('anim', 'card', dict(title='멕시코시티의 길', items=[('226.5km', '지하철 12개 노선', 0), ('195개', '지하철역', 0), ('10.55km', '카블레부스 2호선 · 기네스', 0), ('2021', '케이블카 버스 첫 개통', 0)],
      src='출처: 크로니카(2026.9) · 포브스 멕시코(2021.8)'))], lines=[
    ('언덕 동네엔 케이블카 버스, 카블레부스를 놓았어요.', None),
    ('2호선 10.55km는 세계에서 가장 긴 도시 케이블카로 기네스에 올랐어요.', '이호선 십 점 오오 킬로미터는 세계에서 가장 긴 도시 케이블카로 기네스에 올랐어요.')]),
  dict(chap='Ⅷ   교통 인프라', loc=None, shots=[('clip', '39665647', 0)], lines=[
    ('2024년엔 차풀테펙 숲을 건너는 3호선도 열려, 첫해에만 600만 명 가까이 탔어요.', '이천이십사년엔 차풀테펙 숲을 건너는 삼호선도 열려, 첫해에만 육백만 명 가까이 탔어요.')]),
  dict(chap='Ⅷ   교통 인프라', loc='angel', shots=[('clip', '31986210', 4)], lines=[
    ('도심은 레포르마 대로가 비스듬히 가로질러요. 천사상도 이 길 위에 있어요.', None)]),
  # ── Ⅸ 한국과의 연결
  dict(chap='Ⅸ   한국과의 연결', chapter='09  한국과의 연결', attrib=OSM, note=SELF, shots=[('anim', 'route', dict(bounds=(118.0, 6.0, 276.0, 46.0), span=3.6, start_at=1,
      stops=[('icn', '제물포', '1905.4'), ('salina_cruz360', '살리나크루스', '1905.5'), ('merida360', '유카탄 메리다', '')],
      offsets={'제물포': (1, -0.9), '살리나크루스': (-1, 0.9), '유카탄 메리다': (-1, -1.0)},
      side=dict(title=('첫 한인 이민', 0), big=('1,033명', 1), sub=('1905년 제물포 → 유카탄', 1), sub2=('에네켄(용설란) 농장 계약 노동', 1))))], lines=[
    ('멕시코는 한국과 오랜 인연이 있어요.', None),
    ('1905년 제물포에서 배를 탄 1,033명이 유카탄의 에네켄 농장으로 갔어요.', '천구백오년 제물포에서 배를 탄 천삼십삼 명이 유카탄의 에네켄 농장으로 갔어요.')]),
  dict(chap='Ⅸ   한국과의 연결', loc='zonarosa', shots=[('clip', '36385590', 2)], caption=dict(line=0, t1='3만 명+', t2='멕시코의 한인 이민 후손 · 2025'), lines=[
    ('지금 그 후손은 멕시코에 3만 명이 넘어요.', '지금 그 후손은 멕시코에 삼만 명이 넘어요.'),
    ('천사상 옆 소나 로사에는 한국 가게가 모인 작은 서울, 페케뇨 세울이 있어요.', None)]),
  # ── Ⅹ 한국에서 가는 법
  dict(chap='Ⅹ   한국에서 가는 법', chapter='10  한국에서 가는 법', attrib=OSM, note=SELF, shots=[('anim', 'flight', dict(bounds=(118.0, 10.0, 272.0, 50.0), dest='aicm360', dest_label='멕시코시티 공항',
      side=dict(title=('인천 → 멕시코시티', 0), big=('약 14시간', 0), sub=('직항 · 오는 편은 몬테레이 경유 약 19시간', 1), sub2=('시차 15시간(한국이 빠름)', 1))))], lines=[
    ('인천에서 멕시코시티까지는 직항으로 14시간쯤 걸려요.', '인천에서 멕시코시티까지는 직항으로 열네 시간쯤 걸려요.'),
    ('돌아오는 편은 몬테레이를 거쳐 19시간쯤, 시차는 15시간이에요.', '돌아오는 편은 몬테레이를 거쳐 열아홉 시간쯤, 시차는 열다섯 시간이에요.')]),
  dict(chap='Ⅹ   한국에서 가는 법', loc=(-99.17, 19.42), end=True, shots=[('clip', '11690475', 0)], lines=[
    ('한국 여권이면 비자 없이 최대 180일 머물 수 있어요.', '한국 여권이면 비자 없이 최대 백팔십 일 머물 수 있어요.'),
    ('호수 위 섬에서 시작해 지금도 가라앉고 있는 도시, 멕시코시티였어요.', None)]),
]

# ───────── 쇼츠 (B안 리얼 생생, 1080×1920). hl = 자막에서 황동색으로 칠할 말
S1 = [
  dict(tag='소칼로 광장', loc='zocalo', shots=[('clip', '32622096', 1)], lines=[('멕시코 국기 속 이 독수리, 도시가 태어난 이야기예요.', None, '독수리')]),
  dict(tag='소칼로 · 대형 국기', loc='zocalo', shots=[('clip', '32058674', 2)], lines=[
      ('선인장 위에서 뱀을 먹는 독수리가 보이면 거기 도시를 세우라는 계시였죠.', None, '독수리')]),
  dict(tag='테노치티틀란 · 개략도', attrib=OSM, shots=[lake_map(short=True)], lines=[
      ('그 독수리를 찾은 곳이 텍스코코 호수 위의 작은 섬이었어요.', None, '작은 섬'), ('1325년, 테노치티틀란이에요.', '천삼백이십오년, 테노치티틀란이에요.', '1325년')]),
  dict(tag='위에서 본 소치밀코', attrib=GEA, loc='xochimilco_c', shots=[('ge', GE + 'g5_xochimilco.jpg', 1.0, 1.25, 0.2, 0.0)], lines=[('위에서 보면 지금도 물길이 마을 사이를 지나요.', None, '물길')]),
  dict(tag='소치밀코 운하', loc='xochimilco_c', shots=[('clip', '34464113', 3)], sticker=dict(line=0, delay=0.8, t1='치남파', t2='물 위에 흙을 쌓은 밭'), lines=[
      ('사람들은 물 위에 흙을 쌓아 밭을 만들며 도시를 넓혔어요.', None, '물 위에 흙')]),
  dict(tag='소치밀코', loc='xochimilco_c', shots=[('clip', '34567570', 2)], lines=[('남쪽 소치밀코엔 그 물길이 지금도 남아 있어요.', None, '지금도')]),
  dict(tag='멕시코시티 도심', loc=None, shots=[('clip', '31014956', 3)], bubble=dict(line=0, t1='922만 명', t2='2025년 인구'), lines=[
      ('호수는 거의 다 메워지고, 그 위에 922만 명이 사는 도시가 섰어요.', '호수는 거의 다 메워지고, 그 위에 구백이십이만 명이 사는 도시가 섰어요.', '922만 명')]),
  dict(tag='비 오는 거리', loc=None, end=True, shots=[('clip', '28730771', 1)], lines=[('그래서 이 도시는 지금도 물과 씨름해요. 이야기는 본편에서 이어져요.', None, '물과 씨름')]),
]
S2 = [
  dict(tag='독립기념탑 · 레포르마', loc='angel', shots=[('clip', '35614829', 2)], lines=[('이 천사상, 계단이 14개나 늘어났어요.', '이 천사상, 계단이 열네 개나 늘어났어요.', '14개')]),
  dict(tag='독립기념탑', loc='angel', shots=[('clip', '31088330', 4)], sticker=dict(line=0, delay=1.0, t1='+14계단', t2='1910년 완공 이후'), lines=[
      ('1910년에 세운 뒤 주변 땅이 꺼지면서 계단을 덧붙였거든요.', '천구백십년에 세운 뒤 주변 땅이 꺼지면서 계단을 덧붙였거든요.', '땅이 꺼지면서')]),
  dict(tag='가라앉는 곳 · 개략도', attrib=OSM, shots=[sink_map(short=True)], lines=[('멕시코시티는 빠른 곳이 1년에 50cm까지 가라앉아요.', '멕시코시티는 빠른 곳이 일 년에 오십 센티미터까지 가라앉아요.', '50cm')]),
  dict(tag='메트로폴리탄 대성당', loc='cathedral', shots=[('clip', '32622092', 2)], lines=[
      ('도시가 옛 호수 바닥 진흙 위에 서 있는데,', None, '진흙'), ('땅속 물을 계속 퍼 올리자 진흙이 눌려 꺼지는 거예요.', None, '땅속 물')]),
  dict(tag='멕시코시티 하늘', loc=None, shots=[('clip', '13580874', 2)], lines=[('그런데 펌프를 멈추기도 어려워요. 수돗물 절반 이상이 땅속 우물에서 나오거든요.', None, '절반 이상')]),
  dict(tag='멕시코시티 지하철', loc=None, shots=[('clip', '39883705', 1)], lines=[('땅이 꺼지면서 길과 건물, 지하철까지 피해를 입고 있어요.', None, '지하철까지')]),
  dict(tag='멕시코시티 상공', loc='aicm', attrib=GEA, shots=[('ge', GE + 'g7_aicm.jpg', 1.0, 1.25, 0.0, 0.0)], bubble=dict(line=0, t1='한 달 2cm+', t2='NISAR 위성 · 공항 주변'), lines=[
      ('나사 위성은 공항 주변이 한 달에 2cm 넘게 꺼지는 걸 잡았어요.', '나사 위성은 공항 주변이 한 달에 이 센티미터 넘게 꺼지는 걸 잡았어요.', '2cm')]),
  dict(tag='레포르마의 밤', loc='angel', end=True, shots=[('clip', '34381882', 1)], lines=[('호수 위에 세운 도시의 이야기, 본편에서 이어 볼게요.', None, '호수 위')]),
]

# 설명란·글에 쓰는 숫자 출처
SOURCES = [
    ('INEGI, 「Encuesta Intercensal 2025 — Ciudad de México」(기준일 2025.10.15) — 인구 9,216,407명, 이스타팔라파 1,877,417명(20.48%)', 'https://www.inegi.org.mx/contenidos/programas/eic/2025/doc/eic2025_presentacion_09.pdf'),
    ('INEGI, 「Censo de Población y Vivienda 2020 — Ciudad de México」(2021.1.29) — 9,209,944명, 1㎢당 6,163.3명(→ 면적 약 1,494㎢), 16개 알카디아, 주택 2,756,319채·한 집 3.3명', 'https://www.inegi.org.mx/contenidos/saladeprensa/boletines/2021/EstSociodemo/ResultCenso2020_CdMx.pdf'),
    ('멕시코시티 관광청, About Mexico City — 해발 2,240m, 1325년 텍스코코 호수 섬에 건설, 1521년 포위전으로 파괴', 'https://mexicocity.cdmx.gob.mx/e/about/about-mexico-city'),
    ('Xataka México(2026.8.28), Metrópolis de México 2020 인용 — 광역권 인구 2,140만 명(2020)', 'https://www.xataka.com.mx/otros-1/valle-mexico-no-termina-donde-creiamos-zona-metropolitana-ahora-incluye-84-municipios-alcaldias'),
    ('UNAM Global(2025.3.12) — 테노치티틀란 건설 1325년(2-가옥의 해)', 'https://unamglobal.unam.mx/global_revista/como-sabemos-que-tenochtitlan-fue-fundada-en-1325-la-unam-responde/'),
    ('México Desconocido, 「México-Tenochtitlan」 — 독수리 계시, 둑길(테페약·타쿠바·이스타팔라파), 1521년 8월 13일 함락', 'https://www.mexicodesconocido.com.mx/mexico-tenochtitlan.html'),
    ('México Desconocido, 「테노치티틀란 건설 700년」 — 치남파', 'https://www.mexicodesconocido.com.mx/historia-de-la-fundacion-de-tenochtitlan.html'),
    ('El Imparcial(2024.9.19) — 독수리·선인장·뱀 문양이 국기에', 'https://www.elimparcial.com/locurioso/2024/09/19/que-representa-el-aguila-en-la-bandera-de-mexico'),
    ('INAH, Xochimilco(유네스코 세계유산 1987) — 스페인이 테노치티틀란 폐허 위에 수도 건설·호수 배수 시작, 소치밀코 치남파는 옛 호수 풍경의 흔적', 'https://lugares.inah.gob.mx/en/node/6116'),
    ('Britannica, Mexico City: Landscape — 섬은 텍스코코 호수 서쪽 기슭, 배수로 분지의 호수 물이 거의 다 빠짐', 'https://www.britannica.com/place/Mexico-City/Landscape'),
    ('EBSCO Research Starters, 「Draining of Lake Texcoco」 — 1607년 11월 28일 배수로 착공, 1629년 대홍수', 'https://ebsco.com/research-starters/history/draining-lake-texcoco'),
    ('UNAM Internacional(2026.5.12) — 대운하(Gran Canal del Desagüe) 1900년 개통, 첫 구간 47.5km', 'https://revista.unaminternacional.unam.mx/en/nota/12/cuando-los-rios-se-volvieron-drenaje-saneamiento-desague-y-la-creacion-de-la-ciudad-moderna'),
    ('NASA JPL(2026.4.29) — NISAR 위성 2025.10~2026.1 관측, 공항 주변 한 달 2cm 넘는 침하, 독립기념탑(1910) 계단 14개 추가', 'https://www.jpl.nasa.gov/news/us-indian-space-mission-maps-extreme-subsidence-in-mexico-city/'),
    ('Solano-Rojas 외, Scientific Reports 14:6035(2024.3.12) — 침하 속도 최대 연 500mm, 지하수 과다 추출, 지하철 피해', 'https://www.nature.com/articles/s41598-024-53525-y'),
    ('Meteored(2024.2.21, Conagua 인용) — 우물 약 67%, 쿠차말라 32%', 'https://www.meteored.mx/noticias/actualidad/el-sistema-cutzamala-no-es-la-unica-fuente-de-abasto-de-agua-de-la-ciudad-de-mexico-conagua-sequia.html'),
    ('N+(2025.4.30, UNAM 인용) — 지하 대수층 59%', 'https://www.nmas.com.mx/ciudad-de-mexico/sociedad/de-donde-viene-agua-llega-cdmx-estos-mantos-acuiferos-abastecen-alcaldias/'),
    ('Wikipedia, History of Colonia Roma — 1902년 승인, 도로·상하수도 처음 갖춘 콜로니아, 1985년 지진 건물 472채', 'https://en.wikipedia.org/wiki/History_of_Colonia_Roma'),
    ('Wikipedia, Polanco — 1937년 개발', 'https://en.wikipedia.org/wiki/Polanco'),
    ('Wikipedia, Santa Fe, Mexico City — 모래 채굴장·매립지, 1980년대 개발, 업무지구', 'https://en.wikipedia.org/wiki/Santa_Fe,_Mexico_City'),
    ('Wikipedia, Conjunto Urbano Nonoalco Tlatelolco — 1960~1965년, 처음 102동, 멕시코 최대 아파트 단지', 'https://en.wikipedia.org/wiki/Conjunto_Urbano_Nonoalco_Tlatelolco'),
    ('La Crónica(2026.9.3) — 지하철 1969.9.4 개통, 12개 노선·195개 역·226.5km, 하루 450만 명 이상', 'https://www.cronica.com.mx/metropoli/2026/09/03/metro-cumple-57-anos-con-69-mil-millones-de-usuarios-transportados/'),
    ('Forbes México(2021.8.26) — 카블레부스 2호선 10.55km 기네스 기록, 1호선 9.2km', 'https://www.forbes.com.mx/cablebus-establece-record-guinness-como-el-teleferico-urbano-mas-largo-del-mundo/'),
    ('Infobae(2025.9.25) — 카블레부스 3호선(차풀테펙 숲 횡단) 개통 1년, 이용자 약 600만 명', 'https://www.infobae.com/mexico/2025/09/25/linea-3-del-cablebus-en-cdmx-cumple-un-ano-de-ofrecer-servicio-de-vasco-de-quiroga-a-los-pinos-en-chapultepec/'),
    ('재외동포청 웹진(2025.6) — 1905.4.4 제물포에서 1,033명 승선, 살리나크루스 도착, 유카탄 에네켄 농장, 후손 3만 명 이상', 'https://www.oka.go.kr/attach/cms/webzine/main/2025/06/9A1D9992944C485C893BD46CE6F0B725.pdf'),
    ('Mexico News Daily(2025.11.4) — 1905년 한인 1,033명 유카탄 도착', 'https://mexiconewsdaily.com/culture/the-green-gold-miners-from-korea-a-forgotten-diaspora/'),
    ('Wikipedia, Pequeño Seúl — 소나 로사의 한인타운', 'https://en.wikipedia.org/wiki/Peque%C3%B1o_Se%C3%BAl'),
    ('Airpaz·트립닷컴 AM91 운항 정보(2026.11 조회) — 인천→멕시코시티 직항 13시간 55분', 'https://www.airpaz.com/en/flight/code/AM-91'),
    ('FlightMapper AM90(2026.11 조회) — 멕시코시티→몬테레이→인천 약 19시간 15분', 'https://info.flightmapper.net/flight/Aeromexico_AM_90'),
    ('주한 멕시코 대사관 — 한국 국적자 최대 180일 무비자, 6개월 유효 여권', 'https://embamex.sre.gob.mx/corea/index.php/visas/2016-05-13-07-16-01'),
    ('호텔스컴바인, 인천–멕시코시티 항공권 조회(2026.11.26)', 'https://www.hotelscombined.co.kr/flight-routes/Incheon-Intl-ICN/Mexico-City-Benito-Juarez-MEX.ksp'),
    ('애틀랜타K(2026.1.31) — 인천–멕시코시티 직항 2026년 운휴 검토 보도(항공사 공식 발표 아님)', 'https://atlantak.com/%EC%A4%91%EB%82%A8%EB%AF%B8-%EC%9C%A0%EC%9D%BC-%EC%A7%81%ED%95%AD-%EC%9D%B8%EC%B2%9C-%EB%A9%95%EC%8B%9C%EC%BD%94%EC%8B%9C%ED%8B%B0-%EB%85%B8%EC%84%A0-%EC%8A%A4%ED%86%B1/'),
]
TAGS = ['멕시코시티', 'MexicoCity', 'CDMX', '도시이야기', '테노치티틀란', '텍스코코호', '지반침하', '독립기념탑', '소치밀코', '아스테카', '애니깽', '멕시코여행', '도시구조', '브동산']
