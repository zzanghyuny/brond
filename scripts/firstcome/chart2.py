import json, sys
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from fcfont import FP, ACCENT, INK, MID, SOFT
B=FP; R=FP
d=json.load(open('result2.json'))
def fmt(v):
    w=round(v*1e4/10)*10; s='+' if w>0 else '-' if w<0 else '±'; a=abs(w)
    return f"{s}{a/10000:.2f}억" if a>=10000 else f"{s}{a:,}만"
n=len(d); H=0.40*n+1.7
fig=plt.figure(figsize=(7.75,H),dpi=200,facecolor='white')
ax=fig.add_axes([0.43,0.62/H,0.53,1-1.55/H])
vals=[o['pct'] for o in d]; y=list(range(n))[::-1]
ax.barh(y,vals,color=[ACCENT if v>0 else '#C4C4C4' for v in vals],height=0.62,zorder=3)
ax.axvline(0,color=MID,lw=1)
lo,hi=-36,17; ax.set_xlim(lo,hi); ax.set_ylim(-0.7,n-0.3)
for yy,v,o in zip(y,vals,d):
    f=B.copy(); f.set_size(8.6)
    ax.text(v+(0.5 if v>=0 else -0.5),yy,f"{v:+.1f}%  ({fmt(o['final'])})",fontproperties=f,va='center',ha='left' if v>=0 else 'right',color=INK)
    f2=(B if o['rank']<=3 else R).copy(); f2.set_size(8.6)
    ax.text(lo-1.2,yy,f"{o['rank']}. {o['name']}",fontproperties=f2,va='center',ha='right',color=INK if v>0 else MID,clip_on=False)
ax.set_yticks([]); ax.set_xticks([])
for s in ['top','right','left','bottom']: ax.spines[s].set_visible(False)
t=B.copy(); t.set_size(14); fig.text(0.03,1-0.40/H,'수도권 미분양 선착순 TOP30 · 예상 프리미엄(분양가 대비 %)',fontproperties=t,color=INK)
s2=R.copy(); s2.set_size(8); fig.text(0.03,1-0.70/H,'브동산 약식 모형 v2 · 84㎡ 기준(포레나더샵 59㎡, 월드메르디앙 60㎡) · '+__import__('os').environ.get('RANK_DATE','2026-11-16').replace('-','.')+' 기준',fontproperties=s2,color=SOFT)
fig.text(0.03,0.24/H,'괄호 안은 금액. 분양가는 대표 타입 최고가, 확정된 현금 페이백만 차감. 마피 구간은 6-1 조정 후 값.',fontproperties=s2,color=SOFT)
fig.savefig(sys.argv[1],facecolor='white'); print(sys.argv[1])
