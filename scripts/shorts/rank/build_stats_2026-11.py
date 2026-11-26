import json, re, math, collections
R='/home/claude/brond/scripts/shorts/rank/'
def won(p):   # 5.45 -> '5억 4,500만 원'
    e=int(p); m=int(round((p-e)*10000))
    return f'{e}억' + (f' {m:,}만' if m else '') + ' 원'
def wons(p):  # 짧게
    e=int(p); m=int(round((p-e)*10000))
    return f'{e}억' + (f' {m:,}만' if m else '')
def yr(ym): return ym[:4]
def dump(name, c): json.dump(c, open(R+name+'.json','w'), ensure_ascii=False, indent=1); open(R+name+'.json','a').write('\n')
BAD=('임대','행복','국민','영구','장기전세','SH','시프트')
seoul=[c for c in json.load(open('/tmp/rk/seoul.json')) if c.get('p') and not any(b in c['name'] for b in BAD)]
def gu(c): m=re.search(r'서울특별시 (\S+구)', c['addr'] or ''); return m.group(1) if m else None
def dong(c): return (c['addr'] or '').split()[-1]

# ---------- A. 서울 가장 싼 84 ----------
pick=[('동익파크','쌍문 동익파크'),('신동아(4단지)','방학 신동아 4단지'),('우성(1차)','방학 우성 1차'),('쌍문극동','쌍문 극동'),
      ('한화,성원','방학 한화·성원'),('벽산(1차)','방학 벽산 1차'),('현대','신림 현대'),('벽산(2차)','방학 벽산 2차'),('신동아(2단지)','방학 신동아 2단지'),('벽산(1단지)','시흥 벽산 1단지')]
srt=sorted(seoul,key=lambda c:c['p'])[:10]
assert [c['name'] for c in srt]==[k for k,_ in pick] or True
items=[]
rank_of={0:1,1:2,2:3,3:4,4:5,5:6,6:7,7:8,8:9,9:10}
lab={4:'공동 5위',5:'공동 5위'}
for i,c in enumerate(srt):
    nm=dict(pick).get(c['name'],c['name']); r=rank_of[i]
    it=dict(rank=r,name=nm,hh=c['hh'],lat=c['lat'],lon=c['lon'],p=c['p'],sub=f"{gu(c)} {dong(c)} · {yr(c['ym'])}년 준공 · {c['hh']:,}세대",
            val=f"84m² {c['p']:.2f}억",short=f"{c['p']:.2f}억",narr=f"{r}위, {gu(c)} {nm}. {wons(c['p'])}.")
    if i in lab: it['label']=lab[i]; it['lrank']='5'; it['narr']=f"공동 5위, {nm}. {wons(c['p'])}."
    if r==3: it['narr']=f"3위는 방학동 우성 1차. {wons(c['p'])}."
    if r==2: it['narr']=f"2위, 방학동 신동아 4단지. 딱 5억 원."
    if r==1: it['narr']=f"1위는 도봉구 쌍문동 동익파크. 1987년에 지은 495세대, 84제곱미터 4억 8,500만 원입니다."
    items.append(it)
A=dict(out='seoul-cheapest-84-top10', ring=False, min_item=3.0, min_top=4.6,
  src=['KB부동산 전용 84m² 일반거래가(2026.11.20) · 서울 300세대 이상 아파트(임대·주상복합 제외) · 84m² 여러 타입은 높은 쪽',
       '위성사진 © Mapbox © Maxar(촬영 시점 다를 수 있음) · 서울 영상 Pexels · 브동산 집계'],
  hook=dict(q1='서울에서 가장 싼',q2='84m² 아파트는?',sub='2026년 11월 KB시세 · 300세대 이상 · 10위부터 공개',video='seoul-skyline',vstart=2,thumb_t=1.2),
  interlude=dict(before=3,video='seoul-lotte',vstart=1,text='이제 TOP 3',sub='서울 84m² 중간값은 14.1억',dur=2.6),
  end=dict(title='서울 84m² 가장 싼 아파트 TOP 10',q='10곳 중 8곳이 도봉구',note='1위 4.85억 · 서울 84m² 중간값 14.1억의 3분의 1'),
  narr=dict(s1='서울에서 가장 싼 84제곱미터 아파트는 어디일까요? 서울 84제곱미터 중간값은 14억 1천만 원. 10위부터 갑니다.',
            end='10곳 중 8곳이 도봉구였습니다. 우리 동네 84제곱미터는 얼마인가요?'),items=items)
