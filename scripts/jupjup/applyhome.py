# 청약홈(applyhome.co.kr) APT 분양정보 검색·공고 상세(모집공고 PDF·홈페이지 주소) 도우미. 사용: python3 scripts/jupjup/applyhome.py <단지명 키워드>  (줍줍찬스 notices.json 채울 때)
import re, html, json, sys, time, subprocess, urllib.parse, os, tempfile
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
def curl(url, data=None):
    cmd=['curl','-s','--max-time','40','-A',UA,'-b',os.path.join(tempfile.gettempdir(),'applyhome-cookie.txt'),'-c',os.path.join(tempfile.gettempdir(),'applyhome-cookie.txt')]
    if data: cmd+=['--data',urllib.parse.urlencode(data)]
    cmd.append(url)
    return subprocess.run(cmd,capture_output=True).stdout.decode('utf-8','ignore')
def search(kw, begin='201901', end='202612'):
    out=[]
    for page in (1,2):
        t=curl('https://www.applyhome.co.kr/ai/aia/selectAPTLttotPblancListView.do',
               {'beginPd':begin,'endPd':end,'houseNm':kw,'houseDetailSecd':'','suplyAreaCode':'','pageIndex':page})
        rows=re.findall(r'<tr data-pbno="(\d+)" data-hmno="(\d+)" data-honm="([^"]*)">\s*<td>([^<]*)</td>(.*?)</tr>',t,flags=re.S)
        for pb,hm,nm,reg,rest in rows:
            tds=re.findall(r'<td[^>]*>(.*?)</td>',rest,flags=re.S)
            clean=[re.sub(r'<[^>]+>','',x).strip() for x in tds]
            out.append({'pbno':pb,'hmno':hm,'name':html.unescape(nm),'region':reg,'date':clean[5] if len(clean)>5 else ''})
        if len(rows)<10: break
    return out
def detail(hm,pb):
    t=curl(f'https://www.applyhome.co.kr/ai/aia/selectAPTLttotPblancDetail.do?houseManageNo={hm}&pblancNo={pb}')
    urls=re.findall(r'https?://[^"\'<> ]+',t)
    pdf=next((u for u in urls if 'getAtchmnfl.do' in u),'')
    home=next((u for u in urls if 'applyhome' not in u and 'kab' not in u.lower() and 'go.kr' not in u),'')
    x=html.unescape(re.sub(r'\s+',' ',re.sub(r'<[^>]+>',' ',t)))
    m=re.search(r'공급위치 (.*?) 공급규모 (\d[\d,]*)세대',x)
    return {'pdf':html.unescape(pdf),'home':html.unescape(home),'addr':m.group(1) if m else '','size':m.group(2) if m else ''}
if __name__=='__main__':
    print(json.dumps(search(sys.argv[1]),ensure_ascii=False,indent=0))
