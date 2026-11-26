# -*- coding: utf-8 -*-
"""충칭 편 사이트 글 + 네이버용 HTML + 이미지. 사용: python3 make_posts.py
사이트 글(평서문, 장 순서 = 영상 흐름)과 네이버용(해요체, 한눈에 표 → 이유 3가지 → 볼거리 4곳 → Q&A식 정리)은 내용은 같고 구성은 절반 이상 다르게 만든다.
"""
import os, sys, json, subprocess, html, importlib.util
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); LIB = os.path.join(HERE, '..', 'lib'); sys.path.insert(0, LIB)
import dosi_gfx as gfx
spec = importlib.util.spec_from_file_location('script', os.path.join(HERE, 'script.py')); S = importlib.util.module_from_spec(spec); spec.loader.exec_module(S)
EP = S.EP; GEO = json.load(open(EP['geo'])); REPO = '/home/claude/brond/'
SLUG = 'chongqing-city-structure'; IMG = REPO + f'posts/images/{SLUG}/'; os.makedirs(IMG, exist_ok=True)
URL = f'https://www.brandongsan.com/posts/{SLUG}.html'; IMGURL = f'https://www.brandongsan.com/posts/images/{SLUG}/'
DATE, DATEL = '2026-11-27', '2026. 11. 27'; TAG = '도시이야기 No.002'
TITLE = '충칭은 왜 8D 도시가 됐을까 — 두 강과 산이 만든 입체 도시'
NTITLE = '충칭 8D 도시 총정리 | 서울 136배 크기, 아파트 뚫는 모노레일, 임시정부까지'
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
PHOTOS = dict(cover=('39744311', 5), confluence=('39744311', 9), hongyadong=('36149475', 20), river=('39742352', 8), city=('34766462', 10),
              jiefangbei=('36334237', 4), bridge=('34315157', 12), highrise=('39718554', 10), skybridge=('39718785', 5), hongyadong_day=('39724016', 14),
              street=('36437264', 10), ciqikou=('39761550', 3), liziba=('38906655', 8), liziba2=('29682593', 12), nightbridge=('35439686', 20), raffles=('34315150', 6))
for k, (c, t) in PHOTOS.items(): photo(c, t, k)

def scene_shot(name):
    for s in S.LONG:
        for sh in s['shots']:
            if sh[0] == 'anim' and (s.get('_name') == name): return sh
    return None
MAPS = {}
for i, s in enumerate(S.LONG):
    for sh in s['shots']:
        if sh[0] == 'anim':
            o = sh[2]; key = {'overlay': 'map-size', 'numbers': 'numbers', 'route': 'map-route', 'flight': 'map-flight', 'card': 'card-transport'}.get(sh[1])
            if sh[1] == 'map': key = 'map-rivers' if 'stage' not in o else f"map-axis-{ {'①': 1, '②': 2, '③': 3}[o['stage'][0]] }"
            MAPS[key] = (sh[1], o)
def render_last(name, o, W, H, short, ui, out):
    gfx.UI = ui; gfx.FPS = 2; last = None
    for fr in gfx.frames(name, W, H, 9.0, [0.4, 3.0], o, GEO, short): last = fr
    Image.frombytes('RGB', (W, H), last).save(out, quality=86, optimize=True)
for key, (name, o) in MAPS.items():
    if key in ('numbers', 'card-transport'): continue
    render_last(name, o, 1920, 804, False, 1.0, IMG + key + '.jpg')
    if key == 'map-route':
        o = dict(o, bounds=(102.0, 20.5, 126.0, 34.5), offsets={'충칭': (1, -1.0), '치장': (1, 0.8), '항저우': (1, 0.8), '전장': (-1, -0.8), '상하이': (1, -0.9), '창사': (1, 0), '광저우': (1, 0), '류저우': (1, 0)})
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
    return f'<div class="photo-block"><img src="{src}" alt="{esc(alt)}" style="width:100%;display:block;">{c}</div>'
SRC_LINKS = ' · '.join(f'<a href="{esc(u)}" target="_blank" rel="noopener">{esc(t.split(" — ")[0])} ↗</a>' for t, u in S.SOURCES)
PX = '영상 캡처 Pexels'
MAPCAP = '브동산 자체 제작 개략도 · 지도 © OpenStreetMap contributors · Natural Earth · 실제 경계·축척과 다를 수 있음'

