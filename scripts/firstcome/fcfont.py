# 폰트·색 공통 (Noto Sans CJK 우선, 없으면 WenQuanYi 등으로 대체 — 굵은 글씨는 stroke로 흉내)
import os, glob
import matplotlib.patheffects as pe
from matplotlib.font_manager import FontProperties, findSystemFonts
ACCENT = '#C8A45C'; ACCENT_BG = '#FBF7EC'; INK = '#111111'; MID = '#555555'; SOFT = '#8A8A8A'; GRAY = '#BBBBBB'
def _find():
    for p in ['/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc','/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc']:
        if os.path.exists(p): return p
    for f in findSystemFonts():
        if any(k in f for k in ('NotoSansCJK','Malgun','NanumGothic','wqy')): return f
    raise SystemExit('한글 폰트를 찾을 수 없음')
FONT = _find(); FP = FontProperties(fname=FONT)
def put(ax, x, y, s, size=28, bold=False, color=INK, ha='left', va='center', dpi=100, **kw):
    """픽셀 단위 글씨 크기(캔버스 1000px 기준). bold는 stroke로 흉내"""
    t = ax.text(x, y, s, fontproperties=FP, fontsize=size*72/dpi, color=color, ha=ha, va=va, **kw)
    if bold: t.set_path_effects([pe.withStroke(linewidth=size*0.045*72/dpi*1.4, foreground=color)])
    return t
def fmt(v):
    w = round(v*1e4/10)*10; s = '+' if w > 0 else '-' if w < 0 else '±'; a = abs(w)
    return f"{s}{a/10000:.2f}억" if a >= 10000 else f"{s}{a:,}만"
