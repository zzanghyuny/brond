import sys, os, json, subprocess, asyncio, ssl, certifi, shutil
certifi.where = lambda: "/root/.ccr/ca-bundle.crt"
import edge_tts, edge_tts.communicate as c
c._SSL_CTX = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt")
sys.path.insert(0, '/home/claude/work/ep1'); import script_ep1 as S
VOICE, RATE, PITCH = 'ko-KR-SunHiNeural', '-10%', '+3Hz'
D = '/home/claude/work/ep1/'
def dur(p): return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p]))
async def run(w):
    src = f'{D}tts_{w}.ava.json'
    if not os.path.exists(src): shutil.copy(f'{D}tts_{w}.json', src)
    meta = json.load(open(src)); sc = getattr(S, w); od = f'{D}tts_{w}_sunhi/'; os.makedirs(od, exist_ok=True)
    out = []; stats = []
    for m in meta:
        disp, say = sc[m['scene']]['lines'][m['line']]
        mp3 = f"{od}s{m['scene']:02d}_{m['line']}.mp3"
        for k in range(4):
            try:
                if not (os.path.exists(mp3) and os.path.getsize(mp3) > 1000): await edge_tts.Communicate(say or disp, VOICE, rate=RATE, pitch=PITCH).save(mp3)
                break
            except Exception as e: print('retry', e); await asyncio.sleep(3)
        raw = mp3[:-4] + '_raw.wav'
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', mp3, '-af', 'silenceremove=start_periods=1:start_threshold=-50dB,areverse,silenceremove=start_periods=1:start_threshold=-50dB,areverse', '-ar', '44100', '-ac', '1', raw], check=True)
        dn = dur(raw)
        last_in_scene = not any(x['scene'] == m['scene'] and x['line'] == m['line'] + 1 for x in meta)
        allowed = m['dur'] + (0.65 if last_in_scene else 0.36)
        f = dn / allowed
        fit = mp3[:-4] + '.wav'
        if f > 1.0:
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', raw, '-af', f'atempo={f:.4f}', '-ar', '44100', '-ac', '1', fit], check=True)
        else: shutil.copy(raw, fit)
        stats.append(f); out.append(dict(m, wav=fit))
    json.dump(out, open(f'{D}tts_{w}.json', 'w'), ensure_ascii=False, indent=1)
    print(w, 'lines', len(out), 'sped up', sum(1 for x in stats if x > 1), 'max factor', round(max(stats), 3), 'mean new/old', round(sum(stats) / len(stats), 3))
for w in sys.argv[1:]: asyncio.run(run(w))
