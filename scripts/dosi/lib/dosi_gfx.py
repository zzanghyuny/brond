# -*- coding: utf-8 -*-
"""도시이야기 공용 지도·카드 애니메이션 (cairo + PIL 글자).
frames(name, W, H, D, cues, opts, geo, short=False) -> RGB bytes 프레임 생성기.
A안(본편) 톤: 어두운 바탕, 가는 금색 선, 명조 숫자. 쇼츠도 같은 그림을 세로로 쓴다.
그래픽 장면은 짧게(본편 12초 이하) — 모든 요소가 1초 안에 다 뜨도록 빠르게 등장시킨다.
"""
import json, math, functools
import numpy as np, cairo
from PIL import Image, ImageDraw, ImageFont
from shapely.geometry import shape, box
from shapely.ops import unary_union

FPS = 30
UI = 1.0   # 글자 크기 배율(네이버 모바일 이미지 1.3)
BG = (0x08, 0x08, 0x09); LAND = (0x15, 0x15, 0x17); HAIR = (0x2A, 0x2A, 0x2D); TRACK = (0x22, 0x22, 0x25)
INK = (0xF4, 0xF1, 0xEA); SOFT = (0xB9, 0xB5, 0xAC); FAINT = (0x96, 0x94, 0x8E); DIM = (0x5A, 0x58, 0x54); BRASS = (0xC8, 0xA4, 0x5C)
GOLD = (0xD6, 0xBC, 0x80); RIVER = (0x3A, 0x45, 0x52)
COL = dict(ink=INK, soft=SOFT, faint=FAINT, dim=DIM, brass=BRASS, gold=GOLD, river=RIVER, hair=HAIR)
FP = '/tmp/fonts/'
FONTS = {'sb': FP + 'Pretendard-SemiBold.otf', 'b': FP + 'Pretendard-Bold.otf', 'xb': FP + 'Pretendard-ExtraBold.otf',
         'm': FP + 'Pretendard-Medium.otf', 'r': FP + 'Pretendard-Regular.otf', 'se': FP + 'NotoSerifKR.ttf'}
LAND10 = '/home/claude/media/geo/ne_land10.geojson'

def c01(x): return max(0.0, min(1.0, x))
def ease(x): x = c01(x); return x * x * (3 - 2 * x)
def eout(x): x = c01(x); return 1 - (1 - x) ** 3
def rgb(c, a=1.0): return (c[0] / 255, c[1] / 255, c[2] / 255, a)
def fade(t, t0, d=0.45): return ease((t - t0) / d)
def cue(cues, i): return cues[i] if i < len(cues) else (cues[-1] + 1.5 * (i - len(cues) + 1) if cues else 0.0)
def col(c): return COL[c] if isinstance(c, str) else c

# ---------- 글자
@functools.lru_cache(maxsize=1024)
def _font(font, size):
    if font.startswith('se'):
        f = ImageFont.truetype(FONTS['se'], size)
        try: f.set_variation_by_axes([int(font[2:] or 5) * 100])
        except Exception: pass
        return f
    return ImageFont.truetype(FONTS[font], size)

@functools.lru_cache(maxsize=1024)
def text_surface(s, font='sb', size=40, color=INK, stroke=0):
    f = _font(font, size)
    d0 = ImageDraw.Draw(Image.new('L', (1, 1)))
    l, t, r, b = d0.textbbox((0, 0), s, font=f, stroke_width=stroke)
    w, h = r - l + 8, b - t + 8
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.text((4 - l, 4 - t), s, font=f, fill=color + (255,), stroke_width=stroke, stroke_fill=(8, 8, 9, 255))
    a = np.asarray(im).astype(np.float32); al = a[..., 3:4] / 255.0
    pre = np.ascontiguousarray(np.concatenate([a[..., 2:3] * al, a[..., 1:2] * al, a[..., 0:1] * al, a[..., 3:4]], axis=2).astype(np.uint8))
    surf = cairo.ImageSurface.create_for_data(memoryview(bytearray(pre.tobytes())), cairo.FORMAT_ARGB32, w, h, w * 4)
    return surf, w - 8, h - 8

