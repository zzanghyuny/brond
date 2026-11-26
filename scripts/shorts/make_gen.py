#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""단지별 30초 시네마틱 9:16 영상 생성기 (make_video.py 엔진 재사용)"""
import sys, numpy as np, subprocess, os
from PIL import Image, ImageDraw, ImageOps
import make_video as mv
import audio_orig, sfx, bridge_anim
from make_video import (ease, ease_out, draw_text, text_w, kenburns, hline, finish, overlay, push, grade,
                        W, H, FPS, CX, SAFE_L, SAFE_R, WHITE, GRAY, BG, BRASS)

import os
_IMGROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'posts', 'images') + '/'
CFG = {
 'armusee': dict(
    dir=_IMGROOT+'armusee-xi-ansan/', out='armusee-xi-ansan',
    name='아르뮤제자이', loc_txt='안산 성포동', avg=10.86, rng='층별 10.34 ~ 11.05억 · 세대수 가중평균',
    comps=[('힐스테이트중앙 · 고잔 · 2018.11', 9.20), ('안산파크푸르지오 · 성포동 · 2018.09', 7.65)],
    cvmax=11.0, fair=9.83, prem='-1.03억', pct='약 10%', gvmax=11.5,
    disc='브동산 모형 추정치 · 확정 수익 아님 · 84㎡ 평균 · 2026.11.13 기준',
    info=[('청약', '11월 23일 ~ 25일'), ('전매제한', '6개월'), ('계약금', '5%')],
    scenes=[('title',2.6),('aerial',3.6),('price',3.2),('comps',3.9),('gap',4.3),('layout',3.4),('map',3.4),('info',2.6),('end',3.0)],
    aerial=dict(img='aerial-cg.jpg', t1='안산 성포동', l1='지하 6층 ~ 지상 49층 · 6개 동', l2='아파트 984세대', src='조감도는 CG이며 실제와 다를 수 있음 · 출처: 공식 분양 홈페이지'),
    layout=dict(img='site-layout.jpg', title='단지 배치', cap='6개 동 · 중정형 조경 설계', c0=(0.5,0.30), c1=(0.52,0.42), z=(1.0,1.55), box=(820,860)),
    map=dict(title='입지', cap='중앙역 직선 약 1km', cap2='도보 15~20분 · 노적봉공원이 맞닿음'),
 ),
 'gyeonghuigung': dict(
    dir=_IMGROOT+'gyeonghuigung-efit/', out='gyeonghuigung-efit',
    name='경희궁 에피트', loc_txt='서울 종로구 교남동', avg=24.78, rng='층별 23.46 ~ 25.75억 · 세대수 가중평균',
    comps=[('경희궁자이 2단지 · 교남동 · 2017.02', 26.50), ('서울역센트럴자이 · 2017.08', 22.00)],
    cvmax=29.0, fair=21.71, prem='-3.06억', pct='약 14%', gvmax=27.0,
    disc='브동산 모형 추정치 · 확정 수익 아님 · 84㎡ 평균 · 2026.11.13 기준',
    info=[('청약', '11월 25일 ~ 30일'), ('전매제한', '최대 3년'), ('계약금', '10%')],
    scenes=[('title',2.6),('aerial',3.6),('price',3.2),('comps',3.9),('gap',4.3),('layout',3.4),('feature',3.4),('place',3.4),('info',2.6),('end',3.0)],
    aerial=dict(img='aerial-2.jpg', t1='서울 종로구 교남동', l1='지하 6층 ~ 지상 21층 · 3개 동', l2='일반분양 134세대', src='조감도는 CG이며 실제와 다를 수 있음 · 출처: 공식 분양 홈페이지'),
    layout=dict(img='site-layout.jpg', title='단지 배치', cap='사대문 안 재개발 · 3개 동', c0=(0.5,0.5), c1=(0.5,0.5), z=(1.0,1.3), box=(820,500)),
    feature=dict(img='community-b1.jpg', title='단지 커뮤니티', cap='지하 1층 주민공동시설', cap2='작은도서관 · 맘스카페 · 피트니스 · GX룸', c0=(0.5,0.5), c1=(0.5,0.5), z=(1.0,1.2), box=(820,680)),
    place=dict(img='environment-map-1000.jpg', title='입지', cap='사대문 안 도심 입지', cap2='서대문역 인근 · 공식 입지환경 지도', graded=False, box=(820,780)),
 ),
 'mullae': dict(
    dir=_IMGROOT+'mullae-harrington-place/', out='mullae-harrington-place',
    name='해링턴 플레이스 문래', name_px=72, loc_txt='서울 영등포구 문래동', avg=17.92, rng='층별 16.44 ~ 18.27억 · 세대수 가중평균',
    comps=[('영등포자이 디그니티 · 2026.03 (실거래)', 22.0), ('아크로타워스퀘어 · 2017.08', 20.65)],
    cvmax=24.0, fair=18.83, prem='+9,060만', pct='약 5%', gapword='낮음', gvmax=21.0, thumb_sub='분양가, 저평가일까?',
    plabel='84㎡ 평균 분양가',
    disc='브동산 모형 추정치 · 확정 수익 아님 · 84㎡ 평균 · 2026.11.13 기준',
    info=[('청약', '11월 23일 ~ 26일'), ('전매제한', '3년'), ('계약금', '10%')],
    scenes=[('title',2.6),('aerial',3.6),('price',3.2),('comps',3.9),('gap',4.3),('feature',3.4),('place',3.4),('info',2.6),('end',3.0)],
    aerial=dict(img='aerial-naver.jpg', t1='서울 영등포구 문래동', l1='지하 3층 ~ 지상 29층', l2='218세대 · 전 가구 전용 84㎡', src='조감도는 CG이며 실제와 다를 수 있음 · 출처: 언론 게재 이미지'),
    feature=dict(img='perspective-naver.jpg', title='단지 투시도', cap='지상 29층 · 문래동3가', cap2='투시도는 CG이며 실제와 다를 수 있음', c0=(0.5,0.78), c1=(0.5,0.30), z=(1.15,1.35), box=(700,860)),
    place=dict(img='location-official.jpg', title='입지', cap='영등포 도심권 · 지하철 생활권', cap2='공식 위치도 · GTX-B 계획은 변경될 수 있음', graded=False, box=(840,580)),
 ),
 'nonsan': dict(
    dir=_IMGROOT+'nonsan-elif-the-edition/', out='nonsan-elif-the-edition',
    name='엘리프 논산 디에디션', name_px=72, loc_txt='충남 논산시 내동', avg=5.05, rng='층별 4.38 ~ 5.32억 · 세대수 가중평균',
    comps=[('힐스테이트자이논산 · 내동 · 2019.01', 4.35), ('논산아이파크 · 2025.02', 4.10)],
    cvmax=5.0, fair=4.52, prem='-5,290만', pct='약 12%', gvmax=5.6,
    disc='브동산 모형 추정치 · 확정 수익 아님 · 84㎡ 평균 · 2026.11.13 기준',
    info=[('청약', '11월 23일 ~ 25일'), ('전매제한', '없음'), ('규제', '비규제지역')],
    scenes=[('title',2.6),('aerial',3.6),('price',3.2),('comps',3.9),('gap',4.3),('layout',3.4),('feature',3.4),('place',3.2),('info',2.6),('end',3.0)],
    aerial=dict(img='cover.jpg', t1='충남 논산시 내동', l1='지하 3층 ~ 지상 26층 · 8개 동', l2='499세대 · 전 세대 84㎡', src='조감도는 CG이며 실제와 다를 수 있음 · 출처: 공식 분양 홈페이지'),
    layout=dict(img='siteplan.jpg', title='단지 배치', cap='8개 동 · 중앙 조경 설계', c0=(0.5,0.45), c1=(0.52,0.5), z=(1.0,1.35), box=(820,680)),
    feature=dict(img='landscape.jpg', title='조경 특화', cap='시그니처 라운지 · 테라스 캠핑 가든', cap2='센트럴 웨이브 · 물놀이터 · 공식 홈페이지 CG', c0=(0.3,0.3), c1=(0.6,0.6), z=(1.0,1.35), box=(780,780)),
    place=dict(img='location.jpg', title='입지', cap='논산시청 약 560m · 내동 생활권', cap2='공식 위치도 · KTX 논산역 인근', graded=False, box=(800,760)),
 ),
 'gwangju': dict(
    dir=_IMGROOT+'gwangju-jeil-foredu/', out='gwangju-jeil-foredu',
    name='제일풍경채 광주 포에듀', name_px=64, loc_txt='경기 광주시 탄벌동', avg=6.71, rng='층별 6.03 ~ 6.91억 · 세대수 가중평균',
    ctitle='비교단지 실거래', csub='84㎡ 실거래 · 국토교통부 신고 기준',
    comps=[('두산위브광주센트럴파크 · 2024.10', 5.85), ('경남아너스빌1단지 · 2011.07', 4.23)],
    cvmax=7.0, fair=6.00, prem='-7,100만', pct='약 12%', gvmax=7.4,
    disc='브동산 모형 추정치 · 확정 수익 아님 · 84㎡ 평균 · 2026.11.06 공고 기준',
    info=[('청약', '11월 16일 ~ 18일'), ('전매제한', '6개월'), ('당첨 발표', '11월 24일')],
    scenes=[('title',2.6),('aerial',3.6),('price',3.2),('comps',3.9),('gap',4.3),('layout',3.4),('feature',3.4),('place',3.2),('info',2.6),('end',3.0)],
    aerial=dict(img='cover.jpg', t1='경기 광주시 탄벌동', l1='지하 2층 ~ 지상 29층 · 6개 동', l2='572세대 · 전 세대 84㎡', src='이미지는 CG이며 실제와 다를 수 있음 · 출처: 공식 분양 홈페이지'),
    layout=dict(img='siteplan.jpg', title='단지 배치', cap='6개 동 · 572세대', c0=(0.5,0.45), c1=(0.5,0.5), z=(1.0,1.3), box=(820,640)),
    feature=dict(img='community.jpg', title='단지 커뮤니티', cap='EDU ZONE · HEALTHY ZONE', cap2='공식 홈페이지 커뮤니티 안내', c0=(0.5,0.2), c1=(0.5,0.6), z=(1.0,1.0), box=(780,760)),
    place=dict(img='location.jpg', title='입지', cap='탄벌동 생활권', cap2='공식 위치도 · 교통·개발 계획은 변경될 수 있음', graded=False, box=(840,560)),
 ),
 'gyeongsan': dict(
    dir=_IMGROOT+'gyeongsan-richel-eduforet/', out='gyeongsan-richel-eduforet',
    name='리첼 에듀포레 경산역', name_px=64, loc_txt='경북 경산시 사정동', avg=6.03, rng='층별 5.91 ~ 6.38억 · 세대수 가중평균',
    comps=[('중방스타힐스 · 2023.09', 3.85), ('힐스테이트펜타힐즈 · 2021.03', 5.20)],
    cvmax=6.4, fair=4.83, prem='-1.19억', pct='약 25%', gvmax=6.8,
    disc='브동산 모형 추정치 · 확정 수익 아님 · 84㎡ 평균 · 2026.11.13 기준',
    info=[('청약', '11월 13일 ~ 17일'), ('전매제한', '없음'), ('당첨 발표', '11월 23일')],
    scenes=[('title',2.6),('aerial',3.6),('price',3.2),('comps',3.9),('gap',4.3),('layout',3.4),('feature',3.4),('place',3.2),('info',2.6),('end',3.0)],
    aerial=dict(img='aerial.jpg', t1='경북 경산시 사정동', l1='지하 2층 ~ 지상 29층 · 4개 동', l2='410세대 중 일반분양 201세대', src='조감도는 CG이며 실제와 다를 수 있음 · 출처: 공식 분양 홈페이지'),
    layout=dict(img='layout.jpg', title='단지 배치', cap='4개 동 · 410세대', c0=(0.5,0.5), c1=(0.5,0.5), z=(1.0,1.3), box=(840,500)),
    feature=dict(img='land.jpg', title='단지 조경', cap='단지 조경 특화', cap2='공식 홈페이지 CG · 실제와 다를 수 있음', c0=(0.5,0.5), c1=(0.55,0.45), z=(1.0,1.3), box=(820,620)),
    place=dict(img='location.jpg', title='입지', cap='경산역 역세권', cap2='공식 위치도 · 경산시장·NC백화점 인근', graded=False, box=(800,700)),
 ),
 'siheung': dict(
    dir=_IMGROOT+'siheung-geomo-artera/', out='siheung-geomo-artera',
    name='시흥 거모 아테라', loc_txt='경기 시흥시 거모동', avg=4.58, rng='59A · 59B · 59C 평균',
    plabel='59㎡ 평균 분양가', glabel='실제 분양가 (59㎡ 평균)',
    ctitle='비교단지 실거래', csub='59㎡ 실거래 · 국토교통부 신고 기준',
    comps=[('시흥장현예다음아르테 · 2022.12', 2.90), ('안산신길온천역휴먼빌 · 2005.07', 2.95)],
    cvmax=3.6, fair=3.59, prem='-9,900만', pct='약 28%', gvmax=5.0,
    disc='브동산 모형 추정치 · 확정 수익 아님 · 59㎡ 평균 · 2026.11.06 공고 기준',
    info=[('청약', '11월 26일 ~ 27일'), ('대상', '신혼부부 등'), ('당첨 발표', '12월 8일')],
    scenes=[('title',2.6),('aerial',3.6),('price',3.2),('comps',3.9),('gap',4.3),('layout',3.4),('feature',3.4),('place',3.2),('info',2.6),('end',3.0)],
    aerial=dict(img='cover.jpg', t1='경기 시흥시 거모동', l1='민간참여 공공분양 · 총 720세대', l2='신혼희망타운 본청약', src='조감도는 CG이며 실제와 다를 수 있음 · 출처: 공식 분양 홈페이지'),
    layout=dict(img='siteplan.jpg', title='단지 배치', cap='총 720세대 · 55㎡·59㎡', c0=(0.5,0.3), c1=(0.5,0.42), z=(1.0,1.3), box=(780,800)),
    feature=dict(img='community1.jpg', title='단지 커뮤니티', cap='주민공동시설 피트니스', cap2='공식 홈페이지 CG · 실제와 다를 수 있음', c0=(0.5,0.5), c1=(0.55,0.5), z=(1.0,1.25), box=(840,520)),
    place=dict(img='location.jpg', title='입지', cap='시흥 거모동 생활권', cap2='공식 입지환경 · 교통 계획은 변경될 수 있음', graded=False, c0=(0.5,0.2), c1=(0.5,0.3), z=(1.0,1.15), box=(760,820)),
 ),
 'iksan': dict(
    dir=_IMGROOT+'doosan-weve-trezium-iksan/', out='doosan-weve-trezium-iksan',
    name='두산위브 트레지움 익산', name_px=64, loc_txt='전북 익산시 동산동', avg=4.53, rng='층별 4.22 ~ 4.84억 · 세대수 가중평균',
    comps=[('익산풍경채어바니티 · 마동 · 2024.08', 4.25), ('익산자이그랜드파크 · 마동 · 2025.02', 4.75)],
    cvmax=5.4, fair=4.48, prem='-500만', pct='약 1%', gvmax=5.2, thumb_sub='분양가, 적정가와 거의 같다',
    disc='브동산 모형 추정치 · 확정 수익 아님 · 84㎡ 평균 · 2026.11.18 공고 기준',
    info=[('청약', '11월 23일 ~ 25일'), ('전매제한', '없음'), ('계약금', '5%')],
    scenes=[('title',2.6),('aerial',3.6),('price',3.2),('comps',3.9),('gap',4.3),('feature',3.6),('place',3.2),('info',2.6),('end',3.0)],
    aerial=dict(img='cover.jpg', t1='전북 익산시 동산동', l1='지하 2층 ~ 지상 27층 · 6개 동', l2='591세대 중 일반분양 251세대', src='조감도는 CG이며 실제와 다를 수 있음 · 출처: 공식 분양 홈페이지'),
    feature=dict(img='premium.jpg', title='분양 측 프리미엄', cap='교육 · 생활 · 설계 · 교통 · 직주 · 자연', cap2='분양 측 안내 · 공식 홈페이지', c0=(0.5,0.25), c1=(0.5,0.6), z=(1.0,1.0), box=(760,800)),
    place=dict(img='location-zoom.jpg', title='입지', cap='동산초 · 이리동중 인근', cap2='공식 위치도 · 거리와 위치는 실제와 다를 수 있음', graded=False, box=(800,800)),
 ),
 'gumi': dict(
    dir=_IMGROOT+'gumi-parkone-desian/', out='gumi-parkone-desian',
    name='구미 파크원 데시앙', name_px=76, loc_txt='경북 구미시 도량동', avg=5.18, rng='층별 4.91 ~ 5.26억 · 세대수 가중평균',
    comps=[('도량롯데캐슬골드파크 · 도량동 · 2019.04', 4.20), ('구미아이파크더샵 · 원평동 · 2023.11', 6.11)],
    cvmax=7.0, fair=5.45, prem='+2,730만', pct='약 5%', gapword='낮음', gvmax=6.2, thumb_sub='분양가, 저평가일까?',
    disc='브동산 모형 추정치 · 확정 수익 아님 · 84㎡ 평균 · 2026.11.18 공고 기준',
    info=[('청약', '11월 23일 ~ 25일'), ('전매제한', '없음'), ('계약금', '5%')],
    scenes=[('title',2.6),('aerial',3.6),('price',3.2),('comps',3.9),('gap',4.3),('layout',3.4),('feature',3.4),('place',3.2),('info',2.6),('end',3.0)],
    aerial=dict(img='aerial-cg.jpg', t1='경북 구미시 도량동', l1='지하 3층 ~ 지상 40층 · 10개 동', l2='1단지 1,355세대', src='조감도는 CG이며 실제와 다를 수 있음 · 출처: 공식 분양 홈페이지'),
    layout=dict(img='park-illust.jpg', title='공원 품은 단지', cap='도량동 공원 일대 1단지', cap2='분양 측 일러스트 · 실제와 다를 수 있음', c0=(0.5,0.5), c1=(0.6,0.45), z=(1.0,1.35), box=(840,560)),
    feature=dict(img='community.jpg', title='단지 커뮤니티', cap='피트니스 · 골프 · 사우나 · 키즈', cap2='공식 홈페이지 CG · 실제와 다를 수 있음', c0=(0.5,0.4), c1=(0.5,0.6), z=(1.0,1.2), box=(800,740)),
    place=dict(img='location-map.jpg', title='입지', cap='구미역 생활권 · 도량동', cap2='공식 위치도 · 거리와 위치는 실제와 다를 수 있음', graded=False, box=(800,720)),
 ),
 'goyang': dict(
    dir=_IMGROOT+'goyang-hanshin-thehue-firstone/', out='goyang-hanshin-thehue-firstone',
    name='고양 한신더휴 퍼스트원', name_px=64, loc_txt='경기 고양시 행신동', avg=8.08, rng='층별 7.78 ~ 8.46억 · 세대수 가중평균',
    comps=[('대곡역롯데캐슬엘클라씨 · 토당동 · 2022.12', 8.60), ('원흥호반베르디움더퍼스트 · 2017.09', 9.05)],
    cvmax=10.5, fair=8.68, prem='+5,960만', pct='약 7%', gapword='낮음', gvmax=9.8, thumb_sub='분양가, 저평가일까?',
    disc='브동산 모형 추정치 · 확정 수익 아님 · 84㎡ 평균 · 2026.11.19 공고 기준',
    info=[('청약', '11월 30일 ~ 12월 2일'), ('전매제한', '1년'), ('계약금', '5%')],
    scenes=[('title',2.6),('aerial',3.6),('price',3.2),('comps',3.9),('gap',4.3),('layout',3.6),('place',3.6),('info',2.6),('end',3.0)],
    aerial=dict(img='cover.jpg', t1='경기 고양시 행신동', l1='지하 2층 ~ 지상 17층 · 4개 동', l2='272세대 중 일반분양 102세대', src='조감도는 CG이며 실제와 다를 수 있음 · 출처: 공식 분양 홈페이지'),
    layout=dict(img='redevelop-aerial.jpg', title='행신 재건축 일대', cap='행신2의1구역 재건축', cap2='분양 측 개발 계획도 · 실제와 다를 수 있음', c0=(0.45,0.45), c1=(0.6,0.55), z=(1.0,1.35), box=(840,560)),
    place=dict(img='location.jpg', title='입지', cap='행신동 생활권 · 경의중앙선 인근', cap2='공식 위치도 · 교통 계획은 변경될 수 있음', graded=False, c0=(0.3,0.5), c1=(0.35,0.5), z=(1.3,1.5), box=(840,600)),
 ),
 'ulsan': dict(
    dir=_IMGROOT+'ulsan-hwajeong1-arel/', out='ulsan-arel',
    name='화정1지구 아르엘', loc_txt='울산 동구 화정동', avg=5.56, rng='층별 5.23 ~ 5.67억 · 세대수 가중평균',
    comps=[('힐스테이트이스턴베이 · 화정동 · 2015.12', 4.26), ('신영울산지웰시티자이1단지 · 서부동 · 2023.05', 5.81)],
    cvmax=6.6, fair=5.07, prem='-4,930만', pct='약 9%', gvmax=6.1,
    disc='브동산 모형 추정치 · 확정 수익 아님 · 84㎡ 평균 · 2026.11.13 기준',
    info=[('청약', '11월 23일 ~ 25일'), ('전매제한', '6개월'), ('계약금', '10%')],
    scenes=[('title',2.6),('aerial',3.6),('price',3.0),('comps',3.8),('gap',4.2),('layout',3.4),('feature',3.6),('place',3.2),('info',2.6),('end',3.0)],
    aerial=dict(img='aerial-cg.jpg', t1='울산 동구 화정동', l1='지하 3층 ~ 지상 24층 · 8개 동', l2='아파트 802세대', src='조감도는 CG이며 실제와 다를 수 있음 · 출처: 공식 분양 홈페이지'),
    layout=dict(img='site-layout.jpg', title='단지 배치', cap='8개 동 · 염포산 자락 단지', c0=(0.45,0.35), c1=(0.52,0.55), z=(1.0,1.45), box=(820,630)),
    feature=dict(img='plan-84a.jpg', title='84㎡ A타입', cap='84㎡ 580세대 · 전체의 72%', cap2='전 세대 팬트리 · 실내체육관 · 스카이라운지', c0=(0.5,0.25), c1=(0.5,0.45), z=(1.0,1.5), box=(760,700)),
    place=dict(img='aerial-wide.jpg', title='입지', cap='동구청 · 울산대병원 생활권', cap2='HD현대중공업 · 현대차 인접 (분양 측 안내)', graded=True),
 ),
 'choryang': dict(
    dir=_IMGROOT+'hoban-summit-choryang/', out='hoban-choryang',
    name='호반써밋 초량', loc_txt='부산 동구 초량3동', avg=7.25, rng='층별 6.65 ~ 7.47억 · 84A 가중평균',
    comps=[('범양레우스센트럴베이 · 초량동 · 2020.02', 5.70), ('두산위브 더제니스 하버시티 · 동구 · 2023.05', 7.15)],
    cvmax=8.0, fair=6.76, prem='-4,900만', pct='약 7%', gvmax=8.2,
    disc='브동산 모형 추정치 · 확정 수익 아님 · 84㎡A 평균 · 2026.11.13 기준',
    info=[('청약', '11월 23일 ~ 25일'), ('전매제한', '6개월'), ('계약금', '5%')],
    scenes=[('title',2.6),('loc',4.0),('price',3.0),('comps',3.8),('gap',4.2),('map',3.2),('feature',3.6),('info',2.6),('end',3.0)],
    loc=dict(img='location.jpg', title='위치', cap='1호선 초량역 도보 약 5분', cap2='분양 측 안내 · 부산 동구 초량3구역 재개발'),
    map=dict(title='입지', cap='초량역 약 360m (분양 측 안내)', cap2='같은 초량동 신축과 동구 대단지를 비교'),
    featlist=[('규모', '일반분양 236세대 · 총 432세대'), ('타입', '84㎡A 100세대'), ('주차', '세대당 1.25대'), ('시공·입주', '호반건설 · 2029년 8월')],
 ),
 'daejang': dict(
    dir=_IMGROOT+'bucheon-daejang-haustory-decent/', out='bucheon-daejang',
    name='부천대장 하우스토리 디센트', name_px=52, loc_txt='경기 부천시 오정구 대장동', avg=8.47, rng='8.03 ~ 8.54억 · 84A 가중평균 · 공공분양',
    plabel='84㎡A 평균 분양가', glabel='실제 분양가 (84㎡A 평균)',
    comps=[('부천 아이파크 · 약대동 · 2017.07', 6.85), ('계양효성해링턴플레이스 · 서운동 · 2021.01', 6.05)],
    cvmax=7.8, fair=7.91, prem='-5,640만', pct='약 7%', gvmax=9.2,
    disc='브동산 모형 추정치 · 확정 수익 아님 · 84㎡A 평균 · 2026.11.13 기준',
    info=[('청약', '11월 23일 ~ 25일'), ('전매제한', '3년'), ('거주의무', '3년')],
    scenes=[('title',2.6),('aerial',3.6),('price',3.0),('comps',3.8),('gap',4.2),('layout',3.4),('feature',3.6),('place',3.2),('info',2.6),('end',3.0)],
    aerial=dict(img='cover.jpg', t1='부천 오정구 대장동', l1='지하 2층 ~ 지상 15층 · 8개 동', l2='548세대 · 3기 신도시 공공분양', src='조감도는 CG이며 실제와 다를 수 있음 · 출처: 공식 분양 홈페이지'),
    layout=dict(img='site-plan.jpg', title='단지 배치', cap='저층 중심 8개 동 · 건폐율 22.95%', c0=(0.5,0.35), c1=(0.52,0.55), z=(1.0,1.4), box=(820,640)),
    feature=dict(img='community.jpg', title='단지 커뮤니티', cap='킨더센터 · 어린이집 · 다함께돌봄센터', cap2='계획 시설 · 공식 분양 홈페이지 안내', c0=(0.5,0.28), c1=(0.5,0.62), z=(1.0,1.0), box=(780,740)),
    place=dict(img='location.jpg', title='입지', cap='대장역(가칭) 인접 · 초품아 예정', cap2='예정 노선·학교는 개통·개교 전이며 변경될 수 있음', graded=False, box=(820,780)),
 ),
 'byeongjeom': dict(
    dir=_IMGROOT+'byeongjeom-bokhap-jubok1-public/', out='byeongjeom-bokhap-jubok1',
    name='병점복합타운 주복1블록', name_px=60, loc_txt='경기 화성시 병점동', avg=6.77, rng='층별 6.31 ~ 6.92억 · 84A 가중평균 · LH 공공분양',
    plabel='84㎡A 평균 분양가', glabel='실제 분양가 (84㎡A 평균)', csub='84㎡ 일반거래가 · 2026.11.20',
    comps=[('병점역아이파크캐슬 · 병점동 · 2021.03', 9.50), ('반정아이파크캐슬5단지 · 반정동 · 2022.12', 9.70)],
    cvmax=11.0, fair=9.48, prem='+2.70억', pct='약 29%', gapword='낮음', gvmax=10.5, thumb_sub='분양가, 저평가일까?', thumb_style='title',
    disc='브동산 모형 추정치 · 확정 수익 아님 · 84㎡A 평균 · 2026.11.26 기준',
    info=[('청약', '12월 7일 ~ 10일'), ('전매제한', '3년'), ('거주의무', '3년'), ('기금 융자', '9,000만 원 포함')],
    scenes=[('title',2.6),('aerial',3.6),('price',3.0),('comps',3.8),('gap',4.2),('layout',3.4),('feature',3.6),('place',3.2),('info',3.0),('end',3.0)],
    aerial=dict(img='cover.jpg', t1='경기 화성시 병점동', l1='최고 19~21층 · 6개 동 주상복합', l2='726세대 · LH 공공분양', src='조감도는 이미지컷이며 실제와 다를 수 있음 · 출처: LH 팸플릿'),
    layout=dict(img='siteplan.jpg', title='단지 배치', cap='6개 동 · 84㎡A는 42세대', c0=(0.5,0.40), c1=(0.5,0.55), z=(1.0,1.3), box=(820,640)),
    feature=dict(img='district-aerial.jpg', title='병점복합타운', cap='병점역 바로 옆 블록', cap2='지구 조감도 · 이미지컷 · 상업·업무용지는 아직 비어 있음', c0=(0.5,0.5), c1=(0.52,0.48), z=(1.0,1.25), box=(820,640)),
    place=dict(img='location-map.jpg', title='입지', cap='1호선 병점역 직선 약 360m', cap2='동탄~인덕원선 등은 공사 중 · 개통 시기 미확정', graded=False, box=(820,700)),
 ),
 # 2026.11.26 개정판: 느린 템포(slow) + 비교단지→보정→평균→적정가 브릿지 애니메이션. gap/comps 대신 bridge 한 장면.
 'firstworld': dict(
    dir=_IMGROOT+'thesharp-firstworld-seoul-officetel/', out='thesharp-firstworld-seoul-officetel', slow=True,
    name='더샵 퍼스트월드 서울', name_px=76, avg=9.80, rng='층별 8.31 ~ 11.11억 · 308실 가중평균 · 전 실 84㎡',
    plabel='오피스텔 84㎡ 평균 분양가', thumb_style='title', thumb_sub='분양가, 저평가일까?',
    disc='브동산 모형 추정치 · 확정 수익 아님 · 2026.11.26 공고 기준',
    info=[('청약', '12월 1일 하루'), ('청약통장', '필요 없음'), ('전매', '등기 전까지 불가'), ('입주', '2029년 8월')],
    scenes=[('title',3.4),('aerial',5.2),('price',4.8),('bridge',15.0),('feature',4.8),('place',4.8),('info',5.6),('end',4.2)],
    aerial=dict(img='cover.jpg', t1='서울 중랑구 상봉동', l1='옛 상봉터미널 · 지상 48층', l2='오피스텔 308실 · 전 실 84㎡', src='조감도는 이미지컷이며 실제와 다를 수 있음 · 출처: 공식 홈페이지'),
    feature=dict(img='tower-night.jpg', title='48층 랜드마크', cap='아파트 999가구와 한 단지', cap2='투시도 · 이미지컷 · 출처: 공식 홈페이지', c0=(0.5,0.35), c1=(0.5,0.5), z=(1.0,1.15), box=(620,860)),
    place=dict(img='location-map.jpg', title='입지', cap='7호선·경의중앙선 상봉역 앞', cap2='위치도 · 예정·계획 포함 · 출처: 공식 홈페이지', graded=False, box=(840,620)),
    bridge=dict(title='브동산 적정가는 이렇게', sub='비교 아파트 59m² KB시세(2026.11.20) → 평점·연령 보정 → 평균 → 오피스텔 감액', vmax=15,
        comps=[dict(name='e편한세상화랑대', meta='묵동 · 2017.12 준공 · 아파트 59m²', kb=10.00, mult=1.133, adj=11.33),
               dict(name='사가정센트럴아이파크', meta='면목동 · 2020.07 준공 · 아파트 59m²', kb=12.75, mult=1.073, adj=13.68)],
        avg=12.50, avg_label='두 보정가격 평균 (아파트 59m² 기준)', disc=dict(label='오피스텔 10% 감액', mult=0.9),
        fair=11.25, fair_label='브동산 적정가 (오피스텔 84m²)', price=9.80, price_label='평균 분양가 (308실 가중평균)',
        prem='+1.45억', judge='(저평가)', kind='plus'),
 ),
 'firstion': dict(
    dir=_IMGROOT+'gyeongbuk-docheong-prugio-firstion/', out='gyeongbuk-docheong-prugio-firstion', slow=True,
    name='경북도청 푸르지오 퍼스티온', name_px=60, avg=4.39, rng='층별 3.83 ~ 4.50억 · 1,165세대 가중평균',
    thumb_style='title', thumb_sub='분양가, 적정할까?', thumb_name_px=62,
    disc='브동산 모형 추정치 · 확정 수익 아님 · 2026.11.27 공고 기준',
    info=[('1순위', '12월 8일'), ('전매제한', '1년'), ('거주의무', '없음'), ('입주', '2029년 8월')],
    scenes=[('title',3.4),('aerial',5.2),('price',4.8),('bridge',15.0),('place',5.6),('info',5.6),('end',4.2)],
    aerial=dict(img='cover.jpg', t1='경북 예천군 호명읍', l1='도청신도시 2단계 · 지상 최고 25층', l2='1,165세대 · 전 세대 84㎡', src='조감도는 CG이며 실제와 다를 수 있음 · 출처: 공식 홈페이지'),
    place=dict(img='location.jpg', title='입지', cap='중앙공원 옆 2단계 첫 블록', cap2='개발계획도 · 계획 시설 포함 · 출처: 공식 홈페이지', graded=False, box=(900,540), z=(1.0,1.6), c0=(0.5,0.5), c1=(0.36,0.42)),
    map=dict(title='비교단지 위치', cap='하천 건너 1단계 대단지 2곳', cap2='브동산 자체 제작 개략도 · 축척은 개략적'),
    bridge=dict(title='브동산 적정가는 이렇게', sub='비교단지 84m² KB시세(2026.11.20) → 평점·연령 보정 → 평균', vmax=5.0,
        comps=[dict(name='호반베르디움2차', meta='호명읍 · 2017.11 준공 · 1,133세대', kb=3.45, mult=1.244, adj=4.29),
               dict(name='동일스위트더파크', meta='호명읍 · 2019.02 준공 · 1,499세대', kb=3.20, mult=1.253, adj=4.01)],
        avg=4.15, avg_label='두 보정가격 평균', fair=4.15, fair_label='브동산 적정가 (84m²)', price=4.39, price_label='평균 분양가 (1,165세대 가중평균)',
        prem='-2,440만', judge='(고평가)', kind='minus'),
 ),
 'songdo': dict(
    dir=_IMGROOT+'songdo-logebien-moaelgaa/', out='songdo-logebien-moaelgaa', slow=True,
    name='송도 대광로제비앙 모아엘가', name_px=56, avg=8.80, rng='층별 8.45 ~ 8.88억 · 592세대 가중평균',
    thumb_style='title', thumb_sub='분양가, 적정할까?', thumb_name_px=56,
    disc='브동산 모형 추정치 · 확정 수익 아님 · 2026.11.27 공고 기준',
    info=[('1순위', '12월 8일'), ('전매제한', '6개월'), ('재당첨제한', '없음'), ('입주', '2030년 1월')],
    scenes=[('title',3.4),('aerial',5.2),('price',4.8),('bridge',15.0),('feature',4.8),('place',5.2),('info',5.6),('end',4.2)],
    aerial=dict(img='aerial.jpg', t1='인천 송도 11공구 RC2블록', l1='지상 18~29층 · 7개 동', l2='592세대 · 전 세대 84㎡', src='조감도는 CG이며 실제와 다를 수 있음 · 출처: 공식 홈페이지'),
    feature=dict(img='perspective.jpg', title='워터프론트 앞', cap='수변 상가 · 송도 트램 정거장 계획', cap2='투시도 CG · 계획은 바뀔 수 있음 · 출처: 공식 홈페이지', c0=(0.45,0.45), c1=(0.55,0.5), z=(1.0,1.25), box=(820,560)),
    place=dict(img='location.jpg', title='입지', cap='인천1호선 역까지 직선 약 2.4km', cap2='공식 입지환경 · 트램·GTX-B는 계획·공사 단계', graded=False, box=(860,690), z=(1.0,1.35), c0=(0.5,0.5), c1=(0.68,0.42)),
    bridge=dict(title='브동산 적정가는 이렇게', sub='비교단지 84m² KB시세(2026.11.20) → 평점·연령 보정 → 평균', vmax=13.0,
        comps=[dict(name='롯데캐슬캠퍼스타운', meta='7공구 · 2016.03 준공 · 1,230세대', kb=7.75, mult=0.901, adj=6.98),
               dict(name='힐스테이트송도더스카이', meta='국제업무지구 · 2024.05 준공 · 1,205세대', kb=12.25, mult=0.836, adj=10.24)],
        avg=8.61, avg_label='두 보정가격 평균', fair=8.61, fair_label='브동산 적정가 (84m²)', price=8.80, price_label='평균 분양가 (592세대 가중평균)',
        prem='-1,870만', judge='(적정)', kind='even'),
 ),
}

