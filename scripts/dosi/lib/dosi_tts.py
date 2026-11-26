# -*- coding: utf-8 -*-
"""도시이야기 나레이션(인준). 사용: python3 dosi_tts.py <에피소드 폴더> LONG S1 S2
본편 ko-KR-InJoonNeural -4% -2Hz / 쇼츠 같은 목소리 기본 속도(+0%)."""
import sys, os, json, subprocess, asyncio, ssl, importlib.util
CA = '/root/.ccr/ca-bundle.crt'
if os.path.exists(CA):
    import certifi; certifi.where = lambda: CA
import edge_tts, edge_tts.communicate as c
if os.path.exists(CA): c._SSL_CTX = ssl.create_default_context(cafile=CA)
VOICE = 'ko-KR-InJoonNeural'
PARAMS = {'LONG': ('-4%', '-2Hz'), 'S1': ('+0%', '+0Hz'), 'S2': ('+0%', '+0Hz')}

def load(ep_dir):
    spec = importlib.util.spec_from_file_location('script', os.path.join(ep_dir, 'script.py')); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

async def one(text, out, rate, pitch):
    if os.path.exists(out) and os.path.getsize(out) > 1000: return
    for k in range(5):
        try:
            kw = dict(rate=rate, pitch=pitch)
            if os.environ.get('HTTPS_PROXY'): kw['proxy'] = os.environ['HTTPS_PROXY']
            await edge_tts.Communicate(text, VOICE, **kw).save(out); return
        except TypeError:
            await edge_tts.Communicate(text, VOICE, rate=rate, pitch=pitch).save(out); return
        except Exception as e: print('retry', k, e); await asyncio.sleep(3)
    raise SystemExit('TTS 실패: ' + text)

async def main(ep_dir, which):
    S = load(ep_dir); W = S.EP['work']; sc = getattr(S, which); rate, pitch = PARAMS[which]
    os.makedirs(f'{W}tts_{which}', exist_ok=True); meta = []
    for i, s in enumerate(sc):
        for j, ln in enumerate(s['lines']):
            disp, say = ln[0], ln[1]
            mp3 = f'{W}tts_{which}/s{i:02d}_{j}.mp3'; wav = mp3[:-4] + '.wav'
            await one(say or disp, mp3, rate, pitch)
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', mp3, '-af', 'silenceremove=start_periods=1:start_threshold=-50dB,areverse,silenceremove=start_periods=1:start_threshold=-50dB,areverse', '-ar', '44100', '-ac', '1', wav], check=True)
            d = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', wav]))
            meta.append(dict(scene=i, line=j, wav=wav, dur=d))
    json.dump(meta, open(f'{W}tts_{which}.json', 'w'), ensure_ascii=False, indent=1)
    print(which, 'speech', round(sum(m['dur'] for m in meta), 1), 's,', len(meta), 'lines')

if __name__ == '__main__':
    for w in sys.argv[2:]: asyncio.run(main(sys.argv[1], w))