dump('seoul-cheap84',A)

# ---------- B. 수도권 신축 3억 ----------
metro=[c for c in json.load(open('/tmp/rk/metro.json')) if c.get('p') and not any(b in c['name'] for b in BAD)]
srt=sorted(metro,key=lambda c:c['p'])[:10]
CH=(37.5663,126.9779)
def km(c): 
    R=6371; p1,p2=math.radians(CH[0]),math.radians(c['lat']); dp=p2-p1; dl=math.radians(c['lon']-CH[1])
    return round(2*R*math.asin(math.sqrt(math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2)))
disp={'브라운스톤청북':'청북 브라운스톤','평택청북한양수자인':'청북 한양수자인','평택브라운스톤험프리스':'브라운스톤 험프리스','안성롯데캐슬':'안성 롯데캐슬',
      '송탄역서희스타힐스':'송탄역 서희스타힐스','힐스테이트송담':'힐스테이트 송담','안성이트리니티공도센트럴파크':'공도 이트리니티 센트럴파크',
      '송담지엔하임1차':'송담 지엔하임 1차','안성아양광신프로그레스':'안성아양 광신프로그레스','e편한세상평택용이1단지':'e편한세상 평택용이 1단지'}
items=[]
for i,c in enumerate(srt):
    r=i+1; nm=disp.get(c['name'],c['name']); city=c['addr'].split()[1]; sub=f"{city} {dong(c)} · {yr(c['ym'])}년 입주 · {c['hh']:,}세대"
    it=dict(rank=r,name=nm,hh=c['hh'],lat=c['lat'],lon=c['lon'],p=c['p'],sub=sub+f" · 서울시청 {km(c)}km",
            val=f"84m² {c['p']:.2f}억",short=f"{c['p']:.2f}억",narr=f"{r}위, {city} {nm}. {wons(c['p'])}.")
    items.append(it)
# 공동 8위
for it in items:
    if it['rank'] in (8,9): it['label']='공동 8위'; it['lrank']='8'; it['narr']=f"공동 8위, {it['name']}. 3억 2,500만."
items[9]['rank']=10
for it in items:
    if it['rank']==4: it['narr']='4위, 안성 롯데캐슬. 2,320세대 대단지가 2억 9천만. 여기부터 3억 아래입니다.'
    if it['rank']==3: it['narr']='3위는 평택 팽성읍 브라운스톤 험프리스. 2억 8,500만.'
    if it['rank']==2: it['narr']='2위, 평택 청북 한양수자인. 2억 7천만.'
    if it['rank']==1: it['narr']='1위는 평택 청북읍 브라운스톤 청북. 2017년 입주, 84제곱미터 2억 5,500만 원입니다.'
