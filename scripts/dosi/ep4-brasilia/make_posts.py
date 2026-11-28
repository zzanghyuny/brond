# -*- coding: utf-8 -*-
"""브라질리아 편 사이트 글 + 네이버용 HTML + 이미지. 사용: python3 make_posts.py
사이트 글(평서문, 장 순서 = 영상 흐름)과 네이버용(해요체, 한눈에 표 → 비행기 모양이 된 이유 3가지 → 꼭 보는 장면 4곳 → 주거 이동 표 → 숫자 표 → 한국과의 인연 → 가는 법 체크리스트)은
내용은 같고 구성은 절반 이상 다르게 만든다. 구글 어스 캡처는 본문 사진으로만 쓰고(출처 표기) 표지에는 쓰지 않는다.
"""
import os, sys, json, subprocess, html, importlib.util
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); LIB = os.path.join(HERE, '..', 'lib'); sys.path.insert(0, LIB)
import dosi_gfx as gfx
spec = importlib.util.spec_from_file_location('script', os.path.join(HERE, 'script.py')); S = importlib.util.module_from_spec(spec); spec.loader.exec_module(S)
EP = S.EP; GEO = json.load(open(EP['geo'])); REPO = '/home/claude/brond/'
SLUG = 'brasilia-city-structure'; IMG = REPO + f'posts/images/{SLUG}/'; os.makedirs(IMG, exist_ok=True)
URL = f'https://www.brandongsan.com/posts/{SLUG}.html'; IMGURL = f'https://www.brandongsan.com/posts/images/{SLUG}/'
DATE, DATEL = '2026-11-28', '2026. 11. 28'; TAG = '도시이야기 No.004'
TITLE = '브라질리아는 왜 비행기 모양일까 — 41개월 만에 세운 수도'
NTITLE = '브라질리아 비행기 도시 총정리 | 41개월 만에 세운 수도, 50만 명 계획에 300만 명, 한국에서 가는 법까지'
OUTN = EP['work'] + 'naver/'; os.makedirs(OUTN, exist_ok=True)

def save_pair(im, name):
    im.resize((1600, int(1600 * im.height / im.width)), Image.LANCZOS).save(IMG + name + '.jpg', quality=82, optimize=True)
    n = im.resize((1000, int(1000 * im.height / im.width)), Image.LANCZOS); q = 82
    while True:
        n.save(IMG + name + '-n.jpg', quality=q, optimize=True)
        if os.path.getsize(IMG + name + '-n.jpg') <= 400_000 or q <= 60: break
        q -= 6
def photo(clip, t, name):
    raw = EP['work'] + f'post_{clip}_{t}.png'
    if not os.path.exists(raw): subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(t), '-i', EP['px'] + f'px_{clip}.mp4', '-frames:v', '1', raw], check=True)
    save_pair(Image.open(raw).convert('RGB'), name)
PHOTOS = dict(cover=('35691250', 6), catedral_air=('19141615', 8), esplanada=('35703751', 8), esplanada2=('35691266', 20), ministerios=('30360356', 10),
              congresso=('30179032', 4), catedral=('31711540', 4), torre=('29192349', 10), ponte=('10125425', 8), ponte_sun=('30377363', 12), lake=('20256708', 8),
              sqs=('27902849', 4), stadium=('27956912', 10), run=('27902485', 6), aguas=('32269840', 10), road=('34181001', 2), itamaraty=('5539902', 3),
              jk=('35703753', 20), aerial_end=('35703754', 10), cong_reflect=('30179035', 4))
for k, (c, t) in PHOTOS.items(): photo(c, t, k)
GE = '/home/claude/media/gearth_bsb/'
for k in ('g1_overview', 'g3_superquadra', 'g4_ponte_jk3d', 'g5_ceilandia', 'g6_aguas_claras3d', 'g7_region', 'g8_congresso3d', 'g9_eixo3d'):
    save_pair(Image.open(GE + k + '.jpg').convert('RGB'), 'ge-' + k.split('_', 1)[1].replace('_', '-'))

