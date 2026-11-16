import json, sys, os
sys.path.insert(0,'.')
from texts2 import T
d=json.load(open('result2.json'))
# 회차 기준일: 환경변수 RANK_DATE=YYYY-MM-DD (기본 2026-11-16, 첫 회차)
RD=os.environ.get('RANK_DATE','2026-11-16'); _y,_m,_d=[int(x) for x in RD.split('-')]
SLUG=os.environ.get('RANK_SLUG','sudogwon-firstcome-top30-202611' if RD=='2026-11-16' else f"sudogwon-firstcome-top30-{_y}{_m:02d}{_d:02d}")
D_DOT=f"{_y}.{_m:02d}.{_d:02d}"; D_SP=f"{_y}. {_m}. {_d}"; D_KO=f"{_y}년 {_m}월 {_d}일"; D_MD=f"{_m}월 {_d}일"
OUT=sys.argv[1] if len(sys.argv)>1 else 'out'
os.makedirs(OUT,exist_ok=True)
def fmt(v,unit=True):
    w=round(v*1e4/10)*10; s='+' if w>0 else '-' if w<0 else '±'; a=abs(w)
    return f"{s}{a/10000:.2f}억{'원' if unit else ''}" if a>=10000 else f"{s}{a:,}만{'원' if unit else ''}"
def eok(v): return f"{v:.2f}억"
def pct(o): return f"{o['pct']:+.1f}%"
NN=len(d); NP=sum(1 for o in d if o['final']>0); NB=sum(1 for o in d if o['pct']<=-10)
NS=sum(1 for o in d if -5<o['pct']<=0)
top=d[:3]; by={o['key']:o for o in d}
BASE=f'https://www.brandongsan.com/posts/images/{SLUG}/'
def size(o): return o.get('size','84')
def status_word(o): return '준공' if o.get('done') else '입주예정'
LTAG={'L1':'실질가','L2':'자기 시세','L3':'미분양 상한','L4':'+상한','L5':'비교단지 교체'}
def tags(o): return ' '.join(LTAG[n[0]] for n in o['notes'] if n[0] in LTAG)

LESSONS=[
 ('L1','실질 분양가로 비교한다','확정된 현금 페이백·입주축하금은 분양가에서 뺀다. 오목천역 더리브는 84㎡ 1억원 페이백과 이자 지원 1천만원이 붙어 실질 6.59억원으로 계산했다.'),
 ('L2','준공 단지는 자기 단지 시세가 답이다','이미 지어진 단지는 같은 단지 실거래가 곧 적정가다. 계약금이 묶여 있지 않으니 6-1 마피 조정도 하지 않는다. 고촌센트럴자이·힐스테이트 수원파크포레·힐스테이트 이천역에 적용했다.'),
 ('L3','옆 미분양 단지 가격이 천장이다','주변에 먼저 나온 단지가 아직 안 팔렸거나 분양가 아래로 거래되면, 새 단지 적정가는 그 가격을 넘을 수 없다. 새 단지 점수가 더 낮으면 천장도 그만큼 낮춘다. 브레인시티 세 곳·화서역 아너스빌·이천역 예미지에 적용했다.'),
 ('L4','+5%가 넘으면 먼저 의심한다','선착순으로 남아 있다는 건 시장이 아직 그 가격에 확신이 없다는 뜻이다. 계산이 +5%를 넘으면 비교단지부터 다시 고르고, 그래도 남으면 계약금(분양가 10%)을 상한으로 둔다. 이번에는 재검토 후 +5%를 넘는 단지가 없어 상한을 쓸 일이 없었다.'),
 ('L5','비교단지는 같은 동네 신축으로','다른 생활권의 역세권 대장이나 20년 넘은 구축만 쓰면 값이 크게 틀어진다. 같은 동·지구의 10년 이내 신축이나 분양권으로 바꾼다. 그런 단지가 아예 없으면 결과에 그 사실을 적는다.'),
]
RE=[o for o in d if o.get('v1')]
RE.sort(key=lambda o:-o['v1']['pct'])