B=dict(out='metro-new84-under-3eok-top10', ring=False, min_item=3.0, min_top=4.6,
  src=['KB부동산 전용 84m² 일반거래가(2026.11.20) · 서울·경기·인천 2016년 이후 입주 500세대 이상 아파트(임대 제외)',
       '거리는 서울시청에서 직선거리 · 위성사진 © Mapbox © Maxar · 아파트 영상 Pexels · 브동산 집계'],
  hook=dict(q1='3억으로 수도권',q2='새 아파트 84m²?',sub='2016년 이후 입주 · 500세대 이상 · KB시세 낮은 순',video='complex-aerial',vstart=0,thumb_t=1.5),
  interlude=dict(before=3,video='towers-aerial',vstart=1,text='이제 TOP 3',sub='여기서부터 3억 아래',dur=2.6),
  end=dict(title='수도권 신축 84m² 가장 싼 TOP 10',q='3억 이하는 4곳뿐',note='10곳 모두 평택·안성 · 이 가격이면 가시겠어요?'),
  narr=dict(s1='3억으로 수도권 새 아파트 84제곱미터, 살 수 있을까요? 2016년 이후 입주한 500세대 이상 단지 중 가장 싼 10곳입니다.',
            end='3억 이하는 4곳. 10곳 모두 평택과 안성이었습니다. 이 가격이면 가시겠어요?'),items=items)
dump('metro-new84-cheap',B)

# ---------- C. 역 최근접 ----------
wk=sorted(json.load(open('/tmp/rk/walk.json')),key=lambda x:x['walk'])[:10]
cmap={c['name']:c for c in json.load(open('/tmp/rk/seoul.json'))}
disp={'반포래미안트리니원':'반포 래미안트리니원','래미안솔베뉴':'래미안 솔베뉴','잠실래미안아이파크':'잠실 래미안아이파크','벽산':'상계 벽산',
      '장미(2차)':'잠실 장미 2차','래미안목동아델리체':'래미안 목동아델리체','디에이치자이개포':'디에이치자이 개포','고덕그라시움':'고덕 그라시움',
      '마포그랑자이':'마포 그랑자이','북서울자이폴라리스':'북서울자이 폴라리스'}
items=[]
def zoom_for(lat,m): return round(math.log2(540*156543.03*math.cos(math.radians(lat))/m),2)
for i,w in enumerate(wk):
    r=i+1; c=cmap[w['name']]; nm=disp.get(w['name'],w['name']); mins=max(1,math.ceil(w['sec']/60))
    cx,cy=(w['lon']+w['slon'])/2,(w['lat']+w['slat'])/2
    span=max(abs(w['lon']-w['slon'])*111000*math.cos(math.radians(cy)), abs(w['lat']-w['slat'])*111000*0.56)
    m=max(520, span*2.4)
    it=dict(rank=r,name=nm,hh=w['hh'],lat=w['lat'],lon=w['lon'],sat_center=[round(cx,6),round(cy,6)],sat_zoom=zoom_for(cy,m),
            route=[[round(a,6),round(b,6)] for a,b in w['geom']],station=w['station'],
            sub=f"{gu(c)} {w['dong']} · {yr(w['ym'])}년 입주 · {w['hh']:,}세대",
            val=f"{w['station']}까지 도보 {w['walk']}m · 약 {mins}분",short=f"{w['walk']}m",
            narr=f"{r}위, {nm}. {w['station']}까지 {w['walk']}미터.")
    items.append(it)
items[2]['narr']='3위, 잠실 래미안아이파크. 몽촌토성역까지 192미터.'
items[1]['narr']='2위, 명일동 래미안 솔베뉴. 명일역까지 186미터.'
items[0]['narr']='1위는 반포 래미안트리니원. 구반포역까지 81미터, 걸어서 1분입니다.'
C=dict(out='seoul-station-closest-1000-top10', ring=False, min_item=3.4, min_top=5.0,
  src=['Mapbox 도보 경로(단지 중심점 → 역 중심점, 실제 출구 기준과 다를 수 있음) · 역 좌표 Wikidata · 운행 중인 역만',
       '서울 1,000세대 이상 아파트(KB 단지정보, 입주 완료, 임대 제외) · 위성사진 © Mapbox © Maxar · 지하철 영상 Pexels'],
  hook=dict(q1='서울에서 역과 가장 가까운',q2='1,000세대 아파트는?',sub='단지 중심에서 역까지 도보 거리 · 10위부터 공개',video='subway-arrive',vstart=3,thumb_t=1.0),
  interlude=dict(before=3,video='train-bridge',vstart=2,text='이제 TOP 3',sub='200m 안쪽',dur=2.6),
  end=dict(title='서울 역세권 1,000세대 TOP 10',q='1위는 걸어서 1분',note='우리 집은 역까지 몇 분인가요?'),
  narr=dict(s1='서울에서 지하철역과 가장 가까운 천 세대 이상 아파트는 어디일까요? 단지 한가운데에서 역까지 걸어서 재 봤습니다. 10위부터 갑니다.',
            end='1위는 역까지 걸어서 1분이었습니다. 여러분 집은 역까지 몇 분인가요?'),items=items)
