# -*- coding: utf-8 -*-
"""도시이야기 지도·카드 애니메이션 (cairo + PIL 글자). frames(name, W, H, D, cues, opts) -> 프레임 생성기(RGB bytes)."""
import json, math, functools
import numpy as np, cairo
from PIL import Image, ImageDraw, ImageFont
from shapely.geometry import shape, box
from shapely.ops import unary_union

FPS = 30
BG = (0x08, 0x08, 0x09); LAND = (0x14, 0x14, 0x16); HAIR = (0x2A, 0x2A, 0x2D); TRACK = (0x22, 0x22, 0x25)
INK = (0xF4, 0xF1, 0xEA); SOFT = (0xB9, 0xB5, 0xAC); FAINT = (0x96, 0x94, 0x8E); DIM = (0x5A, 0x58, 0x54); BRASS = (0xC8, 0xA4, 0x5C)
RIVER = (0x3C, 0x3B, 0x39)
FP = '/tmp/fonts/'
FONTS = {'sb': FP + 'Pretendard-SemiBold.otf', 'b': FP + 'Pretendard-Bold.otf', 'xb': FP + 'Pretendard-ExtraBold.otf', 'm': FP + 'Pretendard-Medium.otf', 'r': FP + 'Pretendard-Regular.otf'}
GEO = json.load(open('/home/claude/work/ep1/geo.json'))
P = json.load(open('/home/claude/media/geo/places.json'))
def ll(k): return (P[k]['lon'], P[k]['lat'])

def c01(x): return max(0.0, min(1.0, x))
def ease(x): x = c01(x); return x * x * (3 - 2 * x)
def eout(x): x = c01(x); return 1 - (1 - x) ** 3
def rgb(c, a=1.0): return (c[0] / 255, c[1] / 255, c[2] / 255, a)

# ---------- 글자 스프라이트(PIL → cairo)
@functools.lru_cache(maxsize=512)
def text_surface(s, font='sb', size=40, color=INK, stroke=0):
    f = ImageFont.truetype(FONTS[font], size)
    d0 = ImageDraw.Draw(Image.new('L', (1, 1)))
    l, t, r, b = d0.textbbox((0, 0), s, font=f, stroke_width=stroke)
    w, h = r - l + 8, b - t + 8
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.text((4 - l, 4 - t), s, font=f, fill=color + (255,), stroke_width=stroke, stroke_fill=(8, 8, 9, 255))
    a = np.asarray(im).astype(np.float32); al = a[..., 3:4] / 255.0
    pre = np.concatenate([a[..., 2:3] * al, a[..., 1:2] * al, a[..., 0:1] * al, a[..., 3:4]], axis=2).astype(np.uint8)
    pre = np.ascontiguousarray(pre)
    surf = cairo.ImageSurface.create_for_data(memoryview(bytearray(pre.tobytes())), cairo.FORMAT_ARGB32, w, h, w * 4)
    return surf, w - 8, h - 8, l, t

def put_text(cr, s, x, y, font='sb', size=40, color=INK, alpha=1.0, anchor='lt', stroke=0):
    if alpha <= 0.001: return 0
    surf, w, h, l, t = text_surface(s, font, int(size), tuple(color), stroke)
    ax = {'l': 0, 'm': 0.5, 'r': 1}[anchor[0]]; ay = {'t': 0, 'm': 0.5, 'b': 1}[anchor[1]]
    cr.save(); cr.set_source_surface(surf, x - ax * w - 4, y - ay * h - 4); cr.paint_with_alpha(alpha); cr.restore()
    return w

def text_w(s, font='sb', size=40):
    return text_surface(s, font, int(size), INK, 0)[1]

# ---------- 투영
class Proj:
    def __init__(self, lon0, lat0, spk, cx, cy):
        self.lon0, self.lat0, self.spk, self.cx, self.cy = lon0, lat0, spk, cx, cy
        self.kx = 111.32 * math.cos(math.radians(lat0)); self.ky = 110.57
    def __call__(self, lon, lat):
        return self.cx + (lon - self.lon0) * self.kx * self.spk, self.cy - (lat - self.lat0) * self.ky * self.spk
    @staticmethod
    def fit(bounds, W, H, pad=0.06, cy_off=0.0, rect=None):
        x0, y0, x1, y1 = bounds; lat0 = (y0 + y1) / 2; lon0 = (x0 + x1) / 2
        kx = 111.32 * math.cos(math.radians(lat0)); wk = (x1 - x0) * kx; hk = (y1 - y0) * 110.57
        if rect is None: rect = (0, 0, W, H)
        rw, rh = rect[2] - rect[0], rect[3] - rect[1]
        spk = min(rw * (1 - 2 * pad) / wk, rh * (1 - 2 * pad) / hk)
        return Proj(lon0, lat0, spk, (rect[0] + rect[2]) / 2, (rect[1] + rect[3]) / 2 + cy_off * H)

def path_geom(cr, g, pj, dx=0.0, dy=0.0):
    t = g.geom_type
    if t == 'Polygon': polys = [g]
    elif t == 'MultiPolygon': polys = list(g.geoms)
    elif t in ('LineString', 'MultiLineString'):
        for ln in ([g] if t == 'LineString' else g.geoms):
            for i, (x, y) in enumerate(ln.coords):
                px, py = pj(x, y); (cr.move_to if i == 0 else cr.line_to)(px + dx, py + dy)
        return
    else: return
    for p in polys:
        for ring in [p.exterior] + list(p.interiors):
            for i, (x, y) in enumerate(ring.coords):
                px, py = pj(x, y); (cr.move_to if i == 0 else cr.line_to)(px + dx, py + dy)
            cr.close_path()

def path_km(cr, g, origin, pj, at):
    """g(경위도)를 origin 기준 km 모양으로 바꿔 pj 화면의 at(경위도) 위치에 같은 축척으로 그린다."""
    lon0, lat0 = origin; kx0 = 111.32 * math.cos(math.radians(lat0)); ky = 110.57
    ax, ay = pj(*at); s = pj.spk
    polys = [g] if g.geom_type == 'Polygon' else list(g.geoms)
    for p in polys:
        for i, (x, y) in enumerate(p.exterior.coords):
            px = ax + (x - lon0) * kx0 * s; py = ay - (y - lat0) * ky * s
            (cr.move_to if i == 0 else cr.line_to)(px, py)
        cr.close_path()

