#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""미분양 선착순 TOP N(수도권·지방 권역, RID 환경변수) — 쇼츠·네이버 클립·릴스용 세로(1080x1920) 영상, 약 80초.

가로 풀영상(make_firstcome_long.py)과 같은 무드·도구를 세로 화면에 맞춰 다시 배치한다.
구성: 오프닝 → 훅 → 한눈에(2곳) → 30~21위 순위판 → 20~11위 순위판 → TOP 10 카드(10~4위 빠르게, TOP3 길게) → 한줄평 3묶음 → 마무리.
플랫폼 버튼을 피하는 안전영역(쇼츠 생성기와 동일): 좌 54 · 우 885 · 위 288 · 아래 1440.

사용: LONG_OUT=/tmp/long-out/ python3 scripts/longform/make_firstcome_shorts.py [정지화면 초...]
출력: <slug>-shorts.mp4, <slug>-shorts-thumbnail.png(1080x1920), <slug>-shorts.txt(제목·설명)
"""
import os, sys, subprocess
os.environ['FC_W'], os.environ['FC_H'] = '1080', '1920'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from multiprocessing import Pool
import make_firstcome_long as L
import fcdata as FC
LABEL, NN = FC.LABEL, FC.N
from make_firstcome_long import (text, tw, wrap, hline, ease, ease_out, kenburns, fitbox, ld, fmt, pct, blank, overlay, finish, push,
                                 grade, BRASS, WHITE, GRAY, BG, D, T, NP, B1, B2, B3, D_DOT, SLUG, IMG, OUT, FPS, GROUPS)
import sfx

W, H = 1080, 1920
SL, SR, ST, SB = 54, 885, 288, 1440
CX = (SL + SR) // 2
DISC = f'브동산 모형 추정치 · 확정 수익 아님 · {D_DOT} 기준'
def disc(img, a=1.0): text(img, (CX, 1395), DISC, 26, GRAY, bold=0, a=a)

def s_open(t, L_):
    img = blank()
    text(img, (CX, 560), '브동산', 46, BRASS, sp=18, a=ease((t - 0.4) / 0.7))
    hline(img, 650, CX - 330, CX + 330, ease_out((t - 0.2) / 1.0))
    text(img, (CX, 690 - 14 * (1 - ease_out((t - 0.8) / 0.9))), f'{LABEL} 미분양', 92 if len(LABEL) <= 4 else 80, WHITE, sp=6, bold=2, a=ease((t - 0.8) / 0.8))
    text(img, (CX, 810 - 14 * (1 - ease_out((t - 1.1) / 0.9))), '선착순', 92, WHITE, sp=10, bold=2, a=ease((t - 1.1) / 0.8))
    text(img, (CX, 940 - 14 * (1 - ease_out((t - 1.5) / 0.9))), f'TOP {NN}', 170, BRASS, sp=12, bold=4, a=ease((t - 1.5) / 0.8))
    hline(img, 1170, CX - 330, CX + 330, ease_out((t - 2.0) / 0.9), w=1)
    text(img, (CX, 1200), FC.HOOK, 50, WHITE, sp=3, bold=1, a=ease((t - 2.4) / 0.8))
    return img

def s_hook(t, L_):
    img = blank()
    for i, (s, c) in enumerate([('청약통장 없이,', WHITE), ('원하는 동·호수를,', WHITE), ('시세 수준에.', BRASS)]):
        k = ease((t - 0.2 - i * 0.7) / 0.7)
        text(img, (CX, 620 + i * 140 + 12 * (1 - k)), s, 80, c, sp=3, bold=2, a=k)
    text(img, (CX, 1100), '그 가격, 적정할까요?', 50, GRAY, sp=2, bold=1, a=ease((t - 2.6) / 0.7))
    return img

def s_glance(t, L_):
    img = blank(); d = ImageDraw.Draw(img)
    text(img, (CX, 330), '분양가보다 적정가격이 높은 단지', 44, WHITE, bold=1, a=ease((t - 0.2) / 0.7))
    n = int(round(NP * ease_out((t - 0.5) / 1.2)))
    text(img, (CX, 400), f'{n}', 330, BRASS, bold=5, a=ease((t - 0.5) / 0.5))
    text(img, (CX, 790), (f'{NN}곳 중 단 {NP}곳' if NP else f'{NN}곳 중 0곳'), 64, WHITE, sp=2, bold=2, a=ease((t - 1.6) / 0.7))
    rows = [('플러스', NP, BRASS), ('0 ~ -5%', B1, (225, 222, 214)), ('-5 ~ -10%', B2, (150, 148, 142)), ('-10% 이하', B3, (95, 93, 90))]
    mx = max(r[1] for r in rows)
    for i, (lab, v, c) in enumerate(rows):
        y = 960 + i * 100; p = ease_out((t - 2.2 - i * 0.3) / 0.9)
        text(img, (SL + 20, y), lab, 38, WHITE, anchor='l', bold=1, a=p)
        w = 420 * v / mx * p
        if p > 0: d.rectangle((SL + 270, y + 8, SL + 270 + w, y + 50), fill=c)
        if p > 0.6: text(img, (SL + 290 + w, y), f'{v}곳', 42, BRASS if c == BRASS else WHITE, anchor='l', bold=2, a=ease((p - 0.6) / 0.4))
    disc(img, ease((t - 1.0) / 1.0))
    return img

def s_board(a, b, title):
    rows = D[a:b]
    def f(t, L_):
        img = blank(); d = ImageDraw.Draw(img)
        text(img, (CX, 300), title, 70, WHITE, sp=6, bold=3, a=ease(t / 0.6))
        hline(img, 400, SL + 20, SR - 20, ease_out((t - 0.2) / 0.8))
        lo_ = min(o['pct'] for o in D)
        for i, o in enumerate(rows):
            p = ease_out((t - 0.4 - i * 0.12) / 0.7)
            if p <= 0: continue
            y = 440 + i * 94
            nm = o['name'] if tw(o['name'], 34) < 520 else o['name'][:14] + '…'
            text(img, (SL + 10, y), f"{o['rank']}", 34, BRASS, anchor='l', bold=2, a=p)
            text(img, (SL + 80, y), nm, 34, WHITE, anchor='l', bold=1, a=p)
            sc = 330 / abs(lo_); v = o['pct'] * p
            c = (225, 222, 214) if o['pct'] > -5 else (150, 148, 142) if o['pct'] > -10 else (95, 93, 90)
            d.rectangle((SL + 80, y + 52, SL + 80 + max(3, abs(v) * sc), y + 70), fill=c)
            text(img, (SL + 100 + abs(v) * sc, y + 42), f"{pct(o)}  {fmt(o['final'])}", 28, WHITE, anchor='l', bold=1, a=p)
        disc(img, ease((t - 0.8) / 0.8))
        return img
    return f

def s_divider(lab, sub):
    def f(t, L_):
        img = blank()
        hline(img, 800, CX - 300, CX + 300, ease_out((t - 0.1) / 0.8))
        text(img, (CX, 830 - 10 * (1 - ease_out((t - 0.2) / 0.7))), lab, 150, BRASS, sp=10, bold=4, a=ease((t - 0.2) / 0.6))
        text(img, (CX, 1030), sub, 42, WHITE, sp=2, bold=1, a=ease((t - 0.6) / 0.6))
        hline(img, 1110, CX - 300, CX + 300, ease_out((t - 0.5) / 0.8), w=1)
        return img
    return f

def s_card(o, top=False):
    k_ = o['key']; ae = os.path.exists(IMG + f'{k_}-aerial.jpg'); lo = os.path.exists(IMG + f'{k_}-location.jpg')
    one = T[k_][1]
    def f(t, L_):
        img = blank(); d = ImageDraw.Draw(img)
        bh, y0 = 560, 300
        if ae or lo:
            if ae and lo and top:
                half = L_ * 0.55; a_img = kenburns(ld(f'{k_}-aerial.jpg'), W, bh, t / L_, 1.0, 1.2, 0.5, 0.55, 0.55, 0.45)
                l_img = fitbox(ld(f'{k_}-location.jpg', 'dark'), W, bh, max(0, t - half) / max(0.1, L_ - half))
                k = ease((t - half) / 0.6); pimg = Image.blend(a_img, l_img, k) if k > 0 else a_img
            elif ae: pimg = kenburns(ld(f'{k_}-aerial.jpg'), W, bh, t / L_, 1.0, 1.2, 0.5, 0.55, 0.55, 0.45)
            else: pimg = fitbox(ld(f'{k_}-location.jpg', 'dark'), W, bh, t / L_)
            img.paste(pimg, (0, y0))
            d.line((0, y0, W, y0), fill=BRASS, width=2); d.line((0, y0 + bh, W, y0 + bh), fill=BRASS, width=2)
            text(img, (SL, y0 + bh + 10), f"{FC.IMGJ.get(k_, {}).get('aerial', FC.IMGJ.get(k_, {}).get('location', {})).get('src', '분양 홍보 페이지')} · CG·홍보물로 실제와 다를 수 있음", 22, GRAY, anchor='l', bold=0, a=ease((t - 0.5) / 0.6))
        else:
            d.rectangle((SL, y0, SR, y0 + bh), outline=(46, 45, 42), width=2)
            text(img, (CX, y0 + 110), f"{o['rank']:02d}", 280, (30, 29, 27), bold=4)
        y = y0 + bh + 70
        text(img, (SL, y), f"No. {o['rank']:02d}", 56, BRASS, sp=5, anchor='l', bold=2, a=ease(t / 0.5))
        names = wrap(o['name'], 56, SR - SL)
        for i, nm in enumerate(names[:2]): text(img, (SL, y + 80 + i * 70), nm, 56, WHITE, anchor='l', bold=2, a=ease((t - 0.2) / 0.6))
        y += 80 + 70 * min(2, len(names)) + 6
        meta = f"{o['region']} · {o['n']:,}세대 · {o['yr']}.{o['mo']:02d} {'준공' if o.get('done') else '입주예정'}"
        mpx = 30
        while tw(meta, mpx) > SR - SL and mpx > 22: mpx -= 1
        text(img, (SL, y), meta, mpx, GRAY, anchor='l', bold=0, a=ease((t - 0.4) / 0.6))
        kk = ease_out((t - 0.6) / 1.0); col = BRASS if o['pct'] > 0 else WHITE
        text(img, (SL, y + 50), f"{o['pct'] * kk:+.1f}%", 120, col, anchor='l', bold=4, a=ease((t - 0.6) / 0.4))
        text(img, (SL + tw(f"{o['pct']:+.1f}%", 120) + 30, y + 112), fmt(o['final']), 44, col, anchor='l', bold=2, a=ease((t - 1.2) / 0.6))
        if top:
            mx = max(o['base'], o['fair']) * 1.06; by = y + 230
            for j, (lab, v, c) in enumerate([('적정가격', o['fair'], (225, 222, 214)), ('분양가', o['base'], BRASS)]):
                p = ease_out((t - 1.6 - j * 0.4) / 0.9)
                if p <= 0: continue
                text(img, (SL, by + j * 64), lab, 30, WHITE, anchor='l', bold=0, a=p)
                d.rectangle((SL + 160, by + j * 64 + 6, SL + 160 + 520 * v / mx * p, by + j * 64 + 36), fill=c)
                text(img, (SL + 175 + 520 * v / mx * p, by + j * 64), f'{v:.2f}억', 30, c, anchor='l', bold=1, a=p)
            y = by + 160
        else:
            y += 200
        for i, l in enumerate(wrap(one, 36, SR - SL)[:3]):
            text(img, (SL, y + i * 52), l, 36, BRASS if i == 0 else (225, 222, 214), anchor='l', bold=1 if i == 0 else 0, a=ease((t - (2.4 if top else 1.4) - i * 0.2) / 0.6))
        return img
    return f

SGROUPS = [(a, b, (n if len(n) <= 5 else n[:4] + [f'외 {len(n) - 4}곳'])) for a, b, n in GROUPS]
def s_groups(t, L_):
    img = blank(); d = ImageDraw.Draw(img)
    text(img, (CX, 300), '브동산 한줄평', 60, BRASS, sp=8, bold=2, a=ease(t / 0.6))
    y = 420
    LH = 50; tot = sum(110 + LH * len(g[2]) + 26 for g in SGROUPS)
    while tot > 1010 and LH > 36: LH -= 2; tot = sum(100 + LH * len(g[2]) + 22 for g in SGROUPS)
    for i, (a, b, names) in enumerate(SGROUPS):
        p = ease((t - 0.4 - i * 0.8) / 0.7); hh = (110 if LH == 50 else 100) + LH * len(names)
        if p > 0:
            first = i == 0
            d.rectangle((SL, y, SR, y + hh), outline=BRASS if first else (70, 68, 64), width=2)
            d.rectangle((SL, y, SL + 10, y + hh), fill=BRASS if first else (90, 88, 84))
            apx = 42
            while tw(a, apx) > SR - SL - 60 and apx > 28: apx -= 1
            text(img, (SL + 40, y + 24), a, apx, BRASS if first else WHITE, anchor='l', bold=2, a=p)
            for j, n in enumerate(names): text(img, (SL + 40, y + 92 + j * LH), '· ' + n, 32 if LH >= 44 else 28, WHITE, anchor='l', bold=0, a=p)
        y += hh + (26 if LH == 50 else 22)
    return img

def s_end(t, L_):
    img = blank()
    text(img, (CX, 640), (FC.META.get('end_lines') or (['웃돈은 작아도,', (FC.META.get('end_lines') or (['웃돈은 작아도,', '고를 수 있는 시장'] if FC.NP else ['웃돈보다,', '살 집을 고르는 시장']))[1]] if FC.NP else ['웃돈보다,', '살 집을 고르는 시장']))[0], 80, WHITE, sp=4, bold=2, a=ease(t / 0.6))
    text(img, (CX, 760), (FC.META.get('end_lines') or (['웃돈은 작아도,', '고를 수 있는 시장'] if FC.NP else ['웃돈보다,', '살 집을 고르는 시장']))[1], 80, BRASS, sp=4, bold=2, a=ease((t - 0.4) / 0.6))
    hline(img, 920, CX - 220, CX + 220, ease_out((t - 0.9) / 0.8))
    text(img, (CX, 960), f'{FC.CYCLE} 다시 계산합니다', 46, WHITE, sp=2, bold=1, a=ease((t - 1.3) / 0.6))
    text(img, (CX, 1040), '더 궁금한 단지는 댓글로 남겨주세요', 40, BRASS, sp=2, bold=1, a=ease((t - 1.7) / 0.6))
    text(img, (CX, 1130), '숫자로 읽는 브동산', 38, GRAY, sp=12, bold=0, a=ease((t - 2.1) / 0.6))
    disc(img, ease(t / 0.6))
    return img

def build():
    sc = [(s_open, 4.6, 'open'), (s_hook, 4.4, 'hook'), (s_glance, 6.8, 'glance')]
    starts = list(range(10, NN, 10))[::-1]   # 순위판: 11위 이후를 10위씩(큰 순위부터)
    for a in starts:
        b = min(NN, a + 10); sc.append((s_board(a, b, f'{b}위 ~ {a + 1}위'), 6.0, 'board'))
    tk = min(10, NN)
    sc.append((s_divider(f'TOP {tk}', f'분양가가 시세에 가장 가까운 {tk}곳'), 2.4, 'div'))
    for o in reversed(D[:tk]):
        sc.append((s_card(o, top=o['rank'] <= 3), 6.2 if o['rank'] <= 3 else 3.8, 'top' if o['rank'] <= 3 else 'cx'))
    sc += [(s_groups, 6.4, 'groups'), (s_end, 4.8, 'end')]
    out, cur = [], 0.0
    for fn, ln, kind in sc: out.append((cur, cur + ln, fn, kind, None)); cur += ln
    return out, cur

SC, DUR = build()
XF = 0.45

def frame(fi):
    t = fi / FPS
    idx = next((i for i, s in enumerate(SC) if s[0] <= t < s[1]), len(SC) - 1)
    def r(i):
        s, e, fn, kind, _ = SC[i]; lt = t - s; return push(fn(lt, e - s), lt, e - s, 0.025)
    img = r(idx); e = SC[idx][1]
    if idx + 1 < len(SC) and e - t < XF: img = Image.blend(img, r(idx + 1), ease(1 - (e - t) / XF))
    img = overlay(img, t)
    fade = 1.0
    if t < 0.8: fade = ease(t / 0.8)
    if DUR - t < 1.0: fade = min(fade, ease((DUR - t) / 1.0))
    return finish(img, fi, fade)

def chunk(args):
    a, b, path = args
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
           '-c:v', 'libx264', '-preset', 'medium', '-crf', '21', '-pix_fmt', 'yuv420p', '-an', path]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for fi in range(a, b): p.stdin.write(np.asarray(frame(fi)).tobytes())
    p.stdin.close(); p.wait(); return path

def events():
    ev = [(s - 0.45, 'whoosh', 0.5) for s, *_ in SC[1:]]
    for s, e, fn, kind, _ in SC:
        if kind == 'glance': ev += [(s + 0.6, 'lowhit', 0.7), (s + 0.65, 'ping', 0.42)]
        if kind == 'top': ev += [(s + 0.7, 'lowhit', 0.55), (s + 0.75, 'ping', 0.35)]
        if kind in ('cx',): ev.append((s + 0.6, 'tick', 0.12))
        if kind == 'div': ev.append((s + 0.2, 'lowhit', 0.4))
    ev.append((SC[-1][0] - 1.3, 'shimmer', 0.5))
    return ev

def thumbnail(path):
    top = D[0]
    _c = [IMG + f"{o['key']}-aerial.jpg" for o in D if os.path.exists(IMG + f"{o['key']}-aerial.jpg")]
    src = grade(Image.open(_c[0]).convert('RGB'), 0.55) if _c else Image.new('RGB', (W, H), (40, 40, 40)); bw = int(H * src.width / src.height)
    bg = src.resize((bw, H), Image.BICUBIC).crop(((bw - W) // 2, 0, (bw - W) // 2 + W, H)).filter(ImageFilter.GaussianBlur(2))
    a = np.asarray(bg).astype(np.float32); yy = np.linspace(0, 1, H)[:, None, None]
    a = a * (1 - 0.55 * (0.35 + 0.65 * np.clip(np.abs(yy - 0.5) * 2.2, 0, 1))) * 0.8
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    text(img, (CX, 470), '브동산', 50, BRASS, sp=20, bold=1)
    hline(img, 550, CX - 320, CX + 320, 1.0, BRASS, 3)
    text(img, (CX, 590), f'{LABEL} 미분양 선착순', 74 if len(LABEL) <= 4 else 64, WHITE, sp=3, bold=2)
    text(img, (CX, 690), f'TOP {NN}', 190, WHITE, sp=10, bold=5)
    if NP:
        text(img, (CX, 950), '웃돈 남는 곳', 70, WHITE, sp=4, bold=2)
        text(img, (CX, 1040), f'단 {NP}곳', 200, BRASS, sp=4, bold=5)
    else:
        text(img, (CX, 950), '시세에 가장 가까운 곳', 64, WHITE, sp=3, bold=2)
        text(img, (CX, 1040), pct(top), 180, BRASS, sp=4, bold=5)
    hline(img, 1300, CX - 320, CX + 320, 1.0, BRASS, 3)
    text(img, (CX, 1330), '지금 해볼 만한 단지는?', 54, WHITE, sp=3, bold=1)
    img.save(path); return path

def describe(path):
    ttl = FC.META.get('sh_title') or (f'{LABEL} 미분양 선착순 TOP{NN} | 웃돈 남는 곳 단 {NP}곳, 1위는?' if NP else f'{LABEL} 미분양 선착순 TOP{NN} | 시세에 가장 가까운 곳은?')
    t = ['제목: ' + ttl, '',
         f'설명: {D_DOT} 기준 {FC.AREAS} 미분양 선착순 아파트 {NN}곳의 예상 프리미엄을 브동산 모형으로 계산했습니다. 플러스는 {NP}곳, 1위 {D[0]["name"]} {pct(D[0])}. 단지별 계산은 브동산 홈페이지(brandongsan.com)에서 확인하세요.',
         '', '브동산 모형 추정치이며 확정 수익이 아닙니다. 계약 전 입주자모집공고와 분양 사무실 안내를 확인하세요. 더 궁금한 단지는 댓글로 남겨주세요.',
         '', '해시태그: #미분양 #선착순분양 ' + ' '.join('#' + x + '아파트' for x in FC.AREAS.split('·')) + ' #줍줍 #예상프리미엄 #브동산', '', f'길이: {DUR:.1f}초 · 1080x1920 · 쇼츠·네이버 클립·릴스 공용']
    open(path, 'w', encoding='utf-8').write('\n'.join(t) + '\n'); return path

if __name__ == '__main__':
    st = [float(x) for x in sys.argv[1:]]
    if st:
        for s in st: frame(int(s * FPS)).save(OUT + f'sh_{s}.png'); print(OUT + f'sh_{s}.png')
        sys.exit()
    print('duration', round(DUR, 1))
    nf = int(DUR * FPS); k = os.cpu_count() or 2
    parts = Pool(k).map(chunk, [(nf * i // k, nf * (i + 1) // k, OUT + f'_s{i}.mp4') for i in range(k)])
    open(OUT + '_sl.txt', 'w').write(''.join(f"file '{x}'\n" for x in parts))
    silent = OUT + f'{SLUG}-shorts-silent.mp4'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', OUT + '_sl.txt', '-c', 'copy', silent], check=True)
    rises = [s for s, *_ in SC[1:]]; booms = [(s + 0.7, 0.6) for s, e, fn, kind, _ in SC if kind == 'top'] + [(SC[-1][0], 0.5)]
    L.make_music(OUT + 'smusic.wav', DUR, rises, booms)
    sfx.mix(OUT + 'smusic.wav', OUT + 'saudio.wav', events())
    final = OUT + f'{SLUG}-shorts.mp4'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', silent, '-i', OUT + 'saudio.wav', '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
                    '-c:a', 'aac', '-b:a', '192k', '-t', str(DUR), '-movflags', '+faststart', final], check=True)
    print('video', final); print('thumb', thumbnail(OUT + f'{SLUG}-shorts-thumbnail.png')); print('desc', describe(OUT + f'{SLUG}-shorts.txt'))