def put_text(cr, s, x, y, font='sb', size=40, color=INK, alpha=1.0, anchor='lt', stroke=0):
    if alpha <= 0.001 or not s: return 0
    surf, w, h = text_surface(s, font, int(size * UI), tuple(col(color)), stroke)
    ax = {'l': 0, 'm': 0.5, 'r': 1}[anchor[0]]; ay = {'t': 0, 'm': 0.5, 'b': 1}[anchor[1]]
    cr.save(); cr.set_source_surface(surf, x - ax * w - 4, y - ay * h - 4); cr.paint_with_alpha(alpha); cr.restore()
    return w

def text_w(s, font='sb', size=40): return text_surface(s, font, int(size * UI), INK, 0)[1]

# ---------- 투영
class Proj:
    def __init__(self, lon0, lat0, spk, cx, cy):
        self.lon0, self.lat0, self.spk, self.cx, self.cy = lon0, lat0, spk, cx, cy
        self.kx = 111.32 * math.cos(math.radians(lat0)); self.ky = 110.57
    def __call__(self, lon, lat):
        return self.cx + (lon - self.lon0) * self.kx * self.spk, self.cy - (lat - self.lat0) * self.ky * self.spk
    @staticmethod
    def fit(bounds, rect, pad=0.06):
        x0, y0, x1, y1 = bounds; lat0 = (y0 + y1) / 2; lon0 = (x0 + x1) / 2
        kx = 111.32 * math.cos(math.radians(lat0)); wk = (x1 - x0) * kx; hk = (y1 - y0) * 110.57
        rw, rh = rect[2] - rect[0], rect[3] - rect[1]
        spk = min(rw * (1 - 2 * pad) / wk, rh * (1 - 2 * pad) / hk)
        return Proj(lon0, lat0, spk, (rect[0] + rect[2]) / 2, (rect[1] + rect[3]) / 2)

def path_geom(cr, g, pj):
    t = g.geom_type
    if t in ('LineString', 'MultiLineString'):
        for ln in ([g] if t == 'LineString' else g.geoms):
            for i, (x, y) in enumerate(ln.coords):
                px, py = pj(x, y); (cr.move_to if i == 0 else cr.line_to)(px, py)
        return
    polys = [g] if t == 'Polygon' else list(getattr(g, 'geoms', []))
    for p in polys:
        if p.geom_type != 'Polygon': continue
        for ring in [p.exterior] + list(p.interiors):
            for i, (x, y) in enumerate(ring.coords):
                px, py = pj(x, y); (cr.move_to if i == 0 else cr.line_to)(px, py)
            cr.close_path()

def path_km(cr, g, origin, pj, at):
    """g(경위도)를 origin 기준 km 모양으로 바꿔 pj 화면의 at 위치에 같은 축척으로 그린다."""
    lon0, lat0 = origin; kx0 = 111.32 * math.cos(math.radians(lat0)); ky = 110.57
    ax, ay = pj(*at); s = pj.spk
    polys = [g] if g.geom_type == 'Polygon' else list(g.geoms)
    for p in polys:
        for i, (x, y) in enumerate(p.exterior.coords):
            (cr.move_to if i == 0 else cr.line_to)(ax + (x - lon0) * kx0 * s, ay - (y - lat0) * ky * s)
        cr.close_path()

_land = {}
def land_for(bounds):
    k = tuple(round(b, 2) for b in bounds)
    if k not in _land:
        win = box(bounds[0] - 3, bounds[1] - 3, bounds[2] + 3, bounds[3] + 3)
        feats = json.load(open(LAND10))['features']
        _land[k] = unary_union([shape(f['geometry']).intersection(win) for f in feats if shape(f['geometry']).intersects(win)])
    return _land[k]