MAPS = {}
for i, s in enumerate(S.LONG):
    for sh in s['shots']:
        if sh[0] == 'anim':
            o = sh[2]; key = {'overlay': 'map-size', 'numbers': 'numbers', 'card': None}.get(sh[1], None)
            if sh[1] == 'map':
                key = f"map-axis-{ {'①': 1, '②': 2, '③': 3}[o['stage'][0]] }" if 'stage' in o else 'map-plan'
            if key: MAPS[key] = (sh[1], o)
def render_last(name, o, W, H, short, ui, out):
    gfx.UI = ui; gfx.FPS = 2; last = None
    for fr in gfx.frames(name, W, H, 9.0, [0.4, 3.0], o, GEO, short): last = fr
    Image.frombytes('RGB', (W, H), last).save(out, quality=86, optimize=True)
for key, (name, o) in MAPS.items():
    if key == 'numbers': continue
    render_last(name, o, 1920, 804, False, 1.0, IMG + key + '.jpg')
    if key == 'map-plan': o = dict(o, side=None)
    render_last(name, o, 1000, 1400, True, 1.35, IMG + key + '-n.jpg')
gfx.UI = 1.0
print('images', len(os.listdir(IMG)))

# ---------------- 공통 조각
def esc(x): return html.escape(x, quote=True)
def img(name, alt, cap=None, naver=False):
    src = (IMGURL + name + '-n.jpg') if naver else f'images/{SLUG}/{name}.jpg'
    if naver:
        c = f'<p style="color:#8A8A8A;font-size:13px;">{cap}</p>' if cap else ''
        return f'<img src="{src}" alt="{esc(alt)}" style="width:100%;display:block;">{c}'
    c = f'<div class="cap">{cap}</div>' if cap else ''
    return f'<div class="photo-block"><img src="{src}" alt="{esc(alt)}" loading="lazy" style="width:100%;display:block;">{c}</div>'
SRC_LIST = '\n'.join(f'<li>{esc(t)} — <a href="{esc(u)}" target="_blank" rel="noopener">{esc(u)}</a></li>' for t, u in S.SOURCES)
PX = '영상 캡처 Pexels'
GEC = '위성·3D 화면 Google Earth(2024 이미지)'
MAPCAP = '브동산 자체 제작 개략도 · 지도 © OpenStreetMap contributors · Natural Earth · 실제 경계·축척과 다를 수 있음'