SEOUL = shape(GEO['seoul']); HC_NEW = shape(GEO['hcmc_new_land']); HC_OLD = shape(GEO['hcmc_old'])
BD = shape(GEO['binhduong']); BRVT = shape(GEO['brvt'])
RIV = [shape(GEO['saigon_river']), shape(GEO['nhabe_river']), shape(GEO['dongnai_river'])]
_land_cache = {}
def land_for(bounds):
    k = tuple(round(b, 3) for b in bounds)
    if k not in _land_cache:
        win = box(bounds[0] - 3, bounds[1] - 3, bounds[2] + 3, bounds[3] + 3)
        feats = json.load(open('/home/claude/media/geo/ne_land10.geojson'))['features']
        _land_cache[k] = unary_union([shape(f['geometry']).intersection(win) for f in feats if shape(f['geometry']).intersects(win)])
    return _land_cache[k]
def mainland(g, min_km2=40):
    parts = [p for p in getattr(g, 'geoms', [g]) if p.area * 111 * 109 > min_km2 and p.bounds[1] > 9.5]
    return unary_union(parts)
HC_NEW_M = mainland(HC_NEW); BRVT_M = mainland(BRVT)
SEOUL_C = (SEOUL.centroid.x, SEOUL.centroid.y)

def new_frame(W, H):
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H); cr = cairo.Context(surf)
    cr.set_source_rgb(*rgb(BG)[:3]); cr.paint(); cr.set_line_join(cairo.LINE_JOIN_ROUND); cr.set_line_cap(cairo.LINE_CAP_ROUND)
    return surf, cr
def to_bytes(surf, W, H):
    a = np.ndarray((H, W, 4), np.uint8, surf.get_data())
    return np.ascontiguousarray(a[..., [2, 1, 0]]).tobytes()

def draw_base(cr, pj, bounds, W, H, rivers=True, river_w=1.0, land=True):
    if land:
        cr.set_source_rgba(*rgb(LAND)); path_geom(cr, land_for(bounds), pj); cr.fill()
    if rivers:
        cr.set_source_rgba(*rgb(RIVER)); cr.set_line_width(max(2.0, river_w))
        for r in RIV: path_geom(cr, r, pj); cr.stroke()

def stroke_geom(cr, g, pj, color, alpha, width, fill_alpha=0.0, dash=None):
    if alpha <= 0.001: return
    if fill_alpha > 0:
        cr.set_source_rgba(*rgb(color, fill_alpha * alpha)); path_geom(cr, g, pj); cr.fill()
    cr.set_source_rgba(*rgb(color, alpha)); cr.set_line_width(width)
    if dash: cr.set_dash(dash)
    path_geom(cr, g, pj); cr.stroke(); cr.set_dash([])

def pill(cr, x, y, w, h, color, alpha, r=None):
    r = h / 2 if r is None else r
    cr.new_sub_path(); cr.arc(x + w - r, y + r, r, -math.pi / 2, 0); cr.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    cr.arc(x + r, y + h - r, r, math.pi / 2, math.pi); cr.arc(x + r, y + r, r, math.pi, 1.5 * math.pi); cr.close_path()
    cr.set_source_rgba(*rgb(color, alpha)); cr.fill()

def label(cr, s, x, y, size, color=INK, alpha=1.0, anchor='lm', box_alpha=0.78, font='sb'):
    """지도 위 이름표: 어두운 단색 판 + 글자."""
    if alpha <= 0.001: return
    w = text_w(s, font, size); h = size * 1.35; padx = size * 0.45
    ax = {'l': 0, 'm': 0.5, 'r': 1}[anchor[0]]; ay = {'t': 0, 'm': 0.5, 'b': 1}[anchor[1]]
    bx = x - ax * (w + 2 * padx); by = y - ay * h
    pill(cr, bx, by, w + 2 * padx, h, BG, box_alpha * alpha, r=size * 0.28)
    put_text(cr, s, bx + padx, by + h / 2, font, size, color, alpha, 'lm')

def dot(cr, x, y, r, color, alpha=1.0, ring=True):
    if alpha <= 0.001: return
    if ring:
        cr.arc(x, y, r + max(2, r * 0.45), 0, 2 * math.pi); cr.set_source_rgba(*rgb(BG, alpha)); cr.fill()
    cr.arc(x, y, r, 0, 2 * math.pi); cr.set_source_rgba(*rgb(color, alpha)); cr.fill()

def ellipse(cr, x, y, rx, ry):
    cr.save(); cr.translate(x, y); cr.scale(rx, ry); cr.arc(0, 0, 1, 0, 2 * math.pi); cr.restore()

def zone(cr, pj, lonlat, rkm, color, alpha, fill=0.28, width=3, sx=1.0, sy=1.0):
    if alpha <= 0.001: return
    x, y = pj(*lonlat); r = rkm * pj.spk
    ellipse(cr, x, y, r * sx, r * sy); cr.set_source_rgba(*rgb(color, fill * alpha)); cr.fill()
    ellipse(cr, x, y, r * sx, r * sy); cr.set_source_rgba(*rgb(color, alpha)); cr.set_line_width(width); cr.stroke()

def arrow(cr, p0, p1, color, alpha, width, prog=1.0, bend=0.18, head=None):
    if alpha <= 0.001 or prog <= 0.001: return
    (x0, y0), (x1, y1) = p0, p1; mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    nx, ny = -(y1 - y0), (x1 - x0); cx, cy = mx + nx * bend, my + ny * bend
    pts = []
    for i in range(41):
        t = i / 40 * prog; a = (1 - t) ** 2; b = 2 * (1 - t) * t; c = t * t
        pts.append((a * x0 + b * cx + c * x1, a * y0 + b * cy + c * y1))
    cr.set_source_rgba(*rgb(color, alpha)); cr.set_line_width(width)
    for i, (x, y) in enumerate(pts): (cr.move_to if i == 0 else cr.line_to)(x, y)
    cr.stroke()
    (xa, ya), (xb, yb) = pts[-2], pts[-1]; ang = math.atan2(yb - ya, xb - xa); hl = head or width * 4.2
    cr.move_to(xb + math.cos(ang) * hl * 0.3, yb + math.sin(ang) * hl * 0.3)
    cr.line_to(xb - math.cos(ang - 0.45) * hl, yb - math.sin(ang - 0.45) * hl)
    cr.line_to(xb - math.cos(ang + 0.45) * hl, yb - math.sin(ang + 0.45) * hl); cr.close_path(); cr.fill()