SRC=[
('국민일보 2026.11.15 — 상동역 롯데캐슬 시그니처 선착순 동·호 지정','https://www.kmib.co.kr/article/20261115501388'),
('뉴스핌 2026.11.13 — 향남역 그로브 스위첸 선착순','https://www.newspim.com/news/view/20261113001016'),
('뉴데일리 2025.11.03 — 브레인시티 6개 단지 84㎡ 분양가·청약 결과·선착순 현황','https://biz.newdaily.co.kr/site/data/html/2025/11/03/2025110300160.html'),
('리치고 — 평택브레인시티중흥S-클래스 34평 호가(2026.11.02)','https://m.richgo.ai/realty/community/%ED%8F%89%ED%83%9D%EC%8B%9C-e200f49b8f82/%ED%8F%89%ED%83%9D%EB%B8%8C%EB%A0%88%EC%9D%B8%EC%8B%9C%ED%8B%B0%EC%A4%91%ED%9D%A5S-%ED%81%B4%EB%9E%98%EC%8A%A4-34%ED%8F%89-%EB%A7%A4%EB%AC%BC-%EC%9D%BC%EC%A3%BC%EC%9D%BC%EC%83%88-13%E2%86%9226%EA%B1%B4%EC%9C%BC%EB%A1%9C-%EB%8A%98%EC%96%B4-%E2%80%94-%ED%8F%89%ED%83%9D%EC%8B%9C-%EB%A7%A4%EB%AC%BC-%EC%B2%B4%ED%81%AC-88206'),
('listup24 — 브레인시티 앤네이처 미래도 분양가','https://listup24.com/%ED%8F%89%ED%83%9D-%EB%B8%8C%EB%A0%88%EC%9D%B8%EC%8B%9C%ED%8B%B0-%EC%95%A4%EB%84%A4%EC%9D%B4%EC%B2%98-%EB%AF%B8%EB%9E%98%EB%8F%8410%EB%B8%94%EB%A1%9D-%EB%B6%84%EC%96%91%EA%B0%80-%EC%B2%AD%EC%95%BD/'),
('listup24 — 브레인시티 메디스파크 로제비앙 모아엘가 분양가','https://listup24.com/%EB%B8%8C%EB%A0%88%EC%9D%B8%EC%8B%9C%ED%8B%B0-%EB%A9%94%EB%94%94%EC%8A%A4%ED%8C%8C%ED%81%AC-%EB%A1%9C%EC%A0%9C%EB%B9%84%EC%95%99-%EB%AA%A8%EC%95%84%EC%97%98%EA%B0%80-%EB%B6%84%EC%96%91%EA%B0%80/'),
('mhb-blog — 평택 고덕 우미린 프레스티지','https://mhb-blog.com/yeongtaek-godeok-woomirin-prestige-subscription-guide/'),
('mhb-blog — 고덕국제신도시 수자인풍경채 2단지','https://mhb-blog.com/?p=6145'),
('mhb-blog — 고덕국제신도시 수자인하우스디','https://mhb-blog.com/godeok-sujain-housedy-subscription-guide/'),
('분양홈 — 여주역 로제비앙 더센텀','https://brandhome.kr/yj-logebien/'),
('mhb-blog — 시티오씨엘 9단지 오션파크뷰','https://mhb-blog.com/?p=8842'),
('mhb-blog — 인하대역 수자인 로이센트','https://mhb-blog.com/%EC%9D%B8%ED%95%98%EB%8C%80%EC%97%AD-%EC%88%98%EC%9E%90%EC%9D%B8-%EB%A1%9C%EC%9D%B4%EC%84%BC%ED%8A%B8-%EC%B2%AD%EC%95%BD-%EC%99%84%EB%B2%BD-%EB%B6%84%EC%84%9D-%EB%B6%84%EC%96%91%EA%B0%80-%EC%9D%BC/'),
('mhb-blog — 영종 디에트르 라 메르','https://mhb-blog.com/%EC%9D%B8%EC%B2%9C%EC%98%81%EC%A2%85%EA%B5%AD%EC%A0%9C%EB%8F%84%EC%8B%9C-%EB%94%94%EC%97%90%ED%8A%B8%EB%A5%B4-%EB%9D%BC-%EB%A9%94%EB%A5%B4-%EB%B3%B8%EC%B2%AD%EC%95%BD-%EC%99%84%EB%B2%BD-%EA%B0%80/'),
('mhb-blog — 포레나더샵 인천시청역','https://mhb-blog.com/forena-the-sharp-incheon-city-hall-station-subscription-guide/'),
('mhb-blog — 연수 월드메르디앙 어반포레','https://mhb-blog.com/yeonsu-world-meridian-urban-fore-subscription-guide/'),
('mhb-blog — 두산위브더제니스 부천','https://mhb-blog.com/?p=8545'),
('mhb-blog — 엘리프 한신더휴 수원 D3','https://mhb-blog.com/%EC%97%98%EB%A6%AC%ED%94%84-%ED%95%9C%EC%8B%A0%EB%8D%94%ED%9C%B4-%EC%88%98%EC%9B%90-d3%EB%B8%94%EB%A1%9D-%EC%B2%AD%EC%95%BD-%ED%95%B5%EC%8B%AC-%EC%A0%95%EB%B3%B4-%EB%B6%84%EC%96%91%EA%B0%80/'),
('mhb-blog — 화서역 호수공원 아너스빌','https://mhb-blog.com/hwaseo-station-lake-park-honorsville-subscription-guide/'),
('헤럴드경제 2026.01.20 — 힐스테이트 수원파크포레 준공 후 분양','https://www.heraldk.com/article/2026012016174208682'),
('뉴시스 2026.07.24 — 힐스테이트 수원파크포레 10% 페이백·오목천역 더리브 84㎡ 페이백','https://mobile.newsis.com/view/NISX20260724_0003722536'),
('뉴데일리 2025.12.17 — 이천 중리 B3블록 예미지·힐스테이트 이천역 마피','https://biz.newdaily.co.kr/site/data/html/2025/12/17/2025121700089.html'),
('비즈중앙 — 힐스테이트 이천역 84㎡ 평균 분양가','https://www.bizjoongang.co.kr/news/articleView.html?idxno=39132'),
('위키트리 — 쌍용 더 플래티넘 한강 분양가','https://www.wikitree.co.kr/articles/1165261'),
('파이낸셜뉴스 2026.10.07 — 쌍용 더 플래티넘 한강','https://www.fnnews.com/news/202610071151454050'),
('이코노미스트 2026.11.02 — 오남역 서희스타힐스 여의재 1단지','https://economist.co.kr/article/view/ecn202611020046'),
('mhb-blog — 오남역 서희스타힐스 여의재 1단지 무순위(84㎡ 6.7~7.2억)','https://mhb-blog.com/onam-station-seohee-starhills-yeouijae-1st-unranked-guide/'),
('리치고 — 고덕자이센트로','https://m.richgo.ai/realty/danji/a0hrFxe'),
('리치고 — 고덕국제신도시파라곤에듀포레','https://m.richgo.ai/realty/danji/a4qdMcE'),
('리치고 — 시티오씨엘3단지','https://m.richgo.ai/realty/danji/a8mwUBV'),
('리치고 — 시티오씨엘4단지','https://m.richgo.ai/realty/danji/a1DeRoF'),
('리치고 — 인천SK스카이뷰','https://m.richgo.ai/realty/danji/a4IvJYP'),
('리치고 — 인천시청역힐스테이트','https://m.richgo.ai/realty/danji/a5nCYmP'),
('리치고 — 인천시청역한신더휴','https://m.richgo.ai/realty/danji/a4jDohG'),
('리치고 — 서해그랑블포레스트','https://m.richgo.ai/realty/danji/a2xBhoe'),
('리치고 — 힐스테이트수원파크포레','https://m.richgo.ai/realty/danji/a2ybcjm'),
('리치고 — 화서역파크푸르지오','https://m.richgo.ai/realty/danji/a1ijqjF'),
('리치고 — 호매실역서희스타힐스','https://m.richgo.ai/realty/danji/a4qbeAb'),
('리치고 — 호반써밋수원','https://m.richgo.ai/realty/danji/a8MiTkd'),
('리치고 — 고촌센트럴자이','https://m.richgo.ai/realty/danji/a8YdeBg'),
('리치고 — 힐스테이트이천역2단지','https://m.richgo.ai/realty/danji/a0zdFlt'),
('리치고 — 오산대역세교자이','https://m.richgo.ai/realty/danji/a7TYhqq'),
('리치고 — 오산세교우미린레이크시티','https://m.richgo.ai/realty/danji/a2BlLEr'),
('집품 — 평택 고덕동 아파트 실거래','https://zippoom.com/지역별-부동산/경기-평택시-고덕동/아파트'),
('집품 — 인천 중구 중산동 아파트 실거래','https://zippoom.com/지역별-부동산/인천-중구-중산동/아파트'),
('집품 — 여주시 대장 아파트','https://zippoom.com/블로그/대장아파트/경기-여주시-아파트/2693'),
('집품 — 이천시 30평대 대장 아파트','https://zippoom.com/블로그/대장아파트/경기-이천시-아파트-30평/2343'),
('집품 — 양평군 30평대 대장 아파트','https://zippoom.com/블로그/대장아파트/경기-양평군-아파트-30평/2754'),
('집품 — 양수역이지움리버뷰','https://zippoom.com/%EB%B6%80%EB%8F%99%EC%82%B0/%EA%B2%BD%EA%B8%B0-%EC%96%91%ED%8F%89%EA%B5%B0-%EC%96%91%EC%84%9C%EB%A9%B4-%EC%96%91%EC%88%98%EC%97%AD%EC%9D%B4%EC%A7%80%EC%9B%80%EB%A6%AC%EB%B2%84%EB%B7%B0%EC%95%84%ED%8C%8C%ED%8A%B8/ju2npa'),
('아파트투유 — 서울·경기·인천 분양 목록(잔여세대·선착순 표기)','https://apttoyou.kr/apt'),
(f'다음 블로그 최신순 검색 — 단지별 선착순·잔여세대 영업 글({D_DOT} 확인)','https://search.daum.net/'),
]

