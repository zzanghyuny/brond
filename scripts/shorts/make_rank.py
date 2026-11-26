#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""브동산 '가장 ○○한 곳은?' 랭킹 쇼츠 — 전체 화면 위성사진(Mapbox) + 10위→1위 카운트다운 + 남자 나레이션.

  python3 make_rank.py rank/<키>.json tts            # $RANK_TTS/<out>/<장면>.wav
  python3 make_rank.py rank/<키>.json stills [초…]
  python3 make_rank.py rank/<키>.json render         # $RANK_OUT/<out>.mp4 + -thumbnail.png
사진: rank/fetch_sat.py로 받은 $RANK_IMG/<키>/<순위>.jpg, hook.jpg (1080×1920). 데이터: rank/kb_rank.py (KB 통합검색 전수 수집).
장면: hook(지역 위성 + 질문) → 10위…4위(짧게) → 3·2·1위(길게) → 정리 목록 + 질문 → 첫 화면 루프.
"""
import os, sys, json, wave, subprocess, asyncio, ssl
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import audio_orig, sfx
C = json.load(open(sys.argv[1], encoding='utf8')); KEY = os.path.basename(sys.argv[1])[:-5]
TTS = os.path.join(os.environ.get('RANK_TTS', '/tmp/rank-tts/'), C['out']) + '/'
OUT = os.environ.get('RANK_OUT', '/tmp/rank-out/')
IMGD = os.path.join(os.environ.get('RANK_IMG', '/tmp/rank-img/'), KEY) + '/'
FONTS = os.environ.get('QUIZ_FONTS', '/tmp/nanum/')
VOICE = C.get('voice', ['ko-KR-InJoonNeural', '+16%', '-3Hz'])
ITEMS = sorted(C['items'], key=lambda it: -it['rank'])          # 10위 → 1위
SCN = [('s1', C['narr']['s1'])] + [(f"r{it['rank']}", it['narr']) for it in ITEMS] + [('end', C['narr']['end'])]

def wav_len(p):
    with wave.open(p) as w: return w.getnframes() / w.getframerate()
if sys.argv[2] == 'tts':
    import edge_tts, edge_tts.communicate as EC
    ca = '/root/.ccr/ca-bundle.crt'
    if os.path.exists(ca): EC._SSL_CTX = ssl.create_default_context(cafile=ca)
    os.makedirs(TTS, exist_ok=True)
    for sid, txt in SCN:
        asyncio.run(edge_tts.Communicate(txt, VOICE[0], rate=VOICE[1], pitch=VOICE[2]).save(TTS + sid + '.mp3'))
        subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', TTS + sid + '.mp3', '-af',
                        'silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse',
                        '-ar', '44100', '-ac', '1', TTS + sid + '.wav'], check=True)
        print(sid, round(wav_len(TTS + sid + '.wav'), 2), txt)
    sys.exit(0)

W, H, FPS = 1080, 1920, 30
SAFE_L, SAFE_R = 54, 885; CX = (SAFE_L + SAFE_R) // 2
BG = (8, 8, 9); INK = (244, 241, 234); SOFT = (185, 181, 172); FAINT = (150, 148, 142); HAIR = (42, 42, 45); BRASS = (200, 164, 92)
_f = {}
def F(px, w='B'):
    if (px, w) not in _f: _f[(px, w)] = ImageFont.truetype(FONTS + 'NanumGothic-%s.ttf' % {'R': 'Regular', 'B': 'Bold', 'X': 'ExtraBold'}[w], px)
    return _f[(px, w)]
def ease(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def tw(s, px, w='B'): return F(px, w).getlength(s)
def fit(s, px, w, maxw):
    while px > 18 and tw(s, px, w) > maxw: px -= 2
    return px
def text(img, xy, s, px, color=INK, w='B', anchor='c', alpha=1.0, maxw=None, stroke=0):
    if alpha <= 0.01 or not s: return
    if maxw: px = fit(s, px, w, maxw)
    lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    x = xy[0] - tw(s, px, w) / 2 if anchor == 'c' else (xy[0] - tw(s, px, w) if anchor == 'r' else xy[0])
    a = int(255 * min(1, alpha)); d.text((x, xy[1]), s, font=F(px, w), fill=color + (a,), stroke_width=stroke, stroke_fill=BG + (a,))
    img.alpha_composite(lay)
def rect(img, box, fill=None, outline=None, width=2, alpha=1.0, radius=0):
    if alpha <= 0.01: return
    lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay); a = int(255 * min(1, alpha))
    d.rounded_rectangle(box, radius=radius, fill=(fill + (a,)) if fill else None, outline=(outline + (a,)) if outline else None, width=width)
    img.alpha_composite(lay)

_im = {}
def photo(name):
    if name not in _im:
        im = Image.open(IMGD + name).convert('RGB')
        if im.size != (W, H): im = im.resize((W, H), Image.LANCZOS)
        # 위성사진: 살짝 어둡고 차분하게(사진 원색은 유지하되 대비만 정리)
        a = np.asarray(im).astype(np.float32); a = 255 * ((a / 255) ** 1.12) * 0.92
        _im[name] = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
        _im[name + ':logo'] = im.crop((0, H - 60, 250, H))     # Mapbox 워드마크(좌하단) 보존용
    return _im[name]
def kb(src, k, z0=1.0, z1=1.14):
    z = z0 + (z1 - z0) * ease(k); sw, sh = W / z, H / z
    l, t = (W - sw) / 2, (H - sh) / 2 - 40 * ease(k) / z
    return src.crop((l, t, l + sw, t + sh)).resize((W, H), Image.BICUBIC)
def base(name, k, ring=False, t=0.0):
    img = kb(photo(name), k).convert('RGBA')
    if ring:
        lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        cx, cy = W / 2, H / 2 - 40 * ease(k)
        for i in range(2):
            ph = (t * 0.7 + i * 0.5) % 1.0; r = 120 + 90 * ph
            d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=BRASS + (int(200 * (1 - ph)),), width=5)
        img.alpha_composite(lay)
    img.alpha_composite(_im[name + ':logo'].convert('RGBA'), (8, 1078))   # 정보 띠 위로 옮긴 Mapbox 로고
    return img
def chrome(img):
    w = tw('브', 40, 'X') + tw('동산', 40, 'R'); x = CX - w / 2
    rect(img, (x - 22, 192, x + w + 22, 254), fill=BG, alpha=0.82, radius=8)
    text(img, (x, 200), '브', 40, INK, 'X', anchor='l'); text(img, (x + tw('브', 40, 'X'), 200), '동산', 40, SOFT, 'R', anchor='l')
def footer(img):
    for i, s in enumerate(C['src']): text(img, (CX, 1418 + 34 * i), s, 25, FAINT, 'R', maxw=830)

def sc_hook(img_unused, S, t, d, still=False):
    k = 0 if still else t / max(d, 1e-3)
    img = base('hook.jpg', k * 0.6)
    a = (lambda d0: 1.0) if still else (lambda d0: ease((t - d0) / 0.4))
    rect(img, (0, 760, W, 1130), fill=BG, alpha=0.84)
    q1, q2 = C['hook']['q1'], C['hook']['q2']
    text(img, (CX, 800), q1, 74, INK, 'X', alpha=a(0.1), maxw=880)
    text(img, (CX, 900), q2, 112, BRASS, 'X', alpha=a(0.5), maxw=880)
    text(img, (CX, 1050), C['hook']['sub'], 32, SOFT, 'B', alpha=a(1.0), maxw=860)
    rect(img, (0, 1400, W, 1500), fill=BG, alpha=0.84); footer(img)
    return img

def sc_rank(img_unused, S, t, d):
    it = S['it']; top = it['rank'] <= 3
    img = base(f"{it['rank']}.jpg", t / d, ring=C.get('ring', True), t=t)
    rect(img, (0, 1140, W, 1500), fill=BG, alpha=0.88)
    nar0 = S['_lead'] + S['_nar'] * (0.35 if top else 0.15)
    ar = ease(t / 0.25); an = ease((t - nar0) / 0.3)
    lab = it.get('label', f"{it['rank']}위"); lpx = (120 if top else 100) if 'label' not in it else 64
    text(img, (SAFE_L, 1158 + (30 if 'label' in it else 0)), lab, lpx, BRASS, 'X', anchor='l', alpha=ar)
    rx = SAFE_L + tw(lab, lpx, 'X') + 34
    text(img, (rx, 1176), it['name'], 60, INK, 'X', anchor='l', alpha=an, maxw=SAFE_R + 120 - rx)
    text(img, (rx, 1252), it['sub'], 30, SOFT, 'B', anchor='l', alpha=an, maxw=SAFE_R + 120 - rx)
    text(img, (SAFE_L, 1316), it['val'], 64, BRASS if top else INK, 'X', anchor='l', alpha=an, maxw=820)
    footer(img)
    return img

def sc_end(img_unused, S, t, d):
    loop = ease((t - (d - 1.2)) / 0.9); ai = 1 - loop
    img = Image.new('RGBA', (W, H), BG + (255,))
    text(img, (CX, 300), C['end']['title'], 46, INK, 'X', alpha=ease(t / 0.3) * ai, maxw=860)
    rows = sorted(C['items'], key=lambda it: it['rank'])
    for i, it in enumerate(rows):
        y = 390 + i * min(66, 660 // len(rows)); a = ease((t - 0.15 - 0.06 * i) / 0.3) * ai
        c = BRASS if it['rank'] <= 3 else INK
        text(img, (SAFE_L, y), str(it.get('lrank', it['rank'])), 38, c, 'X', anchor='l', alpha=a)
        text(img, (SAFE_L + 70, y + 2), it['name'], 36, c, 'B', anchor='l', alpha=a, maxw=560)
        text(img, (SAFE_R + 110, y + 2), it['short'], 36, c, 'X', anchor='r', alpha=a, maxw=260)
    tq = S['_lead'] + S['_nar'] - 1.6
    text(img, (CX, 1085), C['end']['q'], 80, BRASS, 'X', alpha=ease((t - tq) / 0.3) * ai, maxw=880)
    text(img, (CX, 1190), C['end']['note'], 30, SOFT, 'B', alpha=ease(t / 0.3) * ai, maxw=860)
    footer(img)
    if loop > 0:
        lo = sc_hook(None, None, 0, 1, still=True); chrome(lo)
        img = Image.blend(img, lo, loop)
    return img

SC = []
for sid, _ in SCN:
    S = dict(id=sid, _nar=wav_len(TTS + sid + '.wav'))
    S['_lead'] = 0.25 if sid == 's1' else 0.15
    if sid == 's1': S.update(draw=sc_hook, tail=0.35)
    elif sid == 'end': S.update(draw=sc_end, tail=1.6)
    else:
        it = next(x for x in C['items'] if f"r{x['rank']}" == sid)
        S.update(draw=sc_rank, it=it, tail=0.55 if it['rank'] <= 3 else 0.2)
    S['_dur'] = S['_lead'] + S['_nar'] + S['tail']
    if sid == 'end': S['_dur'] = max(S['_dur'], 5.4)
    elif S.get('it') and S['it']['rank'] > 3: S['_dur'] = max(S['_dur'], 2.7)
    SC.append(S)
T0 = 0
for S in SC: S['_t0'] = T0; T0 += S['_dur']
DUR = T0

def frame(T):
    for i, S in enumerate(SC):
        if T < S['_t0'] + S['_dur'] or i == len(SC) - 1:
            t = T - S['_t0']; img = S['draw'](None, S, t, S['_dur']); chrome(img)
            if i > 0 and t < 0.16: img.alpha_composite(Image.new('RGBA', (W, H), BG + (int(255 * (1 - t / 0.16)),)))
            return np.asarray(img.convert('RGB'))

SR = 44100
def build_audio(path):
    n = int(DUR * SR) + SR; starts = [S['_t0'] for S in SC]
    hits = [S['_t0'] + S['_lead'] + S['_nar'] * 0.35 for S in SC if S.get('it') and S['it']['rank'] <= 3]
    tmp = OUT + '_rank_music.wav'
    audio_orig.make_audio(tmp, DUR + 1, RISE=tuple(starts[1:]), BOOM=tuple((x, 0.6) for x in hits))
    with wave.open(tmp) as w: m = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32).reshape(-1, 2) / 32768
    mus = np.zeros((n, 2)); L = min(n, len(m)); mus[:L] = m[:L]
    nar = np.zeros(n)
    for S in SC:
        with wave.open(TTS + S['id'] + '.wav') as w: x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
        i = int((S['_t0'] + S['_lead']) * SR); nar[i:i + len(x)] += x[:max(0, n - i)]
    nar /= max(1e-6, np.abs(nar).max()); nar *= 0.85
    env = np.convolve(np.abs(nar), np.ones(int(0.25 * SR)) / int(0.25 * SR), 'same')
    out = mus * 0.16 * (1 - 0.55 * np.clip(env / 0.08, 0, 1))[:, None] + nar[:, None]
    lib = {'whoosh': sfx.whoosh(), 'ping': sfx.ping(), 'shimmer': sfx.shimmer(), 'lowhit': sfx.lowhit(), 'tick': sfx.tick()}
    ev = [(s - 0.25, 'whoosh', 0.13) for s in starts[1:]] + [(DUR - 1.7, 'shimmer', 0.22)]
    ev += [(S['_t0'] + 0.05, 'tick', 0.14) for S in SC if S.get('it') and S['it']['rank'] > 3]
    ev += [(x, 'lowhit', 0.28) for x in hits]
    for t0, nm, g in ev:
        i = int(max(0, t0) * SR); x = lib[nm] * g; Lx = min(len(x), n - i)
        if Lx > 0: out[i:i + Lx] += x[:Lx, None]
    out = out[:int(DUR * SR)]; fd = int(0.4 * SR); out[-fd:] *= np.linspace(1, 0, fd)[:, None]
    out = np.tanh(out * 1.05); out /= max(1e-6, np.abs(out).max()) / 0.89
    with wave.open(path, 'wb') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out * 32767).astype(np.int16).tobytes())

def render():
    name = C['out']; os.makedirs(OUT, exist_ok=True); v = OUT + f'_{name}_v.tmp.mp4'
    p = subprocess.Popen(['ffmpeg', '-nostdin', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '21', '-pix_fmt', 'yuv420p', v], stdin=subprocess.PIPE)
    for fi in range(int(round(DUR * FPS))): p.stdin.write(frame(fi / FPS).tobytes())
    p.stdin.close(); assert p.wait() == 0
    build_audio(OUT + f'_{name}.wav'); tmp = OUT + f'_{name}.tmp.mp4'
    subprocess.run(['ffmpeg', '-nostdin', '-y', '-loglevel', 'error', '-i', v, '-i', OUT + f'_{name}.wav', '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
                    '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', tmp], check=True)
    os.replace(tmp, OUT + f'{name}.mp4'); os.remove(v); os.remove(OUT + f'_{name}.wav')
    th = sc_hook(None, None, 0, 1, still=True); chrome(th); th.convert('RGB').save(OUT + f'{name}-thumbnail.png')
    print('done', OUT + f'{name}.mp4', round(DUR, 2))

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    if sys.argv[2] == 'stills':
        print([(S['id'], round(S['_t0'], 2), round(S['_dur'], 2)) for S in SC], round(DUR, 2))
        for s in sys.argv[3:]: Image.fromarray(frame(float(s))).save(OUT + f'still_{KEY}_{float(s):05.2f}.png')
    elif sys.argv[2] == 'render': render()