def fade(t, t0, d=0.6): return ease((t - t0) / d)
def cue(cues, i, default=0.0):
    return cues[i] if i < len(cues) else (cues[-1] + 2.0 * (i - len(cues) + 1) if cues else default)

# =====================================================================
# 1) 서울 겹쳐 보기 (본편 오프닝 / 쇼츠1)
def anim_overlay(W, H, D, cues, opts, short=False):
    bounds = (106.25, 10.33, 107.62, 11.52)
    far = Proj.fit(bounds, W, H, pad=0.05, rect=None if short else (0, 150, W * 0.70, 850))
    at = ll('ben_thanh')
    near_spk = far.spk * (3.4 if not short else 3.0)
    s = min(W, H) / 1080
    c1 = cue(cues, 1); c2 = cue(cues, 2); c3 = cue(cues, 3); c4 = cue(cues, 4)
    for fi in range(int(round(D * FPS))):
        t = fi / FPS
        z = ease((t - (c1 - 0.2)) / 2.2) if not short else ease((t - (c2 - 0.3)) / 2.2)
        spk = math.exp(math.log(near_spk) * (1 - z) + math.log(far.spk) * z)
        ax, ay = far(*at)
        pj = Proj(at[0], at[1], spk, ax * z + W / 2 * (1 - z), ay * z + H / 2 * (1 - z))
        surf, cr = new_frame(W, H)
        draw_base(cr, pj, bounds, W, H, river_w=2.0 + 3 * (1 - z))
        # 호치민 경계
        if not short:
            a_new = fade(t, c1 + 0.4, 1.2); a_old = 0.0
        else:
            a_old = fade(t, c2 + 0.2, 0.8); a_new = fade(t, c3 + 0.1, 1.0)
        stroke_geom(cr, HC_OLD, pj, SOFT, a_old * (1 - 0.6 * a_new), 2.5 * s, fill_alpha=0.10, dash=[8 * s, 6 * s])
        stroke_geom(cr, HC_NEW_M, pj, BRASS, a_new, 3.5 * s, fill_alpha=0.16)
        # 서울(같은 축척)
        a_se = fade(t, 0.2, 0.8)
        cr.set_source_rgba(*rgb(INK, 0.14 * a_se)); path_km(cr, SEOUL, SEOUL_C, pj, at); cr.fill()
        cr.set_source_rgba(*rgb(INK, a_se)); cr.set_line_width(3.2 * s); path_km(cr, SEOUL, SEOUL_C, pj, at); cr.stroke()
        # 이름표
        sx, sy = pj(*at); r_se = 17 * pj.spk
        lab_a = a_se * (1 - 0.0 * z)
        label(cr, '서울 605㎢', sx, sy - r_se - 18 * s, 34 * s, INK, lab_a, 'mb')
        if not short:
            label(cr, '호치민 6,772㎢', W * 0.80, H * 0.17, 40 * s, BRASS, a_new, 'mm')
            k = fade(t, c2, 0.7)
            if k > 0:
                put_text(cr, '약 11배', W * 0.82, H * 0.42, 'xb', 96 * s, BRASS, k, 'mm')
                put_text(cr, '면적, 2025년 합병 뒤 기준', W * 0.82, H * 0.505, 'm', 28 * s, FAINT, k, 'mm')
        else:
            label(cr, '합병 전 호치민 2,095㎢', W * 0.5, H * 0.08, 34 * s, SOFT, a_old * (1 - a_new), 'mm')
            label(cr, '지금의 호치민 6,772㎢', W * 0.5, H * 0.08, 38 * s, BRASS, a_new, 'mm')
            k = fade(t, c3 + 0.9, 0.7)
            put_text(cr, '서울의 약 11배', W * 0.5, H * 0.92, 'xb', 64 * s, BRASS, k * (1 - fade(t, c4, 0.5)), 'mm')
            k4 = fade(t, c4 + 0.1, 0.6)
            put_text(cr, '인구밀도 ㎢당 약 2,070명 · 서울 15,432명', W * 0.5, H * 0.92, 'b', 36 * s, INK, k4, 'mm')
        yield to_bytes(surf, W, H)

# 2) 2025년 합병
def anim_merge(W, H, D, cues, opts):
    bounds = (106.25, 10.33, 107.62, 11.52); pj = Proj.fit(bounds, W, H, pad=0.05, rect=(0, 150, W * 0.68, 850)); s = H / 1080
    c0, c1, c2 = cue(cues, 0), cue(cues, 1), cue(cues, 2)
    lab = {'hc': (106.62, 10.78), 'bd': (106.62, 11.20), 'br': (107.25, 10.60)}
    for fi in range(int(round(D * FPS))):
        t = fi / FPS; surf, cr = new_frame(W, H)
        draw_base(cr, pj, bounds, W, H, river_w=2.0)
        a0 = fade(t, 0.1, 0.7); a1 = fade(t, c0 + 1.2, 0.8); a2 = fade(t, c1 + 0.2, 1.0)
        stroke_geom(cr, HC_OLD, pj, INK, a0 * (1 - 0.5 * a2), 2.6 * s, fill_alpha=0.10)
        stroke_geom(cr, BD, pj, SOFT, a1 * (1 - 0.5 * a2), 2.2 * s, fill_alpha=0.08, dash=[8 * s, 6 * s])
        stroke_geom(cr, BRVT_M, pj, SOFT, a1 * (1 - 0.5 * a2), 2.2 * s, fill_alpha=0.08, dash=[8 * s, 6 * s])
        stroke_geom(cr, HC_NEW_M, pj, BRASS, a2, 3.6 * s, fill_alpha=0.15)
        label(cr, '옛 호치민', *pj(*lab['hc']), 32 * s, INK, a0, 'mm')
        label(cr, '옛 빈즈엉성', *pj(*lab['bd']), 30 * s, SOFT, a1, 'mm')
        label(cr, '옛 바리아붕따우성', *pj(*lab['br']), 30 * s, SOFT, a1, 'mm')
        k = fade(t, c1 + 0.6, 0.7)
        put_text(cr, '지금의 호치민', W * 0.80, H * 0.26, 'b', 40 * s, INK, k, 'mm')
        put_text(cr, '2025년 7월 1일 출범', W * 0.80, H * 0.325, 'm', 28 * s, FAINT, k, 'mm')
        put_text(cr, '6,772㎢', W * 0.80, H * 0.42, 'xb', 84 * s, BRASS, k, 'mm')
        k2 = fade(t, c2 + 0.2, 0.7)
        put_text(cr, '구(군) 폐지 → 동·사 168개', W * 0.80, H * 0.53, 'b', 32 * s, INK, k2, 'mm')
        yield to_bytes(surf, W, H)