def land_frame(pj, W, H, pad=0.5):
    """화면 전체를 덮는 육지(경위도 창을 화면 크기에서 거꾸로 계산)."""
    lon0 = pj.lon0 + (0 - pj.cx) / (pj.kx * pj.spk); lon1 = pj.lon0 + (W - pj.cx) / (pj.kx * pj.spk)
    lat1 = pj.lat0 + (pj.cy - 0) / (pj.ky * pj.spk); lat0 = pj.lat0 + (pj.cy - H) / (pj.ky * pj.spk)
    k = (round(lon0 - pad, 1), round(lat0 - pad, 1), round(lon1 + pad, 1), round(lat1 + pad, 1))
    if k not in _land:
        win = box(*k); feats = json.load(open(LAND10))['features']
        _land[k] = unary_union([shape(f['geometry']).intersection(win) for f in feats if shape(f['geometry']).intersects(win)])
    return _land[k]

def new_frame(W, H):
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H); cr = cairo.Context(surf)
    cr.set_source_rgb(*rgb(BG)[:3]); cr.paint(); cr.set_line_join(cairo.LINE_JOIN_ROUND); cr.set_line_cap(cairo.LINE_CAP_ROUND)
    return surf, cr
def to_bytes(surf, W, H):
    a = np.ndarray((H, W, 4), np.uint8, surf.get_data()); return np.ascontiguousarray(a[..., [2, 1, 0]]).tobytes()

def stroke_geom(cr, g, pj, color, alpha, width, fill_alpha=0.0, dash=None):
    if alpha <= 0.001: return
    color = col(color)
    if fill_alpha > 0 and g.geom_type not in ('LineString', 'MultiLineString'):
        cr.set_source_rgba(*rgb(color, fill_alpha * alpha)); path_geom(cr, g, pj); cr.fill()
    cr.set_source_rgba(*rgb(color, alpha)); cr.set_line_width(width)
    if dash: cr.set_dash(dash)
    path_geom(cr, g, pj); cr.stroke(); cr.set_dash([])

def rrect(cr, x, y, w, h, r):
    cr.new_sub_path(); cr.arc(x + w - r, y + r, r, -math.pi / 2, 0); cr.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    cr.arc(x + r, y + h - r, r, math.pi / 2, math.pi); cr.arc(x + r, y + r, r, math.pi, 1.5 * math.pi); cr.close_path()

def label(cr, s, x, y, size, color=INK, alpha=1.0, anchor='lm', font='sb', box_alpha=0.8):
    if alpha <= 0.001: return
    w = text_w(s, font, size); h = size * UI * 1.35; padx = size * UI * 0.42
    ax = {'l': 0, 'm': 0.5, 'r': 1}[anchor[0]]; ay = {'t': 0, 'm': 0.5, 'b': 1}[anchor[1]]
    bx = x - ax * (w + 2 * padx); by = y - ay * h
    rrect(cr, bx, by, w + 2 * padx, h, size * UI * 0.22); cr.set_source_rgba(*rgb(BG, box_alpha * alpha)); cr.fill()
    put_text(cr, s, bx + padx, by + h / 2, font, size, color, alpha, 'lm')

def dot(cr, x, y, r, color, alpha=1.0):
    if alpha <= 0.001: return
    cr.arc(x, y, r + max(2, r * 0.45), 0, 2 * math.pi); cr.set_source_rgba(*rgb(BG, alpha)); cr.fill()
    cr.arc(x, y, r, 0, 2 * math.pi); cr.set_source_rgba(*rgb(col(color), alpha)); cr.fill()

def bezier_pts(p0, p1, bend=0.2, n=60, prog=1.0):
    (x0, y0), (x1, y1) = p0, p1; mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    cx, cy = mx - (y1 - y0) * bend, my + (x1 - x0) * bend; pts = []
    for i in range(n + 1):
        t = i / n * prog; a = (1 - t) ** 2; b = 2 * (1 - t) * t; c = t * t
        pts.append((a * x0 + b * cx + c * x1, a * y0 + b * cy + c * y1))
    return pts

