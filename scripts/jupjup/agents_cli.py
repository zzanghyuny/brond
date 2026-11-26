#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""줍줍찬스 상담사 카드 — 계좌이체 신청 처리 도구 (정기 확인 작업이 사용).

  python3 scripts/jupjup/agents_cli.py hold <신청번호> <단지키>          입금 대기 칸 맡기(신청 후 depositHours까지)
  python3 scripts/jupjup/agents_cli.py release <신청번호>                칸 풀기(기한 초과·취소)
  python3 scripts/jupjup/agents_cli.py prune                             기한 지난 칸 정리
  python3 scripts/jupjup/agents_cli.py card <신청서.json> [--photo 경로] --check   카드 미리 검증만(게재 안 함)
  python3 scripts/jupjup/agents_cli.py card <신청서.json> [--photo 경로]           카드 게재(agents.json 추가, 맡은 칸 풀기)

신청서.json: {"id","site","plan","name","company","phone","kakao","intro","received"(메일 받은 시각 ISO)}
holds.json에는 개인정보 없이 단지·기한·신청번호만 둔다(공개 저장소).
"""
import os, sys, json, re, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
J = os.path.join(ROOT, 'jupjup')
PLANS = json.load(open(os.path.join(J, 'plans.json'), encoding='utf-8'))
KST = dt.timezone(dt.timedelta(hours=9))
BANNED = re.compile(r'(보장|확정\s*수익|무조건|100\s*%|최저가\s*보장|로또)')
URLISH = re.compile(r'(https?://|www\.)', re.I)
ID_RE = re.compile(r'^JJ\d{6}-[A-Z0-9]{4}$')


def load(name):
    p = os.path.join(J, name)
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else []


def save(name, data):
    open(os.path.join(J, name), 'w', encoding='utf-8').write(json.dumps(data, ensure_ascii=False, indent=1) + '\n')


def now():
    return dt.datetime.now(KST)


def active_agents(site):
    t = now().date().isoformat()
    return [a for a in load('agents.json') if a.get('site') == site and a['start'] <= t <= a['until']]


def active_holds(site=None, exclude=None):
    n = now()
    return [h for h in load('holds.json') if dt.datetime.fromisoformat(h['until']) > n
            and (site is None or h['site'] == site) and h.get('id') != exclude]


def sites():
    return {s['key']: s for s in json.load(open(os.path.join(J, 'data.json'), encoding='utf-8'))['sites']}


def hold(app_id, site, received=None):
    assert ID_RE.match(app_id), '신청번호 형식이 다릅니다'
    s = sites().get(site)
    assert s and s['status'] == 'open', f'열린 단지가 아닙니다: {site}'
    holds = load('holds.json')
    if any(h.get('id') == app_id for h in holds):
        print('이미 맡아 둔 신청', app_id); return True
    free = PLANS['slotsPerSite'] - len(active_agents(site)) - len(active_holds(site))
    if free <= 0:
        print('칸 없음', site); return False
    base = dt.datetime.fromisoformat(received) if received else now()
    until = (base + dt.timedelta(hours=PLANS['transfer']['depositHours'])).astimezone(KST).isoformat(timespec='minutes')
    holds.append({'id': app_id, 'site': site, 'until': until})
    save('holds.json', holds)
    print('칸 맡김', app_id, site, '~', until); return True


def release(app_id):
    holds = load('holds.json')
    save('holds.json', [h for h in holds if h.get('id') != app_id])
    print('칸 풂', app_id)


def prune():
    n = now()
    holds = load('holds.json')
    keep = [h for h in holds if dt.datetime.fromisoformat(h['until']) > n]
    save('holds.json', keep)
    print('정리', len(holds) - len(keep), '건')


def validate(o):
    errs = []
    if not ID_RE.match(o.get('id', '')): errs.append('신청번호')
    s = sites().get(o.get('site'))
    if not s or s['status'] != 'open': errs.append('단지')
    plan = next((p for p in PLANS['plans'] if p['id'] == o.get('plan')), None)
    if not plan: errs.append('게재 기간')
    for k, n in (('name', 20), ('company', 30), ('intro', 40)):
        v = str(o.get(k, '')).strip()
        if not v or len(v) > n or URLISH.search(v): errs.append(k)
    if BANNED.search(str(o.get('intro', '')) + str(o.get('company', ''))): errs.append('보장 표현')
    phone = re.sub(r'\D', '', str(o.get('phone', '')))
    if not re.match(r'^0\d{8,10}$', phone): errs.append('휴대폰')
    kakao = str(o.get('kakao', '') or '').strip()
    if kakao in ('없음', '-'): kakao = ''
    if kakao and not re.match(r'^https://(open\.kakao\.com|pf\.kakao\.com)/[A-Za-z0-9_\-/]+$', kakao): errs.append('카카오톡 링크')
    return errs, plan, phone, kakao


def card(path, photo=None, check=False):
    o = json.load(open(path, encoding='utf-8'))
    errs, plan, phone, kakao = validate(o)
    if errs:
        print('확인 필요:', ', '.join(errs)); return False
    if any(a['id'] == o['id'] for a in load('agents.json')):
        print('이미 게재된 신청', o['id']); return True
    if PLANS['slotsPerSite'] - len(active_agents(o['site'])) - len(active_holds(o['site'], exclude=o['id'])) <= 0:
        print('칸 없음 — 게재하지 않음'); return False
    start = now().date()
    entry = {'id': o['id'], 'site': o['site'], 'name': o['name'].strip(), 'company': o['company'].strip(),
             'phone': phone, 'kakao': kakao, 'intro': o['intro'].strip(), 'photo': '',
             'plan': plan['id'], 'start': start.isoformat(),
             'until': (start + dt.timedelta(days=plan['days'] - 1)).isoformat(), 'createdAt': now().isoformat(timespec='seconds')}
    if photo:
        from PIL import Image, ImageOps
        im = ImageOps.exif_transpose(Image.open(photo)).convert('RGB')
        s = min(im.size)
        im = im.crop(((im.width - s) // 2, (im.height - s) // 2, (im.width + s) // 2, (im.height + s) // 2)).resize((320, 320))
        out = os.path.join(J, 'agents', f"{o['id']}.jpg")
        if not check:
            os.makedirs(os.path.dirname(out), exist_ok=True)
            im.save(out, 'JPEG', quality=85)
        entry['photo'] = f"/jupjup/agents/{o['id']}.jpg"
    if check:
        print('검증 통과(게재 전):', json.dumps(entry, ensure_ascii=False)); return True
    agents = load('agents.json'); agents.append(entry); save('agents.json', agents)
    release(o['id'])
    print('게재', o['id'], o['site'], entry['start'], '~', entry['until']); return True


if __name__ == '__main__':
    a = sys.argv[1:]
    if not a:
        print(__doc__); sys.exit(1)
    cmd = a[0]
    if cmd == 'hold': ok = hold(a[1], a[2], a[3] if len(a) > 3 else None)
    elif cmd == 'release': release(a[1]); ok = True
    elif cmd == 'prune': prune(); ok = True
    elif cmd == 'card':
        photo = a[a.index('--photo') + 1] if '--photo' in a else None
        ok = card(a[1], photo, '--check' in a)
    else:
        print(__doc__); ok = False
    sys.exit(0 if ok else 1)
