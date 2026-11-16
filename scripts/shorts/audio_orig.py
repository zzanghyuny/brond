import numpy as np, wave
def make_audio(path, DUR=30.0, RISE=(3,7,11,15,19.6,24.4), BOOM=((22.3,0.9),(26.4,0.7))):
    sr = 44100
    n = int(sr * DUR)
    t = np.arange(n) / sr
    rng = np.random.default_rng(3)
    def sine(f, ph=0): return np.sin(2 * np.pi * f * t + ph)
    # 저음 드론 (A1·E2 + 느린 디튠)
    drone = 0.55 * sine(55.0) + 0.35 * sine(55.0 * 1.003, 1.1) + 0.28 * sine(82.41) + 0.12 * sine(110.0)
    # 패드 (A마이너 계열, 느린 스웰)
    pad = np.zeros(n)
    for f, g in [(110.0, .22), (164.81, .18), (220.0, .16), (261.63, .12), (329.63, .10), (440.0, .05)]:
        pad += g * (sine(f) + 0.6 * sine(f * 1.004, 0.7) + 0.4 * sine(f * 0.996, 1.9))
    swell = 0.35 + 0.65 * np.clip(np.sin(np.pi * np.clip(t / DUR, 0, 1)) ** 0.8, 0, 1)
    pad *= swell
    # 심장박동 같은 저음 펄스 (3초부터 점점 강해짐)
    pulse = np.zeros(n)
    beat = 0.9
    tb = 3.0
    while tb < DUR - 3.0:
        i = int(tb * sr)
        k = np.arange(int(0.28 * sr)) / sr
        thump = np.sin(2 * np.pi * (62 - 22 * k / 0.28) * k) * np.exp(-k * 14)
        amp = 0.25 + 0.55 * min(1.0, (tb - 3) / max(1.0, DUR - 12))
        pulse[i:i + len(thump)] += amp * thump[:max(0, min(len(thump), n - i))] if i + len(thump) <= n else 0
        tb += beat
    # 장면 전환 라이저(필터 노이즈 스윕)
    noise = rng.normal(0, 1, n)
    rise = np.zeros(n)
    for c in RISE:
        i0, i1 = int((c - 0.9) * sr), int((c + 0.15) * sr)
        seg = noise[i0:i1]
        env = np.sin(np.linspace(0, np.pi / 2, len(seg))) ** 2 * np.linspace(1, 0.1, len(seg)) ** 0.3
        rise[i0:i1] += seg * env * 0.05
    # 메인 임팩트 두 번(결과 공개 24초, 엔딩 28초)
    boom = np.zeros(n)
    for c, g in BOOM:
        i = int(c * sr); k = np.arange(int(2.2 * sr)) / sr
        b = np.sin(2 * np.pi * (48 - 14 * (1 - np.exp(-k * 2.5)) * 1.0) * k) * np.exp(-k * 1.5)
        boom[i:i + len(b)] += g * b[:max(0, min(len(b), n - i))] if i + len(b) <= n else 0
    mono = 0.30 * drone + 0.33 * pad + pulse * 0.55 + rise + boom * 0.6
    # 간단한 잔향(콤 필터 몇 개)
    out = mono.copy()
    for d_ms, g in [(97, 0.42), (151, 0.36), (233, 0.30), (359, 0.24)]:
        d = int(sr * d_ms / 1000)
        out[d:] += g * mono[:-d]
    # 스테레오 폭(작은 지연 차이)
    L = out
    R = np.concatenate([np.zeros(int(sr * 0.012)), out[:-int(sr * 0.012)]])
    st = np.stack([L, R], 1)
    # 페이드 인/아웃
    env = np.ones(n)
    env[:int(sr * 1.2)] = np.linspace(0, 1, int(sr * 1.2)) ** 2
    env[-int(sr * 1.6):] = np.linspace(1, 0, int(sr * 1.6)) ** 1.5
    st *= env[:, None]
    st = np.tanh(st * 1.1)
    st /= max(1e-6, np.abs(st).max()) / 0.72
    pcm = (st * 32767).astype(np.int16)
    with wave.open(path, 'wb') as wf:
        wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(sr); wf.writeframes(pcm.tobytes())

