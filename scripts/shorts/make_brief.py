#!/usr/bin/env python3
"""청약 단지 '1분 총정리' 쇼츠 (2026.11.28, 트리븐 가흥 첫 편).

구성: 오프닝(단지명 + '청약하실 분은 이것만 보세요' + 체크리스트) → 01 현금 → 02 예상프리미엄(브릿지, 나레이션 길이에 맞춰 짧게)
      → 03 입지(실사·Google Earth·지도) → 04 단지·평면(배치도·커뮤니티·평면, C['prod'])
      → 05 모집공고 속 유의사항(공고문 문구 → 위성 사진 → 배치도 위 단지 안·경계 항목, 개수 제한 없음) → 마무리 요약.
나레이션은 edge-tts InJoon +40%(기존 +16%의 약 1.2배, 2026.11.28 Paul).
모던 고딕(Pretendard), 검정·황동, 필름 그레인·비네팅·빛 번짐 전환, 단지 위치 깜빡임.

  python3 make_brief.py brief/<키>.json tts      # 나레이션
  python3 make_brief.py brief/<키>.json stills 3 12 30 ...
  python3 make_brief.py brief/<키>.json          # 렌더 → $BRIEF_OUT/<out>.mp4 + -thumbnail.png
이미지(지도·Google Earth 캡처·위키미디어 사진)는 C['img'] 폴더, 실사 영상은 $RANK_BROLL(/tmp/broll/)에 둔다(저장소에 넣지 않음).
글꼴: /tmp/fonts/Pretendard-{Medium,SemiBold,Bold,ExtraBold,Black}.otf
"""
import os, sys, json, wave, subprocess, asyncio, ssl, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import audio_orig, sfx, bridge_anim

C = json.load(open(sys.argv[1], encoding='utf8'))
IMG = C['img']
OUT = os.environ.get('BRIEF_OUT', '/tmp/brief-out/')
TTS = os.path.join(os.environ.get('BRIEF_TTS', '/tmp/brief-tts/'), C['out']) + '/'
BROLL = os.environ.get('RANK_BROLL', '/tmp/broll/')
FONTS = os.environ.get('BRIEF_FONTS', '/tmp/fonts/')
VOICE = C.get('voice', ['ko-KR-InJoonNeural', '+16%', '-3Hz'])

W, H, FPS, SR = 1080, 1920, 30, 44100
L, R = 70, 880                    # 오른쪽 플랫폼 버튼을 피한 본문 폭
CX = (L + R) // 2
BG = (8, 8, 9); INK = (246, 244, 238); SOFT = (178, 175, 168); FAINT = (128, 126, 120)
CARD = (18, 18, 20); HAIR = (48, 47, 46); BR = (200, 164, 92); BR_INK = (222, 194, 132)
MINUS = (240, 138, 102)

# ------------------------------------------------------------------ 나레이션
def wav_len(p):
    with wave.open(p) as w: return w.getnframes() / w.getframerate()

def make_tts():
    import edge_tts, edge_tts.communicate as EC
    ca = '/root/.ccr/ca-bundle.crt'
    if os.path.exists(ca): EC._SSL_CTX = ssl.create_default_context(cafile=ca)
    os.makedirs(TTS, exist_ok=True)
    for k, text in C['narration'].items():
        mp3 = TTS + f'{k}.mp3'
        asyncio.run(edge_tts.Communicate(text, VOICE[0], rate=VOICE[1], pitch=VOICE[2], proxy=os.environ.get('HTTPS_PROXY') or None).save(mp3))
        subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', mp3, '-af',
                        'silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse',
                        '-ar', str(SR), '-ac', '1', TTS + f'{k}.wav'], check=True)
        print(k, round(wav_len(TTS + f'{k}.wav'), 2), text)

if len(sys.argv) > 2 and sys.argv[2] == 'tts':
    make_tts(); sys.exit(0)

# ------------------------------------------------------------------ 도구
_f = {}
WN = {'M': 'Medium', 'S': 'SemiBold', 'B': 'Bold', 'X': 'ExtraBold', 'K': 'Black'}
def F(px, w='B'):
    k = (int(px), w)
    if k not in _f: _f[k] = ImageFont.truetype(FONTS + f'Pretendard-{WN[w]}.otf', int(px))
    return _f[k]
def clamp(x): return max(0.0, min(1.0, x))
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def eo(x): x = clamp(x); return 1 - (1 - x) ** 3
def lerp(a, b, t): return a + (b - a) * t

def text(img, xy, s, px, color=INK, w='B', anchor='l', alpha=1.0, maxw=None, track=0):
    if alpha <= 0.01 or not s: return 0
    while maxw and px > 18 and F(px, w).getlength(s) + track * len(s) > maxw: px -= 2
    f = F(px, w); tw = f.getlength(s) + track * max(0, len(s) - 1)
    x, y = xy
    if anchor == 'c': x -= tw / 2
    elif anchor == 'r': x -= tw
    pad = int(px * 0.35)
    m = Image.new('L', (int(tw) + 2 * pad, int(px * 1.45) + pad), 0); d = ImageDraw.Draw(m)
    if track:
        cx = pad
        for ch in s: d.text((cx, 0), ch, font=f, fill=int(255 * alpha)); cx += f.getlength(ch) + track
    else: d.text((pad, 0), s, font=f, fill=int(255 * alpha))
    img.paste(Image.new('RGB', m.size, color), (int(x) - pad, int(y)), m)
    return tw