# 3) 주거축 이동 3단계
AX = dict(
    s1=[((106.668, 10.765), 4.2, 1.0, 0.85, '옛 1·3·5군 · 쩌런', (-1, -1))],
    s2=[((106.718, 10.727), 2.2, 1.1, 1.0, '푸미흥', (1, 0.3)), ((106.737, 10.805), 1.4, 1.0, 1.0, '타오디엔', (-1, -1))],
    s3=[((106.722, 10.773), 1.4, 1.0, 1.0, '투티엠', (1, 0.3)), ((106.785, 10.840), 3.4, 1.2, 1.0, '옛 9군 · 투득', (1, 0)),
        ((106.705, 10.925), 4.8, 1.25, 1.15, '옛 빈즈엉', (1, -0.4))],
)
STAGE_LAB = {1: ('①', '강 서쪽 구도심', '~1990년대'), 2: ('②', '강 건너 첫 신도시', '1990년대~2010년대'), 3: ('③', '투티엠 · 옛 9군 · 옛 빈즈엉', '2020년대~')}
def anim_axis(W, H, D, cues, opts, short=False):
    st = opts['stage']; bounds = (106.60, 10.70, 106.86, 10.985)
    pj = Proj.fit(bounds, W, H, pad=0.04, rect=(0, 0, W, H) if short else (W * 0.10, 150, W * 0.94, 790))
    s = min(W, H) / 1080
    hc_old = HC_OLD
    for fi in range(int(round(D * FPS))):
        t = fi / FPS; surf, cr = new_frame(W, H)
        draw_base(cr, pj, bounds, W, H, river_w=5.5 * s)
        stroke_geom(cr, hc_old, pj, HAIR, 1.0, 1.6 * s)
        stroke_geom(cr, BD, pj, HAIR, 1.0, 1.6 * s)
        # 사이공강 이름
        put_text(cr, '사이공강', *pj(106.712, 10.858), 'm', 28 * s, FAINT, 1.0, 'mm')
        for k in (1, 2, 3):
            if k > max(st, 3 if st == 4 else st): continue
            cur = (k == st) and st != 4
            if cur:
                t0 = cue(cues, 1) if (st == 1 and not short) else (cue(cues, 0) + 0.2)
                a = fade(t, t0, 1.0); col = BRASS; fill = 0.30; wid = 3.4 * s
            elif st == 4:
                a = fade(t, 0.2 + 0.5 * (k - 1), 0.6); col = BRASS if k == 3 else SOFT; fill = 0.22 if k == 3 else 0.12; wid = 2.6 * s
            else:
                a = 1.0; col = SOFT; fill = 0.10; wid = 2.0 * s
            for (lonlat, r, sx, sy, name, off) in AX[f's{k}']:
                zone(cr, pj, lonlat, r, col, a, fill=fill, width=wid, sx=sx, sy=sy)
                x, y = pj(*lonlat); rr = r * pj.spk
                lx = x + off[0] * (rr * sx + 14 * s); ly = y + off[1] * (rr * sy + 14 * s)
                anc = ('l' if off[0] > 0 else 'r' if off[0] < 0 else 'm') + ('t' if off[1] > 0 else 'b' if off[1] < 0 else 'm')
                label(cr, name, lx, ly, (36 if cur else 30) * s, BRASS if cur else INK, a, anc)
        if st == 4:
            p1 = pj(*AX['s1'][0][0]); pa = pj(*AX['s2'][0][0]); pb = pj(*AX['s2'][1][0]); pc = pj(*AX['s3'][2][0]); pd = pj(*AX['s3'][1][0])
            pr = ease((t - 1.2) / 1.2); pr2 = ease((t - 2.6) / 1.2)
            arrow(cr, p1, pa, INK, 0.9, 4 * s, pr, bend=0.25); arrow(cr, p1, pb, INK, 0.9, 4 * s, pr, bend=-0.25)
            arrow(cr, pb, pd, BRASS, 0.95, 4 * s, pr2, bend=-0.2); arrow(cr, p1, pc, BRASS, 0.95, 4 * s, pr2, bend=-0.15)
        # 단계 제목
        if st in (1, 2, 3):
            n, name, yrs = STAGE_LAB[st]; k = fade(t, 0.15, 0.6)
            if not short:
                put_text(cr, f'{n} {name}', 70 * s, 150 * s, 'xb', 52 * s, INK, k, 'lt')
                put_text(cr, yrs, 74 * s, 222 * s, 'm', 30 * s, BRASS, k, 'lt')
            else:
                put_text(cr, f'{n} {name}', 40 * s, 30 * s, 'xb', 46 * s, INK, k, 'lt')
                put_text(cr, yrs, 42 * s, 92 * s, 'm', 28 * s, BRASS, k, 'lt')
        elif st == 4:
            put_text(cr, '주거축이 움직인 순서', 70 * s, 150 * s, 'xb', 52 * s, INK, fade(t, 0.15, 0.6), 'lt')
        yield to_bytes(surf, W, H)

# 4) 교통
M1 = [(106.6980, 10.7725), (106.7032, 10.7767), (106.7066, 10.7816), (106.7155, 10.7955), (106.7232, 10.7985), (106.7333, 10.8017),
      (106.7432, 10.8020), (106.7556, 10.8087), (106.7584, 10.8216), (106.7638, 10.8327), (106.7716, 10.8460), (106.7888, 10.8590),
      (106.8011, 10.8664), (106.8141, 10.8796)]
