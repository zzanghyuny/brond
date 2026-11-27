# -*- coding: utf-8 -*-
"""도시이야기 썸네일 3장: 본편 1280×720 + 쇼츠 1080×1920 ×2. 사용: python3 thumbs.py <에피소드 폴더>
규칙: 구글 어스 화면 금지, 건물 하나를 크게 잡은 사진 금지, 그라데이션 금지(단색 띠), 황동 숫자는 하나.
설정: script.EP['thumbs'] = {LONG: {clip, t, lines[3], sub, accent}, S1/S2: {kind: 'photo'|'overlay', clip, t, big, small, cx, cy}}
"""
import os, sys, json, subprocess, importlib.util
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dosi_gfx as G
from shapely.geometry import shape
EPD = sys.argv[1]
spec = importlib.util.spec_from_file_location('script', os.path.join(EPD, 'script.py')); S = importlib.util.module_from_spec(spec); spec.loader.exec_module(S)
EP = S.EP; T = EP['thumbs']; GEO = json.load(open(EP['geo'])); O = EP['work'] + 'thumb/'; os.makedirs(O, exist_ok=True)
FP = '/tmp/fonts/'; NX = '/tmp/nanum/NanumGothic-ExtraBold.ttf'; NR = '/tmp/nanum/NanumGothic-Regular.ttf'
XB, B, M = FP + 'Pretendard-ExtraBold.otf', FP + 'Pretendard-Bold.otf', FP + 'Pretendard-Medium.otf'
BG = (8, 8, 9); CREAM = (244, 241, 234); SOFT = (185, 181, 172); FAINT = (150, 148, 142); BRASS = (200, 164, 92)
F = lambda p, s: ImageFont.truetype(p, s)
def wordmark(d, x, y, size, anchor='l'):
    fb, fr = F(NX, size), F(NR, size); wb = d.textlength('브', font=fb); wr = d.textlength('동산', font=fr)
    x0 = x if anchor == 'l' else x - (wb + wr) / 2
    d.text((x0, y), '브', font=fb, fill=CREAM, anchor='lm'); d.text((x0 + wb + size * 0.04, y), '동산', font=fr, fill=SOFT, anchor='lm')
def frame(clip, t):
    p = O + f'f_{clip}_{t}.jpg'
    if not os.path.exists(p): subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(t), '-i', EP['px'] + f'px_{clip}.mp4', '-frames:v', '1', '-q:v', '2', p], check=True)
    return Image.open(p).convert('RGB')
def crop(im, w, h, cx=0.5, cy=0.5):
    r = w / h
    if im.width / im.height > r: nw = int(im.height * r); x = int((im.width - nw) * cx); im = im.crop((x, 0, x + nw, im.height))
    else: nh = int(im.width / r); y = int((im.height - nh) * cy); im = im.crop((0, y, im.width, y + nh))
    return im.resize((w, h), Image.LANCZOS)
def fit_font(d, text, path, size, maxw):
    while size > 40 and d.textlength(text, font=F(path, size)) > maxw: size -= 2
    return F(path, size)
N = EP['names']

# 1) 본편 1280×720: 사진 왼쪽 + 오른쪽 단색 띠
c = T['LONG']; im = crop(frame(c['clip'], c['t']), 1280, 720, c.get('cx', 0.3), c.get('cy', 0.5))
im = ImageEnhance.Contrast(ImageEnhance.Color(im).enhance(1.08)).enhance(1.05)
X = 610; band = Image.new('RGBA', (1280, 720), (0, 0, 0, 0)); ImageDraw.Draw(band).rectangle((X, 0, 1280, 720), fill=BG + (238,))
im = Image.alpha_composite(im.convert('RGBA'), band); d = ImageDraw.Draw(im); L = X + 50
wordmark(d, L, 70, 34); d.text((L, 150), f"도시이야기 {EP['no']}", font=F(M, 30), fill=FAINT, anchor='lm')
for k, ln in enumerate(c['lines']): d.text((L - 4, 250 + k * 100), ln, font=fit_font(d, ln, XB, 84, 1280 - L - 30), fill=CREAM, anchor='lm')
f = F(B, 40); a = c['sub']; wa = d.textlength(a, font=f)
d.text((L, 560), a, font=f, fill=SOFT, anchor='lm'); d.text((L + wa, 560), c['accent'], font=F(XB, 40), fill=BRASS, anchor='lm')
d.rectangle((14, 684, 130, 708), fill=(0, 0, 0)); d.text((22, 696), '영상 Pexels', font=F(M, 18), fill=(230, 230, 230), anchor='lm')
im.convert('RGB').save(O + f"{N['LONG']}-thumbnail.jpg", quality=92); im.convert('RGB').save(O + f"{N['LONG']}-thumbnail.png")

