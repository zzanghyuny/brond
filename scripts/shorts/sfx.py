# -*- coding: utf-8 -*-
"""쇼츠·클립·릴스용 효과음 합성과 믹싱 (2026.11.15 확정 조합).
 - 장면 전환마다: whoosh   - 예상 프리미엄 공개: lowhit + ping
 - 마무리 직전: shimmer    - 평균 분양가 카운트업: tick(약하게)
"""
import numpy as np, wave
SR = 44100
_rng = np.random.default_rng(1)

def _lp(x, fc):
    a = np.exp(-2 * np.pi * fc / SR); y = np.zeros_like(x); s = 0.0
    for i in range(len(x)):
        s = (1 - a) * x[i] + a * s; y[i] = s
    return y

def _rev(x, t=1.2):
    n = len(x); irn = int(t * SR); k = np.arange(irn) / SR
    ir = _rng.normal(0, 1, irn) * np.exp(-k / (t / 4)); ir /= np.abs(ir).sum() ** 0.5 * 10
    m = 1 << int(np.ceil(np.log2(n + irn)))
    return np.fft.irfft(np.fft.rfft(x, m) * np.fft.rfft(ir, m), m)[:n]

def _norm(x): return x / max(1e-6, np.abs(x).max())

def whoosh():
    n = int(0.9 * SR); t = np.arange(n) / SR; nz = _rng.normal(0, 1, n)
    env = np.sin(np.pi * np.clip(t / 0.9, 0, 1)) ** 2
    sw = sum(g * _lp(nz, fc) for fc, g in [(400, 1), (1200, .6), (3000, .3)])
    w = np.pad(sw * env, (0, SR))[:int(1.6 * SR)]
    return _norm(_rev(w, .8) + w)

def lowhit():
    n = int(2.0 * SR); t = np.arange(n) / SR
    h = np.sin(2 * np.pi * (55 - 18 * (1 - np.exp(-t * 6))) * t) * np.exp(-t * 2.2) + .5 * np.sin(2 * np.pi * 110 * t) * np.exp(-t * 5)
    h += .3 * _lp(_rng.normal(0, 1, n), 300) * np.exp(-t * 14)
    return _norm(_rev(h, 1.5) * .8 + h)

def tick():
    n = int(.25 * SR); t = np.arange(n) / SR
    return _norm(np.sin(2 * np.pi * 2400 * t) * np.exp(-t * 60) + .4 * np.sin(2 * np.pi * 4800 * t) * np.exp(-t * 90))

def shimmer():
    n = int(1.8 * SR); t = np.arange(n) / SR; r = np.zeros(n)
    for f0 in [523.25, 659.25, 783.99, 1046.5]:
        r += np.sin(2 * np.pi * np.cumsum(f0 * (0.9 + 0.1 * t / 1.8)) / SR) * (t / 1.8) ** 2 * .4
    r *= np.minimum(1, (1.8 - t) / .15); r = np.pad(r, (0, SR))
    return _norm(_rev(r, 1.4) * 1.2 + r * .5)

def ping():
    n = int(2.2 * SR); t = np.arange(n) / SR
    p = np.sin(2 * np.pi * 1318.5 * t) * np.exp(-t * 3.2) + .5 * np.sin(2 * np.pi * 1318.5 * 2.76 * t) * np.exp(-t * 7) + .25 * np.sin(2 * np.pi * 659.25 * t) * np.exp(-t * 2.5)
    return _norm(_rev(p, 1.2) * .8 + p)

def build_events(scenes, reveal):
    """scenes=[(start,end,fn,l0,kind)], reveal=예상 프리미엄 공개 시각. → [(시작초, 효과음, 음량)]"""
    ev = []
    for s, _, _, _, kind in scenes[1:]:
        ev.append((s - 0.45, 'whoosh', 0.55))
    ev.append((reveal, 'lowhit', 0.75)); ev.append((reveal + 0.05, 'ping', 0.45))
    es = scenes[-1][0]; ev.append((es - 1.3, 'shimmer', 0.5))
    for s, e, _, _, kind in scenes:
        if kind == 'price':
            t = s + 0.25
            while t < s + 2.4: ev.append((t, 'tick', 0.16)); t += 0.2
    return ev

def mix(path_in, path_out, events):
    with wave.open(path_in) as w:
        ch = w.getnchannels(); data = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    data = data.reshape(-1, ch)
    lib = {'whoosh': whoosh(), 'lowhit': lowhit(), 'tick': tick(), 'shimmer': shimmer(), 'ping': ping()}
    out = data.copy()
    for t0, name, g in events:
        i = int(max(0, t0) * SR); x = lib[name] * g
        L = min(len(x), len(out) - i)
        if L > 0: out[i:i + L] += x[:L, None]
    out = np.tanh(out * 0.95); out /= max(1e-6, np.abs(out).max()) / 0.9
    with wave.open(path_out, 'wb') as w:
        w.setnchannels(ch); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out * 32767).astype(np.int16).tobytes())