def polyline(cr, pts, color, alpha, width, dash=None):
    if alpha <= 0.001 or len(pts) < 2: return
    cr.set_source_rgba(*rgb(col(color), alpha)); cr.set_line_width(width)
    if dash: cr.set_dash(dash)
    for i, (x, y) in enumerate(pts): (cr.move_to if i == 0 else cr.line_to)(x, y)
    cr.stroke(); cr.set_dash([])

def side_text(cr, side, t, cues, x, y, s, short=False):
    """오른쪽(세로면 아래) 큰 숫자 블록: title(작게) / big(명조 황동) / sub(작게). 각 항목 at=cue 번호."""
    if not side: return
    yy = y
    for key, font, size, color in (('title', 'b', 34, INK), ('big', 'se7', 112, BRASS), ('sub', 'm', 30, SOFT), ('sub2', 'm', 26, FAINT)):
        if key not in side: continue
        txt, at = side[key] if isinstance(side[key], (list, tuple)) else (side[key], 0)
        a = fade(t, cue(cues, at) + (0.25 if key != 'title' else 0.0), 0.45)
        put_text(cr, txt, x, yy, font, size * s, color, a, 'mt' if short else 'lt')
        yy += (size * UI * 1.32 + (10 if key == 'big' else 6)) * s

# =====================================================================
# 1) 같은 축척으로 겹쳐 보기: 도시 경계 + 서울 + (선택) 비교 영역(남한 등)
def anim_overlay(W, H, D, cues, o, geo, short=False):
    city = shape(geo[o['city']]); seoul = shape(geo['seoul']); comp = shape(geo[o['compare']]) if o.get('compare') else None
    s = min(W, H) / 803 if not short else W / 1080
    rect = (0, 0, W, H * 0.62) if short else (40, 20, W * 0.62, H - 20)
    b = city.bounds; pj = Proj.fit(b, rect, pad=0.07)
    at = o.get('seoul_at') or (city.centroid.x, city.centroid.y)
    sc = (seoul.centroid.x, seoul.centroid.y)
    comp_at = o.get('compare_at') or (city.centroid.x, city.centroid.y)
    cc = (comp.centroid.x, comp.centroid.y) if comp else None
    c0, c1 = cue(cues, 0), cue(cues, 1)
    for fi in range(int(round(D * FPS))):
        t = fi / FPS; surf, cr = new_frame(W, H)
        cr.set_source_rgba(*rgb(LAND)); path_geom(cr, land_frame(pj, W, H), pj); cr.fill()
        a_c = fade(t, 0.05, 0.5)
        stroke_geom(cr, city, pj, BRASS, a_c, 3.2 * s, fill_alpha=0.16)
        a_k = fade(t, c1 + 0.1, 0.6) if comp else 0
        if a_k > 0:
            cr.set_source_rgba(*rgb(INK, 0.06 * a_k)); path_km(cr, comp, cc, pj, comp_at); cr.fill()
            cr.set_source_rgba(*rgb(INK, 0.85 * a_k)); cr.set_line_width(2.2 * s); cr.set_dash([9 * s, 7 * s]); path_km(cr, comp, cc, pj, comp_at); cr.stroke(); cr.set_dash([])
        a_s = fade(t, c0 + 0.6, 0.5)
        cr.set_source_rgba(*rgb(INK, 0.9 * a_s)); path_km(cr, seoul, sc, pj, at); cr.fill()
        x, y = pj(*at); label(cr, o.get('seoul_label', '서울 605㎢'), x + 18 * s, y - 24 * s, 28 * s, INK, a_s, 'lm')
        if comp:
            kx, ky = pj(comp_at[0] - 1.8, comp_at[1] + 1.6); label(cr, o.get('compare_label', ''), kx, ky, 28 * s, INK, a_k, 'mm')
        label(cr, o.get('city_label', ''), *pj(b[2] - 0.8, b[3] - 0.2), 30 * s, BRASS, a_c, 'rm')
        if short: side_text(cr, o.get('side'), t, cues, W / 2, H * 0.66, s, True)
        else: side_text(cr, o.get('side'), t, cues, W * 0.66, H * 0.22, s)
        yield to_bytes(surf, W, H)