# ---------------- 사이트 글
tmpl = open('/home/claude/src/brond/posts/hcmc-city-structure.html', encoding='utf-8').read()
head = tmpl[:tmpl.find('<title>')]
style = tmpl[tmpl.find('<style>'):tmpl.find('</head>')]
foot = tmpl[tmpl.find('<footer>'):]
DESC = '충칭시는 서울의 136배, 인구 3,187만 명. 장강과 자링강이 만나는 반도에서 시작해 강 건너편과 북쪽 신도시로 커진 순서, 리쯔바역과 훙야둥, 임시정부와의 인연까지 정리했다.'
body = f'''<body>
<div class="top-eyebrow"><div class="wrap"><a class="brand-mark" href="https://brandongsan.com/"><span class="bm-b">브</span><span class="bm-rest">동산</span></a><a class="list-btn" href="https://brandongsan.com/city-story.html">☰ 목록</a></div></div>
<div class="wrap">
  <div class="titleblock"><h1>{TITLE}</h1></div>
  <div class="byline"><span class="avatar">브</span><span class="who">서당개</span><span class="dot">·</span><span class="when">{DATEL}</span><span class="tag">{TAG}</span></div>
</div>
<div class="hairline"></div>
<div class="content"><div class="wrap">

{img('cover', '장강과 자링강이 만나는 충칭 차오톈먼 일대를 드론으로 내려다본 모습', '장강과 자링강이 만나는 차오톈먼 일대 · ' + PX)}
<section><p class="lede">충칭 사진을 보면 길이 머리 위에도 있고 발밑에도 있다. 열차가 아파트 건물을 뚫고 지나가고, 11층에서 나가도 1층에서 나가도 길이다. 사람들이 이 도시를 '8D 도시'라고 부르는 이유다. 충칭은 왜 이렇게 입체적인 모양이 됐을까?</p></section>

<section><h2>1. 서울의 136배, 남한의 82%</h2>
<p>먼저 크기부터 보자. 충칭시 면적은 82,400㎢다. 서울(605㎢)의 136배, 남한 면적의 82%쯤 된다. 충칭은 성(省)과 같은 급의 직할시라서, 시 경계 안에 도시뿐 아니라 산골 마을과 농촌까지 들어 있다.</p>
{img('map-size', '충칭시 경계 위에 서울과 남한을 같은 축척으로 겹쳐 본 지도', '같은 축척으로 겹쳐 본 충칭시(황동색), 서울(흰색), 남한(점선) · ' + MAPCAP)}
<p>2025년 말 충칭시 상주인구는 3,187만 명으로 서울의 세 배가 넘는다. 다만 우리가 '충칭'이라고 떠올리는 중심 시가지에 사는 사람은 2024년 기준 1,058만 명이다.</p>
<div class="tbl-wrap"><table class="rule"><thead><tr><th>항목</th><th>충칭</th><th>서울</th></tr></thead><tbody>
<tr><td>면적</td><td>82,400㎢</td><td>605㎢</td></tr>
<tr><td>인구(2025년 말)</td><td>3,187만 명</td><td>934만 명</td></tr>
<tr><td>중심 시가지 인구(2024)</td><td>1,058만 명</td><td>—</td></tr>
<tr><td>도시화율</td><td>73.0%</td><td>—</td></tr>
<tr><td>다리</td><td>2만 개 이상</td><td>—</td></tr>
<tr><td>도시철도(2025년 말)</td><td>582.6km</td><td>—</td></tr>
</tbody></table></div>
<p class="note">출처: 충칭시 통계국 2025 통계공보, 제일재경, 인민일보, 중국도시궤도교통협회, 통계청(서울 인구)</p>
</section>

<section><h2>2. 두 강이 만나는 반도에서 시작했다</h2>
<p>충칭 한가운데에서 장강(양쯔강)과 자링강이 만난다. 두 강 사이로 혀처럼 튀어나온 땅이 위중반도이고, 그 끝이 차오톈먼이다. 위중반도의 면적은 24㎢로 서울 종로구만 하다. 충칭은 이 좁은 반도에서 시작했다.</p>
{img('map-rivers', '장강과 자링강 사이의 위중반도를 표시한 개략도', '두 강 사이의 위중반도(황동색) · ' + MAPCAP)}
<p>땅이 좁고 비탈지다 보니 사람들은 강가 절벽에 기둥을 세우고 집을 올렸다. 이런 집을 댜오자오러우(吊脚楼)라고 한다. 지금 관광지로 유명한 훙야둥은 그 모습을 되살려 2006년 충칭시가 지은 거리다.</p>
{img('hongyadong', '절벽에 층층이 붙은 훙야둥 건물', '훙야둥 · ' + PX)}
<p>충칭이라는 이름은 1189년에 생겼다. 남송의 왕자가 이 지역의 왕으로 봉해진 뒤 황제가 되자 '두 번 겹친 경사'라는 뜻으로 충칭부(重慶府)라 불렀다. 강은 이 도시의 길이었다. 장강 뱃길은 상하이까지 이어졌고, 1891년 충칭은 내륙 도시로는 처음 외국에 항구를 열었다.</p>
{img('river', '밤의 장강을 지나는 유람선과 차오톈먼 대교', '밤의 장강과 차오톈먼 대교 · ' + PX)}
<p>1937년 11월부터 1946년 5월까지는 중일전쟁을 피해 옮겨 온 중화민국의 임시 수도였다. 관청과 사람이 몰려들면서 반도 밖으로 도시가 넘치기 시작했다. 1997년에는 베이징·상하이·톈진에 이어 네 번째 직할시가 됐다.</p>
</section>

<section><h2>3. 사람들은 세 번 옮겨 갔다</h2>
<p>주거와 상업의 중심은 크게 세 번 옮겨 갔다.</p>
<h3>① 위중반도 · ~1960년대</h3>
<p>오랫동안 충칭의 중심은 반도 한가운데 제팡베이 일대였다. 좁은 땅에 상점과 관청, 집이 층층이 들어찼다.</p>
{img('map-axis-1', '1단계: 위중반도와 제팡베이를 표시한 개략도', '①단계 · ' + MAPCAP)}
{img('jiefangbei', '해 질 녘 제팡베이 일대의 고층 빌딩', '제팡베이 일대 · ' + PX)}
<h3>② 강 건너편으로 · 1966년~</h3>
<p>1966년 1월 시내에 처음으로 강을 건너는 다리(뉴자오퉈 자링강대교)가 놓였다. 그전에는 배를 타야 강을 건널 수 있었다. 다리가 하나씩 늘면서 북쪽 장베이의 관인차오, 남쪽 난안의 난핑, 서쪽 사핑바, 주룽포의 양자핑으로 동네가 퍼졌다. 2003년 사핑바 싼샤광장과 양자핑이 차례로 상권으로 자리 잡았다. 지금 중심 시가지에서 강을 건너는 다리는 38개다.</p>
{img('map-axis-2', '2단계: 강 건너 관인차오, 난핑, 사핑바, 양자핑을 표시한 개략도', '②단계 · ' + MAPCAP)}
{img('bridge', '붉은 둥수이먼 대교 아래층을 지나는 모노레일', '둥수이먼 대교 · ' + PX)}
<h3>③ 북쪽 신도시 량장신구 · 2010년~</h3>
<p>2010년 6월 18일 국가급 신구인 량장신구가 생겼다. 두 강이 만나는 맞은편 장베이쭈이에 금융가가 들어섰고, 북쪽 리자와 웨라이, 공항 가는 길에 새 아파트 단지가 생겼다. 2025년 11월에는 장베이구·위베이구와 합쳐 면적 약 1,360㎢, 인구 약 352만 명의 구가 됐다.</p>
{img('map-axis-3', '3단계: 북쪽 량장신구와 장베이쭈이, 리자, 웨라이를 표시한 개략도', '③단계 · ' + MAPCAP)}
</section>

<section><h2>4. 산비탈 위로 쌓은 집</h2>
<p>지금 충칭 사람 대부분은 산비탈에 선 고층 아파트에 산다. 평지가 모자라니 위로 올렸고, 건물 사이가 아주 좁다.</p>
{img('highrise', '좁은 간격으로 붙어 선 충칭의 고층 아파트', '충칭의 고층 아파트 · ' + PX)}
<p>길도 산 중턱마다 나 있다. 그래서 건물과 건물을 공중 다리로 잇기도 하고, 건물 중간층이 도로와 바로 닿기도 한다. 11층짜리 훙야둥은 1층이 강변도로, 11층이 위쪽 창바이로에 닿는다. 어느 층으로 나가도 길인 셈이다.</p>
{img('skybridge', '고층 건물 사이를 잇는 공중 다리', '건물 사이 공중 다리 · ' + PX)}
{img('hongyadong_day', '낮에 올려다본 훙야둥', '낮의 훙야둥 · ' + PX)}
</section>

<section><h2>5. 3,187만 명이 사는 도시</h2>
<p>충칭시 사람 열 명 중 일곱은 도시에 산다. 2025년 도시화율은 73.0%였다. 인구는 2023년부터 3년째 조금씩 줄었지만, 2025년에도 밖에서 들어온 사람이 나간 사람보다 11만 명 넘게 많았다. 출생아가 줄어든 만큼을 유입이 메우는 구조다.</p>
{img('street', '제팡베이 근처 골목의 노점과 사람들', '시내 골목 · ' + PX)}
<p>오래된 거리 츠치커우에는 비 오는 날에도 사람이 몰리고, 저녁이면 골목마다 매운 훠궈와 길거리 음식 냄새가 퍼진다.</p>
{img('ciqikou', '비 오는 날 츠치커우 옛 거리', '츠치커우 · ' + PX)}
</section>

<section><h2>6. 모노레일과 다리의 도시</h2>
<p>이 도시 교통의 상징은 건물을 뚫고 지나가는 모노레일이다. 2호선 리쯔바역은 19층 건물 안에 있다. 1~5층은 상가와 사무실, 6~8층은 역(대합실·설비·승강장), 9~19층은 집이다. 역과 건물은 1998년에 함께 설계됐다. 설계자는 선로를 돌리거나 건물을 다른 곳에 짓는 대신, 비용을 줄이려고 둘을 한 건물에 넣었다고 설명한다.</p>
{img('liziba', '리쯔바역 건물을 통과하는 2호선 모노레일', '리쯔바역 · ' + PX)}
<p>산이 많은 충칭은 가파른 비탈과 급한 곡선을 잘 타는 모노레일을 일찍 깔았다. 2025년 말 도시철도는 582.6km이고, 그중 모노레일이 98.45km다. 2026년 11월 12일에는 무인으로 달리는 급행선 15호선 일부 구간도 열렸다.</p>
<p>다리는 2만 개가 넘는다. 장강과 자링강을 건너는 큰 다리만 105개라서 충칭은 '다리의 도시(橋都)'로도 불린다.</p>
{img('nightbridge', '불이 켜진 밤의 다리 아래층을 지나는 열차', '밤의 다리 · ' + PX)}
</section>

<section><h2>7. 한국과 이어진 도시</h2>
<p>1919년 상하이에서 출범한 대한민국 임시정부는 일본의 추격을 피해 항저우, 전장, 창사, 광저우, 류저우, 치장을 거쳐 1940년 9월 충칭에 자리 잡았다. 같은 달 17일 이곳에서 한국광복군이 창설됐고, 임시정부는 1945년 11월 귀국할 때까지 충칭에 머물렀다. 마지막 청사(위중구 롄화츠)는 지금 기념관으로 남아 있다.</p>
{img('map-route', '대한민국 임시정부가 상하이에서 충칭까지 옮겨 간 경로', '임시정부 이동 경로(연도는 도착 기준) · ' + MAPCAP)}
<p>한국 기업도 이 도시에 들어왔다. SK하이닉스는 2014년 7월부터 충칭에서 낸드플래시 패키징·테스트 공장을 운영해 왔다. 2026년 8월에는 이 공장 지분 매각을 검토한다는 보도가 나왔고, 회사는 "확정된 것은 없다"고 밝혔다. 현대차는 충칭에 공장을 지었다가 2024년 1월 매각했다.</p>
{img('raffles', '흐린 날의 충칭 래플스 시티와 장강', '래플스 시티와 장강 · ' + PX)}
</section>

<section><h2>8. 한국에서 가는 법</h2>
{img('map-flight', '인천에서 충칭 장베이 공항까지 항로', '인천 → 충칭 항로(개략) · ' + MAPCAP)}
<div class="tbl-wrap"><table class="rule"><thead><tr><th>항목</th><th>내용</th></tr></thead><tbody>
<tr><td>비행</td><td>인천–충칭 직항 약 4시간 5분(돌아오는 편 약 3시간 35분)</td></tr>
<tr><td>시차</td><td>한국보다 1시간 늦다</td></tr>
<tr><td>비자</td><td>한국 일반여권 30일 무비자, 2026년 12월 31일까지(2027년 연장은 11월 17일 현재 미발표)</td></tr>
<tr><td>항공권</td><td>검색 기준 왕복 약 30만~55만 원(직항·경유, 시기에 따라 다르다)</td></tr>
</tbody></table></div>
<p class="note">비자 조건과 항공권 값은 바뀔 수 있다. 출국 전에 주한중국대사관 공지와 항공사 일정을 다시 확인하자.</p>
</section>

<section><h2>9. 정리</h2>
<div class="tbl-wrap"><table class="rule"><thead><tr><th>연도</th><th>일어난 일</th><th>도시 모양으로 보면</th></tr></thead><tbody>
<tr><td>1189</td><td>충칭부라는 이름</td><td>두 강 합류부의 성곽 도시</td></tr>
<tr><td>1891</td><td>내륙 도시 첫 개항</td><td>장강 뱃길 항구</td></tr>
<tr><td>1937~1946</td><td>중화민국 임시 수도</td><td>반도 밖으로 넘친 도시</td></tr>
<tr><td>1940~1945</td><td>대한민국 임시정부</td><td>한국과의 인연</td></tr>
<tr><td>1966</td><td>시내 첫 강 다리</td><td>강 건너편으로 확장</td></tr>
<tr><td>1997</td><td>네 번째 직할시</td><td>시 경계 82,400㎢</td></tr>
<tr><td>2010</td><td>량장신구 출범</td><td>북쪽 신도시</td></tr>
<tr><td>2025~2026</td><td>량장신구 통합, 15호선 개통</td><td>북쪽 축이 커지고 철도 확장</td></tr>
</tbody></table></div>
<p>정리하면 충칭은 두 강이 만나는 좁은 반도에서 시작해, 다리를 놓아 강 건너편으로, 다시 북쪽 신도시로 커졌다. 평지가 모자란 산 위에서 커지다 보니 길과 집과 철도를 층층이 쌓을 수밖에 없었고, 그 결과가 지금의 '8D 도시'다.</p>
<p class="note">이 글은 브동산 유튜브 '도시이야기 2 · 충칭' 영상과 함께 만들었다.</p>
</section>

<section><h2>참고한 자료</h2><p class="note">{SRC_LINKS}</p>
<p class="note">사진: Pexels 영상 캡처(Pexels License). 지도: 브동산 자체 제작 개략도(© OpenStreetMap contributors · Natural Earth).</p></section>

<section id="related">
  <h2>도시이야기의 다른 포스팅</h2>
  <p class="related-empty">다음 도시 이야기를 준비 중입니다.</p>
  <div class="list-more"><a class="btn-list" href="https://brandongsan.com/city-story.html">도시이야기 목록 전체보기</a></div>
</section>

</div></div>

'''
meta = f'''<title>{TITLE} | 브동산</title>
<meta name="description" content="{esc(DESC)}">
<link rel="canonical" href="{URL}">
<meta property="og:type" content="article"><meta property="og:title" content="{esc(TITLE)}"><meta property="og:description" content="{esc(DESC)}"><meta property="og:image" content="{IMGURL}cover.jpg"><meta property="og:url" content="{URL}">
'''
site = head + meta + style + '</head>\n' + body + foot
site = site.replace('<p class="lede">', '<p class="lede">', 1)
open(REPO + f'posts/{SLUG}.html', 'w', encoding='utf-8').write(site)
print('site', len(site))

