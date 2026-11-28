# -*- coding: utf-8 -*-
"""도시이야기 4편 — 브라질리아는 왜 비행기 모양일까. 가로 본편(LONG, A안) + 쇼츠 2편(S1 비행기, S2 밖에 사는 사람들, B안).
shot: ('clip', pexels_id, start) | ('ge', 구글어스 캡처, 시작배율, 끝배율, 가로이동, 세로이동) | ('anim', name, {opts})
line: (자막, 읽을 문장 또는 None)  — 숫자는 읽을 문장에서 한글로 푼다.
2026.11.28 Paul 새 기준: 나레이션 약 1.2배(본편 +15%, 쇼츠 +20% — lib/dosi_tts.py 기본값), 구글 어스·드론 실사를 최대한 많이.
"""
GE = '/home/claude/media/gearth_bsb/'
GEA = 'Google Earth · 2024 이미지'
EP = dict(
    no=4, city='브라질리아', slug='brasilia', key='bsb',
    title='브라질리아는 왜 비행기 모양일까', subtitle='41개월 만에 세운 수도',
    yt_title='브라질리아는 왜 비행기 모양일까 — 41개월 만에 세운 수도 | 도시이야기 4',
    shorts={'S1': ('브라질리아는 왜', '비행기 모양일까'), 'S2': ('브라질리아 사람들은', '왜 도시 밖에 살까')},
    shorts_title={'S1': '브라질리아는 왜 비행기 모양일까 | 도시이야기', 'S2': '브라질리아 사람들은 왜 도시 밖에 살까 | 도시이야기'},
    px='/home/claude/media/pexels_bsb/', geo='/home/claude/brond/scripts/dosi/ep4-brasilia/geo.json',
    work='/home/claude/work/ep4/', center=(-47.88, -15.79),
    minimap_bounds=(-48.16, -15.95, -47.78, -15.70), minimap_layers=['r_plano_piloto'], minimap_rivers=[],
    names={'LONG': 'brasilia-dosi-4-youtube', 'S1': 'brasilia-dosi-4-shorts-airplane', 'S2': 'brasilia-dosi-4-shorts-outside'},
    credits_map='지도  © OpenStreetMap contributors · Natural Earth', credits_ge='위성·3D 화면  Google Earth', ge_attrib='Google Earth',
    site_url='https://www.brandongsan.com/posts/brasilia-city-structure.html',
    yt_intro='1956년 브라질은 해안의 리우데자네이루에서 텅 빈 내륙 고원으로 수도를 옮기기로 했어요. 루시우 코스타가 그린 두 축이 만나는 십자 — 하늘에서 보면 비행기 모양인 계획도시는 41개월 만에 문을 열었어요. 50만 명을 위해 설계한 도시에 지금은 300만 명이 살고, 대부분은 비행기 바깥의 위성 도시에 사는 이유, 6층 슈퍼쿼드라와 30층 아과스 클라라스, 1963년 산투스에 닿은 첫 한인 이민, 한국에서 가는 법까지 구글 어스와 드론 실사로 정리했어요.',
    shorts_desc={'S1': '브라질리아는 1956년부터 41개월 만에 지은 계획 수도예요. 루시우 코스타의 설계는 두 축이 직각으로 만나는 십자에서 시작했고, 지형에 맞춰 한쪽 축을 휘게 그리면서 하늘에서 보면 비행기 모양이 됐어요. 몸통은 정부 청사가 늘어선 기념축, 날개는 6층 아파트 단지(슈퍼쿼드라)예요.\n출처: Domus(2020), 위키백과(Brasília), Correio Braziliense(2026.11)',
                 'S2': '루시우 코스타의 플라누 필로투는 50만 명을 위한 도시였어요. 지금 연방구 인구는 약 300만 명(IBGE 2025 추정)인데, 플라누 필로투에는 22만 명(PDAD 2021)만 살아요. 나머지는 1971년 세운 세일란지아(28.7만 명), 30층 아파트가 늘어선 아과스 클라라스 같은 위성 도시에 살아요.\n출처: IBGE, IPEDF PDAD 2021, Jornal de Brasília(2024)'},
    thumbs=dict(LONG=dict(clip='19141615', t=5, cx=0.5, lines=['브라질리아는', '왜 비행기', '모양일까'], sub='41개월 만에 세운 수도 ', accent='1960'),
                S1=dict(kind='photo', clip='35691266', t=10, cx=0.5, cy=0.5, big='41개월', small='텅 빈 고원에 세운 수도'),
                S2=dict(kind='photo', clip='32269840', t=8, cx=0.5, cy=0.5, big='50만→300만', small='설계보다 6배 커진 도시')),
)
OSM = '© OpenStreetMap contributors · Natural Earth'
SELF = '브동산 자체 제작 개략도 · 실제 경계·축척과 다를 수 있음'
RA = ['r_plano_piloto', 'r_ceilandia', 'r_taguatinga', 'r_aguas_claras', 'r_samambaia', 'r_gama', 'r_lago_sul', 'r_lago_norte', 'r_sobradinho',
      'r_guara', 'r_cruzeiro', 'r_sudoeste', 'r_recanto', 'r_santa_maria']