# ---------- 사이트 ----------
STYLE="body{font-family:'Pretendard','Apple SD Gothic Neo','Malgun Gothic',sans-serif;line-height:1.8;font-size:16px;color:#111;background:#fff;max-width:760px;margin:0 auto;padding:24px 16px}h1{font-size:26px;line-height:1.4}h2{font-size:21px;margin-top:44px;border-top:1px solid #E3E3E3;padding-top:30px}h3{font-size:17px;margin-top:30px}table{width:100%;border-collapse:collapse;margin:14px 0;font-size:14px}th,td{border:1px solid #D8D8D8;padding:7px;vertical-align:top;text-align:left}th{background:#F5F5F5}.note{font-size:13px;color:#8A8A8A}.stat{border:1px solid #111;padding:14px 16px;margin:12px 0}.big{font-size:22px;font-weight:800}.byline{font-size:14px;color:#555}img{max-width:100%;display:block}a{color:#111}td.num{text-align:right;white-space:nowrap}.wrap{overflow-x:auto}"
rows=''.join(f"<tr><td class='num'>{o['rank']}</td><td>{'<b>' if o['rank']<=3 else ''}{o['name']}{'</b>' if o['rank']<=3 else ''}<br><span class='note'>{o['region']} · {size(o)}㎡</span></td><td class='num'>{eok(o['base'])}</td><td class='num'>{eok(o['fair'])}</td><td class='num'>{fmt(o['final'],False)}</td><td class='num'><b>{pct(o)}</b></td></tr>" for o in d)
rank_tbl=f"<div class='wrap'><table><thead><tr><th>순위</th><th>단지</th><th>기준 분양가</th><th>적정가격</th><th>예상 프리미엄</th><th>증감률</th></tr></thead><tbody>{rows}</tbody></table></div>"
ltbl="<table><thead><tr><th>번호</th><th>레슨런</th><th>내용</th></tr></thead><tbody>"+''.join(f"<tr><td>{k}</td><td><b>{t}</b></td><td>{x}</td></tr>" for k,t,x in LESSONS)+"</tbody></table>"
retbl="<table><thead><tr><th>단지</th><th>1차 계산</th><th>재검토 후</th><th>바뀐 이유</th></tr></thead><tbody>"+''.join(f"<tr><td>{o['name']}</td><td class='num'>{o['v1']['pct']:+.1f}%<br><span class='note'>{fmt(o['v1']['final'],False)}</span></td><td class='num'><b>{pct(o)}</b><br><span class='note'>{fmt(o['final'],False)}</span></td><td>{tags(o)}</td></tr>" for o in RE)+"</tbody></table>"
import os
IMG=json.load(open('images.json')) if os.path.exists('images.json') else {}
def imgstack(o):
    m=IMG.get(o['key'],{}); h=''
    for kind,lab in (('aerial','조감도'),('location','위치도')):
        x=m.get(kind)
        if x: h+=f"<img src='{BASE}{x['file']}' alt='{o['name']} {lab}' style='width:100%;display:block;'><p class='note'>{lab} · {x['src']}</p>"
    return h