def rrect(img, box, fill=None, alpha=1.0, radius=0, outline=None, width=2, oalpha=None):
    if alpha <= 0.01: return
    x0, y0, x1, y1 = [int(v) for v in box]
    if x1 <= x0 or y1 <= y0: return
    lay = Image.new('RGBA', (x1 - x0, y1 - y0), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((0, 0, x1 - x0 - 1, y1 - y0 - 1), radius=radius,
                        fill=(fill + (int(255 * alpha),)) if fill else None,
                        outline=(outline + (int(255 * (oalpha if oalpha is not None else alpha)),)) if outline else None, width=width)
    img.paste(lay, (x0, y0), lay)

def ring(img, c, r, color, width, alpha):
    if alpha <= 0.01 or r <= 0: return
    x, y = c; rr = int(r) + width
    lay = Image.new('RGBA', (2 * rr + 2, 2 * rr + 2), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.ellipse((rr - r, rr - r, rr + r, rr + r), outline=color + (int(255 * alpha),), width=width)
    img.paste(lay, (int(x - rr), int(y - rr)), lay)

def dot(img, c, r, color, alpha=1.0, outline=(255, 255, 255), ow=5):
    x, y = c; rr = int(r) + ow
    lay = Image.new('RGBA', (2 * rr + 2, 2 * rr + 2), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.ellipse((rr - r, rr - r, rr + r, rr + r), fill=color + (int(255 * alpha),), outline=outline + (int(255 * alpha),), width=ow)
    img.paste(lay, (int(x - rr), int(y - rr)), lay)

def pulse(img, c, t, a=1.0, scale=1.0):
    """단지 위치 깜빡임 — 퍼지는 황동 고리 3개 + 중심 점."""
    for k in range(3):
        ph = (t * 0.8 + k / 3) % 1.0
        ring(img, c, (28 + 150 * ph) * scale, BR, 5, a * (1 - ph) * 0.9)
    dot(img, c, 22 * scale, BR, a)

def line(img, pts, color, width, alpha):
    if alpha <= 0.01 or len(pts) < 2: return
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.line(pts, fill=color + (int(255 * alpha),), width=width, joint='curve')
    img.paste(lay, (0, 0), lay)

def merc(lon, lat, z):
    ws = 512 * 2 ** z
    return (lon + 180) / 360 * ws, (1 - math.log(math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))) / math.pi) / 2 * ws

def P(pt, view=None):
    """점 좌표: 픽셀 [x, y] 그대로, 또는 {'ll': [lon, lat]} → view(center·zoom, Mapbox 540×960@2x) 위 픽셀."""
    if isinstance(pt, dict):
        v = view or C['views'][pt.get('view', 'open')]
        (cx, cy), (x, y) = merc(*v['center'], v['zoom']), merc(*pt['ll'], v['zoom'])
        return [(x - cx) * 2 + 540, (y - cy) * 2 + 960]
    return pt

_im = {}
def load(name):
    if name not in _im: _im[name] = Image.open(IMG + name).convert('RGB')
    return _im[name]

def ge_crop(im):
    """Google Earth 캡처(1568×778)에서 위쪽 메뉴·아래 상태줄·모서리 버튼을 잘라낸다."""
    if im.size == (1568, 778): return im.crop((60, 52, 1508, 752)), (60, 52)
    return im, (0, 0)

def kb(src, t, z0, z1, cx0, cy0, cx1, cy1, ow, oh):
    """src를 ow×oh 비율로 잘라 확대·이동(켄 번스). 반환: (이미지, 변환 함수 src좌표→출력좌표)."""
    sw, sh = src.size; k = ease(t)
    z = lerp(z0, z1, k); cx = lerp(cx0, cx1, k) * sw; cy = lerp(cy0, cy1, k) * sh
    ar = ow / oh
    bw = min(sw, sh * ar) / z; bh = bw / ar
    x0 = min(max(0, cx - bw / 2), sw - bw); y0 = min(max(0, cy - bh / 2), sh - bh)
    out = src.resize((ow, oh), Image.BILINEAR, box=(x0, y0, x0 + bw, y0 + bh))
    s = ow / bw
    return out, (lambda p: ((p[0] - x0) * s, (p[1] - y0) * s))

# 전역 질감: 필름 그레인·비네팅
rng = np.random.default_rng(7)
GRAIN = [np.repeat(np.repeat(rng.normal(0, 1, (H // 2, W // 2, 1)).astype(np.float32), 2, 0), 2, 1) for _ in range(6)]
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
VIG = (1 - 0.38 * np.clip(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2, 0, 1) ** 1.2)[..., None]
SWEEP = None

def finish(img, fi):
    a = np.asarray(img).astype(np.float32) * VIG + GRAIN[fi % 6] * 2.2
    return np.clip(a, 0, 255).astype(np.uint8)

# ------------------------------------------------------------------ 공통 화면 요소
def darken(im, amount):
    return ImageEnhance.Brightness(ImageEnhance.Color(im).enhance(0.8)).enhance(amount)

def shade_tb(im, top=0.30, bot=0.62, ka=0.88, kb_=0.92):
    a = np.asarray(im).astype(np.float32)
    y = np.linspace(0, 1, im.size[1])[:, None]
    s = np.maximum(np.clip(1 - y / top, 0, 1) ** 1.4 * ka, np.clip((y - bot) / (1 - bot), 0, 1) ** 1.2 * kb_)[..., None]
    return Image.fromarray((a * (1 - s) + np.array(BG) * s).astype(np.uint8))

CHAP = C['chapters']
def progress(img, ci, p, a=1.0):
    """맨 위 진행 막대(네 장). ci: 지금 장(0~3), p: 장 안 진행률."""
    if a <= 0.01: return
    n = len(CHAP); gap = 14; sw = (R - L - gap * (n - 1)) / n; y = 132
    for i, name in enumerate(CHAP):
        x0 = L + i * (sw + gap)
        rrect(img, (x0, y, x0 + sw, y + 8), HAIR, a, 4)
        fill = 1.0 if i < ci else (p if i == ci else 0.0)
        if fill > 0: rrect(img, (x0, y, x0 + sw * fill, y + 8), BR, a, 4)
        text(img, (x0, y + 22), name, 27, BR if i == ci else (SOFT if i < ci else FAINT), 'B' if i == ci else 'M', 'l', a, maxw=sw)
    text(img, (L, 72), '브동산', 30, BR, 'K', 'l', a)
    text(img, (L + 98, 74), '1분 총정리 · ' + C['name'], 28, SOFT, 'M', 'l', a)

def num(k):
    ks = [x for x in ('cash', 'prem', 'loc', 'prod', 'trap') if x in C['narration']]
    return f'{ks.index(k) + 1:02d}'

def chapter(img, t, num, title, y=228):
    a = ease((t - 0.05) / 0.35); k = eo((t - 0.05) / 0.5)
    text(img, (L, y + (1 - k) * 18), num, 40, BR, 'K', 'l', a)
    text(img, (L + 72, y - 10 + (1 - k) * 30), title, 78, INK, 'K', 'l', a, maxw=R - L - 72)
    w = (R - L) * eo((t - 0.25) / 0.7)
    rrect(img, (L, y + 104, L + w, y + 106), BR, a * 0.8)

def footer(img, s=None, a=1.0):
    text(img, (L, 1508), s or C['src'], 22, FAINT, 'M', 'l', a, maxw=R - L)

def sweep(img, t, a=0.28):
    """장 전환 빛 번짐: 황동빛 띠가 대각선으로 지나간다(0~0.7초)."""
    if not 0 <= t <= 0.7: return
    global SWEEP
    if SWEEP is None:
        g = np.exp(-((np.arange(W * 2) - W) / 160.0) ** 2).astype(np.float32)
        SWEEP = g
    k = eo(t / 0.7); off = int(lerp(-W * 1.2, W * 1.2, k))
    arr = np.asarray(img).astype(np.float32)
    band = np.zeros((H, W), np.float32)
    xs = np.arange(W)[None, :] + (np.arange(H)[:, None] * 0.35).astype(np.int32) - off
    band = SWEEP[np.clip(xs + W // 2, 0, 2 * W - 1)]
    glow = band[..., None] * np.array(BR, np.float32)[None, None, :] * a * (1 - abs(2 * k - 1))
    arr = 255 - (255 - arr) * (1 - glow / 255)
    img.paste(Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)))

# ------------------------------------------------------------------ 장면
def bg_blur(name, amount=0.32, radius=22):
    key = f'blur:{name}:{amount}'
    if key not in _im:
        im = load(name); im = ge_crop(im)[0]
        r = max(W / im.size[0], H / im.size[1]); im = im.resize((int(im.size[0] * r) + 1, int(im.size[1] * r) + 1))
        im = im.crop(((im.size[0] - W) // 2, (im.size[1] - H) // 2, (im.size[0] - W) // 2 + W, (im.size[1] - H) // 2 + H))
        _im[key] = darken(im.filter(ImageFilter.GaussianBlur(radius)), amount)
    return _im[key].copy()

OPEN = None
def open_bg(t, k):
    global OPEN
    if OPEN is None: OPEN = shade_tb(darken(load('open.jpg'), 0.66), top=0.30, bot=0.56)
    sx, sy = C.get('site_open') or P({'ll': C['site_ll'], 'view': 'open'})
    out, tf = kb(OPEN, k, 1.0, 1.22, sx / W, sy / H, sx / W, sy / H, W, H)
    return out, tf((sx, sy))

TICKS = C.get('tick_at', [0.30, 0.45, 0.60, 0.74])
def checklist(img, ca, ons):
    n = len(C['checklist']); gap = 96 if n <= 4 else 82; px = 58 if n <= 4 else 52; y0 = 1150 if n <= 4 else 1112
    rrect(img, (95, y0 - 36, 885, y0 + n * gap + 10), (10, 10, 11), 0.86 * ca, 26, BR, 2, 0.6 * ca)
    for i, r in enumerate(C['checklist']):
        y = y0 + i * gap; on = ons[i]; b = px - 8
        rrect(img, (150, y + 8, 150 + b, y + 8 + b), BR if on > 0.5 else None, ca, 10, BR, 4, ca)
        if on > 0: line(img, [(158, y + 8 + b * 0.52), (150 + b * 0.42, y + 8 + b * 0.8), (150 + b * 0.84, y + 8 + b * 0.2)], BG, 7, on * ca)
        text(img, (226, y), r, px, INK if on > 0.5 else SOFT, 'B', 'l', ca, maxw=640)

def sc_open(t, d, nar):
    img, sp = open_bg(t, t / d)
    pulse(img, sp, t, ease((t - 0.3) / 0.6))
    a1 = ease((t - 0.1) / 0.4)
    text(img, (CX, 150), C['region'], 52, BR, 'B', 'c', a1)
    k = eo((t - 0.25) / 0.7)
    text(img, (CX, 225 + (1 - k) * 40), C['name'], 168, INK, 'K', 'c', ease((t - 0.25) / 0.5), maxw=900, track=-2)
    text(img, (CX, 445), '청약하실 분은 이것만 보세요', 64, INK, 'X', 'c', ease((t - 0.9) / 0.4), maxw=880)
    ca = ease((t - 1.6) / 0.4)
    checklist(img, ca, [ease((t - nar * f) / 0.25) for f in TICKS])
    pa = ease((t - nar * 0.86) / 0.3); pk = eo((t - nar * 0.86) / 0.45)
    w = 330 * pk
    rrect(img, (CX - w, 1592 - 30, CX + w, 1680 - 30), BR, pa, 46)
    text(img, (CX, 1574), '청약 전 1분 총정리', 56, BG, 'K', 'c', pa)
    text(img, (24, 1888), '© Mapbox © Maxar', 20, FAINT, 'M', 'l', 1)
    return img

def sc_cash(t, d, nar, lead):
    c = C['cash']; img = bg_blur(c.get('bg', 'aerial-wide.jpg'), 0.26)
    tn = t - lead
    chapter(img, t, num('cash'), '당첨되면 현금 얼마?')
    # 분양가 막대
    ya = 400; ab = ease((t - 0.4) / 0.4)
    text(img, (L, ya), c['price'], 38, INK, 'X', 'l', ab)
    x = L; lab_end = L - 28; tot = sum(p for _, p in c['segs']); gx = eo((t - 0.6) / 1.0)
    for i, (lab, p) in enumerate(c['segs']):
        wseg = (R - L - 8 * (len(c['segs']) - 1)) * p / tot
        col = BR if i == 0 else ((96, 94, 90) if i == 1 else INK)
        rrect(img, (x, ya + 64, x + wseg * gx, ya + 112), col, ab, 8)
        lx = max(x, lab_end + 28); lab_end = lx + text(img, (lx, ya + 124), lab, 28, SOFT, 'S', 'l', ab * ease((t - 1.2) / 0.4))
        x += wseg + 8
    # 카드 3장
    for i, cd in enumerate(c['cards']):
        y = 600 + i * 238; ta = lead + nar * cd['at']; a = ease((tn - nar * cd['at']) / 0.4); k = eo((tn - nar * cd['at']) / 0.6)
        if a <= 0: continue
        yo = (1 - k) * 40
        rrect(img, (L, y + yo, R, y + 208 + yo), CARD, 0.9 * a, 22, HAIR, 2, a)
        rrect(img, (L, y + 26 + yo, L + 6, y + 182 + yo), BR, a, 3)
        text(img, (L + 34, y + 30 + yo), cd['k'], 40, INK, 'X', 'l', a)
        text(img, (L + 34, y + 84 + yo), cd['d'], 30, FAINT, 'M', 'l', a)
        cnt = eo((tn - nar * cd['at'] - 0.2) / 1.0)
        if 'v' in cd:
            v = int(round(cd['v'] * cnt)); s = f"{v:,}{cd['unit']}"
            text(img, (R - 34, y + 22 + yo), s, 80, BR, 'K', 'r', a)
        else:
            if cd.get('strike'):
                sa = a * (1 - 0.55 * ease((tn - nar * cd['at'] - 0.9) / 0.4))
                tw = text(img, (R - 34, y + 40 + yo), cd['strike'], 44, SOFT, 'B', 'r', sa)
                st = ease((tn - nar * cd['at'] - 0.6) / 0.4)
                rrect(img, (R - 34 - tw * st, y + 66 + yo, R - 34, y + 70 + yo), MINUS, a * st)
                text(img, (R - 34, y + 92 + yo), cd['vtxt'], 62, BR, 'K', 'r', a * ease((tn - nar * cd['at'] - 1.0) / 0.4))
            else:
                text(img, (R - 34, y + 22 + yo), cd['vtxt'], 80, BR, 'K', 'r', a * ease((tn - nar * cd['at'] - 0.3) / 0.4))
        text(img, (L + 34, y + 146 + yo), cd['sub'], 29, SOFT, 'M', 'l', a, maxw=R - L - 68)
    na = ease((tn - nar * c['note_at']) / 0.4)
    rrect(img, (L, 1322, R, 1402), None, na, 40, BR, 3, na)
    text(img, (CX, 1340), c['note'], 34, BR_INK, 'B', 'c', na, maxw=R - L - 60)
    footer(img, c['foot'] + ' · ' + C['src'], ease((t - 0.8) / 0.5))
    return img

BRIDGE = None
def _btext(img, xy, s, px, color, anchor='l', alpha=1.0, w='R', maxw=None):
    text(img, (xy[0], xy[1] - px * 0.12), s, px, color, {'R': 'M', 'B': 'B', 'X': 'K'}[w], anchor, alpha, maxw=maxw)
def bridge_T(d=None):
    bridge_anim.GAP.update(adj=1.0, avg=1.25, disc=1.2, price=1.15, prem=1.0)
    T = bridge_anim.phase_times(C['bridge'], 0.45, NAR['prem'] + 0.4)
    T['end'] = T['prem'] + 1.9
    return T
def sc_prem(t, d, nar, lead):
    global BRIDGE
    if BRIDGE is None: BRIDGE = bridge_anim.Bridge(C['bridge'], _btext, L, R, CX)
    img = bg_blur(C.get('prem_bg', 'ge2.jpg'), 0.18, 30)
    chapter(img, t, num('prem'), '예상프리미엄 얼마?')
    BRIDGE.draw(img, t, bridge_T(d))
    footer(img, None, ease((t - 0.8) / 0.5))
    return img

# 입지: 띠(밴드) 화면 — 흐린 배경 + 선명한 와이드 띠
BAND_Y, BAND_H = 440, 640
def band_img(src_img, t, kbp, pins=(), ring_=None, ring_label=None, pin_label=None, rt=0.0):
    src, off = ge_crop(src_img)
    out, tf = kb(src, t, *kbp, W, BAND_H)
    return out, (lambda p: tf((p[0] - off[0], p[1] - off[1])))

def draw_band(img, out, a=1.0):
    if a < 1:
        base = img.crop((0, BAND_Y, W, BAND_Y + BAND_H)); out = Image.blend(base, out, a)
    img.paste(out, (0, BAND_Y))
    rrect(img, (0, BAND_Y - 2, W, BAND_Y), BR, 0.7 * a); rrect(img, (0, BAND_Y + BAND_H, W, BAND_Y + BAND_H + 2), BR, 0.7 * a)

def label_chip(img, xy, s, a, px=34, fg=BG, bg=BR, anchor='l'):
    f = F(px, 'X'); tw = f.getlength(s); x, y = xy
    if anchor == 'r': x -= tw + 36
    elif anchor == 'c': x -= (tw + 36) / 2
    x = min(max(x, 16), W - 16 - (tw + 36))         # 화면 밖으로 나가지 않게
    rrect(img, (x, y, x + tw + 36, y + px * 1.5), bg, a, int(px * 0.75))
    text(img, (x + 18, y + px * 0.18), s, px, fg, 'X', 'l', a)

_vbg = {}

def vframe(name, start, tt, dur=8):
    key = f'{name}@{start}'
    d = f'/tmp/broll-frames/{name}_{start}_land/'
    if key not in _vbg:
        if not os.path.exists(d + 'done'):
            os.makedirs(d, exist_ok=True)
            subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-ss', str(start), '-i', BROLL + name + '.mp4', '-t', str(dur),
                            '-vf', f'fps={FPS},scale=1280:-2', '-q:v', '3', d + '%05d.jpg'], check=True)
            open(d + 'done', 'w').close()
        _vbg[key] = len([f for f in os.listdir(d) if f.endswith('.jpg')])
    n = _vbg[key]; i = min(n, max(1, int(tt * FPS) + 1))
    return Image.open(d + f'{i:05d}.jpg').convert('RGB')

LOC_T = []
def loc_times(d):
    ts = []; s = 0.0
    shots = C['loc']
    fixed = sum(sh.get('dur', 0) for sh in shots if sh['type'] != 'map')
    for sh in shots:
        dur = sh['dur'] if sh['type'] != 'map' else max(4.0, d - fixed)
        ts.append((s, dur)); s += dur
    return ts

def sc_loc(t, d, nar, lead):
    shots = C['loc']; ts = loc_times(d)
    i = max(j for j, (s, _) in enumerate(ts) if t >= s or j == 0); s0, dur = ts[i]; sh = shots[i]; lt = t - s0
    if sh['type'] == 'map':
        img = map_shot(sh, lt, dur)
    else:
        src = vframe(sh['src'], sh['start'], lt) if sh['type'] == 'video' else load(sh['src'])
        img = bg_blur(sh['src'] if sh['type'] != 'video' else sh.get('bg', 'ge1.jpg'), 0.22, 30)
        kbp = sh.get('kb', [1.0, 1.06, 0.5, 0.5, 0.5, 0.5])
        out, tf = band_img(src, lt / dur, kbp)
        # 띠 위 표시
        if sh.get('pin'):
            p = tf(P(sh['pin'])); bimg = out
            pulse(bimg, p, lt, ease((lt - 0.5) / 0.4), 0.8)
            if sh.get('pin_label'): label_chip(bimg, (p[0] + 40, p[1] - 110), sh['pin_label'], ease((lt - 0.8) / 0.4))
        draw_band(img, out, ease(lt / 0.35) if i == 0 else 1.0)
        ca = ease((lt - 0.3) / 0.4)
        text(img, (L, BAND_Y + BAND_H + 40), sh['cap'], 50, INK, 'X', 'l', ca, maxw=R - L)
        text(img, (L, BAND_Y + BAND_H + 112), sh['credit'], 24, FAINT, 'M', 'l', ca)
    chapter(img, t, num('loc'), '어떤 동네인가?')
    return img

MAPS = {}
def map_shot(sh, lt, dur):
    if sh['src'] not in MAPS: MAPS[sh['src']] = shade_tb(darken(load(sh['src']), 0.62), top=0.28, bot=0.70)
    site = P(sh['site'])
    out, tf = kb(MAPS[sh['src']], lt / dur, 1.18, 1.0, site[0] / W + 0.18, site[1] / H, 0.5, 0.5, W, H)
    img = out.copy()
    sp = tf(site)
    pois = [(n, ds, P(pt), sd) for n, ds, pt, sd in sh['pois']]
    for j, (name, dist, pt, side) in enumerate(pois):
        tj = 0.6 + j * 0.9; k = eo((lt - tj) / 0.8); a = ease((lt - tj) / 0.3)
        if a <= 0: continue
        pp = tf(pt); ep = (lerp(sp[0], pp[0], k), lerp(sp[1], pp[1], k))
        line(img, [sp, ep], BR, 5, a * 0.95)
        if k > 0.95: dot(img, pp, 13, INK, a, BR, 4)
    for j, (name, dist, pt, side) in enumerate(pois):
        tj = 0.6 + j * 0.9; pp = tf(pt)
        if eo((lt - tj) / 0.8) > 0.95:
            lx = pp[0] + 26 if side == 'r' else pp[0] - 26
            label_chip(img, (lx, pp[1] - 70), f'{name} {dist}', ease((lt - tj - 0.7) / 0.3), 32, BG, INK, 'l' if side == 'r' else 'r')
    pulse(img, sp, lt, 1.0, 0.9)
    label_chip(img, (sp[0] + 30, sp[1] + 30), '단지', 1.0, 34)
    if sh.get('photo'):
        ph, cred, at = sh['photo']; tp = 1.0
        pa = ease((lt - tp) / 0.4) * (1 - ease((lt - tp - 2.4) / 0.4))
        if pa > 0:
            im = load(ph); r = 420 / im.size[0]; im = im.resize((420, int(im.size[1] * r)))
            x0, y0 = R - 420, 1080
            rrect(img, (x0 - 6, y0 - 6, x0 + 426, y0 + im.size[1] + 6), INK, pa, 14)
            img.paste(Image.blend(img.crop((x0, y0, x0 + 420, y0 + im.size[1])), im, pa), (x0, y0))
            text(img, (x0, y0 + im.size[1] + 14), cred, 20, SOFT, 'M', 'l', pa, maxw=430)
    text(img, (L, 1508), sh['credit'], 22, FAINT, 'M', 'l', 1)
    return img

def shot_slots(lead, nar, d, ats):
    """[(시작, 길이)] — 나레이션 비율 at 기준, 0.2초 먼저 들어온다."""
    st = [max(0.0, lead + nar * a - 0.2) for a in ats]
    return [(s0, (st[i + 1] if i + 1 < len(st) else d) - s0) for i, s0 in enumerate(st)]

def pick(slots, t):
    i = max(j for j, (s0, _) in enumerate(slots) if t >= s0 or j == 0); return i, t - slots[i][0], slots[i][1]

def caption(img, cap, sub, ca, y=None):
    y = BAND_Y + BAND_H + 36 if y is None else y
    lines = wrap(cap, 46, 'X', R - L)
    for j, ln in enumerate(lines): text(img, (L, y + j * 60), ln, 46, INK, 'X', 'l', ca)
    if sub: text(img, (L, y + 4 + len(lines) * 60), sub, 30, SOFT, 'M', 'l', ca, maxw=R - L)
    return y + 4 + len(lines) * 60 + (48 if sub else 0)

# ---------- 상품: 단지 배치 → 커뮤니티 → 평면
def sc_prod(t, d, nar, lead):
    P = C['prod']; shots = P['shots']
    i, lt, dur = pick(shot_slots(lead, nar, d, [sh['at'] for sh in shots]), t)
    sh = shots[i]; tn = t - lead
    img = bg_blur(sh['src'], 0.2, 30)
    out, tf = band_img(load(sh['src']), lt / max(1.0, dur), sh['kb'])
    if sh['type'] == 'site' and sh.get('ring'):
        rc = tf(sh['ring'][:2]); ra = ease((lt - 0.5) / 0.4)
        ring(out, rc, sh['ring'][2] * (0.95 + 0.05 * math.sin(lt * 4)), BR, 6, ra)
        label_chip(out, (max(24, rc[0] - 200), max(16, rc[1] - sh['ring'][2] - 66)), sh['ring_label'], ease((lt - 0.8) / 0.3), 30)
        if sh.get('pin'):
            pp = tf(sh['pin']); pulse(out, pp, lt, ease((lt - 1.4) / 0.4), 0.55)
            label_chip(out, (max(24, pp[0] - 260), pp[1] + 40), sh['pin_label'], ease((lt - 1.7) / 0.3), 30, BG, INK)
    elif sh['type'] == 'plan':
        for j, b in enumerate(sh.get('bays', [])):
            ba = ease((lt - 0.4 - j * 0.22) / 0.25); bp = tf(b)
            dot(out, bp, 26, BR, ba, BG, 4)
            text(out, (bp[0], bp[1] - 21), str(j + 1), 30, BG, 'K', 'c', ba)
        if sh.get('alpha'):
            ap = tf(sh['alpha']); aa = ease((lt - 1.6) / 0.4)
            ring(out, ap, 70 * (0.95 + 0.05 * math.sin(lt * 4)), BR, 6, aa)
            label_chip(out, (ap[0] + 60, ap[1] - 90), sh.get('alpha_label', '알파룸'), ease((lt - 1.8) / 0.3), 32)
    draw_band(img, out, ease(lt / 0.3))
    label_chip(img, (L, BAND_Y - 74), sh['chip'], ease((lt - 0.1) / 0.3), 32)
    ca = ease((lt - 0.4) / 0.4)
    y = caption(img, sh['cap'], sh.get('sub'), ca)
    if sh['type'] == 'comm':
        cx, cy = L, y + 6
        for j, (fl, name) in enumerate(sh['chips']):
            at = lead + nar * sh['chip_at'][j]; a = ease((t - at) / 0.3)
            w = F(32, 'B').getlength(name) + F(24, 'K').getlength(fl) + 66
            if cx + w > R: cx = L; cy += 70
            if a > 0:
                yo = (1 - eo((t - at) / 0.4)) * 16
                rrect(img, (cx, cy + yo, cx + w, cy + 56 + yo), CARD, 0.92 * a, 28, BR if fl == 'B1' else SOFT, 2, a)
                text(img, (cx + 20, cy + 14 + yo), fl, 24, BR if fl == 'B1' else SOFT, 'K', 'l', a)
                text(img, (cx + 34 + F(24, 'K').getlength(fl), cy + 8 + yo), name, 32, INK, 'B', 'l', a)
            cx += w + 14
    elif sh.get('chips'):
        cx, cy = L, y + 6
        for j, name in enumerate(sh['chips']):
            a = ease((lt - 1.0 - j * 0.35) / 0.3); w = F(32, 'B').getlength(name) + 44
            if cx + w > R: cx = L; cy += 70
            rrect(img, (cx, cy, cx + w, cy + 56), CARD, 0.92 * a, 28, BR, 2, a)
            text(img, (cx + 22, cy + 8), name, 32, INK, 'B', 'l', a); cx += w + 14
    text(img, (L, 1508), P['credit'], 22, FAINT, 'M', 'l', 1)
    chapter(img, t, num('prod'), '단지·평면은 어떤가?')
    return img

# ---------- 유의사항: 공고문 문구(가격 조건) → 위성(주변 시설) → 배치도(단지 안·경계)
def sc_trap(t, d, nar, lead):
    T = C['trap']; S = T.get('site'); shots = T.get('shots', [])
    segs = ([('q', None)] if T.get('quotes') else []) + [('s', sh) for sh in shots] + ([('site', S)] if S else [])
    slots = [(0.0 if kd == 'q' else max(0.0, lead + nar * x['at'] - 0.2)) for kd, x in segs]
    slots = [(s0, (slots[j + 1] if j + 1 < len(slots) else d) - s0) for j, s0 in enumerate(slots)]
    i, lt, dur = pick(slots, t); kind, sh = segs[i]
    if kind == 'q':
        img = bg_blur(T.get('bg', 'ge3.jpg'), 0.16, 32)
        for i, q in enumerate(T['quotes']):
            y = 420 + i * 470; t0 = lead + nar * q['at']; a = ease((t - t0) / 0.3); k = eo((t - t0) / 0.45)
            if a <= 0: continue
            yo = (1 - k) * 36
            rrect(img, (L, y + yo, R, y + 420 + yo), CARD, 0.92 * a, 24, HAIR, 2, a)
            label_chip(img, (L + 30, y + 30 + yo), q['chip'], a, 32)
            lines = wrap(q['q'], 40, 'M', R - L - 90)
            hl = eo((t - t0 - 0.3) / 0.8)
            for j, ln in enumerate(lines):
                ly = y + 112 + j * 56 + yo; tw = F(40, 'M').getlength(ln)
                rrect(img, (L + 40, ly + 8, L + 46 + tw * clamp(hl * len(lines) - j), ly + 50), (90, 74, 40), a * 0.9, 6)
                text(img, (L + 44, ly), ln, 40, INK, 'M', 'l', a)
            text(img, (L + 44, y + 112 + len(lines) * 56 + 6 + yo), '— 입주자모집공고', 24, FAINT, 'M', 'l', a)
            ra = ease((t - t0 - 0.9) / 0.35)
            text(img, (L + 44, max(y + 330, y + 112 + len(lines) * 56 + 48) + yo), '→ ' + q['r'], 42, BR_INK, 'X', 'l', ra, maxw=R - L - 90)
        footer(img, None, 1)
    elif kind == 'site':
        img = bg_blur(S['src'], 0.2, 30)
        out, tf = band_img(load(S['src']), lt / max(1.0, dur), S['kb'])
        for it in S['items']:
            at = lead + nar * it['at']; a = ease((t - at) / 0.3)
            if a <= 0 or not it.get('pt'): continue
            c = tf(P(it['pt'])); cur = t < (lead + nar * S['items'][min(len(S['items']) - 1, S['items'].index(it) + 1)]['at']) or it is S['items'][-1]
            ring(out, c, it['r'] * (0.9 + 0.1 * math.sin((t - at) * 5)) if cur else it['r'], MINUS, 6 if cur else 4, a * (1.0 if cur else 0.55))
            dot(out, (c[0] + it['r'] * 0.72, c[1] - it['r'] * 0.72), 24, MINUS, a, BG, 3)
            text(out, (c[0] + it['r'] * 0.72, c[1] - it['r'] * 0.72 - 20), it['n'], 30, BG, 'K', 'c', a)
        draw_band(img, out, ease(lt / 0.3))
        label_chip(img, (L, BAND_Y - 74), S['chip'], ease((lt - 0.1) / 0.3), 32, BG, MINUS)
        for j, it in enumerate(S['items']):
            at = lead + nar * it['at']; a = ease((t - at) / 0.3); yo = (1 - eo((t - at) / 0.4)) * 20
            y = BAND_Y + BAND_H + 34 + j * 98
            if a <= 0: continue
            dot(img, (L + 24, y + 26 + yo), 22, MINUS, a, BG, 2)
            text(img, (L + 24, y + 6 + yo), it['n'], 28, BG, 'K', 'c', a)
            text(img, (L + 66, y + yo), it['k'], 40, INK, 'X', 'l', a, maxw=R - L - 70)
            text(img, (L + 66, y + 52 + yo), it['v'], 27, SOFT, 'M', 'l', a, maxw=R - L - 70)
        text(img, (L, 1508), S['credit'], 22, FAINT, 'M', 'l', 1)
    else:
        img = bg_blur(sh['src'], 0.2, 30)
        out, tf = band_img(load(sh['src']), lt / max(1.0, dur), sh['kb'])
        if sh.get('pin'): pulse(out, tf(P(sh['pin'])), lt, ease((lt - 0.3) / 0.4), 0.7)
        rg = sh.get('ring')
        if rg:
            rp, rr = (P(rg), rg['r']) if isinstance(rg, dict) else (rg[:2], rg[2])
            rc = tf(rp); ra = ease((lt - 0.5) / 0.4)
            for k in range(2):
                ring(out, rc, rr * (0.85 + 0.15 * k) * (0.9 + 0.1 * math.sin(lt * 4)), MINUS, 6 - 2 * k, ra * (0.95 - 0.4 * k))
            lw = F(32, 'X').getlength(sh['ring_label']) + 36
            label_chip(out, (min(max(24, rc[0] - lw / 2), W - 200 - lw), max(20, rc[1] - rr - 70)), sh['ring_label'], ease((lt - 0.8) / 0.3), 32, BG, MINUS, 'l')
        if sh.get('pin_label') and sh.get('pin'):
            pp = tf(P(sh['pin'])); label_chip(out, (pp[0] + 40, pp[1] - 100), sh['pin_label'], ease((lt - 0.6) / 0.3), 30)
        draw_band(img, out, ease(lt / 0.3))
        label_chip(img, (L, BAND_Y - 74), sh['chip'], ease((lt - 0.1) / 0.3), 32, BG, MINUS)
        caption(img, sh['cap'], sh.get('sub'), ease((lt - 0.7) / 0.4))
        text(img, (L, 1508), sh['credit'], 22, FAINT, 'M', 'l', 1)
    chapter(img, t, num('trap'), '모집공고 속 유의사항은?')
    return img

def wrap(s, px, w, maxw):
    f = F(px, w); out = []; cur = ''
    for word in s.split(' '):
        nx = (cur + ' ' + word).strip()
        if f.getlength(nx) <= maxw: cur = nx
        else: out.append(cur); cur = word
    if cur: out.append(cur)
    return out

def sc_end(t, d, nar, lead):
    img, sp = open_bg(1.0, 1.0)
    img = darken(img, 0.55)
    pulse(img, sp, t, 0.8)
    text(img, (CX, 220), C['name'], 120, INK, 'K', 'c', ease(t / 0.4), maxw=880, track=-2)
    text(img, (CX, 372), '1분 총정리', 46, BR, 'X', 'c', ease((t - 0.2) / 0.4))
    E = C['end']
    n = len(E['rows']); gap = 152 if n <= 4 else 124
    rrect(img, (L, 470, R, 470 + 40 + n * gap - 30), (10, 10, 11), 0.9 * ease((t - 0.2) / 0.4), 26, BR, 2, 0.6)
    for i, (n_, k, v) in enumerate(E['rows']):
        n = n_; y = 506 + i * gap; a = ease((t - 0.35 - i * 0.18) / 0.35)
        text(img, (L + 36, y), n, 34, BR, 'K', 'l', a)
        text(img, (L + 100, y - 4), k, 40, INK, 'X', 'l', a)
        text(img, (L + 100, y + 52), v, 32, SOFT, 'B', 'l', a, maxw=R - L - 140)
        if i < len(E['rows']) - 1: rrect(img, (L + 36, y + gap - 32, R - 36, y + gap - 30), HAIR, a)
    sa = ease((t - 1.4) / 0.4)
    rrect(img, (L, 1180, R, 1270), None, sa, 45, BR, 3, sa)
    text(img, (CX, 1200), E['sched'], 40, BR_INK, 'X', 'c', sa, maxw=R - L - 60)
    qa = ease((t - nar * 0.82) / 0.4); qk = eo((t - nar * 0.82) / 0.6)
    text(img, (CX, 1310 + (1 - qk) * 30), E['q'], 96, BR, 'K', 'c', qa)
    footer(img, None, 1)
    return img

# ------------------------------------------------------------------ 타임라인
NAR = {k: wav_len(TTS + f'{k}.wav') for k in C['narration']}
SCN = [('open', sc_open, 0.2, 0.6), ('cash', sc_cash, 0.4, 1.0), ('prem', sc_prem, 0.35, 0.3),
       ('loc', sc_loc, 0.3, 0.7), ('prod', sc_prod, 0.3, 0.9), ('trap', sc_trap, 0.3, 1.3), ('end', sc_end, 0.3, 1.6)]
SCN = [x for x in SCN if x[0] in C['narration']]
CH = [k for k, *_ in SCN if k not in ('open', 'end')]   # 진행 막대 순서
SC = []; cur = 0.0
for k, fn, lead, tail in SCN:
    d = lead + NAR[k] + tail
    if k == 'prem': d = max(d, bridge_T()['end'] + 0.2)
    if k == 'loc': d = max(d, sum(s.get('dur', 0) for s in C['loc'] if s['type'] != 'map') + 4.0)
    SC.append((k, fn, cur, d, lead)); cur += d
DUR = cur
XF = 0.3

def draw_scene(i, t):
    k, fn, s, d, lead = SC[i]; lt = t - s
    if k == 'open': img = fn(lt, d, NAR[k])
    else: img = fn(lt, d, NAR[k], lead)
    if k != 'open':
        ci = CH.index(k) if k in CH else len(CH)
        progress(img, ci, clamp(lt / d) if ci < len(CH) else 1.0, ease(lt / 0.4) if k == CH[0] else 1.0)
        sweep(img, lt)
    return img

def frame(t):
    i = max(j for j, s in enumerate(SC) if t >= s[2] or j == 0)
    img = draw_scene(i, t)
    k, fn, s, d, lead = SC[i]
    if i + 1 < len(SC) and t > s + d - XF:
        nxt = draw_scene(i + 1, t)
        img = Image.blend(img, nxt, ease((t - (s + d - XF)) / XF))
    return img

# ------------------------------------------------------------------ 소리·렌더
def build_audio(path):
    n = int(DUR * SR) + SR
    starts = [s for _, _, s, _, _ in SC]
    st = {k: (s, d, l) for k, _, s, d, l in SC}
    reveal = st['prem'][0] + bridge_T(st['prem'][1])['prem'] + 0.2
    tmp = OUT + '_music.wav'
    audio_orig.make_audio(tmp, DUR + 1.0, RISE=tuple(starts[1:]), BOOM=((reveal, 0.6), (st['end'][0] + 0.2, 0.5)))
    with wave.open(tmp) as w:
        m = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32).reshape(-1, 2) / 32768
    mus = np.zeros((n, 2)); Lm = min(n, len(m)); mus[:Lm] = m[:Lm]
    nar = np.zeros(n)
    for k, (s, d, l) in st.items():
        with wave.open(TTS + f'{k}.wav') as w:
            x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
        i = int((s + l) * SR); nar[i:i + len(x)] += x[:max(0, n - i)]
    nar /= max(1e-6, np.abs(nar).max()); nar *= 0.85
    env = np.convolve(np.abs(nar), np.ones(int(0.25 * SR)) / int(0.25 * SR), 'same')
    duck = 1.0 - 0.6 * np.clip(env / 0.08, 0, 1)
    out = mus * 0.15 * duck[:, None] + nar[:, None]
    lib = {'whoosh': sfx.whoosh(), 'lowhit': sfx.lowhit(), 'tick': sfx.tick(), 'shimmer': sfx.shimmer(), 'ping': sfx.ping()}
    ev = [(s - 0.3, 'whoosh', 0.16) for s in starts[1:]]
    ev += [(st['open'][0] + NAR['open'] * f + 0.2, 'tick', 0.22) for f in TICKS]
    if 'prod' in st:
        ev += [(st['prod'][0] + st['prod'][2] + NAR['prod'] * sh['at'] - 0.25, 'whoosh', 0.1) for sh in C['prod']['shots'][1:]]
    ev += [(reveal, 'lowhit', 0.3), (reveal, 'ping', 0.2)]
    for cd in C['cash']['cards']:
        ev.append((st['cash'][0] + st['cash'][2] + NAR['cash'] * cd['at'] + 0.4, 'tick', 0.2))
    for s in C['trap'].get('shots', []) + C['trap'].get('site', {}).get('items', []):
        ev.append((st['trap'][0] + st['trap'][2] + NAR['trap'] * s['at'] + 0.4, 'lowhit', 0.2))
    ev += [(DUR - 2.0, 'shimmer', 0.2)]
    for t0, name, g in ev:
        i = int(max(0, t0) * SR); x = lib[name] * g; Lx = min(len(x), n - i)
        if Lx > 0: out[i:i + Lx] += x[:Lx, None]
    out = out[:int(DUR * SR)]
    fade = int(0.5 * SR); out[-fade:] *= np.linspace(1, 0, fade)[:, None]
    out = np.tanh(out * 1.05); out /= max(1e-6, np.abs(out).max()) / 0.89
    with wave.open(path, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out * 32767).astype(np.int16).tobytes())

def thumbnail(path):
    img, sp = open_bg(0, 0.0)
    rings = img.copy()
    for r, al in [(150, 0.25), (105, 0.45), (64, 0.7)]: ring(img, sp, r, BR, 5, al)
    dot(img, sp, 26, BR, 1.0, (255, 255, 255), 6)
    tx, ty = sp[0] + 60, sp[1] - 150
    line(img, [(sp[0] + 18, sp[1] - 20), (tx + 10, ty + 70)], BR, 4, 1)
    label_chip(img, (tx, ty), '단지 위치', 1.0, 50)
    text(img, (CX, 150), C['region'], 52, BR, 'B', 'c')
    text(img, (CX, 225), C['name'], 168, INK, 'K', 'c', maxw=900, track=-2)
    text(img, (CX, 445), '청약하실 분은 이것만 보세요', 64, INK, 'X', 'c', maxw=880)
    checklist(img, 1.0, [1.0] * len(C['checklist']))
    rrect(img, (CX - 330, 1562, CX + 330, 1650), BR, 1, 46)
    text(img, (CX, 1574), '청약 전 1분 총정리', 56, BG, 'K', 'c')
    text(img, (24, 1888), '© Mapbox © Maxar', 20, FAINT, 'M', 'l')
    img.save(path)

def render():
    name = C['out']; os.makedirs(OUT, exist_ok=True)
    vtmp = OUT + f'_{name}_v.tmp.mp4'
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '23', '-pix_fmt', 'yuv420p', vtmp], stdin=subprocess.PIPE)
    nf = int(round(DUR * FPS))
    for fi in range(nf):
        p.stdin.write(finish(frame(fi / FPS), fi).tobytes())
        if fi % 300 == 0: print('frame', fi, '/', nf, flush=True)
    p.stdin.close(); assert p.wait() == 0
    build_audio(OUT + f'_{name}.wav')
    tmp = OUT + f'_{name}.tmp.mp4'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', vtmp, '-i', OUT + f'_{name}.wav', '-map', '0:v', '-map', '1:a',
                    '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', tmp], check=True)
    os.replace(tmp, OUT + f'{name}.mp4'); os.remove(vtmp)
    thumbnail(OUT + f'{name}-thumbnail.png')
    print('done', OUT + f'{name}.mp4', round(DUR, 2))

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    cmd = sys.argv[2] if len(sys.argv) > 2 else 'render'
    if cmd == 'stills':
        print([(k, round(s, 2), round(d, 2)) for k, _, s, d, _ in SC], round(DUR, 2))
        for a in sys.argv[3:]:
            t = float(a); Image.fromarray(finish(frame(t), 0)).save(OUT + f'still_{float(a):06.2f}.png')
    elif cmd == 'thumb':
        thumbnail(OUT + f"{C['out']}-thumbnail.png")
    else:
        render()