def anim_transport(W, H, D, cues, opts):
    bounds = (106.62, 10.72, 107.07, 10.91); pj = Proj.fit(bounds, W, H, pad=0.04, rect=(0, 200, W, 880)); s = H / 1080
    c = [cue(cues, i) for i in range(6)]
    pts = [pj(*p) for p in M1]
    seg = [0.0]
    for i in range(1, len(pts)): seg.append(seg[-1] + math.dist(pts[i - 1], pts[i]))
    tsn = pj(*ll('tsn')); lt = pj(*ll('long_thanh')); bt = pts[0]; tt = pj(106.7215, 10.7745)
    for fi in range(int(round(D * FPS))):
        t = fi / FPS; surf, cr = new_frame(W, H)
        draw_base(cr, pj, bounds, W, H, river_w=4.5 * s)
        stroke_geom(cr, HC_NEW_M, pj, HAIR, 1.0, 1.6 * s)
        # 메트로 1호선
        pr = ease((t - c[1]) / 2.4); L = seg[-1] * pr
        if pr > 0:
            cr.set_source_rgba(*rgb(BRASS if t < c[3] else INK, 1.0)); cr.set_line_width(7 * s)
            cr.move_to(*pts[0])
            for i in range(1, len(pts)):
                if seg[i] <= L: cr.line_to(*pts[i])
                else:
                    f = (L - seg[i - 1]) / max(1e-6, seg[i] - seg[i - 1]); x = pts[i - 1][0] + f * (pts[i][0] - pts[i - 1][0]); y = pts[i - 1][1] + f * (pts[i][1] - pts[i - 1][1]); cr.line_to(x, y); break
            cr.stroke()
            for i, p in enumerate(pts):
                if seg[i] <= L + 1: dot(cr, p[0], p[1], 6.5 * s, INK)
        k1 = fade(t, c[1] + 1.0, 0.6)
        label(cr, '메트로 1호선 · 19.7km · 14개 역 (2024.12)', pts[-1][0] - 20 * s, pts[-1][1] - 24 * s, 30 * s, BRASS if t < c[3] else INK, k1, 'rb')
        label(cr, '벤탄', bt[0] - 16 * s, bt[1] + 6 * s, 26 * s, INK, k1, 'rm')
        label(cr, '수오이띠엔', pts[-1][0] + 18 * s, pts[-1][1] + 4 * s, 26 * s, INK, k1, 'lm')
        # 2호선 벤탄–투티엠 구간
        k3 = fade(t, c[3], 0.8)
        if k3 > 0:
            cr.set_source_rgba(*rgb(BRASS if t < c[4] else SOFT, k3)); cr.set_line_width(6 * s); cr.set_dash([14 * s, 9 * s])
            cr.move_to(*bt); cr.line_to(bt[0] + (tt[0] - bt[0]) * k3, bt[1] + (tt[1] - bt[1]) * k3); cr.stroke(); cr.set_dash([])
            dot(cr, tt[0], tt[1], 7 * s, BRASS if t < c[4] else SOFT, k3)
            label(cr, '2호선 벤탄–투티엠 구간 착공 (2026.4)', tt[0] + 10 * s, tt[1] + 40 * s, 28 * s, BRASS if t < c[4] else SOFT, k3, 'lt')
        # 공항
        k4 = fade(t, c[4], 0.8)
        for (p, name, col, a) in [(tsn, '떤선녓 공항 (지금)', INK, k4), (lt, '롱탄 신공항 · 2026.12.24 상업 운항 예정', BRASS, k4)]:
            if a > 0:
                cr.save(); cr.translate(*p); cr.set_source_rgba(*rgb(col, a))
                cr.move_to(0, -16 * s); cr.line_to(5 * s, -2 * s); cr.line_to(20 * s, 4 * s); cr.line_to(20 * s, 9 * s); cr.line_to(5 * s, 6 * s)
                cr.line_to(3 * s, 15 * s); cr.line_to(8 * s, 19 * s); cr.line_to(-8 * s, 19 * s); cr.line_to(-3 * s, 15 * s); cr.line_to(-5 * s, 6 * s)
                cr.line_to(-20 * s, 9 * s); cr.line_to(-20 * s, 4 * s); cr.line_to(-5 * s, -2 * s); cr.close_path(); cr.fill(); cr.restore()
                label(cr, name, p[0] + (30 if col == INK else -30) * s, p[1] - 30 * s, 28 * s, col, a, 'lb' if col == INK else 'rb')
        # 남북 고속철도(계획)
        k5 = fade(t, c[5], 0.8)
        if k5 > 0:
            src = pj(107.06, 10.905)
            arrow(cr, src, (tt[0] + 8 * s, tt[1] + 4 * s), BRASS, k5, 5 * s, ease((t - c[5]) / 1.4), bend=0.16)
            label(cr, '남북 고속철도(계획) 하노이–투티엠 1,541km · 착공 2027.12 예정', W - 60 * s, 200 * s, 28 * s, BRASS, k5, 'rt')
        put_text(cr, '교통 인프라', 70 * s, 150 * s, 'xb', 52 * s, INK, fade(t, 0.1, 0.6), 'lt')
        yield to_bytes(surf, W, H)

# 5) 한국 기업 사업지
KR = [  # (경위도, 제목, 설명, 이름표 방향 dx,dy, cue 번호)
    ((106.7240, 10.7715), '롯데 에코스마트시티', '투티엠 2A 구역 · 약 23억 달러 · 2026.10 공사 재개', (1, 0), 0),
    ((106.7030, 10.7000), 'GS건설 냐베 신도시', '350ha', (-1, 0), 2),
    ((106.8290, 10.8730), 'GS건설 롱빈 신도시', '약 92ha · 메트로 1호선 차량기지 옆', (-1, -1), 3),
    ((106.7290, 10.7830), 'GS건설 투티엠 주거 사업', '', (1, -1), 3),
    ((106.7950, 10.8560), '삼성전자 HCMC CE 콤플렉스', '하이테크파크 · 70ha · TV·가전', (-1, 0.6), 4),
    ((106.7230, 10.7270), '푸미흥 한인 생활권', '한국국제학교 · 한인 상권', (1, 1), 5),
]
def anim_korea(W, H, D, cues, opts):
    bounds = (106.66, 10.685, 106.86, 10.895); pj = Proj.fit(bounds, W, H, pad=0.03, rect=(W * 0.20, 160, W * 0.98, 780)); s = H / 1080
    for fi in range(int(round(D * FPS))):
        t = fi / FPS; surf, cr = new_frame(W, H)
        draw_base(cr, pj, bounds, W, H, river_w=5 * s)
        stroke_geom(cr, HC_NEW_M, pj, HAIR, 1.0, 1.6 * s)
        # 메트로 1호선(참고)
        cr.set_source_rgba(*rgb(DIM, 1.0)); cr.set_line_width(4 * s)
        for i, p in enumerate(M1): (cr.move_to if i == 0 else cr.line_to)(*pj(*p))
        cr.stroke()
        cur_i = max([i for i in range(6) if t >= cue(cues, i) - 0.05] or [0])
        for (lonlat, title, desc, off, ci) in KR:
            a = fade(t, cue(cues, ci) + 0.1, 0.6)
            if a <= 0: continue
            x, y = pj(*lonlat); active = (ci == cur_i) or (ci == 0 and cur_i == 1)
            col = BRASS if active else INK
            cr.arc(x, y, 13 * s, 0, 2 * math.pi); cr.set_source_rgba(*rgb(col, 0.25 * a)); cr.fill()
            dot(cr, x, y, 8 * s, col, a)
            lx = x + off[0] * 26 * s; ly = y + off[1] * 26 * s
            anc = ('l' if off[0] > 0 else 'r') + ('t' if off[1] > 0.5 else 'b' if off[1] < -0.5 else 'm')
            if desc:
                tw = max(text_w(title, 'b', 30 * s), text_w(desc, 'm', 24 * s)); bh = 92 * s; padx = 16 * s
                bx = lx if anc[0] == 'l' else lx - tw - 2 * padx
                by = ly if anc[1] == 't' else (ly - bh if anc[1] == 'b' else ly - bh / 2)
                pill(cr, bx, by, tw + 2 * padx, bh, BG, 0.82 * a, r=8 * s)
                put_text(cr, title, bx + padx, by + 14 * s, 'b', 30 * s, col, a, 'lt')
                put_text(cr, desc, bx + padx, by + 56 * s, 'm', 24 * s, SOFT, a, 'lt')
            else:
                label(cr, title, lx, ly, 28 * s, col, a, anc)
        put_text(cr, '한국과의 연결', 70 * s, 150 * s, 'xb', 52 * s, INK, fade(t, 0.1, 0.6), 'lt')
        put_text(cr, '공개 보도 기준 · 위치는 개략', 74 * s, 222 * s, 'm', 26 * s, FAINT, fade(t, 0.1, 0.6), 'lt')
        yield to_bytes(surf, W, H)