def build(key):
    c = CFG[key]
    mv.IMG = c['dir']
    ld = lambda n: Image.open(c['dir'] + n).convert('RGB')
    DUR = sum(d for _, d in c['scenes'])
    mv.DUR = DUR
    disc = lambda img, a: draw_text(img, (CX, 1395), c['disc'], 28, GRAY, bold=0, alpha=a)

    def title(t):
        img = Image.new('RGB', (W, H), BG)
        hline(img, 880, CX - 280, CX + 280, ease_out((t - 0.2) / 1.1))
        draw_text(img, (CX, 700), '브동산', 46, BRASS, spacing=18, bold=1, alpha=ease((t - 0.7) / 0.7))
        px = c.get('name_px') or (118 if len(c['name']) <= 8 else 98)
        draw_text(img, (CX, 930 - 14 * (1 - ease_out((t - 1.0) / 0.9))), c['name'], px, WHITE, spacing=6, bold=2, alpha=ease((t - 1.0) / 0.8))
        draw_text(img, (CX, 1090 - 12 * (1 - ease_out((t - 1.5) / 0.9))), '예상프리미엄 분석', 70, WHITE, spacing=10, bold=1, alpha=ease((t - 1.5) / 0.8))
        hline(img, 1010, CX - 280, CX + 280, ease_out((t - 1.9) / 0.9), w=2)
        return img

    def aerial(t):
        a = c['aerial']; src = grade(ld(a['img']))
        img = Image.new('RGB', (W, H), BG); bh = 640
        img.paste(kenburns(src, W, bh, t / 4.0, 1.0, 1.3, 0.55, 0.55, 0.6, 0.45), (0, 560))
        d = ImageDraw.Draw(img); d.line((0, 560, W, 560), fill=BRASS, width=2); d.line((0, 560 + bh, W, 560 + bh), fill=BRASS, width=2)
        draw_text(img, (CX, 380), a['t1'], 66, WHITE, spacing=8, bold=1, alpha=ease((t - 0.3) / 0.8))
        draw_text(img, (CX, 1262), a['l1'], 44, WHITE, spacing=2, bold=0, alpha=ease((t - 1.0) / 0.8))
        draw_text(img, (CX, 1325), a['l2'], 56, BRASS, spacing=4, bold=1, alpha=ease((t - 1.5) / 0.8))
        draw_text(img, (CX, 1400), a['src'], 28, GRAY, bold=0, alpha=ease((t - 1.8) / 0.8))
        return img

    def photo_scene(spec, dark=0.85, graded=False, big=False):
        src = ld(spec['img'])
        if graded: src = grade(src)
        else: src = Image.fromarray(np.clip(np.asarray(src).astype(np.float32) * dark, 0, 255).astype(np.uint8))
        def f(t, L=1.0):
            img = Image.new('RGB', (W, H), BG)
            draw_text(img, (CX, 330), spec['title'], 52, BRASS, spacing=14, bold=1, alpha=ease(t / 0.6))
            bw, bh = spec.get('box', (820, 860))
            if graded: bw, bh = 880, 760
            m = kenburns(src, bw, bh, min(1, t / L), *( (spec['z'][0], spec['z'][1], *spec['c0'], *spec['c1']) if 'z' in spec else (1.0, 1.25, 0.5, 0.5, 0.52, 0.5)))
            x0, y0 = CX - bw // 2, 430
            img.paste(m, (x0, y0))
            d = ImageDraw.Draw(img); d.rectangle((x0, y0, x0 + bw, y0 + bh), outline=GRAY, width=1)
            yy = y0 + bh + 50
            draw_text(img, (CX, yy), spec['cap'], 50, WHITE, spacing=3, bold=1, alpha=ease((t - 0.7) / 0.7))
            if spec.get('cap2'):
                draw_text(img, (CX, yy + 78), spec['cap2'], 36, GRAY, bold=0, alpha=ease((t - 1.2) / 0.7))
            return img
        return f

    def price(t):
        img = Image.new('RGB', (W, H), BG)
        draw_text(img, (CX, 560), c.get('plabel', '84㎡ 평균 분양가'), 54, BRASS, spacing=10, bold=1, alpha=ease(t / 0.7))
        s_final = f"{c['avg']:0.2f}"
        wn = text_w(s_final, 230, 4); wu = text_w('억', 80)
        x0 = CX - (wn + 28 + wu) / 2
        v = c['avg'] * ease_out(t / 2.2)
        draw_text(img, (x0, 700), f'{v:0.2f}', 230, WHITE, anchor='l', spacing=4, bold=3)
        draw_text(img, (x0 + wn + 28, 820), '억', 80, WHITE, anchor='l', bold=2, alpha=ease((t - 0.4) / 0.6))
        hline(img, 1090, CX - 280, CX + 280, ease_out((t - 1.0) / 1.0), w=2)
        draw_text(img, (CX, 1130), c['rng'], 38, GRAY, bold=0, alpha=ease((t - 1.8) / 0.8))
        return img

    def comps(t):
        img = Image.new('RGB', (W, H), BG)
        draw_text(img, (CX, 420), c.get('ctitle', '비교단지 KB시세'), 54, BRASS, spacing=10, bold=1, alpha=ease(t / 0.7))
        draw_text(img, (CX, 495), c.get('csub', '84㎡ 일반거래가 · 2026.11.13'), 36, GRAY, bold=0, alpha=ease(t / 0.7))
        mv.bar(img, 760, c['comps'][0][0], c['comps'][0][1], c['cvmax'], (t - 0.8) / 1.4, (225, 222, 214), ease((t - 0.6) / 0.6))
        mv.bar(img, 1000, c['comps'][1][0], c['comps'][1][1], c['cvmax'], (t - 1.8) / 1.4, (150, 148, 142), ease((t - 1.6) / 0.6))
        draw_text(img, (CX, 1200), '신축 입주 시점과 점수 차이를 보정해 평균', 38, WHITE, bold=0, alpha=ease((t - 3.2) / 0.8))
        draw_text(img, (CX, 1260), '= 브동산 적정가격', 50, BRASS, spacing=6, bold=1, alpha=ease((t - 3.6) / 0.8))
        disc(img, ease((t - 1.0) / 1.0))
        return img

    def gap(t):
        img = Image.new('RGB', (W, H), BG)
        draw_text(img, (CX, 360), '예상 프리미엄', 54, BRASS, spacing=12, bold=1, alpha=ease(t / 0.7))
        mv.bar(img, 640, '브동산 적정가격', c['fair'], c['gvmax'], (t - 0.5) / 1.3, (225, 222, 214), ease((t - 0.4) / 0.6))
        mv.bar(img, 860, c.get('glabel', '실제 분양가 (84㎡ 평균)'), c['avg'], c['gvmax'], (t - 1.4) / 1.3, BRASS, ease((t - 1.3) / 0.6))
        k = ease((t - 2.8) / 1.0)
        draw_text(img, (CX, 1010 - 10 * (1 - k)), c['prem'], 190, WHITE, spacing=2, bold=3, alpha=k)
        draw_text(img, (CX, 1235), f"분양가가 적정가격보다 {c['pct']} {c.get('gapword', '높음')}", 44, WHITE, bold=0, alpha=ease((t - 3.4) / 0.8))
        disc(img, 1.0)
        return img

    def feature_list(t):
        img = Image.new('RGB', (W, H), BG)
        draw_text(img, (CX, 440), '단지 특징', 54, BRASS, spacing=14, bold=1, alpha=ease(t / 0.6))
        for i, (a, b) in enumerate(c['featlist']):
            y = 600 + i * 170
            p = ease((t - 0.35 - i * 0.4) / 0.6)
            hline(img, y - 20, SAFE_L + 20, SAFE_R - 20, p, GRAY, 1)
            draw_text(img, (SAFE_L + 40, y + 12), a, 40, GRAY, anchor='l', bold=0, alpha=p)
            draw_text(img, (SAFE_R - 40 - text_w(b, 46), y), b, 46, WHITE, anchor='l', bold=1, alpha=p)
        return img

    def info(t):
        img = Image.new('RGB', (W, H), BG)
        draw_text(img, (CX, 440), '청약 체크', 54, BRASS, spacing=14, bold=1, alpha=ease(t / 0.6))
        for i, (a, b) in enumerate(c['info']):
            y = 620 + i * 190
            p = ease((t - 0.35 - i * 0.45) / 0.6)
            hline(img, y - 20, SAFE_L + 20, SAFE_R - 20, p, GRAY, 1)
            draw_text(img, (SAFE_L + 40, y + 10), a, 42, GRAY, anchor='l', bold=0, alpha=p)
            draw_text(img, (SAFE_R - 40 - text_w(b, 62), y - 8), b, 62, WHITE, anchor='l', bold=1, alpha=p)
        disc(img, 1.0)
        return img

    def end(t):
        img = Image.new('RGB', (W, H), BG)
        draw_text(img, (CX, 640), '분양가는 숫자일 뿐,', 68, WHITE, spacing=4, bold=2, alpha=ease(t / 0.6))
        draw_text(img, (CX, 745), '판단은 청약자의 몫', 68, WHITE, spacing=4, bold=2, alpha=ease((t - 0.35) / 0.6))
        hline(img, 900, CX - 200, CX + 200, ease_out((t - 0.9) / 0.8))
        draw_text(img, (CX, 950), '더 궁금한 단지는 댓글로 남겨주세요', 44, BRASS, spacing=3, bold=1, alpha=ease((t - 1.3) / 0.7))
        draw_text(img, (CX, 1050), '숫자로 읽는 브동산', 40, GRAY, spacing=12, bold=0, alpha=ease((t - 1.8) / 0.7))
        disc(img, ease(t / 0.6))
        return img

    # 사진 장면: 원래 길이(L0)를 장면 길이로 정규화하기 위해 L=1.0 사용 → 장면 함수에 (lt*l0/len) 넘기므로 L0로 설정
    # 비교단지 KB → 평점·연령 보정 → 평균 → (감액) → 브동산 적정가 → 분양가와 차이. bridge_anim.py 공용.
    def _btext(img, xy, s, px, color, anchor='l', alpha=1.0, w='R', maxw=None):
        b = 0 if w == 'R' or px < 40 else 1      # WQY 획 두께: 작은 글씨는 굵게 하지 않는다(뭉개짐)
        if maxw:
            while px > 20 and text_w(s, px) > maxw: px -= 2
        x = xy[0] - text_w(s, px) if anchor == 'r' else xy[0]
        draw_text(img, (x, xy[1]), s, px, color, anchor='c' if anchor == 'c' else 'l', bold=b, alpha=alpha)
    BR = c.get('bridge')
    BRIDGE = bridge_anim.Bridge(BR, _btext, SAFE_L, SAFE_R, CX) if BR else None
    def bridge_T(ln):
        return bridge_anim.phase_times(BR, 0.4, max(6.0, ln - 4.0))
    def bridge_len(ln):                 # 단계 간격(GAP)을 지키도록 장면 길이를 늘린다
        return max(ln, bridge_T(ln)['end'] + 0.5)

    def mk(kind, ln=None):
        slow = c.get('slow')
        if kind == 'bridge':
            T = bridge_T(ln)
            def f(t):
                img = Image.new('RGB', (W, H), BG); BRIDGE.draw(img, t, T); disc(img, ease(t / 0.8)); return img
            return f, ln
        if slow and kind in ('layout', 'feature', 'place', 'loc') and kind in c:
            ph = photo_scene(c[kind], dark=0.8 if kind == 'loc' else 0.85,
                             graded=c[kind].get('graded', True) if kind == 'place' else False)
            return (lambda t: ph(t, ln)), ln     # 실제 초 단위로 그리고, 줌은 장면 전체에 걸쳐 천천히
        if slow and ln and kind in ('title', 'aerial', 'price', 'info', 'end'):
            fn, _ = mk(kind)
            return fn, ln                        # 늘리지 않음: 애니메이션은 원래 속도, 남는 시간은 머무름
        if kind == 'layout': return photo_scene(c['layout']), 3.0
        if kind == 'feature' and 'feature' in c: return photo_scene(c['feature']), 3.0
        if kind == 'feature': return feature_list, 3.0
        if kind == 'place': return photo_scene(c['place'], graded=c['place'].get('graded', True)), 3.0
        if kind == 'loc': return photo_scene(c['loc'], dark=0.8), 3.0
        if kind == 'map':
            mp = ImageOps.invert(Image.open(c['dir'] + 'chart-map-naver.png').convert('RGB'))
            sp = dict(title=c['map']['title'], cap=c['map']['cap'], cap2=c['map']['cap2'], box=(800, 800))
            def f(t):
                img = Image.new('RGB', (W, H), BG)
                draw_text(img, (CX, 330), sp['title'], 52, BRASS, spacing=14, bold=1, alpha=ease(t / 0.7))
                m = kenburns(mp, 800, 800, t / 4.0, 1.0, 1.06, 0.5, 0.5, 0.5, 0.52)
                img.paste(m, (CX - 400, 430))
                draw_text(img, (CX, 1270), sp['cap'], 54, WHITE, spacing=2, bold=1, alpha=ease((t - 0.9) / 0.8))
                draw_text(img, (CX, 1345), sp['cap2'], 36, GRAY, bold=0, alpha=ease((t - 1.4) / 0.8))
                return img
            return f, 4.0
        return {'title': (title, 3.0), 'aerial': (aerial, 4.0), 'price': (price, 4.0), 'comps': (comps, 4.4),
                'gap': (gap, 4.8), 'info': (info, 2.0), 'end': (end, 3.6)}[kind]

    scenes = []; cur = 0.0
    for kind, ln in c['scenes']:
        if kind == 'bridge': ln = bridge_len(ln)
        fn, l0 = mk(kind, ln)
        scenes.append((cur, cur + ln, fn, l0, kind)); cur += ln
    DUR = cur; mv.DUR = DUR
    XF = 0.45
    rise = [s for s, _, _, _, _ in scenes[1:]]
    mv.RISE = rise
    gi = [i for i, s in enumerate(scenes) if s[4] == 'gap']
    if gi:
        gi = gi[0]; reveal = scenes[gi][0] + 2.8 * (scenes[gi][1] - scenes[gi][0]) / 4.8
    else:                               # 브릿지: 예상 프리미엄이 뜨는 순간
        bi = [i for i, s in enumerate(scenes) if s[4] == 'bridge'][0]
        reveal = scenes[bi][0] + bridge_T(scenes[bi][1] - scenes[bi][0])['prem'] + 0.2
    mv.BOOM = [(reveal, 0.8), (scenes[-1][0], 0.5)]

    def render(i, t):
        s, e, fn, l0, kind = scenes[i]
        lt = t - s
        img = fn(lt * l0 / (e - s))
        if kind not in ('aerial', 'bridge'):
            img = push(img, lt, e - s)
        return img

    def frame(fi):
        t = fi / FPS
        idx = next((i for i, sc in enumerate(scenes) if sc[0] <= t < sc[1]), len(scenes) - 1)
        img = render(idx, t)
        e = scenes[idx][1]
        if idx + 1 < len(scenes) and e - t < XF:
            img = Image.blend(img, render(idx + 1, t), ease(1 - (e - t) / XF))
        img = overlay(img, t)
        fade = 1.0
        if t < 0.8: fade = ease(t / 0.8)
        if DUR - t < 0.9: fade = min(fade, ease((DUR - t) / 0.9))
        if fade < 1.0:
            img = Image.fromarray((np.asarray(img).astype(np.float32) * fade).astype(np.uint8))
        return finish(img, fi)
    return c, DUR, frame, scenes