# 2) 숫자 표 (빠르게: 모든 줄이 1초 안에 뜬다)
def anim_numbers(W, H, D, cues, o, geo, short=False):
    rows = o['rows']; s = (W / 1080) if short else H / 803
    if short: X0, X1, X2, Y0, RH, W2 = 60 * s, 60 * s, 60 * s, 380 * s, 150 * s, W - 120 * s
    else: X0, X1, X2, Y0, RH = 150 * s, 640 * s, 1250 * s, 210 * s, 76 * s
    head = o.get('head', ('', ''))
    for fi in range(int(round(D * FPS))):
        t = fi / FPS; surf, cr = new_frame(W, H)
        put_text(cr, o['title'], X0, (220 if short else 90) * s, 'se7', (64 if short else 52) * s, INK, fade(t, 0.0, 0.35), 'lt')
        hk = fade(t, 0.15, 0.35)
        if not short:
            put_text(cr, head[0], X1, Y0 - 36 * s, 'b', 26 * s, BRASS, hk, 'lm'); put_text(cr, head[1], X2, Y0 - 36 * s, 'b', 26 * s, SOFT, hk, 'lm')
            cr.set_source_rgba(*rgb(INK, hk)); cr.rectangle(X0, Y0 - 14 * s, W - X0 - 150 * s, 2 * s); cr.fill()
        for i, r in enumerate(rows):
            a = fade(t, 0.25 + 0.12 * i, 0.3); y = Y0 + i * RH
            if short:
                put_text(cr, r[0], X0, y, 'm', 34 * s, SOFT, a, 'lt')
                put_text(cr, r[1], X0, y + 44 * s, 'se7', 60 * s, BRASS if r[3] else INK, a, 'lt')
                if r[2]: put_text(cr, '서울 ' + r[2], W - 60 * s, y + 52 * s, 'm', 32 * s, FAINT, a, 'rt')
                cr.set_source_rgba(*rgb(HAIR, a)); cr.rectangle(X0, y + RH - 18 * s, W - 120 * s, 1.5 * s); cr.fill()
            else:
                put_text(cr, r[0], X0, y + RH / 2, 'm', 28 * s, SOFT, a, 'lm')
                put_text(cr, r[1], X1, y + RH / 2, 'se6', 36 * s, BRASS if r[3] else INK, a, 'lm')
                put_text(cr, r[2], X2, y + RH / 2, 'm', 28 * s, SOFT, a, 'lm')
                cr.set_source_rgba(*rgb(HAIR, a)); cr.rectangle(X0, y + RH - 1, W - X0 - 150 * s, 1.5 * s); cr.fill()
        src = o.get('src')
        if src: put_text(cr, src, X0, (Y0 + len(rows) * RH + 18 * s), 'r', (22 if short else 18) * s, FAINT, fade(t, 0.6), 'lt')
        yield to_bytes(surf, W, H)