# 6) 인천 → 호치민 항로
def gc_points(a, b, n=120):
    (lo1, la1), (lo2, la2) = [(math.radians(x), math.radians(y)) for x, y in (a, b)]
    p1 = np.array([math.cos(la1) * math.cos(lo1), math.cos(la1) * math.sin(lo1), math.sin(la1)])
    p2 = np.array([math.cos(la2) * math.cos(lo2), math.cos(la2) * math.sin(lo2), math.sin(la2)])
    om = math.acos(max(-1, min(1, float(p1 @ p2)))); out = []
    for i in range(n + 1):
        f = i / n; v = (math.sin((1 - f) * om) * p1 + math.sin(f * om) * p2) / math.sin(om)
        out.append((math.degrees(math.atan2(v[1], v[0])), math.degrees(math.asin(v[2]))))
    return out
_world = None
def world():
    global _world
    if _world is None:
        win = box(80, -5, 150, 50)
        _world = unary_union([shape(f['geometry']).intersection(win) for f in json.load(open('/home/claude/media/geo/ne_countries50.geojson'))['features'] if shape(f['geometry']).intersects(win)])
        cs = {}
        for f in json.load(open('/home/claude/media/geo/ne_countries50.geojson'))['features']:
            if f['properties'].get('ADM0_A3') in ('KOR', 'VNM'): cs[f['properties']['ADM0_A3']] = shape(f['geometry'])
        _world = (_world, cs)
    return _world
def anim_flight(W, H, D, cues, opts):
    land, cs = world(); bounds = (95, 4, 136, 42); pj = Proj.fit(bounds, W, H, pad=0.02, rect=(30, 140, W * 0.62, 850)); s = H / 1080
    icn = (126.44, 37.46); sgn = (106.656, 10.818); arc = [pj(*p) for p in gc_points(icn, sgn)]
    c0, c1, c2 = cue(cues, 0), cue(cues, 1), cue(cues, 2)
    for fi in range(int(round(D * FPS))):
        t = fi / FPS; surf, cr = new_frame(W, H)
        cr.set_source_rgba(*rgb(LAND)); path_geom(cr, land, pj); cr.fill()
        cr.set_source_rgba(*rgb(HAIR)); cr.set_line_width(1.2 * s); path_geom(cr, land, pj); cr.stroke()
        for k in ('KOR', 'VNM'):
            cr.set_source_rgba(*rgb(SOFT, 0.18)); path_geom(cr, cs[k], pj); cr.fill()
        pr = ease((t - 0.4) / 3.2); n = max(2, int(len(arc) * pr))
        cr.set_source_rgba(*rgb(BRASS)); cr.set_line_width(5 * s)
        for i, p in enumerate(arc[:n]): (cr.move_to if i == 0 else cr.line_to)(*p)
        cr.stroke()
        dot(cr, *arc[0], 9 * s, INK); dot(cr, *arc[-1], 9 * s, INK if pr < 1 else BRASS)
        if pr < 1: dot(cr, *arc[n - 1], 7 * s, BRASS)
        label(cr, '인천 ICN', arc[0][0] + 18 * s, arc[0][1], 32 * s, INK, fade(t, 0.2), 'lm')
        label(cr, '호치민 SGN', arc[-1][0] - 18 * s, arc[-1][1] + 6 * s, 32 * s, INK, fade(t, 0.2), 'rm')
        k = fade(t, 2.2, 0.7); X = W * 0.66
        put_text(cr, '직항 약 5시간 30분', X, H * 0.34, 'xb', 64 * s, BRASS, k, 'lt')
        put_text(cr, '인천 → 호치민 평균 · 시차 2시간(한국이 빠름)', X, H * 0.34 + 84 * s, 'm', 28 * s, SOFT, k, 'lt')
        k1 = fade(t, c1, 0.7)
        put_text(cr, '대한항공 · 베트남항공 · 비엣젯 등', X, H * 0.50, 'b', 32 * s, INK, k1, 'lt')
        put_text(cr, '왕복 30만 원대 후반부터 · 시기별로 다름', X, H * 0.50 + 50 * s, 'm', 28 * s, SOFT, k1, 'lt')
        k2 = fade(t, c2, 0.7)
        put_text(cr, '롱탄 신공항 개항 뒤', X, H * 0.64, 'b', 32 * s, INK, k2, 'lt')
        put_text(cr, '국제선 단계적 이전 예정 → 도착 공항 확인', X, H * 0.64 + 50 * s, 'm', 28 * s, SOFT, k2, 'lt')
        put_text(cr, '한국에서 가는 법', 70 * s, 150 * s, 'xb', 52 * s, INK, fade(t, 0.1, 0.6), 'lt')
        yield to_bytes(surf, W, H)

