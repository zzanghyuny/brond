#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
브동산 posts/<slug>.html -> 네이버 복사용 HTML 자동 변환기.
beodongsan-naver-copy 스킬 규칙을 그대로 코드화:
- 광고카드(#ad)/관련포스팅(#related) 제외
- map/radar/bridge SVG -> 실제 PNG(chart-map.png 등) <img>로 대체
- 표(table, dl.spec)는 진짜 <table>로
- stat-box는 template의 .stat div로
- 이미지 상대경로 -> https://www.brandongsan.com 절대경로
- 하단 광고카드 언급 문장 제거 + 새 문의 안내문 추가(같은 이메일, 광고 티 안 나게)
"""
import sys, os, re, copy
from bs4 import BeautifulSoup

SITE_BASE = "https://www.brandongsan.com"
NEW_EMAIL = "seodangdog81@gmail.com"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(SCRIPT_DIR, "..", "assets", "copy-template.html")

# 사용법: python3 build_naver_copies.py <repo-root> <out-dir> <slug1,slug2,...|--all>
#   --all이면 슬러그 목록을 표준입력(한 줄에 하나씩)으로 받는다.
# 예: python3 build_naver_copies.py /home/user/brond /tmp/naver-copies mokdong-yunseulxi,geomam-prugio-pravenue
#     grep -rl "청약 언박싱" /home/user/brond/posts/*.html | xargs -n1 basename -s .html | \
#       python3 build_naver_copies.py /home/user/brond /tmp/naver-copies --all
if len(sys.argv) < 4:
    print("사용법: python3 build_naver_copies.py <repo-root> <out-dir> <slug1,slug2,...|--all (stdin)>")
    sys.exit(1)

REPO = sys.argv[1]
OUT_DIR = sys.argv[2]
os.makedirs(OUT_DIR, exist_ok=True)


def _parse_fragment(tag):
    frag = BeautifulSoup(str(tag), "lxml")
    root = frag.find(tag.name) if tag.name != "[document]" else frag
    if root is None:
        return frag
    imgs = ([root] if root.name == "img" else []) + root.find_all("img")
    for img in imgs:
        src = img.get("src", "")
        if src and not src.startswith("http"):
            img["src"] = SITE_BASE + "/posts/" + src
        for k in list(img.attrs.keys()):
            if k not in ("src", "alt"):
                del img[k]
    all_els = [root] + root.find_all(True)
    for el in all_els:
        if el.name == "img":
            continue
        classes = el.get("class", [])
        keep_note = "note" in classes
        for k in list(el.attrs.keys()):
            del el[k]
        if keep_note:
            el["class"] = "note"
    return root


def outer_html(tag):
    root = _parse_fragment(tag)
    return str(root).strip()


def inner_html(tag):
    root = _parse_fragment(tag)
    return root.decode_contents().strip()


def render_stat_box(box):
    sk = box.select_one(".sk")
    sv = box.select_one(".sv")
    extra = box.select_one(".premium") or box.select_one(".delta")
    sk_text = sk.get_text(strip=True) if sk else ""
    sv_text = re.sub(r"\s+", " ", sv.get_text(strip=True)) if sv else ""
    html = f'<div class="stat"><div class="note">{sk_text}</div><div class="v">{sv_text}</div>'
    if extra:
        html += f"<div>{extra.get_text(strip=True)}</div>"
    html += "</div>"
    return html


RADAR_CAPTION = "차트: 입지·브랜드·상품성·연식 4개 축으로 본 SITE·비교단지 2곳 비교 레이더 차트 — 브동산 자체 산정"


def convert_section(section, slug, out):
    children = list(section.find_all(recursive=False))
    n = len(children)
    i = 0
    while i < n:
        el = children[i]
        name = el.name
        cls = el.get("class", []) if hasattr(el, "get") else []

        if name in ("h2", "h3"):
            out.append(outer_html(el))
        elif name == "p":
            out.append(outer_html(el))
        elif name == "div" and "stat-pair" in cls:
            for box in el.select(".stat-box"):
                out.append(render_stat_box(box))
        elif name == "div" and "map-wrap" in cls:
            img_url = f"{SITE_BASE}/posts/images/{slug}/chart-map.png"
            svg = el.find("svg")
            alt = svg.get("aria-label", "") if svg else ""
            out.append(f'<img src="{img_url}" alt="{alt}">')
            nxt = children[i + 1] if i + 1 < n else None
            if nxt is not None and getattr(nxt, "name", None) == "div" and "cover-cap" in nxt.get("class", []):
                out.append(f'<p class="note">{inner_html(nxt)}</p>')
                i += 1
        elif name == "div" and "radar-wrap" in cls:
            img_url = f"{SITE_BASE}/posts/images/{slug}/chart-radar.png"
            svg = el.find("svg")
            alt = svg.get("aria-label", "") if svg else ""
            out.append(f'<img src="{img_url}" alt="{alt}">')
            out.append(f'<p class="note">{RADAR_CAPTION}</p>')
        elif name == "div" and "bridge-wrap" in cls:
            img_url = f"{SITE_BASE}/posts/images/{slug}/chart-bridge.png"
            svg = el.find("svg")
            alt = svg.get("aria-label", "") if svg else ""
            out.append(f'<img src="{img_url}" alt="{alt}">')
            nxt = children[i + 1] if i + 1 < n else None
            if nxt is not None and getattr(nxt, "name", None) == "div" and "cover-cap" in nxt.get("class", []):
                out.append(f'<p class="note">{inner_html(nxt)}</p>')
                i += 1
        elif name == "div" and "tablewrap" in cls:
            table = el.find("table")
            if table:
                out.append(outer_html(table))
        elif name == "dl" and "spec" in cls:
            rows = []
            for row in el.select(".row"):
                dt = row.find("dt")
                dd = row.find("dd")
                dt_text = dt.get_text(strip=True) if dt else ""
                dd_html = inner_html(dd) if dd else ""
                rows.append(f"<tr><td>{dt_text}</td><td>{dd_html}</td></tr>")
            out.append("<table>\n<tbody>\n" + "\n".join(rows) + "\n</tbody>\n</table>")
        elif name == "ul":
            out.append(outer_html(el))
        elif name == "div" and "photo-block" in cls:
            img = el.find("img")
            if img:
                out.append(outer_html(img))
            nxt = children[i + 1] if i + 1 < n else None
            if nxt is not None and getattr(nxt, "name", None) == "div" and "cover-cap" in nxt.get("class", []):
                out.append(f'<p class="note">{inner_html(nxt)}</p>')
                i += 1
        elif name == "div" and "cover-cap" in cls:
            out.append(f'<p class="note">{inner_html(el)}</p>')
        elif name == "div" and "split" in cls:
            for box in el.select(".box"):
                for bc in box.find_all(recursive=False):
                    out.append(outer_html(bc))
        elif name == "div" and "note" in cls:
            out.append(f'<p class="note">{inner_html(el)}</p>')
        elif name == "div" and "quote" in cls:
            qt = el.select_one(".qt")
            p = el.find("p")
            qt_text = qt.get_text(strip=True) if qt else ""
            p_html = inner_html(p) if p else ""
            out.append(f'<div class="stat"><b>{qt_text}</b><div style="margin-top:8px;font-weight:400;font-size:15px;">{p_html}</div></div>')
        elif name == "div" and "bar-row" in cls:
            rows = []
            while i < n and getattr(children[i], "name", None) == "div" and "bar-row" in children[i].get("class", []):
                row = children[i]
                label = row.select_one(".bar-label")
                val = row.select_one(".bar-val")
                label_text = label.get_text(strip=True) if label else ""
                val_text = val.get_text(strip=True) if val else ""
                rows.append(f"<tr><td>{label_text}</td><td>{val_text}</td></tr>")
                i += 1
            out.append("<table>\n<tbody>\n" + "\n".join(rows) + "\n</tbody>\n</table>")
            continue
        elif name == "span" and "delta" in cls:
            out.append(f"<p><b>{el.get_text(strip=True)}</b></p>")
        else:
            out.append(f"<!-- UNHANDLED tag={name} class={cls} -->")
            out.append(outer_html(el))
        i += 1


def convert_post(slug):
    post_path = os.path.join(REPO, "posts", f"{slug}.html")
    soup = BeautifulSoup(open(post_path, encoding="utf-8").read(), "lxml")

    h1 = soup.select_one(".titleblock h1")
    title = h1.get_text(strip=True) if h1 else slug

    byline = soup.select_one(".byline")
    who = byline.select_one(".who").get_text(strip=True) if byline else "브동산"
    when = byline.select_one(".when").get_text(strip=True) if byline else ""
    tag = byline.select_one(".tag").get_text(strip=True) if byline else ""
    byline_text = f"{who} · {when} · {tag}"

    body = []

    cover = soup.select_one(".cover img")
    if cover:
        body.append(outer_html(cover))
        cover_div = soup.select_one(".cover")
        cap = cover_div.find_next_sibling("div", class_="cover-cap") if cover_div else None
        if cap:
            body.append(f'<p class="note">{inner_html(cap)}</p>')

    content = soup.select_one(".wrap.content")
    for section in content.find_all("section", recursive=False):
        sec_id = section.get("id", "")
        if sec_id in ("ad", "related"):
            continue
        convert_section(section, slug, body)

    footer_p = soup.select_one("footer p")
    disclaimer = ""
    if footer_p:
        disclaimer_full = inner_html(footer_p)
        disclaimer = disclaimer_full.split("하단 상담 카드는")[0].strip()

    ad_note = (
        f"이 단지 판매를 담당하는 팀장님 연락처가 필요하신 분은 아래 메일로 문의 남겨주시면 "
        f"확인 후 안내해드립니다. {NEW_EMAIL}"
    )

    template = open(TEMPLATE_PATH, encoding="utf-8").read()
    out_html = (
        template.replace("{{TITLE}}", title)
        .replace("{{BYLINE}}", byline_text)
        .replace("{{BODY}}", "\n\n".join(body))
        .replace("{{DISCLAIMER}}", disclaimer + "<br><br>" + ad_note)
    )

    out_path = os.path.join(OUT_DIR, f"{slug}-copy.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(out_html)

    unhandled = out_html.count("UNHANDLED")
    return out_path, unhandled


if __name__ == "__main__":
    slug_arg = sys.argv[3]
    if slug_arg == "--all":
        # 슬러그 목록을 표준입력(한 줄에 하나씩)으로 받는다
        slugs = [l.strip() for l in sys.stdin if l.strip()]
    else:
        slugs = slug_arg.split(",")
    total_unhandled = 0
    for slug in slugs:
        path, unhandled = convert_post(slug)
        flag = f"  !! UNHANDLED x{unhandled}" if unhandled else ""
        print(f"{slug} -> {path}{flag}")
        total_unhandled += unhandled
    print(f"\n총 {len(slugs)}편 변환 완료, UNHANDLED 총 {total_unhandled}건")