# 3) 범용 지도: 강·구역·점·이름표가 cue에 맞춰 빠르게 등장
def anim_map(W, H, D, cues, o, geo, short=False):
    s = (W / 1080) if short else H / 803
    rect = (0, H * 0.10, W, H * 0.70) if short else ((40, 20, W * 0.64, H - 20) if o.get('side') else (60, 20, W - 60, H - 20))
    pj = Proj.fit(o['bounds'], rect, pad=0.04); P = geo['places']
    def ll(k): return (P[k]['lon'], P[k]['lat']) if isinstance(k, str) else k
    land = land_frame(pj, W, H)
    for fi in range(int(round(D * FPS))):
        t = fi / FPS; surf, cr = new_frame(W, H)
        cr.set_source_rgba(*rgb(LAND)); path_geom(cr, land, pj); cr.fill()
        for L in o.get('layers', []):
            g = shape(geo[L['g']]); a = fade(t, cue(cues, L.get('at', 0)) + L.get('d', 0.0), 0.45) * L.get('alpha', 1.0)
            if L.get('until') is not None: a *= 1 - 0.65 * fade(t, cue(cues, L['until']), 0.4)
            stroke_geom(cr, g, pj, L.get('color', 'river'), a, L.get('width', 2.0) * s, L.get('fill', 0.0), [L['dash'][0] * s, L['dash'][1] * s] if L.get('dash') else None)
            if L.get('label'):
                tx, lon, lat = L['label']; label(cr, tx, *pj(lon, lat), 26 * s, col(L.get('lcolor', 'soft')), a, 'mm', font='se6')
        for z in o.get('zones', []):
            a = fade(t, cue(cues, z.get('at', 0)) + z.get('d', 0.0), 0.45)
            if a <= 0: continue
            x, y = pj(*ll(z['p'])); r = z['rkm'] * pj.spk
            cr.arc(x, y, r, 0, 2 * math.pi); cr.set_source_rgba(*rgb(col(z.get('color', 'brass')), (0.22 if z.get('color', 'brass') == 'brass' else 0.08) * a)); cr.fill()
            cr.arc(x, y, r, 0, 2 * math.pi); cr.set_source_rgba(*rgb(col(z.get('color', 'brass')), a)); cr.set_line_width(2.4 * s); cr.stroke()
            if z.get('label'):
                dx, dy = z.get('off', (0, -1)); label(cr, z['label'], x + dx * (r + 14 * s), y + dy * (r + 18 * s), 26 * s, col(z.get('color', 'brass')), a, 'mm')
        for m in o.get('markers', []):
            a = fade(t, cue(cues, m.get('at', 0)) + m.get('d', 0.0), 0.4)
            x, y = pj(*ll(m['p'])); dot(cr, x, y, m.get('r', 7) * s, m.get('color', 'brass'), a)
            if m.get('label'):
                dx, dy = m.get('off', (1, 0)); label(cr, m['label'], x + dx * 16 * s, y + dy * 22 * s, m.get('size', 26) * s, col(m.get('lcolor', 'ink')), a, m.get('anchor', 'lm'))
        for tx in o.get('texts', []):
            a = fade(t, cue(cues, tx.get('at', 0)) + tx.get('d', 0.0), 0.45)
            put_text(cr, tx['s'], *pj(*ll(tx['p'])), tx.get('font', 'se6'), tx.get('size', 30) * s, col(tx.get('color', 'soft')), a * tx.get('alpha', 1.0), 'mm')
        if o.get('stage'):
            n, name, when = o['stage']; a = fade(t, 0.0, 0.35)
            if short: put_text(cr, f'{n}  {name}', W / 2, H * 0.075, 'b', 44 * s, INK, a, 'mm'); put_text(cr, when, W / 2, H * 0.115, 'm', 30 * s, FAINT, a, 'mm')
            else: label(cr, f'{n}  {name}', 70 * s, 70 * s, 34 * s, INK, a, 'lm', font='b'); put_text(cr, when, 80 * s, 118 * s, 'm', 24 * s, FAINT, a, 'lm')
        if short: side_text(cr, o.get('side'), t, cues, W / 2, H * 0.74, s, True)
        else: side_text(cr, o.get('side'), t, cues, W * 0.68, H * 0.24, s)
        yield to_bytes(surf, W, H)

