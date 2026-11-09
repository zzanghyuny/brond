# -*- coding: utf-8 -*-
def subway(d):
    if d is None: return 0
    return 16 if d<=300 else 12 if d<=500 else 8 if d<=700 else 4 if d<=1000 else 0
def hh(n): return 10 if n>=2000 else 9 if n>=1500 else 8 if n>=1000 else 6 if n>=700 else 4 if n>=400 else 3 if n>=200 else 2
def pk(r): return 5 if r>=1.5 else 4 if r>=1.3 else 3 if r>=1.2 else 2 if r>=1.0 else 1
def cv(c): return 5 if c<=15 else 4 if c<=20 else 3 if c<=25 else 2 if c<=30 else 1
def months(a,b):  # a,b 'YYYY.MM' -> a-b months
    ya,ma=map(int,a.split('.')); yb,mb=map(int,b.split('.')); return (ya-yb)*12+(ma-mb)
def agef(m):
    if m<=0: return 1.0
    if m<=120: return 1+(m/120)*0.08
    if m<=240: return 1.08+((m-120)/120)*0.12
    return 1.2
def unit(x): # 억 -> text
    return f'{x:.2f}'
def man(x):  # 억 diff -> 십만원 반올림 만원표기
    v=round(x*10000/10)*10  # 만원 단위, 십만원 반올림
    return v
def man_txt(v):
    s='+' if v>=0 else '-'; a=abs(v)
    if a>=10000: return f'{s}{a/10000:.2f}억'.replace('.00억','억')
    return f'{s}{a:,}만'
def calc(p):
    S=p['site']
    S['입지']=S['교통']+S['주거']+S['교육']
    S['상품성']=S['상품수준']+S['세대수점']+S['조망']+S['주차점']+S['건폐점']
    S['평점']=S['입지']+S['브랜드']+S['상품성']
    adj=[]
    for c in p['comps']:
        c['입지']=c['교통']+c['주거']+c['교육']
        c['상품성']=c['상품수준']+c['세대수점']+c['조망']+c['주차점']+c['건폐점']
        c['평점']=c['입지']+c['브랜드']+c['상품성']
        diff=S['평점']-c['평점']
        c['평점보정']=1+max(-20,min(20,diff))/100
        c['개월']=months(S['입주'],c['준공'])
        c['연령']=agef(c['개월'])
        c['보정가']=c['기준가']*c['평점보정']*c['연령']
        adj.append(c['보정가'])
    p['적정가']=sum(adj)/len(adj)
    if S.get('분양가'):
        raw=p['적정가']-S['분양가']
        p['raw']=raw; p['프리미엄']=raw
    return p
