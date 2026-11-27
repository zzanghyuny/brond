# -*- coding: utf-8 -*-
"""멕시코시티 편 사이트 글 + 네이버용 HTML + 이미지. 사용: python3 make_posts.py
사이트 글(평서문, 장 순서 = 영상 흐름)과 네이버용(해요체, 한눈에 표 → 가라앉는 이유 3가지 → 꼭 보는 장면 4곳 → 주거 이동 표 → 숫자 표 → 한국과의 인연 → 가는 법 체크리스트)은
내용은 같고 구성은 절반 이상 다르게 만든다.
"""
import os, sys, json, subprocess, html, importlib.util
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); LIB = os.path.join(HERE, '..', 'lib'); sys.path.insert(0, LIB)
import dosi_gfx as gfx
spec = importlib.util.spec_from_file_location('script', os.path.join(HERE, 'script.py')); S = importlib.util.module_from_spec(spec); spec.loader.exec_module(S)
EP = S.EP; GEO = json.load(open(EP['geo'])); REPO = '/home/claude/brond/'
SLUG = 'mexico-city-city-structure'; IMG = REPO + f'posts/images/{SLUG}/'; os.makedirs(IMG, exist_ok=True)
URL = f'https://www.brandongsan.com/posts/{SLUG}.html'; IMGURL = f'https://www.brandongsan.com/posts/images/{SLUG}/'
DATE, DATEL = '2026-11-28', '2026. 11. 28'; TAG = '도시이야기 No.003'
TITLE = '멕시코시티는 왜 가라앉을까 — 호수를 메워 세운 도시 700년'
NTITLE = '멕시코시티 가라앉는 도시 총정리 | 호수 위 섬에서 시작, 해마다 최대 50cm, 한국에서 가는 법까지'
OUTN = EP['work'] + 'naver/'; os.makedirs(OUTN, exist_ok=True)

# ---------------- 이미지
def photo(clip, t, name):
    raw = EP['work'] + f'post_{clip}_{t}.png'
    if not os.path.exists(raw): subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(t), '-i', EP['px'] + f'px_{clip}.mp4', '-frames:v', '1', raw], check=True)
    im = Image.open(raw).convert('RGB')
    im.resize((1600, int(1600 * im.height / im.width)), Image.LANCZOS).save(IMG + name + '.jpg', quality=82, optimize=True)
    n = im.resize((1000, int(1000 * im.height / im.width)), Image.LANCZOS); q = 82
    while True:
        n.save(IMG + name + '-n.jpg', quality=q, optimize=True)
        if os.path.getsize(IMG + name + '-n.jpg') <= 400_000 or q <= 60: break
        q -= 6
PHOTOS = dict(cover=('11690475', 6), volcano=('35691533', 8), zocalo=('4044986', 8), chinampa=('40140926', 10), canal=('31986191', 15), basilica=('34795249', 6),
              cathedral=('3562640', 3), flood=('28730770', 8), haze=('4591141', 5), angel_top=('13638459', 8), angel_dusk=('15809156', 10), urban=('30056250', 15),
              centro=('30138329', 10), roma=('31623394', 6), jacaranda=('36301273', 3), polanco=('12943393', 10), santafe=('28833289', 6), tlatelolco=('38659251', 10),
              sprawl=('30404668', 12), housing=('37796402', 3), crowd=('30138330', 12), market=('30138479', 20), metro=('39928082', 8), cable=('39665647', 6),
              reforma=('31986210', 20), angel_street=('36385590', 8), skyline=('34849951', 20))
for k, (c, t) in PHOTOS.items(): photo(c, t, k)

MAPS = {}
for i, s in enumerate(S.LONG):
    for sh in s['shots']:
        if sh[0] == 'anim':
            o = sh[2]; key = {'overlay': 'map-size', 'numbers': 'numbers', 'route': 'map-route', 'flight': 'map-flight', 'card': 'card-transport'}.get(sh[1])
            if sh[1] == 'map':
                if 'stage' in o: key = f"map-axis-{ {'①': 1, '②': 2, '③': 3}[o['stage'][0]] }"
                else: key = 'map-lake' if any(L['g'] == 'c_tepeyac' for L in o['layers']) else 'map-sink'
            MAPS[key] = (sh[1], o)
def render_last(name, o, W, H, short, ui, out):
    gfx.UI = ui; gfx.FPS = 2; last = None
    for fr in gfx.frames(name, W, H, 9.0, [0.4, 3.0], o, GEO, short): last = fr
    Image.frombytes('RGB', (W, H), last).save(out, quality=86, optimize=True)
