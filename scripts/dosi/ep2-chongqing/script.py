# -*- coding: utf-8 -*-
"""도시이야기 2편 — 충칭은 왜 8D 도시가 됐을까. 가로 본편(LONG, A안) + 쇼츠 2편(S1, S2, B안).
shot: ('clip', pexels_id, start) | ('anim', name, {opts})
line: (자막, 읽을 문장 또는 None)  — 숫자는 읽을 문장에서 한글로 푼다.
오프닝 순서(2026.11.27 확정): 제목+실사 → 서울과 면적 비교 → 숫자로 보는 도시 → 나머지 9꼭지.
실사 없는 장면은 짧게(면적 비교 8초 안팎, 숫자 12초 안쪽, 그 밖의 그래픽 12초 이하).
"""
EP = dict(
    no=2, city='충칭', slug='chongqing', key='cq',
    title='충칭은 왜 8D 도시가 됐을까', subtitle='두 강과 산이 만든 입체 도시',
    yt_title='충칭은 왜 8D 도시가 됐을까 — 두 강과 산이 만든 입체 도시 | 도시이야기 2',
    shorts={'S1': ('충칭은 서울보다', '얼마나 클까'), 'S2': ('충칭 지하철은 왜', '아파트를 뚫고 지나갈까')},
    shorts_title={'S1': '충칭은 서울보다 얼마나 클까 | 도시이야기', 'S2': '충칭 지하철은 왜 아파트를 뚫고 지나갈까 | 도시이야기'},
    px='/home/claude/media/pexels_cq/', geo='/home/claude/brond/scripts/dosi/ep2-chongqing/geo.json',
    work='/home/claude/work/ep2/', center=(106.55, 29.56),
    minimap_bounds=(106.36, 29.44, 106.72, 29.70), minimap_layers=['d_yuzhong'], minimap_rivers=['osm_yangtze', 'osm_jialing'],
    names={'LONG': 'chongqing-dosi-2-youtube', 'S1': 'chongqing-dosi-2-shorts-size', 'S2': 'chongqing-dosi-2-shorts-liziba'},
    credits_map='지도  © OpenStreetMap contributors · Natural Earth',
    site_url='https://www.brandongsan.com/posts/chongqing-city-structure.html',
    yt_intro='서울의 136배, 인구 3,187만 명. 장강과 자링강이 만나는 좁은 반도에서 시작한 충칭이 강 건너편과 북쪽 신도시로 커지면서 길과 집과 철도를 층층이 쌓은 "8D 도시"가 된 순서를 지도와 실사로 따라가요. 19층 건물을 뚫고 지나가는 리쯔바역, 1층도 11층도 길인 훙야둥, 대한민국 임시정부가 머문 도시, 한국에서 가는 법까지 정리했어요.',
    shorts_desc={'S1': '같은 축척으로 겹쳐 보면 충칭시는 서울의 136배, 남한 면적의 약 82%예요. (82,400㎢ vs 605㎢)\n출처: 충칭시 통계국 2025 통계공보, 통계청(2025)',
                 'S2': '충칭 2호선 리쯔바역은 19층 건물의 6~8층에 있어요. 1~5층은 상가, 9~19층은 집. 역과 건물은 1998년에 함께 설계됐어요.\n출처: 중국신문망(2018) 설계자 인터뷰, 중국도시궤도교통협회(2026.1)'},
    thumbs=dict(LONG=dict(clip='39744311', t=5, cx=0.35, lines=['충칭은 왜', '8D 도시가', '됐을까'], sub='두 강과 산이 만든 ', accent='입체 도시'),
                S1=dict(kind='overlay', city='cq', seoul_at=(106.55, 29.56), city_label='충칭시', big='136배', small='같은 축척으로 겹쳐 본 면적'),
                S2=dict(kind='photo', clip='29682593', t=10, cx=0.5, cy=0.4, big='6~8층이 역', small='19층 건물 속 리쯔바역')),
)
OSM = '© OpenStreetMap contributors · Natural Earth'
SELF = '브동산 자체 제작 개략도 · 실제 경계·축척과 다를 수 있음'
CITY_B = (106.26, 29.42, 106.78, 29.78)      # 중심 시가지
RIV_B = (106.43, 29.50, 106.65, 29.63)       # 두 강이 만나는 곳
RIVERS = [dict(g='osm_yangtze', color='river', width=14, label=('장강(양쯔강)', 106.533, 29.531), at=0),
          dict(g='osm_jialing', color='river', width=10, label=('자링강', 106.488, 29.566), at=0)]
