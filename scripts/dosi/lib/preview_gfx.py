# -*- coding: utf-8 -*-
"""그래픽 장면 미리보기: python3 preview_gfx.py <에피소드> LONG|S1|S2 → work/prev_<which>.jpg (장면 끝 직전 프레임 모음)"""
import sys, os, json, importlib.util
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dosi_gfx as gfx
EPD, WHICH = sys.argv[1], sys.argv[2]
spec = importlib.util.spec_from_file_location('script', os.path.join(EPD, 'script.py')); S = importlib.util.module_from_spec(spec); spec.loader.exec_module(S)
GEO = json.load(open(S.EP['geo'])); gfx.FPS = 2
short = WHICH != 'LONG'; Wd, Hd = (1080, 1920) if short else (1920, 803)
meta = json.load(open(S.EP['work'] + f'tts_{WHICH}.json'))
ims = []
for i, s in enumerate(getattr(S, WHICH)):
    for sh in s['shots']:
        if sh[0] != 'anim': continue
        subs = [m for m in meta if m['scene'] == i]; cues = []; c = 0.45
        for m in subs: cues.append(c); c += m['dur'] + 0.42
        D = c + 0.5; last = None
        for fr in gfx.frames(sh[1], Wd, Hd, D, cues, sh[2], GEO, short): last = fr
        im = Image.frombytes('RGB', (Wd, Hd), last); ims.append(im.resize((Wd // 2, Hd // 2)))
cols = 2 if not short else 4; w, h = ims[0].size; rows = (len(ims) + cols - 1) // cols
sheet = Image.new('RGB', (cols * w, rows * h), 'gray')
for k, im in enumerate(ims): sheet.paste(im, ((k % cols) * w, (k // cols) * h))
sheet.save(S.EP['work'] + f'prev_{WHICH}.jpg', quality=82); print(len(ims), 'frames')
