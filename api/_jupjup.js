// 브동산 미분양 줍줍 — 상담사 카드 결제 공통 모듈 (Vercel 서버 함수 전용, 파일명이 _로 시작해 공개 경로가 되지 않는다)
'use strict';
const PLANS = require('../jupjup/plans.json');
const DATA = require('../jupjup/data.json');

const ENV = {
  clientKey: process.env.TOSS_CLIENT_KEY || '',
  secretKey: process.env.TOSS_SECRET_KEY || '',
  ghToken: process.env.JUPJUP_GITHUB_TOKEN || '',
  repo: process.env.JUPJUP_GITHUB_REPO || 'zzanghyuny/brond',
  branch: process.env.JUPJUP_GITHUB_BRANCH || 'main',
};
const isTest = () => ENV.secretKey.startsWith('test_');
const ready = () => !!(ENV.clientKey && ENV.secretKey && ENV.ghToken) &&
  ENV.clientKey.slice(0, 5) === ENV.secretKey.slice(0, 5); // test/live 키를 섞어 쓰지 않게
const listFile = () => (isTest() ? 'jupjup/agents-test.json' : 'jupjup/agents.json');

function kstToday() {
  return new Date(Date.now() + 9 * 3600e3).toISOString().slice(0, 10);
}
function addDays(ymd, n) {
  const d = new Date(ymd + 'T00:00:00Z');
  d.setUTCDate(d.getUTCDate() + n);
  return d.toISOString().slice(0, 10);
}
function activeFor(list, site, today) {
  return (list || []).filter((a) => a && a.site === site && a.start <= today && today <= a.until);
}

const BANNED = /(보장|확정\s*수익|무조건|100\s*%|최저가\s*보장|로또)/;
const URLISH = /(https?:\/\/|www\.)/i;

// 입력 검증. 통과하면 정리된 값, 아니면 { error }
function validate(o) {
  const t = (v, n) => String(v == null ? '' : v).replace(/[\u0000-\u001f\u007f<>]/g, '').replace(/\s+/g, ' ').trim().slice(0, n);
  const site = DATA.sites.find((s) => s.key === o.site && s.status === 'open');
  if (!site) return { error: '선착순 분양 중인 단지를 다시 골라 주세요.' };
  const plan = PLANS.plans.find((p) => p.id === o.plan);
  if (!plan) return { error: '게재 기간을 다시 골라 주세요.' };
  const name = t(o.name, 20), company = t(o.company, 30), intro = t(o.intro, 40);
  const phone = String(o.phone || '').replace(/\D/g, '');
  const kakao = String(o.kakao || '').trim();
  if (!name || !company || !intro) return { error: '이름·소속·한 줄 소개를 모두 적어 주세요.' };
  if (URLISH.test(name + company + intro)) return { error: '이름·소속·소개에는 링크를 넣을 수 없습니다.' };
  if (BANNED.test(intro + company)) return { error: '수익·가격을 보장하는 표현은 쓸 수 없습니다.' };
  if (!/^0\d{8,10}$/.test(phone)) return { error: '휴대폰 번호를 확인해 주세요.' };
  if (kakao && !/^https:\/\/(open\.kakao\.com|pf\.kakao\.com)\/[A-Za-z0-9_\-/]+$/.test(kakao)) return { error: '카카오톡 링크는 open.kakao.com 주소만 쓸 수 있습니다.' };
  let photo = '';
  if (o.photo) {
    const m = /^data:image\/jpeg;base64,([A-Za-z0-9+/=]+)$/.exec(String(o.photo));
    if (!m) return { error: '사진 형식을 확인해 주세요.' };
    if (Buffer.from(m[1], 'base64').length > 250 * 1024) return { error: '사진이 너무 큽니다.' };
    photo = m[1];
  }
  if (!(o.agree_public && o.agree_role && o.agree_terms)) return { error: '동의 항목을 모두 확인해 주세요.' };
  return { site, plan, name, company, intro, phone, kakao, photo };
}