RIVERS_C = [dict(g='osm_yangtze', color='river', width=8, alpha=0.95, at=0), dict(g='osm_jialing', color='river', width=6, alpha=0.95, at=0)]
DIST = [dict(g=k, color='hair', width=1.2, at=0) for k in ('d_nanan', 'd_shapingba', 'd_jiulongpo', 'd_dadukou', 'd_banan', 'd_beibei')]

def axis(stage):
    lay = DIST + [dict(g='d_yuzhong', color='brass', width=2.6, fill=0.30 if stage == 1 else 0.12, at=0)]
    mk, zn = [], []
    if stage >= 2:
        zn += [dict(p='guanyinqiao', rkm=1.5, label='관인차오', off=(0, -1), at=0 if stage > 2 else 1, color='brass' if stage == 2 else 'soft'),
               dict(p='nanping', rkm=1.5, label='난핑', off=(1.1, 0.6), at=0 if stage > 2 else 1, color='brass' if stage == 2 else 'soft'),
               dict(p='sanxia', rkm=1.5, label='사핑바', off=(0, -1), at=0 if stage > 2 else 1, color='brass' if stage == 2 else 'soft'),
               dict(p='yangjiaping', rkm=1.5, label='양자핑', off=(0, 1.1), at=0 if stage > 2 else 1, color='brass' if stage == 2 else 'soft')]
    if stage == 3:
        lay += [dict(g='d_liangjiang', color='brass', width=2.4, fill=0.14, at=0)]
        mk += [dict(p='jiangbeizui', label='장베이쭈이 금융가', at=1, off=(1, -0.4)), dict(p='lijia', label='리자', at=1, off=(-1, 0), anchor='rm'),
               dict(p='yuelai', label='웨라이', at=1), dict(p='ckg', label='장베이 공항', at=1, color='soft', lcolor='soft')]
    lay = lay + RIVERS_C
    mk += [dict(p='jiefangbei', label='제팡베이', at=0 if stage > 1 else 1, off=(1, 0.6), color='ink' if stage > 1 else 'brass')]
    stg = {1: ('①', '위중반도', '~1960년대'), 2: ('②', '강 건너편으로', '1966년 첫 시내 강 다리 이후'), 3: ('③', '북쪽 신도시 량장신구', '2010년~')}[stage]
    bnd = {1: (106.43, 29.49, 106.66, 29.63), 2: (106.38, 29.46, 106.67, 29.65), 3: CITY_B}[stage]
    return ('anim', 'map', dict(bounds=bnd, layers=lay, zones=zn, markers=mk, stage=stg))

