# -*- coding: utf-8 -*-
"""도시이야기 가로 본편 렌더러 — A안 '시네마틱 다큐'.
사용: python3 render_long.py <에피소드 폴더> [render|timeline|check k:t ...|audio]
2.39:1 화면(위 띠 0~50, 그림 50~853, 아래 띠 853~1080), 명조 자막 y=900, 청록·주황 색보정 + 필름 질감,
장면마다 5% 천천히 다가가는 줌, 숫자는 금색 세로선 캡션, 0.8초 디졸브, 처음·끝 검은 화면 페이드.
"""
import os, sys, json, subprocess, wave, importlib.util
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
LIB = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, LIB)
import dosi_gfx as gfx, sfx

EPD = sys.argv[1]; MODE = sys.argv[2] if len(sys.argv) > 2 else 'render'
spec = importlib.util.spec_from_file_location('script', os.path.join(EPD, 'script.py')); S = importlib.util.module_from_spec(spec); spec.loader.exec_module(S)
EP = S.EP; SC = S.LONG; GEO = json.load(open(EP['geo'])); P = GEO['places']
W, H, FPS = 1920, 1080, 30; TOP, PIC_B = 50, 854; PW, PH = 1920, PIC_B - TOP; SUB_C = 900; XF = 0.8
OUT = EP['work'] + 'out_LONG/'; os.makedirs(OUT, exist_ok=True)
FP = '/tmp/fonts/'; MONO = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'; NX = '/tmp/nanum/NanumGothic-ExtraBold.ttf'; NR = '/tmp/nanum/NanumGothic-Regular.ttf'
TXT = (240, 234, 220); DIMT = (160, 154, 142); GOLD = (214, 188, 128); CHAP = (196, 184, 156)
_f = {}
def SERIF(s, w=500):
    if ('se', s, w) not in _f:
        f = ImageFont.truetype(FP + 'NotoSerifKR.ttf', s)
        try: f.set_variation_by_axes([w])
        except Exception: pass
        _f[('se', s, w)] = f
    return _f[('se', s, w)]
def F(p, s):
    if (p, s) not in _f: _f[(p, s)] = ImageFont.truetype(p, s)
    return _f[(p, s)]
def probe(p): return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p]))

# ---------------- 타임라인 (실사 없는 장면은 끝 정지 0.5초만)
meta = json.load(open(EP['work'] + 'tts_LONG.json'))
LEAD0, LEAD, GAP, TAIL, ANIM_HOLD, TITLE_PRE, ENDCARD = 0.9, 0.45, 0.42, 0.65, 0.5, 1.4, 4.5
timeline = []; t = 0.0
for i, s in enumerate(SC):
    st = t; c = st + (LEAD0 if i == 0 else LEAD) + (TITLE_PRE if s.get('title') else 0.0); subs = []
    is_anim = all(sh[0] == 'anim' for sh in s['shots'])
    for m in [m for m in meta if m['scene'] == i]:
        subs.append(dict(text=s['lines'][m['line']][0], t0=c - st, t1=c - st + m['dur'] + 0.15, wav=m['wav'], abs=c)); c += m['dur'] + GAP
    Dur = (c - GAP) - st + (0.35 + ANIM_HOLD if is_anim else TAIL) + (ENDCARD if s.get('end') else 0)
    timeline.append(dict(i=i, start=st, dur=Dur, subs=subs, anim=is_anim)); t = st + Dur
TOTAL = t

# ---------------- 오버레이 그림
def coord_txt(loc):
    if loc is None: loc = EP['center']
    lon, lat = (P[loc]['lon'], P[loc]['lat']) if isinstance(loc, str) else loc
    def dm(v, pos, neg): d = int(abs(v)); m = int(round((abs(v) - d) * 60)); return f"{d}°{m:02d}′{pos if v >= 0 else neg}"
    return f"{dm(lat, 'N', 'S')}  {dm(lon, 'E', 'W')}"

def wrap(text, f, maxw, d):
    if d.textlength(text, font=f) <= maxw: return [text]
    words = text.split(' '); best = None
    for k in range(1, len(words)):
        a, b = ' '.join(words[:k]), ' '.join(words[k:]); wa, wb = d.textlength(a, font=f), d.textlength(b, font=f)
        if max(wa, wb) > maxw: continue
        sc = max(wa, wb) - (220 if a[-1] in '.,?!' else 0)
        if best is None or sc < best[0]: best = (sc, [a, b])
    return best[1] if best else [text]

