# -*- coding: utf-8 -*-
import math
from model import man,man_txt
def esc(s): return s.replace('&','&amp;').replace('<','&lt;')
def f2(x): return f'{x:.2f}'
# ---------------- radar
def radar(p):
    S=p['site']; items=[(S['이름'],S,'site')]+[(c['이름'],c,'c') for c in p['comps']]
    cx=cy=120; R=90
    def pt(ax,v): # ax 0..3 (입지 up, 브랜드 right, 상품성 down, 연식 left)
        d=[(0,-1),(1,0),(0,1),(-1,0)][ax]; return (cx+d[0]*R*v, cy+d[1]*R*v)
    def vals(x,isSite):
        age=1.0 if isSite else 1-0.75*(x['연령']-1)/0.2
        return [x['입지']/40,x['브랜드']/20,x['상품성']/40,max(0.25,min(1,age))]
    g=''.join(f'<polygon points="{cx},{cy-R*k} {cx+R*k},{cy} {cx},{cy+R*k} {cx-R*k},{cy}" fill="none" stroke="#E3E3E3" stroke-width="1"/>' for k in (1,.8,.6,.4,.2))
    styles={'site':'fill="rgba(17,17,17,0.08)" stroke="#111111" stroke-width="2"'}
    cstyles=['fill="none" stroke="#555555" stroke-width="1.5" stroke-dasharray="5 3"','fill="none" stroke="#8A8A8A" stroke-width="1.5" stroke-dasharray="1.5 3"']
    polys=''; ci=0
    for nm,x,kind in reversed(items):
        v=vals(x,kind=='site'); pts=' '.join(f'{pt(i,max(v[i],0.02))[0]:.1f},{pt(i,max(v[i],0.02))[1]:.1f}' for i in range(4))
        if kind=='site': polys+=f'<polygon points="{pts}" {styles["site"]}/>'
        else: polys+=f'<polygon points="{pts}" {cstyles[(len(p["comps"])-1-ci)%2] if False else cstyles[ci%2]}/>'; ci+=1
    labs='<text x="120" y="20" text-anchor="middle" font-size="12" fill="#555555">입지</text><text x="222" y="124" text-anchor="middle" font-size="12" fill="#555555">브랜드</text><text x="120" y="228" text-anchor="middle" font-size="12" fill="#555555">상품성</text><text x="18" y="124" text-anchor="middle" font-size="12" fill="#555555">연식</text>'
    svg=f'<svg viewBox="0 0 240 260" role="img" aria-label="입지, 브랜드, 상품성, 연식 4개 축으로 본 3개 단지 비교 레이더 차트"><g>{g}</g>{polys}{labs}</svg>'
    leg=f'<div class="radar-legend"><span class="lg-item"><i class="lg-swatch lg-site"></i>SITE · {esc(S["이름"])}</span>'+''.join(f'<span class="lg-item"><i class="lg-swatch {"lg-c1" if i==0 else "lg-c2"}"></i>{esc(c["이름"])}</span>' for i,c in enumerate(p['comps']))+'</div>'
    return f'<div class="radar-wrap">{svg}{leg}</div>'