# 2·3) 쇼츠 1080×1920
for which in ('S1', 'S2'):
    c = T[which]; t1, t2 = EP['shorts'][which]
    cv = Image.new('RGB', (1080, 1920), BG); d = ImageDraw.Draw(cv); wordmark(d, 540, 130, 48, 'm')
    d.text((540, 290), t1, font=fit_font(d, t1, XB, 92, 1000), fill=CREAM, anchor='mm')
    d.text((540, 405), t2, font=fit_font(d, t2, XB, 92, 1000), fill=CREAM, anchor='mm')
    if c['kind'] == 'overlay':
        Wm = Hm = 1080; surf, cr = G.new_frame(Wm, Hm); city = shape(GEO[c['city']]); pj = G.Proj.fit(city.bounds, (0, 0, Wm, Hm), pad=0.06)
        cr.set_source_rgba(*G.rgb(G.LAND)); G.path_geom(cr, G.land_frame(pj, Wm, Hm), pj); cr.fill()
        G.stroke_geom(cr, city, pj, G.BRASS, 1.0, 4.0, fill_alpha=0.18)
        se = shape(GEO['seoul']); at = c['seoul_at']
        cr.set_source_rgba(*G.rgb(G.INK, 0.95)); G.path_km(cr, se, (se.centroid.x, se.centroid.y), pj, at); cr.fill()
        x, y = pj(*at); G.label(cr, '서울', x + 22, y - 30, 40, G.INK, 1.0, 'lm'); G.label(cr, c.get('city_label', EP['city']), *pj(*(c.get('city_label_at') or (city.bounds[2] - 1.0, city.bounds[3] - 0.3))), 44, G.BRASS, 1.0, 'rm')
        cv.paste(Image.frombytes('RGB', (Wm, Hm), G.to_bytes(surf, Wm, Hm)), (0, 500))
    else:
        cv.paste(ImageEnhance.Color(crop(frame(c['clip'], c['t']), 1080, 1000, c.get('cx', 0.5), c.get('cy', 0.5))).enhance(1.1), (0, 500))
        d.text((1050, 1480), '영상 Pexels', font=F(M, 22), fill=(230, 230, 230), anchor='rm')
    d.text((540, 1640), c['big'], font=fit_font(d, c['big'], XB, 170, 1000), fill=BRASS, anchor='mm')
    d.text((540, 1775), c['small'], font=F(M, 38), fill=FAINT, anchor='mm')
    cv.save(O + f"{N[which]}-thumbnail.jpg", quality=92); cv.save(O + f"{N[which]}-thumbnail.png")

a = Image.open(O + f"{N['LONG']}-thumbnail.jpg").resize((960, 540))
b = Image.open(O + f"{N['S1']}-thumbnail.jpg").resize((304, 540)); c2 = Image.open(O + f"{N['S2']}-thumbnail.jpg").resize((304, 540))
s = Image.new('RGB', (960 + 304 * 2 + 20, 540), 'white'); s.paste(a, (0, 0)); s.paste(b, (970, 0)); s.paste(c2, (970 + 314, 0)); s.save(O + 'thumbs_prev.jpg', quality=85)
print('ok')