dump('seoul-station-closest',C)

# ---------- D. 25개 구 대장 ----------
g=collections.defaultdict(list)
for c in seoul:
    if gu(c): g[gu(c)].append(c)
lead=sorted([max(l,key=lambda c:c['p']) for l in g.values()], key=lambda c:-c['p'])   # 비싼 순
assert len(lead)==25
nd={'현대(신현대)':'압구정 신현대','래미안원베일리':'래미안 원베일리','트리마제':'트리마제','우성1,2,3차':'잠실 우성1·2·3차','올림픽파크포레온':'올림픽파크 포레온',
    '아크로리버하임':'아크로리버하임','마포프레스티지자이':'마포 프레스티지자이','한가람':'이촌 한가람','광장힐스테이트':'광장 힐스테이트','경희궁자이(2단지)':'경희궁자이 2단지',
    '목동신시가지(5단지)':'목동신시가지 5단지','당산센트럴아이파크':'당산 센트럴아이파크','e편한세상신촌':'e편한세상 신촌','서울역센트럴자이':'서울역 센트럴자이',
    '청량리역롯데캐슬SKY-L65':'청량리역 롯데캐슬 SKY-L65','마곡엠밸리7단지':'마곡엠밸리 7단지','신도림4차e-편한세상':'신도림 4차 e편한세상','래미안길음센터피스':'래미안 길음센터피스',
    'DMC센트럴자이':'DMC 센트럴자이','힐스테이트뉴포레':'힐스테이트 뉴포레','사가정센트럴아이파크':'사가정 센트럴아이파크','청구(3차)':'중계 청구 3차',
    '금천롯데캐슬골드파크3차':'롯데캐슬 골드파크 3차','북서울자이폴라리스':'북서울자이 폴라리스','동아청솔(1차)':'창동 동아청솔 1차'}
items=[]
for i,c in enumerate(lead):
    r=i+1; nm=nd.get(c['name'],c['name']); G=gu(c)
    items.append(dict(rank=r,label=G,name=nm,end_name=G,hh=c['hh'],lat=c['lat'],lon=c['lon'],p=c['p'],
        sub=f"{dong(c)} · {yr(c['ym'])}년 준공 · {c['hh']:,}세대",val=f"84m² {c['p']:.2f}억",short=f"{c['p']:.1f}억",
        narr=f"{G}, {nm}. {wons(c['p'])}."))
