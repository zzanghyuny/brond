#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""shorts-upload/<YYYY-MM>/README.md를 퀴즈 설정(quiz/*.json)으로 만든다.
usage: python3 upload_readme.py <YYYY-MM> <키:접수 요약> ...   (순서 = 올리는 순서)
예:    python3 upload_readme.py 2026-11 "gyeonghuigung:특공 11.25 · 1순위 11.26~27" ...
"""
import os, sys, json, re
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
month = sys.argv[1]
rows, blocks = [], []
for i, arg in enumerate(sys.argv[2:], 1):
    key, when = arg.split(':', 1)
    C = json.load(open(os.path.join(HERE, 'quiz', key + '.json'), encoding='utf8'))
    s1, s7 = C['s1'], C['s7']
    fair = next(v for l, v, c in s7['bars'] if c == 'brass'); price = next(v for l, v, c in s7['bars'] if c == 'ink')
    prem = s7['badge'].split(' ', 1)[1]
    area = C.get('area', '84m²')
    hook = s1['hook1'].rstrip(',') + ', ' + s1.get('hook2', '맞히면 부동산 고수')
    tag = re.sub(r'\s+', '', s1['name'])
    city = s1['region'].split(' ')[1] if len(s1['region'].split(' ')) > 1 else ''
    rows.append(f"| {i} | `{C['out']}` | {when} | {s1['name']} |")
    blocks.append(f"""### {i}. {C['out']}
- 제목: {hook} | {s1['name']} 예상프리미엄 {prem}
- 설명:
  {s1['region']} {s1['name']}. {area} 평균 분양가 {price:.2f}억, 브동산 적정가 {fair:.2f}억({s7['badge']}).
  {C['s8']['l1']}, {C['s8']['big']}. 접수 {when}.
  브동산 모형 추정치이며 확정 수익이 아닙니다. 자격·일정은 청약홈 입주자모집공고를 확인하세요. 투자 권유 아님.
- 해시태그: #{tag} #{re.sub(r'(시|군|구)$', '', city)}아파트 #청약 #분양가 #부동산퀴즈 #브동산
- 고정 댓글: 몇 번 고르셨나요? A·B·C로 남겨주세요. 맞히셨으면 부동산 고수 인정!
""")
out = os.path.join(REPO, 'shorts-upload', month, 'README.md')
open(out, 'w', encoding='utf8').write(f"""# 쇼츠·클립·릴스 업로드 묶음 ({month})

Aside 배포용. 영상(`<이름>.mp4`, 1080×1920 세로, 40~45초)과 썸네일(`<이름>-thumbnail.png`)이 한 쌍이다. 이 폴더는 사이트(Vercel)에는 배포되지 않는다(`.vercelignore`). GitHub에서 파일을 열어 **Download raw file**로 받는다.

**Aside가 유튜브 업로드를 마치면 Paul이 삭제를 요청한다 → 그때 해당 파일을 이 폴더에서 지운다.**

## 올리는 순서 (접수일이 빠른 순)

| 순서 | 파일 | 접수 | 단지 |
|---|---|---|---|
""" + '\n'.join(rows) + "\n\n## 제목 · 설명 · 해시태그 (복사용)\n\n" + '\n'.join(blocks))
print(out)
