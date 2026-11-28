# -*- coding: utf-8 -*-
"""도시이야기 카드뉴스 — '이 도시는 왜 이런 모양일까' (docs/cardnews-plan.md ④, 2026.11.28 Paul: 실제 사는 모습·희한한 주거형태 사진을 더).
사용: python3 scripts/cardnews/city.py <도시 키>   예) brasilia
- 숫자·문구는 그 도시 대본(scripts/dosi/epN-*/script.py)·사이트 글과 같은 값만 쓴다. 표지에 Google Earth 화면 금지.
- 사진: Pexels(영상 정지 화면·사진) + Wikimedia Commons(CC BY / CC BY-SA, 작가·라이선스를 장 아래와 캡션 파일에 표기).
- 결과: /home/claude/work/cardnews/<키>/01.png … + 카드뉴스-캡션.txt(캡션·해시태그·사진 출처 전체)
"""
import os, subprocess, sys
sys.path.insert(0, os.path.dirname(__file__))
from cardkit import *



def src_image(cfg, P, spec, tag):
    """('px', 영상id, 초) 영상 정지 화면 | ('img', 경로) 사진 | ('ge', 파일) 구글 어스 | ('site', 파일, crop) 사이트 이미지"""
    kind = spec[0]
    if kind == 'px':
        out = f'{P}/_{tag}.jpg'
        if not os.path.exists(out):
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(spec[2]), '-i', f"{cfg['px']}px_{spec[1]}.mp4",
                            '-frames:v', '1', '-q:v', '1', out], check=True)
        return Image.open(out).convert('RGB')
    if kind == 'img':
        return Image.open(spec[1]).convert('RGB')
    if kind == 'ge':
        return Image.open(cfg['ge'] + spec[1]).convert('RGB')
    im = Image.open(cfg['site'] + spec[1]).convert('RGB')
    return im.crop(spec[2]) if len(spec) > 2 else im


from city_cfg import CITIES

def head(d, kicker, title, y=120):
    if kicker:
        d.text((M, y), kicker, font=font('b', 30), fill=C['brass'], anchor='lt')
        y += 50
    return text(d, (M, y), title, font('xb', 64), C['ink'], maxw=W - 2 * M, lh=1.2)


def credit_line(d, s):
    """긴 사진 출처는 워드마크 위(오른쪽 정렬, 넘치면 줄바꿈)."""
    f = font('r', 21)
    lines = wrap(d, s, f, W - 2 * M)
    y = H - 96 - (len(lines) - 1) * 28
    for ln in lines:
        d.text((W - M, y), ln, font=f, fill=C['faint'], anchor='rm')
        y += 28


def card_cover(cfg, P, n):
    c = cfg['cover']
    im = fit(src_image(cfg, P, c['photo'], 'cover'), W, H, cx=c['cx'])
    band(im, 800, H, 0.88)
    d = ImageDraw.Draw(im)
    chrome(im, d, 1, n, '', credit=c['credit'])
    d.text((M, 860), c['kicker'], font=font('b', 34), fill=C['brass'], anchor='lt')
    y = text(d, (M, 920), c['title'], font('xb', 96), C['ink'], lh=1.18)
    text(d, (M, y + 18), c['sub'], font('m', 36), C['ink_soft'])
    return im


def card_numbers(cfg, P, page, n):
    c = cfg['numbers']
    im, d = new()
    chrome(im, d, page, n, cfg['label'], credit=c['credit'])
    y = head(d, None, c['title'])
    im.paste(fit(src_image(cfg, P, c['photo'], 'num'), W - 2 * M, 330), (M, y + 20))
    y += 20 + 330 + 30
    for big, desc, hi in c['rows']:
        hline(d, y)
        d.text((M, y + 28), big, font=font('xb', 70), fill=C['brass'] if hi else C['ink'], anchor='lt')
        text(d, (M, y + 116), desc, font('m', 32), C['ink_soft'], maxw=W - 2 * M)
        y += 200
    hline(d, y)
    d.text((M, y + 22), c['src'], font=font('r', 22), fill=C['faint'], anchor='lt')
    return im


def label_on(d, x, y, lab, sub=None):
    x2 = chip(d, (x, y), lab, font('b', 30))
    if sub:
        chip(d, (x2, y), sub, font('m', 26), color=C['ink_soft'], pad=(4, 10))


