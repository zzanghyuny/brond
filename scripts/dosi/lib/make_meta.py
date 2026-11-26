# -*- coding: utf-8 -*-
"""유튜브 제목·설명(챕터·출처)·태그 + credits_log.csv. 렌더 뒤 실행: python3 make_meta.py <에피소드 폴더>
결과: <work>/deliver/{name}-description.txt (본편·쇼츠 2), credits_log.csv"""
import os, sys, json, csv, importlib.util, datetime
EPD = sys.argv[1]
spec = importlib.util.spec_from_file_location('script', os.path.join(EPD, 'script.py')); S = importlib.util.module_from_spec(spec); spec.loader.exec_module(S)
EP = S.EP; W = EP['work']; O = W + 'deliver/'; os.makedirs(O, exist_ok=True); N = EP['names']
TODAY = datetime.date.today().isoformat()
def mmss(t): t = int(round(t)); return f'{t // 60}:{t % 60:02d}'
tl = json.load(open(W + 'out_LONG/timeline.json'))
chap = [(0, '오프닝')] + [(st, n) for st, n in tl['chapters'] if st > 0]
# 유튜브 챕터는 10초 이상이어야 해서 짧은 챕터는 다음 챕터와 합친다
i = 0
while i < len(chap) - 1:
    if chap[i + 1][0] - chap[i][0] < 10.0 and i > 0:
        chap[i] = (chap[i][0], chap[i][1] + ' · ' + chap[i + 1][1]); del chap[i + 1]
    elif chap[i + 1][0] - chap[i][0] < 10.0:
        chap[i + 1] = (chap[i + 1][0], chap[i + 1][1]); i += 1
    else: i += 1
tags = ' '.join('#' + t for t in S.TAGS[:8])
src = '\n'.join(f'· {t} — {u}' for t, u in S.SOURCES)
site = EP.get('site_url', 'https://www.brandongsan.com/city-story.html')
desc = f"""{EP['yt_title']}

{EP.get('yt_intro', '')}

[챕터]
""" + '\n'.join(f'{mmss(t)} {n}' for t, n in chap) + f"""

[글로 보기] {site}

[숫자 출처]
{src}

[화면 출처]
· 영상: Pexels (Pexels License, 상업 이용 가능)
· 지도: © OpenStreetMap contributors (ODbL), Natural Earth — 브동산 자체 제작 개략도, 실제 경계·축척과 다를 수 있음
· 음악: 브동산 자체 제작 · 내레이션: AI 음성(인준)

※ 공개 자료를 정리한 교육용 콘텐츠이며 특정 부동산의 분양·투자를 권유하지 않아요.
브동산 brandongsan.com
{tags}
"""
open(O + f"{N['LONG']}-description.txt", 'w', encoding='utf-8').write(
    f"[제목]\n{EP['yt_title']}\n\n[태그]\n{', '.join(S.TAGS)}\n\n[설명]\n" + desc)
for w in ('S1', 'S2'):
    t = EP['shorts_title'][w]; d = EP.get('shorts_desc', {}).get(w, '')
    open(O + f"{N[w]}-description.txt", 'w', encoding='utf-8').write(
        f"[제목]\n{t}\n\n[설명]\n{d}\n\n본편: {EP['yt_title']}\n글로 보기: {site}\n영상 Pexels · 지도 © OpenStreetMap contributors · Natural Earth\n{tags} #shorts\n")
rows = []; n = 0
for w in ('LONG', 'S1', 'S2'):
    tlw = tl['timeline'] if w == 'LONG' else json.load(open(W + f'out_{w}/timeline.json'))['timeline'] if os.path.exists(W + f'out_{w}/timeline.json') else None
    for i, s in enumerate(getattr(S, w)):
        for sh in s['shots']:
            if sh[0] != 'clip': continue
            n += 1; tc = f"{mmss(tlw[i]['start'])}" if tlw else ''
            rows.append([f'A{n:03d}', f'px_{sh[1]}.mp4', '영상', 'Pexels', f'https://www.pexels.com/video/{sh[1]}/', '', 'Pexels License', TODAY, 'Y', 'N', w, tc, s.get('tag', s.get('chap', ''))])
with open(O + 'credits_log.csv', 'w', newline='', encoding='utf-8-sig') as f:
    cw = csv.writer(f); cw.writerow(['번호', '파일', '종류', '출처', '원본 주소', '작가', '라이선스', '확인일', '상업이용', '구글어스', '영상', '시간', '장면']); cw.writerows(rows)
print('meta ok', len(rows))