LONG = [
  # ── Ⅰ 오프닝: 제목 + 실사 → 서울과 면적 비교
  dict(chap='Ⅰ   오프닝', loc='hongyadong', title=True, shots=[('clip', '39742350', 0)], lines=[
    ('밤이 되면 강가 절벽에 불이 켜지는 도시, 중국 충칭이에요.', None),
    ('충칭은 왜 이렇게 입체적인 도시가 됐을까요?', None)]),
  dict(chap='Ⅰ   오프닝', chapter='01  충칭은 얼마나 클까', attrib=OSM, note=SELF, shots=[('anim', 'overlay', dict(
      city='cq', compare='kor', city_label='충칭시', seoul_at=(106.55, 29.56), compare_at=(107.55, 30.05),
      compare_label='남한(같은 축척)', side=dict(title=('충칭시 면적', 0), big=('82,400㎢', 0), sub=('서울의 136배', 1), sub2=('남한 면적의 약 82%', 1))))], lines=[
    ('충칭시는 82,400㎢예요.', '충칭시는 팔만 이천사백 제곱킬로미터예요.'),
    ('서울의 136배, 남한 면적의 82%쯤이에요.', '서울의 백삼십육 배, 남한 면적의 팔십이 퍼센트쯤이에요.')]),
  # ── Ⅱ 숫자로 보는 충칭
  dict(chap='Ⅱ   숫자로 보는 충칭', chapter='02  숫자로 보는 충칭', shots=[('anim', 'numbers', dict(title='숫자로 보는 충칭', head=('충칭', '서울'), rows=[
      ('면적', '82,400㎢', '605㎢', True), ('인구(2025년 말)', '3,187만 명', '934만 명', False), ('중심 시가지 인구(2024)', '1,058만 명', '', False),
      ('도시화율', '73%', '', False), ('다리', '2만 개 이상', '', False), ('인천에서', '직항 약 4시간 · 시차 1시간', '', False)],
      src='출처: 충칭시 통계국 2025 통계공보 · 인민일보(2025.3) · 통계청(2025) · 항공권 검색(2026)'))], lines=[
    ('인구는 3,187만 명, 서울의 세 배가 넘어요.', '인구는 삼천백팔십칠만 명, 서울의 세 배가 넘어요.'),
    ('그중 중심 시가지에 사는 사람은 천만 명 남짓이에요.', None)]),
  # ── Ⅲ 두 강이 만든 도시
  dict(chap='Ⅲ   두 강이 만든 도시', chapter='03  두 강이 만든 도시', loc='chaotianmen', shots=[('clip', '39744311', 0)], lines=[
    ('충칭 한가운데에서 두 강이 만나요. 장강과 자링강이에요.', None),
    ('두 강이 만나는 끝, 빌딩 여덟 동이 선 곳이 차오톈먼이에요.', '두 강이 만나는 끝, 빌딩 여덟 동이 선 곳이 차오톈먼이에요.')]),
  dict(chap='Ⅲ   두 강이 만든 도시', attrib=OSM, note=SELF, shots=[('anim', 'map', dict(bounds=RIV_B, layers=DIST + [
      dict(g='d_yuzhong', color='brass', width=3, fill=0.30, at=0, d=0.3)] + RIVERS, markers=[dict(p='chaotianmen', label='차오톈먼', at=0, d=0.5), dict(p='jiefangbei', label='제팡베이', at=1, off=(-1, 0.8), anchor='rm')],
      side=dict(title=('위중반도', 0), big=('24㎢', 1), sub=('서울 종로구만 한 땅', 1))))], lines=[
    ('두 강 사이 혀처럼 튀어나온 땅, 위중반도에서 충칭이 시작됐어요.', None),
    ('면적은 24㎢, 서울 종로구만 해요.', '면적은 이십사 제곱킬로미터, 서울 종로구만 해요.')]),
  dict(chap='Ⅲ   두 강이 만든 도시', loc='hongyadong', shots=[('clip', '36149475', 12)], lines=[
    ('땅이 좁고 비탈지다 보니, 사람들은 절벽에 기둥을 세우고 집을 올렸어요.', None),
    ('이런 집을 댜오자오러우라고 해요. 훙야둥은 그 모습을 되살려 지은 거리예요.', None)]),
  dict(chap='Ⅲ   두 강이 만든 도시', loc='chaotianmen', shots=[('clip', '39742352', 3)], caption=dict(line=1, t1='1891', t2='내륙 도시 첫 개항'), lines=[
    ('강은 이 도시의 길이었어요. 장강 배길은 상하이까지 이어져요.', None),
    ('1891년, 충칭은 내륙 도시로는 처음 외국에 항구를 열었어요.', '천팔백구십일년, 충칭은 내륙 도시로는 처음 외국에 항구를 열었어요.')]),
  dict(chap='Ⅲ   두 강이 만든 도시', loc=(106.55, 29.56), shots=[('clip', '34766462', 4)], caption=dict(line=1, t1='1997', t2='네 번째 직할시'), lines=[
    ('1937년부터 1946년까지는 중화민국의 임시 수도였어요.', '천구백삼십칠년부터 천구백사십육년까지는 중화민국의 임시 수도였어요.'),
    ('1997년엔 베이징·상하이·톈진에 이어 네 번째 직할시가 됐어요.', '천구백구십칠년엔 베이징, 상하이, 톈진에 이어 네 번째 직할시가 됐어요.')]),
  # ── Ⅳ 주거축 이동 3단계
  dict(chap='Ⅳ   주거축 이동 3단계', chapter='04  주거축 이동 3단계', attrib=OSM, note=SELF, shots=[axis(1)], lines=[
    ('그럼 사람들은 어디에 살았을까요? 중심은 세 번 옮겨 갔어요.', None),
    ('첫 번째는 위중반도, 제팡베이 일대예요.', None)]),
  dict(chap='Ⅳ   주거축 이동 3단계', loc='jiefangbei', shots=[('clip', '36334237', 0)], lines=[
    ('좁은 반도에 상점과 관청, 집이 층층이 들어찼어요.', None)]),
  dict(chap='Ⅳ   주거축 이동 3단계', attrib=OSM, note=SELF, shots=[axis(2)], lines=[
    ('두 번째는 강 건너편, 1966년 첫 다리가 놓이면서예요.', '두 번째는 강 건너편, 천구백육십육년 첫 다리가 놓이면서예요.'),
    ('그 뒤로 관인차오, 난핑, 사핑바로 동네가 퍼졌어요.', None)]),
  dict(chap='Ⅳ   주거축 이동 3단계', loc=(106.587, 29.558), shots=[('clip', '34315157', 6)], lines=[
    ('지금은 중심 시가지에서 강을 건너는 다리만 38개예요.', '지금은 중심 시가지에서 강을 건너는 다리만 서른여덟 개예요.')]),
  dict(chap='Ⅳ   주거축 이동 3단계', attrib=OSM, note=SELF, shots=[axis(3)], lines=[
    ('세 번째는 북쪽 신도시예요. 2010년 량장신구가 생겼어요.', '세 번째는 북쪽 신도시예요. 이천십년 량장신구가 생겼어요.'),
    ('장베이쭈이 금융가와 리자, 웨라이에 새 아파트가 들어섰어요.', None)]),
  dict(chap='Ⅳ   주거축 이동 3단계', loc=(106.565, 29.565), shots=[('clip', '39745061', 0)], caption=dict(line=0, t1='352만', t2='량장신구 인구 · 2025년 개편'), lines=[
    ('2025년엔 장베이구, 위베이구와 합쳐 인구 352만 명의 구가 됐어요.', '이천이십오년엔 장베이구, 위베이구와 합쳐 인구 삼백오십이만 명의 구가 됐어요.')]),
  # ── Ⅴ 충칭 사람들이 사는 집
  dict(chap='Ⅴ   충칭 사람들이 사는 집', chapter='05  충칭 사람들이 사는 집', loc=(106.55, 29.56), shots=[('clip', '39718554', 2)], lines=[
    ('지금 충칭 사람 대부분은 산비탈에 선 고층 아파트에 살아요.', None),
    ('평지가 모자라니 위로 올린 거예요. 건물 사이가 아주 좁아요.', None)]),
  dict(chap='Ⅴ   충칭 사람들이 사는 집', loc='hongyadong', shots=[('clip', '39718785', 0), ('clip', '39724016', 8)], caption=dict(line=1, t1='1층 = 11층', t2='훙야둥 · 두 층 모두 길과 닿아요'), lines=[
    ('길이 산 중턱마다 나 있어서, 건물과 건물을 다리로 잇기도 해요.', None),
    ('11층짜리 훙야둥은 1층도 길, 11층도 길이에요.', '십일 층짜리 훙야둥은 일 층도 길, 십일 층도 길이에요.')]),
  # ── Ⅵ 충칭 사람들
  dict(chap='Ⅵ   충칭 사람들', chapter='06  충칭 사람들', loc='jiefangbei', shots=[('clip', '36437264', 4)], lines=[
    ('충칭시 사람 열 명 중 일곱은 도시에 살아요. 도시화율은 73%예요.', '충칭시 사람 열 명 중 일곱은 도시에 살아요. 도시화율은 칠십삼 퍼센트예요.'),
    ('인구는 3년째 조금씩 줄었지만, 밖에서 들어오는 사람은 오히려 늘었어요.', '인구는 삼 년째 조금씩 줄었지만, 밖에서 들어오는 사람은 오히려 늘었어요.')]),
  dict(chap='Ⅵ   충칭 사람들', loc='ciqikou', shots=[('clip', '39761550', 0), ('clip', '39750342', 1)], lines=[
    ('천 년 된 옛 거리 츠치커우엔 비 오는 날에도 사람이 몰려요.', None),
    ('저녁이면 골목마다 매운 훠궈와 길거리 음식 냄새가 퍼져요.', None)]),
  # ── Ⅶ 교통 인프라
  dict(chap='Ⅶ   교통 인프라', chapter='07  교통 인프라', loc='liziba', shots=[('clip', '38906655', 0)], caption=dict(line=1, t1='6~8층', t2='리쯔바역 · 19층 건물'), lines=[
    ('이 도시 교통의 상징은 건물을 뚫고 지나가는 모노레일이에요.', None),
    ('리쯔바역은 19층 건물의 6~8층에 있어요. 위로는 집, 아래로는 상가예요.', '리쯔바역은 십구 층 건물의 육 층부터 팔 층에 있어요. 위로는 집, 아래로는 상가예요.')]),
  dict(chap='Ⅶ   교통 인프라', loc='liziba', shots=[('clip', '39718215', 1)], lines=[
    ('산이 많아서, 가파른 비탈과 급한 곡선을 잘 타는 모노레일을 깔았어요.', None)]),
  dict(chap='Ⅶ   교통 인프라', shots=[('anim', 'card', dict(title='충칭의 길', items=[('583km', '도시철도(2025년 말)', 0), ('98km', '그중 모노레일', 0), ('2만 개+', '다리', 1), ('15호선', '2026년 11월 개통 · 무인 급행', 1)],
      src='출처: 중국도시궤도교통협회(2026.1) · 인민일보(2025.3) · 신화통신(2026.11)'))], lines=[
    ('도시철도는 583km, 그중 모노레일이 98km예요.', '도시철도는 오백팔십삼 킬로미터, 그중 모노레일이 구십팔 킬로미터예요.'),
    ('다리는 2만 개가 넘어요.', '다리는 이만 개가 넘어요.')]),
  dict(chap='Ⅶ   교통 인프라', loc=(106.565, 29.57), shots=[('clip', '35439686', 10)], lines=[
    ('장강과 자링강을 건너는 큰 다리만 105개, 그래서 충칭을 다리의 도시라고도 불러요.', '장강과 자링강을 건너는 큰 다리만 백다섯 개, 그래서 충칭을 다리의 도시라고도 불러요.')]),
  # ── Ⅷ 한국과의 연결
  dict(chap='Ⅷ   한국과의 연결', chapter='08  한국과의 연결', attrib=OSM, note=SELF, shots=[('anim', 'route', dict(bounds=(103.5, 21.8, 123.5, 33.4), span=4.6, start_at=1,
      stops=[('shanghai', '상하이', '1919'), ('hangzhou', '항저우', '1932'), ('zhenjiang', '전장', '1935'), ('changsha', '창사', '1937'), ('guangzhou', '광저우', '1938'),
             ('liuzhou', '류저우', '1938'), ('qijiang', '치장', '1939'), ('lianhuachi', '충칭', '1940')],
      offsets={'충칭': (-1, -0.9), '치장': (-1, 0.6), '항저우': (1, 0.6), '전장': (1, -0.6)},
      side=dict(title=('대한민국 임시정부', 0), big=('1940', 1), sub=('충칭 도착 · 일곱 번째 이동', 1))))], lines=[
    ('충칭은 한국 역사와도 이어져 있어요.', None),
    ('1919년 상하이에서 시작한 대한민국 임시정부는 일곱 번 자리를 옮겨 1940년 충칭에 닿았어요.', '천구백십구년 상하이에서 시작한 대한민국 임시정부는 일곱 번 자리를 옮겨, 천구백사십년 충칭에 닿았어요.')]),
  dict(chap='Ⅷ   한국과의 연결', loc='lianhuachi', shots=[('clip', '36432123', 3)], caption=dict(line=0, t1='1940–1945', t2='대한민국 임시정부 충칭 시기'), lines=[
    ('임시정부는 이곳에서 광복군을 만들었고, 1945년 11월까지 머물렀어요.', '임시정부는 이곳에서 광복군을 만들었고, 천구백사십오년 십일월까지 머물렀어요.'),
    ('마지막 청사는 지금 기념관이 되어 위중구 시내에 남아 있어요.', None)]),
  dict(chap='Ⅷ   한국과의 연결', loc='chaotianmen', shots=[('clip', '34315150', 2)], lines=[
    ('한국 기업도 왔어요. SK하이닉스는 2014년부터 이곳에서 반도체 후공정 공장을 돌려요.', '한국 기업도 왔어요. 에스케이하이닉스는 이천십사년부터 이곳에서 반도체 후공정 공장을 돌려요.'),
    ('현대차는 충칭에 공장을 지었다가 2024년에 팔았어요.', '현대차는 충칭에 공장을 지었다가 이천이십사년에 팔았어요.')]),
  # ── Ⅸ 한국에서 가는 법
  dict(chap='Ⅸ   한국에서 가는 법', chapter='09  한국에서 가는 법', attrib=OSM, note=SELF, shots=[('anim', 'flight', dict(bounds=(102.0, 26.5, 129.0, 39.5), dest='ckg', dest_label='충칭 장베이 공항',
      side=dict(title=('인천 → 충칭', 0), big=('약 4시간', 0), sub=('직항 · 돌아올 땐 약 3시간 반', 0), sub2=('시차 1시간(한국보다 늦음)', 0))))], lines=[
    ('인천에서 충칭까지는 직항으로 4시간쯤 걸려요. 시차는 1시간이에요.', '인천에서 충칭까지는 직항으로 네 시간쯤 걸려요. 시차는 한 시간이에요.')]),
  dict(chap='Ⅸ   한국에서 가는 법', loc=(106.587, 29.558), end=True, shots=[('clip', '34315158', 22)], lines=[
    ('한국인은 올해 12월 31일까지 비자 없이 30일 머물 수 있어요. 내년 연장은 아직 발표 전이에요.', '한국인은 올해 십이월 삼십일일까지 비자 없이 삼십 일 머물 수 있어요. 내년 연장은 아직 발표 전이에요.'),
    ('두 강과 산이 만든 입체 도시, 충칭이었어요.', None)]),
]

