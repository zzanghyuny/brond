// POST /api/jupjup-confirm — 토스 결제 승인 → 상담사 카드 게재
// 순서: 입력 검증 → 빈 칸 확인 → 결제 승인(금액은 서버의 plans.json 기준) → 목록 커밋. 게재에 실패하면 결제를 바로 취소한다.
'use strict';
const J = require('./_jupjup');

function send(res, code, body) {
  res.statusCode = code;
  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  res.setHeader('Cache-Control', 'no-store');
  res.end(JSON.stringify(body));
}

module.exports = async (req, res) => {
  if (req.method !== 'POST') return send(res, 405, { error: 'POST만 받습니다.' });
  if (!J.ready()) return send(res, 503, { error: '결제 준비 중입니다. 잠시 뒤 다시 시도해 주세요.' });

  let body = req.body;
  if (typeof body === 'string') { try { body = JSON.parse(body); } catch (e) { body = null; } }
  if (!body || typeof body !== 'object') return send(res, 400, { error: '요청 형식이 올바르지 않습니다.' });

  const { paymentKey, orderId } = body;
  const amount = Number(body.amount);
  const order = body.order || {};
  if (typeof paymentKey !== 'string' || !paymentKey || paymentKey.length > 200) return send(res, 400, { error: '결제 정보가 없습니다.' });
  if (typeof orderId !== 'string' || !/^jj[0-9]{8}-[a-z0-9]{10}$/.test(orderId) || order.orderId !== orderId) {
    return send(res, 400, { error: '주문 번호가 올바르지 않습니다.' });
  }

  const v = J.validate(order);
  if (v.error) return send(res, 400, { error: v.error + ' (결제는 확정되지 않았습니다)' });
  if (amount !== v.plan.price) return send(res, 400, { error: '결제 금액이 상품 가격과 다릅니다. (결제는 확정되지 않았습니다)' });

  const today = J.kstToday();
  const slots = J.PLANS.slotsPerSite;
  const entry = {
    id: orderId,
    site: v.site.key,
    name: v.name,
    company: v.company,
    phone: v.phone,
    kakao: v.kakao,
    intro: v.intro,
    photo: v.photo ? `/jupjup/agents/${orderId}.jpg` : '',
    plan: v.plan.id,
    start: today,
    until: J.addDays(today, v.plan.days - 1),
    createdAt: new Date().toISOString(),
  };

  // 1) 이미 처리된 주문인지, 빈 칸이 있는지 — 결제 승인 전에 확인(없으면 승인하지 않아 청구되지 않는다)
  try {
    const list = await J.readList(await J.headSha());
    const dup = list.find((a) => a.id === orderId);
    if (dup) return send(res, 200, { ok: true, test: J.isTest(), entry: dup, already: true });
    if (J.activeFor(list, entry.site, today).length >= slots) {
      return send(res, 409, { error: '그 사이 이 단지의 상담사 카드 칸이 모두 찼습니다. 결제는 확정되지 않았습니다.' });
    }
  } catch (e) {
    console.error('precheck', e);
    return send(res, 502, { error: '게재 목록을 확인하지 못했습니다. 결제는 확정되지 않았습니다. 잠시 뒤 다시 시도해 주세요.' });
  }

  // 2) 결제 승인
  const c = await J.tossConfirm(paymentKey, orderId, v.plan.price);
  if (!c.ok) {
    const msg = (c.data && c.data.message) || '결제 승인에 실패했습니다.';
    return send(res, 400, { error: msg, code: c.data && c.data.code });
  }
  if (c.data.status !== 'DONE' || Number(c.data.totalAmount) !== v.plan.price || c.data.orderId !== orderId) {
    await J.tossCancel(paymentKey, '결제 정보 불일치로 자동 취소');
    return send(res, 400, { error: '결제 정보가 맞지 않아 자동으로 취소했습니다.' });
  }

  // 3) 게재(커밋). 실패하면 결제 취소
  try {
    const r = await J.publish(entry, v.photo, slots);
    if (r.full) {
      const refunded = await J.tossCancel(paymentKey, '상담사 카드 칸 마감으로 자동 취소');
      return send(res, 409, { error: '그 사이 칸이 모두 찼습니다. ' + (refunded ? '결제를 바로 취소했습니다.' : '결제 취소를 처리 중이니 문의 페이지로 알려 주세요.'), refunded });
    }
    return send(res, 200, { ok: true, test: J.isTest(), entry: r.entry, already: !!r.dup, receipt: c.data.receipt && c.data.receipt.url });
  } catch (e) {
    console.error('publish', e);
    const refunded = await J.tossCancel(paymentKey, '게재 처리 오류로 자동 취소');
    return send(res, 500, { error: '게재 중 오류가 났습니다. ' + (refunded ? '결제를 바로 취소했습니다.' : '결제 취소를 처리 중이니 문의 페이지로 알려 주세요.'), refunded });
  }
};