# ---------------- 사이트 글
tmpl = open(REPO + 'posts/mexico-city-city-structure.html', encoding='utf-8').read()
head = tmpl[:tmpl.find('<title>')]
style = tmpl[tmpl.find('<style>'):tmpl.find('</head>')]
foot = tmpl[tmpl.find('<footer>'):]
DESC = '브라질리아는 1956년부터 41개월 만에 텅 빈 내륙 고원에 세운 계획 수도다. 하늘에서 보면 비행기 모양인 이유, 6층 슈퍼쿼드라와 위성 도시, 50만 명 계획에 300만 명이 사는 지금, 한국과의 인연과 가는 법까지 정리했다.'
RELATED = '''<section id="related">
  <h2>도시이야기의 다른 포스팅</h2>
  <div class="related-list"><a class="related-item" href="mexico-city-city-structure.html"><span class="r-tag">도시이야기 No.003</span><span class="r-title">멕시코시티는 왜 가라앉을까 — 호수를 메워 세운 도시 700년</span></a><a class="related-item" href="chongqing-city-structure.html"><span class="r-tag">도시이야기 No.002</span><span class="r-title">충칭은 왜 8D 도시가 됐을까 — 두 강과 산이 만든 입체 도시</span></a><a class="related-item" href="hcmc-city-structure.html"><span class="r-tag">도시이야기 No.001</span><span class="r-title">호치민은 왜 이런 모양이 됐을까 — 강을 따라 자란 도시 300년</span></a></div>
  <div class="list-more"><a class="btn-list" href="https://brandongsan.com/city-story.html">도시이야기 목록 전체보기</a></div>
</section>'''
body = f'''<body>
<div class="top-eyebrow"><div class="wrap"><a class="brand-mark" href="https://brandongsan.com/"><span class="bm-b">브</span><span class="bm-rest">동산</span></a><a class="list-btn" href="https://brandongsan.com/city-story.html">☰ 목록</a></div></div>
<div class="wrap">
  <div class="titleblock"><h1>{TITLE}</h1></div>
  <div class="byline"><span class="avatar">브</span><span class="who">서당개</span><span class="dot">·</span><span class="when">{DATEL}</span><span class="tag">{TAG}</span></div>
</div>
<div class="hairline"></div>
<div class="content"><div class="wrap">

{img('cover', '브라질리아 대성당과 기념축 일대를 드론으로 내려다본 모습', '기념축과 대성당 · ' + PX)}
<section><p class="lede">브라질리아는 해발 1,172m 고원에 있는 브라질의 수도다. 하늘에서 보면 이 도시는 비행기 모양이다. 가운데 긴 몸통이 있고, 양쪽으로 휜 날개가 뻗어 있다. 사람이 거의 살지 않던 땅에 왜, 어떻게 이런 도시가 생겼을까?</p></section>

<section><h2>1. 서울의 9.5배, 인구는 300만 명</h2>
<p>수도 브라질리아가 있는 연방구(Distrito Federal)의 면적은 5,760㎢로 서울(605㎢)의 9.5배쯤이다. 연방구 전체가 사실상 하나의 시이고, 행정구역(região administrativa)은 35곳이다. 2022년 인구조사 인구는 282만 명, 2025년 추정 인구는 약 300만 명이다.</p>
{img('map-size', '연방구 경계 위에 서울을 같은 축척으로 겹쳐 본 지도', '같은 축척으로 겹쳐 본 연방구(황동색)와 서울(흰색) · ' + MAPCAP)}
<div class="tbl-wrap"><table class="rule"><thead><tr><th>항목</th><th>브라질리아(연방구)</th><th>서울</th></tr></thead><tbody>
<tr><td>면적</td><td>5,760㎢</td><td>605㎢</td></tr>
<tr><td>인구</td><td>약 300만 명(2025 추정)</td><td>934만 명</td></tr>
<tr><td>그중 플라누 필로투</td><td>22만 명(2021)</td><td>—</td></tr>
<tr><td>해발 고도</td><td>1,172m</td><td>—</td></tr>
<tr><td>수도가 된 해</td><td>1960년</td><td>—</td></tr>
</tbody></table></div>
<p class="note">출처: IBGE(면적·2022 인구조사·2025 추정), IPEDF PDAD 2021, 통계청(서울 인구)</p>
<p>눈여겨볼 숫자는 마지막에서 두 번째 줄이다. 하늘에서 보이는 비행기 모양 안, 원래 계획한 도시(플라누 필로투)에 사는 사람은 22만 명뿐이다.</p>
</section>

<section><h2>2. 텅 빈 고원에 세운 수도</h2>
<p>1950년대까지 브라질의 수도는 대서양 바닷가의 리우데자네이루였다. 1956년 취임한 주셀리누 쿠비체크 대통령은 나라 한가운데의 텅 빈 고원에 새 수도를 짓기로 했다. 해안에만 몰린 사람과 돈을 내륙으로 끌어들이겠다는 계획이었다.</p>
{img('ge-region', '위에서 본 연방구와 파라노아 호수 일대 위성사진', '위에서 본 브라질리아와 주변 · ' + GEC)}
<p>1957년 도시 계획 공모에서 뽑힌 것은 루시우 코스타의 안이었다. 그는 손 스케치 15장과 짧은 설명만 냈는데, 출발점은 '어떤 자리를 표시하는 몸짓', 곧 두 축이 직각으로 만나는 십자였다. 지형에 맞춰 한 축을 활처럼 휘게 그리자 하늘에서 보면 비행기(또는 잠자리)처럼 보이는 모양이 됐다.</p>
{img('map-plan', '기념축과 주거축이 만나는 플라누 필로투 개략도', '플라누 필로투의 두 축(개략) · ' + MAPCAP)}
{img('ge-overview', '위에서 본 플라누 필로투 위성사진', '위에서 본 플라누 필로투 · ' + GEC)}
<p>공사는 1956년에 시작했다. 41개월 뒤인 1960년 4월 21일, 새 수도가 문을 열었다. 1987년 유네스코는 플라누 필로투를 세계유산으로 올렸다.</p>
{img('esplanada', '기념축과 부처 청사를 드론으로 내려다본 모습', '기념축 · ' + PX)}
</section>

<section><h2>3. 비행기의 몸통, 기념축</h2>
<p>몸통은 기념축(에이슈 몬누멘타우)이다. 넓은 잔디 광장 양쪽으로 큰 길이 달리고, 그 옆에 똑같이 생긴 부처 청사가 줄지어 서 있다. 정부 건물은 대부분 건축가 오스카르 니에메예르가 설계했다.</p>
{img('ge-eixo3d', '기념축을 비스듬히 내려다본 3D 지도', '기념축(앞)과 TV 타워 쪽 · ' + GEC)}
{img('ministerios', '기념축 양옆의 부처 청사', '부처 청사 · ' + PX)}
<p>조종석 자리에는 국회가 있다. 쌍둥이 빌딩과 위로 열린 접시, 엎은 접시 모양의 지붕이 상원·하원이다. 그 앞이 대통령궁(플라날투궁)과 대법원이 마주 보는 3권 광장이다.</p>
{img('congresso', '쌍둥이 빌딩과 접시 모양 지붕의 국회의사당', '국회의사당 · ' + PX)}
{img('ge-congresso3d', '국회와 3권 광장을 비스듬히 내려다본 3D 지도', '국회와 3권 광장 · ' + GEC)}
<p>왕관처럼 생긴 메트로폴리탄 대성당도 이 길 위에 있다. 두 축이 만나는 곳에는 버스터미널이 있고, 그 서쪽에 TV 타워가 서 있다.</p>
{img('catedral', '왕관 모양의 브라질리아 대성당', '메트로폴리탄 대성당 · ' + PX)}
{img('torre', '밤에 붉게 빛나는 TV 타워', '밤의 TV 타워 · ' + PX)}
</section>

<section><h2>4. 만든 호수, 파라노아</h2>
<p>도시를 감싼 파라노아 호수도 사람이 만들었다. 1959년 9월 파라노아강에 댐을 막아 넓이 48㎢, 최대 수심 38m의 호수가 생겼다. 건조한 고원 도시에 습기를 더하고 쉴 곳을 만들려는 목적이었다.</p>
{img('ge-ponte-jk3d', '파라노아 호수와 JK 다리를 비스듬히 내려다본 3D 지도', '파라노아 호수와 JK 다리 · ' + GEC)}
{img('ponte', '호수 위 아치 세 개가 이어진 JK 다리', 'JK 다리 · ' + PX)}
<p>호숫가에는 대통령 관저(알보라다궁)와 넓은 단독주택 동네(라구 술·라구 노르치)가 들어섰다.</p>
{img('lake', '파라노아 호숫가를 드론으로 내려다본 모습', '파라노아 호숫가 · ' + PX)}
</section>

<section><h2>5. 비행기의 날개, 슈퍼쿼드라</h2>
<p>날개(아자 노르치·아자 술)에는 사람들이 사는 아파트 단지, 슈퍼쿼드라가 줄지어 있다. 나무가 빽빽한 큰 블록 안에 6층 이하 아파트가 1층을 비운 기둥(필로티) 위에 서 있다. 1층이 비어 있으니 누구나 단지 사이를 걸어서 지나갈 수 있다.</p>
{img('ge-superquadra', '위에서 본 아자 술의 슈퍼쿼드라', '위에서 본 슈퍼쿼드라 · ' + GEC)}
<p>슈퍼쿼드라 네 개가 학교·상점·교회를 함께 쓰는 한 동네(이웃 단위)가 되도록 설계됐다. 남쪽 날개의 308 술 쿼드라는 처음 계획을 가장 잘 보여 주는 '모델 쿼드라'로 불린다.</p>
{img('sqs', '나무 사이의 슈퍼쿼드라 아파트와 길', '슈퍼쿼드라 · ' + PX)}
</section>

<section><h2>6. 비행기 밖으로 — 주거축 3단계</h2>
<h3>① 비행기 안, 플라누 필로투 · 1960년~</h3>
<p>플라누 필로투는 50만 명이 살 도시로 계획됐다. 하지만 수도를 지으러 온 노동자(칸당구)들은 처음부터 도시 밖에 자리를 잡았다.</p>
{img('map-axis-1', '1단계: 플라누 필로투를 표시한 개략도', '①단계 · ' + MAPCAP)}
<h3>② 서쪽 위성 도시 · 1958·1971년~</h3>
<p>1958년 서쪽에 타구아팅가가 생겼다. 1971년에는 도심 가까운 판자촌 주민을 옮기는 '판자촌 철거 캠페인(Campanha de Erradicação de Invasões, CEI)'의 이름을 딴 세일란지아가 세워졌다. 지금 세일란지아에는 28만 7천 명(2022 인구조사)이 살아 연방구에서 가장 사람이 많다.</p>
{img('map-axis-2', '2단계: 타구아팅가와 세일란지아를 표시한 개략도', '②단계 · ' + MAPCAP)}
{img('ge-ceilandia', '위에서 본 세일란지아의 촘촘한 주택가', '위에서 본 세일란지아 · ' + GEC)}
<h3>③ 고층 아파트 도시 · 2000년대~</h3>
<p>2003년 타구아팅가에서 떨어져 나온 아과스 클라라스는 6층으로 묶인 플라누 필로투와 반대로 20층, 30층 아파트가 숲처럼 섰다. 9.2㎢에 12만 8천 명, 1㎢에 1만 4천 명이 사는 연방구에서 가장 빽빽한 동네다.</p>
{img('map-axis-3', '3단계: 아과스 클라라스를 표시한 개략도', '③단계 · ' + MAPCAP)}
{img('ge-aguas-claras3d', '아과스 클라라스의 고층 아파트를 비스듬히 내려다본 3D 지도', '아과스 클라라스 · ' + GEC)}
{img('aguas', '고층 아파트가 빽빽한 거리', '고층 아파트 동네 · ' + PX)}
</section>

<section><h2>7. 브라질리아 사람들</h2>
<p>일자리는 여전히 비행기 안에 몰려 있다. 2021년 연방구 조사(PDAD)에서 일하는 사람의 40.7%가 플라누 필로투로 출근했다. 2024년 조사에서는 34.4%로 줄었다. 위성 도시가 스스로 일자리를 키우고 있다는 뜻이다.</p>
{img('run', '기념축을 가득 메운 마라톤 참가자들', '기념축의 마라톤 · ' + PX)}
{img('stadium', '마네 가힌샤 경기장을 드론으로 내려다본 모습', '마네 가힌샤 경기장 · ' + PX)}
</section>

<section><h2>8. 교통 인프라</h2>
<p>도시는 자동차를 기준으로 설계됐다. 신호등 대신 입체 교차로가 많고, 2021년 조사에서 출근하는 사람의 52% 넘게 자가용을 탔다.</p>
{img('road', '넓은 도로를 달리는 차들', '브라질리아의 도로 · ' + PX)}
<div class="tbl-wrap"><table class="rule"><thead><tr><th>항목</th><th>내용</th></tr></thead><tbody>
<tr><td>지하철</td><td>1개 노선이 두 갈래(세일란지아·사맘바이아) · 42.38km · 운행 역 27개 · 하루 약 14만 명</td></tr>
<tr><td>연장 공사</td><td>사맘바이아 3.6km(2025.2 착공), 세일란지아 2.3km</td></tr>
<tr><td>출근 수단</td><td>자가용 52% 이상(2021)</td></tr>
</tbody></table></div>
<p class="note">출처: Metrô-DF 자료(연방구 의회, 2025), Correio Braziliense(2026.6), PDAD 2021</p>
</section>

<section><h2>9. 한국과의 연결</h2>
<p>한국과 브라질은 1959년 10월 31일, 브라질리아가 문을 열기 몇 달 전에 수교했다. 브라질은 중남미에서 한국과 처음 수교한 나라다. 1962년 12월 18일 부산항을 떠난 첫 이민단 103명이 이듬해 2월 산투스항에 닿았고, 지금 브라질의 한인은 5만 명이 넘는다. 브라질리아에는 기념축 북쪽 대사관 거리에 주브라질 한국 대사관이 있다.</p>
{img('itamaraty', '브라질 외교부 이타마라치궁', '브라질 외교부(이타마라치궁) · ' + PX)}
</section>

<section><h2>10. 한국에서 가는 법</h2>
<div class="tbl-wrap"><table class="rule"><thead><tr><th>항목</th><th>내용</th></tr></thead><tbody>
<tr><td>비행</td><td>직항 없음 · 보통 2회 경유(중동·유럽·북미 경유 후 상파울루 등) · 약 35시간</td></tr>
<tr><td>시차</td><td>한국보다 12시간 늦다</td></tr>
<tr><td>비자</td><td>한국 여권 관광·출장 90일 무비자, 돌아가는 항공권 필요</td></tr>
</tbody></table></div>
<p class="note">출처: KAYAK 노선 정보, 스카이스캐너 비자 안내(2026.11 조회). 출국 전 주한 브라질 대사관 공지를 다시 확인하자.</p>
{img('aerial_end', '해 질 녘 브라질리아 시가지를 드론으로 내려다본 모습', '브라질리아 · ' + PX)}
</section>

<section><h2>11. 정리</h2>
<div class="tbl-wrap"><table class="rule"><thead><tr><th>연도</th><th>일어난 일</th><th>도시 모양으로 보면</th></tr></thead><tbody>
<tr><td>1956</td><td>새 수도 공사 시작</td><td>텅 빈 고원</td></tr>
<tr><td>1957</td><td>루시우 코스타 계획 당선</td><td>십자 → 비행기 모양</td></tr>
<tr><td>1958</td><td>타구아팅가</td><td>첫 위성 도시</td></tr>
<tr><td>1959</td><td>파라노아 호수 · 한국과 수교</td><td>만든 호수</td></tr>
<tr><td>1960.4.21</td><td>수도 개막</td><td>몸통(기념축)·날개(슈퍼쿼드라)</td></tr>
<tr><td>1971</td><td>세일란지아</td><td>판자촌을 옮겨 세운 도시</td></tr>
<tr><td>1987</td><td>유네스코 세계유산</td><td>플라누 필로투 보존</td></tr>
<tr><td>2003</td><td>아과스 클라라스 독립</td><td>고층 아파트 도시</td></tr>
</tbody></table></div>
<p>정리하면 브라질리아는 두 길이 만나는 십자에서 시작해 41개월 만에 비행기 모양으로 세운 도시다. 비행기 안은 6층 아파트와 정부 청사로 계획대로 남았고, 늘어난 사람들은 비행기 밖 위성 도시로 퍼졌다. 50만 명을 위한 도시에 지금은 300만 명이 산다.</p>
<p class="note">이 글은 브동산 유튜브 '도시이야기 4 · 브라질리아' 영상과 함께 만들었다.</p>
</section>

<section><h2>참고한 자료</h2><ul class="src">
{SRC_LIST}
</ul>
<p class="note">사진: Pexels 영상 캡처(Pexels License), 위성·3D 화면 Google Earth(출처 표기). 지도: 브동산 자체 제작 개략도(© OpenStreetMap contributors · Natural Earth).</p></section>

{RELATED}

</div></div>

'''
meta = f'''<title>{TITLE} | 브동산</title>
<meta name="description" content="{esc(DESC)}">
<link rel="canonical" href="{URL}">
<meta property="og:type" content="article"><meta property="og:title" content="{esc(TITLE)}"><meta property="og:description" content="{esc(DESC)}"><meta property="og:image" content="{IMGURL}cover.jpg"><meta property="og:url" content="{URL}">
'''
site = head + meta + style + '</head>\n' + body + foot
open(REPO + f'posts/{SLUG}.html', 'w', encoding='utf-8').write(site)
print('site', len(site))