for key, (name, o) in MAPS.items():
    if key in ('numbers', 'card-transport'): continue
    render_last(name, o, 1920, 804, False, 1.0, IMG + key + '.jpg')
    if key in ('map-lake', 'map-sink'): o = dict(o, side=None)
    if key in ('map-flight', 'map-route'): o = dict(o, bounds=(116.0, -2.0, 300.0, 56.0))
    if key == 'map-flight': o = dict(o, dest_label='멕시코시티')
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
MAPCAP = '브동산 자체 제작 개략도 · 지도 © OpenStreetMap contributors · Natural Earth · 실제 경계·축척과 다를 수 있음'

# ---------------- 사이트 글
tmpl = open(REPO + 'posts/chongqing-city-structure.html', encoding='utf-8').read()
head = tmpl[:tmpl.find('<title>')]
style = tmpl[tmpl.find('<style>'):tmpl.find('<style id="cp-style">')] if '<style id="cp-style">' in tmpl else tmpl[tmpl.find('<style>'):tmpl.find('</head>')]
if '.related-item' not in style:
    style = style.replace('  .related-list{', '  .related-item{ display:block; padding:13px 0; border-bottom:1px solid var(--hair); text-decoration:none; }\n  .related-item .r-tag{ display:block; font-size:11.5px; color:var(--ink-faint); margin-bottom:4px; }\n  .related-item .r-title{ display:block; font-size:15px; font-weight:700; color:var(--ink); line-height:1.5; }\n  .related-list{', 1)