# ---------------- bridge
def bridge(p):
    S=p['site']; cs=p['comps']; ad=p['적정가']; bun=S.get('분양가')
    vals=[ad]+[c['기준가'] for c in cs]+[c['보정가'] for c in cs]+([bun] if bun else [])
    lo=min(vals); hi=max(vals); span=max(hi-lo,0.5); lo-=span*0.12; hi+=span*0.12
    X=lambda v:70+(v-lo)/(hi-lo)*500
    o=[f'<svg viewBox="0 0 640 310" role="img" aria-label="비교단지 현재시세가 평점·연령 보정을 거쳐 SITE 적정가로 이어지는 과정을 보여주는 브동산 적정가 산출 브릿지 차트"><rect x="0" y="0" width="640" height="310" fill="#FAFAFA"/>',
       f'<line x1="{X(ad):.2f}" y1="20" x2="{X(ad):.2f}" y2="219" stroke="#BBBBBB" stroke-width="1" stroke-dasharray="3 3"/>']
    ys=[36,122]
    for c,y in zip(cs,ys):
        x0=X(c['기준가']); x1=X(c['보정가']); fx=c['평점보정']*c['연령']
        o.append(f'<text x="0" y="{y}" font-size="12.5" font-weight="800" fill="#111111">{esc(c["이름"])}</text>')
        o.append(f'<text x="{(x0+x1)/2:.2f}" y="{y+16}" text-anchor="middle" font-size="10.5" fill="#8A8A8A">평점·연령 ×{fx:.3f}</text>')
        o.append(f'<line x1="{x0:.2f}" y1="{y+30}" x2="{x1:.2f}" y2="{y+30}" stroke="#555555" stroke-width="1.5"/>')
        o.append(f'<circle cx="{x0:.2f}" cy="{y+30}" r="5.5" fill="#FFFFFF" stroke="#555555" stroke-width="2"/>')
        o.append(f'<rect x="{x1-5:.2f}" y="{y+25}" width="10" height="10" fill="#111111"/>')
        d=1 if x1>=x0 else -1
        o.append(f'<polygon points="{x1-5*d:.2f},{y+30} {x1-13*d:.2f},{y+27} {x1-13*d:.2f},{y+33}" fill="#555555"/>')
        a1='start' if x1>=x0 else 'end'; a2='end' if x1>=x0 else 'start'
        o.append(f'<text x="{x0+(10 if x1>=x0 else -10):.2f}" y="{y+48}" text-anchor="{a1}" font-size="11" fill="#8A8A8A">{f2(c["기준가"])}억</text><text x="{x1+(-10 if x1>=x0 else 10):.2f}" y="{y+48}" text-anchor="{a2}" font-size="11" font-weight="700" fill="#111111">{f2(c["보정가"])}억</text>')
    o.append('<line x1="0" y1="194" x2="640" y2="194" stroke="#E3E3E3" stroke-width="1"/>')
    o.append(f'<text x="0" y="218" font-size="12.5" font-weight="800" fill="#111111">{esc(S["이름"])} (SITE)</text>')
    xa=X(ad)
    if bun:
        xb=X(bun); prem=man_txt(p['프리미엄_표시'])
        o.append(f'<text x="{(xa+xb)/2:.2f}" y="234" text-anchor="middle" font-size="11" font-weight="800" fill="#111111">예상 프리미엄 {prem}</text>')
        o.append(f'<line x1="{xa:.2f}" y1="248" x2="{xb:.2f}" y2="248" stroke="#111111" stroke-width="2"/>')
        o.append(f'<circle cx="{xb:.2f}" cy="248" r="5.5" fill="#FFFFFF" stroke="#111111" stroke-width="2"/>')
        o.append(f'<path d="M {xa-6:.2f} 248 L {xa:.2f} 242 L {xa+6:.2f} 248 L {xa:.2f} 254 Z" fill="#111111"/>')
        d=1 if xb>=xa else -1
        o.append(f'<polygon points="{xa+7*d:.2f},248 {xa+15*d:.2f},245 {xa+15*d:.2f},251" fill="#111111"/>')
        left,right=(xa,xb) if xa<=xb else (xb,xa)
        o.append(f'<text x="{xa-9 if xa<=xb else xa+9:.2f}" y="270" text-anchor="{"end" if xa<=xb else "start"}" font-size="11" font-weight="800" fill="#111111">적정가 {f2(ad)}억</text>')
        o.append(f'<text x="{xb+9 if xa<=xb else xb-9:.2f}" y="270" text-anchor="{"start" if xa<=xb else "end"}" font-size="11" fill="#8A8A8A">실제분양가 {f2(bun)}억</text>')
    else:
        o.append(f'<path d="M {xa-6:.2f} 248 L {xa:.2f} 242 L {xa+6:.2f} 248 L {xa:.2f} 254 Z" fill="#111111"/>')
        o.append(f'<text x="{xa+12:.2f}" y="252" text-anchor="start" font-size="11" font-weight="800" fill="#111111">적정가 {f2(ad)}억</text>')
        o.append(f'<text x="{xa+12:.2f}" y="268" text-anchor="start" font-size="11" fill="#8A8A8A">실제분양가 미공개(공고 후 확인)</text>')
    o.append('<text x="0" y="298" font-size="10.5" fill="#8A8A8A">○=시세(KB 일반거래가)/실제분양가 · ■=평점·연령 보정 후 보정가격 · ◆=SITE 적정가(두 보정가격 평균) · 점선=적정가 기준선</text></svg>')
    return '<div class="bridge-wrap">'+''.join(o)+'</div><div class="cover-cap">적정가 산출 브릿지: 비교단지 시세가 평점·연령 보정을 거쳐 보정가격이 되고, 그 평균이 SITE 적정가가 되는 과정 — 브동산 모형 자체 시각화</div>'
# ---------------- rating table
def table(p,unit_label):
    S=p['site']; cs=p['comps']
    def h(x,meta): return f'<th>{esc(x["이름"])}<br><span class="note" style="margin-top:2px;">({meta})</span></th>'
    th='<th>평가 항목</th>'+h(S,'SITE')+''.join(h(c,c['메타']) for c in cs)
    def row(lbl,f,bold=False):
        return f'<tr><td>{lbl}</td>'+''.join(f'<td class="figure">{"<b>"+f(x)+"</b>" if bold and i==0 else f(x)}</td>' for i,x in enumerate([S]+cs))+'</tr>'
    rows=[row('입지(40)',lambda x:str(x['입지'])),row('　교통(20)',lambda x:str(x['교통'])),row('브랜드(20)',lambda x:str(x['브랜드'])),row('상품성(40)',lambda x:str(x['상품성'])),
          row('종합평점',lambda x:str(x['평점']),True),
          f'<tr><td>연식 가산율</td><td class="figure">기준(신축)</td>'+''.join(f'<td class="figure">{c["개월"]//12}년{c["개월"]%12}개월차 · ×{c["연령"]:.4f}</td>' for c in cs)+'</tr>',
          f'<tr><td>{unit_label} 기준가</td><td class="figure">-</td>'+''.join(f'<td class="figure">{f2(c["기준가"])}억</td>' for c in cs)+'</tr>',
          f'<tr><td>보정가격</td><td class="figure">-</td>'+''.join(f'<td class="figure">{f2(c["보정가"])}억</td>' for c in cs)+'</tr>']
    return f'<div class="tablewrap"><table><thead><tr>{th}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>'