# 4) 경로(연도와 함께 점을 차례로 잇기)
def anim_route(W, H, D, cues, o, geo, short=False):
    s = (W / 1080) if short else H / 803; P = geo['places']
    rect = (0, H * 0.10, W, H * 0.72) if short else (40, 20, W * 0.66, H - 20)
    pj = Proj.fit(o['bounds'], rect, pad=0.05); land = land_frame(pj, W, H)
    pts = [(pj(P[k]['lon'], P[k]['lat']), lab, yr) for k, lab, yr in o['stops']]
    t0 = cue(cues, o.get('start_at', 0)) + 0.2; span = max(1.0, min(o.get('span', 4.0), D - t0 - 1.2)); n = len(pts) - 1
    for fi in range(int(round(D * FPS))):
        t = fi / FPS; surf, cr = new_frame(W, H)
        cr.set_source_rgba(*rgb(LAND)); path_geom(cr, land, pj); cr.fill()
        for L in o.get('layers', []):
            stroke_geom(cr, shape(geo[L['g']]), pj, L.get('color', 'hair'), L.get('alpha', 1.0), L.get('width', 1.5) * s, L.get('fill', 0.0))
        p = c01((t - t0) / span) * n
        for i in range(n):
            seg = c01(p - i)
            if seg <= 0: break
            (a0, _, _), (a1, _, _) = pts[i], pts[i + 1]
            polyline(cr, bezier_pts(a0, a1, 0.12, 30, seg), BRASS, 0.95, 3.2 * s)
        for i, ((x, y), lab, yr) in enumerate(pts):
            a = fade(t, t0 + (i / max(1, n)) * span - 0.15, 0.3); last = i == n
            dot(cr, x, y, (9 if last else 6) * s, BRASS if last else INK, a)
            if lab:
                off = o.get('offsets', {}).get(lab, (1, 0))
                label(cr, f'{lab} {yr}' if yr else lab, x + off[0] * 16 * s, y + off[1] * 24 * s, (30 if last else 24) * s, BRASS if last else SOFT, a, 'lm' if off[0] >= 0 else 'rm')
        if short: side_text(cr, o.get('side'), t, cues, W / 2, H * 0.75, s, True)
        else: side_text(cr, o.get('side'), t, cues, W * 0.70, H * 0.24, s)
        yield to_bytes(surf, W, H)

# 5) 항로(인천 → 도시)
def anim_flight(W, H, D, cues, o, geo, short=False):
    s = (W / 1080) if short else H / 803; P = geo['places']
    rect = (0, H * 0.10, W, H * 0.70) if short else (40, 20, W * 0.64, H - 20)
    pj = Proj.fit(o['bounds'], rect, pad=0.08); land = land_frame(pj, W, H)
    a0 = pj(P['icn']['lon'], P['icn']['lat']); a1 = pj(P[o['dest']]['lon'], P[o['dest']]['lat'])
    for fi in range(int(round(D * FPS))):
        t = fi / FPS; surf, cr = new_frame(W, H)
        cr.set_source_rgba(*rgb(LAND)); path_geom(cr, land, pj); cr.fill()
        pr = eout((t - 0.3) / 1.8)
        polyline(cr, bezier_pts(a0, a1, 0.18, 80, 1.0), HAIR, 1.0, 2 * s, [6 * s, 6 * s])
        pts = bezier_pts(a0, a1, 0.18, 80, max(0.001, pr)); polyline(cr, pts, BRASS, 0.95, 3.4 * s)
        dot(cr, *a0, 7 * s, INK, fade(t, 0.05)); label(cr, '인천', a0[0] + 14 * s, a0[1] + 24 * s, 28 * s, INK, fade(t, 0.05), 'lm')
        dot(cr, *a1, 9 * s, BRASS, fade(t, 1.8)); label(cr, o['dest_label'], a1[0] + 16 * s, a1[1] + 30 * s, 30 * s, BRASS, fade(t, 1.8), 'lm')
        if short: side_text(cr, o.get('side'), t, cues, W / 2, H * 0.74, s, True)
        else: side_text(cr, o.get('side'), t, cues, W * 0.68, H * 0.26, s)
        yield to_bytes(surf, W, H)

