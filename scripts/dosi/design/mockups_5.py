# -*- coding: utf-8 -*-
"""도시이야기 영상 디자인 5안 시안(같은 실사·같은 문장, 디자인만 다르게)."""
import sys, math, numpy as np
sys.path.insert(0, '/home/claude/work/ep1')
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps
import graphics as G, cairo
T = '/home/claude/work/ep1/thumb/'; O = '/home/claude/work/ep1/mock/'
import os; os.makedirs(O, exist_ok=True)
FP = '/tmp/fonts/'
PSB, PB, PXB, PM, PR = (FP + f for f in ('Pretendard-SemiBold.otf', 'Pretendard-Bold.otf', 'Pretendard-ExtraBold.otf', 'Pretendard-Medium.otf', 'Pretendard-Regular.otf'))
MONO = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'
NX, NR = '/tmp/nanum/NanumGothic-ExtraBold.ttf', '/tmp/nanum/NanumGothic-Regular.ttf'
W, H = 1920, 1080
BRASS = (200, 164, 92); CREAM = (244, 241, 234); SOFT = (185, 181, 172); FAINT = (150, 148, 142); INK = (17, 17, 17); BG = (8, 8, 9)
def F(p, s): return ImageFont.truetype(p, s)
def SERIF(s, w=600):
    f = ImageFont.truetype(FP + 'NotoSerifKR.ttf', s)
    try: f.set_variation_by_axes([w])
    except Exception: pass
    return f
def load(name): return Image.open(T + name).convert('RGB').resize((W, H), Image.LANCZOS)
def wordmark(d, x, y, size, c1=CREAM, c2=SOFT, anchor='l'):
    fb, fr = F(NX, size), F(NR, size); wb = d.textlength('브', font=fb); wr = d.textlength('동산', font=fr)
    x0 = x if anchor == 'l' else (x - (wb + wr) if anchor == 'r' else x - (wb + wr) / 2)
    d.text((x0, y), '브', font=fb, fill=c1, anchor='lm'); d.text((x0 + wb + size * 0.04, y), '동산', font=fr, fill=c2, anchor='lm')
def shadow_text(im, xy, s, f, fill, blur=8, alpha=210, stroke=0, anchor='mm'):
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
    sd.text((xy[0] + 2, xy[1] + 3), s, font=f, fill=(0, 0, 0, alpha), anchor=anchor, stroke_width=stroke + 2, stroke_fill=(0, 0, 0, alpha))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(blur))); ImageDraw.Draw(im).text(xy, s, font=f, fill=fill, anchor=anchor)

# ---------- 지도(팔레트 바꿔 그리기)
def map_img(w, h, pal, rect=None, seoul=True, label=True):
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, w, h); cr = cairo.Context(surf)
    cr.set_source_rgb(*[c / 255 for c in pal['sea']]); cr.paint(); cr.set_line_join(cairo.LINE_JOIN_ROUND)
    bounds = (106.25, 10.33, 107.62, 11.52); pj = G.Proj.fit(bounds, w, h, pad=0.06, rect=rect)
    cr.set_source_rgb(*[c / 255 for c in pal['land']]); G.path_geom(cr, G.land_for(bounds), pj); cr.fill()
    cr.set_source_rgb(*[c / 255 for c in pal['river']]); cr.set_line_width(2.5)
    for r in G.RIV: G.path_geom(cr, r, pj); cr.stroke()
    c = pal['hc']; cr.set_source_rgba(c[0] / 255, c[1] / 255, c[2] / 255, pal.get('hc_fill', 0.18)); G.path_geom(cr, G.HC_NEW_M, pj); cr.fill()
    cr.set_source_rgb(*[x / 255 for x in c]); cr.set_line_width(pal.get('lw', 3)); G.path_geom(cr, G.HC_NEW_M, pj); cr.stroke()
    at = G.ll('ben_thanh')
    if seoul:
        s = pal['seoul']; cr.set_source_rgba(s[0] / 255, s[1] / 255, s[2] / 255, pal.get('se_fill', 0.2)); G.path_km(cr, G.SEOUL, G.SEOUL_C, pj, at); cr.fill()
        cr.set_source_rgb(*[x / 255 for x in s]); cr.set_line_width(pal.get('lw', 3)); G.path_km(cr, G.SEOUL, G.SEOUL_C, pj, at); cr.stroke()
    a = np.ndarray((h, w, 4), np.uint8, surf.get_data()); im = Image.fromarray(np.ascontiguousarray(a[..., [2, 1, 0]]))
    return im, pj, at