HAIR = [dict(g=k, color='hair', width=1.1, at=0) for k in RA]
LAKE = dict(g='w_paranoa', color='river', width=1.2, fill=0.55, at=0)

def plan_map(short=False):
    return ('anim', 'map', dict(bounds=(-47.975, -15.865, -47.80, -15.715), layers=[dict(g='r_plano_piloto', color='soft', width=1.4, alpha=0.6, at=0), LAKE,
        dict(g='ax_mon', color='brass', width=7, at=0, d=0.2), dict(g='ax_rod', color='brass', width=7, at=1, d=0.1)],
        markers=[dict(p='tres_poderes', label='3권 광장(조종석)', at=0, d=0.6, off=(1, 0.9)), dict(p='rodoviaria', label='버스터미널(교차점)', at=1, d=0.5, off=(-1, 0), anchor='rm'),
                 dict(p='asa_norte', label='북쪽 날개', at=1, d=0.8, off=(-1, 0), anchor='rm', color='ink'), dict(p='asa_sul', label='남쪽 날개', at=1, d=1.0, off=(-1, 0), anchor='rm', color='ink')],
        texts=[dict(s='파라노아 호수', p=(-47.835, -15.765), at=0, size=30, color='soft', alpha=0.9)],
        side=None if short else dict(title=('플라누 필로투', 0), big=('1957', 0), sub=('루시우 코스타의 당선안', 0), sub2=('몸통 = 기념축 · 날개 = 주거', 1))))

def axis(stage):
    zn = []
    c1 = 'brass' if stage == 1 else 'soft'
    zn.append(dict(p='rodoviaria', rkm=5.5, label='플라누 필로투', off=(0, -1), at=0, color=c1))
    if stage >= 2:
        c2 = 'brass' if stage == 2 else 'soft'
        zn += [dict(p='taguatinga_c', rkm=2.5, label='타구아팅가 1958', off=(0.3, -1.1), at=0 if stage > 2 else 1, color=c2),
               dict(p='ceilandia_c', rkm=3.4, label='세일란지아 1971', off=(-0.3, 1.1), at=0 if stage > 2 else 1, d=0.3, color=c2)]
    if stage == 3:
        zn += [dict(p='aguas_claras_c', rkm=2.2, label='아과스 클라라스 2003', off=(0.2, 1.1), at=1, color='brass')]
    stg = {1: ('①', '비행기 안, 플라누 필로투', '1960년~'), 2: ('②', '서쪽 위성 도시', '1958·1971년~'), 3: ('③', '고층 아파트 도시', '2000년대~')}[stage]
    return ('anim', 'map', dict(bounds=(-48.16, -15.93, -47.79, -15.71), layers=HAIR + [LAKE], zones=zn, stage=stg))