# ───────── 쇼츠 (B안 리얼 생생, 1080×1920). hl = 자막에서 황동색으로 칠할 말
S1 = [
  dict(tag='충칭 · 훙야둥', loc='hongyadong', shots=[('clip', '39742350', 2)], lines=[('이 도시, 서울보다 얼마나 클까요?', None, '서울보다')]),
  dict(tag='충칭시 · 서울 같은 축척', attrib=OSM, shots=[('anim', 'overlay', dict(city='cq', compare=None, city_label='충칭시', seoul_at=(106.55, 29.56),
      side=dict(big=('136배', 1), sub=('충칭시 82,400㎢ · 서울 605㎢', 1))))], lines=[
      ('충칭시 면적은 82,400㎢.', '충칭시 면적은 팔만 이천사백 제곱킬로미터.', '82,400㎢'), ('서울의 136배예요.', '서울의 백삼십육 배예요.', '136배')]),
  dict(tag='충칭 시가지', loc=None, shots=[('clip', '34766462', 6)], sticker=dict(line=0, delay=0.5, t1='남한의 82%', t2='충칭시 면적'), lines=[
      ('남한 면적의 82%쯤 되는 크기예요.', '남한 면적의 팔십이 퍼센트쯤 되는 크기예요.', '82%')]),
  dict(tag='제팡베이 거리', loc='jiefangbei', shots=[('clip', '36437264', 6)], bubble=dict(line=0, t1='3,187만 명', t2='2025년 말 상주인구'), lines=[
      ('사는 사람도 3,187만 명, 서울의 세 배가 넘어요.', '사는 사람도 삼천백팔십칠만 명, 서울의 세 배가 넘어요.', '세 배')]),
  dict(tag='차오톈먼 · 두 강이 만나는 곳', loc='chaotianmen', shots=[('clip', '39744311', 1)], lines=[
      ('그런데 시가지는 두 강 사이 좁은 언덕에 몰려 있어요.', None, '좁은 언덕'), ('그래서 건물이 위로, 또 위로 올라갔어요.', None, '위로')]),
  dict(tag='충칭 고층 아파트', loc=None, end=True, shots=[('clip', '39718554', 4)], lines=[('충칭이 왜 8D 도시가 됐는지는 본편에서 이어 볼게요.', '충칭이 왜 입체 도시가 됐는지는 본편에서 이어 볼게요.', '8D 도시')]),
]
S2 = [
  dict(tag='리쯔바역 · 2호선', loc='liziba', shots=[('clip', '38906655', 2)], lines=[('열차가 아파트 건물 속으로 들어가요.', None, '건물 속으로')]),
  dict(tag='리쯔바역 · 충칭', loc='liziba', shots=[('clip', '39718215', 0)], lines=[('중국 충칭의 리쯔바역이에요.', None, '리쯔바역'), ('역이 19층 건물 안에 있어요.', '역이 십구 층 건물 안에 있어요.', '19층 건물')]),
  dict(tag='', shots=[('anim', 'stack', dict(title='리쯔바역 건물', floors=19, segs=[(1, 5, '상가·사무실', 'soft'), (6, 8, '역(대합실·설비·승강장)', 'brass'), (9, 19, '집', 'ink')],
      train=dict(floor=8)))], lines=[('1~5층은 상가, 6~8층은 역, 9층부터 19층까지는 집이에요.', '일 층부터 오 층은 상가, 육 층부터 팔 층은 역, 구 층부터 십구 층까지는 집이에요.', '6~8층은 역')]),
  dict(tag='리쯔바역 곡선 구간', loc='liziba', shots=[('clip', '29682593', 4)], lines=[
      ('왜 이렇게 지었을까요? 선로를 돌리는 것보다 비용이 덜 들었거든요.', None, '비용'), ('역과 건물은 1998년에 함께 설계됐어요.', '역과 건물은 천구백구십팔년에 함께 설계됐어요.', '함께 설계')]),
  dict(tag='둥수이먼 대교', loc=None, shots=[('clip', '34315157', 8)], sticker=dict(line=0, delay=1.2, t1='모노레일 98km', t2='2025년 말 기준'), lines=[
      ('산이 많은 충칭은 비탈을 잘 오르는 모노레일을 98km나 깔았어요.', '산이 많은 충칭은 비탈을 잘 오르는 모노레일을 구십팔 킬로미터나 깔았어요.', '98km')]),
  dict(tag='충칭의 밤 다리', loc=None, end=True, shots=[('clip', '35439686', 12)], lines=[('다리도 2만 개가 넘어요. 그래서 충칭을 입체 도시라고 불러요.', '다리도 이만 개가 넘어요. 그래서 충칭을 입체 도시라고 불러요.', '입체 도시')]),
]

