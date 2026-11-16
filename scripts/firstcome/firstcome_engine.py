# 브동산 미분양 선착순 랭킹 엔진 (v2, 2026.11.16) — 단독 실행 가능
# python3 firstcome_engine.py → result2.json 생성 + 콘솔 출력
import json
def months(y1,m1,y2,m2): return (y2-y1)*12+(m2-m1)
def age_mult(diff):  # 수도권 맥스 1.2, diff = SITE준공 - 비교단지준공(개월), 음수면 1.0 미만 처리
    if diff<0:
        # SITE가 더 오래된 경우: 대칭 적용(역보정)
        return 1/age_mult(-diff)
    if diff<=120: return 1+diff/120*0.08
    if diff<=240: return 1.08+(diff-120)/120*0.12
    return 1.2
def score_mult(site,comp):
    d=site-comp; m=1+d*0.01
    return max(0.8,min(1.2,m))
def hh(n):
    return 10 if n>=2000 else 9 if n>=1500 else 8 if n>=1000 else 7 if n>=700 else 6 if n>=500 else 5 if n>=300 else 3
def prod(year,n,view=6):
    lvl = 8 if year>=2027 else 7 if year>=2020 else 6 if year>=2015 else 5 if year>=2008 else 4
    park = 5 if year>=2027 else 4 if year>=2015 else 3
    bcr = 4 if year>=2015 else 3
    return lvl+hh(n)+view+park+bcr
# 입지 = 교통(20) + 편의(10) + 교육(10)
def C(name,yr,mo,n,brand,trans,conv,edu,price,deal,view=6,note=''):
    return dict(name=name,yr=yr,mo=mo,n=n,brand=brand,trans=trans,conv=conv,edu=edu,price=price,deal=deal,view=view,note=note)

# ---- 비교단지(직전 회차 값, 다음 회차에 최신 실거래로 갱신) ----
comps = {
 'hyang1': C('모아미래도에듀파크서봉마을4단지',2018,6,894,12,0,6,7,4.33,'2026.07.30'),
 'hyang2': C('서봉마을 모아엘가',2015,6,496,12,0,6,6,4.15,'2026.10.20'),
 'osan1': C('더샵 오산센트럴',2020,6,596,20,8,7,7,6.80,'2026.10~11 5건 중앙값'),
 'osan2': C('병점역아이파크캐슬',2021,3,2666,20,12,8,7,9.25,'2026.10 8건 중앙값'),
 'pt1': C('지제역더샵센트럴시티',2022,5,1999,20,15,8,7,9.20,'2026.11.07'),
 'pt2': C('고덕국제신도시제일풍경채',2019,11,1022,12,0,7,7,5.80,'2026.10~11 5건 중앙값'),
 'onsu1': C('e편한세상 온수역',2020,6,921,20,17,7,6,11.00,'2026.07.06'),
 'onsu2': C('일루미스테이트',2024,6,3724,16,4,7,7,8.50,'2026.09.08'),
 'yj1': C('중앙역중흥S클래스센텀시티3블록',2022,6,666,16,8,7,6,5.70,'2026.07.30'),
 'yj2': C('회천신도시디에트르센트럴시티',2022,6,860,12,8,6,6,5.39,'2026.05.18'),
 'sw1': C('포레나 북수원',2023,6,1063,16,0,6,6,9.10,'2026.10.16'),
 'sw2': C('서광교 파크 스위첸',2023,6,1130,16,0,6,6,9.40,'2026.05.18'),
 'gc1': C('고촌행정타운 한양수자인',2017,6,420,12,12,7,6,7.55,'2026.11.05'),
 'gc2': C('수기마을힐스테이트',2008,6,1149,20,8,7,7,6.80,'2026.10.21'),
 'om1': C('쌍용더플래티넘오목천역',2022,9,930,16,16,6,6,7.14,'2026.09 2건 평균'),
 'om2': C('오목천역서희스타힐스',2016,6,844,12,12,6,6,5.65,'2026.07.04'),
 'sh1': C('장현호반써밋',2020,6,712,12,8,7,7,6.38,'2026.09.01'),
 'sh2': C('제일풍경채 에듀',2020,6,489,12,4,7,7,5.65,'2026.10.12'),
 'on1': C('오남아이파크',2009,6,584,20,4,6,6,4.30,'2026.09.05'),
 'on2': C('오남 e편한세상(470세대)',2009,6,470,20,8,6,6,4.35,'2026.10.31'),
 'sd1': C('센트럴파크 푸르지오',2020,6,999,20,12,9,8,14.35,'2026.10.15'),
 'sd2': C('힐스테이트 중동',2022,6,999,20,12,9,8,13.20,'2026.08.21'),
 'gw1': C('한내들퍼스티지',2016,6,860,12,9,8,7,5.73,'2026.10.31'),
 'gw2': C('구월 힐스테이트1단지',2007,6,5076,20,13,8,7,5.05,'2026.11.10'),
 'ss1': C('힐스테이트소사역',2025,6,850,20,17,7,6,10.10,'2026.11.01',note='세대수 미확인(7점 가정)'),
 'ss2': C('래미안부천어반비스타',2021,6,850,20,8,7,6,8.75,'2026.08.14',note='세대수 미확인(7점 가정)'),
 'ps1': C('송화지구우미이노스빌',2005,6,719,12,0,5,5,2.48,'2026.10.18'),
 'ps2': C('송화마을현대홈타운',2005,6,364,16,0,5,5,2.30,'2026.06.22'),
 'yb1': C('역북 푸르지오',2017,6,1259,20,12,6,7,6.89,'2026.11.10'),
 'yb2': C('용인역북명지대역동원로얄듀크',2018,6,842,12,12,6,6,7.20,'2026.06.13'),
}