LONG = [
  # ── Ⅰ 오프닝: 제목 + 실사 → 서울과 면적 비교
  dict(chap='Ⅰ   오프닝', loc='catedral', title=True, shots=[('clip', '19141615', 0), ('clip', '35691250', 2)], lines=[
    ('해발 1,172m 고원, 브라질의 수도 브라질리아예요.', '해발 천백칠십이 미터 고원, 브라질의 수도 브라질리아예요.'),
    ('하늘에서 보면 이 도시는 비행기 모양이에요. 왜일까요?', None)]),
  dict(chap='Ⅰ   오프닝', chapter='01  브라질리아는 얼마나 클까', attrib=OSM, note=SELF, shots=[('anim', 'overlay', dict(
      city='df', compare=None, city_label='브라질리아 연방구', city_label_at=(-47.32, -15.47), seoul_at=(-47.88, -15.82),
      side=dict(title=('연방구 면적', 0), big=('5,760㎢', 0), sub=('서울의 약 9.5배', 0), sub2=('행정구역 35곳', 0))))], lines=[
    ('수도가 있는 연방구는 5,760㎢, 서울의 9.5배쯤이에요.', '수도가 있는 연방구는 오천칠백육십 제곱킬로미터, 서울의 아홉 배 반쯤이에요.')]),
  # ── Ⅱ 숫자로 보는 브라질리아
  dict(chap='Ⅱ   숫자로 보는 브라질리아', chapter='02  숫자로 보는 브라질리아', shots=[('anim', 'numbers', dict(title='숫자로 보는 브라질리아', head=('브라질리아', '서울'), rows=[
      ('면적(연방구)', '5,760㎢', '605㎢', True), ('인구(2025 추정)', '약 300만 명', '934만 명', False), ('그중 플라누 필로투', '22만 명(2021)', '', False),
      ('해발 고도', '1,172m', '', False), ('수도가 된 해', '1960년', '', False), ('인천에서', '2회 경유 약 35시간 · 시차 12시간', '', False)],
      src='출처: IBGE(2025 추정·면적) · IPEDF PDAD 2021 · 통계청(2025) · 항공편 조회(2026.11)'))], lines=[
    ('약 300만 명이 사는데, 비행기 모양 안에 사는 사람은 22만 명뿐이에요.', '약 삼백만 명이 사는데, 비행기 모양 안에 사는 사람은 이십이만 명뿐이에요.')]),
  # ── Ⅲ 텅 빈 고원에 세운 수도
  dict(chap='Ⅲ   텅 빈 고원에 세운 수도', chapter='03  텅 빈 고원에 세운 수도', attrib=GEA, loc=(-47.92, -15.79), shots=[('ge', GE + 'g7_region.jpg', 1.0, 1.25, 0.0, 0.0)], lines=[
    ('1950년대까지 브라질의 수도는 바닷가의 리우데자네이루였어요.', '천구백오십년대까지 브라질의 수도는 바닷가의 리우데자네이루였어요.'),
    ('1956년, 쿠비체크 대통령은 텅 빈 내륙 고원에 새 수도를 짓기로 했어요.', '천구백오십육년, 쿠비체크 대통령은 텅 빈 내륙 고원에 새 수도를 짓기로 했어요.')]),
  dict(chap='Ⅲ   텅 빈 고원에 세운 수도', loc='esplanada', shots=[('clip', '35703751', 2)], lines=[
    ('사람이 거의 살지 않던 땅에 바다 대신 나라 한가운데를 키우겠다는 계획이었죠.', None)]),
  dict(chap='Ⅲ   텅 빈 고원에 세운 수도', attrib=OSM, note=SELF, shots=[plan_map()], lines=[
    ('1957년 공모에서 뽑힌 루시우 코스타의 도시 계획은 두 축이 직각으로 만나는 십자에서 시작했어요.', '천구백오십칠년 공모에서 뽑힌 루시우 코스타의 도시 계획은 두 축이 직각으로 만나는 십자에서 시작했어요.'),
    ('지형에 맞춰 한 축을 휘자, 비행기 모양이 됐어요.', None)]),
  dict(chap='Ⅲ   텅 빈 고원에 세운 수도', attrib=GEA, loc='rodoviaria', shots=[('ge', GE + 'g1_overview.jpg', 1.0, 1.18, -0.1, 0.0)], lines=[
    ('위에서 보면 그대로예요. 가운데 몸통과 양쪽으로 휜 날개.', None)]),
  dict(chap='Ⅲ   텅 빈 고원에 세운 수도', loc='esplanada', shots=[('clip', '35691266', 0)], caption=dict(line=1, t1='41개월', t2='1956 착공 → 1960.4.21 개막'), lines=[
    ('공사는 1956년에 시작했고,', '공사는 천구백오십육년에 시작했고,'),
    ('41개월 만인 1960년 4월 21일, 새 수도가 문을 열었어요.', '사십일 개월 만인 천구백육십년 사월 이십일일, 새 수도가 문을 열었어요.')]),
  # ── Ⅳ 비행기의 몸통, 기념축
  dict(chap='Ⅳ   비행기의 몸통, 기념축', chapter='04  비행기의 몸통, 기념축', attrib=GEA, loc='esplanada', shots=[('ge', GE + 'g9_eixo3d.jpg', 1.0, 1.15, 0.0, -0.1)], lines=[
    ('몸통은 기념축이에요. 넓은 잔디 광장 양쪽으로 큰 길이 달려요.', None)]),
  dict(chap='Ⅳ   비행기의 몸통, 기념축', loc='esplanada', shots=[('clip', '30360356', 2), ('clip', '35703753', 4)], lines=[
    ('양옆엔 똑같이 생긴 부처 청사가 줄지어 서 있어요.', None),
    ('설계는 건축가 오스카르 니에메예르가 맡았어요.', None)]),
  dict(chap='Ⅳ   비행기의 몸통, 기념축', loc='congresso', shots=[('clip', '30179032', 0)], lines=[
    ('조종석 자리엔 국회가 있어요. 쌍둥이 빌딩과 두 개의 접시 모양 지붕이에요.', None)]),
  dict(chap='Ⅳ   비행기의 몸통, 기념축', loc='tres_poderes', shots=[('ge', GE + 'g8_congresso3d.jpg', 1.0, 1.14, 0.0, 0.0)], attrib=GEA, lines=[
    ('그 앞이 대통령궁과 대법원이 마주 보는 3권 광장이에요.', '그 앞이 대통령궁과 대법원이 마주 보는 삼권 광장이에요.')]),
  dict(chap='Ⅳ   비행기의 몸통, 기념축', loc='catedral', shots=[('clip', '31711540', 0), ('clip', '31711579', 2)], caption=dict(line=0, t1='1987', t2='유네스코 세계유산 등재'), lines=[
    ('왕관처럼 생긴 대성당도 이 길 위에 있어요.', None),
    ('도시 전체가 1987년 유네스코 세계유산이 됐어요.', '도시 전체가 천구백팔십칠년 유네스코 세계유산이 됐어요.')]),
  dict(chap='Ⅳ   비행기의 몸통, 기념축', loc='torre_tv', shots=[('clip', '29192349', 4)], lines=[
    ('두 축이 만나는 곳엔 버스터미널이 있고, 그 서쪽에 TV 타워가 서 있어요.', '두 축이 만나는 곳엔 버스터미널이 있고, 그 서쪽에 티비 타워가 서 있어요.')]),
  # ── Ⅴ 파라노아 호수
  dict(chap='Ⅴ   만든 호수, 파라노아', chapter='05  만든 호수, 파라노아', attrib=GEA, loc='ponte_jk', shots=[('ge', GE + 'g4_ponte_jk3d.jpg', 1.0, 1.15, 0.1, 0.0)], caption=dict(line=0, t1='48㎢', t2='1959년 댐으로 만든 호수'), lines=[
    ('도시를 감싼 호수도 사람이 만들었어요. 1959년 강을 막아 만든 48㎢ 호수예요.', '도시를 감싼 호수도 사람이 만들었어요. 천구백오십구년 강을 막아 만든 사십팔 제곱킬로미터 호수예요.')]),
  dict(chap='Ⅴ   만든 호수, 파라노아', loc='ponte_jk', shots=[('clip', '10125425', 2), ('clip', '30377363', 4)], lines=[
    ('건조한 고원 도시에 습기를 더하려는 이유도 있었어요.', None),
    ('호수 위로는 아치 세 개가 이어진 JK 다리가 놓였어요.', '호수 위로는 아치 세 개가 이어진 제이케이 다리가 놓였어요.')]),
  dict(chap='Ⅴ   만든 호수, 파라노아', loc='alvorada', shots=[('clip', '20256708', 2)], lines=[
    ('호숫가엔 대통령 관저와 넓은 단독주택 동네가 들어섰어요.', None)]),
  # ── Ⅵ 비행기의 날개, 슈퍼쿼드라
  dict(chap='Ⅵ   비행기의 날개, 슈퍼쿼드라', chapter='06  비행기의 날개, 슈퍼쿼드라', attrib=GEA, loc='sqs308', shots=[('ge', GE + 'g3_superquadra.jpg', 1.05, 1.25, 0.0, 0.0)], caption=dict(line=1, t1='6층', t2='슈퍼쿼드라 · 필로티 위 아파트'), lines=[
    ('날개에는 사람들이 사는 아파트 단지, 슈퍼쿼드라가 줄지어 있어요.', None),
    ('나무숲 속에 6층 아파트가 1층을 비운 기둥 위에 서 있어요.', '나무숲 속에 육층 아파트가 일층을 비운 기둥 위에 서 있어요.')]),
  dict(chap='Ⅵ   비행기의 날개, 슈퍼쿼드라', loc='sqs308', shots=[('clip', '27902849', 2)], lines=[
    ('단지 네 개가 학교와 가게를 함께 쓰는 한 동네가 되도록 설계했어요.', None)]),
  # ── Ⅶ 주거축 이동 3단계
  dict(chap='Ⅶ   비행기 밖으로', chapter='07  비행기 밖으로 — 주거축 3단계', attrib=OSM, note=SELF, shots=[axis(1)], lines=[
    ('플라누 필로투는 50만 명이 살 도시로 계획됐어요.', '플라누 필로투는 오십만 명이 살 도시로 계획됐어요.'),
    ('그런데 수도를 지으러 온 노동자들은 처음부터 도시 밖에 자리를 잡았어요.', None)]),
  dict(chap='Ⅶ   비행기 밖으로', attrib=OSM, note=SELF, shots=[axis(2)], lines=[
    ('1958년 타구아팅가가 생겼고,', '천구백오십팔년 타구아팅가가 생겼고,'),
    ('1971년엔 판자촌을 옮기는 캠페인 이름을 딴 세일란지아가 세워졌어요.', '천구백칠십일년엔 판자촌을 옮기는 캠페인 이름을 딴 세일란지아가 세워졌어요.')]),
  dict(chap='Ⅶ   비행기 밖으로', attrib=GEA, loc='ceilandia_c', shots=[('ge', GE + 'g5_ceilandia.jpg', 1.0, 1.22, -0.15, 0.0)], caption=dict(line=0, t1='28.7만 명', t2='세일란지아 · 2022 인구조사'), lines=[
    ('지금 세일란지아엔 28만 7천 명, 연방구에서 가장 많은 사람이 살아요.', '지금 세일란지아엔 이십팔만 칠천 명, 연방구에서 가장 많은 사람이 살아요.')]),
  dict(chap='Ⅶ   비행기 밖으로', attrib=OSM, note=SELF, shots=[axis(3)], lines=[
    ('세 번째는 2003년 따로 떨어져 나온 아과스 클라라스예요.', '세 번째는 이천삼년 따로 떨어져 나온 아과스 클라라스예요.')]),
  dict(chap='Ⅶ   비행기 밖으로', attrib=GEA, loc='aguas_claras_c', shots=[('ge', GE + 'g6_aguas_claras3d.jpg', 1.0, 1.15, 0.0, 0.0)], lines=[
    ('6층으로 묶인 플라누 필로투와 달리 20층, 30층 아파트가 숲처럼 섰어요.', '육층으로 묶인 플라누 필로투와 달리 이십층, 삼십층 아파트가 숲처럼 섰어요.')]),
  dict(chap='Ⅶ   비행기 밖으로', loc='aguas_claras_c', shots=[('clip', '32269840', 2)], caption=dict(line=0, t1='1㎢에 1.4만 명', t2='아과스 클라라스 · 연방구 최고 밀도'), lines=[
    ('9.2㎢에 12만 8천 명, 연방구에서 가장 빽빽한 동네예요.', '구 점 이 제곱킬로미터에 십이만 팔천 명, 연방구에서 가장 빽빽한 동네예요.')]),
  # ── Ⅷ 사람들
  dict(chap='Ⅷ   브라질리아 사람들', chapter='08  브라질리아 사람들', loc='esplanada', shots=[('clip', '27902485', 2), ('clip', '27902453', 6)], lines=[
    ('일자리는 여전히 비행기 안에 몰려 있어요.', None),
    ('2021년 일하는 사람의 40.7%가 플라누 필로투로 출근했어요.', '이천이십일년 일하는 사람의 사십 점 칠 퍼센트가 플라누 필로투로 출근했어요.')]),
  dict(chap='Ⅷ   브라질리아 사람들', loc='mane', shots=[('clip', '27956912', 2)], lines=[
    ('2024년엔 34.4%로 줄었어요. 위성 도시가 스스로 일자리를 키우고 있다는 뜻이에요.', '이천이십사년엔 삼십사 점 사 퍼센트로 줄었어요. 위성 도시가 스스로 일자리를 키우고 있다는 뜻이에요.')]),
  # ── Ⅸ 교통
  dict(chap='Ⅸ   교통 인프라', chapter='09  교통 인프라', loc='esplanada', shots=[('clip', '34181001', 0), ('clip', '10136771', 2)], lines=[
    ('도시는 자동차를 기준으로 설계됐어요. 신호등 대신 입체 교차로가 많아요.', None),
    ('지금도 출퇴근하는 사람의 절반 넘게 자가용을 타요.', None)]),
  dict(chap='Ⅸ   교통 인프라', shots=[('anim', 'card', dict(title='브라질리아의 길', items=[('42.38km', '지하철 1개 노선 · 두 갈래', 0), ('27개', '운행 중인 역', 0), ('14만 명', '하루 승객', 1), ('52%', '자가용으로 출근(2021)', 1)],
      src='출처: Metrô-DF · Correio Braziliense(2026.6) · IPEDF PDAD 2021'))], lines=[
    ('지하철은 42km, 27개 역에 하루 14만 명이 타요.', '지하철은 사십이 킬로미터, 이십칠 개 역에 하루 십사만 명이 타요.'),
    ('비행기 몸통에서 세일란지아와 사맘바이아로 갈라져 나가요.', None)]),
  # ── Ⅹ 한국과의 연결
  dict(chap='Ⅹ   한국과의 연결', chapter='10  한국과의 연결', loc='itamaraty', shots=[('clip', '5539902', 0)], caption=dict(line=0, t1='1959.10.31', t2='한국–브라질 수교'), lines=[
    ('한국과 브라질은 1959년, 브라질리아가 문을 열기 직전에 수교했어요.', '한국과 브라질은 천구백오십구년, 브라질리아가 문을 열기 직전에 수교했어요.'),
    ('중남미에서 한국과 처음 수교한 나라예요.', None)]),
  dict(chap='Ⅹ   한국과의 연결', shots=[('anim', 'card', dict(title='한국과 브라질', items=[('1962.12.18', '부산항 출발 · 첫 이민단 103명', 0), ('1963.2.12', '산투스항 도착', 0), ('5만 명+', '브라질의 한인', 1)],
      src='출처: 중앙일보(2022.12) · DBpia 재브라질 한인사회 연구 · 위키백과(Brazil–South Korea relations)'))], lines=[
    ('1962년 12월 부산항을 떠난 첫 이민단 103명이 이듬해 2월 산투스항에 닿았어요.', '천구백육십이년 십이월 부산항을 떠난 첫 이민단 백세 명이 이듬해 이월 산투스항에 닿았어요.'),
    ('지금 브라질의 한인은 5만 명이 넘어요.', '지금 브라질의 한인은 오만 명이 넘어요.')]),
  # ── Ⅺ 한국에서 가는 법
  dict(chap='Ⅺ   한국에서 가는 법', chapter='11  한국에서 가는 법', loc='bsb', shots=[('clip', '35703754', 2)], caption=dict(line=0, t1='약 35시간', t2='인천 → 브라질리아 · 2회 경유'), lines=[
    ('인천에서 브라질리아로 가는 직항은 없어요. 두 번 갈아타고 35시간쯤 걸려요.', '인천에서 브라질리아로 가는 직항은 없어요. 두 번 갈아타고 서른다섯 시간쯤 걸려요.'),
    ('시차는 12시간, 한국 여권이면 비자 없이 90일까지 머물 수 있어요.', '시차는 열두 시간, 한국 여권이면 비자 없이 구십 일까지 머물 수 있어요.')]),
  dict(chap='Ⅺ   한국에서 가는 법', loc='congresso', end=True, shots=[('clip', '30179035', 0)], lines=[
    ('텅 빈 고원에 비행기를 그려 세운 도시, 브라질리아였어요.', None)]),
]

