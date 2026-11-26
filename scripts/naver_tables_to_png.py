# -*- coding: utf-8 -*-
"""네이버 발행본 HTML의 모든 <table>을 모바일 폭 PNG 이미지로 바꾼다.

사용법:
  python3 naver_tables_to_png.py <naver.html> <out_dir> <slug>
결과:
  - out_dir/naver-table-01.png ... (표 순서대로)
  - <naver.html> 안의 각 <table>이 이미지 자리 주석 + <img>로 교체됨
    (src = https://www.brandongsan.com/posts/images/<slug>/naver-table-NN.png)
  - 이미지 alt에는 표의 글자를 한 줄로 이어 붙여 숫자가 검색·접근성용으로 남게 한다.
디자인: 흑백 모노톤(Paul 기준), 폭 360 CSS px, 3배 해상도(1080px), Noto Sans CJK KR.
"""
import re, sys, html as H
from pathlib import Path
from playwright.sync_api import sync_playwright

W = 360          # 휴대폰 본문 폭(CSS px)
SCALE = 3        # 출력 해상도 배수 → 1080px

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
html,body{background:#fff}
body{width:%dpx;padding:14px 12px 16px;font-family:'Noto Sans CJK KR','Pretendard','Apple SD Gothic Neo',sans-serif;
     color:#111;-webkit-font-smoothing:antialiased;word-break:keep-all;overflow-wrap:anywhere}
table{width:100%%;border-collapse:collapse;border-top:2px solid #111;border-bottom:1px solid #111}
th,td{padding:10px 8px;font-size:%dpx;line-height:1.5;text-align:left;vertical-align:middle;border-bottom:1px solid #E3E3E3}
tr:last-child td{border-bottom:0}
thead th{background:#F5F5F5;font-weight:700;font-size:%dpx;color:#555;border-bottom:1px solid #111}
td:first-child,th:first-child{font-weight:700}
tbody tr.hl td{background:#F5F5F5}
td b,td strong{font-weight:800}
.lbl td:first-child{width:28%%;color:#555;font-weight:700}
.cards{border-top:2px solid #111;border-bottom:1px solid #111}
.card{padding:13px 4px 12px;border-bottom:1px solid #E3E3E3}
.card:last-child{border-bottom:0}
.card.hl{background:#F5F5F5;padding-left:10px;padding-right:10px}
.ct{font-size:%dpx;font-weight:800;margin-bottom:7px}
.card dl{display:grid;grid-template-columns:30%% 1fr;row-gap:4px;column-gap:8px}
.card dt{font-size:%dpx;color:#8A8A8A}
.card dd{font-size:%dpx;line-height:1.5}
"""


def text_of(fragment):
    t = re.sub(r'<br\s*/?>', ' ', fragment)
    t = re.sub(r'<[^>]+>', '', t)
    return re.sub(r'\s+', ' ', H.unescape(t)).strip()


def alt_of(table_html):
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table_html, flags=re.S)
    out = []
    for r in rows:
        cells = [text_of(c) for c in re.findall(r'<t[hd][^>]*>(.*?)</t[hd]>', r, flags=re.S)]
        out.append(' · '.join(c for c in cells if c))
    return ' / '.join(out).replace('"', "'")


def ncols(table_html):
    first = re.search(r'<tr[^>]*>(.*?)</tr>', table_html, flags=re.S)
    return len(re.findall(r'<t[hd][^>]*>', first.group(1))) if first else 0


def cells_of(row):
    return re.findall(r'<t[hd][^>]*>(.*?)</t[hd]>', row, flags=re.S)


def as_cards(table_html):
    """칸이 많고 글이 긴 표는 휴대폰에서 칸이 좁아지므로 카드형(행마다 블록)으로 그린다."""
    head = re.search(r'<thead[^>]*>.*?<tr[^>]*>(.*?)</tr>', table_html, flags=re.S)
    heads = [text_of(c) for c in cells_of(head.group(1))] if head else []
    body = re.search(r'<tbody[^>]*>(.*?)</tbody>', table_html, flags=re.S)
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', body.group(1) if body else table_html, flags=re.S)
    out = ['<div class="cards">']
    for r in rows:
        cs = cells_of(r)
        if not cs:
            continue
        hl = all(re.search(r'<(b|strong)>', c) for c in cs)
        out.append(f'<div class="card{" hl" if hl else ""}"><div class="ct">{cs[0]}</div><dl>')
        for j, c in enumerate(cs[1:], 1):
            out.append(f'<dt>{heads[j] if j < len(heads) else ""}</dt><dd>{c}</dd>')
        out.append('</dl></div>')
    out.append('</div>')
    return ''.join(out)


def prepare(table_html):
    """표 종류에 맞게 클래스·글자 크기를 정한다."""
    n = ncols(table_html)
    longest = max((len(text_of(c)) for c in re.findall(r'<td[^>]*>(.*?)</td>', table_html, flags=re.S)), default=0)
    if n >= 4 and longest > 14 and '<thead' in table_html:
        return as_cards(table_html), 14
    has_head = '<thead' in table_html
    t = table_html
    # 굵은 행(<b>가 모든 칸에 있는 행)은 회색 강조 배경
    def mark(m):
        row = m.group(0)
        cells = re.findall(r'<td[^>]*>(.*?)</td>', row, flags=re.S)
        if cells and all(re.search(r'<(b|strong)>', c) for c in cells):
            return row.replace('<tr', '<tr class="hl"', 1)
        return row
    t = re.sub(r'<tr[^>]*>.*?</tr>', mark, t, flags=re.S)
    if n == 2 and not has_head:          # 항목 | 내용 표
        t = t.replace('<table', '<table class="lbl"', 1)
    fs = 15 if n <= 2 else (14 if n == 3 else 13)
    return t, fs


def main(src, out_dir, slug):
    src = Path(src); out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    doc = src.read_text(encoding='utf-8')
    tables = list(re.finditer(r'<table[^>]*>.*?</table>', doc, flags=re.S))
    base = f'https://www.brandongsan.com/posts/images/{slug}/'
    made = []
    # 이미 문서에서 쓰는 naver-table-NN 번호와 겹치지 않게 그다음 번호부터 매긴다(재실행 시 기존 표 이미지 덮어쓰기 방지)
    used = [int(n) for n in re.findall(r'naver-table-(\d+)\.png', doc)]
    start = max(used) + 1 if used else 1
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={'width': W, 'height': 200}, device_scale_factor=SCALE)
        for i, m in enumerate(tables, start):
            t, fs = prepare(m.group(0))
            css = CSS % (W, fs, fs - 1, fs + 1, fs - 1, fs)
            pg.set_content(f'<html><head><meta charset="utf-8"><style>{css}</style></head><body>{t}</body></html>')
            pg.wait_for_timeout(150)
            name = f'naver-table-{i:02d}.png'
            pg.locator('body').screenshot(path=str(out / name))
            made.append((m, name))
        b.close()
    # 뒤에서부터 교체(인덱스 보존)
    for m, name in reversed(made):
        alt = alt_of(m.group(0))
        rep = (f'<!-- [이미지 삽입 자리] {name} : 표 이미지(모바일 폭) -->\n'
               f'<img src="{base}{name}" alt="{alt}" style="width:100%;display:block;">')
        doc = doc[:m.start()] + rep + doc[m.end():]
    src.write_text(doc, encoding='utf-8')
    print(f'{len(made)} tables -> {out}')


if __name__ == '__main__':
    main(*sys.argv[1:4])