comps.update({
 # 여주
 'yeo1': C('여주역푸르지오클라테르',2021,6,551,20,12,6,6,5.00,'2026.09.28'),
 'yeo2': C('여주역금호어울림베르티스',2022,6,605,12,12,6,6,4.70,'2026.07.11'),
 # 평택 고덕 (2단계 블록 → 가장 가까운 신축·준신축)
 'gd1': C('고덕자이센트로',2025,8,569,20,0,5,6,5.08,'2026.01~08 3건 평균'),
 'gd2': C('고덕국제신도시파라곤에듀포레',2021,7,654,12,0,6,7,5.72,'2026.10.16~17 2건 평균'),
 # 평택 외곽 신축 대체 비교군(팽성) — L5
 'pt_jh': C('평택브레인시티중흥S-클래스(호가)',2027,2,1980,16,0,4,6,5.20,'2026.11.02 34평 평균 호가'),
 # 인천 학익·용현
 'co3': C('시티오씨엘3단지',2024,12,977,20,8,7,6,6.39,'2026.11 리치고 시세'),
 'co4': C('시티오씨엘4단지',2025,1,428,20,8,7,6,6.36,'2026.09.12'),
 'skyv': C('인천SK스카이뷰',2016,6,3971,20,10,8,8,5.90,'2026.10.09'),
 # 영종
 'yjg1': C('e편한세상 영종국제도시 센텀베뉴',2023,6,1409,20,4,6,6,5.06,'2026.11.10 2건 평균'),
 'yjg2': C('스카이시티자이',2018,6,1034,20,4,7,6,4.70,'2026.11.11'),
 # 인천 간석 59㎡
 'ich59a': C('인천시청역힐스테이트(59㎡)',2024,6,746,20,18,8,6,5.40,'2026.08~10 3건 중앙값'),
 'ich59b': C('간석래미안자이(59㎡)',2008,6,2432,20,14,8,7,4.10,'2026.01'),
 # 인천 구월 — gw2(2007년 구축) 교체, L5
 'gw3': C('인천시청역한신더휴',2025,12,469,12,16,8,6,6.21,'2026.11 리치고 34평 시세'),
 # 인천 연수 59·60㎡
 'ys1': C('서해그랑블포레스트(59㎡)',2019,4,334,8,0,6,7,3.90,'2026.09~10 3건 평균'),
 'ys2': C('연수 서해그랑블1단지(60㎡)',2017,12,1043,8,0,6,7,5.15,'mhb-blog 인용'),
 # 수원 당수·호매실
 'hm1': C('호매실역서희스타힐스',2011,11,1318,12,4,7,7,6.75,'2026.09~10 2건 평균'),
 'hm2': C('호반써밋수원',2017,4,567,12,4,7,7,9.30,'2026.08~09 3건 평균'),
 # 수원 서둔·화서
 'hsp': C('힐스테이트 수원파크포레',2024,12,482,20,12,7,6,8.61,'2026.11 리치고 시세(10.07 8.55억)'),
 'hwpp': C('화서역파크푸르지오',2021,8,2355,20,16,8,7,15.07,'2026.10~11 3건 평균'),
 # 오산 내삼미·세교 (L5 재선정)
 'osd1': C('오산대역세교자이',2018,1,1110,20,10,6,6,6.11,'2026.10 3건 평균'),
 'osd2': C('오산세교우미린레이크시티(분양권)',2029,7,1424,12,0,5,6,5.32,'2026.10~11 분양권 3건 중앙값'),
 # 이천
 'ic1': C('이천자이더파크',2024,6,706,20,4,7,6,4.80,'2026.11.09'),
 'ic2': C('롯데캐슬페라즈스카이',2023,6,299,20,4,7,6,5.04,'2026.11.05'),
 # 양평
 'yp1': C('양수역이지움리버뷰',2024,2,72,8,14,4,6,5.58,'2026.07~09 3건 평균'),
 'yp2': C('양평역 한라비발디',2023,6,1602,12,12,6,6,4.80,'2026.11.04'),
})