// ---- GitHub (카드 목록 = 저장소의 JSON 파일, 커밋하면 Vercel이 다시 배포)
async function gh(path, opt = {}) {
  const r = await fetch(`https://api.github.com/repos/${ENV.repo}${path}`, {
    ...opt,
    headers: {
      Authorization: `Bearer ${ENV.ghToken}`,
      Accept: 'application/vnd.github+json',
      'X-GitHub-Api-Version': '2022-11-28',
      'User-Agent': 'brandongsan-jupjup',
      ...(opt.body ? { 'Content-Type': 'application/json' } : {}),
    },
  });
  const text = await r.text();
  if (!r.ok) {
    const err = new Error(`GitHub ${r.status} ${path}: ${text.slice(0, 200)}`);
    err.status = r.status;
    throw err;
  }
  return text ? JSON.parse(text) : {};
}
async function readList(ref) {
  try {
    const j = await gh(`/contents/${listFile()}?ref=${ref}`);
    return JSON.parse(Buffer.from(j.content, 'base64').toString('utf8'));
  } catch (e) {
    if (e.status === 404) return [];
    throw e;
  }
}
async function headSha() {
  const ref = await gh(`/git/ref/heads/${ENV.branch}`);
  return ref.object.sha;
}

// 카드 한 장을 목록에 넣는 커밋 하나를 만든다. 다른 커밋과 겹치면 최대 3번 다시 시도.
async function publish(entry, photoB64, slots) {
  for (let i = 0; i < 3; i++) {
    const head = await headSha();
    const commit = await gh(`/git/commits/${head}`);
    const list = await readList(head);
    if (list.some((a) => a.id === entry.id)) return { dup: true, entry: list.find((a) => a.id === entry.id) };
    if (activeFor(list, entry.site, entry.start).length >= slots) return { full: true };
    list.push(entry);
    const tree = [{ path: listFile(), mode: '100644', type: 'blob', content: JSON.stringify(list, null, 1) + '\n' }];
    if (photoB64) {
      const blob = await gh('/git/blobs', { method: 'POST', body: JSON.stringify({ content: photoB64, encoding: 'base64' }) });
      tree.push({ path: entry.photo.replace(/^\//, ''), mode: '100644', type: 'blob', sha: blob.sha });
    }
    const t = await gh('/git/trees', { method: 'POST', body: JSON.stringify({ base_tree: commit.tree.sha, tree }) });
    const c = await gh('/git/commits', {
      method: 'POST',
      body: JSON.stringify({ message: `jupjup: 상담사 카드 게재 ${entry.site} (${entry.id})${isTest() ? ' [test]' : ''}`, tree: t.sha, parents: [head] }),
    });
    try {
      await gh(`/git/refs/heads/${ENV.branch}`, { method: 'PATCH', body: JSON.stringify({ sha: c.sha, force: false }) });
      return { ok: true, entry };
    } catch (e) {
      if (i === 2 || (e.status !== 422 && e.status !== 409)) throw e;
    }
  }
  throw new Error('publish retry exhausted');
}

// ---- 토스페이먼츠
function tossAuth() {
  return 'Basic ' + Buffer.from(ENV.secretKey + ':').toString('base64');
}
async function tossConfirm(paymentKey, orderId, amount) {
  const r = await fetch('https://api.tosspayments.com/v1/payments/confirm', {
    method: 'POST',
    headers: { Authorization: tossAuth(), 'Content-Type': 'application/json' },
    body: JSON.stringify({ paymentKey, orderId, amount }),
  });
  const j = await r.json().catch(() => ({}));
  return { ok: r.ok, data: j };
}
async function tossCancel(paymentKey, reason) {
  const r = await fetch(`https://api.tosspayments.com/v1/payments/${encodeURIComponent(paymentKey)}/cancel`, {
    method: 'POST',
    headers: { Authorization: tossAuth(), 'Content-Type': 'application/json' },
    body: JSON.stringify({ cancelReason: reason }),
  });
  return r.ok;
}

module.exports = { PLANS, DATA, ENV, isTest, ready, kstToday, addDays, activeFor, validate, gh, readList, headSha, publish, tossConfirm, tossCancel };