def wordmark(d, x, y, size, anchor='r'):
    fb, fr = F(NX, size), F(NR, size); wb = d.textlength('브', font=fb); wr = d.textlength('동산', font=fr)
    x0 = x - wb - wr - 1 if anchor == 'r' else (x - (wb + wr) / 2 if anchor == 'm' else x)
    d.text((x0, y), '브', font=fb, fill=(220, 214, 200), anchor='lm'); d.text((x0 + wb + 1, y), '동산', font=fr, fill=(150, 146, 136), anchor='lm')

def frame_overlay(s, path):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W, TOP), fill=(0, 0, 0, 255)); d.rectangle((0, PIC_B, W, H), fill=(0, 0, 0, 255))
    d.text((60, TOP / 2), s.get('chap', ''), font=SERIF(22, 500), fill=CHAP, anchor='lm')
    if not all(sh[0] == 'anim' for sh in s['shots']) or s.get('loc'):
        d.text((W - 60, TOP / 2), coord_txt(s.get('loc')), font=F(MONO, 18), fill=(130, 126, 118), anchor='rm')
    wordmark(d, W - 60, H - 40, 22)
    note = '  ·  '.join(x for x in (s.get('attrib'), s.get('note')) if x)
    if note:
        f = F(FP + 'Pretendard-Regular.otf', 19); w = d.textlength(note, font=f)
        d.rectangle((40, PIC_B - 40, 40 + w + 24, PIC_B - 10), fill=(0, 0, 0, 150)); d.text((52, PIC_B - 25), note, font=f, fill=(200, 196, 186), anchor='lm')
    im.save(path)

def sub_img(text, path):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im); f = SERIF(40, 500)
    lines = wrap(text, f, 1560, d); lh = 54
    for k, ln in enumerate(lines): d.text((W / 2, SUB_C - lh * (len(lines) - 1) / 2 + k * lh), ln, font=f, fill=TXT, anchor='mm')
    im.save(path)

def caption_img(t1, t2, path):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im); x, y = 1240, 120
    f1, f2 = SERIF(76, 600), SERIF(30, 500); w = max(d.textlength(t1, font=f1), d.textlength(t2, font=f2))
    pl = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(pl).rectangle((x - 30, y - 10, x + w + 50, y + 170), fill=(0, 0, 0, 110)); im.alpha_composite(pl.filter(ImageFilter.GaussianBlur(14)))
    d.line((x, y + 10, x, y + 150), fill=GOLD + (255,), width=3)
    d.text((x + 28, y + 50), t1, font=f1, fill=GOLD, anchor='lm'); d.text((x + 30, y + 118), t2, font=f2, fill=TXT, anchor='lm')
    im.save(path)

def title_img(path):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); band = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(band).rectangle((0, 300, W, 620), fill=(6, 6, 7, 150)); im.alpha_composite(band); d = ImageDraw.Draw(im)
    d.text((W / 2, 352), f"도시이야기 {EP['no']}  ·  {EP['city']}", font=SERIF(30, 500), fill=(196, 184, 156), anchor='mm')
    d.text((W / 2, 450), EP['title'], font=SERIF(86, 700), fill=TXT, anchor='mm')
    d.text((W / 2, 556), EP['subtitle'], font=SERIF(42, 500), fill=GOLD, anchor='mm')
    im.save(path)

def chapter_img(text, path):
    num, name = text.split('  ', 1)
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); band = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(band).rectangle((0, 360, W, 540), fill=(6, 6, 7, 120)); im.alpha_composite(band); d = ImageDraw.Draw(im)
    d.text((W / 2, 405), num, font=SERIF(34, 600), fill=GOLD, anchor='mm'); d.text((W / 2, 478), name, font=SERIF(58, 600), fill=TXT, anchor='mm')
    im.save(path)

CREDITS = ['영상  Pexels', EP.get('credits_map', '지도  © OpenStreetMap contributors · Natural Earth'), '음악  브동산 자체 제작 · 내레이션 AI 음성(인준)', '숫자 출처는 설명란에 있어요']
def end_img(path):
    im = Image.new('RGBA', (W, H), (8, 8, 9, 225)); d = ImageDraw.Draw(im); cx = W // 2; y = 330
    wordmark(d, cx, y, 92, anchor='m')
    d.text((cx, y + 100), f"도시이야기 · 다음 도시도 이어집니다", font=SERIF(36, 500), fill=(196, 184, 156), anchor='mm')
    d.text((cx, y + 160), 'brandongsan.com', font=F(FP + 'Pretendard-Bold.otf', 34), fill=GOLD, anchor='mm')
    for k, r in enumerate(CREDITS): d.text((cx, y + 250 + k * 46), r, font=F(FP + 'Pretendard-Regular.otf', 26), fill=(190, 188, 180), anchor='mm')
    im.save(path)