# 주변 미분양·마피 단지 상한(L3): 신규 단지 적정가는 이 단지 현재가(평점 보정만, 연식 가산 없음)를 넘지 못한다
CEIL = {
 'bc': dict(name='브레인시티 중흥S-클래스',yr=2027,mo=2,n=1980,brand=16,trans=0,conv=4,edu=6,price=5.20,src='34평 평균 호가 5.2억(리치고 2026.11.02), 분양가 5.27억보다 낮음'),
 'hsp': dict(name='힐스테이트 수원파크포레',yr=2024,mo=12,n=482,brand=20,trans=12,conv=7,edu=6,price=8.61,src='준공 후 잔여세대 분양 중, 리치고 시세 8.61억(10.07 실거래 8.55억)'),
 'hsic': dict(name='힐스테이트 이천역 2단지',yr=2026,mo=7,n=885,brand=20,trans=14,conv=6,edu=6,price=5.10,src='준공 후 잔여세대 분양 중, 10월 실거래 5.0·5.1·5.75억(중앙값 5.1억)'),
}

S=lambda **k: k
sites = [
 S(key='sangdong-lotte',name='상동역 롯데캐슬 시그니처',region='부천 상동',yr=2032,mo=3,n=1859,brand=20,builder='롯데건설',trans=16,conv=9,edu=8,price=16.38,price_note='84A 14.01~16.38억',comps=['sd1','sd2']),
 S(key='hyangnam',name='향남역 그로브 스위첸',region='화성 향남',yr=2029,mo=6,n=933,brand=16,builder='KCC건설',trans=4,conv=7,edu=6,price=5.575,price_note='84A 5.14~5.58억',comps=['hyang1','hyang2']),
 S(key='yeoju-rosebien',name='여주역 로제비앙 더센텀',region='여주 홍문동',yr=2028,mo=4,n=744,brand=12,builder='대광건영',trans=12,conv=5,edu=6,price=5.36,price_note='84 4.30~5.36억',comps=['yeo1','yeo2']),
 S(key='godeok-sujain',name='고덕 수자인풍경채 1·2단지',region='평택 고덕(Abc-61BL 등)',yr=2029,mo=1,n=1126,brand=12,builder='BS한양·제일건설',trans=0,conv=4,edu=6,price=5.671,price_note='84A 5.11~5.67억',comps=['gd1','gd2']),
 S(key='godeok-housed',name='고덕 수자인하우스디',region='평택 고덕(A-67BL)',yr=2029,mo=2,n=403,brand=12,builder='대보건설',trans=0,conv=4,edu=6,price=5.698,price_note='84A 5.13~5.70억',comps=['gd1','gd2']),
 S(key='godeok-woomi',name='평택 고덕 우미린 프레스티지',region='평택 고덕(Abc-36BL)',yr=2028,mo=12,n=743,brand=12,builder='우미건설 외',trans=0,conv=4,edu=6,price=5.873,price_note='84A 5.29~5.87억',comps=['gd1','gd2']),
 S(key='bc-vista',name='브레인시티 비스타동원',region='평택 브레인시티 4BL',yr=2028,mo=12,n=1600,brand=12,builder='동원개발',trans=0,conv=4,edu=6,price=5.66,price_note='84B 5.24~5.66억',comps=['pt1','pt2'],ceil='bc'),
 S(key='bc-annature',name='브레인시티 앤네이처 미래도',region='평택 브레인시티 10BL',yr=2028,mo=7,n=1413,brand=12,builder='미래도건설',trans=0,conv=4,edu=6,price=4.952,price_note='84C 4.80~4.95억',comps=['pt1','pt2'],ceil='bc'),
 S(key='bc-medis',name='브레인시티 메디스파크 대광로제비앙 모아엘가',region='평택 브레인시티',yr=2028,mo=5,n=1215,brand=12,builder='대광건영·모아건설',trans=0,conv=4,edu=6,price=5.43,price_note='84 최고 5.43억',comps=['pt1','pt2'],ceil='bc'),
 S(key='cityociel9',name='시티오씨엘 9단지 오션파크뷰',region='인천 학익동',yr=2030,mo=4,n=1949,brand=20,builder='HDC현산 컨소시엄',trans=8,conv=7,edu=6,price=7.129,price_note='84A 6.68~7.13억',comps=['co3','co4']),
 S(key='inha-roicent',name='인하대역 수자인 로이센트',region='인천 용현동',yr=2029,mo=4,n=1199,brand=12,builder='BS한양',trans=14,conv=7,edu=7,price=6.991,price_note='84 6.52~6.99억',comps=['skyv','co4']),
 S(key='guwol-artpark',name='힐스테이트 구월아트파크',region='인천 구월동',yr=2030,mo=10,n=496,brand=20,builder='현대엔지니어링',trans=16,conv=9,edu=7,price=8.88,price_note='84A 7.63~8.88억',comps=['gw1','gw3'],l5='구월 힐스테이트1단지(2007년식, 연식차 23년)를 빼고 2025년 준공 인천시청역한신더휴로 교체'),
 S(key='yeongjong-dietre',name='영종 디에트르 라 메르Ⅰ',region='인천 영종 중산동',yr=2029,mo=10,n=1009,brand=12,builder='대방건설',trans=4,conv=6,edu=6,price=6.61,price_note='84A 5.67~6.61억',comps=['yjg1','yjg2'],warn='84A 최고가(고층) 기준이다. 84B 저층(5.15억)을 고르면 격차가 1억원 넘게 줄어든다'),
 S(key='forena-sicheong',name='포레나더샵 인천시청역',region='인천 간석동',yr=2029,mo=9,n=2568,brand=20,builder='한화·포스코이앤씨',trans=18,conv=8,edu=6,price=6.656,price_note='59A 5.78~6.66억',comps=['ich59a','ich59b'],size='59'),
 S(key='yeonsu-meridian',name='연수 월드메르디앙 어반포레',region='인천 연수 동춘동',yr=2026,mo=4,n=133,brand=8,builder='월드건설',trans=0,conv=6,edu=7,price=4.92,price_note='60A 4.38~4.92억',comps=['ys1','ys2'],size='60'),
 S(key='doosan-bucheon',name='두산위브더제니스 부천',region='부천 소사본동',yr=2032,mo=2,n=1728,brand=16,builder='두산건설',trans=17,conv=7,edu=6,price=11.82,price_note='84A 10.11~11.82억',comps=['ss1','ss2']),
 S(key='osan-heritage',name='오산헤리티지자이',region='오산 양산동',yr=2029,mo=9,n=1783,brand=20,builder='GS건설',trans=4,conv=5,edu=6,price=7.83,price_note='84 7.12~7.83억',comps=['osan1','osan2']),
 S(key='bukosan-deforet',name='북오산자이 드포레',region='오산 내삼미동',yr=2029,mo=10,n=1517,brand=20,builder='GS건설',trans=0,conv=5,edu=6,price=6.72,price_note='84A 6.21~6.72억',comps=['osd1','osd2'],l5='병점역아이파크캐슬(화성 병점 역세권)을 빼고 같은 내삼미동 오산대역세교자이·세교 신규 분양권으로 교체'),
 S(key='onam1',name='오남역 서희스타힐스 여의재 1단지',region='남양주 오남읍',yr=2028,mo=12,n=1308,brand=12,builder='서희건설',trans=12,conv=5,edu=7,price=7.19,price_note='84 6.70~7.19억',comps=['on1','on2'],warn='오남·진접에 10년 이내 신축 실거래가 없어 2009년식과 비교했다. 연령보정 상한(1.2배)에 걸려 적정가가 낮게 나왔을 수 있다'),
 S(key='onam3',name='오남역 서희스타힐스 여의재 3단지',region='남양주 오남읍',yr=2029,mo=1,n=1056,brand=12,builder='서희건설',trans=12,conv=5,edu=7,price=7.09,price_note='84 6.88~7.09억',comps=['on1','on2'],warn='오남·진접에 10년 이내 신축 실거래가 없어 2009년식과 비교했다. 연령보정 상한(1.2배)에 걸려 적정가가 낮게 나왔을 수 있다'),
 S(key='imok-dietre2',name='북수원이목 디에트르 더 리체Ⅱ',region='수원 장안 이목동',yr=2028,mo=5,n=1744,brand=12,builder='대방건설',trans=0,conv=5,edu=7,price=10.307,price_note='84C 10.31억(84 최고 11.41억)',comps=['sw1','sw2']),
 S(key='elif-suwon',name='엘리프 한신더휴 수원 D3',region='수원 권선 당수1지구',yr=2028,mo=4,n=697,brand=12,builder='계룡건설·한신공영',trans=4,conv=5,edu=6,price=7.95,price_note='84A 6.89~7.95억',comps=['om1','hm1'],l5='호반써밋수원(호매실역 예정지 앞, 9.3억)을 빼고 서수원 신축 쌍용더플래티넘오목천역으로 교체'),
 S(key='hwaseo-honors',name='화서역 호수공원 아너스빌',region='수원 권선 서둔동',yr=2029,mo=10,n=476,brand=12,builder='경남기업',trans=14,conv=7,edu=6,price=8.98,price_note='84 8.32~8.98억',comps=['hsp','hwpp'],ceil='hsp'),
 S(key='hs-parkforet',name='힐스테이트 수원파크포레',region='수원 권선 서둔동',yr=2024,mo=12,n=482,brand=20,builder='현대엔지니어링',trans=12,conv=7,edu=6,price=8.94,price_note='84 8.94억~(준공 후 분양)',comps=['hsp','hwpp'],own=8.61,own_src='리치고 시세 8.61억 · 10.07 실거래 8.55억',done=True,warn='113㎡에 분양가 10% 현금 페이백 보도(뉴시스 2026.07.24). 84㎡에도 같으면 실질가 8.08억, 프리미엄 +5,340만원(+6.6%)으로 1위'),
 S(key='omokcheon-thelive',name='오목천역 더리브',region='수원 권선 오목천동',yr=2026,mo=2,n=201,brand=8,builder='SGC이테크건설',trans=16,conv=6,edu=6,price=7.687,price_note='84C 7.69억(84 최고 8.22억)',comps=['om1','om2'],benefit=1.1,benefit_src='84㎡ 페이백 1억원+이자지원 1천만원(뉴시스 2026.07.24)',done=True),
 S(key='gochon-xi',name='고촌센트럴자이',region='김포 고촌읍',yr=2024,mo=6,n=1297,brand=20,builder='GS건설',trans=4,conv=5,edu=6,price=7.584,price_note='84A 7.45~7.58억(최초 분양가)',comps=['gc1','gc2'],own=7.69,own_src='리치고 시세 7.69억 · 11.02 실거래 7.52억',done=True),
 S(key='icheon-yemiji',name='이천역 예미지 센트럴파크',region='이천 중리동',yr=2026,mo=11,n=1009,brand=12,builder='금성백조',trans=6,conv=5,edu=6,price=5.47,price_note='84 5.09~5.47억',comps=['ic1','ic2'],ceil='hsic',done=True),
 S(key='hs-icheon',name='힐스테이트 이천역',region='이천 증일동',yr=2026,mo=7,n=885,brand=20,builder='현대건설',trans=14,conv=6,edu=6,price=6.10,price_note='2단지 84 평균 6.10억',comps=['ic1','ic2'],own=5.10,own_src='2단지 10월 실거래 5.0·5.1·5.75억(중앙값)',done=True),
 S(key='pine-avenue',name='더 플래티넘 파인애비뉴',region='평택 팽성읍',yr=2028,mo=3,n=1048,brand=16,builder='쌍용건설',trans=0,conv=4,edu=5,price=5.39,price_note='84 4.96~5.39억',comps=['gd1','pt_jh'],l5='송화지구 2005년식 구축(1.7~2.8억)만 있어 평택 외곽 신축으로 교체'),
 S(key='ssy-hangang',name='쌍용 더 플래티넘 한강',region='양평 양서면',yr=2029,mo=5,n=333,brand=16,builder='쌍용건설',trans=14,conv=4,edu=6,price=7.48,price_note='84A 5.87~7.48억',comps=['yp1','yp2']),
]
# v1 비교단지(참고용, 레슨런 비교 표에 사용)
V1 = {'bukosan-deforet':['osan1','osan2'],'elif-suwon':['hm1','hm2'],'guwol-artpark':['gw1','gw2'],'pine-avenue':['ps1','ps2'],'bc-vista':['pt1','pt2'],'bc-annature':['pt1','pt2'],'bc-medis':['pt1','pt2']}