def imgpair(o,naver=False):
    m=IMG.get(o['key'],{}); cells=[]; caps=[]
    for kind,lab in (('aerial','조감도'),('location','위치도')):
        x=m.get(kind)
        if not x: continue
        src=(x['file'] if naver else f"images/{SLUG}/{x['file']}")
        cells.append(f"<td style='width:50%;padding:2px;border:none'><img src='{src}' alt='{o['name']} {lab}' style='width:100%;display:block;'></td>")
        caps.append(f"{lab}: {x['src']}")
    if not cells: return ''
    return f"<table style='border:none'><tbody><tr>{''.join(cells)}</tr></tbody></table><p class='note'>이미지 · {' / '.join(caps)}</p>"
cards=''
for o in d:
    ct=''.join(f"{c['comp']} {eok(c['price'])}<span class='note'>({c['deal']}) → 보정 {eok(c['adj'])}</span><br>" for c in o['comps'])
    nt=''.join(f"<li class='note'>{x}</li>" for k,x in o['notes'])
    extra=''
    if o['basis']: extra=f"<li class='note'>원 계산값 {fmt(o['raw'])}에 {o['basis']}을 적용</li>"
    cards+=f"""<h3>{o['rank']}위. {o['name']} <span class='note'>{pct(o)}</span></h3>
<p class='note'>{o['region']} · {o['builder']} · {o['n']:,}세대 · {o['yr']}.{o['mo']:02d} {status_word(o)} · 평점 {o['score']}점</p>
<table><tbody><tr><th>분양가</th><td>{o['price_note']}{f" → 실질 {eok(o['base'])}" if o.get('benefit') else ''}</td></tr><tr><th>비교 기준</th><td>{ct}</td></tr><tr><th>적정가격</th><td>{eok(o['fair'])}</td></tr><tr><th>예상 프리미엄</th><td><b>{fmt(o['final'])} ({pct(o)})</b></td></tr></tbody></table>
{imgpair(o)}
<p>{T[o['key']][0]}</p>
{f"<ul>{nt}{extra}</ul>" if (nt or extra) else ''}
<p><b>{T[o['key']][1]}</b></p>
"""
site=f"""<!doctype html><html lang='ko'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>수도권 미분양 선착순 단지 TOP30, 지금 해볼 만한 단지가 있을까? | 브동산</title>
<meta name='description' content='{D_KO} 기준 수도권 미분양 선착순 아파트 30곳의 예상 프리미엄을 브동산 모형으로 계산해 분양가 대비 증감률 순으로 정리했다. 플러스는 2곳뿐이었다.'>
<style>{STYLE}</style></head><body>
<p class='byline'>브동산 · 수도권 미분양 선착순 랭킹 · {D_SP}</p>
<h1>수도권 미분양 선착순 단지 TOP30, 지금 해볼 만한 단지가 있을까?</h1>
<h2>1. 핵심 요약 — 지금 동·호수를 골라 살 수 있는 30곳, 남는 곳이 있나?</h2>
<p>청약통장 없이 동·호수를 골라 계약할 수 있는 수도권 미분양 선착순 단지 30곳을 브동산 모형으로 계산했다. <b>분양가보다 적정가격이 높게 나온 곳은 {NP}곳뿐이고, 그마저 +2%를 넘지 않았다.</b></p>
<div class='stat'><div class='note'>1위 · {top[0]['name']}</div><div class='big'>{pct(top[0])} ({fmt(top[0]['final'])})</div><div>기준 분양가 {eok(top[0]['base'])} · 적정가격 {eok(top[0]['fair'])}</div></div>
<p><b>1위 {top[0]['name']}({pct(top[0])}), 2위 {top[1]['name']}({pct(top[1])}), 3위 {top[2]['name']}({pct(top[2])})까지가 사실상 무피권이다.</b> 0~−5% 구간에 {NS}곳이 몰려 있고, −10%보다 나쁜 단지도 {NB}곳이다.</p>
<img src='images/{SLUG}/chart-top30.png' style='width:100%;display:block;' alt='수도권 미분양 선착순 TOP30 예상 프리미엄 증감률 순위 그래프'>
<p class='note'>이미지 01 · 분양가 대비 예상 프리미엄(%) 순위. 괄호 안은 금액.</p>
{rank_tbl}
<p class='note'>기준 분양가는 대표 타입 최고가이며, 확정된 현금 페이백은 뺐다(오목천역 더리브). 포레나더샵 인천시청역은 59㎡, 연수 월드메르디앙은 60㎡ 기준이다.</p>
<h2>2. 어떻게 골랐고, 어떻게 계산했나</h2>
<p>청약홈 무순위·임의공급은 뺐다. 기사·분양 사이트·미분양 집계에서 후보를 모은 뒤, 공식 분양 사이트에 선착순 동·호 지정이 떠 있거나 최근 한 달 안에 분양 상담사의 블로그·카페 영업 글이 있는 단지만 남겼다. 이렇게 31곳이 확인됐고, 84㎡ 최고 분양가와 비교 거래를 확인하지 못한 왕길역 로열파크씨티 푸르지오를 빼서 30곳이다.</p>
<p>계산은 브동산 약식 모형이다. 단지마다 평점(입지 40·브랜드 20·상품성 40)을 매기고, 비교단지 2곳의 최근 실거래를 평점 보정과 연령 보정(수도권 상한 1.2배)으로 고쳐 평균을 냈다. 84㎡가 없는 단지는 59·60㎡끼리 비교했다. 마이너스 1억원 안쪽은 선분양 수요를 감안해 절반으로, 1억~1.5억원은 계약금 하한을 감안해 3천만원 줄였다(6-1 조정). 순위는 금액이 아니라 분양가 대비 증감률로 매겼다. 16억원짜리와 5억원짜리를 같은 금액으로 비교할 수 없어서다.</p>
<h2>3. 순위별 단지 정보</h2>
{cards}
<h2>4. 숫자 뒤에 있는 리스크</h2>
<p>선착순 단지는 조건이 수시로 바뀐다. 계약금 정액제, 중도금 무이자, 발코니 무상 확장, 현금 페이백이 붙으면 실제 부담은 표보다 낮아진다. 이번 순위에는 84㎡에 적용이 확인된 페이백만 넣었다. 힐스테이트 수원파크포레는 113㎡ 10% 페이백이 보도됐는데, 84㎡에도 같은 조건이면 실질가 8.08억원, 프리미엄 +5,340만원(+6.6%)으로 1위가 된다. 계약 전에 꼭 확인할 부분이다.</p>
<p>분양가는 대표 타입 최고가로 맞췄다. 상동역 롯데캐슬(최고 49층), 영종 디에트르 라 메르, 쌍용 더 플래티넘 한강처럼 층·타입별 차이가 1억원 넘는 단지는 저층이나 다른 타입을 고르면 결과가 크게 달라진다.</p>
<p>비교 기준이 약한 단지도 있다. 오남역 서희스타힐스는 오남·진접에 10년 이내 신축 실거래가 없어 2009년식과 비교했고, 연수 월드메르디앙의 60㎡ 비교 거래 중 하나는 거래일이 표시되지 않은 인용값이다. 브레인시티 상한으로 쓴 중흥S-클래스 5.2억원은 실거래가 아니라 호가 평균이다.</p>
<h2>5. 결론 — 웃돈은 작아도, 실거주자에게는 고를 수 있는 시장</h2>
<p><b>계산상 웃돈이 크게 남는 단지는 없다. 대신 30곳 중 절반이 넘는 {NS+NP}곳이 시세와 5% 안쪽 차이다. 청약통장 없이, 원하는 동·호수를, 시세 수준에 고를 수 있다는 뜻이다. 살 동네가 정해진 실거주자에게는 분명한 기회다.</b></p>
<p>지금 바로 볼 만한 곳은 시세 수준이면서 입지 요건이 좋은 단지다. 병점 생활권 오산헤리티지자이, 바로 입주하는 고촌센트럴자이, 7호선 역 앞 상동역 롯데캐슬, 49층 대단지 시티오씨엘 9단지, 여주역 도보권 로제비앙, 향남역 예정지 옆 그로브 스위첸이 여기에 든다.</p>
<p>조건을 확인하면 기회가 되는 곳도 있다. 힐스테이트 수원파크포레는 84㎡에도 10% 페이백이 붙으면 1위가 되고, 오목천역 더리브는 역 앞 즉시입주에 1억원 페이백이 이미 붙어 있다. 구월아트파크·영종 디에트르·쌍용 더 플래티넘 한강처럼 층·타입별 가격 차이가 큰 단지는 저층이나 다른 타입을 고르면 격차가 크게 줄어든다.</p>
<p>선착순 단지는 판촉 조건이 붙는 순간 순위가 바뀐다. 브동산은 이 랭킹을 보름마다 다시 계산해 올린다.</p>
<h3>출처</h3>
<ul>{''.join(f"<li class='note'><a href='{u}'>{t}</a></li>" for t,u in SRC)}</ul>
<p class='note'>본 글은 정보 제공 목적이며 투자 권유나 매수·계약 대행이 아니다. 브동산 모형은 공개 실거래와 자체 평점으로 계산한 추정치이며, 실제 계약 전에는 입주자모집공고와 분양 사무실 안내를 확인해야 한다.</p>
</body></html>"""
open(f'{OUT}/{SLUG}.html','w').write(site)