# 7) 숫자 카드
NUM = [  # (항목, 호치민, 서울, 브라스 여부, 나타날 cue)
    ('면적', '6,772㎢', '605㎢', '11배', 0), ('인구', '1,400만 명+', '934만 명', '', 1), ('인구밀도(㎢당)', '약 2,070명', '15,432명', '', 2),
    ('탈것', '오토바이 1,130만 대+', '자동차 316만 대', '', 3), ('시차 · 비행', '한국보다 2시간 늦음', '인천에서 직항 약 5시간 30분', '', 4),
    ('베트남의 한국 동포', '19만 2,683명', '세계 5위', '', 5),
]
SRC_NUM = '출처: 호치민시·베트남 보도(2025), 통계청 시도별 인구(2025), 서울시 자동차 등록(2025), 호치민시 건설국(2026), 재외동포청 「2025 재외동포현황」(2024년 말 기준), KAYAK'
def anim_numbers(W, H, D, cues, opts):
    s = H / 1080; X0, X1, X2 = 150 * s, 640 * s, 1240 * s; Y0 = 290 * s; RH = 72 * s
    for fi in range(int(round(D * FPS))):
        t = fi / FPS; surf, cr = new_frame(W, H)
        put_text(cr, '숫자로 보는 호치민', 150 * s, 150 * s, 'xb', 56 * s, INK, fade(t, 0.1), 'lt')
        hk = fade(t, 0.3)
        put_text(cr, '호치민', X1, Y0 - 40 * s, 'b', 28 * s, INK, hk, 'lm'); put_text(cr, '서울', X2, Y0 - 40 * s, 'b', 28 * s, SOFT, hk, 'lm')
        cr.set_source_rgba(*rgb(INK, hk)); cr.rectangle(X0, Y0 - 18 * s, W - X0 - 150 * s, 2 * s); cr.fill()
        for i, (name, a, b, br, ci) in enumerate(NUM):
            k = fade(t, cue(cues, ci) + 0.15, 0.5); y = Y0 + i * RH + RH / 2 + (1 - k) * 14 * s
            if k <= 0: continue
            if i == 4:  # 시차·비행은 한 줄 설명
                put_text(cr, name, X0, y, 'm', 28 * s, SOFT, k, 'lm'); put_text(cr, a, X1, y, 'b', 34 * s, INK, k, 'lm'); put_text(cr, b, X2, y, 'm', 28 * s, SOFT, k, 'lm')
            else:
                put_text(cr, name, X0, y, 'm', 28 * s, SOFT, k, 'lm')
                w = put_text(cr, a, X1, y, 'xb', 40 * s, INK, k, 'lm')
                if br:
                    put_text(cr, br, X1 + w + 22 * s, y, 'xb', 40 * s, BRASS, k, 'lm')
                put_text(cr, b, X2, y, 'b' if i != 5 else 'm', 34 * s if i != 5 else 28 * s, SOFT, k, 'lm')
            cr.set_source_rgba(*rgb(HAIR, k)); cr.rectangle(X0, Y0 + (i + 1) * RH, W - X0 - 150 * s, 1.5 * s); cr.fill()
        put_text(cr, SRC_NUM, X0, Y0 + 6 * RH + 18 * s, 'r', 19 * s, FAINT, fade(t, 0.5), 'lt')
        yield to_bytes(surf, W, H)

# 8) 주거 형태 네 가지
def draw_house(cr, kind, x, y, w, h, col, a):
    cr.set_source_rgba(*rgb(col, a)); cr.set_line_width(3)
    if kind == 'tube':
        for i in range(3):
            bx = x + w * (0.16 + i * 0.24); bw = w * 0.2; bh = h * (0.62 + 0.12 * ((i + 1) % 2))
            cr.rectangle(bx, y + h - bh, bw, bh); cr.stroke()
            for j in range(4): cr.rectangle(bx + bw * 0.3, y + h - bh + bh * (0.1 + j * 0.2), bw * 0.4, bh * 0.08); cr.fill()
    elif kind == 'apt':
        for i, hh in enumerate((0.95, 0.8, 0.9)):
            bx = x + w * (0.12 + i * 0.27); bw = w * 0.22; bh = h * hh
            cr.rectangle(bx, y + h - bh, bw, bh); cr.stroke()
            for j in range(8): cr.move_to(bx + bw * 0.2, y + h - bh + bh * (0.08 + j * 0.11)); cr.line_to(bx + bw * 0.8, y + h - bh + bh * (0.08 + j * 0.11))
            cr.stroke()
    elif kind == 'villa':
        for i in range(2):
            bx = x + w * (0.1 + i * 0.44); bw = w * 0.36; bh = h * 0.42
            cr.rectangle(bx, y + h - bh, bw, bh); cr.stroke()
            cr.move_to(bx - bw * 0.06, y + h - bh); cr.line_to(bx + bw / 2, y + h - bh - h * 0.2); cr.line_to(bx + bw * 1.06, y + h - bh); cr.stroke()
            cr.rectangle(bx + bw * 0.4, y + h - bh * 0.45, bw * 0.2, bh * 0.45); cr.stroke()
    elif kind == 'svc':
        bx = x + w * 0.3; bw = w * 0.4; bh = h * 0.92
        cr.rectangle(bx, y + h - bh, bw, bh); cr.stroke()
        for j in range(7):
            for q in range(3): cr.rectangle(bx + bw * (0.14 + q * 0.27), y + h - bh + bh * (0.08 + j * 0.12), bw * 0.16, bh * 0.06); cr.fill()
    cr.set_source_rgba(*rgb(HAIR, a)); cr.rectangle(x, y + h + 4, w, 2); cr.fill()
HOUSING = [('tube', '튜브하우스', '정면 3~4m · 안으로 긴 집', '구도심 골목'), ('apt', '아파트 대단지', '신도시 고층 단지', '투티엠 · 옛 9군 · 옛 빈즈엉'),
           ('villa', '빌라 단지', '단독·타운하우스', '푸미흥 · 타오디엔'), ('svc', '서비스드 아파트', '호텔식 임대 주거', '외국인 장기 체류')]
