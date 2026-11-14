#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""네이버 모바일 발행 키트 생성기.

naver-html/<slug>.html 을 폰에서 블록 단위로 복사·저장할 수 있는 naver-kit/<slug>.html 로 바꾼다.
  - 제목·태그·본문 텍스트 블록: [복사] 버튼(text/html + text/plain 동시 복사)
  - 이미지·표(PNG로 렌더)·스탯 박스(PNG): 번호 붙은 파일 + [이미지 저장], 한 번에 받는 zip
사용: python3 scripts/naver_kit.py <slug> [<slug>...]   |   python3 scripts/naver_kit.py --all   (발행 전 글 전체)
      python3 scripts/naver_kit.py --index-only         (목록 페이지만 다시 만들기)
"""
import sys, os, re, json, shutil, zipfile, subprocess, html as htmllib, glob
from bs4 import BeautifulSoup, NavigableString
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KIT = os.path.join(ROOT, 'naver-kit')
SITE = 'https://www.brandongsan.com/'
MAXW, MAXKB = 1000, 450
FONT = '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'
MERGE_MAXH, MERGE_MAXKB, GAP = 4500, 800, 24
WARN = []
BEFORE_AFTER = {}


SHORT_BY_STEM = [
    ('chart-a', '평점 비교표'), ('chart-b', '적정가격 그래프'), ('chart-map', '위치 개략도'), ('chart-c', '청약 일정'),
    ('chart-radar', '레이더 차트'), ('chart-bridge', '적정가 산출 그래프'), ('stat', '핵심 수치 박스'), ('table', '표'),
    ('cover', '대표 조감도'), ('aerial', '광역 조감도'), ('location', '입지 정보'), ('site-layout', '단지 배치도'), ('siteplan', '단지 배치도'),
    ('unit-layout', '동호수 배치도'), ('dongho', '동호수 배치도'), ('community', '커뮤니티'), ('overview', '단지 개요'), ('map', '위치도'),
]


def shortlabel(stem, alt=''):
    """사진 자리표시 옆에 붙는 짧은 라벨(≤14자)."""
    st = stem.lower()
    m = re.match(r'^(?:\d+-)?plan[-_]?(.*)$', st)
    if m:
        return ('평면도 ' + m.group(1).upper()).strip()
    for k, v in SHORT_BY_STEM:
        if k in st:
            return v
    a = htmllib.unescape(alt or '').strip()
    a = re.split(r'[:：·(—-]', a)[0].strip() or '이미지'
    return a if len(a) <= 14 else a[:13] + '…'


def load_manifest():
    d = json.load(open(os.path.join(ROOT, 'posts-manifest.json'), encoding='utf-8'))
    return d if isinstance(d, list) else d.get('posts', d.get('items'))


def clean_inline(node):
    """허용 태그(b/strong/a/br)만 남긴 inner HTML."""
    out = []
    for c in node.children:
        if isinstance(c, NavigableString):
            out.append(htmllib.escape(str(c)))
        elif c.name in ('b', 'strong'):
            out.append('<b>' + clean_inline(c) + '</b>')
        elif c.name == 'a':
            out.append('<a href="%s">%s</a>' % (htmllib.escape(c.get('href', ''), True), clean_inline(c)))
        elif c.name == 'br':
            out.append('<br>')
        elif c.name == 'i' or c.name == 'em':
            out.append('<i>' + clean_inline(c) + '</i>')
        else:
            out.append(clean_inline(c))
    return ''.join(out).strip()


def local_image(slug, src):
    if src.startswith(SITE):
        rel = src[len(SITE):]
    elif src.startswith('http'):
        return None
    else:
        rel = 'posts/' + src.lstrip('./')
    p = os.path.join(ROOT, rel)
    return p if os.path.exists(p) else None


def save_image(src_path, dst_base):
    """1000px 폭 이하로 줄이고 ≤450KB가 되도록 저장. 사진=JPEG, 차트/PNG=PNG 유지(필요하면 팔레트화)."""
    im = Image.open(src_path)
    is_png = src_path.lower().endswith('.png')
    if im.width > MAXW:
        im = im.resize((MAXW, round(im.height * MAXW / im.width)), Image.LANCZOS)
    if is_png:
        dst = dst_base + '.png'
        im = im.convert('RGBA') if im.mode in ('RGBA', 'LA', 'P') else im.convert('RGB')
        im.save(dst, 'PNG', optimize=True)
        if os.path.getsize(dst) > MAXKB * 1024:
            q = im.convert('RGB').quantize(colors=128, method=Image.Quantize.MEDIANCUT)
            q.save(dst, 'PNG', optimize=True)
    else:
        dst = dst_base + '.jpg'
        im = im.convert('RGB')
        for qual in (82, 74, 66, 58):
            im.save(dst, 'JPEG', quality=qual, optimize=True)
            if os.path.getsize(dst) <= MAXKB * 1024:
                break
    return dst


def render_fragments(jobs):
    if not jobs:
        return
    jf = os.path.join(KIT, '_jobs.json')
    json.dump(jobs, open(jf, 'w', encoding='utf-8'), ensure_ascii=False)
    subprocess.run(['node', os.path.join(ROOT, 'scripts', 'naver_kit_render.js'), jf], check=True)
    os.remove(jf)


def _wrap(draw, text, font, maxw, maxlines=2):
    lines, cur = [], ''
    for ch in text:
        if draw.textlength(cur + ch, font=font) <= maxw:
            cur += ch
        else:
            lines.append(cur); cur = ch
    if cur:
        lines.append(cur)
    if len(lines) > maxlines:
        lines = lines[:maxlines]; lines[-1] = lines[-1][:-1] + '…'
    return lines


def _bar(text, size, bold=False, W=MAXW):
    font = ImageFont.truetype(FONT, size)
    tmp = ImageDraw.Draw(Image.new('RGB', (W, 10)))
    lines = _wrap(tmp, text, font, W - 48)
    lh = size + 12
    im = Image.new('RGB', (W, 20 + lh * len(lines)), 'white')
    d = ImageDraw.Draw(im)
    for k, ln in enumerate(lines):
        d.text((24, 10 + k * lh), ln, font=font, fill=(17, 17, 17), stroke_width=1 if bold else 0, stroke_fill=(17, 17, 17))
    return im


def _part_image(part, path):
    """제목바(선택) + 캡션바(선택) + 이미지를 세로로 쌓은 한 조각."""
    im = Image.open(path).convert('RGB')
    if im.width != MAXW:
        im = im.resize((MAXW, max(1, round(im.height * MAXW / im.width))), Image.LANCZOS)
    pieces = []
    if part.get('head'):
        pieces.append(_bar(part['head'], 36, True))
    if part.get('cap'):
        pieces.append(_bar(part['cap'], 30))
    pieces.append(im)
    h = sum(x.height for x in pieces)
    out = Image.new('RGB', (MAXW, h), 'white')
    y = 0
    for x in pieces:
        out.paste(x, (0, y)); y += x.height
    return out


def _save_jpeg(im, dst):
    q = 85
    while True:
        im.save(dst, 'JPEG', quality=q, optimize=True)
        if os.path.getsize(dst) <= MERGE_MAXKB * 1024 or (q <= 62 and im.width <= 720):
            return
        if q > 62:
            q -= 8
        else:
            im = im.resize((round(im.width * .9), round(im.height * .9)), Image.LANCZOS)


def merge_runs(slug, outdir, blocks):
    """연속 이미지 블록(사이에 짧은 캡션·h3 제목만 있는 경우)을 세로로 이어 붙인 큰 이미지로 합친다.
    반환: 새 블록 리스트, 최종 파일명 리스트(게시 순서)."""
    tmpdir = outdir + '_new'
    shutil.rmtree(tmpdir, ignore_errors=True); os.makedirs(tmpdir)
    out, files, seq = [], [], 0

    def is_img(b):
        return b['kind'] == 'img' and b.get('file')

    def is_cap(b):
        return b['kind'] == 'text' and b['tag'] == 'note' and len(re.sub('<[^>]+>', '', b['html'])) <= 70

    def is_head(b):
        return b['kind'] == 'text' and b['tag'] == 'h3' and len(re.sub('<[^>]+>', '', b['html'])) <= 40

    i = 0
    while i < len(blocks):
        b = blocks[i]
        if not is_img(b):
            out.append(b); i += 1; continue
        run = [dict(head=None, cap=None, b=b)]
        j = i + 1
        while True:
            k = j
            cap = None
            if k < len(blocks) and is_cap(blocks[k]):
                cap = re.sub('<[^>]+>', '', htmllib.unescape(blocks[k]['html'])).strip(); k += 1
            run[-1]['cap_k'] = (j, k) if cap else None
            run[-1]['cap'] = cap
            head = None
            m = k
            if m < len(blocks) and is_head(blocks[m]):
                head = re.sub('<[^>]+>', '', htmllib.unescape(blocks[m]['html'])).strip(); m += 1
            if m < len(blocks) and is_img(blocks[m]):
                run.append(dict(head=head, cap=None, b=blocks[m])); j = m + 1
                continue
            break
        end = j  # 마지막 이미지 다음 위치(캡션 포함 전)
        if len(run) == 1:
            seq += 1
            stem = re.sub(r'^\d+-', '', os.path.splitext(b['file'])[0]); ext = os.path.splitext(b['file'])[1]
            nf = '%02d-%s%s' % (seq, stem, ext)
            shutil.copy(os.path.join(outdir, b['file']), os.path.join(tmpdir, nf))
            nb = dict(b); nb.update(n=seq, file=nf); out.append(nb); files.append(nf)
            i += 1; continue
        # 합치기: 마지막 이미지의 캡션까지 흡수
        last_cap_end = run[-1]['cap_k'][1] if run[-1]['cap_k'] else end
        nums = [int(x) for r in run for x in re.findall(r'^이미지\s*(\d+)', r['cap'] or '')]
        span = ('이미지 %02d–%02d 묶음' % (nums[0], nums[-1])) if len(nums) >= 2 else ('%d장 묶음' % len(run))
        pages, cur, curh, curr = [], [], 0, []
        pshort = []
        for r in run:
            pim = _part_image(r, os.path.join(outdir, r['b']['file']))
            if cur and curh + GAP + pim.height > MERGE_MAXH:
                pages.append(cur); pshort.append(curr); cur, curh, curr = [], 0, []
            curh += (GAP if cur else 0) + pim.height; cur.append(pim); curr.append(r)
        pages.append(cur); pshort.append(curr)
        for pi, pg in enumerate(pages, 1):
            H = sum(x.height for x in pg) + GAP * (len(pg) - 1)
            canvas = Image.new('RGB', (MAXW, H), 'white'); y = 0
            for x in pg:
                canvas.paste(x, (0, y)); y += x.height + GAP
            seq += 1
            nf = '%02d-set%s.jpg' % (seq, ('-%d' % pi) if len(pages) > 1 else '')
            _save_jpeg(canvas, os.path.join(tmpdir, nf))
            lab = span + ((' (%d/%d)' % (pi, len(pages))) if len(pages) > 1 else '')
            rr = pshort[pi - 1]
            first = rr[0]['head'] or rr[0]['b'].get('short') or '이미지'
            first = first if len(first) <= 9 else first[:8] + '…'
            sh = '%s 외 %d장' % (first, len(rr) - 1) if len(rr) > 1 else first
            out.append(dict(kind='img', n=seq, file=nf, label=lab, merged=True, short=sh, count=len(rr)))
            files.append(nf)
        i = last_cap_end
    shutil.rmtree(outdir); os.rename(tmpdir, outdir)
    return out, files


def build(slug, entry):
    src = os.path.join(ROOT, 'naver-html', slug + '.html')
    soup = BeautifulSoup(open(src, encoding='utf-8').read(), 'html.parser')
    outdir = os.path.join(KIT, slug)
    if os.path.isdir(outdir):
        shutil.rmtree(outdir)
    os.makedirs(outdir)
    blocks, jobs, imgfiles = [], [], []
    n_img = 0

    def next_img():
        nonlocal n_img
        n_img += 1
        return n_img

    kids = [c for c in soup.body.find_all(recursive=False)]
    i = 0
    while i < len(kids):
        c = kids[i]
        cls = c.get('class') or []
        text = c.get_text(' ', strip=True).replace('\xa0', '').strip()
        if c.name == 'h1' or c.name == 'hr':
            pass
        elif c.name == 'div' and 'stat' in cls:
            group = [c]
            while i + 1 < len(kids) and kids[i + 1].name == 'div' and 'stat' in (kids[i + 1].get('class') or []):
                i += 1; group.append(kids[i])
            n = next_img()
            fn = '%02d-stat.png' % n
            jobs.append({'html': ''.join(str(g) for g in group), 'out': os.path.join(outdir, fn)})
            imgfiles.append(fn)
            blocks.append(dict(kind='img', n=n, file=fn, label='스탯 박스 3개(적정가격·분양가·예상 프리미엄)', short='핵심 수치 박스'))
        elif c.name == 'div':
            for sub in c.find_all(['div'], class_='stat'):
                pass
        elif c.name == 'table':
            ncol = max(len(r.find_all(['th', 'td'])) for r in c.find_all('tr'))
            if ncol > 4:
                WARN.append('%s: 표 열 %d개(>4) — 폰에서 글씨가 작을 수 있음' % (slug, ncol))
            n = next_img()
            fn = '%02d-table.png' % n
            jobs.append({'html': str(c), 'out': os.path.join(outdir, fn)})
            imgfiles.append(fn)
            blocks.append(dict(kind='img', n=n, file=fn, label='표(이미지로 넣기)', short='표'))
        elif c.name == 'img' or (c.name == 'p' and c.find('img')):
            im = c if c.name == 'img' else c.find('img')
            lp = local_image(slug, im.get('src', ''))
            n = next_img()
            if lp is None:
                WARN.append('%s: 이미지 파일 없음 %s' % (slug, im.get('src')))
                fn = None
            else:
                stem = os.path.splitext(os.path.basename(lp))[0]
                dst = save_image(lp, os.path.join(outdir, '%02d-%s' % (n, stem)))
                fn = os.path.basename(dst)
                imgfiles.append(fn)
            blocks.append(dict(kind='img', n=n, file=fn, label=htmllib.escape(im.get('alt', '') or '이미지'),
                               short=shortlabel(os.path.splitext(os.path.basename(lp))[0] if lp else '', im.get('alt', ''))))
        elif c.name in ('h2', 'h3') and text:
            blocks.append(dict(kind='text', tag=c.name, html=clean_inline(c)))
        elif c.name == 'p' and text:
            kind_note = 'note' in cls
            blocks.append(dict(kind='text', tag='note' if kind_note else 'p', html=clean_inline(c)))
        elif c.name == 'ul' or c.name == 'ol':
            for li in c.find_all('li'):
                blocks.append(dict(kind='text', tag='p', html='• ' + clean_inline(li)))
        i += 1

    render_fragments(jobs)
    n_before = len(imgfiles)
    blocks, imgfiles = merge_runs(slug, outdir, blocks)
    BEFORE_AFTER[slug] = (n_before, len(imgfiles))
    # zip
    zp = os.path.join(KIT, slug + '.zip')
    with zipfile.ZipFile(zp, 'w', zipfile.ZIP_DEFLATED) as z:
        for fn in imgfiles:
            z.write(os.path.join(outdir, fn), fn)

    title = entry.get('naver_title') or soup.find('h1').get_text(strip=True)
    tags = entry.get('naver_tags') or []
    cover = ', '.join(os.path.basename(c) for c in (entry.get('cover_candidates') or []))
    write_page(slug, entry, title, tags, cover, blocks, len(imgfiles), imgfiles)
    return len(blocks), len(imgfiles)


TAGLABEL = {'h2': '큰 소제목 — 굵게 + 큰 글씨', 'h3': '작은 소제목 — 굵게', 'p': '본문', 'note': '작은 회색 글씨(설명·메모)'}

CSS = """
:root{--ink:#111;--mut:#666;--hair:#ddd;--soft:#f5f5f5;--bg:#fff}
@media(prefers-color-scheme:dark){:root{--ink:#f2f2f2;--mut:#9a9a9a;--hair:#333;--soft:#161616;--bg:#000}}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.65 -apple-system,"Apple SD Gothic Neo","Malgun Gothic","Noto Sans KR",sans-serif;padding-bottom:24px}
.w{max-width:560px;margin:0 auto;padding:0 14px}
header{padding:18px 0 6px}h1{font-size:19px;line-height:1.35;margin:0 0 4px}.sub{color:var(--mut);font-size:13.5px}
.howto{border:1px solid var(--ink);background:var(--soft);padding:12px 14px;font-size:14.5px;margin:12px 0}
.howto ol{margin:6px 0 0;padding-left:20px}
.blk{border:1px solid var(--hair);margin:12px 0;padding:12px 12px 10px;background:var(--bg)}
.blk.done{opacity:.45}
.lab{display:flex;justify-content:space-between;align-items:center;gap:8px;font-size:12.5px;color:var(--mut);margin-bottom:8px}
.src{font-size:16px;word-break:keep-all;overflow-wrap:anywhere}
.src.h2{font-size:19px;font-weight:800}.src.h3{font-size:17px;font-weight:800}.src.note{font-size:13.5px;color:var(--mut)}
.btns{display:flex;gap:8px;align-items:center;margin-top:10px;flex-wrap:wrap}
.btn,.btn:visited{appearance:none;border:1.5px solid var(--ink);background:var(--ink);color:var(--bg);font:700 16px/1 inherit;padding:13px 18px;min-height:48px;display:inline-flex;align-items:center;justify-content:center;text-decoration:none;cursor:pointer;flex:1 1 0}
.btn.ghost{background:transparent;color:var(--ink)}
.btn.ok{background:#1b7a3a;border-color:#1b7a3a;color:#fff}
.chk{display:flex;align-items:center;gap:6px;font-size:14px;min-height:48px;color:var(--mut);white-space:nowrap}
.chk input{width:22px;height:22px;accent-color:#111}
.blk img{width:100%;height:auto;display:block;border:1px solid var(--hair)}
.hint{font-size:12.5px;color:var(--mut);margin-top:6px}
.list{border:1px solid var(--hair);margin:14px 0}.list a{display:block;padding:14px;border-bottom:1px solid var(--hair);color:inherit;text-decoration:none}.list a:last-child{border:0}.list small{color:var(--mut);display:block}
#bar[hidden]{display:none}#bar{position:fixed;left:0;right:0;bottom:0;background:var(--bg);border-top:1.5px solid var(--ink);padding:10px 14px calc(10px + env(safe-area-inset-bottom));z-index:9;font-size:14.5px;font-weight:700}
#bar i{display:block;height:6px;background:var(--hair);margin-top:6px}#bar i b{display:block;height:6px;background:var(--ink);width:0}
.sec{margin:20px 0}.sec>h2{font-size:17px;margin:0 0 6px}details.sec>summary{font-weight:800;font-size:16px;padding:12px;border:1px solid var(--hair);cursor:pointer}
.btn.big{font-size:18px;min-height:58px}.btn.sm{min-height:40px;font-size:14px;padding:8px 12px;flex:0 0 auto;margin-top:6px}
.prev{font-size:14px;border:1px solid var(--hair);padding:10px;margin-top:8px;max-height:420px;overflow:auto}.prev h2{font-size:16px;margin:8px 0 2px}.prev h3{font-size:15px;margin:6px 0 2px}.prev p{margin:4px 0}
.rows .row{display:flex;gap:10px;border:1px solid var(--hair);margin:8px 0;padding:8px}.rows img{width:92px;height:92px;object-fit:cover;object-position:top;border:1px solid var(--hair);flex:0 0 auto}
.rt{display:flex;flex-direction:column;min-width:0}.rt b{font-size:16px}.rt span{font-size:14px}.rt small{color:var(--mut);font-size:12px;overflow-wrap:anywhere}
.blk{overflow-wrap:anywhere}.final ul{margin:6px 0 0;padding-left:0;list-style:none}.final li{padding:8px 0;border-bottom:1px solid var(--hair)}
"""

JS = """
const KEY='naverkit:'+document.body.dataset.slug;let st={};try{st=JSON.parse(localStorage.getItem(KEY)||'{}')}catch(e){}
function upd(){const all=[...document.querySelectorAll('.blk[data-i]')].filter(b=>b.querySelector('.chk input'));const n=all.filter(b=>b.querySelector('.chk input').checked).length;if(!all.length)return;
document.getElementById('cnt').textContent=n+'/'+all.length+' 완료';document.querySelector('#bar i b').style.width=(100*n/all.length)+'%'}
document.querySelectorAll('.blk[data-i]').forEach(b=>{const cb=b.querySelector('.chk input');if(!cb)return;const k=b.dataset.i;
if(st[k]){cb.checked=true;b.classList.add('done')}
cb.addEventListener('change',()=>{b.classList.toggle('done',cb.checked);st[k]=cb.checked;try{localStorage.setItem(KEY,JSON.stringify(st))}catch(e){}upd()})});
upd();
async function copyBody(btn){const d=document.getElementById('prev');const el=document.getElementById('bodysrc');const html=el.innerHTML.trim();const text=JSON.parse(document.getElementById('bodyplain').textContent);let ok=false;
try{await navigator.clipboard.write([new ClipboardItem({'text/html':new Blob([html],{type:'text/html'}),'text/plain':new Blob([text],{type:'text/plain'})})]);ok=true}catch(e){}
if(!ok){const was=d.open;d.open=true;try{const r=document.createRange();r.selectNodeContents(el);const s=getSelection();s.removeAllRanges();s.addRange(r);ok=document.execCommand('copy');s.removeAllRanges()}catch(e){}d.open=was}
if(!ok){try{await navigator.clipboard.writeText(text);ok=true}catch(e){}}
const o=btn.textContent;btn.textContent=ok?'복사됨 ✓ 이제 에디터에 붙여넣으세요':'복사 실패 — 미리보기를 길게 눌러 전체 선택';btn.classList.toggle('ok',ok);setTimeout(()=>{btn.textContent=o;btn.classList.remove('ok')},2600)}
const CB=document.getElementById('copybody');if(CB)CB.addEventListener('click',()=>copyBody(CB));
const ALT=document.getElementById('alt');if(ALT)ALT.addEventListener('toggle',()=>{document.getElementById('bar').hidden=!ALT.open;document.body.style.paddingBottom=ALT.open?'84px':'24px'});
async function doCopy(btn){const b=btn.closest('.blk');const el=b.querySelector('.src');const html=el.innerHTML.trim();const text=el.innerText.trim();let ok=false;
try{await navigator.clipboard.write([new ClipboardItem({'text/html':new Blob([html],{type:'text/html'}),'text/plain':new Blob([text],{type:'text/plain'})})]);ok=true}catch(e){}
if(!ok){try{const r=document.createRange();r.selectNodeContents(el);const s=getSelection();s.removeAllRanges();s.addRange(r);ok=document.execCommand('copy');s.removeAllRanges()}catch(e){}}
if(!ok){try{await navigator.clipboard.writeText(text);ok=true}catch(e){}}
const o=btn.textContent;btn.textContent=ok?'복사됨 ✓':'복사 실패 — 글을 길게 눌러 직접 복사';btn.classList.toggle('ok',ok);
if(ok){const cb=b.querySelector('.chk input');if(cb&&!cb.checked){cb.checked=true;cb.dispatchEvent(new Event('change'))}}
setTimeout(()=>{btn.textContent=o;btn.classList.remove('ok')},1600)}
document.addEventListener('click',e=>{const t=e.target.closest('[data-copy]');if(t)doCopy(t)});
const SA=document.getElementById('saveall');
if(SA){const LAB=SA.textContent;SA.addEventListener('click',async()=>{const msg=document.getElementById('shmsg');const urls=JSON.parse(SA.dataset.files);
const fallback=(why)=>{msg.textContent=why+' zip을 대신 내려받습니다.';const a=document.createElement('a');a.href=SA.dataset.zip;a.download='';document.body.appendChild(a);a.click();a.remove()};
try{if(!navigator.canShare||!navigator.share){fallback('이 브라우저는 한꺼번에 저장 공유를 지원하지 않습니다.');return}
SA.textContent='이미지 준비 중…';const files=[];for(const u of urls){const r=await fetch(u);const b=await r.blob();files.push(new File([b],u.split('/').pop(),{type:b.type||'image/jpeg'}))}
if(!navigator.canShare({files})){SA.textContent=LAB;fallback('이 기기는 이 개수의 파일 공유를 허용하지 않습니다.');return}
await navigator.share({files,title:document.title});SA.textContent=LAB}
catch(err){SA.textContent=LAB;if(err&&err.name!=='AbortError')fallback('공유에 실패했습니다.')}})}
"""


CAPNUM = re.compile(r'^\s*이미지\s*\d+\s*[·.:\-]\s*')


def body_copy(blocks):
    """본문 전체 복사용 HTML/plain. 이미지 자리는 【사진 NN】 단독 문단(번호 = 저장된 파일 번호)."""
    H, T = [], []
    for b in blocks:
        if b['kind'] == 'img':
            lab = b.get('short') or '이미지'
            H.append('<p>&nbsp;</p><p><b>【사진 %02d】</b> · %s</p><p>&nbsp;</p>' % (b['n'], htmllib.escape(lab)))
            T.append('\n【사진 %02d】 · %s\n' % (b['n'], lab))
            continue
        plain = re.sub(r'<br\s*/?>', '\n', b['html']); plain = htmllib.unescape(re.sub(r'<[^>]+>', '', plain)).strip()
        if b['tag'] == 'h2':
            H.append('<p>&nbsp;</p><h2>%s</h2>' % b['html']); T.append('\n' + plain)
        elif b['tag'] == 'h3':
            H.append('<h3>%s</h3>' % b['html']); T.append(plain)
        elif b['tag'] == 'note':
            h = CAPNUM.sub('', b['html'])
            H.append('<p style="font-size:13px;color:#777">%s</p>' % h)
            T.append(CAPNUM.sub('', plain))
        else:
            H.append('<p>%s</p>' % b['html']); T.append(plain)
    return '\n'.join(H), re.sub(r'\n{3,}', '\n\n', '\n\n'.join(T)).strip()


def write_page(slug, entry, title, tags, cover, blocks, nimg, files=()):
    num = entry.get('number')
    idx = 0

    def chk(i):
        return '<label class="chk"><input type="checkbox"> 완료</label>'

    def text_block(label, html, tag='p', check=True):
        nonlocal idx
        idx += 1
        return ('<div class="blk" data-i="%d"><div class="lab"><span>%s</span></div>'
                '<div class="src %s">%s</div><div class="btns"><button class="btn" data-copy>복사</button>%s</div></div>'
                % (idx, label, tag, html, chk(idx) if check else ''))

    # 상단: 제목·태그
    top = [text_block('① 제목', htmllib.escape(title), 'p', False), text_block('② 태그 (쉼표로 구분 · # 없이)', htmllib.escape(','.join(tags)), 'p', False)]
    idx = 0
    # 본문 전체 복사
    bh, bt = body_copy(blocks)
    nph = sum(1 for b in blocks if b['kind'] == 'img' and b.get('file'))
    bodysec = ('<section class="sec"><h2>③ 본문 전체 복사</h2>'
               '<div class="hint">버튼 한 번으로 본문 전체를 복사합니다. 사진이 들어갈 자리는 <b>【사진 번호】</b> 줄로 표시되어 있습니다. 붙여넣은 뒤 그 줄을 찾아 같은 번호 사진을 넣으세요.</div>'
               '<div class="btns"><button class="btn big" id="copybody">본문 전체 복사 (자리표시 %d곳)</button></div>'
               '<details id="prev"><summary>붙여넣을 내용 미리보기</summary><div class="src prev" id="bodysrc">%s</div></details>'
               '<script type="application/json" id="bodyplain">%s</script></section>'
               % (nph, bh, json.dumps(bt, ensure_ascii=False).replace('</', '<\\/')))
    # 사진 자리표시 ↔ 파일
    files_json = htmllib.escape(json.dumps(['%s/%s' % (slug, f) for f in files], ensure_ascii=False), True)
    rows = []
    for b in blocks:
        if b['kind'] == 'img' and b.get('file'):
            rows.append('<div class="row"><img loading="lazy" src="%s/%s" alt=""><div class="rt"><b>【사진 %02d】</b><span>%s</span><small>%s</small>'
                        '<a class="btn sm" href="%s/%s" download>이미지 저장</a></div></div>'
                        % (slug, b['file'], b['n'], htmllib.escape(b.get('short') or ''), htmllib.escape(b['file']), slug, b['file']))
    photosec = ('<section class="sec"><h2>④ 사진 자리표시 ↔ 파일</h2>'
                '<div class="btns"><button class="btn big" id="saveall" data-files="%s" data-zip="%s.zip">이미지 전체 사진첩에 저장 (%d장)</button></div>'
                '<div class="btns"><a class="btn ghost" href="%s.zip" download>zip으로 받기</a></div>'
                '<div class="hint" id="shmsg">공유 기능이 없는 브라우저에서는 zip이 대신 내려받아집니다. 파일 이름 앞 번호가 【사진 번호】와 같습니다. PC에서도 같은 이미지를 사진 버튼으로 올리면 외부 링크가 아니라 네이버에 올라간 이미지가 됩니다.</div>'
                '<div class="rows">%s</div></section>' % (files_json, slug, len(files), slug, ''.join(rows)))
    # 대안: 블록별 복사
    alt = []
    for b in blocks:
        if b['kind'] == 'text':
            alt.append(text_block(TAGLABEL.get(b['tag'], '본문'), CAPNUM.sub('', b['html']) if b['tag'] == 'note' else b['html'], b['tag']))
        else:
            idx += 1
            if b.get('file'):
                body = ('<img src="%s/%s" alt="%s"><div class="btns"><a class="btn" href="%s/%s" download>이미지 저장</a>%s</div>'
                        % (slug, b['file'], htmllib.escape(b.get('short') or ''), slug, b['file'], chk(idx)))
            else:
                body = '<div class="hint">이미지 파일을 찾지 못했습니다.</div><div class="btns">%s</div>' % chk(idx)
            alt.append('<div class="blk" data-i="%d"><div class="lab"><span>【사진 %02d】 · 여기에 삽입</span><span>%s</span></div>%s</div>'
                       % (idx, b['n'], htmllib.escape(b.get('short') or ''), body))
    altsec = ('<details class="sec" id="alt"><summary>블록별 복사 (대안)</summary>'
              '<div class="hint">본문 전체 복사가 잘 안 될 때, 위에서부터 한 블록씩 복사해 붙여넣는 방법입니다. 완료 체크는 이 목록에서만 기록됩니다.</div>%s</details>'
              % ''.join(alt))
    final = ('<div class="blk final"><div class="lab"><span>⑥ 발행 체크리스트</span></div><ul>'
             '<li>카테고리: <b>부동산이야기</b></li><li>제목 · 태그 입력 확인</li>'
             '<li>대표 이미지(썸네일): %s</li><li>【사진】 자리표시 줄이 모두 지워지고 사진으로 바뀌었는지 훑어보기</li><li>발행 버튼</li></ul></div>'
             % htmllib.escape(cover or '첫 번째 이미지'))
    header = ('<header class="w"><div class="sub"><a href="index.html">← 키트 목록</a></div><h1>%s</h1>'
              '<div class="sub">청약 언박싱 No.%s · 사진 %d장</div></header>' % (htmllib.escape(title), num or '', nimg))
    howto = ('<div class="howto"><b>앱에서 올리는 법 (6단계)</b><ol>'
             '<li><b>제목 복사</b> → 새 글 제목에 붙여넣기</li><li><b>태그 복사</b> → 태그 칸에 붙여넣기</li>'
             '<li><b>본문 전체 복사</b> 후 본문에 붙여넣기</li>'
             '<li><b>이미지 전체 사진첩에 저장</b> (공유창에서 \'이미지 저장\')</li>'
             '<li>에디터에서 <b>【사진 번호】</b> 줄을 찾아 그 자리에서 사진 버튼 → 같은 번호 파일 선택 (자리표시 줄은 지우기)</li>'
             '<li>카테고리·대표이미지 확인 후 발행</li></ol></div>')
    page = ('<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<meta name="robots" content="noindex,nofollow"><title>네이버 발행 키트 · %s</title><style>%s</style></head>'
            '<body data-slug="%s">%s<main class="w">%s%s%s%s%s%s</main>'
            '<div id="bar" hidden><span id="cnt"></span><i><b></b></i></div><script>%s</script></body></html>'
            % (htmllib.escape(title), CSS, slug, header, howto, ''.join(top), bodysec, photosec, final, altsec, JS))
    open(os.path.join(KIT, slug + '.html'), 'w', encoding='utf-8').write(page)


def write_index(manifest):
    rows = []
    for e in manifest:
        s = e['slug']
        if os.path.exists(os.path.join(KIT, s + '.html')):
            rows.append((e.get('number') or 0, s, e.get('naver_title') or e.get('title') or s, bool(e.get('naver_published'))))
    rows.sort(reverse=True)
    items = ''.join('<a href="%s.html"><b>No.%s %s</b><small>%s</small></a>'
                    % (s, n, htmllib.escape(t), '발행 완료' if p else '발행 전') for n, s, t, p in rows)
    page = ('<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<meta name="robots" content="noindex,nofollow"><title>네이버 발행 키트</title><style>%s</style></head><body>'
            '<header class="w"><h1>네이버 발행 키트</h1><div class="sub">폰에서 복사·저장하며 올리는 용도</div></header>'
            '<main class="w"><div class="howto"><b>앱에서 올리는 법 (6단계)</b><ol>'
            '<li>글을 열고 <b>제목 복사</b> → 새 글 제목에 붙여넣기</li><li><b>태그 복사</b> → 태그 칸에 붙여넣기</li>'
            '<li><b>본문 전체 복사</b> 후 본문에 붙여넣기 (사진 자리는 【사진 번호】 줄로 표시)</li>'
            '<li><b>이미지 전체 사진첩에 저장</b> (공유창에서 \'이미지 저장\')</li>'
            '<li>에디터에서 <b>【사진 번호】</b> 줄을 찾아 그 자리에서 사진 버튼 → 같은 번호 파일 선택 (자리표시 줄은 지우기)</li>'
            '<li>카테고리·대표이미지 확인 후 발행</li></ol></div><div class="list">%s</div></main></body></html>'
            % (CSS, items))
    open(os.path.join(KIT, 'index.html'), 'w', encoding='utf-8').write(page)


def main(argv):
    os.makedirs(KIT, exist_ok=True)
    manifest = load_manifest()
    by = {e['slug']: e for e in manifest}
    if '--index-only' in argv:
        write_index(manifest); return
    if '--all' in argv:
        slugs = [e['slug'] for e in manifest if e.get('naver_html') and not e.get('naver_published')]
    else:
        slugs = [a for a in argv if not a.startswith('--')]
    for s in slugs:
        if s not in by:
            print('unknown slug', s); continue
        nb, ni = build(s, by[s])
        ba = BEFORE_AFTER.get(s, (ni, ni))
        print('%s: %d blocks, images %d -> %d' % (s, nb, ba[0], ba[1]))
    write_index(manifest)
    for w in WARN:
        print('WARN', w)


if __name__ == '__main__':
    main(sys.argv[1:])