# ---------- 네이버 ----------
NSTYLE="body{font-family:'Malgun Gothic','Apple SD Gothic Neo',sans-serif;line-height:1.8;font-size:16px;color:#000;max-width:720px;margin:0 auto;padding:24px}h1{font-size:25px}h2{font-size:21px}h3{font-size:17px}table{width:100%;border-collapse:collapse;margin:12px 0;font-size:14px}th,td{border:1px solid #D8D8D8;padding:7px;vertical-align:top}th{background:#F5F5F5}.note{font-size:13px;color:#8A8A8A}.stat{border:1px solid #111;padding:14px;margin:12px 0}img{max-width:100%}"
BL="<p>&nbsp;</p>"
ntop=''.join(f"<tr><td>{o['rank']}. {o['name']}</td><td style='white-space:nowrap'><b>{pct(o)}</b><br>{fmt(o['final'],False)}</td></tr>" for o in d)
ntbl=f"<table><thead><tr><th>순위·단지</th><th>프리미엄</th></tr></thead><tbody>{ntop}</tbody></table>"
def ncards(a,b,title,summ):
    gi=a//10+1
    h=f"<h3>{title}</h3>\n<!-- [이미지 삽입 자리] chart-m-{gi}.png : {title} 순위 그래프(모바일용) -->\n<img src='{BASE}chart-m-{gi}.png' alt='{title} 예상 프리미엄 순위' style='width:100%;display:block;'>\n<p class='note'>{title} · 분양가 대비 예상 프리미엄(%), 괄호는 금액</p>\n{BL}"
    for o in d[a:b]:
        h+=f"""<p><b>{o['rank']}위 {o['name']} · {pct(o)} ({fmt(o['final'],False)})</b></p>
{imgstack(o)}
<p>{o['region']} · {o['builder']} · {o['n']:,}세대 · {o['yr']}.{o['mo']:02d} {status_word(o)} · {o['price_note']}</p>
<p>{T[o['key']][1]}</p>
{BL}"""
    return h+f"<p><b>{summ}</b></p>"
