#!/usr/bin/env python3
"""쿠팡 파트너스 상품 카드(결론 아래 1칸)와 대가성 문구(바이라인 아래)를 포스팅에 넣는다.

대상: posts-data.js 기준
  - category "realestate" 중 "미분양 랭킹" 태그가 아닌 글 (청약 언박싱 등)
  - category "space" (공간이야기)
  - brand·vietnam, 미분양 랭킹 글은 넣지 않는다.

여러 번 실행해도 결과가 같다(이전에 넣은 블록을 지우고 다시 넣는다).
링크·문구를 바꾸려면 아래 LINKS / 문구만 고치고 다시 실행하면 된다.

사용: 저장소 루트에서  python3 scripts/coupang/apply_coupang.py [--dry-run]
      특정 파일만:      python3 scripts/coupang/apply_coupang.py posts/xxx.html
"""
import json, os, re, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

DISCLOSURE = "이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다."

# 쿠팡 파트너스 '간편 링크 만들기'로 만든 검색결과 링크 (2026.11.21 생성, 채널 기본값)
LINKS = [
    ("입주청소 용품", "https://link.coupang.com/a/iQzml1Xmqi"),
    ("이사박스", "https://link.coupang.com/a/iQznzWysyi"),
    ("암막커튼", "https://link.coupang.com/a/iQzozRnBEP"),
]

STYLE = """<style id="cp-style">
.cp-disclosure{margin:10px 0 0;font-size:12.5px;line-height:1.5;color:#555}
.cp-card{margin:40px 0 8px;padding:20px 22px;border:1px solid #E3E3E3;border-radius:12px;background:#FFF}
.cp-card .cp-badge{display:inline-block;font-size:11px;letter-spacing:.04em;color:#555;border:1px solid #E3E3E3;border-radius:999px;padding:3px 10px}
.cp-card .cp-title{margin:12px 0 4px;font-size:17px;font-weight:700;color:#111}
.cp-card .cp-desc{margin:0 0 14px;font-size:14px;color:#555;line-height:1.6}
.cp-card .cp-links{display:flex;flex-wrap:wrap;gap:8px}
.cp-card .cp-links a{display:inline-flex;align-items:center;gap:6px;padding:9px 16px;border:1px solid #111;border-radius:999px;color:#111;background:#FFF;font-size:14px;text-decoration:none}
.cp-card .cp-links a:hover{background:#111;color:#FFF}
.cp-card .cp-note{margin:14px 0 0;font-size:12px;color:#8A8A8A;line-height:1.5}
</style>"""

DISCLOSURE_HTML = f'<!--cp-disclosure:start--><p class="cp-disclosure">{DISCLOSURE}</p><!--cp-disclosure:end-->'

_links = "".join(
    f'<a href="{u}" target="_blank" rel="sponsored nofollow noopener">{t} <span aria-hidden="true">→</span></a>'
    for t, u in LINKS
)
CARD_HTML = (
    '<!--cp-card:start-->'
    '<aside class="cp-card" aria-label="쿠팡 파트너스 광고">'
    '<span class="cp-badge">AD · 쿠팡 파트너스</span>'
    '<p class="cp-title">새 집 입주 준비, 미리 챙겨 두면 좋은 것</p>'
    '<p class="cp-desc">입주 전후로 많이 찾는 품목을 쿠팡 검색 결과로 모았습니다.</p>'
    f'<div class="cp-links">{_links}</div>'
    f'<p class="cp-note">{DISCLOSURE}</p>'
    '</aside>'
    '<!--cp-card:end-->'
)

RE_BLOCKS = [
    re.compile(r'<style id="cp-style">.*?</style>\n?', re.S),
    re.compile(r"<!--cp-disclosure:start-->.*?<!--cp-disclosure:end-->", re.S),
    re.compile(r"<!--cp-card:start-->.*?<!--cp-card:end-->", re.S),
]


def load_posts():
    js = (
        "global.window={};const fs=require('fs');"
        "eval(fs.readFileSync('posts-data.js','utf8')+';global.P=POSTS;');"
        "console.log(JSON.stringify(P.map(p=>({url:p.url,category:p.category,tag:p.tag||''}))));"
    )
    out = subprocess.check_output(["node", "-e", js], cwd=ROOT, text=True)
    return json.loads(out)


def eligible(p):
    if p["category"] == "space":
        return True
    return p["category"] == "realestate" and "랭킹" not in p["tag"]


def strip(s):
    for r in RE_BLOCKS:
        s = r.sub("", s)
    return s


def card_position(s):
    """결론 섹션이 끝나는 곳. 없으면 관련 포스팅 섹션 바로 앞."""
    heads = [m for m in re.finditer(r"<h2[^>]*>(.*?)</h2>", s, re.S) if "결론" in re.sub("<[^>]+>", "", m.group(1))]
    if heads:
        end = s.find("</section>", heads[-1].end())
        if end != -1:
            return end + len("</section>"), "after-conclusion"
    i = s.find('<section id="related"')
    if i != -1:
        return i, "before-related"
    return None, "none"


def apply(path, dry):
    s0 = open(path, encoding="utf8").read()
    s = strip(s0)
    if "</head>" not in s:
        return "skip: no </head>"
    m = re.search(r'<div class="byline">.*?</div>', s, re.S)
    if not m:
        return "skip: no byline"
    pos, how = card_position(s)
    if pos is None:
        return "skip: no conclusion/related"
    # 뒤에서부터 넣어야 앞쪽 위치가 안 밀린다
    s = s[:pos] + CARD_HTML + s[pos:]
    s = s[: m.end()] + DISCLOSURE_HTML + s[m.end():]
    s = s.replace("</head>", STYLE + "\n</head>", 1)
    if s != s0 and not dry:
        open(path, "w", encoding="utf8").write(s)
    return how + ("" if s != s0 else " (unchanged)")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry = "--dry-run" in sys.argv
    posts = load_posts()
    targets = [p["url"] for p in posts if eligible(p)]
    if args:
        targets = [a for a in args]
    result = {}
    for t in targets:
        r = apply(os.path.join(ROOT, t), dry)
        result.setdefault(r, []).append(t)
    for k, v in result.items():
        print(f"{k}: {len(v)}")
        if k.startswith("skip") or k == "before-related":
            for x in v:
                print("   ", x)


if __name__ == "__main__":
    main()