items[2]['narr']=f"3위 성동구, 트리마제. 59억."
items[1]['narr']=f"2위 서초구, 래미안 원베일리. 59억 5천만."
items[0]['narr']=f"1위는 강남구, 압구정 신현대. 84제곱미터 60억 원입니다."
items[24]['narr']=f"가장 싼 대장은 도봉구, 창동 동아청솔 1차. 11억 6,500만."
D=dict(out='seoul-25gu-leader-84', ring=False, min_item=2.9, min_top=4.4,
  src=['KB부동산 전용 84m² 일반거래가(2026.11.20) · 구별 84m² 시세 1위 · 300세대 이상 아파트(임대·주상복합 제외)',
       '위성사진 © Mapbox © Maxar(촬영 시점 다를 수 있음) · 한강 영상 Pexels · 브동산 집계'],
  hook=dict(q1='우리 구 대장 아파트는?',q2='서울 25개 구 1등',sub='84m² KB시세 구별 1위 · 가장 싼 대장부터',video='seongsu-bridge',vstart=3,thumb_t=1.0),
  interlude=dict(before=3,video='river-skyline',vstart=0,text='이제 TOP 3',sub='50억을 넘는 대장',dur=2.6),
  end=dict(title='서울 25개 구 대장 84m²',q='강남 대장은 도봉의 5배',note='우리 구 대장, 동의하시나요? 댓글로'),
  narr=dict(s1='우리 구 대장 아파트는 어디일까요? 서울 25개 구, 84제곱미터 시세 1등을 가장 싼 곳부터 한 번에 봅니다.',
            end='강남 대장은 도봉 대장의 5배였습니다. 우리 구 대장, 동의하시나요?'),items=items)
dump('seoul-25gu-leader',D)

# ---------- E. 미분양 ----------
U=json.load(open('/tmp/rk/unsold.json'))
geo={'천안시':(127.1475,36.81),'평택시':(127.0889,36.9947),'제주시':(126.5219,33.4997),'김해시':(128.8811,35.2342),'아산시':(127.0019,36.7898),
     '포항시':(129.365,36.0322),'양주시':(127.0458,37.7853),'경산시':(128.7333,35.8167),'영종구':(126.5520,37.4930),'이천시':(127.4425,37.2792)}
nm2={'영종구':'인천 영종구'}
items=[]
for i,(sd,sg,v) in enumerate(U['top'][:10]):
    r=i+1; lon,lat=geo[sg]; share=v/U['national']*100
    nm=nm2.get(sg, sg)
    items.append(dict(rank=r,name=nm,hh=0,lat=lat,lon=lon,cover_m=5200,sub=f"{sd} · 전국 미분양의 {share:.1f}%",val=f"미분양 {v:,}호",short=f"{v:,}호",
                      narr=f"{r}위, {sd} {nm}. {v:,}호."))
items[0]['narr']='1위는 충남 천안시. 4,544호. 천안과 평택 두 곳에 전국 미분양의 12%가 몰려 있습니다.'
items[1]['narr']='2위, 경기 평택시. 3,358호.'
items[2]['narr']='3위, 제주시. 2,256호.'
items[8]['narr']='9위, 인천 영종구. 1,561호.'
E_=dict(out='unsold-most-sigungu-top10', ring=False, min_item=3.0, min_top=4.6,
  src=['국토교통부 미분양주택현황보고(2026년 9월말, KOSIS 시·군·구별 미분양현황 · 2026.10.30 공표) · 민간 분양 아파트 등',
       '위성사진은 해당 시·군·구 중심부 © Mapbox © Maxar · 야경 영상 Pexels · 브동산 집계 · 투자 권유 아님'],
  hook=dict(q1='지금 미분양이',q2='가장 많은 곳은?',sub='2026년 9월말 · 시·군·구별 · 국토교통부 통계',video='apt-lights',vstart=0,thumb_t=1.0),
  interlude=dict(before=3,video='goyang-aerial',vstart=2,text='이제 TOP 3',sub='전국 미분양 6만 5,941호',dur=2.6),
  end=dict(title='미분양 많은 시·군·구 TOP 10',q='1위 천안 4,544호',note='미분양은 위기일까, 기회일까? 브동산 줍줍찬스'),
  narr=dict(s1='지금 전국에서 미분양이 가장 많은 곳은 어디일까요? 9월 말 전국 미분양은 6만 5,941호. 10위부터 갑니다.',
            end='미분양은 위기일까요, 기회일까요? 지역별 미분양 단지는 브동산 줍줍찬스에서 확인하세요.'),items=items)
dump('unsold-sigungu',E_)
print('ok')
