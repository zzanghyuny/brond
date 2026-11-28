#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""글 목록 카드용 대표사진(썸네일) 만들기 — 2026.11.28 Paul 지시.

posts-data.js의 글마다 대표 이미지를 골라 posts/images/<slug>/thumb.jpg(가로 720px)를 만들고,
그 글 항목에 thumb 필드를 넣는다. feed.js가 이 필드로 카드에 사진을 붙인다.

대표 이미지 고르는 순서:
  0. 청약(realestate) 글은 공식 조감도·투시도(alt에 조감·투시 → 대표 이미지·전경 순, 위치·배치·평면 등 제외)
  1. og:image  2. 커버(.cover) 안의 첫 img
  3. 미분양 랭킹 글은 제목의 1위 단지 조감도(없으면 그 단지 위치도), 그다음 첫 *-aerial.jpg  4. 본문 첫 img(아바타·로고 제외)
세로로 긴 합성 이미지는 위쪽(조감도가 있는 쪽)을 4:3으로 잘라 쓴다. 원본은 건드리지 않는다.

사용법:
  python3 scripts/build_thumbs.py            # 썸네일이 없는 글만 만든다 (새 글 발행 때)
  python3 scripts/build_thumbs.py <slug> ... # 지정한 글만 다시 만든다
  python3 scripts/build_thumbs.py --force    # 전부 다시 만든다