foot = tmpl[tmpl.find('<footer>'):]
DESC = '멕시코시티는 서울의 약 2.5배, 인구 922만 명. 1325년 텍스코코 호수 위 섬에 세운 테노치티틀란에서 시작해 호수를 메운 도시가 해마다 최대 50cm 가라앉는 이유, 주거 중심의 이동, 한인 이민 120년의 인연, 한국에서 가는 법까지 정리했다.'
RELATED = '''<section id="related">
  <h2>도시이야기의 다른 포스팅</h2>
  <div class="related-list"><a class="related-item" href="chongqing-city-structure.html"><span class="r-tag">도시이야기 No.002</span><span class="r-title">충칭은 왜 8D 도시가 됐을까 — 두 강과 산이 만든 입체 도시</span></a></div>
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

{img('cover', '해 질 녘 멕시코시티 레포르마 대로 일대의 고층 빌딩과 시가지를 드론으로 내려다본 모습', '해 질 녘의 멕시코시티 · ' + PX)}
<section><p class="lede">멕시코시티는 해발 2,240m, 산과 화산에 둘러싸인 분지에 있다. 겉보기엔 평평한 대도시지만 이 도시는 해마다 조금씩 가라앉는다. 빠른 곳은 1년에 50cm까지 내려앉는다. 이유를 찾으려면 700년 전, 이 땅이 호수였던 때로 거슬러 올라가야 한다.</p></section>

<section><h2>1. 서울의 2.5배, 인구는 서울과 비슷</h2>
<p>멕시코시티(시우다드 데 메히코)의 면적은 약 1,494㎢로 서울(605㎢)의 2.5배쯤이다. 행정구역은 알카디아라고 부르는 16개 구로 나뉜다. 2025년 10월 기준 인구는 922만 명으로 서울(934만 명)과 비슷하다.</p>
{img('map-size', '멕시코시티 경계 위에 서울을 같은 축척으로 겹쳐 본 지도', '같은 축척으로 겹쳐 본 멕시코시티(황동색)와 서울(흰색) · ' + MAPCAP)}
<p>하지만 도시는 경계 밖으로 한참 넘쳐 있다. 주변 멕시코주·이달고주의 시까지 합친 광역권(멕시코 계곡 대도시권) 인구는 2020년 2,140만 명이었다.</p>
<div class="tbl-wrap"><table class="rule"><thead><tr><th>항목</th><th>멕시코시티</th><th>서울</th></tr></thead><tbody>
<tr><td>면적</td><td>약 1,494㎢</td><td>605㎢</td></tr>
<tr><td>인구(2025)</td><td>922만 명</td><td>934만 명</td></tr>
<tr><td>광역권 인구(2020)</td><td>2,140만 명</td><td>—</td></tr>
<tr><td>해발 고도</td><td>2,240m</td><td>—</td></tr>
<tr><td>구</td><td>알카디아 16곳</td><td>자치구 25곳</td></tr>
</tbody></table></div>
<p class="note">출처: INEGI 2025 인구조사(Encuesta Intercensal)·2020 센서스(면적은 인구밀도로 환산), Metrópolis de México 2020, 멕시코시티 관광청, 통계청(서울 인구)</p>
{img('volcano', '해 뜰 무렵 멀리 화산이 보이는 멕시코시티 분지', '해 뜰 무렵의 분지와 멀리 보이는 화산 · ' + PX)}
</section>

<section><h2>2. 호수 위의 섬에서 시작했다</h2>
<p>도시 한가운데 소칼로 광장 자리는 700년 전 텍스코코 호수 서쪽에 떠 있던 작은 섬이었다. 아스테카(메시카) 사람들은 선인장 위에서 뱀을 먹는 독수리가 보이는 곳에 도시를 세우라는 계시를 따라 이 섬에 자리 잡았다고 전한다. 이 장면은 지금 멕시코 국기에 그려져 있다. 도시 이름은 테노치티틀란, 건설 연도는 1325년으로 본다.</p>
{img('zocalo', '사람으로 가득한 소칼로 광장과 국립궁전', '소칼로 광장 · ' + PX)}
<p>섬은 북쪽 테페약, 서쪽 타쿠바, 남쪽 이스타팔라파로 놓은 둑길(칼사다)로 호숫가와 이어졌다. 도시 안에는 카누가 다니는 운하가 여럿 놓였다. 섬 북쪽에는 쌍둥이 도시 틀라텔롤코가 있었다.</p>
{img('map-lake', '테노치티틀란과 둑길을 표시한 개략도', '테노치티틀란과 둑길(점선, 개략 위치) · ' + MAPCAP)}
<p>땅이 모자라자 사람들은 얕은 물 위에 흙을 쌓아 밭을 만들었다. 이것이 치남파다. 남쪽 소치밀코에는 옛 호수의 남쪽 줄기와 치남파가 지금도 남아 있어, 1987년 멕시코시티 역사지구와 함께 유네스코 세계유산이 됐다.</p>
{img('chinampa', '소치밀코의 치남파 밭과 물길을 드론으로 내려다본 모습', '소치밀코의 치남파 · ' + PX)}
{img('canal', '소치밀코 운하에 늘어선 색색의 트라히네라 배', '소치밀코 운하의 트라히네라 · ' + PX)}
<p>북쪽 둑길이 닿던 테페약 언덕에는 지금 과달루페 성모 대성당이 서 있다.</p>
{img('basilica', '테페약 언덕 아래 과달루페 성모 대성당과 광장', '과달루페 성모 대성당 · ' + PX)}
<p>1521년 8월 13일, 몇 달에 걸친 포위 끝에 스페인군과 동맹군이 테노치티틀란을 무너뜨렸다. 스페인은 그 폐허 위에 누에바 에스파냐의 수도를 세웠고, 도시를 둘러싼 호수의 물을 빼기 시작했다. 소칼로 옆 메트로폴리탄 대성당과 템플로 마요르 유적이 그 겹친 시간을 보여 준다.</p>
{img('cathedral', '소칼로 광장의 메트로폴리탄 대성당', '메트로폴리탄 대성당 · ' + PX)}
<p>호숫가 도시는 홍수에 자주 시달렸다. 1607년 11월 북쪽 우에우에토카 쪽으로 첫 배수로 공사가 시작됐지만 1629년 큰 홍수가 도시를 덮쳤다. 1900년에는 포르피리오 디아스 정부가 대운하(Gran Canal del Desagüe)를 열었다. 처음 연 지상 구간만 47.5km였다. 그렇게 분지의 호수는 거의 다 말라 사라졌고, 옛 호수 바닥 위로 시가지가 퍼졌다.</p>
{img('flood', '큰비에 물이 차오른 멕시코시티의 도로', '큰비가 내린 날의 도로 · ' + PX)}
{img('haze', '옛 호수 바닥 위로 끝없이 펼쳐진 시가지를 드론으로 내려다본 모습', '옛 호수 바닥 위에 퍼진 시가지 · ' + PX)}
</section>

<section><h2>3. 해마다 가라앉는 도시</h2>
<p>레포르마 대로의 독립기념탑(천사상)은 1910년에 세워졌다. 그 뒤 주변 땅이 내려앉으면서 받침에 계단을 14개나 더 붙여야 했다. 탑이 솟은 게 아니라 땅이 꺼진 것이다.</p>
{img('angel_top', '위에서 내려다본 독립기념탑과 원형 교차로', '독립기념탑(천사상) · ' + PX)}
<p>도시 아래는 옛 호수 바닥에 쌓인 무른 진흙층이다. 지난 100년 동안 이 지층에서 지하수를 대량으로 퍼 올리자 진흙이 눌리며 땅이 꺼졌다. 2024년 학술지 Scientific Reports에 실린 위성 관측 연구에 따르면 빠른 곳은 1년에 500mm, 곧 50cm까지 내려앉는다. 미국·인도 공동 위성 NISAR는 2025년 10월부터 2026년 1월 사이 공항 주변 등에서 한 달에 2cm 넘게 꺼지는 곳을 잡아냈다.</p>
{img('map-sink', '멕시코시티에서 지반 침하가 빠른 공항 주변과 찰코를 표시한 개략도', '침하가 빠른 곳(개략) · NASA JPL(2026)·Scientific Reports(2024) 보도 기준 · ' + MAPCAP)}
<p>그렇다고 펌프를 멈추기도 어렵다. 멕시코시티 수돗물의 절반 이상(자료에 따라 59~67%)이 땅속 우물에서 나온다. 멀리 쿠차말라 수계에서 끌어오는 물은 3분의 1이 안 된다.</p>
{img('urban', '멕시코시티 시가지를 낮게 내려다본 드론 사진', '시가지 · ' + PX)}
<p>땅이 꺼지면서 길과 건물, 수도관이 갈라지고 지하철도 피해를 입는다.</p>
{img('angel_dusk', '해 질 녘 독립기념탑의 금빛 천사상', '해 질 녘의 천사상 · ' + PX)}
</section>

<section><h2>4. 사람들은 세 번 옮겨 갔다</h2>
<p>주거와 상업의 중심은 크게 세 번 옮겨 갔다.</p>
<h3>① 옛 섬 자리, 센트로 · ~1900년</h3>
<p>스페인 시대부터 20세기 초까지 도시의 중심은 옛 테노치티틀란 섬 자리, 지금의 센트로 이스토리코(역사지구)였다.</p>
{img('map-axis-1', '1단계: 소칼로 일대 센트로를 표시한 개략도', '①단계 · ' + MAPCAP)}
{img('centro', '돌길이 깔린 센트로 이스토리코의 거리', '센트로 이스토리코 · ' + PX)}
<h3>② 서쪽 새 동네, 로마·콘데사·폴랑코 · 1902년~</h3>
<p>1902년 시 정부는 서쪽에 로마 지구 계획을 승인했다. 로마는 도로·상수도·하수도를 처음부터 갖춘 멕시코시티의 첫 콜로니아(동네)였다. 이웃한 콘데사는 1920~30년대에 건물이 빠르게 들어섰고, 1937년에는 더 서쪽 옛 아시엔다(농장) 땅에 폴랑코가 개발됐다.</p>
{img('map-axis-2', '2단계: 서쪽 로마, 콘데사, 폴랑코를 표시한 개략도', '②단계 · ' + MAPCAP)}
{img('roma', '로마 지구의 시벨레스 분수', '로마 지구의 시벨레스 분수 · ' + PX)}
<p>1985년 9월 대지진은 이 동네들에도 큰 상처를 남겼다. 로마 지구에서만 건물 472채가 무너지거나 부서졌다. 로마의 인구는 1970년 9만 5천 명에서 1995년 3만 5천 명으로 줄었다.</p>
{img('jacaranda', '보라색 자카란다 꽃이 핀 주거지', '봄의 자카란다 · ' + PX)}
<p>폴랑코는 지금 마사리크 거리를 중심으로 고급 상점과 사무용 빌딩이 늘어선 동네가 됐다.</p>
{img('polanco', '폴랑코 일대의 유리 외벽 고층 빌딩', '폴랑코 일대 · ' + PX)}
<h3>③ 서쪽 언덕, 산타페 · 1980년대~</h3>
<p>서쪽 언덕의 산타페는 식민지 시대부터 모래를 캐던 곳이었고, 1960년대부터는 쓰레기 매립지로 쓰였다. 1980년대 대학과 건물이 들어서기 시작했고, 1988~1994년 정부가 세운 개발 계획이 1994년 경제 위기로 멈췄다가 2000년 다시 추진되면서 업무지구로 자리 잡았다. 지금은 고층 빌딩과 대형 쇼핑몰 센트로 산타페, 대학이 모인 신도심이다.</p>
{img('map-axis-3', '3단계: 서쪽 언덕 산타페를 표시한 개략도', '③단계 · ' + MAPCAP)}
{img('santafe', '산타페의 고층 빌딩과 쇼핑몰', '산타페 · ' + PX)}
</section>

<section><h2>5. 멕시코시티 사람들이 사는 집</h2>
<p>1960~1965년 정부는 북쪽 틀라텔롤코에 거대한 아파트 단지를 지었다. 건축가 마리오 파니가 설계한 노노알코-틀라텔롤코 단지는 처음에 아파트 102동, 멕시코에서 가장 큰 단지였다. 1985년 지진 때 누에보 레온 동이 무너지는 큰 피해를 입었다.</p>
{img('tlatelolco', '노노알코-틀라텔롤코 아파트 단지를 내려다본 모습', '노노알코-틀라텔롤코 단지 · ' + PX)}
<p>도시 바깥쪽으로는 낮은 집이 끝없이 이어진다. 2020년 멕시코시티에는 사람이 사는 집이 276만 채 있었고, 한 집에 평균 3.3명이 살았다. 2000년 4.0명에서 꾸준히 줄었다.</p>
{img('sprawl', '낮은 집이 끝없이 이어진 시가지를 드론으로 내려다본 모습', '끝없이 이어진 낮은 집 · ' + PX)}
{img('housing', '붉은 지붕의 주택가를 드론으로 내려다본 모습', '주택가 · ' + PX)}
</section>

<section><h2>6. 922만 명이 사는 도시</h2>
<p>16개 구 가운데 인구가 가장 많은 곳은 동쪽 이스타팔라파로, 2025년 188만 명이 산다. 시민 다섯 명 중 한 명꼴이다. 이스타팔라파는 침하가 심한 옛 호수 바닥 지역이기도 하다.</p>
{img('crowd', '센트로의 횡단보도를 건너는 사람들', '센트로의 거리 · ' + PX)}
<p>구시가지 골목에는 시장과 노점이 줄지어 있고, 11월 초 망자의 날 무렵이면 거리가 종이 장식(파펠 피카도)과 금잔화로 물든다.</p>
{img('market', '종이 장식이 걸린 구시가지 시장 골목', '구시가지 시장 골목 · ' + PX)}
</section>

<section><h2>7. 지하철과 케이블카</h2>
<p>멕시코시티 지하철은 1969년 9월 4일 처음 달렸다. 2026년 현재 12개 노선, 195개 역, 226.5km이고 하루 450만 명 넘게 탄다.</p>
{img('metro', '멕시코시티 지하철에 오르는 승객들', '지하철 · ' + PX)}
<p>지하철이 닿지 않는 언덕 동네에는 케이블카 버스 '카블레부스(Cablebús)'를 놓았다. 2021년 북쪽 1호선(9.2km)이 처음 열렸고, 같은 해 동쪽 이스타팔라파의 2호선(10.55km)은 세계에서 가장 긴 도시 대중교통 케이블카로 기네스 기록에 올랐다. 2024년에는 차풀테펙 숲을 건너는 3호선이 열려 첫해에만 600만 명 가까이 탔다.</p>
<div class="tbl-wrap"><table class="rule"><thead><tr><th>항목</th><th>내용</th></tr></thead><tbody>
<tr><td>지하철</td><td>1969년 개통 · 12개 노선 · 195개 역 · 226.5km · 하루 450만 명 이상</td></tr>
<tr><td>카블레부스 1호선</td><td>2021년 · 9.2km(인디오스 베르데스–쿠아우테펙)</td></tr>
<tr><td>카블레부스 2호선</td><td>2021년 · 10.55km · 기네스 '가장 긴 도시 케이블카'</td></tr>
<tr><td>카블레부스 3호선</td><td>2024년 · 차풀테펙 숲 횡단 · 첫해 약 600만 명</td></tr>
</tbody></table></div>
{img('cable', '도시 위를 지나는 케이블카', '케이블카 · ' + PX)}
<p>도심은 레포르마 대로가 비스듬히 가로지른다. 독립기념탑도 이 대로 위에 있다.</p>
{img('reforma', '고층 빌딩 사이로 뻗은 레포르마 대로', '레포르마 대로 · ' + PX)}
</section>

<section><h2>8. 한국과 이어진 도시</h2>
<p>1905년 4월 4일, 한인 1,033명이 영국 배 일포드호를 타고 제물포(지금의 인천)를 떠났다. 한 달여 뒤 태평양 쪽 살리나크루스에 내린 이들은 기차와 배로 유카탄반도로 옮겨 가 에네켄(용설란의 한 종류) 농장에서 계약 노동을 했다. 2025년 재외동포청 자료에 따르면 지금 멕시코에 사는 그 후손은 3만 명이 넘는다.</p>
{img('map-route', '1905년 한인 이민자가 제물포에서 멕시코 유카탄까지 간 경로', '1905년 첫 한인 이민 경로(개략) · ' + MAPCAP)}
<p>멕시코시티 독립기념탑 옆 소나 로사에는 1990년대 이후 한인이 모여들어 한국 식당과 가게가 모인 '작은 서울(Pequeño Seúl)'이 생겼다.</p>
{img('angel_street', '해 질 녘 레포르마 대로의 독립기념탑', '독립기념탑 일대 · ' + PX)}
</section>

<section><h2>9. 한국에서 가는 법</h2>
{img('map-flight', '인천에서 멕시코시티까지 항로', '인천 → 멕시코시티 항로(개략) · ' + MAPCAP)}
<div class="tbl-wrap"><table class="rule"><thead><tr><th>항목</th><th>내용</th></tr></thead><tbody>
<tr><td>비행</td><td>아에로멕시코 인천→멕시코시티 직항 약 13시간 55분, 돌아오는 편은 몬테레이 경유 약 19시간 15분(2026년 11월 운항 정보 기준)</td></tr>
<tr><td>경유</td><td>미국·캐나다 경유 1회 환승 약 16~20시간</td></tr>
<tr><td>시차</td><td>한국보다 15시간 늦다(멕시코시티는 서머타임 없음)</td></tr>
<tr><td>비자</td><td>한국 국적자 관광·출장 최대 180일 무비자, 6개월 이상 유효 여권</td></tr>
<tr><td>항공권</td><td>왕복 약 100만~200만 원대(2026년 11월 조회, 시기·경유에 따라 크게 다르다)</td></tr>
</tbody></table></div>
<p class="note">이 노선은 운항 요일·횟수가 자주 바뀌고, 2026년 초에는 운휴를 검토한다는 보도도 있었다. 출국 전에 항공사 일정과 주한 멕시코 대사관 공지를 다시 확인하자.</p>
{img('skyline', '푸른 숲과 고층 빌딩이 어우러진 멕시코시티 스카이라인', '멕시코시티 스카이라인 · ' + PX)}
</section>

<section><h2>10. 정리</h2>
<div class="tbl-wrap"><table class="rule"><thead><tr><th>연도</th><th>일어난 일</th><th>도시 모양으로 보면</th></tr></thead><tbody>
<tr><td>1325</td><td>테노치티틀란 건설</td><td>호수 위 섬 도시, 둑길·운하·치남파</td></tr>
<tr><td>1521</td><td>스페인에 함락</td><td>폐허 위에 새 수도, 호수 배수 시작</td></tr>
<tr><td>1607~1629</td><td>첫 배수로 공사, 대홍수</td><td>물과의 싸움</td></tr>
<tr><td>1900</td><td>대운하 개통</td><td>호수가 거의 사라지고 시가지 확장</td></tr>
<tr><td>1902~1937</td><td>로마·콘데사·폴랑코</td><td>서쪽 새 동네</td></tr>
<tr><td>1905</td><td>첫 한인 이민 1,033명</td><td>한국과의 인연</td></tr>
<tr><td>1910</td><td>독립기념탑 완공</td><td>이후 계단 14개 추가</td></tr>
<tr><td>1960~1965</td><td>틀라텔롤코 아파트 단지</td><td>대규모 공공 주택</td></tr>
<tr><td>1969</td><td>지하철 개통</td><td>지금 12개 노선</td></tr>
<tr><td>1980년대~</td><td>산타페 개발</td><td>서쪽 언덕 신도심</td></tr>
<tr><td>2021~2024</td><td>카블레부스 1~3호선</td><td>언덕 동네와 숲을 잇는 케이블카</td></tr>
</tbody></table></div>
<p>정리하면 멕시코시티는 호수 위 작은 섬에서 시작해, 호수의 물을 빼고 그 바닥 위로 커진 도시다. 옛 호수 바닥의 진흙과 그 아래 지하수에 기대 사는 구조가 지금도 땅을 끌어내리고 있다. 사람들이 살 곳을 찾아 서쪽 언덕으로 옮겨 간 것도, 도시가 해마다 가라앉는 것도 결국 이 땅이 호수였다는 사실에서 시작된다.</p>
<p class="note">이 글은 브동산 유튜브 '도시이야기 3 · 멕시코시티' 영상과 함께 만들었다.</p>
</section>

<section><h2>참고한 자료</h2><ul class="src">
{SRC_LIST}
</ul>
<p class="note">사진: Pexels 영상 캡처(Pexels License). 지도: 브동산 자체 제작 개략도(© OpenStreetMap contributors · Natural Earth).</p></section>

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
NTAGS = '멕시코시티,멕시코여행,CDMX,테노치티틀란,텍스코코호,지반침하,독립기념탑,소치밀코,소칼로,아스테카,애니깽,멕시코한인,도시이야기,도시구조,브동산'
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
cover_candidates: cover-n.jpg (대표사진 = 해 질 녘 멕시코시티 드론 사진)
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

<p><strong>멕시코시티는 700년 전 호수 위 작은 섬에서 시작해, 호수의 물을 빼고 그 바닥 위로 커진 도시예요. 그래서 지금도 빠른 곳은 1년에 50cm까지 가라앉아요. 왜 그런지 지도와 사진으로 정리했어요.</strong></p><p style="color:#8A8A8A;font-size:13px;">브동산 · {TAG} · {DATEL}</p>
<h1>{NTITLE}</h1>

{img('cover', '해 질 녘 멕시코시티 시가지 드론 사진', '해 질 녘의 멕시코시티 · ' + PX, True)}

{h2('멕시코시티 한눈에 보기')}
<table {T2}><tbody>
{tr('위치', '멕시코 중부 고원, 해발 2,240m 분지')}
{tr('면적', '약 1,494㎢ · 서울의 약 2.5배')}
{tr('인구', '922만 명(2025) · 광역권 2,140만 명(2020)')}
{tr('행정구역', '알카디아(구) 16곳')}
{tr('시작', '1325년 텍스코코 호수 위 섬, 테노치티틀란')}
{tr('한국에서', '인천 직항 약 14시간 · 시차 15시간')}
</tbody></table>
{img('map-size', '멕시코시티 경계 위에 서울을 같은 축척으로 겹친 지도', '같은 축척으로 겹쳐 본 멕시코시티·서울 · ' + MAPCAP, True)}
<p>인구는 서울과 비슷한데, 경계 밖 멕시코주·이달고주까지 이어진 광역권은 2천만 명이 넘는 거대 도시권이에요.</p>

{h2('멕시코시티가 가라앉는 이유 3가지')}
<h3>① 도시가 옛 호수 바닥 위에 서 있어요</h3>
<p>아스테카 사람들은 1325년 텍스코코 호수 위 작은 섬에 테노치티틀란을 세웠어요. 1521년 스페인이 그 폐허 위에 새 수도를 짓고 호수의 물을 빼기 시작했고, 1900년 47.5km 대운하까지 열리면서 호수는 거의 다 사라졌어요.</p>
{img('map-lake', '테노치티틀란과 둑길 개략도', '테노치티틀란과 둑길(점선, 개략) · ' + MAPCAP, True)}
<h3>② 그 바닥은 물을 머금은 무른 진흙이에요</h3>
<p>옛 호수 바닥의 진흙층은 물을 빼면 스펀지처럼 눌려요. 빠른 곳은 1년에 50cm까지 내려앉고, 2025년 말 위성(NISAR)은 공항 주변이 한 달에 2cm 넘게 꺼지는 걸 잡아냈어요.</p>
{img('map-sink', '침하가 빠른 공항 주변과 찰코 개략도', '침하가 빠른 곳(개략) · ' + MAPCAP, True)}
<h3>③ 그런데도 땅속 물을 계속 퍼 올려요</h3>
<p>수돗물의 절반 이상(자료에 따라 59~67%)이 땅속 우물에서 나와요. 펌프를 멈추기 어려우니 땅도 계속 꺼지고, 길과 건물, 수도관, 지하철까지 피해를 입어요.</p>
{img('urban', '멕시코시티 시가지 드론 사진', PX, True)}

{h2('멕시코시티에서 꼭 보는 장면 4곳')}
<p><b>1) 독립기념탑(천사상)</b> — 1910년에 세운 뒤 주변 땅이 꺼지면서 받침에 계단 14개를 더 붙였어요. 가라앉는 도시를 눈으로 확인하는 곳이에요.</p>
{img('angel_top', '위에서 내려다본 독립기념탑', PX, True)}
<p><b>2) 소칼로 광장과 대성당</b> — 옛 테노치티틀란 섬의 한가운데예요. 대성당 옆에는 아스테카 대신전(템플로 마요르) 유적이 남아 있어요.</p>
{img('cathedral', '소칼로 광장의 메트로폴리탄 대성당', PX, True)}
<p><b>3) 소치밀코</b> — 옛 호수의 남쪽 줄기와 물 위의 밭 '치남파'가 남은 곳이에요. 1987년 역사지구와 함께 유네스코 세계유산이 됐어요.</p>
{img('chinampa', '소치밀코의 치남파 밭', PX, True)}
<p><b>4) 틀라텔롤코 아파트 단지</b> — 1960~1965년에 지은 아파트 102동, 멕시코에서 가장 큰 단지였어요.</p>
{img('tlatelolco', '노노알코-틀라텔롤코 아파트 단지', PX, True)}

{h2('사람들은 이렇게 옮겨 갔어요')}
<table {T2}><tbody>
{tr('① ~1900년', '옛 섬 자리 센트로(역사지구)')}
{tr('② 1902년~', '서쪽 새 동네 로마(1902)·콘데사·폴랑코(1937)')}
{tr('③ 1980년대~', '서쪽 언덕 산타페 · 모래 채굴장·매립지 → 업무지구')}
</tbody></table>
{img('map-axis-3', '센트로에서 서쪽 산타페까지 주거 중심 이동 개략도', '③단계까지 넓어진 시가지 · ' + MAPCAP, True)}
<p>로마 지구는 도로와 상하수도를 처음부터 갖춘 첫 동네였어요. 1985년 대지진 때는 로마 지구에서만 건물 472채가 무너지거나 부서졌어요.</p>
{img('santafe', '산타페의 고층 빌딩', PX, True)}

{h2('숫자로 보는 멕시코시티')}
<table {T2}><tbody>
{tr('가장 큰 구', '이스타팔라파 188만 명(시민 5명 중 1명)')}
{tr('집', '276만 채 · 한 집 평균 3.3명(2020)')}
{tr('지하철', '1969년 개통 · 12개 노선 · 195개 역 · 하루 450만 명+')}
{tr('케이블카', '카블레부스 2호선 10.55km · 기네스 가장 긴 도시 케이블카')}
{tr('침하 속도', '빠른 곳 연 50cm · 공항 주변 월 2cm+')}
</tbody></table>
{img('metro', '멕시코시티 지하철에 오르는 승객들', PX, True)}

{h2('한국과는 어떤 인연이 있나요?')}
<ul>
<li>1905년 4월 4일, 한인 1,033명이 제물포에서 일포드호를 타고 떠나 멕시코 살리나크루스에 내렸어요.</li>
<li>유카탄의 에네켄(용설란) 농장에서 계약 노동을 했고, 지금 멕시코에 사는 후손은 3만 명이 넘어요(재외동포청, 2025).</li>
<li>멕시코시티 독립기념탑 옆 소나 로사에는 한국 식당과 가게가 모인 '작은 서울(Pequeño Seúl)'이 있어요.</li>
</ul>
{img('map-route', '1905년 한인 이민 경로', '1905년 첫 한인 이민 경로(개략) · ' + MAPCAP, True)}

{h2('한국에서 가는 법 체크리스트')}
<table {T2}><tbody>
{tr('비행', '인천→멕시코시티 직항 약 13시간 55분 · 돌아오는 편 몬테레이 경유 약 19시간(2026년 11월 기준)')}
{tr('시차', '한국보다 15시간 늦어요(서머타임 없음)')}
{tr('비자', '관광·출장 최대 180일 무비자 · 6개월 이상 유효 여권')}
{tr('항공권', '왕복 약 100만~200만 원대(시기·경유에 따라 달라요)')}
</tbody></table>
{img('map-flight', '인천에서 멕시코시티까지 항로', MAPCAP, True)}
<p>직항은 운항 요일·횟수가 자주 바뀌어요. 출국 전에 항공사 일정과 주한 멕시코 대사관 공지를 꼭 다시 확인하세요.</p>

{h2('마무리')}
<p>멕시코시티는 호수 위 작은 섬에서 시작해 호수를 메우며 커진 도시예요. 그 바닥의 진흙과 땅속 물에 기대 사는 구조가 지금도 도시를 끌어내리고 있어요.</p>
<p>지도와 연표를 더 자세히 담은 글은 브동산 홈페이지 도시이야기에 있어요.</p>
{img('skyline', '멕시코시티 스카이라인', PX, True)}

<p> </p><p style="color:#8A8A8A;font-size:13px;">출처: {'; '.join(t.split(' — ')[0] for t, u in S.SOURCES)}. 사진은 Pexels 영상 캡처, 지도는 브동산 자체 제작 개략도(© OpenStreetMap contributors · Natural Earth)예요.</p>
<p style="color:#8A8A8A;font-size:13px;">태그: {' '.join('#' + t for t in NTAGS.split(','))}</p>

</body></html>
'''
open(OUTN + f'{SLUG}-naver.html', 'w', encoding='utf-8').write(nv)
print('naver', len(nv))