# ---------------- 네이버용 (해요체, 구성 다르게)
NTAGS = '충칭,중경,충칭여행,8D도시,리쯔바역,훙야둥,츠치커우,장강,자링강,대한민국임시정부,중국무비자,중국여행,도시이야기,도시구조,브동산'
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
cover_candidates: cover-n.jpg (대표사진 = 차오톈먼 드론 사진)
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

<p><strong>중국 충칭은 면적 82,400㎢로 서울의 136배, 인구 3,187만 명이 사는 도시예요. 열차가 19층 건물을 뚫고 지나가고 11층에서 나가도 길이 나오는, 이른바 '8D 도시'가 된 이유를 지도와 사진으로 정리했어요.</strong></p><p style="color:#8A8A8A;font-size:13px;">브동산 · {TAG} · {DATEL}</p>
<h1>{NTITLE}</h1>

{img('cover', '장강과 자링강이 만나는 충칭 차오톈먼 일대 드론 사진', '두 강이 만나는 차오톈먼 일대 · ' + PX, True)}

{h2('충칭 한눈에 보기')}
<table {T2}><tbody>
{tr('위치', '중국 서남부, 장강과 자링강이 만나는 곳')}
{tr('면적', '82,400㎢ · 서울의 136배, 남한의 약 82%')}
{tr('인구', '3,187만 명(2025년 말) · 중심 시가지 1,058만 명(2024)')}
{tr('별명', '산성(山城), 다리의 도시, 8D 도시')}
{tr('한국에서', '인천 직항 약 4시간 · 시차 1시간')}
</tbody></table>
{img('map-size', '충칭시 경계 위에 서울과 남한을 같은 축척으로 겹친 지도', '같은 축척으로 겹쳐 본 충칭시·서울·남한 · ' + MAPCAP, True)}
<p>충칭은 성(省)과 같은 급의 직할시라서 시 경계 안에 산골과 농촌까지 들어 있어요. 우리가 사진으로 보는 고층 빌딩 숲은 그 가운데 작은 부분이에요.</p>

