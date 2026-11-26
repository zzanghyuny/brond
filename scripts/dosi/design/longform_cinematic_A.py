# -*- coding: utf-8 -*-
"""A안 '시네마틱 다큐' 움직이는 샘플(남자 한국어 음성). 사용: python3 sample_a.py injoon|hyunsu"""
import sys, os, subprocess, wave, math, asyncio, ssl, certifi, numpy as np
certifi.where = lambda: "/root/.ccr/ca-bundle.crt"
import edge_tts, edge_tts.communicate as c
c._SSL_CTX = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt")
sys.path.insert(0, '/home/claude/src/brond/scripts/shorts')
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import sfx
VK = sys.argv[1] if len(sys.argv) > 1 else 'injoon'
VOICES = {'injoon': ('ko-KR-InJoonNeural', '-4%', '-2Hz', '인준'), 'hyunsu': ('ko-KR-HyunsuMultilingualNeural', '-4%', '-1Hz', '현수')}
VOICE, RATE, PITCH, VNAME = VOICES[VK]
W, H, FPS = 1920, 1080, 30
D = '/home/claude/work/ep1/'; OUT = D + 'sampleA/'; os.makedirs(OUT, exist_ok=True)
FP = '/tmp/fonts/'; MONO = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'
def SERIF(s, w=500):
    f = ImageFont.truetype(FP + 'NotoSerifKR.ttf', s)
    try: f.set_variation_by_axes([w])
    except Exception: pass
    return f
TOP, PIC_B = 50, 853          # 위 띠 0~50, 화면 50~853(2.39:1), 아래 띠 853~1080
SUB_C = 900                    # 자막 중심(아래 띠 위쪽: 유튜브 재생 막대 영역 위)
TXT = (240, 234, 220); DIMT = (160, 154, 142); GOLD = (214, 188, 128)

SCENES = [
  dict(clip='33846690', start=1.0, chap='Ⅱ   강이 만든 도시', coord='10°48′N  106°44′E', lines=[
      ('호치민은 강이 만든 도시예요. 사이공강이 크게 휘어 흐르고,', None),
      ('운하가 시가지 사이를 지나가요. 강 서쪽은 옛 시가지, 강 건너는 새 동네예요.', None)]),
  dict(clip='35527318', start=0.0, chap='Ⅱ   강이 만든 도시', coord='10°46′N  106°41′E', lines=[
      ('도시 모양을 크게 바꾼 건 프랑스였어요.', None),
      ('1862년, 프랑스 장교 코팽은 이곳에 50만 명이 살 도시 계획을 그렸어요.', '천팔백육십이년, 프랑스 장교 코팽은 이곳에 오십만 명이 살 도시 계획을 그렸어요.')],
      caption=dict(line=1, t1='1862', t2='코팽의 도시 계획 · 50만 명')),
]
async def tts():
    for i, s in enumerate(SCENES):
        for j, (disp, say) in enumerate(s['lines']):
            mp3 = f'{OUT}{VK}_{i}_{j}.mp3'; wav = mp3[:-4] + '.wav'
            if not os.path.exists(mp3): await edge_tts.Communicate(say or disp, VOICE, rate=RATE, pitch=PITCH).save(mp3)
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', mp3, '-af', 'silenceremove=start_periods=1:start_threshold=-50dB,areverse,silenceremove=start_periods=1:start_threshold=-50dB,areverse', '-ar', '44100', '-ac', '1', wav], check=True)
asyncio.run(tts())
def wav_dur(p): return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p]))
LEAD, GAP, TAIL, XF = 0.8, 0.5, 1.0, 0.8
t = 0.0
for i, s in enumerate(SCENES):
    s['t0'] = t; c0 = LEAD; s['subs'] = []
    for j, (disp, say) in enumerate(s['lines']):
        wav = f'{OUT}{VK}_{i}_{j}.wav'; d = wav_dur(wav); s['subs'].append(dict(wav=wav, text=disp, a=c0, b=c0 + d + 0.15)); c0 += d + GAP
    s['dur'] = c0 - GAP + TAIL; t += s['dur']
TOTAL = t; print(VK, 'total', round(TOTAL, 2))

def wrap(text, f, maxw, d):
    words = text.split(' '); best = None
    if d.textlength(text, font=f) <= maxw: return [text]
    for k in range(1, len(words)):
        a, b = ' '.join(words[:k]), ' '.join(words[k:]); wa, wb = d.textlength(a, font=f), d.textlength(b, font=f)
        if max(wa, wb) > maxw: continue
        sc = max(wa, wb) - (220 if a[-1] in '.,?!' else 0)
        if best is None or sc < best[0]: best = (sc, [a, b])
    return best[1] if best else [text]
def sub_img(text):
    im = Image.new('RGBA', (W, 140), (0, 0, 0, 0)); d = ImageDraw.Draw(im); f = SERIF(40, 500)
    lines = wrap(text, f, 1500, d); lh = 54
    for k, ln in enumerate(lines): d.text((W / 2, 70 - lh * (len(lines) - 1) / 2 + k * lh), ln, font=f, fill=TXT, anchor='mm')
    return im
def frame_overlay(s):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W, TOP), fill=(0, 0, 0, 255)); d.rectangle((0, PIC_B, W, H), fill=(0, 0, 0, 255))
    d.text((60, TOP / 2), s['chap'], font=SERIF(22, 500), fill=(196, 184, 156), anchor='lm')
    d.text((W - 60, TOP / 2), s['coord'], font=ImageFont.truetype(MONO, 18), fill=(130, 126, 118), anchor='rm')
    fb = ImageFont.truetype('/tmp/nanum/NanumGothic-ExtraBold.ttf', 22); fr = ImageFont.truetype('/tmp/nanum/NanumGothic-Regular.ttf', 22)
    d.text((W - 60, H - 40), '동산', font=fr, fill=(150, 146, 136), anchor='rm'); wr = d.textlength('동산', font=fr)
    d.text((W - 60 - wr - 1, H - 40), '브', font=fb, fill=(220, 214, 200), anchor='rm')
    return im
