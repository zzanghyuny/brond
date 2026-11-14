#!/usr/bin/env python3
"""비교단지 후보 스캔: 지역 키워드 + 브랜드로 KB 단지를 검색해 준공·세대수·대표 타입 KB 일반거래가를 표로 뽑는다.
사용: python3 scripts/beodongsan/comp_scan.py 안산 --area 84 [--min-year 2016] [--min-hh 500]
키워드는 '안산 푸르지오'처럼 구·동·브랜드를 섞어 여러 개 줄 수 있다(--kw 반복). 결과는 시세 오래된 순서가 아니라 세대수·준공·가격 표다.
KB 미등록·일반거래가 없는 단지는 가격 칸이 None이다(그 경우 국토부 실거래 신고로 보완)."""
import sys, argparse, os
sys.path.insert(0, os.path.dirname(__file__))
from kb import search
import kb_detail as k

BRANDS = ['자이', '푸르지오', '힐스테이트', '래미안', '아이파크', '더샵', 'e편한세상', '롯데캐슬', 'SK뷰', '포레나', '호반', '센트레빌', '쌍용', '위브']

def scan(region, area=84, min_year=2016, min_hh=500, extra=()):
    kws = [region] + [f'{region} {b}' for b in BRANDS] + list(extra)
    seen, rows = set(), []
    for kw in kws:
        try:
            res = search(kw)
        except Exception:
            continue
        for no, nm, ad in res:
            if no in seen or not ad or region not in ad:
                continue
            seen.add(no)
            try:
                i = k.info(no)
                ym = str(i['준공년월'])
                if int(ym[:4]) < min_year or int(i['총세대수'] or 0) < min_hh:
                    continue
                price = None
                for t in k.types(no):
                    if area - 1.5 <= float(t[1]) <= area + 1.5:
                        s = k.sise(no, t[0])
                        if s and s[0][1]:
                            price = (s[0][1] / 10000, s[0][3]); break
                rows.append((nm, ad, ym, i['총세대수'], i['시공사명'], price))
            except Exception:
                continue
    return sorted(rows, key=lambda r: (r[5] is None, -(r[5][0] if r[5] else 0)))

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('region'); ap.add_argument('--area', type=float, default=84)
    ap.add_argument('--min-year', type=int, default=2016); ap.add_argument('--min-hh', type=int, default=500)
    ap.add_argument('--kw', action='append', default=[])
    a = ap.parse_args()
    for nm, ad, ym, hh, bd, p in scan(a.region, a.area, a.min_year, a.min_hh, a.kw):
        print(f'{nm} | {ad} | {ym} | {hh}세대 | {bd} | {a.area:.0f}㎡ KB일반 {p[0]:.2f}억 ({p[1]})' if p else f'{nm} | {ad} | {ym} | {hh}세대 | {bd} | KB일반거래가 없음')
