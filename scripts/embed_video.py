#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""사이트 글에 '영상으로 보기'(유튜브) 칸을 넣는다 — 2026.11.28 교차링크 기획.

어사이드가 영상을 올린 뒤 드라이브 단지/도시 폴더의 `05_업로드주소.txt`에 주소를 적으면,
다음 예약 회차가 이 스크립트로 사이트 글에 영상을 넣고 push한다. 여러 번 실행해도 결과가 같다
(같은 글에 이미 칸이 있으면 주소만 바꾼다).

사용법:
  python3 scripts/embed_video.py <slug> <유튜브주소> [<유튜브주소2> ...]
  예) python3 scripts/embed_video.py trivn-gaheung https://youtube.com/shorts/AbC123 https://youtu.be/XyZ789
쇼츠(세로)는 세로 비율로, 일반 영상은 16:9로 넣는다. 글의 '관련 포스팅' 바로 위(없으면 푸터 위)에 들어간다.
"""
import os, re, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
START, END = '<!-- video-embed:start -->', '<!-- video-embed:end -->'


def vid(url):
    m = re.search(r'(?:youtu\.be/|v=|/shorts/|/embed/|/live/)([A-Za-z0-9_-]{11})', url)
    if not m:
        raise SystemExit('유튜브 주소를 읽지 못했습니다: ' + url)
    return m.group(1), '/shorts/' in url


def block(urls):
    items = []
    for u in urls:
        v, short = vid(u)
        ratio = '9/16' if short else '16/9'
        width = 'max-width:360px;' if short else ''
        items.append(
            f'<div style="{width}margin:14px auto;aspect-ratio:{ratio};border:1px solid #E3E3E3;border-radius:10px;overflow:hidden;background:#000">'
            f'<iframe src="https://www.youtube-nocookie.com/embed/{v}" title="브동산 영상" loading="lazy" '
            f'style="width:100%;height:100%;border:0;display:block" '
            f'allow="accelerometer; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe></div>')
    return (f'{START}\n<section id="video" style="margin:36px 0 8px">\n<h2>영상으로 보기</h2>\n'
            f'<p style="color:#555;font-size:14.5px;margin:6px 0 0">같은 내용을 짧은 영상으로 정리했습니다. 유튜브 브동산 채널에서도 볼 수 있습니다.</p>\n'
            + '\n'.join(items) + f'\n</section>\n{END}\n')


def main():
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    slug, urls = sys.argv[1], sys.argv[2:]
    p = os.path.join(ROOT, 'posts', slug + '.html')
    t = open(p, encoding='utf-8').read()
    b = block(urls)
    if START in t:
        t = re.sub(re.escape(START) + r'.*?' + re.escape(END) + r'\n?', lambda m: b, t, flags=re.S)
    else:
        for anchor in ('<section id="related">', '<footer'):
            i = t.find(anchor)
            if i >= 0:
                t = t[:i] + b + t[i:]
                break
        else:
            raise SystemExit('넣을 자리(관련 포스팅·푸터)를 찾지 못했습니다: ' + slug)
    open(p, 'w', encoding='utf-8').write(t)
    print('영상 %d개 →' % len(urls), 'posts/%s.html' % slug)


if __name__ == '__main__':
    main()