"""
import base64, io, os, re, sys
from PIL import Image

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA = os.path.join(REPO, 'posts-data.js')
W = 720


GOOD = re.compile(r'조감|투시')
OKAY = re.compile(r'조감|투시|대표 이미지|전경')
BAD = re.compile(r'위치|지역|주변|참고|커뮤니티|배치|일대|합성|평면')


def find_aerial(html):
    """청약 글: 사이트 커버는 입지 개략도지만 카드 사진은 공식 조감도·투시도가 보기 좋다."""
    imgs = []
    for a in re.findall(r'<img([^>]+)>', html.split('<body', 1)[-1]):
        s = re.search(r'src=["\']([^"\']+)', a)
        t = re.search(r'alt=["\']([^"\']*)', a)
        if s and 'chart-' not in s.group(1):
            imgs.append((s.group(1), t.group(1) if t else ''))
    for test in (lambda s, t: GOOD.search(t) and not BAD.search(t),
                 lambda s, t: OKAY.search(t) and not BAD.search(t),
                 lambda s, t: GOOD.search(t),
                 lambda s, t: re.search(r'aerial|perspective|cover', s, re.I)):
        for s, t in imgs:
            if test(s, t):
                return s
    return None


def find_top1(html, title):
    """미분양 랭킹 글: 제목의 '1위 ○○' 단지 조감도(없으면 그 단지의 다른 공식 이미지)."""
    m = re.search(r'1위\s*(.+?)\s*예상', title or '')
    if not m:
        return None
    key = m.group(1).replace(' ', '')
    hits = []
    for a in re.findall(r'<img([^>]+)>', html.split('<body', 1)[-1]):
        s = re.search(r'src=["\']([^"\']+)', a)
        t = re.search(r'alt=["\']([^"\']*)', a)
        if s and t and key in t.group(1).replace(' ', '') and 'chart-' not in s.group(1):
            hits.append((s.group(1), t.group(1)))
    for s, t in hits:
        if GOOD.search(t):
            return s
    return hits[0][0] if hits else None


def find_source(html):
    m = re.search(r'property=["\']og:image["\']\s+content=["\']([^"\']+)', html) or \
        re.search(r'content=["\']([^"\']+)["\']\s+property=["\']og:image', html)
    if m:
        return m.group(1)
    m = re.search(r'class=["\'][^"\']*\bcover\b[^"\']*["\'][^>]*>(.*?)</(?:div|figure)>', html, re.S)
    if m:
        i = re.search(r'<img[^>]+src=["\']([^"\']+)', m.group(1))
        if i:
            return i.group(1)
    body = html.split('<body', 1)[-1]
    imgs = [s for s in re.findall(r'<img[^>]+src=["\']([^"\']+)', body)
            if not re.search(r'avatar|logo|icon', s, re.I)]
    aerial = [s for s in imgs if s.endswith('-aerial.jpg')]
    if aerial:
        return aerial[0]
    return imgs[0] if imgs else None


def load(src):
    if src.startswith('data:'):
        return Image.open(io.BytesIO(base64.b64decode(src.split(',', 1)[1])))
    p = re.sub(r'^https?://(www\.)?brandongsan\.com/', '', src)
    p = p if p.startswith('posts/') else os.path.join('posts', p.lstrip('./'))
    p = os.path.join(REPO, p.split('?')[0])
    return Image.open(p) if os.path.exists(p) else None


def make_thumb(im, out):
    if im.mode in ('RGBA', 'LA', 'P'):
        im = im.convert('RGBA')
        bg = Image.new('RGB', im.size, 'white')
        bg.paste(im, mask=im.split()[-1])
        im = bg
    im = im.convert('RGB')
    w, h = im.size
    if h > w * 1.05:  # 세로 이미지 → 4:3으로 자름 (아주 긴 합성 이미지는 위쪽, 아니면 가운데)
        ch = int(w * 0.75)
        top = 0 if h > w * 1.6 else (h - ch) // 2
        im = im.crop((0, top, w, top + ch))
    if im.width > W:
        im = im.resize((W, round(im.height * W / im.width)), Image.LANCZOS)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    im.save(out, 'JPEG', quality=80, optimize=True, progressive=True)


def set_field(js, url, thumb):
    """posts-data.js에서 그 글의 url 바로 뒤에 thumb 필드를 넣거나 고친다(다른 글은 건드리지 않음)."""
    u = re.escape(url)
    have = re.compile(r'((?P<k>"?)url(?P=k)\s*:\s*"' + u + r'"\s*,\s*"?thumb"?\s*:\s*)"[^"]*"')
    if have.search(js):
        return have.sub(lambda m: m.group(1) + '"' + thumb + '"', js, count=1), True
    pat = re.compile(r'(?P<k>"?)url(?P=k)\s*:\s*"' + u + r'"\s*,?')
    m = pat.search(js)
    if not m:
        return js, False
    q = m.group('k')
    s = m.group(0)
    ins = (s if s.rstrip().endswith(',') else s + ',') + ' %sthumb%s: "%s",' % (q, q, thumb)
    return js[:m.start()] + ins + js[m.end():], True


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    force = '--force' in sys.argv
    js = open(DATA, encoding='utf8').read()
    urls = re.findall(r'"?url"?\s*:\s*"(posts/[^"]+\.html)"', js)
    cats, titles = {}, {}
    for blk in re.split(r'\n  \{', js):
        u = re.search(r'"?url"?\s*:\s*"(posts/[^"]+\.html)"', blk)
        c = re.search(r'"?category"?\s*:\s*"([^"]+)"', blk)
        t = re.search(r'"?title"?\s*:\s*"([^"]+)"', blk)
        if u and c:
            cats[u.group(1)] = c.group(1)
        if u and t:
            titles[u.group(1)] = t.group(1)
    made, skipped = [], []
    for url in urls:
        slug = os.path.basename(url)[:-5]
        if args and slug not in args:
            continue
        rel = 'posts/images/%s/thumb.jpg' % slug
        out = os.path.join(REPO, rel)
        if os.path.exists(out) and not force and not args:
            js, _ = set_field(js, url, rel)
            continue
        path = os.path.join(REPO, url)
        if not os.path.exists(path):
            skipped.append((slug, '글 파일 없음')); continue
        html = open(path, encoding='utf8', errors='ignore').read()
        src = (find_top1(html, titles.get(url)) or (find_aerial(html) if cats.get(url) == 'realestate' else None)
               or find_source(html))
        im = load(src) if src else None
        if im is None:
            skipped.append((slug, '대표 이미지 없음: %s' % (src or '-')[:80])); continue
        make_thumb(im, out)
        js, ok = set_field(js, url, rel)
        made.append(slug)
    open(DATA, 'w', encoding='utf8').write(js)
    print('만든 썸네일 %d개' % len(made))
    for s, why in skipped:
        print('  건너뜀', s, '-', why)


if __name__ == '__main__':
    main()
