/* 브동산 줍줍찬스 — 상담사 카드 등록·결제·게재 확인 */
(function () {
  'use strict';
  var J = window.JJ;
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var BANNED = /(보장|확정\s*수익|무조건|100\s*%|최저가\s*보장|로또)/;
  var URLISH = /(https?:\/\/|www\.)/i;
  function won(n) { return Number(n).toLocaleString('ko-KR') + '원'; }
  function getConfig() {
    return fetch('/api/jupjup-config', { cache: 'no-store' }).then(function (r) { return r.ok ? r.json() : null; }).catch(function () { return null; });
  }

  // ================= 등록 폼
  var f = $('[data-agent-form]');
  if (f) {
    var msg = $('[data-msg]'), btn = $('[data-pay]'), totalEl = $('[data-total]'), preview = $('[data-preview]');
    var slotsMsg = $('[data-slots-msg]'), banner = $('[data-mode]');
    var plans = null, agents = [], cfg = null, photoData = '', busy = false;
    var qs = new URLSearchParams(location.search);
    if (qs.get('site')) { f.site.value = qs.get('site'); }

    function say(t, err) { msg.textContent = t || ''; msg.className = 'jj-msg' + (err ? ' err' : ''); }
    function plan() {
      var id = (f.querySelector('input[name=plan]:checked') || {}).value;
      return plans && plans.plans.filter(function (p) { return p.id === id; })[0];
    }
    function free() {
      if (!plans || !f.site.value) return 0;
      var used = J.activeAgents(agents).filter(function (a) { return a.site === f.site.value; }).length;
      return plans.slotsPerSite - used;
    }
    function refresh() {
      var p = plan();
      if (p) totalEl.textContent = won(p.price);
      var fr = free();
      if (plans && f.site.value) {
        slotsMsg.textContent = fr > 0 ? '이 단지는 ' + plans.slotsPerSite + '칸 중 ' + fr + '칸이 비어 있습니다.' : '이 단지는 칸이 모두 찼습니다. 다른 단지를 골라 주세요.';
      } else slotsMsg.textContent = '';
      var phone = f.phone.value.replace(/\D/g, '');
      preview.innerHTML = J.agentCard({
        name: f.name.value || '이름', company: f.company.value || '소속', intro: f.intro.value || '한 줄 소개가 여기에 들어갑니다.',
        phone: phone || '01000000000', kakao: f.kakao.value.trim(),
        until: p ? (function () { var d = new Date(J.kstToday() + 'T00:00:00Z'); d.setUTCDate(d.getUTCDate() + p.days - 1); return d.toISOString().slice(0, 10); })() : ''
      }, { previewPhoto: photoData });
      btn.disabled = busy || !cfg || !cfg.ready || fr <= 0;
    }

    f.phone.addEventListener('input', function () {
      var d = f.phone.value.replace(/\D/g, '').slice(0, 11);
      f.phone.value = d.length > 7 ? d.slice(0, 3) + '-' + d.slice(3, d.length - 4) + '-' + d.slice(-4) : d.length > 3 ? d.slice(0, 3) + '-' + d.slice(3) : d;
    });
    f.addEventListener('input', refresh);
    f.addEventListener('change', refresh);

    // 사진: 정사각형으로 잘라 320px JPEG로 줄인다
    f.photo.addEventListener('change', function () {
      var file = f.photo.files && f.photo.files[0];
      photoData = '';
      if (!file) return refresh();
      if (file.size > 15 * 1024 * 1024) { say('사진 파일이 너무 큽니다.', true); f.photo.value = ''; return; }
      var img = new Image(), url = URL.createObjectURL(file);
      img.onload = function () {
        var s = Math.min(img.naturalWidth, img.naturalHeight), c = document.createElement('canvas');
        c.width = c.height = 320;
        c.getContext('2d').drawImage(img, (img.naturalWidth - s) / 2, (img.naturalHeight - s) / 2, s, s, 0, 0, 320, 320);
        photoData = c.toDataURL('image/jpeg', 0.85);
        URL.revokeObjectURL(url);
        refresh();
      };
      img.onerror = function () { say('사진을 읽지 못했습니다. JPG·PNG 파일을 골라 주세요.', true); };
      img.src = url;
    });

    function check() {
      var name = f.name.value.trim(), co = f.company.value.trim(), intro = f.intro.value.trim();
      var phone = f.phone.value.replace(/\D/g, ''), kakao = f.kakao.value.trim();
      if (!f.site.value) return '단지를 골라 주세요.';
      if (free() <= 0) return '이 단지는 칸이 모두 찼습니다.';
      if (!name || !co || !intro) return '이름·소속·한 줄 소개를 모두 적어 주세요.';
      if (URLISH.test(name + co + intro)) return '이름·소속·소개에는 링크를 넣을 수 없습니다.';
      if (BANNED.test(intro + co)) return '수익·가격을 보장하는 표현은 쓸 수 없습니다.';
      if (!/^0\d{8,10}$/.test(phone)) return '휴대폰 번호를 확인해 주세요.';
      if (kakao && !/^https:\/\/(open\.kakao\.com|pf\.kakao\.com)\/[A-Za-z0-9_\-/]+$/.test(kakao)) return '카카오톡 링크는 open.kakao.com 주소만 쓸 수 있습니다.';
      if (!plan()) return '게재 기간을 골라 주세요.';
      if (!(f.agree_public.checked && f.agree_role.checked && f.agree_terms.checked)) return '동의 항목을 모두 확인해 주세요.';
      return '';
    }
    function newOrderId() {
      var a = 'abcdefghijklmnopqrstuvwxyz0123456789', r = '', b = new Uint8Array(10);
      crypto.getRandomValues(b);
      for (var i = 0; i < 10; i++) r += a[b[i] % a.length];
      return 'jj' + J.kstToday().replace(/-/g, '') + '-' + r;
    }

    f.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var err = check();
      if (err) return say(err, true);
      if (!cfg || !cfg.ready || typeof TossPayments !== 'function') return say('결제 준비 중입니다. 잠시 뒤 다시 시도해 주세요.', true);
      var p = plan(), orderId = newOrderId();
      var siteName = f.site.options[f.site.selectedIndex].text;
      var order = {
        orderId: orderId, site: f.site.value, siteName: siteName, plan: p.id,
        name: f.name.value.trim(), company: f.company.value.trim(), intro: f.intro.value.trim(),
        phone: f.phone.value.replace(/\D/g, ''), kakao: f.kakao.value.trim(), photo: photoData,
        agree_public: true, agree_role: true, agree_terms: true
      };
      try { sessionStorage.setItem('jj-order', JSON.stringify(order)); }
      catch (e) { return say('브라우저 저장 공간이 부족합니다. 사진 없이 다시 시도해 주세요.', true); }
      busy = true; refresh(); say('결제 창을 여는 중입니다…');
      var payment = TossPayments(cfg.clientKey).payment({ customerKey: TossPayments.ANONYMOUS });
      payment.requestPayment({
        method: 'CARD',
        amount: { currency: 'KRW', value: p.price },
        orderId: orderId,
        orderName: '브동산 상담사 카드 ' + p.label + ' · ' + siteName.slice(0, 30),
        successUrl: location.origin + '/jupjup/agent-success.html',
        failUrl: location.origin + '/jupjup/agent-fail.html',
        customerName: order.name,
        customerMobilePhone: order.phone
      }).catch(function (e) {
        busy = false; refresh();
        say(e && e.code === 'USER_CANCEL' ? '결제를 취소했습니다.' : '결제 창을 열지 못했습니다. ' + ((e && e.message) || ''), true);
      });
    });

    Promise.all([
      J.getJSON('/jupjup/plans.json'),
      J.getJSON(J.AGENTS_URL).catch(function () { return []; }),
      getConfig()
    ]).then(function (r) {
      plans = r[0]; agents = r[1]; cfg = r[2];
      if (!cfg || !cfg.ready) {
        banner.hidden = false;
        banner.textContent = '카드결제 연결을 준비하고 있습니다. 결제 버튼은 준비가 끝나면 열립니다.';
      } else if (cfg.test) {
        banner.hidden = false;
        banner.textContent = '테스트 모드입니다. 실제로 청구되지 않으며, 등록한 카드는 실제 단지 페이지가 아니라 테스트 목록(주소 뒤 ?test=1)에만 보입니다.';
      }
      refresh();
    });
  }

  // ================= 계좌이체 + 메일 신청
  var tf = $('[data-transfer-form]');
  if (tf) {
    var tmsg = $('[data-msg]'), ttotal = $('[data-total]'), tprev = $('[data-preview]'), tslots = $('[data-slots-msg]'), tdone = $('[data-done]');
    var tplans = null, tagents = [], tholds = [];
    var tq = new URLSearchParams(location.search);
    if (tq.get('site')) tf.site.value = tq.get('site');
    var tsay = function (t, err) { tmsg.textContent = t || ''; tmsg.className = 'jj-msg' + (err ? ' err' : ''); };
    var tplan = function () {
      var id = (tf.querySelector('input[name=plan]:checked') || {}).value;
      return tplans && tplans.plans.filter(function (p) { return p.id === id; })[0];
    };
    var tfree = function () {
      if (!tplans || !tf.site.value) return 0;
      var s = tf.site.value;
      return tplans.slotsPerSite - J.activeAgents(tagents).filter(function (a) { return a.site === s; }).length -
        J.activeHolds(tholds).filter(function (h) { return h.site === s; }).length;
    };
    var trefresh = function () {
      var p = tplan(); if (p) ttotal.textContent = won(p.price);
      if (tplans && tf.site.value) {
        var fr = tfree();
        tslots.textContent = fr > 0 ? '이 단지는 ' + tplans.slotsPerSite + '칸 중 ' + fr + '칸이 비어 있습니다.' : '이 단지는 칸이 모두 찼습니다. 다른 단지를 골라 주세요.';
      } else tslots.textContent = '';
      tprev.innerHTML = J.agentCard({
        name: tf.name.value || '이름', company: tf.company.value || '소속', intro: tf.intro.value || '한 줄 소개가 여기에 들어갑니다.',
        phone: tf.phone.value.replace(/\D/g, '') || '01000000000', kakao: tf.kakao.value.trim()
      });
    };
    tf.phone.addEventListener('input', function () {
      var d = tf.phone.value.replace(/\D/g, '').slice(0, 11);
      tf.phone.value = d.length > 7 ? d.slice(0, 3) + '-' + d.slice(3, d.length - 4) + '-' + d.slice(-4) : d.length > 3 ? d.slice(0, 3) + '-' + d.slice(3) : d;
    });
    tf.addEventListener('input', trefresh);
    tf.addEventListener('change', trefresh);
    var tcheck = function () {
      var name = tf.name.value.trim(), co = tf.company.value.trim(), intro = tf.intro.value.trim();
      var phone = tf.phone.value.replace(/\D/g, ''), kakao = tf.kakao.value.trim();
      if (!tf.site.value) return '단지를 골라 주세요.';
      if (tfree() <= 0) return '이 단지는 칸이 모두 찼습니다.';
      if (!name || !co || !intro) return '이름·소속·한 줄 소개를 모두 적어 주세요.';
      if (URLISH.test(name + co + intro)) return '이름·소속·소개에는 링크를 넣을 수 없습니다.';
      if (BANNED.test(intro + co)) return '수익·가격을 보장하는 표현은 쓸 수 없습니다.';
      if (!/^0\d{8,10}$/.test(phone)) return '휴대폰 번호를 확인해 주세요.';
      if (kakao && !/^https:\/\/(open\.kakao\.com|pf\.kakao\.com)\/[A-Za-z0-9_\-/]+$/.test(kakao)) return '카카오톡 링크는 open.kakao.com 주소만 쓸 수 있습니다.';
      if (!tplan()) return '게재 기간을 골라 주세요.';
      if (!(tf.agree_public.checked && tf.agree_role.checked && tf.agree_terms.checked)) return '동의 항목을 모두 확인해 주세요.';
      return '';
    };
    var applyId = function () {
      var a = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789', r = '', b = new Uint8Array(4);
      crypto.getRandomValues(b);
      for (var i = 0; i < 4; i++) r += a[b[i] % a.length];
      return 'JJ' + J.kstToday().slice(2).replace(/-/g, '') + '-' + r;
    };
    tf.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var err = tcheck();
      if (err) return tsay(err, true);
      var p = tplan(), id = applyId(), hours = +tf.dataset.hours || 24;
      var siteName = tf.site.options[tf.site.selectedIndex].text;
      var name = tf.name.value.trim(), depositor = name + id.slice(-4);
      var due = new Date(Date.now() + hours * 3600e3 + 9 * 3600e3).toISOString().slice(0, 16).replace('T', ' ').replace(/-/g, '.');
      var subject = '[줍줍찬스 신청] ' + siteName + ' / ' + name + ' / ' + id;
      var body = [
        '줍줍찬스 상담사 카드 신청',
        '신청번호: ' + id,
        '단지: ' + siteName + ' (' + tf.site.value + ')',
        '게재 기간: ' + p.label + ' (' + won(p.price) + ')',
        '이름: ' + name,
        '소속: ' + tf.company.value.trim(),
        '휴대폰: ' + tf.phone.value.replace(/\D/g, ''),
        '카카오톡: ' + (tf.kakao.value.trim() || '없음'),
        '한 줄 소개: ' + tf.intro.value.trim(),
        '입금자명: ' + depositor,
        '동의: 카드 정보 공개 동의 / 이 단지 상담 업무 확인 / 약관·개인정보처리방침 동의',
        '',
        '※ 사진을 올리려면 이 메일에 첨부해 주세요(선택).',
        '※ ' + due + '(한국 시간)까지 ' + tf.dataset.acct + '으로 ' + won(p.price) + '을 입금해 주세요.'
      ].join('\n');
      var mailto = 'mailto:' + tf.dataset.email + '?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(body);
      tdone.innerHTML = '<h2>신청 메일을 보내 주세요</h2>' +
        '<p class="jj-sub">메일 앱이 열리면 내용은 그대로 두고 보내기만 누르시면 됩니다. 사진은 그 메일에 첨부해 주세요.</p>' +
        '<table class="jj-kv"><tbody>' +
        '<tr><th>신청번호</th><td>' + J.esc(id) + '</td></tr>' +
        '<tr><th>입금 계좌</th><td>' + J.esc(tf.dataset.acct) + '</td></tr>' +
        '<tr><th>입금 금액</th><td>' + won(p.price) + '</td></tr>' +
        '<tr><th>입금자명</th><td><b>' + J.esc(depositor) + '</b></td></tr>' +
        '<tr><th>입금 기한</th><td>' + J.esc(due) + ' (한국 시간)</td></tr></tbody></table>' +
        '<p><a class="jj-btn solid" href="' + J.esc(mailto) + '">메일 앱 다시 열기</a></p>' +
        '<p class="jj-note">메일 앱이 열리지 않으면 아래 내용을 복사해 ' + J.esc(tf.dataset.email) + ' 로 보내 주세요. 제목: ' + J.esc(subject) + '</p>' +
        '<textarea readonly rows="12" style="width:100%;font-family:inherit;font-size:13px;border:1px solid #E3E3E3;padding:10px">' + J.esc(body) + '</textarea>' +
        '<p class="jj-note">메일이 접수되면 입금 기한까지 칸을 맡아 두고, 입금이 확인되면 24시간 안에 카드를 올립니다.</p>';
      tf.hidden = true; tdone.hidden = false;
      window.scrollTo(0, tdone.offsetTop - 20);
      location.href = mailto;
    });
    Promise.all([J.getJSON('/jupjup/plans.json'), J.getJSON(J.AGENTS_URL).catch(function () { return []; }), J.getHolds()])
      .then(function (r) { tplans = r[0]; tagents = r[1]; tholds = r[2]; trefresh(); });
    trefresh();
  }

  // ================= 결제 성공 → 서버 승인·게재
  var ok = $('[data-success]');
  if (ok) {
    var q = new URLSearchParams(location.search);
    var orderId = q.get('orderId'), paymentKey = q.get('paymentKey'), amount = q.get('amount');
    var out = function (h) { ok.innerHTML = h; };
    var order = null;
    try { order = JSON.parse(sessionStorage.getItem('jj-order') || 'null'); } catch (e) { order = null; }
    var doneKey = 'jj-done-' + orderId;
    var prev = sessionStorage.getItem(doneKey);
    function show(r) {
      if (r.ok) {
        var a = r.entry || {};
        var link = '/jupjup/' + J.esc(a.site) + '.html' + (r.test ? '?test=1' : '') + '#agents';
        out('<h1>' + (r.test ? '테스트 결제가 끝났습니다' : '상담사 카드를 게재했습니다') + '</h1>' +
          '<p class="jj-sub">' + (r.test ? '테스트 목록에 올라갔습니다. 실제 단지 페이지에는 보이지 않습니다.' : '1~2분 안에 단지 페이지 맨 아래에 보입니다.') + '</p>' +
          '<table class="jj-kv"><tbody><tr><th>단지</th><td>' + J.esc((order && order.siteName) || a.site) + '</td></tr>' +
          '<tr><th>게재 기간</th><td>' + J.esc(String(a.start).replace(/-/g, '.')) + ' ~ ' + J.esc(String(a.until).replace(/-/g, '.')) + '</td></tr>' +
          '<tr><th>주문 번호</th><td>' + J.esc(a.id) + '</td></tr></tbody></table>' +
          '<p><a class="jj-btn solid" href="' + link + '">단지 페이지에서 확인</a>' +
          (r.receipt ? ' <a class="jj-btn" href="' + J.esc(r.receipt) + '" target="_blank" rel="noopener">카드 영수증</a>' : '') + '</p>' +
          '<p class="jj-note">카드 내용 수정·게재 중단은 <a href="/contact.html">문의 페이지</a>로 주문 번호와 함께 알려 주세요.</p>');
      } else {
        out('<h1>게재하지 못했습니다</h1><p class="jj-msg err">' + J.esc(r.error || '알 수 없는 오류') + '</p>' +
          '<p class="jj-note">주문 번호 ' + J.esc(orderId || '-') + ' · 문제가 계속되면 <a href="/contact.html">문의 페이지</a>로 알려 주세요.</p>' +
          '<p><a class="jj-btn" href="/jupjup/agent.html">다시 등록하기</a></p>');
      }
    }
    if (prev) { show(JSON.parse(prev)); }
    else if (!order || order.orderId !== orderId || !paymentKey) {
      show({ ok: false, error: '결제 정보를 찾지 못해 결제를 확정하지 않았습니다. 확정되지 않은 결제는 청구되지 않습니다. 같은 브라우저에서 다시 등록해 주세요.' });
    } else {
      fetch('/api/jupjup-confirm', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ paymentKey: paymentKey, orderId: orderId, amount: Number(amount), order: order })
      }).then(function (r) { return r.json().catch(function () { return { ok: false, error: '서버 응답을 읽지 못했습니다.' }; }); })
        .then(function (r) {
          if (r.ok) { try { sessionStorage.setItem(doneKey, JSON.stringify(r)); sessionStorage.removeItem('jj-order'); } catch (e) {} }
          show(r);
        })
        .catch(function () { show({ ok: false, error: '서버에 연결하지 못했습니다. 이 페이지를 새로고침해 주세요.' }); });
    }
  }

  // ================= 결제 실패
  var fail = $('[data-fail]');
  if (fail) {
    var fq = new URLSearchParams(location.search);
    var code = fq.get('code') || '', m = fq.get('message') || '';
    var text = code === 'PAY_PROCESS_CANCELED' ? '결제를 취소했습니다.' : (m || '결제가 완료되지 않았습니다.');
    fail.innerHTML = '<h1>결제가 완료되지 않았습니다</h1><p class="jj-msg err">' + J.esc(text) + '</p>' +
      '<p class="jj-note">청구된 금액은 없습니다. ' + (code ? '오류 코드 ' + J.esc(code) : '') + '</p>' +
      '<p><a class="jj-btn solid" href="/jupjup/agent.html">다시 등록하기</a></p>';
  }
})();
