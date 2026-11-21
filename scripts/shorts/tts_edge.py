# -*- coding: utf-8 -*-
"""쇼츠 나레이션 TTS (Microsoft Edge 신경망 음성, pip install edge-tts)
usage: python3 tts_edge.py <voice> <rate> <pitch> "<문장>" <out.mp3>
채널 보이스: ko-KR-InJoonNeural +16% -3Hz (2026.11.21 부천대장 퀴즈 첫 편)
프록시 환경에서는 CCR CA 번들을 신뢰 저장소로 쓴다(edge-tts가 certifi를 고정해 두기 때문).
"""
import os
import sys, ssl, asyncio
import edge_tts, edge_tts.communicate as C
_CA = '/root/.ccr/ca-bundle.crt'
if os.path.exists(_CA):
    C._SSL_CTX = ssl.create_default_context(cafile=_CA)
async def main(voice, rate, pitch, text, out):
    await edge_tts.Communicate(text, voice, rate=rate, pitch=pitch).save(out)
asyncio.run(main(*sys.argv[1:6]))
