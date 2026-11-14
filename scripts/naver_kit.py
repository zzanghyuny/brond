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
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KIT = os.path.join(ROOT, 'naver-kit')
SITE = 'https://www.brandongsan.com/'
MAXW, MAXKB = 1000, 450
WARN = []


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
            blocks.append(dict(kind='img', n=n, file=fn, label='스탯 박스 3개(적정가격·분양가·예상 프리미엄)'))
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
            blocks.append(dict(kind='img', n=n, file=fn, label='표(이미지로 넣기)'))
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
            blocks.append(dict(kind='img', n=n, file=fn, label=htmllib.escape(im.get('alt', '') or '이미지')))
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
    # zip
    zp = os.path.join(KIT, slug + '.zip')
    with zipfile.ZipFile(zp, 'w', zipfile.ZIP_DEFLATED) as z:
        for fn in imgfiles:
            z.write(os.path.join(outdir, fn), fn)

    title = entry.get('naver_title') or soup.find('h1').get_text(strip=True)
    tags = entry.get('naver_tags') or []
    cover = ', '.join(os.path.basename(c) for c in (entry.get('cover_candidates') or []))
    write_page(slug, entry, title, tags, cover, blocks, len(imgfiles))
    return len(blocks), len(imgfiles)


TAGLABEL = {'h2': '큰 소제목 — 굵게 + 큰 글씨', 'h3': '작은 소제목 — 굵게', 'p': '본문', 'note': '작은 회색 글씨(설명·메모)'}

CSS = """
:root{--ink:#111;--mut:#666;--hair:#ddd;--soft:#f5f5f5;--bg:#fff}
@media(prefers-color-scheme:dark){:root{--ink:#f2f2f2;--mut:#9a9a9a;--hair:#333;--soft:#161616;--bg:#000}}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.65 -apple-system,"Apple SD Gothic Neo","Malgun Gothic","Noto Sans KR",sans-serif;padding-bottom:84px}
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
#bar{position:fixed;left:0;right:0;bottom:0;background:var(--bg);border-top:1.5px solid var(--ink);padding:10px 14px calc(10px + env(safe-area-inset-bottom));z-index:9;font-size:14.5px;font-weight:700}
#bar i{display:block;height:6px;background:var(--hair);margin-top:6px}#bar i b{display:block;height:6px;background:var(--ink);width:0}
.blk{overflow-wrap:anywhere}.final ul{margin:6px 0 0;padding-left:0;list-style:none}.final li{padding:8px 0;border-bottom:1px solid var(--hair)}
"""

JS = """
const KEY='naverkit:'+document.body.dataset.slug;let st={};try{st=JSON.parse(localStorage.getItem(KEY)||'{}')}catch(e){}
function upd(){const all=[...document.querySelectorAll('.blk[data-i]')];const n=all.filter(b=>b.querySelector('.chk input').checked).length;
document.getElementById('cnt').textContent=n+'/'+all.length+' 완료';document.querySelector('#bar i b').style.width=(100*n/all.length)+'%'}
document.querySelectorAll('.blk[data-i]').forEach(b=>{const cb=b.querySelector('.chk input');const k=b.dataset.i;
if(st[k]){cb.checked=true;b.classList.add('done')}
cb.addEventListener('change',()=>{b.classList.toggle('done',cb.checked);st[k]=cb.checked;try{localStorage.setItem(KEY,JSON.stringify(st))}catch(e){}upd()})});
upd();
async function doCopy(btn){const b=btn.closest('.blk');const el=b.querySelector('.src');const html=el.innerHTML.trim();const text=el.innerText.trim();let ok=false;
try{await navigator.clipboard.write([new ClipboardItem({'text/html':new Blob([html],{type:'text/html'}),'text/plain':new Blob([text],{type:'text/plain'})})]);ok=true}catch(e){}
if(!ok){try{const r=document.createRange();r.selectNodeContents(el);const s=getSelection();s.removeAllRanges();s.addRange(r);ok=document.execCommand('copy');s.removeAllRanges()}catch(e){}}
if(!ok){try{await navigator.clipboard.writeText(text);ok=true}catch(e){}}
const o=btn.textContent;btn.textContent=ok?'복사됨 ✓':'복사 실패 — 글을 길게 눌러 직접 복사';btn.classList.toggle('ok',ok);
if(ok){const cb=b.querySelector('.chk input');if(cb&&!cb.checked){cb.checked=true;cb.dispatchEvent(new Event('change'))}}
setTimeout(()=>{btn.textContent=o;btn.classList.remove('ok')},1600)}
document.addEventListener('click',e=>{const t=e.target.closest('[data-copy]');if(t)doCopy(t)});
"""