# ───────── 쇼츠 (B안 리얼 생생, 1080×1920). hl = 자막에서 황동색으로 칠할 말
S1 = [
  dict(tag='브라질리아 기념축', loc='esplanada', shots=[('clip', '35691266', 0)], lines=[('브라질리아는 하늘에서 보면 비행기 모양이에요.', None, '비행기 모양')]),
  dict(tag='위에서 본 브라질리아', attrib=GEA, loc='rodoviaria', shots=[('ge', GE + 'g1_overview.jpg', 1.0, 1.2, 0.0, 0.0)], lines=[
      ('가운데 몸통, 양쪽으로 휜 날개. 진짜죠?', None, '날개')]),
  dict(tag='플라누 필로투 · 개략도', attrib=OSM, shots=[plan_map(short=True)], lines=[
      ('처음 그림은 두 길이 직각으로 만나는 십자였어요.', None, '십자'), ('지형에 맞춰 한 축을 휘자 비행기가 됐죠.', None, '비행기')]),
  dict(tag='국회의사당', loc='congresso', shots=[('clip', '30179032', 0)], lines=[('조종석 자리엔 국회가 있어요.', None, '국회')]),
  dict(tag='기념축 · 부처 청사', attrib=GEA, loc='esplanada', shots=[('ge', GE + 'g9_eixo3d.jpg', 1.0, 1.15, 0.0, 0.0)], lines=[('몸통엔 정부 청사가 줄지어 서 있고,', None, '정부 청사')]),
  dict(tag='슈퍼쿼드라', attrib=GEA, loc='sqs308', shots=[('ge', GE + 'g3_superquadra.jpg', 1.05, 1.3, 0.0, 0.0)], sticker=dict(line=0, delay=0.8, t1='6층', t2='슈퍼쿼드라'), lines=[
      ('날개엔 6층 아파트가 숲속에 늘어서 있어요.', '날개엔 육층 아파트가 숲속에 늘어서 있어요.', '6층 아파트')]),
  dict(tag='메트로폴리탄 대성당', loc='catedral', shots=[('clip', '31711543', 0)], bubble=dict(line=0, t1='41개월', t2='1956 → 1960 개막'), lines=[
      ('이 도시를 텅 빈 고원에 41개월 만에 지었어요.', '이 도시를 텅 빈 고원에 사십일 개월 만에 지었어요.', '41개월')]),
  dict(tag='JK 다리', loc='ponte_jk', end=True, shots=[('clip', '30377363', 2)], lines=[('비행기 도시가 생긴 이야기, 본편에서 이어져요.', None, '본편')]),
]
S2 = [
  dict(tag='브라질리아', loc='catedral', shots=[('clip', '19141615', 2)], lines=[('브라질리아는 50만 명이 살 도시로 설계됐어요.', '브라질리아는 오십만 명이 살 도시로 설계됐어요.', '50만 명')]),
  dict(tag='위에서 본 연방구', attrib=GEA, loc=(-47.95, -15.8), shots=[('ge', GE + 'g7_region.jpg', 1.0, 1.25, 0.0, 0.0)], bubble=dict(line=0, t1='약 300만 명', t2='연방구 인구 · 2025 추정'), lines=[
      ('그런데 지금 300만 명이 살아요.', '그런데 지금 삼백만 명이 살아요.', '300만 명')]),
  dict(tag='주거축 · 개략도', attrib=OSM, shots=[axis(2)], lines=[('비행기 모양 안에 사는 사람은 22만 명뿐이에요.', '비행기 모양 안에 사는 사람은 이십이만 명뿐이에요.', '22만 명')]),
  dict(tag='세일란지아', attrib=GEA, loc='ceilandia_c', shots=[('ge', GE + 'g5_ceilandia.jpg', 1.0, 1.25, 0.0, 0.0)], sticker=dict(line=0, delay=0.8, t1='1971', t2='세일란지아'), lines=[
      ('수도를 지은 노동자들의 판자촌을 옮겨 세운 도시가 세일란지아예요.', None, '세일란지아')]),
  dict(tag='세일란지아 · 가장 큰 동네', attrib=GEA, loc='ceilandia_c', shots=[('ge', GE + 'g5_ceilandia.jpg', 1.3, 1.5, 0.2, 0.1)], lines=[
      ('지금은 28만 명, 연방구에서 사람이 가장 많아요.', '지금은 이십팔만 명, 연방구에서 사람이 가장 많아요.', '28만 명')]),
  dict(tag='아과스 클라라스', attrib=GEA, loc='aguas_claras_c', shots=[('ge', GE + 'g6_aguas_claras3d.jpg', 1.0, 1.2, 0.0, 0.0)], lines=[
      ('6층으로 묶인 도심 대신 30층 아파트 도시도 생겼어요.', '육층으로 묶인 도심 대신 삼십층 아파트 도시도 생겼어요.', '30층')]),
  dict(tag='아과스 클라라스', loc='aguas_claras_c', shots=[('clip', '32269840', 3)], lines=[('1㎢에 1만 4천 명, 가장 빽빽한 동네예요.', '일 제곱킬로미터에 만 사천 명, 가장 빽빽한 동네예요.', '1만 4천 명')]),
  dict(tag='기념축의 아침', loc='esplanada', end=True, shots=[('clip', '30360458', 2)], lines=[('비행기 밖으로 커진 도시 이야기, 본편에서 이어져요.', None, '비행기 밖')]),
]