# ===================== A. 시네마틱 다큐
def grade_teal_orange(im):
    a = np.asarray(im).astype(np.float32) / 255; l = a.mean(2, keepdims=True)
    a = a + (0.5 - l) * np.array([-0.06, 0.02, 0.07]) * 1.0 + (l - 0.5) * np.array([0.10, 0.03, -0.08])
    a = np.clip((a - 0.5) * 1.12 + 0.5, 0, 1); return Image.fromarray((a * 255).astype(np.uint8))
def grain(im, k=10):
    n = np.random.default_rng(3).normal(0, k, (H, W, 1)); a = np.clip(np.asarray(im).astype(np.float32) + n, 0, 255); return Image.fromarray(a.astype(np.uint8))
def letterbox(im):
    bh = int((H - W / 2.39) / 2); d = ImageDraw.Draw(im); d.rectangle((0, 0, W, bh), fill=(0, 0, 0)); d.rectangle((0, H - bh, W, H), fill=(0, 0, 0)); return bh
def A1():
    im = grain(grade_teal_orange(load('f_33846690_7.jpg'))).convert('RGBA'); bh = letterbox(im); d = ImageDraw.Draw(im)
    d.text((70, bh // 2), 'Ⅱ  강이 만든 도시', font=SERIF(34, 500), fill=(214, 200, 170), anchor='lm')
    d.text((W - 70, bh // 2), '10°47′N  106°42′E', font=F(MONO, 26), fill=(150, 146, 136), anchor='rm')
    d.text((W // 2, H - bh // 2), '호치민은 강이 만든 도시예요. 사이공강이 크게 휘어 흐르고,', font=SERIF(42, 500), fill=(240, 234, 220), anchor='mm')
    return im.convert('RGB')
def A2():
    pal = dict(sea=(6, 7, 8), land=(18, 19, 20), river=(48, 52, 56), hc=(200, 164, 92), seoul=(236, 230, 214), hc_fill=0.10, se_fill=0.10, lw=1.6)
    m, pj, at = map_img(W, H, pal, rect=(80, 150, W * 0.62, 930)); im = grain(m, 6).convert('RGBA'); bh = letterbox(im); d = ImageDraw.Draw(im)
    d.text((W * 0.80, 400), '11', font=SERIF(230, 700), fill=(210, 182, 120), anchor='mm')
    d.text((W * 0.80, 560), '서울을 열한 번 겹친 넓이', font=SERIF(40, 500), fill=(232, 226, 210), anchor='mm')
    d.text((W * 0.80, 620), '호치민 6,772㎢ · 서울 605㎢', font=SERIF(28, 400), fill=(160, 156, 146), anchor='mm')
    d.text((W // 2, H - bh // 2), '서울보다 열한 배쯤 넓어요.', font=SERIF(42, 500), fill=(240, 234, 220), anchor='mm')
    return im.convert('RGB')

# ===================== B. 리얼 생생(현장감)
def vivid(im): return ImageEnhance.Contrast(ImageEnhance.Color(ImageEnhance.Brightness(im).enhance(1.05)).enhance(1.35)).enhance(1.08)
def chip(d, x, y, text, f, bg=(255, 255, 255), fg=INK, dot=BRASS, pad=18, r=28):
    w = d.textlength(text, font=f); h = f.size + pad * 1.1
    d.rounded_rectangle((x, y, x + w + pad * 2 + 30, y + h), r, fill=bg); d.ellipse((x + pad, y + h / 2 - 8, x + pad + 16, y + h / 2 + 8), fill=dot)
    d.text((x + pad + 30, y + h / 2), text, font=f, fill=fg, anchor='lm')
def big_sub(im, lines, y_bottom=930, size=64, hl=None):
    d = ImageDraw.Draw(im); f = F(PXB, size); lh = int(size * 1.3)
    for k, ln in enumerate(lines):
        y = y_bottom - lh * (len(lines) - k - 0.5)
        if hl and hl in ln:
            a, b = ln.split(hl, 1); wa, wh, wb = d.textlength(a, font=f), d.textlength(hl, font=f), d.textlength(b, font=f); x0 = W / 2 - (wa + wh + wb) / 2
            for txt, x, col in ((a, x0, (255, 255, 255)), (hl, x0 + wa, BRASS), (b, x0 + wa + wh, (255, 255, 255))):
                d.text((x, y), txt, font=f, fill=col, anchor='lm', stroke_width=7, stroke_fill=(0, 0, 0))
        else: d.text((W // 2, y), ln, font=f, fill=(255, 255, 255), anchor='mm', stroke_width=7, stroke_fill=(0, 0, 0))
def B1():
    im = vivid(load('f_35527318_5.jpg')).convert('RGBA'); d = ImageDraw.Draw(im)
    chip(d, 50, 44, '옛 1군 · 벤탄 시장', F(PB, 34))
    mm, pj, at = map_img(360, 240, dict(sea=(20, 22, 26), land=(44, 46, 50), river=(90, 110, 130), hc=(200, 164, 92), seoul=(255, 255, 255), hc_fill=0.25), seoul=False)
    md = ImageDraw.Draw(mm); x, y = pj(*G.ll('ben_thanh')); md.ellipse((x - 9, y - 9, x + 9, y + 9), fill=(255, 80, 60), outline='white', width=3)
    mm = ImageOps.expand(mm, border=5, fill='white'); im.paste(mm, (W - 420, 40))
    d.rounded_rectangle((1180, 330, 1640, 450), 22, fill=(255, 255, 255)); d.polygon([(1240, 450), (1280, 450), (1200, 510)], fill=(255, 255, 255))
    d.text((1210, 362), '1862년', font=F(PXB, 44), fill=BRASS, anchor='lm'); d.text((1210, 418), '프랑스 도시 계획 시작', font=F(PB, 32), fill=INK, anchor='lm')
    big_sub(im, ['도시 모양을 크게 바꾼 건', '프랑스였어요.'], hl='프랑스')
    return im.convert('RGB')
def B2():
    im = vivid(load('f_31149203_10.jpg')).convert('RGBA'); d = ImageDraw.Draw(im)
    chip(d, 50, 44, '호치민 출근길', F(PB, 34))
    d.rounded_rectangle((W // 2 - 420, 250, W // 2 + 420, 520), 36, fill=(0, 0, 0, 0), outline=None)
    st = Image.new('RGBA', (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
    sd.rounded_rectangle((W // 2 - 430, 230, W // 2 + 430, 500), 40, fill=(255, 255, 255, 240))
    sd.text((W // 2, 320), '오토바이 1,130만 대', font=F(PXB, 84), fill=INK, anchor='mm'); sd.text((W // 2, 420), '서울 자동차의 세 배 반', font=F(PB, 46), fill=BRASS, anchor='mm')
    im.alpha_composite(st.rotate(-3, center=(W // 2, 365), resample=Image.BICUBIC))
    big_sub(im, ['출퇴근 시간이면 다리와 교차로가', '오토바이로 가득 차요.'], hl='오토바이')
    return im.convert('RGB')

# ===================== C. 에디토리얼 매거진(밝은 지면)
def C1():
    im = Image.new('RGB', (W, H), (250, 249, 246)); d = ImageDraw.Draw(im)
    ph = load('f_32427386_8.jpg').resize((1100, 619), Image.LANCZOS); im.paste(ph, (90, 230)); d.rectangle((90, 230, 1190, 849), outline=(227, 227, 227), width=2)
    d.text((90, 870), '사이공강과 운하 · 영상 Pexels', font=F(PR, 24), fill=(138, 138, 138), anchor='lt')
    wordmark(d, 90, 120, 38, c1=INK, c2=(85, 85, 85)); d.text((W - 90, 120), '도시이야기 1 — 호치민', font=F(PM, 28), fill=(85, 85, 85), anchor='rm')
    d.line((90, 170, W - 90, 170), fill=(17, 17, 17), width=2)
    x = 1270; d.text((x, 250), '02', font=F(PXB, 110), fill=BRASS, anchor='lt'); d.text((x, 390), '강이 만든 도시', font=F(PXB, 62), fill=INK, anchor='lt')
    body = ['호치민은 강이 만든 도시예요.', '사이공강이 크게 휘어 흐르고,', '운하가 시가지 사이를 지나가요.', '강 서쪽은 옛 시가지,', '강 건너는 새 동네예요.']
    for k, ln in enumerate(body): d.text((x, 500 + k * 58), ln, font=F(PM, 38), fill=(40, 40, 40), anchor='lt')
    return im
def C2():
    pal = dict(sea=(232, 236, 238), land=(250, 249, 246), river=(200, 210, 216), hc=(17, 17, 17), seoul=(200, 164, 92), hc_fill=0.04, se_fill=0.35, lw=2.4)
    im, pj, at = map_img(W, H, pal, rect=(60, 190, W * 0.60, 1000)); d = ImageDraw.Draw(im)
    wordmark(d, 90, 120, 38, c1=INK, c2=(85, 85, 85)); d.line((90, 170, W - 90, 170), fill=(17, 17, 17), width=2)
    x = 1240; d.text((x, 280), '서울과 겹쳐 보기', font=F(PXB, 58), fill=INK, anchor='lt')
    d.text((x, 380), '6,772㎢', font=F(PXB, 120), fill=INK, anchor='lt'); d.text((x, 530), '지금의 호치민 · 서울의 약 11배', font=F(PB, 38), fill=(122, 92, 34), anchor='lt')
    d.rectangle((x, 610, x + 36, 640), fill=(200, 164, 92)); d.text((x + 52, 625), '서울 605㎢(같은 축척)', font=F(PM, 30), fill=(60, 60, 60), anchor='lm')
    d.text((x, 960), '지도 © OpenStreetMap contributors · Natural Earth', font=F(PR, 22), fill=(138, 138, 138), anchor='lt')
    return im

# ===================== D. 위성 데이터 저널리즘(HUD)
def hud(im, d):
    for gx in range(0, W, 240): d.line((gx, 0, gx, H), fill=(120, 200, 190, 40), width=1)
    for gy in range(0, H, 240): d.line((0, gy, W, gy), fill=(120, 200, 190, 40), width=1)
    fm = F(MONO, 22)
    for k, gx in enumerate(range(240, W, 480)): d.text((gx + 6, 14), f'106.{62 + k * 4:02d}°E', font=fm, fill=(170, 230, 220, 200))
    for k, gy in enumerate(range(240, H, 480)): d.text((10, gy + 6), f'10.{82 - k * 4:02d}°N', font=fm, fill=(170, 230, 220, 200))
def D1():
    g = Image.open('/home/claude/media/gearth/g1_overview.png').convert('RGB'); r = W / H; w = int(g.height * r); x = (g.width - w) // 2
    im = ImageEnhance.Brightness(g.crop((x, 0, x + w, g.height)).resize((W, H), Image.LANCZOS)).enhance(0.72).convert('RGBA')
    ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov); hud(im, d)
    fm = F(MONO, 24); fk = F(PB, 32)
    for (px, py, tx, ty, t1, t2) in [(760, 520, 380, 300, '옛 1군 격자 시가지', 'GRID · 1862'), (1130, 600, 1350, 330, '투티엠', 'PLAN · 1996'), (1000, 880, 1300, 860, '사이공강', 'RIVER')]:
        d.ellipse((px - 10, py - 10, px + 10, py + 10), outline=(255, 214, 120, 255), width=3); d.line((px, py, tx, ty + 40), fill=(255, 214, 120, 230), width=2)
        d.rectangle((tx - 6, ty - 4, tx + max(d.textlength(t1, font=fk), d.textlength(t2, font=fm)) + 16, ty + 84), fill=(0, 0, 0, 170))
        d.text((tx + 4, ty + 2), t1, font=fk, fill=(255, 255, 255, 255)); d.text((tx + 4, ty + 46), t2, font=fm, fill=(255, 214, 120, 255))
    d.line((70, 1000, 330, 1000), fill=(255, 255, 255, 230), width=4); d.text((70, 970), '0        5 km', font=fm, fill=(255, 255, 255, 230))
    d.text((W - 40, H - 30), 'Google Earth · 이미지 Airbus', font=F(PM, 22), fill=(255, 255, 255, 220), anchor='rm')
    d.rectangle((0, 0, W, 0), fill=(0, 0, 0, 0)); im.alpha_composite(ov); d2 = ImageDraw.Draw(im)
    d2.rectangle((560, 900, 1360, 960), fill=(0, 0, 0, 190)); d2.text((W // 2, 930), '강변에서 안쪽으로 반듯한 격자 도로가 깔렸어요.', font=F(PSB, 36), fill='white', anchor='mm')
    return im.convert('RGB')
def D2():
    pal = dict(sea=(4, 12, 16), land=(14, 26, 30), river=(40, 90, 100), hc=(255, 214, 120), seoul=(160, 240, 230), hc_fill=0.10, se_fill=0.15, lw=2)
    m, pj, at = map_img(W, H, pal, rect=(40, 80, W * 0.62, 1040)); im = m.convert('RGBA'); ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov); hud(im, d)
    fm = F(MONO, 26); x0 = 1240
    d.text((x0, 200), 'AREA  km²', font=fm, fill=(170, 230, 220, 255))
    for k, (name, v, col) in enumerate([('HCMC', 6772, (255, 214, 120)), ('SEOUL', 605, (160, 240, 230))]):
        y = 260 + k * 120; bw = 560 * v / 6772
        d.rectangle((x0, y, x0 + 560, y + 56), outline=(80, 120, 120, 255), width=1); d.rectangle((x0, y, x0 + bw, y + 56), fill=col + (255,))
        d.text((x0, y + 70), f'{name}  {v:,}', font=fm, fill=(230, 240, 238, 255))
    d.text((x0, 560), 'RATIO  ×11.2', font=F(MONO, 54), fill=(255, 214, 120, 255))
    d.text((x0, 640), '© OpenStreetMap · Natural Earth', font=F(MONO, 20), fill=(140, 170, 168, 255))
    im.alpha_composite(ov); d2 = ImageDraw.Draw(im); d2.rectangle((560, 900, 1360, 960), fill=(0, 0, 0, 190)); d2.text((W // 2, 930), '서울보다 열한 배쯤 넓어요.', font=F(PSB, 36), fill='white', anchor='mm')
    return im.convert('RGB')

# ===================== E. 미니멀 모노 + 황동
def E1():
    im = ImageOps.grayscale(load('f_33846690_7.jpg')); im = ImageEnhance.Contrast(im).enhance(1.25).convert('RGBA')
    ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov); d.rectangle((0, 0, W, H), fill=(0, 0, 0, 70)); im.alpha_composite(ov); d = ImageDraw.Draw(im)
    d.text((110, 300), '300', font=F(PXB, 260), fill=BRASS, anchor='lt'); d.text((120, 590), '년, 강을 따라 자란 도시', font=F(PB, 54), fill=CREAM, anchor='lt')
    wordmark(d, 110, 120, 40)
    shadow_text(im, (W // 2, 900), '호치민은 강이 만든 도시예요.', F(PSB, 50), (255, 255, 255))
    return im.convert('RGB')
def E2():
    im = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(im); wordmark(d, 110, 120, 40)
    d.text((W // 2, 420), '6,772㎢', font=F(PXB, 230), fill=CREAM, anchor='mm')
    w = d.textlength('서울의 ', font=F(PB, 64)); x0 = W / 2 - (w + d.textlength('11배', font=F(PXB, 64))) / 2
    d.text((x0, 610), '서울의 ', font=F(PB, 64), fill=SOFT, anchor='lm'); d.text((x0 + w, 610), '11배', font=F(PXB, 64), fill=BRASS, anchor='lm')
    d.line((W // 2 - 60, 700, W // 2 + 60, 700), fill=(60, 60, 62), width=2)
    d.text((W // 2, 750), '2025년 합병 뒤 호치민 · 서울 605㎢', font=F(PM, 30), fill=FAINT, anchor='mm')
    return im

STYLES = [('A', '시네마틱 다큐', '2.39:1 영화 화면비·필름 질감·명조 자막(자막이 화면을 안 가림)', A1, A2),
          ('B', '리얼 생생', '채도 높은 실사·굵은 자막·위치 칩·미니맵·숫자 말풍선', B1, B2),
          ('C', '에디토리얼 매거진', '밝은 지면에 사진과 글을 나눠 배치하는 잡지 레이아웃', C1, C2),
          ('D', '위성 데이터 저널리즘', '위성 위에 좌표 격자·주석선·데이터 막대(HUD)', D1, D2),
          ('E', '미니멀 모노 + 황동', '흑백 실사·큰 숫자·황동 한 점(브동산 가이드라인 그대로)', E1, E2)]
rows = []
for k, name, desc, f1, f2 in STYLES:
    a, b = f1(), f2(); a.save(O + f'{k}1.jpg', quality=90); b.save(O + f'{k}2.jpg', quality=90)
    row = Image.new('RGB', (1940, 640), 'white'); dr = ImageDraw.Draw(row)
    dr.text((10, 34), f'{k}  {name}', font=F(PXB, 44), fill=INK, anchor='lm'); dr.text((10 + dr.textlength(f'{k}  {name}', font=F(PXB, 44)) + 24, 36), desc, font=F(PM, 28), fill=(90, 90, 90), anchor='lm')
    row.paste(a.resize((960, 540), Image.LANCZOS), (0, 80)); row.paste(b.resize((960, 540), Image.LANCZOS), (980, 80)); rows.append(row)
    row.save(O + f'design-{k}.jpg', quality=88)
sheet = Image.new('RGB', (1940, 640 * len(rows)), 'white')
for i, r in enumerate(rows): sheet.paste(r, (0, i * 640))
sheet.save(O + 'design-5-options.jpg', quality=86); print('ok', sheet.size)