def write_page(slug, entry, title, tags, cover, blocks, nimg):
    num = entry.get('number')
    parts = []
    idx = 0

    def chk(i):
        return '<label class="chk"><input type="checkbox"> 완료</label>'

    def text_block(label, html, tag='p'):
        nonlocal idx
        idx += 1
        return ('<div class="blk" data-i="%d"><div class="lab"><span>%s</span></div>'
                '<div class="src %s">%s</div><div class="btns"><button class="btn" data-copy>복사</button>%s</div></div>'
                % (idx, label, tag, html, chk(idx)))

    parts.append(text_block('① 제목', htmllib.escape(title), 'p'))
    parts.append(text_block('② 태그 (쉼표로 구분 · # 없이)', htmllib.escape(','.join(tags)), 'p'))
    for b in blocks:
        if b['kind'] == 'text':
            parts.append(text_block(TAGLABEL.get(b['tag'], '본문'), b['html'], b['tag']))
        else:
            idx += 1
            if b['file']:
                body = ('<img src="%s/%s" alt="%s"><div class="btns"><a class="btn" href="%s/%s" download>이미지 저장</a>%s</div>'
                        '<div class="hint">저장이 안 되면 이미지를 길게 눌러 저장하세요.</div>'
                        % (slug, b['file'], b['label'], slug, b['file'], chk(idx)))
            else:
                body = '<div class="hint">이미지 파일을 찾지 못했습니다.</div><div class="btns">%s</div>' % chk(idx)
            parts.append('<div class="blk" data-i="%d"><div class="lab"><span>이미지 %02d · 여기에 삽입</span><span>%s</span></div>%s</div>'
                         % (idx, b['n'], b['label'], body))
    final = ('<div class="blk final"><div class="lab"><span>마지막 · 발행 체크리스트</span></div><ul>'
             '<li>카테고리: <b>부동산이야기</b></li><li>제목 · 태그 입력 확인</li>'
             '<li>대표 이미지(썸네일): %s</li><li>이미지가 순서대로 들어갔는지 훑어보기</li><li>발행 버튼</li></ul></div>'
             % htmllib.escape(cover or '첫 번째 이미지'))
    header = ('<header class="w"><div class="sub"><a href="index.html">← 키트 목록</a></div><h1>%s</h1>'
              '<div class="sub">청약 언박싱 No.%s · 이미지 %d장</div></header>' % (htmllib.escape(title), num or '', nimg))
    howto = ('<div class="howto"><b>폰에서 올리는 법</b><ol>'
             '<li>먼저 아래 <b>이미지 전체 받기(zip)</b>로 사진을 폰에 저장합니다.</li>'
             '<li>네이버 앱 글쓰기를 열고, 이 페이지에서 위에서부터 <b>[복사] → 앱에 붙여넣기</b>를 반복합니다.</li>'
             '<li>이미지 칸에서는 앱의 사진 추가로 같은 번호 사진을 넣습니다. 끝나면 맨 아래 체크리스트로 발행합니다.</li></ol>'
             '<div class="btns"><a class="btn ghost" href="%s.zip" download>이미지 전체 받기 (zip)</a></div></div>' % slug)
    page = ('<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<meta name="robots" content="noindex,nofollow"><title>네이버 발행 키트 · %s</title><style>%s</style></head>'
            '<body data-slug="%s">%s<main class="w">%s%s%s</main>'
            '<div id="bar"><span id="cnt"></span><i><b></b></i></div><script>%s</script></body></html>'
            % (htmllib.escape(title), CSS, slug, header, howto, ''.join(parts), final, JS))
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
            '<main class="w"><div class="howto"><b>3단계</b><ol><li>글을 고르고 이미지 zip을 폰에 저장</li>'
            '<li>[복사] → 네이버 앱 본문에 붙여넣기 (위에서부터 순서대로)</li>'
            '<li>이미지 칸마다 같은 번호 사진을 추가하고 마지막에 발행</li></ol></div><div class="list">%s</div></main></body></html>'
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
        print('%s: %d blocks, %d images' % (s, nb, ni))
    write_index(manifest)
    for w in WARN:
        print('WARN', w)


if __name__ == '__main__':
    main(sys.argv[1:])