# ---------------- 장면
GRADE = 'colorbalance=rs=-0.06:bs=0.07:rh=0.08:gh=0.02:bh=-0.07,eq=contrast=1.10:saturation=0.95,noise=alls=7:allf=t'
def render_anim(k, name, opts, L):
    out = f'{OUT}anim_{k:02d}.mp4'; tmp = out[:-4] + '.tmp.mp4'
    cues = [sb['t0'] for sb in timeline[k]['subs']]
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{PW}x{PH}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '16', '-pix_fmt', 'yuv420p', tmp], stdin=subprocess.PIPE)
    for fr in gfx.frames(name, PW, PH, L, cues, opts, GEO): p.stdin.write(fr)
    p.stdin.close(); assert p.wait() == 0; os.replace(tmp, out); return out

def render_scene(k):
    s = SC[k]; tl = timeline[k]; last = k == len(SC) - 1
    out = f'{OUT}scene_{k:02d}.mp4'
    if os.environ.get('SKIP_EXISTING') and os.path.exists(out): return out
    L = tl['dur'] + (0 if last else XF); shots = s['shots']; n = len(shots); seg = L / n
    inputs, filt = [], []
    for j, sh in enumerate(shots):
        N = int(round(seg * FPS)) + 2
        if sh[0] == 'clip':
            src = EP['px'] + f'px_{sh[1]}.mp4'; avail = probe(src) - sh[2] - 0.1; f = max(1.0, seg / max(0.5, avail))
            inputs += ['-ss', str(sh[2]), '-i', src]
            filt.append(f"[{j}:v]setpts=(PTS-STARTPTS)*{f:.4f},fps={FPS},scale=2112:884:force_original_aspect_ratio=increase,crop=2112:884,"
                        f"zoompan=z='1+0.05*on/{N}':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2':d=1:s={PW}x{PH}:fps={FPS},{GRADE},trim=duration={seg:.3f},setpts=PTS-STARTPTS,setsar=1[b{j}]")
        else:
            src = render_anim(k, sh[1], sh[2], seg); inputs += ['-i', src]
            filt.append(f'[{j}:v]fps={FPS},noise=alls=4:allf=t,trim=duration={seg:.3f},setpts=PTS-STARTPTS,setsar=1[b{j}]')
    filt.append(''.join(f'[b{j}]' for j in range(n)) + f'concat=n={n}:v=1:a=0,pad={W}:{H}:0:{TOP}:color=black[c0]')
    cur, idx = 'c0', n
    def add_img(path, extra=''):
        nonlocal cur, idx
        inputs.extend(['-loop', '1', '-framerate', str(FPS), '-i', path])
        filt.append(f"[{idx}:v]format=rgba{extra}[i{idx}];[{cur}][i{idx}]overlay=0:0:shortest=1[o{idx}]"); cur = f'o{idx}'; idx += 1
    p0 = f'{OUT}frame_{k}.png'; frame_overlay(s, p0); add_img(p0)
    if s.get('title'): p = f'{OUT}title.png'; title_img(p); add_img(p, f",fade=t=in:st=0.3:d=0.9:alpha=1,fade=t=out:st={tl['dur'] - 1.6:.2f}:d=0.9:alpha=1")
    if s.get('chapter') and shots[0][0] == 'clip': p = f'{OUT}chap_{k}.png'; chapter_img(s['chapter'], p); add_img(p, ',fade=t=in:st=0.2:d=0.6:alpha=1,fade=t=out:st=2.6:d=0.6:alpha=1')
    if s.get('caption'):
        cp = s['caption']; p = f'{OUT}cap_{k}.png'; caption_img(cp['t1'], cp['t2'], p); t0 = tl['subs'][cp['line']]['t0'] + 0.5
        add_img(p, f',fade=t=in:st={t0:.2f}:d=0.8:alpha=1')
    for q, sb in enumerate(tl['subs']):
        p = f'{OUT}sub_{k}_{q}.png'; sub_img(sb['text'], p)
        add_img(p, f",fade=t=in:st={sb['t0']:.3f}:d=0.3:alpha=1,fade=t=out:st={sb['t1'] + 0.05:.3f}:d=0.3:alpha=1")
    if s.get('end'): p = f'{OUT}end.png'; end_img(p); add_img(p, f",fade=t=in:st={tl['dur'] - ENDCARD + 0.2:.2f}:d=0.7:alpha=1")
    filt.append(f'[{cur}]trim=duration={L:.3f},format=yuv420p[vout]')
    tmp = out[:-4] + '.tmp.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y'] + inputs + ['-filter_complex', ';'.join(filt), '-map', '[vout]', '-r', str(FPS), '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-t', f'{L:.3f}', tmp], check=True)
    os.replace(tmp, out); return out