# 설명란·글에 쓰는 숫자 출처
SOURCES = [
    ('충칭시 통계국·국가통계국 충칭조사총대, 「2025년 충칭시 국민경제·사회발전 통계공보」(2026.3.26) — 상주인구 3,187.26만 명, 도시화율 73.02%', 'https://cbgc.scol.com.cn/news/7427946'),
    ('제일재경, 「충칭 중심 시가지 상주인구 1,058.46만 명(2024)」(2026.2.26)', 'https://www.yicai.com/news/103061163.html'),
    ('중국도시궤도교통협회, 「2025년 중국 내륙 도시궤도교통 노선 개황」(2026.1.1) — 충칭 582.60km, 모노레일 98.45km', 'https://infosharingp2-oss.camet.org.cn/resources/manual/2026/01/04/759313381470277.pdf'),
    ('신화통신, 「충칭 첫 무인 운행 도시궤도 급행선 개통」(2026.11.12)', 'https://www.news.cn/politics/20261112/f6bf4014321d42f996cb50c8647a8533/c.html'),
    ('인민일보, 「충칭 다리 2만 개 이상, 장강·자링강 횡단 특대교 105개」(2025.3.31)', 'https://www.peopleapp.com/column/30048662518-500006173780'),
    ('충칭상보, 「2024 충칭 중심 시가지 교통발전 연보 — 강 횡단 다리 38개」(2025.7.23)', 'https://epaper.cqcb.com/attachment/202507/23/108968de-b8a9-45a9-83d3-9514d9f1b58b.pdf'),
    ('충칭일보, 「1966년 1월 시내 첫 강 횡단 다리(뉴자오퉈 자링강대교) 개통」(2021.7.1)', 'https://epaper.cqrb.cn/html/cqrb/2021-07/01/039/cqrb20210701039.pdf'),
    ('국민경략(후시우), 「량장신구·장베이구·위베이구 통합, 면적 약 1,360㎢·인구 약 352만」(2025.11.10)', 'https://www.huxiu.com/article/4802987.html'),
    ('중국신문망, 「리쯔바역 설계자 인터뷰 — 1~5층 상가, 6~8층 역, 9~19층 주거, 1998년 설계」(2018.5.25)', 'https://cs.com.cn/fdc/201805/t20180525_5812252.html'),
    ('씨트립, 「훙야둥 11층·높이 79m, 1층과 11층 모두 도로에 접함」', 'https://gs.ctrip.com/html5/you/travels/158/3958583.html'),
    ('위키피디아, Chongqing — 1891년 내륙 첫 개항, 1937.11~1946.5 임시 수도', 'https://en.wikipedia.org/wiki/Chongqing'),
    ('위키피디아(광둥어), 重慶 — 1189년 충칭부 이름, 1997년 직할시', 'https://wikiwand.com/zh-yue/重慶'),
    ('윈상왕, 「충칭 상권 발전사 — 2003년 싼샤광장·양자핑·난핑 상권」', 'https://m.winshang.com/news664025.html'),
    ('제일재경, 「충칭 2025년 인구 3.21만 명 감소, 순유입 11.49만 명」(2026.3.26)', 'https://www.yicai.com/news/103105770.html'),
    ('메이구, 「훙야둥 — 2006년 충칭시 정부 3.85억 위안 투자, 11층」', 'https://m.maigoo.com/citiao/113907.html'),
    ('KAYAK, 인천–충칭 왕복 항공권 검색(2026)', 'https://www.kayak.co.kr/항공권/대한민국-KR0/충칭-Chongqing-CKG'),
    ('서울신문, 「대한민국 임시정부 100년 — 충칭 정착, 1945년 11월 귀국」(2019.2.14)', 'https://m.seoul.co.kr/news/2019/02/14/20190214008001'),
    ('경향신문, 「1940년 9월 17일 충칭에서 한국광복군 창설」(2018.9.4)', 'https://www.khan.co.kr/article/201809040600035/amp'),
    ('머니투데이방송, 「SK하이닉스 충칭 공장(2014년 7월 양산) 지분 매각 검토」(2026.8.9)', 'https://news.mtn.co.kr/news-detail/2026080909254140636'),
    ('다음뉴스, 「Hyundai Motor Group sells Chongqing factory」(2024.1.17)', 'https://v.daum.net/v/20240117112401433'),
    ('한국경제, 「중국 무비자 2026년 12월 31일까지 연장」(2025.11.3) · 연합뉴스(2026.11.17) 연장 여부 미발표', 'https://www.hankyung.com/article/202511031390i'),
    ('호텔스컴바인·KAYAK, 인천–충칭 직항 약 4시간 5분(돌아오는 편 약 3시간 35분)', 'https://www.hotelscombined.co.kr/flight-routes/Seoul-SEL/Chongqing-Jiangbei-Intl-CKG.ksp'),
]
TAGS = ['충칭', '중경', 'Chongqing', '도시이야기', '8D도시', '훙야둥', '리쯔바역', '모노레일', '장강', '자링강', '대한민국임시정부', '중국여행', '중국무비자', '도시구조', '브동산']