# ---------------- map (station-centred schematic)
def mapsvg(m):
    # m: {'station':name,'places':[{'name','sub','dist','bearing'(deg from north, None=free),'kind':'site'|'comp'|'school'|'poi'}],'note':..}
    W,H=640,460; cx,cy=320,225; scale=165/1000.0  # px per m (1km = 165px)
    o=[f'<svg viewBox="0 0 640 460" role="img" aria-label="{esc(m["aria"])}"><rect x="0" y="0" width="640" height="460" fill="#FAFAFA"/>']
    o.append(f'<circle cx="{cx}" cy="{cy}" r="{165*0.5}" fill="none" stroke="#E3E3E3" stroke-dasharray="3 4"/><circle cx="{cx}" cy="{cy}" r="165" fill="none" stroke="#E3E3E3" stroke-dasharray="3 4"/>')
    o.append(f'<text x="{cx+84}" y="{cy-2}" font-size="10" fill="#8A8A8A">500m</text><text x="{cx+169}" y="{cy-2}" font-size="10" fill="#8A8A8A">1km</text>')
    o.append('<g transform="translate(596,36)"><line x1="0" y1="10" x2="0" y2="-14" stroke="#555555" stroke-width="1.5"/><polygon points="0,-18 -5,-8 5,-8" fill="#555555"/><text x="0" y="24" font-size="11" text-anchor="middle" fill="#555555">N</text></g>')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="6" fill="#555555"/><text x="{cx+10}" y="{cy+16}" font-size="12" font-weight="700" fill="#111111">{esc(m["station"])}</text>')
    pos=[]
    for pl in m['places']:
        a=math.radians(pl['bearing']); r=min(pl['dist'],1900)*scale
        x=cx+r*math.sin(a); y=cy-r*math.cos(a); pos.append((x,y,pl))
    for x,y,pl in pos:
        k=pl['kind']
        if k in('site','comp'): o.append(f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" stroke="#CCCCCC" stroke-width="1" stroke-dasharray="3 3"/>')
    for x,y,pl in pos:
        k=pl['kind']
        wd=max(len(pl['name'])*(10.5 if k=='site' else 8.5)+(46 if k=='site' else 0),len(pl['sub'])*7.2)
        anchor='start' if x+16+wd<=630 else 'end'
        if anchor=='end' and x-16-wd<8: anchor='start'
        tx=x+16 if anchor=='start' else x-16
        if k=='site':
            o.append(f'<rect x="{x-11:.1f}" y="{y-11:.1f}" width="22" height="22" fill="#111111"/><text x="{tx:.1f}" y="{y-2:.1f}" text-anchor="{anchor}" font-size="13.5" font-weight="800" fill="#111111">SITE · {esc(pl["name"])}</text><text x="{tx:.1f}" y="{y+14:.1f}" text-anchor="{anchor}" font-size="11" fill="#8A8A8A">{esc(pl["sub"])}</text>')
        elif k=='comp':
            o.append(f'<rect x="{x-8:.1f}" y="{y-8:.1f}" width="16" height="16" fill="#FFFFFF" stroke="#555555" stroke-width="2.5"/><text x="{tx:.1f}" y="{y-2:.1f}" text-anchor="{anchor}" font-size="13" fill="#111111">{esc(pl["name"])}</text><text x="{tx:.1f}" y="{y+13:.1f}" text-anchor="{anchor}" font-size="11" fill="#8A8A8A">{esc(pl["sub"])}</text>')
        else:
            o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="#8A8A8A"/><text x="{tx:.1f}" y="{y+4:.1f}" text-anchor="{anchor}" font-size="11.5" fill="#555555">{esc(pl["name"])}</text>')
    o.append(f'<g transform="translate(20,398)"><rect x="0" y="-10" width="600" height="30" fill="#FFFFFF" stroke="#E3E3E3"/><text x="14" y="10" font-size="10.5" fill="#555555">{esc(m["dist"])}</text></g>')
    o.append('<text x="20" y="450" font-size="10.5" fill="#8A8A8A">■ 검정=SITE · □(회색 테두리)=비교단지 · ●=역·주요 시설 · 역 중심 개략도(방향·거리는 개략)</text></svg>')
    return '<div class="map-wrap">'+''.join(o)+'</div><div class="cover-cap">'+esc(m['cap'])+'</div>'