# 6) 숫자 카드(큰 숫자 2~4개)
def anim_card(W, H, D, cues, o, geo, short=False):
    s = (W / 1080) if short else H / 803; items = o['items']; n = len(items)
    for fi in range(int(round(D * FPS))):
        t = fi / FPS; surf, cr = new_frame(W, H)
        put_text(cr, o['title'], W / 2, (300 if short else 110) * s, 'se7', (60 if short else 46) * s, INK, fade(t, 0.0, 0.35), 'mm')
        for i, it in enumerate(items):
            big, lab, at = it[0], it[1], (it[2] if len(it) > 2 else 0)
            a = fade(t, cue(cues, at) + 0.1 + 0.12 * i, 0.35)
            if short: cx, cy = W / 2, (520 + i * 300) * s
            else:
                cols = min(n, 4); cx = W * (i % cols + 0.5) / cols; cy = (330 + (i // cols) * 260) * s
            put_text(cr, big, cx, cy, 'se7', (92 if short else 78) * s, BRASS if i == 0 else INK, a, 'mm')
            put_text(cr, lab, cx, cy + (78 if short else 66) * s, 'm', (34 if short else 26) * s, SOFT, a, 'mm')
        if o.get('src'): put_text(cr, o['src'], W / 2, H - (90 if short else 40) * s, 'r', (22 if short else 18) * s, FAINT, fade(t, 0.5), 'mm')
        yield to_bytes(surf, W, H)

# 7) 건물 단면(층 구간)
def anim_stack(W, H, D, cues, o, geo, short=False):
    s = (W / 1080) if short else H / 803; floors = o['floors']; segs = o['segs']
    bw = (420 if short else 300) * s; fh = (44 if short else 30) * s; bx = W / 2 - bw / 2 - (0 if short else 260 * s)
    by = (1500 if short else 720) * s
    for fi in range(int(round(D * FPS))):
        t = fi / FPS; surf, cr = new_frame(W, H)
        put_text(cr, o['title'], W / 2, (210 if short else 70) * s, 'se7', (56 if short else 44) * s, INK, fade(t, 0.0, 0.35), 'mm')
        for k in range(floors):
            a = fade(t, 0.1 + 0.025 * k, 0.25); y = by - (k + 1) * fh
            seg = next(sg for sg in segs if sg[0] <= k + 1 <= sg[1]); c = col(seg[3])
            cr.rectangle(bx, y + 2 * s, bw, fh - 4 * s); cr.set_source_rgba(*rgb(c, (0.9 if seg[3] == 'brass' else 0.35) * a)); cr.fill()
        for i, (f0, f1, lab, c) in enumerate(segs):
            a = fade(t, cue(cues, o.get('label_at', [0] * len(segs))[i]) + 0.3 + 0.15 * i, 0.35)
            ym = by - (f0 - 1 + (f1 - f0 + 1) / 2) * fh
            cr.set_source_rgba(*rgb(INK, 0.5 * a)); cr.set_line_width(1.5 * s); cr.move_to(bx + bw + 12 * s, ym); cr.line_to(bx + bw + 60 * s, ym); cr.stroke()
            put_text(cr, f'{f0}~{f1}층' if f0 != f1 else f'{f0}층', bx + bw + 72 * s, ym - 22 * s, 'se6', 46 * s, col(c) if c == 'brass' else INK, a, 'lm')
            put_text(cr, lab, bx + bw + 72 * s, ym + 26 * s, 'm', 32 * s, SOFT, a, 'lm')
        tr = o.get('train')
        if tr:
            f = tr['floor']; y = by - (f - 0.5) * fh; p = c01((t - 0.9) / 2.2)
            cr.set_source_rgba(*rgb(SOFT, 0.7)); cr.set_line_width(3 * s); cr.move_to(bx - 260 * s, y); cr.line_to(bx + bw + 40 * s, y); cr.stroke()
            x = bx - 260 * s + (bw + 300 * s) * p - 120 * s; cr.rectangle(x, y - 16 * s, 160 * s, 32 * s); cr.set_source_rgba(*rgb(INK, 0.95 * (p > 0))); cr.fill()
        yield to_bytes(surf, W, H)

ANIMS = dict(overlay=anim_overlay, numbers=anim_numbers, map=anim_map, route=anim_route, flight=anim_flight, card=anim_card, stack=anim_stack)
def frames(name, W, H, D, cues, opts, geo, short=False):
    return ANIMS[name](W, H, D, cues, opts, geo, short)