# ---------------- 소리: 나레이션 + 자체 합성 패드·드론(나레이션 때 낮춤) + 전환 whoosh(약하게)
SR = 44100
def build_audio(path):
    n = int(SR * (TOTAL + 0.5)); voice = np.zeros(n); fx = np.zeros(n); t = np.arange(n) / SR
    def add(buf, x, at, g=1.0):
        i = int(at * SR); L = min(len(x), n - i)
        if L > 0: buf[i:i + L] += x[:L] * g
    for tl in timeline:
        for sb in tl['subs']:
            with wave.open(sb['wav']) as w: x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
            add(voice, x, sb['abs'])
    wh = sfx.whoosh()
    for tl in timeline[1:]: add(fx, wh, tl['start'] - 0.5, 0.06)
    pad = np.zeros(n); chords = [[110.0, 164.81, 220.0, 261.63, 329.63], [98.0, 146.83, 196.0, 246.94, 293.66], [87.31, 130.81, 174.61, 220.0, 261.63], [98.0, 146.83, 196.0, 246.94, 329.63]]
    for ci in range(int(TOTAL // 8) + 2):
        env = np.clip(1 - np.abs((t - ci * 8 - 4) / 6), 0, 1) ** 1.5
        for f in chords[ci % 4]: pad += env * (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 1.004 * t + 0.7))
    drone = 0.6 * np.sin(2 * np.pi * 55 * t) + 0.3 * np.sin(2 * np.pi * 55.2 * t + 1.1)
    music = 0.6 * pad + 0.4 * drone; music *= np.clip(t / 2.0, 0, 1) * np.clip((TOTAL + 0.5 - t) / 3.0, 0, 1)
    env = np.convolve((np.abs(voice) > 0.02).astype(float), np.ones(int(SR * 0.3)) / int(SR * 0.3), 'same')
    mix = voice / max(1e-6, np.abs(voice).max()) * 0.9 + music / max(1e-6, np.abs(music).max()) * (0.15 - 0.08 * np.clip(env * 3, 0, 1)) + fx
    mix = np.tanh(mix); mix /= max(1e-6, np.abs(mix).max()) / 0.9
    st = np.stack([mix, mix], 1)[:int(SR * TOTAL)]
    with wave.open(path, 'wb') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype(np.int16).tobytes())

def chapters():
    out = []
    for tl, s in zip(timeline, SC):
        if s.get('title') and tl['i'] == 0: out.append((0.0, '오프닝'))
        elif s.get('chapter'):
            st = tl['start']; m = int(st // 60); sec = int(st % 60); out.append((st, s['chapter'].split('  ', 1)[1]))
    return out

if __name__ == '__main__':
    NAME = EP['names']['LONG']
    if MODE == 'timeline':
        for tl in timeline: print(tl['i'], round(tl['start'], 1), round(tl['dur'], 1), 'ANIM' if tl['anim'] else '', [round(s['t0'], 1) for s in tl['subs']])
        print('total', round(TOTAL, 1)); sys.exit()
    if MODE == 'check':
        for a in sys.argv[3:]:
            k, tt = a.split(':'); k = int(k); p = render_scene(k)
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', tt, '-i', p, '-frames:v', '1', '-q:v', '3', f'{OUT}check_{k}_{tt}.jpg'])
        sys.exit()
    if MODE == 'audio':
        build_audio(f'{OUT}audio.wav'); sys.exit()
    from multiprocessing import Pool
    with Pool(2) as pool: files = pool.map(render_scene, range(len(SC)))
    build_audio(f'{OUT}audio.wav')
    ins = sum((['-i', f] for f in files), []); fl = []; cur = '0:v'; off = 0.0
    for k in range(1, len(files)):
        off += timeline[k - 1]['dur']; fl.append(f'[{cur}][{k}:v]xfade=transition=fade:duration={XF}:offset={off:.3f}[x{k}]'); cur = f'x{k}'
    fl.append(f'[{cur}]fade=t=in:st=0:d=0.8,fade=t=out:st={TOTAL - 1.2:.3f}:d=1.2[vf]')
    final = f'{OUT}{NAME}.mp4'; tmp = final[:-4] + '.tmp.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y'] + ins + ['-i', f'{OUT}audio.wav', '-filter_complex', ';'.join(fl), '-map', '[vf]', '-map', f'{len(files)}:a',
                    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '21', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', '-shortest', tmp], check=True)
    os.replace(tmp, final)
    json.dump(dict(timeline=[dict(i=t['i'], start=round(t['start'], 2), dur=round(t['dur'], 2)) for t in timeline], chapters=chapters(), total=TOTAL), open(f'{OUT}timeline.json', 'w'), ensure_ascii=False)
    print('done', final, round(probe(final), 1))