def anim_housing(W, H, D, cues, opts):
    s = H / 1080; cw = 380 * s; gap = 40 * s; x0 = (W - 4 * cw - 3 * gap) / 2; y0 = 250 * s
    show = [0.2, cue(cues, 0) + 0.1, cue(cues, 0) + 1.6, cue(cues, 1) + 0.1]
    for fi in range(int(round(D * FPS))):
        t = fi / FPS; surf, cr = new_frame(W, H)
        put_text(cr, '호치민 사람들이 사는 집', x0, 150 * s, 'xb', 56 * s, INK, fade(t, 0.1), 'lt')
        for i, (kind, name, d1, d2) in enumerate(HOUSING):
            k = fade(t, show[i], 0.6); x = x0 + i * (cw + gap)
            if k <= 0: continue
            active = (i == 3 and t >= show[3]) or (i in (1, 2) and show[1] <= t < show[3]) or (i == 0 and t < show[1])
            col = BRASS if active else INK
            cr.set_source_rgba(*rgb(HAIR, k)); cr.set_line_width(1.5 * s); cr.rectangle(x, y0, cw, 480 * s); cr.stroke()
            draw_house(cr, kind, x + 40 * s, y0 + 36 * s, cw - 80 * s, 210 * s, col, k)
            put_text(cr, name, x + 30 * s, y0 + 290 * s, 'xb', 40 * s, col, k, 'lt')
            put_text(cr, d1, x + 30 * s, y0 + 352 * s, 'm', 27 * s, INK, k, 'lt')
            put_text(cr, d2, x + 30 * s, y0 + 396 * s, 'm', 25 * s, FAINT, k, 'lt')
        put_text(cr, '외국인 소유: 아파트 한 동의 30%까지 · 50년 기한 (Viet Nam News)', x0 + 4 * cw + 3 * gap, 175 * s, 'r', 22 * s, FAINT, fade(t, 0.5), 'rm')
        yield to_bytes(surf, W, H)

# 9) 인구 구성 · 외국인 거주지
def anim_people(W, H, D, cues, opts):
    s = H / 1080; c0, c1, c2, c3 = [cue(cues, i) for i in range(4)]
    for fi in range(int(round(D * FPS))):
        t = fi / FPS; surf, cr = new_frame(W, H)
        put_text(cr, '호치민 사람들', 150 * s, 150 * s, 'xb', 56 * s, INK, fade(t, 0.1), 'lt')
        # 민족 막대(2019, 옛 호치민)
        k = fade(t, 0.2, 0.7); bx, by, bw, bh = 150 * s, 290 * s, 760 * s, 34 * s
        put_text(cr, '2019년 인구조사 · 옛 호치민', bx, by - 50 * s, 'm', 26 * s, FAINT, k, 'lt')
        cr.set_source_rgba(*rgb(TRACK, k)); cr.rectangle(bx, by, bw, bh); cr.fill()
        cr.set_source_rgba(*rgb(INK, k)); cr.rectangle(bx, by, bw * 852 / 899 * ease((t - 0.3) / 1.2), bh); cr.fill()
        put_text(cr, '낀족 852만', bx, by + bh + 16 * s, 'b', 32 * s, INK, k, 'lt'); put_text(cr, '전체 899만 명', bx + bw, by + bh + 16 * s, 'm', 28 * s, SOFT, k, 'rt')
        ka = fade(t, c0 + 0.1)
        put_text(cr, '중국계 호아족 · 쩌런 일대에 모여 삶', bx, by + 120 * s, 'b', 32 * s, INK, ka, 'lt')
        kb = fade(t, c1 + 0.1)
        put_text(cr, '합계출산율', bx, by + 220 * s, 'm', 28 * s, SOFT, kb, 'lt')
        w = put_text(cr, '1.39명', bx, by + 262 * s, 'xb', 64 * s, BRASS, kb, 'lt')
        put_text(cr, '베트남에서 가장 낮음 (GSO)', bx + w + 24 * s, by + 290 * s, 'm', 28 * s, SOFT, kb, 'lt')
        # 외국인 동네 두 곳
        for j, (name, side, who, n, ci) in enumerate([('푸미흥', '남쪽 · 옛 7군', '한국인 · 아시아계', '외국인 약 1.3만 명', c2), ('타오디엔', '동쪽 · 옛 2군', '서양계', '외국인 약 1.2만 명', c3)]):
            kk = fade(t, ci + 0.1, 0.6); x = 1060 * s; y = 230 * s + j * 250 * s
            if kk <= 0: continue
            cr.set_source_rgba(*rgb(BRASS if j == (1 if t >= c3 else 0) else HAIR, kk)); cr.set_line_width(2 * s); cr.rectangle(x, y, 700 * s, 220 * s); cr.stroke()
            put_text(cr, name, x + 36 * s, y + 28 * s, 'xb', 46 * s, INK, kk, 'lt'); put_text(cr, side, x + 36 * s, y + 92 * s, 'm', 26 * s, FAINT, kk, 'lt')
            put_text(cr, who, x + 36 * s, y + 130 * s, 'b', 34 * s, INK, kk, 'lt'); put_text(cr, n, x + 36 * s, y + 176 * s, 'm', 28 * s, SOFT, kk, 'lt')
        put_text(cr, '출처: citypopulation(2019 인구조사), GSO, Kyoto Review', 1760 * s, 175 * s, 'r', 22 * s, FAINT, fade(t, 0.5), 'rm')
        yield to_bytes(surf, W, H)

def frames(name, W, H, D, cues, opts):
    if name == 'overlay': return anim_overlay(W, H, D, cues, opts)
    if name == 'overlay_s': return anim_overlay(W, H, D, cues, opts, short=True)
    if name == 'merge': return anim_merge(W, H, D, cues, opts)
    if name == 'axis': return anim_axis(W, H, D, cues, opts)
    if name == 'axis_s': return anim_axis(W, H, D, cues, opts, short=True)
    if name == 'transport': return anim_transport(W, H, D, cues, opts)
    if name == 'korea': return anim_korea(W, H, D, cues, opts)
    if name == 'flight': return anim_flight(W, H, D, cues, opts)
    if name == 'numbers': return anim_numbers(W, H, D, cues, opts)
    if name == 'housing': return anim_housing(W, H, D, cues, opts)
    if name == 'people': return anim_people(W, H, D, cues, opts)
    raise KeyError(name)

def snapshot(name, W, H, D, cues, opts, t):
    """미리보기: t초 프레임 한 장."""
    n = int(t * FPS)
    for i, fr in enumerate(frames(name, W, H, D, cues, opts)):
        if i == n: return Image.frombytes('RGB', (W, H), fr)