def caption_img(t1, t2):
    im = Image.new('RGBA', (620, 170), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.line((0, 20, 0, 150), fill=GOLD + (255,), width=3)
    d.text((28, 60), t1, font=SERIF(72, 600), fill=GOLD, anchor='lm'); d.text((30, 125), t2, font=SERIF(30, 500), fill=TXT, anchor='lm')
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0)); sh.paste((0, 0, 0, 150), mask=im.getchannel('A').filter(ImageFilter.GaussianBlur(6)))
    out = Image.new('RGBA', im.size, (0, 0, 0, 0)); out.alpha_composite(sh); out.alpha_composite(im); return out
def fade_a(im, a):
    if a >= 0.999: return im
    x = im.copy(); x.putalpha(x.getchannel('A').point(lambda v: int(v * a))); return x

def render_scene(i, s):
    L = s['dur'] + (XF if i < len(SCENES) - 1 else 0); N = int(round(L * FPS))
    src = f'/home/claude/media/pexels/px_{s["clip"]}.mp4'
    vf = (f'fps={FPS},scale=2112:1188:force_original_aspect_ratio=increase,crop=2112:1188,'
          f"zoompan=z='1+0.05*on/{N}':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2':d=1:s={W}x{H}:fps={FPS},"
          'colorbalance=rs=-0.06:bs=0.07:rh=0.08:gh=0.02:bh=-0.07,eq=contrast=1.10:saturation=0.95,noise=alls=7:allf=t')
    dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', str(s['start']), '-i', src, '-t', f'{L + 0.3:.3f}', '-vf', vf, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    out = f'{OUT}{VK}_scene_{i}.mp4'
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    ov = frame_overlay(s); subs = [sub_img(sb['text']) for sb in s['subs']]
    cap = caption_img(s['caption']['t1'], s['caption']['t2']) if 'caption' in s else None
    last = None
    for fi in range(N):
        t = fi / FPS; raw = dec.stdout.read(W * H * 3)
        if len(raw) < W * H * 3: raw = last
        last = raw
        fr = Image.frombytes('RGB', (W, H), raw).convert('RGBA'); fr.alpha_composite(ov)
        if cap is not None:
            t0 = s['subs'][s['caption']['line']]['a'] + 0.6; a = max(0, min(1, (t - t0) / 0.8))
            if a > 0: fr.alpha_composite(fade_a(cap, a), (1180, 150 + int((1 - a) * 12)))
        for sb, im in zip(s['subs'], subs):
            a = min(1, (t - sb['a']) / 0.3, (sb['b'] + 0.25 - t) / 0.3)
            if a > 0: fr.alpha_composite(fade_a(im, a), (0, SUB_C - 70))
        enc.stdin.write(fr.convert('RGB').tobytes())
    enc.stdin.close(); enc.wait(); dec.kill(); return out

files = [render_scene(i, s) for i, s in enumerate(SCENES)]
SR = 44100; n = int(SR * (TOTAL + 0.5)); voice = np.zeros(n); fx = np.zeros(n)
def add(buf, x, at, g=1.0):
    i = int(at * SR); L = min(len(x), n - i)
    if L > 0: buf[i:i + L] += x[:L] * g
for s in SCENES:
    for sb in s['subs']:
        with wave.open(sb['wav']) as w: x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
        add(voice, x, s['t0'] + sb['a'])
add(fx, sfx.whoosh(), SCENES[1]['t0'] - 0.5, 0.06)
t = np.arange(n) / SR; pad = np.zeros(n)
chords = [[110.0, 164.81, 220.0, 261.63, 329.63], [98.0, 146.83, 196.0, 246.94, 293.66], [87.31, 130.81, 174.61, 220.0, 261.63]]
for ci in range(int(TOTAL // 8) + 2):
    env = np.clip(1 - np.abs((t - ci * 8 - 4) / 6), 0, 1) ** 1.5
    for f in chords[ci % 3]: pad += env * (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 1.004 * t + 0.7))
drone = 0.6 * np.sin(2 * np.pi * 55 * t) + 0.3 * np.sin(2 * np.pi * 55.2 * t + 1.1)
music = 0.6 * pad + 0.4 * drone; music *= np.clip(t / 2.0, 0, 1) * np.clip((TOTAL + 0.5 - t) / 2.5, 0, 1)
env = np.convolve((np.abs(voice) > 0.02).astype(float), np.ones(int(SR * 0.3)) / int(SR * 0.3), 'same')
mix = voice / max(1e-6, np.abs(voice).max()) * 0.9 + music / max(1e-6, np.abs(music).max()) * (0.16 - 0.08 * np.clip(env * 3, 0, 1)) + fx
mix = np.tanh(mix); mix /= max(1e-6, np.abs(mix).max()) / 0.9
wav_out = f'{OUT}{VK}_audio.wav'
with wave.open(wav_out, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.stack([mix, mix], 1) * 32767).astype(np.int16).tobytes())
off = SCENES[0]['dur']
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', files[0], '-i', files[1], '-i', wav_out, '-filter_complex',
                f'[0:v][1:v]xfade=transition=fade:duration={XF}:offset={off:.3f},fade=t=in:st=0:d=0.8,fade=t=out:st={TOTAL - 1.0:.3f}:d=1.0[v]',
                '-map', '[v]', '-map', '2:a', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', '-shortest', '-movflags', '+faststart', f'{OUT}design-A-sample-{VK}.mp4'], check=True)
print('done', VNAME)