def card_reason(cfg, P, r, page, n):
    im, d = new()
    chrome(im, d, page, n, cfg['label'])
    y = head(d, f'이렇게 된 이유 {r["no"]}/3', r['title']) + 28
    if r.get('pair'):
        hh = r.get('hh', 380)
        for k, (spec, lab, sub, cy) in enumerate(r['pair']):
            im.paste(fit(src_image(cfg, P, spec, f'r{r["no"]}{k}'), W - 2 * M, hh, cy=cy), (M, y))
            d = ImageDraw.Draw(im)
            label_on(d, M, y + hh - 56, lab, sub)
            y += hh + 18
    else:
        ph = fit(src_image(cfg, P, r['img'], f'r{r["no"]}'), W - 2 * M, r.get('h', 600))
        im.paste(ph, (M, y))
        d = ImageDraw.Draw(im)
        y += ph.height + 18
    text(d, (M, y + 20), r['body'], font('m', 38), C['ink'], maxw=W - 2 * M, lh=1.55)
    credit_line(d, r['credit'])
    return im


def card_feature(cfg, P, f, page, n, tag):
    im, d = new()
    chrome(im, d, page, n, cfg['label'])
    y = head(d, f['kicker'], f['title']) + 28
    if f.get('photo'):
        hh = f.get('h', 640)
        im.paste(fit(src_image(cfg, P, f['photo'], tag), W - 2 * M, hh, cy=f.get('cy', 0.5)), (M, y))
        d = ImageDraw.Draw(im)
        if f.get('tag'):
            label_on(d, M, y, f['tag'])
        if f.get('mark'):   # 사진 속 한 곳을 가리키는 황동 표시 (원본 사진 비율 기준 y)
            my, mx = y + round(hh * f['mark'][0]), M + round((W - 2 * M) * f['mark'][2])
            d.line((mx, my + 26, mx, my + 70), fill=C['brass'], width=5)
            d.polygon([(mx - 12, my + 62), (mx + 12, my + 62), (mx, my + 82)], fill=C['brass'])
            chip(d, (mx - 30, my - 26), f['mark'][1], font('b', 28), fill=C['brass'], color=C['paper'])
        y += hh + 18
    else:
        g = 14
        big_h, small_h = 420, 300
        (s0, l0, c0), (s1, l1, c1), (s2, l2, c2) = f['grid']
        im.paste(fit(src_image(cfg, P, s0, tag + 'a'), W - 2 * M, big_h, cy=c0), (M, y))
        sw = (W - 2 * M - g) // 2
        im.paste(fit(src_image(cfg, P, s1, tag + 'b'), sw, small_h, cy=c1), (M, y + big_h + g))
        im.paste(fit(src_image(cfg, P, s2, tag + 'c'), sw, small_h, cy=c2), (M + sw + g, y + big_h + g))
        d = ImageDraw.Draw(im)
        label_on(d, M, y + big_h - 56, l0)
        label_on(d, M, y + big_h + g + small_h - 56, l1)
        label_on(d, M + sw + g, y + big_h + g + small_h - 56, l2)
        y += big_h + g + small_h + 18
    y = text(d, (M, y + 14), f['body'], font('m', 36), C['ink'], maxw=W - 2 * M, lh=1.5)
    d.text((M, y + 6), f['src'], font=font('r', 22), fill=C['faint'], anchor='lt')
    credit_line(d, f['credit'])
    return im


