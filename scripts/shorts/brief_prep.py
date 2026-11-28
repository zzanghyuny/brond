#!/usr/bin/env python3
# 1분 총정리 준비: 사이트 글 텍스트·청약홈 공고문 텍스트(pdftotext)·KB 좌표·공고문 유의사항 후보 문장(/tmp/brief/<slug>/hits.txt)
#   python3 scripts/shorts/brief_prep.py <slug> <청약홈 단지명 키워드> [KB 키워드]
import sys, os, re, html, json, subprocess
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); sys.path.insert(0, ROOT + '/jupjup'); sys.path.insert(0, ROOT + '/beodongsan')
os.environ.setdefault('KB_CACHE', ROOT + '/beodongsan/kbcache.json')
import applyhome, kb
slug, kw = sys.argv[1], sys.argv[2]; kbkw = sys.argv[3] if len(sys.argv) > 3 else kw
D = f'/tmp/brief/{slug}/'; os.makedirs(D + 'img', exist_ok=True)
t = html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', open(os.path.join(ROOT, '..', 'posts', slug + '.html')).read())))
open(D + 'post.txt', 'w').write(t)
if not os.path.exists(D + 'notice.txt'):
    rs = [r for r in applyhome.search(kw, '202610', '202612')]
    print('applyhome', rs[:5])
    if rs:
        r = rs[0]; d = applyhome.detail(r['hmno'], r['pbno']); print('detail', d)
        if d['pdf']:
            subprocess.run(['curl', '-s', '--max-time', '90', '-A', applyhome.UA, '-o', D + 'notice.pdf', d['pdf']])
            subprocess.run(['pdftotext', '-layout', D + 'notice.pdf', D + 'notice.txt'])
try:
    dd = kb.get('land-complex/serch/intgraSerch', 검색설정명='SRC_HSCM', 검색키워드=kbkw, 출력갯수='10', 콜센터구분='')
    for x in dd['dataBody']['data']['data'].get('HSCM', {}).get('data', []):
        print('KB', x.get('HSCM_NM'), x.get('WGS84_LNG'), x.get('WGS84_LAT'), x.get('JUSO_ARNO'))
except Exception as e: print('KB fail', e)
if os.path.exists(D + 'notice.txt'):
    n = re.sub(r'\s+', ' ', open(D + 'notice.txt').read())
    sents = re.split(r'(?<=다\.)\s|•|※', n)
    keys = ['비선호', '방음벽', '소음', '빛 공해|빛공해', '냄새|악취', '정압기', '안테나', '변전|송전|철탑|고압', '산업단지|공장', '하수|오수처리|분뇨', '쓰레기|분리수거', '근린공원|문화공원|공원', '주유소|충전소', '고속도로|철도|선로|고가', '학교.*(배정|신설|예정)', '중도금.*(무이자|이자후불|알선)', '소급', '발코니 확장', '지체상금|지체보상', '일조|조망', '군부대|비행|공항|소음지도', '묘지|납골|장례', '기부채납', '사다리차', '전매|재당첨|거주의무']
    out = []
    for k in keys:
        hits = [x.strip()[:260] for x in sents if re.search(k, x)]
        out.append(f'## {k} ({len(hits)})'); out += ['  - ' + h for h in hits[:6]]
    open(D + 'hits.txt', 'w').write('\n'.join(out)); print('hits', D + 'hits.txt', len(n))