# 설명란·글에 쓰는 숫자 출처
SOURCES = [
    ('IBGE Cidades@ 연방구 — 면적 5,760.785㎢(2025), 인구 2,817,381명(2022 인구조사), 추정 2,996,899명(2025)', 'https://www.ibge.gov.br/cidades-e-estados/df'),
    ('Wikipedia, Brasília — 1960.4.21 개막, 해발 1,172m, 비행기 모양 계획(기념축·3권 광장), 연방구 행정구역', 'https://en.wikipedia.org/wiki/Bras%C3%ADlia'),
    ('Domus(2020.4.21) — 1956~1960 41개월 공사, 루시우 코스타 계획·니에메예르 건축, 유네스코 세계유산', 'https://domusweb.it/en/speciali/brasilia/2020/brasilia-today-we-celebrate-its-60th-anniversary.html'),
    ('NSC Total(2026.4) — 두 축이 직각으로 만나는 십자에서 출발, 50만 명 계획', 'https://www.nsctotal.com.br/turismo/brasilia-66-anos-modernismo-unesco'),
    ('Il Post(2020.4.21) — 처음엔 십자, 지형 때문에 비행기 모양으로', 'https://www.ilpost.it/2020/04/21/brasilia-capitale-brasile/?amp=1'),
    ('EBSCO Research Starters, 「Brazil Builds a New Capital City」 — 1956.4.18~1960.4.21, 1987 세계유산', 'https://www.ebsco.com/research-starters/history/brazil-builds-new-capital-city'),
    ('Agência Senado(2020.4) — 플라누 필로투 30만 명 미만, 계획 50만 명', 'https://www12.senado.leg.br/noticias/infomaterias/2020/04/brasilia-60-anos-a-cidade-em-debate'),
    ('IPEDF PDAD 2021(플라누 필로투) — 도시 인구 224,848명', 'https://ipe.df.gov.br/documents/9915964/10216206/PDAD_2021-Apresentacao_Central.pdf'),
    ('Metrópoles(2022.7.6), PDAD 2021 — 일하는 사람의 40.7%가 플라누 필로투에서 일함, 자가용 출근 52% 이상', 'https://www.metropoles.com/distrito-federal/codeplan-divulga-pesquisa-comparativa-sobre-perfil-das-33-ras-do-df'),
    ('Correio da Manhã(2025.5.7), PDAD-A 2024 — 플라누 필로투 근무 34.4%', 'https://digital.correiodamanha.com.br/jornalcorreiodamanha/2025/05/07/000184/pdf/0705df_cmanha09.pdf'),
    ('Correio Braziliense(2026.11.17) — 슈퍼쿼드라 6층 이하·필로티', 'https://www.correiobraziliense.com.br/cbradar/predios-brasilia-parecem-flutuar-pilotis-lucio-costa/'),
    ('Oculum Ensaios(2013) — 슈퍼쿼드라 4개가 한 동네(유니다지 지 비지냔사)', 'https://doaj.org/article/57b98ac151e740c898caf9dc5fe06917'),
    ('Google Arts & Culture — 파라노아 호수 1959년 조성, 48㎢, 최대 수심 38m, 습도를 높이려는 목적', 'https://artsandculture.google.com/asset/paranoa-lake-brasilia/5QH9rvPmebf9og'),
    ('Jornal de Brasília(2024) — 세일란지아 1971년, 2022 인구조사 287,023명, 이름은 판자촌 철거 캠페인(CEI)', 'https://jornaldebrasilia.com.br/brasilia/regiao-mais-populosa-do-df-ceilandia-completa-53-anos/'),
    ('Jornal de Brasília(2026) — PDAD-A, 연방구 행정구역 35곳', 'https://jornaldebrasilia.com.br/brasilia/ceilandia-continua-sendo-a-cidade-com-maior-numero-de-moradores-segundo-nova-pdad-ampliada/'),
    ('Jornal de Brasília(2024.3.22) — 아과스 클라라스 9.2㎢에 12만 8천 명, 1㎢당 14,074명', 'https://jornaldebrasilia.com.br/brasilia/aguas-claras-tudo-junto-no-mesmo-lugar/'),
    ('Correio Braziliense(2026.5.3) — 아과스 클라라스 2003년 행정구역 지정', 'https://edicao.correiobraziliense.com.br/correiobraziliense/2026/05/03/20427a/pdf/A16-CID-0305-DIG.pdf'),
    ('Câmara Legislativa do DF(2025), Metrô-DF 자료 — 42.38km, 27개 역 운행', 'https://www.cl.df.gov.br/documents/20063946/34008274/apresenta%C3%A7%C3%A3o%20Vai%20de%20Gra%C3%A7a%20vers%C3%A3o%202.pdf'),
    ('Correio Braziliense(2026.6) — 지하철 하루 약 14만 명, 세일란지아·사맘바이아 연장 공사', 'https://www.correiobraziliense.com.br/cidades-df/2026/06/7432508-expansao-do-metro-avanca-mas-desafios-de-infraestrutura-persistem.html'),
    ('외교부 — 한국·브라질 수교 1959.10.31', 'https://www.mofa.go.kr/eng/nation/m_4902/view.do?seq=47'),
    ('주한 브라질 대사관(2024) — 중남미 첫 한국 수교국', 'https://www.gov.br/mre/pt-br/embaixada-seul/noticias/65-anos-das-relacoes-diplomaticas-brasil-e-coreia-do-sul'),
    ('중앙일보(2022.12.7) — 1962.12.18 제1차 브라질 이민단 103명 부산항 출발', 'https://v.daum.net/v/20221207101151029'),
    ('DBpia, 재브라질 한인사회 연구 — 1963.2.12 도착', 'https://www.dbpia.co.kr/Article/NODE02086564'),
    ('Wikipedia, Brazil–South Korea relations — 브라질 한인 5만 명 이상', 'https://en.wikipedia.org/wiki/Brazil%E2%80%93South_Korea_relations'),
    ('KAYAK — 인천–브라질리아 직항 없음, 최소 2회 경유, 약 35시간', 'https://www.kayak.co.kr/%EB%B8%8C%EB%9D%BC%EC%A7%88%EB%A6%AC%EC%95%84-Brasilia-%EA%B3%B5%ED%95%AD.BSB.ap.html'),
    ('스카이스캐너 — 한국 여권 브라질 무비자 90일', 'https://www.skyscanner.co.kr/destinations/visa/29475405/brazil'),
]
TAGS = ['브라질리아', 'Brasilia', '브라질', '도시이야기', '계획도시', '루시우코스타', '니에메예르', '슈퍼쿼드라', '파라노아호수', '세일란지아', '브라질수도', '브라질여행', '도시구조', '브동산']
