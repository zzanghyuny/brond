# -*- coding: utf-8 -*-
"""도시이야기 1편 렌더러. 사용: python3 render_ep1.py LONG|S1|S2 [render|check i:t ...]"""
import os, sys, json, subprocess, math, wave, shutil
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
D0 = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D0)
import script_ep1 as script, graphics
sys.path.insert(0, '/home/claude/src/brond/scripts/shorts')
import sfx

WHICH = sys.argv[1]; MODE = sys.argv[2] if len(sys.argv) > 2 else 'render'
VERT = WHICH != 'LONG'
CW, CH = (1080, 1920) if VERT else (1920, 1080)
BW, BH = (1080, 830) if VERT else (1920, 1080)     # 영상(배경) 영역
BY = 470 if VERT else 0
FPS = 30; XF = 0.5
PX = '/home/claude/media/pexels/'
OUT = f'{D0}/out_{WHICH}/'; os.makedirs(OUT, exist_ok=True)
FP = '/tmp/fonts/'; NX = '/tmp/nanum/NanumGothic-ExtraBold.ttf'; NR = '/tmp/nanum/NanumGothic-Regular.ttf'
PSB, PB, PXB, PM, PR = (FP + f for f in ('Pretendard-SemiBold.otf', 'Pretendard-Bold.otf', 'Pretendard-ExtraBold.otf', 'Pretendard-Medium.otf', 'Pretendard-Regular.otf'))
BRASS = (200, 164, 92); WHITE = (255, 255, 255); CREAM = (244, 241, 234); SOFT = (185, 181, 172); FAINT = (150, 148, 142)
_f = {}
def F(p, s):
    if (p, s) not in _f: _f[(p, s)] = ImageFont.truetype(p, s)
    return _f[(p, s)]

SC = getattr(script, WHICH)
meta = json.load(open(f'{D0}/tts_{WHICH}.json'))
LEAD0, LEAD, GAP, TAIL, ENDCARD = 0.8, 0.45, 0.42, 0.7, (2.2 if VERT else 4.5)
SUB_BOTTOM = 1500 if VERT else 932     # 자막 블록 아래끝
SUB_CX = 500 if VERT else CW // 2       # 쇼츠는 오른쪽 버튼을 피해 왼쪽으로

# ---------------- 타임라인
timeline = []; t = 0.0
for i, s in enumerate(SC):
    st = t; c = st + (LEAD0 if i == 0 else LEAD); subs = []
    hold = 1.2 if any(sh[0] == 'anim' for sh in s['shots']) else 0.0
    if s.get('title'): c += 1.0
    for m in [m for m in meta if m['scene'] == i]:
        subs.append(dict(text=s['lines'][m['line']][0], t0=c - st, t1=c - st + m['dur'] + 0.15, wav=m['wav'], abs=c))
        c += m['dur'] + GAP
    Dur = (c - GAP) - st + TAIL + hold + (ENDCARD if s.get('end') else 0)
    timeline.append(dict(i=i, start=st, dur=Dur, subs=subs)); t = st + Dur
TOTAL = t
print(WHICH, 'total', round(TOTAL, 1), 's')

# ---------------- 오버레이
def wrap(text, font, maxw, d):
    words = text.split(' '); lines = ['']
    for w in words:
        cand = (lines[-1] + ' ' + w).strip()
        if d.textlength(cand, font=font) <= maxw: lines[-1] = cand
        else: lines.append(w)
    if len(lines) == 2:   # 두 줄이면 문장부호 뒤에서 끊고, 아니면 고르게
        allw = text.split(' '); best = None
        for k in range(1, len(allw)):
            a, b = ' '.join(allw[:k]), ' '.join(allw[k:]); wa, wb = d.textlength(a, font=font), d.textlength(b, font=font)
            if max(wa, wb) > maxw: continue
            sc = max(wa, wb) - (260 if a[-1] in '.,?!' else 0)
            if best is None or sc < best[0]: best = (sc, [a, b])
        if best: lines = best[1]
    return lines

def shadow_text(im, xy, s, f, fill, blur=8, alpha=220, stroke=2, anchor='mm'):
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
    sd.text((xy[0] + 2, xy[1] + 3), s, font=f, fill=(0, 0, 0, alpha), anchor=anchor, stroke_width=stroke + 2, stroke_fill=(0, 0, 0, alpha))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(blur)))
    ImageDraw.Draw(im).text(xy, s, font=f, fill=fill, anchor=anchor)