{h2('충칭이 8D 도시가 된 이유 3가지')}
<h3>① 두 강이 만나는 좁은 반도에서 시작했어요</h3>
<p>장강과 자링강 사이 혀처럼 튀어나온 위중반도(24㎢, 서울 종로구만 한 땅)가 충칭의 출발점이에요.</p>
{img('map-rivers', '장강과 자링강 사이의 위중반도 개략도', MAPCAP, True)}
<h3>② 평지가 거의 없는 산 위 도시예요</h3>
<p>땅이 모자라니 건물은 위로 올라갔어요. 지금 충칭 사람 대부분이 산비탈 고층 아파트에 살아요.</p>
{img('highrise', '좁은 간격으로 선 충칭 고층 아파트', PX, True)}
<h3>③ 그래서 길과 집을 층층이 쌓았어요</h3>
<p>예전엔 절벽에 기둥을 세워 집(댜오자오러우)을 올렸고, 지금은 건물 중간층이 길과 바로 닿아요. 훙야둥은 1층도 길, 11층도 길이에요.</p>
{img('hongyadong', '절벽에 층층이 붙은 훙야둥', PX, True)}

{h2('충칭에서 꼭 보는 장면 4곳')}
<p><b>1) 리쯔바역</b> — 2호선 모노레일이 19층 건물의 6~8층을 지나가요. 1~5층은 상가, 9~19층은 집이에요. 역과 건물은 1998년에 함께 설계됐어요.</p>
{img('liziba', '리쯔바역 건물을 통과하는 모노레일', PX, True)}
<p><b>2) 훙야둥</b> — 2006년 충칭시가 옛 댜오자오러우 모습을 되살려 지은 11층 거리예요. 밤 조명이 유명해요.</p>
{img('hongyadong_day', '낮에 올려다본 훙야둥', PX, True)}
<p><b>3) 차오톈먼</b> — 두 강이 만나는 반도 끝이에요. 1891년 내륙 도시로는 처음 외국에 항구를 연 곳이 이 강가예요.</p>
{img('river', '밤의 장강과 차오톈먼 대교', PX, True)}
<p><b>4) 츠치커우</b> — 오래된 옛 거리예요. 비 오는 날에도 사람이 몰리고, 저녁엔 훠궈와 길거리 음식이 가득해요.</p>
{img('ciqikou', '비 오는 날 츠치커우 옛 거리', PX, True)}