def tot(x): return x['trans']+x['conv']+x['edu']+x['brand']+prod(x['yr'],x['n'],x.get('view',6))
def fair_of(s,keys):
    ss=tot(s); rows=[]
    for ck in keys:
        c=comps[ck]; cs=tot(c)
        sm=score_mult(ss,cs); dm=months(c['yr'],c['mo'],s['yr'],s['mo']); am=age_mult(dm)
        rows.append(dict(comp=c['name'],yr=c['yr'],mo=c['mo'],n=c['n'],score=cs,price=c['price'],deal=c['deal'],sm=round(sm,3),diff=dm,am=round(am,3),adj=round(c['price']*sm*am,4)))
    return sum(r['adj'] for r in rows)/len(rows), rows

def adjust61(raw):
    if raw<=-1.5: return raw,None
    if raw<-1.0: return raw+0.3,'6-1 근거1(계약금 하한)'
    if raw<0: return raw/2,'6-1 근거2(선분양 수요)'
    return raw,None

out=[]
for s in sites:
    ss=tot(s); notes=[]
    fair,rows=fair_of(s,s['comps'])
    model_fair=fair
    base=s['price']-s.get('benefit',0)
    if s.get('benefit'): notes.append(('L1',f"실질 분양가 {base:.2f}억 = 분양가 {s['price']:.2f}억 − {s['benefit_src']}"))
    if s.get('own'):
        fair=s['own']; notes.append(('L2',f"준공 단지: 자기 단지 시세 {s['own']:.2f}억을 적정가로 사용({s['own_src']}). 모형값 {model_fair:.2f}억은 참고"))
    if s.get('ceil'):
        c=CEIL[s['ceil']]; cap=c['price']*score_mult(ss,tot(c))
        if fair>cap:
            notes.append(('L3',f"주변 미분양 상한: {c['name']} {c['price']:.2f}억 × 평점보정 {score_mult(ss,tot(c)):.2f} = {cap:.2f}억으로 제한(모형값 {fair:.2f}억). 근거: {c['src']}"))
            fair=cap
        else:
            notes.append(('L3',f"주변 미분양 상한 {cap:.2f}억 이내라 조정 없음"))
    if s.get('l5'): notes.append(('L5',s['l5']))
    if s.get('warn'): notes.append(('주의',s['warn']))
    raw=fair-base
    if s.get('done'):
        fin,basis=raw,None  # 준공 단지는 계약금 잠금 논리가 없어 6-1 미적용
    else:
        fin,basis=adjust61(raw)
    capped=False
    if fin>0 and not s.get('done'):
        lim=base*0.10
        if fin>lim:
            notes.append(('L4',f"미분양 상한: 계산값 +{fin:.2f}억이 계약금(분양가 10%, {lim:.2f}억)을 넘어 {lim:.2f}억으로 제한"))
            fin=lim; capped=True
    pct=fin/base*100
    v1=None
    if s['key'] in V1:
        f1,_=fair_of(s,V1[s['key']]); r1=f1-s['price']; v1=dict(fair=round(f1,3),final=round(adjust61(r1)[0],3),pct=round(adjust61(r1)[0]/s['price']*100,1))
    out.append(dict(**{k:v for k,v in s.items() if k not in('comps',)},score=ss,comps=rows,model_fair=round(model_fair,4),fair=round(fair,4),base=round(base,4),raw=round(raw,4),final=round(fin,4),basis=basis,capped=capped,pct=round(pct,1),notes=notes,v1=v1))
out.sort(key=lambda x:-x['pct'])
for i,o in enumerate(out,1): o['rank']=i
json.dump(out,open('result2.json','w'),ensure_ascii=False,indent=1)

def fmt(v):
    w=round(v*1e4/10)*10; sign='+' if w>0 else '-' if w<0 else '±'; a=abs(w)
    return f"{sign}{a/10000:.2f}억" if a>=10000 else f"{sign}{a:,}만원"
if __name__=='__main__':
    for o in out:
        print(o['rank'],o['name'],'|점',o['score'],'|기준',o['base'],'|모형',round(o['model_fair'],2),'|적정',round(o['fair'],2),'|raw',fmt(o['raw']),'|final',fmt(o['final']),o['basis'] or '','|',o['pct'],'%')
        for r in o['comps']: print('     ',r['comp'],r['score'],r['price'],'x',r['sm'],'x',r['am'],f"({r['diff']}m)",'=',round(r['adj'],2))
        for n in o['notes']: print('      *',n[0],n[1])
        if o['v1']: print('      v1:',o['v1'])