def wordmark(d, x, y, size, anchor='l'):
    fb, fr = F(NX, size), F(NR, size); wb = d.textlength('브', font=fb); wr = d.textlength('동산', font=fr)
    x0 = x if anchor == 'l' else x - (wb + wr) / 2
    d.text((x0, y), '브', font=fb, fill=CREAM, anchor='lm'); d.text((x0 + wb + size * 0.04, y), '동산', font=fr, fill=SOFT, anchor='lm')

def sub_overlay(text, path):
    im = Image.new('RGBA', (CW, CH), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    size = 52 if VERT else 56; lh = int(size * 1.4); f = F(PSB, size)
    lines = wrap(text, f, 860 if VERT else 1500, d)
    for k, ln in enumerate(lines):
        y = SUB_BOTTOM - lh * (len(lines) - k - 0.5)
        shadow_text(im, (SUB_CX, y), ln, f, WHITE, blur=8, alpha=220, stroke=2)
    im.save(path)

def static_overlay(s, path, k):
    im = Image.new('RGBA', (CW, CH), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if VERT:
        wordmark(d, CW // 2, 120, 44, anchor='m')
        t1, t2 = script.TITLES[WHICH]
        d.text((CW // 2, 240), t1, font=F(PXB, 78), fill=CREAM, anchor='mm')
        d.text((CW // 2, 340), t2, font=F(PXB, 78), fill=CREAM, anchor='mm')
        d.text((CW // 2, 425), '도시이야기 · 호치민 편', font=F(PM, 32), fill=FAINT, anchor='mm')
        tag = s.get('tag', '')
        if tag:
            f = F(PSB, 28); w = d.textlength(tag, font=f); x, y = 24, BY + 20
            d.rounded_rectangle((x, y, x + w + 52, y + 50), 10, fill=(0, 0, 0, 160))
            d.ellipse((x + 16, y + 18, x + 30, y + 32), fill=BRASS); d.text((x + 40, y + 25), tag, font=f, fill=WHITE, anchor='lm')
        at = s.get('attrib')
        if at:
            f = F(PM, 20); w = d.textlength(at, font=f)
            d.rectangle((CW - 20 - w - 16, BY + BH - 44, CW - 20, BY + BH - 12), fill=(0, 0, 0, 170)); d.text((CW - 28, BY + BH - 28), at, font=f, fill=WHITE, anchor='rm')
    else:
        sh = Image.new('RGBA', (CW, CH), (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
        wordmark(sd, 62, 72, 44); im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(5))); im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(5)))
        wordmark(d, 60, 70, 44)
        tag = s.get('tag', ''); y = 46
        if tag:
            f = F(PSB, 32); w = d.textlength(tag, font=f); pad = 16; x1 = CW - 60; x0 = x1 - (w + 2 * pad + 26)
            d.rounded_rectangle((x0, y, x1, y + 56), 10, fill=(0, 0, 0, 150))
            d.ellipse((x0 + pad, y + 21, x0 + pad + 14, y + 35), fill=BRASS); d.text((x0 + pad + 26, y + 28), tag, font=f, fill=WHITE, anchor='lm')
        at = s.get('attrib')
        if at:
            f = F(PM, 24); w = d.textlength(at, font=f)
            d.rectangle((CW - 60 - w - 18, 112, CW - 60, 146), fill=(0, 0, 0, 160)); d.text((CW - 69, 129), at, font=f, fill=WHITE, anchor='rm')
        note = s.get('note')
        if note:
            f = F(PR, 22); d.text((62, 112), note, font=f, fill=(170, 168, 160, 255), anchor='lt')
    im.save(path)

def chapter_overlay(text, path):
    im = Image.new('RGBA', (CW, CH), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    num, name = text.split('  ', 1)
    f1, f2 = F(PXB, 40), F(PB, 40); w1 = d.textlength(num, font=f1); w2 = d.textlength(name, font=f2)
    x, y = 60, 170; d.rectangle((x, y, x + w1 + w2 + 64, y + 72), fill=(8, 8, 9, 225))
    d.text((x + 22, y + 36), num, font=f1, fill=BRASS, anchor='lm'); d.text((x + 22 + w1 + 20, y + 36), name, font=f2, fill=CREAM, anchor='lm')
    im.save(path)

def title_overlay(path):
    im = Image.new('RGBA', (CW, CH), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    band = Image.new('RGBA', (CW, CH), (0, 0, 0, 0)); bd = ImageDraw.Draw(band); bd.rectangle((0, 300, CW, 640), fill=(8, 8, 9, 170)); im.alpha_composite(band)
    d.text((CW // 2, 360), '도시이야기 1 · 호치민', font=F(PM, 36), fill=SOFT, anchor='mm')
    d.text((CW // 2, 465), '호치민은 왜 이런 모양이 됐을까', font=F(PXB, 92), fill=CREAM, anchor='mm')
    d.text((CW // 2, 570), '강을 따라 자란 도시 300년', font=F(PB, 48), fill=BRASS, anchor='mm')
    im.save(path)

CREDITS = ['영상  Pexels', '위성·3D 화면  Google Earth · Airbus', '지도  © OpenStreetMap contributors · Natural Earth', '음악  브동산 자체 제작 · 내레이션 AI 음성', '숫자 출처는 설명란에 있어요']
def end_overlay(path):
    im = Image.new('RGBA', (CW, CH), (8, 8, 9, 215)); d = ImageDraw.Draw(im); cx = CW // 2
    y = CH // 2 - (330 if VERT else 200)
    wordmark(d, cx, y, 84 if VERT else 96, anchor='m')
    d.text((cx, y + 100), '도시이야기 · 다음 도시도 이어집니다', font=F(PM, 36 if VERT else 38), fill=SOFT, anchor='mm')
    d.text((cx, y + 160), 'brandongsan.com', font=F(PB, 36), fill=BRASS, anchor='mm')
    for k, r in enumerate(CREDITS):
        d.text((cx, y + 260 + k * 50), r, font=F(PR, 26 if VERT else 28), fill=(190, 188, 180), anchor='mm')
    im.save(path)

# ---------------- 정지 이미지
def prep_still(path, idx):
    out = f'{OUT}still_{idx}.png'
    if os.path.exists(out): return out
    im = Image.open(path).convert('RGB')
    if im.height == 778: im = im.crop((0, 40, 1568, 705))
    r = BW / BH
    if im.width / im.height > r: w = int(im.height * r); x = (im.width - w) // 2; im = im.crop((x, 0, x + w, im.height))
    else: h = int(im.width / r); y = (im.height - h) // 2; im = im.crop((0, y, im.width, y + h))
    im = im.resize((BW * 2, BH * 2), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 60, 2))
    im.save(out); return out

def probe(p): return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p]))

def render_anim(k, name, opts, L):
    out = f'{OUT}anim_{k:02d}.mp4'; tmp = out[:-4] + '.tmp.mp4'
    cues = [sb['t0'] for sb in timeline[k]['subs']]
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{BW}x{BH}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '16', '-pix_fmt', 'yuv420p', tmp], stdin=subprocess.PIPE)
    for fr in graphics.frames(name, BW, BH, L, cues, opts): p.stdin.write(fr)
    p.stdin.close(); assert p.wait() == 0; os.replace(tmp, out); return out

def render_scene(k):
    s = SC[k]; tl = timeline[k]; last = k == len(SC) - 1
    if os.environ.get('SKIP_EXISTING') and os.path.exists(f'{OUT}scene_{k:02d}.mp4'): return f'{OUT}scene_{k:02d}.mp4'
    L = tl['dur'] + (0 if last else XF)
    shots = s['shots']; n = len(shots); seg = L / n
    inputs, filt = [], []
    for j, sh in enumerate(shots):
        if sh[0] == 'clip':
            src = PX + f'px_{sh[1]}.mp4'; avail = probe(src) - sh[2] - 0.1
            f = max(1.0, seg / avail)
            inputs += ['-ss', str(sh[2]), '-i', src]
            filt.append(f'[{j}:v]setpts=(PTS-STARTPTS)*{f:.4f},fps={FPS},scale={BW}:{BH}:force_original_aspect_ratio=increase,crop={BW}:{BH},trim=duration={seg:.3f},setpts=PTS-STARTPTS,setsar=1[b{j}]')
        elif sh[0] == 'still':
            img = prep_still(sh[1], f'{k}_{j}'); zf, zt, px, py = sh[2:]
            N = int(round(seg * FPS))
            inputs += ['-loop', '1', '-framerate', str(FPS), '-t', f'{seg:.3f}', '-i', img]
            z = f'({zf}+({zt}-{zf})*on/{N})'
            filt.append(f"[{j}:v]zoompan=z='{z}':x='(iw-iw/zoom)/2*(1+{px}*on/{N})':y='(ih-ih/zoom)/2*(1+{py}*on/{N})':d=1:s={BW}x{BH}:fps={FPS},trim=duration={seg:.3f},setpts=PTS-STARTPTS,setsar=1[b{j}]")
        else:
            src = render_anim(k, sh[1], sh[2], seg)
            inputs += ['-i', src]
            filt.append(f'[{j}:v]fps={FPS},trim=duration={seg:.3f},setpts=PTS-STARTPTS,setsar=1[b{j}]')
    filt.append(''.join(f'[b{j}]' for j in range(n)) + f'concat=n={n}:v=1:a=0[bg]')
    if VERT: filt.append(f'[bg]pad={CW}:{CH}:0:{BY}:color=0x080809[c0]')
    else: filt.append('[bg]null[c0]')
    p0 = f'{OUT}static_{k}.png'; static_overlay(s, p0, k)
    cur = 'c0'; idx = n
    inputs += ['-loop', '1', '-i', p0]
    filt.append(f'[{cur}][{idx}:v]overlay=0:0:shortest=1[o{idx}]'); cur = f'o{idx}'; idx += 1
    if s.get('chapter') and not VERT and shots[0][0] != 'anim':
        p = f'{OUT}chap_{k}.png'; chapter_overlay(s['chapter'], p)
        inputs += ['-loop', '1', '-i', p]
        filt.append(f"[{idx}:v]format=rgba,fade=t=in:st=0.3:d=0.4:alpha=1,fade=t=out:st=3.6:d=0.5:alpha=1[ch];[{cur}][ch]overlay=0:0:shortest=1[o{idx}]"); cur = f'o{idx}'; idx += 1
    if s.get('title') and not VERT:
        p = f'{OUT}title.png'; title_overlay(p)
        inputs += ['-loop', '1', '-i', p]
        filt.append(f"[{idx}:v]format=rgba,fade=t=in:st=0.2:d=0.8:alpha=1,fade=t=out:st={tl['dur'] - 1.4:.2f}:d=0.8:alpha=1[tt];[{cur}][tt]overlay=0:0:shortest=1[o{idx}]"); cur = f'o{idx}'; idx += 1
    for q, sb in enumerate(tl['subs']):
        p = f'{OUT}sub_{k}_{q}.png'; sub_overlay(sb['text'], p)
        inputs += ['-loop', '1', '-i', p]
        filt.append(f"[{cur}][{idx}:v]overlay=0:0:shortest=1:enable='between(t,{sb['t0']:.3f},{sb['t1']:.3f})'[o{idx}]"); cur = f'o{idx}'; idx += 1
    if s.get('end'):
        p = f'{OUT}end.png'; end_overlay(p); e0 = tl['dur'] - ENDCARD + 0.2
        inputs += ['-loop', '1', '-i', p]
        filt.append(f"[{idx}:v]format=rgba,fade=t=in:st={e0:.3f}:d=0.6:alpha=1[ef];[{cur}][ef]overlay=0:0:shortest=1[o{idx}]"); cur = f'o{idx}'; idx += 1
    filt.append(f'[{cur}]trim=duration={L:.3f},format=yuv420p[vout]')
    out = f'{OUT}scene_{k:02d}.mp4'; tmp = out[:-4] + '.tmp.mp4'
    cmd = ['ffmpeg', '-v', 'error', '-y'] + inputs + ['-filter_complex', ';'.join(filt), '-map', '[vout]', '-r', str(FPS), '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-t', f'{L:.3f}', tmp]
    subprocess.run(cmd, check=True); os.replace(tmp, out)
    return out

# ---------------- 소리
SR = 44100
def music(D):
    n = int(SR * D); t = np.arange(n) / SR
    sine = lambda f, ph=0: np.sin(2 * np.pi * f * t + ph)
    drone = 0.5 * sine(55.0) + 0.3 * sine(55.0 * 1.003, 1.1) + 0.22 * sine(82.41)
    pad = np.zeros(n)
    chords = [[110.0, 164.81, 220.0, 261.63, 329.63], [98.0, 146.83, 196.0, 246.94, 293.66], [87.31, 130.81, 174.61, 220.0, 261.63], [98.0, 146.83, 196.0, 246.94, 329.63]]
    seglen = 8.0
    for ci in range(int(D // seglen) + 2):
        ch = chords[ci % 4]; a = ci * seglen
        env = np.clip(1 - np.abs((t - a - seglen / 2) / (seglen * 0.75)), 0, 1) ** 1.5
        for f in ch: pad += env * 0.16 * (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 1.004 * t + 0.7))
    mono = 0.35 * drone + 0.6 * pad
    out = mono.copy()
    for d_ms, g in [(97, 0.4), (151, 0.33), (233, 0.27), (359, 0.2)]:
        dd = int(SR * d_ms / 1000); out[dd:] += g * mono[:-dd]
    env = np.ones(n); env[:int(SR * 2)] = np.linspace(0, 1, int(SR * 2)); env[-int(SR * 3):] = np.linspace(1, 0, int(SR * 3))
    out = np.tanh(out * env); return out / max(1e-6, np.abs(out).max())

def build_audio(path):
    n = int(SR * TOTAL) + SR; voice = np.zeros(n); mus = music(TOTAL + 1)[:n]
    for tl in timeline:
        for sb in tl['subs']:
            with wave.open(sb['wav']) as w: x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
            i = int(sb['abs'] * SR); voice[i:i + len(x)] += x[:max(0, n - i)]
    voice /= max(1e-6, np.abs(voice).max()) / 0.92
    env = np.convolve((np.abs(voice) > 0.02).astype(float), np.ones(int(SR * 0.3)) / int(SR * 0.3), 'same')
    duck = 0.16 - 0.08 * np.clip(env * 3, 0, 1)
    mix = voice + mus * duck
    wh = sfx.whoosh()
    for tl in timeline[1:]:
        i = int(max(0, tl['start'] - 0.35) * SR); L = min(len(wh), n - i); mix[i:i + L] += wh[:L] * 0.08
    mix = np.tanh(mix * 0.98); mix /= max(1e-6, np.abs(mix).max()) / 0.92
    st = np.stack([mix, mix], 1)[:int(SR * TOTAL)]
    with wave.open(path, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype(np.int16).tobytes())

NAMES = {'LONG': 'hcmc-dosi-1-youtube', 'S1': 'hcmc-dosi-1-shorts-size', 'S2': 'hcmc-dosi-1-shorts-axis'}
if __name__ == '__main__':
    if MODE == 'check':   # check k:t ... → 장면 k를 렌더한 뒤 t초 프레임 저장
        for a in sys.argv[3:]:
            k, tt = a.split(':'); k = int(k); p = render_scene(k)
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', tt, '-i', p, '-frames:v', '1', '-q:v', '3', f'{OUT}check_{k}_{tt}.jpg'])
        sys.exit()
    if MODE == 'audio':   # 영상은 그대로, 소리만 다시 입힘
        build_audio(f'{OUT}audio.wav'); final = f'{OUT}{NAMES[WHICH]}.mp4'; tmp = final[:-4] + '.tmp.mp4'
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', final, '-i', f'{OUT}audio.wav', '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', '-shortest', tmp], check=True)
        os.replace(tmp, final); print('re-voiced', final, round(probe(final), 1)); sys.exit()
    if MODE == 'timeline':
        for tl in timeline: print(tl['i'], round(tl['start'], 1), round(tl['dur'], 1), [round(s['t0'], 1) for s in tl['subs']])
        sys.exit()
    from multiprocessing import Pool
    with Pool(2) as pool: files = pool.map(render_scene, range(len(SC)))
    build_audio(f'{OUT}audio.wav')
    # 장면 사이 0.5초 디졸브(최종 한 번에)
    ins = sum((['-i', f] for f in files), []); fl = []; cur = '0:v'; off = 0.0
    for k in range(1, len(files)):
        off += timeline[k - 1]['dur']
        fl.append(f'[{cur}][{k}:v]xfade=transition=fade:duration={XF}:offset={off:.3f}[x{k}]'); cur = f'x{k}'
    final = f'{OUT}{NAMES[WHICH]}.mp4'; tmp = final[:-4] + '.tmp.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y'] + ins + ['-i', f'{OUT}audio.wav', '-filter_complex', ';'.join(fl), '-map', f'[{cur}]', '-map', f'{len(files)}:a',
                    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '21', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', '-shortest', tmp], check=True)
    os.replace(tmp, final)
    json.dump([dict(i=t['i'], start=round(t['start'], 2), dur=round(t['dur'], 2)) for t in timeline], open(f'{OUT}timeline.json', 'w'))
    print('done', final, round(probe(final), 1))