{h2('주거 중심은 이렇게 옮겨 갔어요')}
<table {T2}><tbody>
{tr('① ~1960년대', '위중반도 제팡베이 일대')}
{tr('② 1966년~', '시내 첫 강 다리 이후 강 건너 관인차오·난핑·사핑바·양자핑')}
{tr('③ 2010년~', '북쪽 신도시 량장신구(장베이쭈이 금융가, 리자, 웨라이)')}
</tbody></table>
{img('map-axis-3', '량장신구까지 넓어진 충칭 시가지 개략도', '③단계까지 넓어진 시가지 · ' + MAPCAP, True)}
<p>2025년 11월에는 량장신구가 장베이구·위베이구와 합쳐 인구 약 352만 명의 구가 됐어요. 지금 중심 시가지에서 강을 건너는 다리만 38개예요.</p>

{h2('숫자로 보는 충칭의 길')}
<table {T2}><tbody>
{tr('도시철도', '582.6km(2025년 말), 그중 모노레일 98.45km')}
{tr('새 노선', '15호선 일부 구간 2026년 11월 12일 개통 · 무인 급행')}
{tr('다리', '2만 개 이상 · 장강·자링강을 건너는 큰 다리 105개')}
</tbody></table>
{img('nightbridge', '불이 켜진 밤의 다리 아래층을 지나는 열차', PX, True)}