def make_thumbnail(key, path):
    """썸네일(커버) 이미지 1080x1920: 대표 이미지를 어둡게 깔고 단지명·예상 프리미엄을 황동 포인트로."""
    from PIL import ImageFilter
    c = CFG[key]
    if c.get('thumb_style') == 'title':   # 검정 바탕 + 브동산 + 단지명 + '예상프리미엄 분석' (예전 인기 쇼츠 첫 화면 구도)
        img = Image.new('RGB', (W, H), BG)
        draw_text(img, (CX, 700), '브동산', 50, BRASS, spacing=18, bold=1)
        hline(img, 850, CX - 300, CX + 300, 1.0)
        px = c.get('thumb_name_px') or (118 if len(c['name']) <= 8 else (96 if len(c['name']) <= 10 else 76))
        draw_text(img, (CX, 910), c['name'], px, WHITE, spacing=4, bold=2)
        draw_text(img, (CX, 910 + px + 60), '예상프리미엄 분석', 70, (190, 186, 178), spacing=10, bold=1)
        img.save(path)
        return path
    ld = lambda n: Image.open(c['dir'] + n).convert('RGB')
    hero = c.get('aerial', {}).get('img') or c.get('loc', {}).get('img') or c.get('place', {}).get('img')
    src = grade(ld(hero), bright=0.55)
    bw = int(H * src.width / src.height)
    bg = src.resize((bw, H), Image.BICUBIC).crop(((bw - W) // 2, 0, (bw - W) // 2 + W, H))
    bg = bg.filter(ImageFilter.GaussianBlur(2))
    a = np.asarray(bg).astype(np.float32)
    yy = np.linspace(0, 1, H)[:, None, None]
    shade = 0.35 + 0.65 * np.clip(np.abs(yy - 0.5) * 2.2, 0, 1)   # 가운데는 밝게, 위아래는 어둡게
    a = a * (1 - 0.55 * shade) * 0.8
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    px = c.get('name_px') or (118 if len(c['name']) <= 8 else 98)
    px = int(px * 1.15) if len(c['name']) > 10 else int(px * 1.1)
    draw_text(img, (CX, 560), '브동산', 50, BRASS, spacing=20, bold=1)
    hline(img, 640, CX - 300, CX + 300, 1.0)
    draw_text(img, (CX, 700), c['name'], px, WHITE, spacing=4, bold=2)
    draw_text(img, (CX, 860), '예상 프리미엄', 60, WHITE, spacing=10, bold=1)
    draw_text(img, (CX, 960), c['prem'], 200, BRASS, spacing=2, bold=3)
    hline(img, 1230, CX - 300, CX + 300, 1.0)
    draw_text(img, (CX, 1270), c.get('thumb_sub', '분양가는 적정한 걸까?'), 54, WHITE, spacing=4, bold=1)
    img.save(path)
    return path

if __name__ == '__main__':
    key = sys.argv[1]; stills = [float(x) for x in sys.argv[2:]]
    if key.endswith('--thumb') or (stills == [] and False): pass
    c, DUR, frame, scenes = build(key)
    OUT = mv.OUT
    if stills:
        for s in stills: frame(int(s * FPS)).save(OUT + f'g_{key}_{s}.png')
        sys.exit()
    audio_orig.make_audio(OUT + f'audio_{key}_music.wav', DUR, mv.RISE, mv.BOOM)
    sfx.mix(OUT + f'audio_{key}_music.wav', OUT + f'audio_{key}.wav', sfx.build_events(scenes, mv.BOOM[0][0]))
    outp = OUT + f"{c['out']}-silent.mp4"
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
           '-c:v', 'libx264', '-preset', 'medium', '-crf', '21', '-maxrate', '10M', '-bufsize', '20M',
           '-pix_fmt', 'yuv420p', '-an', '-movflags', '+faststart', outp]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for fi in range(int(DUR * FPS)): p.stdin.write(np.asarray(frame(fi)).tobytes())
    p.stdin.close(); p.wait()
    final = OUT + f"{c['out']}-shorts.mp4"
    subprocess.run(['ffmpeg','-loglevel','error','-y','-i',outp,'-i',OUT+f'audio_{key}.wav','-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','192k','-t',str(DUR),'-movflags','+faststart',final],check=True)
    print('done', final)
    print('thumb', make_thumbnail(key, OUT + f"{c['out']}-thumbnail.png"))
