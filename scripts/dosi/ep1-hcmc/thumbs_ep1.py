# -*- coding: utf-8 -*-
"""도시이야기 1편 썸네일 3장 (구글 어스 미사용, 단일 건물 주인공 없음)."""
import sys, math
sys.path.insert(0, '/home/claude/work/ep1')
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import graphics as G, cairo
O = '/home/claude/work/ep1/thumb/'
FP = '/tmp/fonts/'; NX = '/tmp/nanum/NanumGothic-ExtraBold.ttf'; NR = '/tmp/nanum/NanumGothic-Regular.ttf'
XB, B, M = FP + 'Pretendard-ExtraBold.otf', FP + 'Pretendard-Bold.otf', FP + 'Pretendard-Medium.otf'
BG = (8, 8, 9); CREAM = (244, 241, 234); SOFT = (185, 181, 172); FAINT = (150, 148, 142); BRASS = (200, 164, 92)
F = lambda p, s: ImageFont.truetype(p, s)

def wordmark(d, x, y, size, anchor='l'):
    fb, fr = F(NX, size), F(NR, size); wb = d.textlength('브', font=fb); wr = d.textlength('동산', font=fr)
    x0 = x if anchor == 'l' else x - (wb + wr) / 2
    d.text((x0, y), '브', font=fb, fill=CREAM, anchor='lm'); d.text((x0 + wb + size * 0.04, y), '동산', font=fr, fill=SOFT, anchor='lm')

def crop(im, w, h, cx=0.5, cy=0.5):
    r = w / h
    if im.width / im.height > r: nw = int(im.height * r); x = int((im.width - nw) * cx); im = im.crop((x, 0, x + nw, im.height))
    else: nh = int(im.width / r); y = int((im.height - nh) * cy); im = im.crop((0, y, im.width, y + nh))
    return im.resize((w, h), Image.LANCZOS)

# ---- 1) 가로 1280x720 (사진 왼쪽: 강 굽이 · 글자 오른쪽 단색 띠)
ph = Image.open(O + 'f_33846690_7.jpg').convert('RGB')
im = crop(ph, 1280, 720, 0.0, 0.5); im = ImageEnhance.Contrast(ImageEnhance.Color(im).enhance(1.08)).enhance(1.05)
X = 600
band = Image.new('RGBA', (1280, 720), (0, 0, 0, 0)); ImageDraw.Draw(band).rectangle((X, 0, 1280, 720), fill=BG + (236,))
im = Image.alpha_composite(im.convert('RGBA'), band); d = ImageDraw.Draw(im)
L = X + 52
wordmark(d, L, 70, 34)
d.text((L, 150), '도시이야기 1', font=F(M, 30), fill=FAINT, anchor='lm')
d.text((L - 4, 250), '호치민은 왜', font=F(XB, 84), fill=CREAM, anchor='lm')
d.text((L - 4, 350), '이런 모양이', font=F(XB, 84), fill=CREAM, anchor='lm')
d.text((L - 4, 450), '됐을까', font=F(XB, 84), fill=CREAM, anchor='lm')
f = F(B, 40); a = '강을 따라 자란 도시 '; wa = d.textlength(a, font=f)
d.text((L, 560), a, font=f, fill=SOFT, anchor='lm'); d.text((L + wa, 560), '300년', font=F(XB, 40), fill=BRASS, anchor='lm')
d.rectangle((14, 684, 130, 708), fill=(0, 0, 0)); d.text((22, 696), '영상 Pexels', font=F(M, 18), fill=(230, 230, 230), anchor='lm')
im.convert('RGB').save(O + 'hcmc-dosi-1-youtube-thumbnail.jpg', quality=92)

# ---- 2) 쇼츠1 1080x1920: 서울 겹쳐 보기
W, H = 1080, 1080
surf, cr = G.new_frame(W, H)
bounds = (106.25, 10.33, 107.62, 11.52); pj = G.Proj.fit(bounds, W, H, pad=0.05)
G.draw_base(cr, pj, bounds, W, H, river_w=2.5)
G.stroke_geom(cr, G.HC_NEW_M, pj, G.BRASS, 1.0, 4.0, fill_alpha=0.18)
at = G.ll('ben_thanh')
cr.set_source_rgba(*G.rgb(G.INK, 0.16)); G.path_km(cr, G.SEOUL, G.SEOUL_C, pj, at); cr.fill()
cr.set_source_rgba(*G.rgb(G.INK, 1.0)); cr.set_line_width(3.6); G.path_km(cr, G.SEOUL, G.SEOUL_C, pj, at); cr.stroke()
sx, sy = pj(*at); G.label(cr, '서울', sx, sy - 17 * pj.spk - 14, 40, G.INK, 1.0, 'mb')
G.label(cr, '호치민', *pj(107.25, 10.66), 44, G.BRASS, 1.0, 'mm')
mp = Image.frombytes('RGB', (W, H), G.to_bytes(surf, W, H))
cv = Image.new('RGB', (1080, 1920), BG); d = ImageDraw.Draw(cv)
wordmark(d, 540, 130, 48, 'm')
d.text((540, 290), '호치민은 서울보다', font=F(XB, 92), fill=CREAM, anchor='mm')
d.text((540, 405), '얼마나 클까', font=F(XB, 92), fill=CREAM, anchor='mm')
cv.paste(mp, (0, 500))
d.text((540, 1650), '11배', font=F(XB, 170), fill=BRASS, anchor='mm')
d.text((540, 1775), '같은 축척으로 겹쳐 본 면적', font=F(M, 36), fill=FAINT, anchor='mm')
cv.save(O + 'hcmc-dosi-1-shorts-size-thumbnail.jpg', quality=92)

# ---- 3) 쇼츠2 1080x1920: 강을 건넌 주거축
ph = Image.open(O + 'f_33846690_2.jpg').convert('RGB')
cv = Image.new('RGB', (1080, 1920), BG); d = ImageDraw.Draw(cv)
wordmark(d, 540, 130, 48, 'm')
d.text((540, 290), '호치민 사람들은', font=F(XB, 92), fill=CREAM, anchor='mm')
d.text((540, 405), '왜 강을 건넜을까', font=F(XB, 92), fill=CREAM, anchor='mm')
cv.paste(ImageEnhance.Color(crop(ph, 1080, 1000, 0.32, 0.6)).enhance(1.08), (0, 500))
d.text((540, 1630), '주거축 3단계', font=F(XB, 110), fill=BRASS, anchor='mm')
d.text((540, 1750), '강 서쪽 → 남쪽·동쪽 → 북쪽', font=F(B, 44), fill=CREAM, anchor='mm')
d.text((1050, 1480), '영상 Pexels', font=F(M, 22), fill=(230, 230, 230), anchor='rm')
cv.save(O + 'hcmc-dosi-1-shorts-axis-thumbnail.jpg', quality=92)

a = Image.open(O + 'hcmc-dosi-1-youtube-thumbnail.jpg').resize((960, 540))
b = Image.open(O + 'hcmc-dosi-1-shorts-size-thumbnail.jpg').resize((304, 540)); c = Image.open(O + 'hcmc-dosi-1-shorts-axis-thumbnail.jpg').resize((304, 540))
s = Image.new('RGB', (960 + 304 * 2 + 20, 540), 'white'); s.paste(a, (0, 0)); s.paste(b, (970, 0)); s.paste(c, (970 + 314, 0)); s.save(O + 'thumbs_prev.jpg', quality=85)
print('ok')