def card_three(cfg, P, page, n):
    c = cfg['three']
    im, d = new()
    chrome(im, d, page, n, cfg['label'])
    y = head(d, c['kicker'], c['title']) + 26
    hh, g = 250, 14
    for k, (spec, cy, lab, sub) in enumerate(c['rows']):
        im.paste(fit(src_image(cfg, P, spec, f't{k}'), W - 2 * M, hh, cy=cy), (M, y))
        ov = Image.new('RGBA', (W - 2 * M, 92), (8, 8, 9, 210))
        im.paste(ov, (M, y + hh - 92), ov)
        d = ImageDraw.Draw(im)
        d.text((M + 20, y + hh - 66), lab, font=font('xb', 32), fill=C['ink'], anchor='lm')
        d.text((M + 20, y + hh - 26), sub, font=font('m', 26), fill=C['ink_soft'], anchor='lm')
        y += hh + g
    y += 8
    d.rectangle((M, y, W - M, y + 78), fill=C['brass_tint'], outline=C['brass'], width=2)
    d.text((W // 2, y + 39), c['foot'], font=font('b', 33), fill=C['brass_ink'], anchor='mm')
    d.text((M, y + 98), c['src'], font=font('r', 22), fill=C['faint'], anchor='lt')
    credit_line(d, c['credit'])
    return im


def card_scenes(cfg, P, page, n):
    c = cfg['scenes']
    im, d = new()
    chrome(im, d, page, n, cfg['label'], credit=c['credit'])
    y = head(d, None, c['title']) + 30
    g = 16
    cw, ch = (W - 2 * M - g) // 2, 450
    for i, (spec, lab, cx) in enumerate(c['items']):
        x0, y0 = M + (i % 2) * (cw + g), y + (i // 2) * (ch + g)
        im.paste(fit(src_image(cfg, P, spec, f's{i}'), cw, ch, cx=cx), (x0, y0))
        d = ImageDraw.Draw(im)
        chip(d, (x0, y0 + ch - 52), f'{i + 1}  {lab}', font('b', 26))
    return im


def card_end(cfg, P, page, n):
    c = cfg['end']
    im, d = new()
    chrome(im, d, page, n, cfg['label'], credit=c.get('credit', '사진: Pexels'))
    y = head(d, '다음 행동 하나', '이 도시 이야기,\n본편에서 이어져요')
    im.paste(fit(src_image(cfg, P, c['photo'], 'end'), W - 2 * M, 420), (M, y + 24))
    d = ImageDraw.Draw(im)
    cx, cy = W // 2, y + 24 + 210
    d.ellipse((cx - 56, cy - 56, cx + 56, cy + 56), fill=C['paper'], outline=C['ink'], width=3)
    d.polygon([(cx - 18, cy - 28), (cx - 18, cy + 28), (cx + 30, cy)], fill=C['ink'])
    y += 24 + 420 + 34
    y = text(d, (M, y), c['yt'], font('b', 34), C['ink'], maxw=W - 2 * M, lh=1.4)
    y = text(d, (M, y + 6), c['where'], font('m', 30), C['ink_soft'], maxw=W - 2 * M)
    y += 22
    d.rectangle((M, y, W - M, y + 92), fill=C['ink'])
    d.text((W // 2, y + 46), '▶  ' + c['cta'], font=font('xb', 38), fill=C['paper'], anchor='mm')
    y += 92 + 26
    y = text(d, (M, y), c['src'], font('r', 22), C['faint'], maxw=W - 2 * M, lh=1.4)
    d.text((M, y + 4), '도시 정보를 정리한 콘텐츠예요. 투자 권유가 아니에요.', font=font('r', 22), fill=C['faint'], anchor='lt')
    return im


def build(key):
    cfg = CITIES[key]
    P = f'/home/claude/work/cardnews/{key}'
    os.makedirs(P, exist_ok=True)
    for f in os.listdir(P):
        if f.endswith('.png'):
            os.remove(os.path.join(P, f))
    n = 2 + len(cfg['reasons']) + len(cfg['features']) + 3
    cards = [card_cover(cfg, P, n), card_numbers(cfg, P, 2, n)]
    pg = 3
    for r in cfg['reasons']:
        cards.append(card_reason(cfg, P, r, pg, n)); pg += 1
    for i, f in enumerate(cfg['features']):
        cards.append(card_feature(cfg, P, f, pg, n, f'f{i}')); pg += 1
    cards += [card_three(cfg, P, pg, n), card_scenes(cfg, P, pg + 1, n), card_end(cfg, P, pg + 2, n)]
    for i, im in enumerate(cards, 1):
        im.save(f'{P}/{i:02d}.png', optimize=True)
    cap = '\n'.join(cfg['caption']) + '\n\n' + ' '.join('#' + t for t in cfg['tags']) + (
        f'\n\n[올릴 때 메모]\n- 네이버 클립: 이미지 게시물로 01~{n:02d} 순서대로, \'정보 스티커 → 블로그\'로 이 도시 네이버 글을 붙여 주세요.\n'
        '- 유튜브: 이미지 게시물(여러 장)로 같은 순서, 본문 첫 줄에 본편 영상 링크.\n'
        '- 첫 묶음이라 올린 뒤 잘림이 있는지 알려 주세요(문제 있으면 9:16판을 함께 만들어요).\n'
        '- 게시물 본문 끝에 아래 [사진 출처]를 그대로 붙여 주세요(CC 라이선스 표기).\n\n[사진 출처]\n' + '\n'.join(cfg['photo_credits']) + '\n')
    open(f'{P}/카드뉴스-캡션.txt', 'w', encoding='utf-8').write(cap)
    return P


if __name__ == '__main__':
    print(build(sys.argv[1] if len(sys.argv) > 1 else 'brasilia'))