{h2('한국과는 어떤 인연이 있나요?')}
<ul>
<li>1919년 상하이에서 출범한 대한민국 임시정부가 일곱 번 옮겨 다닌 끝에 1940년 9월 충칭에 자리 잡았어요.</li>
<li>1940년 9월 17일 한국광복군이 충칭에서 창설됐고, 임시정부는 1945년 11월 귀국 때까지 이곳에 있었어요. 마지막 청사는 기념관으로 남아 있어요.</li>
<li>SK하이닉스는 2014년부터 충칭에서 반도체 패키징·테스트 공장을 운영해 왔어요(2026년 8월 지분 매각 검토 보도, 회사는 확정된 것 없다고 밝힘). 현대차는 2024년 충칭 공장을 팔았어요.</li>
</ul>
{img('map-route', '대한민국 임시정부가 상하이에서 충칭까지 옮겨 간 경로', '임시정부 이동 경로 · ' + MAPCAP, True)}

{h2('한국에서 가는 법 체크리스트')}
<table {T2}><tbody>
{tr('비행', '인천 직항 약 4시간 5분 · 돌아오는 편 약 3시간 35분')}
{tr('시차', '한국보다 1시간 늦어요')}
{tr('비자', '30일 무비자, 2026년 12월 31일까지(2027년 연장은 11월 17일 현재 미발표)')}
{tr('항공권', '검색 기준 왕복 약 30만~55만 원(시기·경유에 따라 달라요)')}
</tbody></table>
{img('map-flight', '인천에서 충칭까지 항로', MAPCAP, True)}
<p>비자 조건과 항공권 값은 바뀔 수 있어요. 출국 전에 주한중국대사관 공지와 항공사 일정을 꼭 다시 확인하세요.</p>

{h2('마무리')}
<p>충칭은 두 강 사이 좁은 반도에서 시작해 다리를 놓아 강 건너로, 다시 북쪽 신도시로 커졌어요. 평지 없는 산 위에서 커지다 보니 길과 집과 철도를 층층이 쌓았고, 그게 지금의 '8D 도시'예요.</p>
<p>지도와 연표를 더 자세히 담은 글은 브동산 홈페이지 도시이야기에 있어요.</p>

<p> </p><p style="color:#8A8A8A;font-size:13px;">출처: {'; '.join(t.split(' — ')[0] for t, u in S.SOURCES)}. 사진은 Pexels 영상 캡처, 지도는 브동산 자체 제작 개략도(© OpenStreetMap contributors · Natural Earth)예요.</p>
<p style="color:#8A8A8A;font-size:13px;">태그: {' '.join('#' + t for t in NTAGS.split(','))}</p>

</body></html>
'''
open(OUTN + f'{SLUG}-naver.html', 'w', encoding='utf-8').write(nv)
print('naver', len(nv))
