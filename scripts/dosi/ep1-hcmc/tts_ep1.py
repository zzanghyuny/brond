import sys, os, json, subprocess, asyncio, ssl, certifi
certifi.where = lambda: "/root/.ccr/ca-bundle.crt"
import edge_tts, edge_tts.communicate as c
c._SSL_CTX = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import script_ep1 as script
VOICE, RATE, PITCH = 'en-US-AvaMultilingualNeural', '-6%', '+0Hz'
D = os.path.dirname(os.path.abspath(__file__))
async def one(text, out):
    if os.path.exists(out) and os.path.getsize(out) > 1000: return
    for k in range(4):
        try:
            await edge_tts.Communicate(text, VOICE, rate=RATE, pitch=PITCH).save(out); return
        except Exception as e: print('retry', k, e); await asyncio.sleep(3)
async def main(which):
    sc = getattr(script, which); os.makedirs(f'{D}/tts_{which}', exist_ok=True); meta = []
    for i, s in enumerate(sc):
        for j, (disp, say) in enumerate(s['lines']):
            mp3 = f'{D}/tts_{which}/s{i:02d}_{j}.mp3'; wav = mp3[:-4] + '.wav'
            await one(say or disp, mp3)
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', mp3, '-af', 'silenceremove=start_periods=1:start_threshold=-50dB,areverse,silenceremove=start_periods=1:start_threshold=-50dB,areverse', '-ar', '44100', '-ac', '1', wav], check=True)
            d = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', wav]))
            meta.append(dict(scene=i, line=j, wav=wav, dur=d))
    json.dump(meta, open(f'{D}/tts_{which}.json', 'w'), ensure_ascii=False, indent=1)
    print(which, 'total speech', round(sum(m['dur'] for m in meta), 1), 's,', len(meta), 'lines')
for w in sys.argv[1:]: asyncio.run(main(w))
