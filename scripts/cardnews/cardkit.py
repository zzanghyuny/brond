# -*- coding: utf-8 -*-
"""브동산 카드뉴스 공통 도구 — 1080×1350(4:5), 흑백 + 황동 포인트.
dark 테마(영상·썸네일과 같은 색)를 기본으로 쓴다. 기준: docs/cardnews-plan.md, 디자인 가이드라인 9장.
"""
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
FP = '/tmp/fonts/'
FONTS = {'xb': 'Pretendard-ExtraBold.otf', 'b': 'Pretendard-Bold.otf', 'sb': 'Pretendard-SemiBold.otf',
         'm': 'Pretendard-Medium.otf', 'r': 'Pretendard-Regular.otf'}
C = dict(paper='#080809', soft_bg='#141416', hair='#2A2A2D', ink='#F4F1EA', ink_soft='#B9B5AC',
         faint='#96948E', brass='#C8A45C', brass_ink='#D9BC7E', brass_tint='#2A2416')
M = 64          # 좌우 여백


def font(k, size):
    return ImageFont.truetype(FP + FONTS[k], size)


def new():
    im = Image.new('RGB', (W, H), C['paper'])
    return im, ImageDraw.Draw(im)


def fit(src, w, h, cx=0.5, cy=0.5):
    """사진을 w×h로 꽉 채워 자른다(cx·cy = 자를 때 중심)."""
    im = Image.open(src).convert('RGB') if isinstance(src, str) else src
    s = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x = min(max(0, round(im.width * cx - w / 2)), im.width - w)
    y = min(max(0, round(im.height * cy - h / 2)), im.height - h)
    return im.crop((x, y, x + w, y + h))


def wrap(d, text, f, maxw):
    """띄어쓰기 단위로 줄바꿈. '\n'은 강제 줄바꿈."""
    out = []
    for para in text.split('\n'):
        line = ''
        for word in para.split(' '):
            t = (line + ' ' + word).strip()
            if d.textlength(t, font=f) <= maxw or not line:
                line = t
            else:
                out.append(line)
                line = word
        out.append(line)
    return out


def text(d, xy, s, f, fill, maxw=None, lh=1.45, anchor='la'):
    """여러 줄 글. 마지막 줄 아래 y를 돌려준다."""
    x, y = xy
    lines = wrap(d, s, f, maxw) if maxw else s.split('\n')
    step = round(f.size * lh)
    for ln in lines:
        d.text((x, y), ln, font=f, fill=fill, anchor=anchor)
        y += step
    return y


def chrome(im, d, page, total, label, credit=None):
    """매 장 공통: 왼쪽 위 시리즈 라벨, 오른쪽 위 쪽 번호, 아래 워드마크·출처."""
    f = font('sb', 26)
    d.text((M, 54), label, font=f, fill=C['faint'], anchor='lm')
    pg = f'{page}/{total}'
    fw = d.textlength(pg, font=f)
    d.rounded_rectangle((W - M - fw - 28, 34, W - M, 74), radius=20, fill=C['paper'], outline=C['hair'], width=2)
    d.text((W - M - 14, 54), pg, font=f, fill=C['ink'], anchor='rm')
    wordmark(d, M, H - 50)
    if credit:
        d.text((W - M, H - 50), credit, font=font('r', 22), fill=C['faint'], anchor='rm')


def wordmark(d, x, y, size=34):
    fb, fr = font('xb', size), font('r', size)
    d.text((x, y), '브', font=fb, fill=C['ink'], anchor='lm')
    d.text((x + d.textlength('브', font=fb) + 1, y), '동산', font=fr, fill=C['ink_soft'], anchor='lm')


def band(im, y0, y1, alpha=0.86):
    """사진 위 글자용 단색 띠(그라데이션 없음)."""
    ov = Image.new('RGBA', (W, y1 - y0), (8, 8, 9, round(255 * alpha)))
    im.paste(ov, (0, y0), ov)


def chip(d, xy, s, f, fill=None, color=None, pad=(16, 8)):
    x, y = xy
    tw = d.textlength(s, font=f)
    d.rectangle((x, y, x + tw + pad[0] * 2, y + f.size + pad[1] * 2), fill=fill or C['paper'])
    d.text((x + pad[0], y + pad[1] + f.size / 2), s, font=f, fill=color or C['ink'], anchor='lm')
    return x + tw + pad[0] * 2


def hline(d, y, x0=M, x1=W - M, color=None, width=2):
    d.line((x0, y, x1, y), fill=color or C['hair'], width=width)