# ---------------- 네이버용 (해요체, 구성 다르게)
NTAGS = '브라질리아,브라질,브라질여행,계획도시,루시우코스타,니에메예르,슈퍼쿼드라,파라노아호수,세일란지아,브라질수도,브라질한인,도시이야기,도시구조,브동산'
sp = '<p> </p><p> </p>'
def h2(t): return f'{sp}<h2><b><span style="font-size:20px;">{t}</span></b></h2>\n<p> </p>'
T2 = 'style="width:100%;border-collapse:collapse;margin:14px 0;font-size:15px;"'
def tr(a, b): return f'<tr><td style="border:1px solid #E3E3E3;padding:9px 10px;width:34%;background:#FAFAFA;font-weight:800;">{a}</td><td style="border:1px solid #E3E3E3;padding:9px 10px;">{b}</td></tr>'
nv = f'''<!doctype html>
<html lang="ko"><head><meta charset="utf-8">
<meta name="robots" content="noindex,nofollow">
<!--
slug: {SLUG}
title: {NTITLE}
category: 도시이야기
naver_category: 부동산정보
tags: {NTAGS}
cover_candidates: cover-n.jpg (대표사진 = 기념축과 대성당 드론 사진)
site_url: {URL}
-->
<title>{NTITLE} — 네이버 블로그 복사용</title>
<style>
body{{font-family:'Nanum Myeongjo','NanumMyeongjo','AppleMyungjo',serif;line-height:1.8;font-size:16px;color:#111;max-width:720px;margin:0 auto;padding:24px;}}
h1{{font-size:26px;}} h2{{font-size:20px;font-weight:800;margin-top:42px;border-top:1px solid #E3E3E3;padding-top:30px;}} h3{{font-size:17px;}}
img{{max-width:100%;display:block;}} ul{{padding-left:20px;}} li{{margin:8px 0;}}
</style>
</head>

<body>

<p><strong>브라질의 수도 브라질리아는 하늘에서 보면 비행기 모양이에요. 1956년부터 41개월 만에 텅 빈 고원에 지은 계획도시인데, 50만 명을 위해 설계한 도시에 지금은 300만 명이 살아요.</strong></p><p style="color:#8A8A8A;font-size:13px;">브동산 · {TAG} · {DATEL}</p>
<h1>{NTITLE}</h1>

{img('cover', '기념축과 대성당 드론 사진', '기념축과 대성당 · ' + PX, True)}

{h2('브라질리아 한눈에 보기')}
<table {T2}><tbody>
{tr('위치', '브라질 중부 고원, 해발 1,172m')}
{tr('면적', '연방구 5,760㎢ · 서울의 약 9.5배')}
{tr('인구', '약 300만 명(2025 추정) · 계획 도시 안은 22만 명')}
{tr('수도가 된 날', '1960년 4월 21일')}
{tr('세계유산', '1987년 유네스코')}
{tr('한국에서', '2회 경유 약 35시간 · 시차 12시간')}
</tbody></table>
{img('map-size', '연방구에 서울을 같은 축척으로 겹친 지도', '같은 축척으로 겹쳐 본 연방구·서울 · ' + MAPCAP, True)}

{h2('비행기 모양이 된 이유 3가지')}
<h3>① 바닷가 수도를 나라 한가운데로 옮겼어요</h3>
<p>1950년대까지 수도는 바닷가 리우데자네이루였어요. 1956년 쿠비체크 대통령이 텅 빈 내륙 고원에 새 수도를 짓기로 했어요.</p>
{img('ge-region', '위에서 본 브라질리아 일대 위성사진', GEC, True)}
<h3>② 출발점은 두 길이 만나는 십자였어요</h3>
<p>1957년 공모에서 뽑힌 루시우 코스타의 계획은 두 축이 직각으로 만나는 십자에서 시작했어요. 지형에 맞춰 한 축을 휘자 비행기 모양이 됐어요.</p>
{img('map-plan', '기념축과 주거축이 만나는 개략도', '플라누 필로투의 두 축(개략) · ' + MAPCAP, True)}
<h3>③ 몸통과 날개에 할 일을 나눴어요</h3>
<p>몸통(기념축)에는 정부 청사, 날개에는 아파트 단지(슈퍼쿼드라)를 놓았어요. 그리고 41개월 만인 1960년 4월 21일 문을 열었어요.</p>
{img('ge-overview', '위에서 본 플라누 필로투', GEC, True)}

{h2('브라질리아에서 꼭 보는 장면 4곳')}
<p><b>1) 국회의사당과 3권 광장</b> — 비행기 조종석 자리예요. 쌍둥이 빌딩과 접시 모양 지붕, 그 앞에 대통령궁과 대법원이 마주 봐요.</p>
{img('congresso', '국회의사당', PX, True)}
<p><b>2) 메트로폴리탄 대성당</b> — 왕관처럼 생긴 니에메예르의 대성당이에요.</p>
{img('catedral', '브라질리아 대성당', PX, True)}
<p><b>3) 파라노아 호수와 JK 다리</b> — 1959년 댐으로 만든 48㎢ 호수예요. 아치 세 개가 이어진 다리가 놓였어요.</p>
{img('ponte', 'JK 다리', PX, True)}
<p><b>4) 슈퍼쿼드라</b> — 숲속에 6층 아파트가 1층을 비운 기둥 위에 서 있어요. 누구나 단지 사이를 걸어 지나갈 수 있어요.</p>
{img('ge-superquadra', '위에서 본 슈퍼쿼드라', GEC, True)}

{h2('사람들은 비행기 밖으로 퍼졌어요')}
<table {T2}><tbody>
{tr('① 1960년~', '비행기 안 플라누 필로투 · 50만 명 계획, 지금 22만 명')}
{tr('② 1958·1971년~', '위성 도시 타구아팅가, 세일란지아(28.7만 명, 가장 많음)')}
{tr('③ 2000년대~', '20~30층 아파트 도시 아과스 클라라스(1㎢에 1.4만 명)')}
</tbody></table>
{img('map-axis-3', '플라누 필로투에서 위성 도시까지 주거 이동 개략도', '③단계까지 넓어진 도시 · ' + MAPCAP, True)}
<p>세일란지아라는 이름은 1971년 판자촌 주민을 옮긴 캠페인(CEI)에서 왔어요. 수도를 지은 노동자들이 처음부터 도시 밖에 살았거든요.</p>
{img('ge-aguas-claras3d', '아과스 클라라스의 고층 아파트 3D 지도', GEC, True)}

{h2('숫자로 보는 브라질리아')}
<table {T2}><tbody>
{tr('공사 기간', '41개월(1956 → 1960.4.21)')}
{tr('파라노아 호수', '48㎢ · 최대 수심 38m(1959)')}
{tr('슈퍼쿼드라', '6층 이하 · 1층은 기둥만')}
{tr('지하철', '42.38km · 27개 역 · 하루 약 14만 명')}
{tr('출근', '자가용 52% 이상 · 플라누 필로투로 출근 40.7%(2021) → 34.4%(2024)')}
</tbody></table>
{img('esplanada', '기념축과 부처 청사 드론 사진', PX, True)}

{h2('한국과는 어떤 인연이 있나요?')}
<ul>
<li>한국과 브라질은 1959년 10월 31일 수교했어요. 브라질은 중남미에서 한국과 처음 수교한 나라예요.</li>
<li>1962년 12월 부산항을 떠난 첫 이민단 103명이 1963년 2월 산투스항에 닿았어요.</li>
<li>지금 브라질의 한인은 5만 명이 넘어요.</li>
</ul>
{img('itamaraty', '브라질 외교부 이타마라치궁', PX, True)}

{h2('한국에서 가는 법 체크리스트')}
<table {T2}><tbody>
{tr('비행', '직항 없음 · 보통 2회 경유 · 약 35시간')}
{tr('시차', '한국보다 12시간 늦어요')}
{tr('비자', '관광·출장 90일 무비자 · 돌아가는 항공권 필요')}
</tbody></table>
<p>경유 노선과 시간은 자주 바뀌어요. 출국 전에 항공사 일정과 주한 브라질 대사관 공지를 꼭 다시 확인하세요.</p>

{h2('마무리')}
<p>브라질리아는 두 길이 만나는 십자에서 시작해 41개월 만에 비행기 모양으로 세운 도시예요. 비행기 안은 계획대로 남았고, 늘어난 사람들은 비행기 밖 위성 도시로 퍼졌어요.</p>
<p>지도와 연표를 더 자세히 담은 글은 브동산 홈페이지 도시이야기에 있어요.</p>
{img('aerial_end', '브라질리아 드론 사진', PX, True)}

<p> </p><p style="color:#8A8A8A;font-size:13px;">출처: {'; '.join(t.split(' — ')[0] for t, u in S.SOURCES)}. 사진은 Pexels 영상 캡처와 Google Earth 화면(출처 표기), 지도는 브동산 자체 제작 개략도(© OpenStreetMap contributors · Natural Earth)예요.</p>
<p style="color:#8A8A8A;font-size:13px;">태그: {' '.join('#' + t for t in NTAGS.split(','))}</p>

</body></html>
'''
open(OUTN + f'{SLUG}-naver.html', 'w', encoding='utf-8').write(nv)
print('naver', len(nv))