def chunk(a,b):
    return "<table><thead><tr><th>순위</th><th>단지 정보</th><th>프리미엄</th><th>한줄평</th></tr></thead><tbody>"+''.join(f"<tr><td>{o['rank']}</td><td><b>{o['name']}</b><br>{o['region']} · {o['n']:,}세대 · {o['yr']}.{o['mo']:02d} {status_word(o)}<br>{o['price_note']}</td><td><b>{pct(o)}</b><br>{fmt(o['final'],False)}</td><td>{T[o['key']][1]}</td></tr>" for o in d[a:b])+"</tbody></table>"
nre="<table><thead><tr><th>단지</th><th>1차</th><th>재검토</th><th>이유</th></tr></thead><tbody>"+''.join(f"<tr><td>{o['name']}</td><td>{o['v1']['pct']:+.1f}%</td><td><b>{pct(o)}</b></td><td>{tags(o)}</td></tr>" for o in RE)+"</tbody></table>"
nles="<table><thead><tr><th>레슨런</th><th>한 줄 요약</th></tr></thead><tbody>"+''.join(f"<tr><td><b>{t}</b></td><td>{x.split('. ')[0]}.</td></tr>" for k,t,x in LESSONS)+"</tbody></table>"
nv=f"""<!doctype html><html lang='ko'><head><meta charset='utf-8'><title>수도권 미분양 선착순 단지 TOP30 | 지금 해볼 만한 단지 있을까?</title><style>{NSTYLE}</style></head><body>
<p class='note'>브동산 · 수도권 미분양 선착순 랭킹 · {D_SP} 기준</p>
<h1>수도권 미분양 선착순 단지 TOP30 | 지금 해볼 만한 단지 있을까?</h1>
{BL}
<h2>1. 결론부터 — 30곳 중 웃돈이 남는 곳은 {NP}곳</h2>
<p>청약통장 없이 동·호수를 골라 살 수 있는 수도권 미분양 선착순 단지 30곳을 브동산 방식으로 계산했습니다. <b>플러스는 {NP}곳, 그것도 +2% 안쪽이었습니다.</b></p>
<img src='{BASE}chart-summary.png' alt='수도권 미분양 선착순 TOP30 요약 인포그래픽' style='width:100%;display:block;'>
<p class='note'>이미지 01 · 1위 단지와 증감률 분포</p>
<p>1위 {top[0]['name']}의 브동산 분석 적정가격은 <b>{eok(top[0]['fair'])}원</b>, 분양가는 <b>{eok(top[0]['base'])}원</b>입니다.</p>
{BL}
{ntbl}
<p><b>순위는 금액이 아니라 분양가 대비 증감률입니다. 0~−5% 구간에 {NS}곳이 몰려 있고, −10%보다 나쁜 곳도 {NB}곳입니다.</b></p>
<p class='note'>분양가는 대표 타입 최고가, 확정된 현금 페이백만 차감. 포레나더샵 인천시청역 59㎡, 연수 월드메르디앙 60㎡ 기준.</p>
{BL}
<h2>2. 이렇게 계산했습니다</h2>
<img src='{BASE}chart-method.png' alt='브동산 모형 계산 순서' style='width:100%;display:block;'>
<p class='note'>이미지 02 · 계산 순서</p>
<table><tbody><tr><th>대상</th><td>{D_MD} 현재 선착순 동·호 지정 중인 수도권 아파트 30곳(청약홈 무순위 제외)</td></tr><tr><th>확정 기준</th><td>분양 홈페이지에 선착순이 떠 있거나, 최근 한 달 안에 분양 상담 글이 있는 단지</td></tr><tr><th>기준 평형</th><td>84㎡ 최고가(없으면 59·60㎡)</td></tr><tr><th>적정가격</th><td>같은 동네 신축 2곳의 실거래를 평점·연식으로 보정해 평균. 준공 단지는 자기 단지 시세, 옆 단지가 미분양이면 그 가격을 상한으로</td></tr><tr><th>순위</th><td>분양가 대비 증감률(%)</td></tr></tbody></table>
<p><b>16억원 단지와 5억원 단지를 같은 금액으로 비교할 수 없어, 순위는 증감률로 매겼습니다.</b></p>
{BL}
<h2>3. 순위별 단지 정보</h2>
{ncards(0,10,'1~10위','10위까지는 −3% 안쪽, 사실상 시세 수준 분양가입니다.')}
{ncards(10,20,'11~20위','11~20위는 −3%~−6%, 수천만원 차이라 실거주 요건이 좋으면 충분히 고를 만한 구간입니다.')}
{ncards(20,30,'21~30위','21위부터는 −6%~−26%입니다. 저층·다른 타입·판촉 조건으로 격차를 줄일 수 있는지가 열쇠입니다.')}
{BL}
<h2>4. 브동산 한줄평</h2>
<img src='{BASE}chart-picks.png' alt='브동산 한줄평 3묶음' style='width:100%;display:block;'>
<p class='note'>이미지 · 한줄평 3묶음</p>
<p><b>큰 웃돈을 노릴 시장은 아니지만, 실거주자에게는 통장 없이 원하는 동·호수를 시세 수준에 고를 수 있는 기회입니다.</b></p>
<table><thead><tr><th>구분</th><th>단지</th></tr></thead><tbody>
<tr><td><b>지금 볼 만한 곳</b><br>시세 수준 + 입지 요건 좋음</td><td>오산헤리티지자이 · 고촌센트럴자이 · 상동역 롯데캐슬 시그니처 · 시티오씨엘 9단지 · 여주역 로제비앙 더센텀 · 향남역 그로브 스위첸</td></tr>
<tr><td><b>조건 확인하면 기회</b><br>페이백·할인 조건</td><td>힐스테이트 수원파크포레(84㎡ 10% 페이백 여부) · 오목천역 더리브(1억원 페이백) · 화서역 호수공원 아너스빌 · 인하대역 수자인 로이센트</td></tr>
<tr><td><b>저층·타입이 열쇠</b><br>층·타입별 가격 차 큼</td><td>힐스테이트 구월아트파크 · 영종 디에트르 라 메르Ⅰ · 쌍용 더 플래티넘 한강</td></tr>
</tbody></table>
<p><b>살 동네가 정해져 있다면, 지금이 원하는 동·호수를 먼저 고를 수 있는 때입니다.</b></p>
{BL}
<h2>5. 결론</h2>
<p><b>계산상 웃돈은 작지만, 30곳 중 {NS+NP}곳이 시세와 5% 안쪽 차이입니다. 차익보다 '살 집을 시세에, 원하는 동·호수로' 고르는 기회로 보세요. 브동산은 이 랭킹을 보름마다 다시 계산해 올립니다.</b></p>
<p>단지별 비교단지와 보정 과정은 <a href='https://www.brandongsan.com/posts/{SLUG}.html'>브동산 홈페이지</a>에서 확인하실 수 있습니다.</p>
<p class='note'>본 글은 정보 제공 목적이며 투자 권유가 아닙니다. 계약 전에는 입주자모집공고와 분양 사무실 안내를 반드시 확인하세요.</p>
</body></html>"""
open(f'{OUT}/{SLUG}-naver.html','w').write(nv)
TAGS=['미분양아파트','선착순분양','수도권미분양','잔여세대','동호수지정','줍줍','예상프리미엄','브레인시티','고덕국제신도시','오산헤리티지자이','고촌센트럴자이','상동역롯데캐슬','힐스테이트구월아트파크','분양가비교','브동산']
open(f'{OUT}/{SLUG}-naver-tags.txt','w').write(' '.join('#'+t for t in TAGS))
print('built',NN,NP,NS,NB)
