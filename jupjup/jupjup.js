/* 브동산 줍줍찬스 — 목록 필터 · 상담사 카드 표시 */
(function () {
  'use strict';
  var TEST = /[?&]test=1\b/.test(location.search);
  var AGENTS_URL = '/jupjup/' + (TEST ? 'agents-test.json' : 'agents.json');

  function kstToday() {
    return new Date(Date.now() + 9 * 3600e3).toISOString().slice(0, 10);
  }
  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function getJSON(url) {
    return fetch(url + '?t=' + Math.floor(Date.now() / 60000), { cache: 'no-store' }).then(function (r) {
      if (!r.ok) throw new Error(r.status);
      return r.json();
    });
  }
  function activeAgents(list) {
    var t = kstToday();
    return (list || []).filter(function (a) { return a && a.start <= t && t <= a.until; })
      .sort(function (a, b) { return (a.createdAt || '').localeCompare(b.createdAt || ''); });
  }
  function fmtPhone(p) {
    var d = String(p || '').replace(/\D/g, '');
    if (d.length === 11) return d.slice(0, 3) + '-' + d.slice(3, 7) + '-' + d.slice(7);
    if (d.length === 10) return d.slice(0, 3) + '-' + d.slice(3, 6) + '-' + d.slice(6);
    return d;
  }
  function safeKakao(u) {
    return /^https:\/\/(open\.kakao\.com|pf\.kakao\.com)\/[A-Za-z0-9_\-\/]+$/.test(u || '') ? u : '';
  }
  function safePhoto(u) {
    return /^\/jupjup\/agents\/[A-Za-z0-9_\-]+\.jpg$/.test(u || '') ? u : '';
  }

  // 상담사 카드 한 장 (등록 화면 미리보기에서도 사용)
  function agentCard(a, opts) {
    opts = opts || {};
    var phone = String(a.phone || '').replace(/\D/g, '');
    var photo = opts.previewPhoto || safePhoto(a.photo);
    var kakao = safeKakao(a.kakao);
    var av = photo ? '<img class="jj-avatar" src="' + esc(photo) + '" alt="' + esc(a.name) + ' 상담사 사진">'
      : '<span class="jj-avatar" aria-hidden="true">' + esc(String(a.name || '상').slice(0, 1)) + '</span>';
    var btns = '';
    if (phone) {
      btns += '<a class="jj-btn solid" href="tel:' + phone + '">전화 ' + esc(fmtPhone(phone)) + '</a>';
      btns += '<a class="jj-btn" href="sms:' + phone + '">문자</a>';
    }
    if (kakao) btns += '<a class="jj-btn" href="' + esc(kakao) + '" target="_blank" rel="noopener nofollow">카카오톡</a>';
    var until = a.until ? '<p class="jj-agent-until">게재 기간 ~ ' + esc(a.until.replace(/-/g, '.')) + '</p>' : '';
    return '<div class="jj-agent">' +
      '<div class="jj-agent-top">' + av +
      '<div class="jj-agent-meta"><div class="jj-agent-name">' + esc(a.name) +
      '<span class="jj-agent-co">' + esc(a.company) + '</span></div>' +
      '<div class="jj-agent-intro">' + esc(a.intro) + '</div></div>' +
      '<span class="jj-ad">AD</span></div>' +
      '<div class="jj-agent-btns">' + btns + '</div>' + until + '</div>';
  }
  // 입금 대기 중인 신청이 맡아 둔 칸 (개인정보 없이 단지·기한만)
  function activeHolds(list) {
    var now = Date.now();
    return (list || []).filter(function (h) { return h && h.site && Date.parse(h.until) > now; });
  }
  function getHolds() {
    return TEST ? Promise.resolve([]) : getJSON('/jupjup/holds.json').catch(function () { return []; });
  }
  window.JJ = { agentCard: agentCard, activeAgents: activeAgents, activeHolds: activeHolds, getHolds: getHolds, getJSON: getJSON, esc: esc, kstToday: kstToday, AGENTS_URL: AGENTS_URL, TEST: TEST };

  // ---- 목록 페이지
  var grid = document.querySelector('[data-grid]');
  if (grid && document.querySelector('[data-pills]')) {
    var cards = Array.prototype.slice.call(grid.querySelectorAll('.jj-card'));
    var st = { r: '', sido: '', done: '', p: '', sort: 'move' };
    var params = new URLSearchParams(location.search);
    if (params.get('r')) st.r = params.get('r');
    var pills = document.querySelectorAll('[data-f-r]');
    var selSido = document.querySelector('[data-f-sido]');
    var selDone = document.querySelector('[data-f-done]');
    var selP = document.querySelector('[data-f-p]');
    var selSort = document.querySelector('[data-sort]');
    var countEl = document.querySelector('[data-count]');
    var emptyEl = document.querySelector('[data-empty]');
    var sorters = {
      move: function (a, b) { return a.dataset.move - b.dataset.move || b.dataset.img - a.dataset.img || b.dataset.n - a.dataset.n; },
      n: function (a, b) { return b.dataset.n - a.dataset.n; },
      pa: function (a, b) { return a.dataset.price - b.dataset.price; },
      pd: function (a, b) { return b.dataset.price - a.dataset.price; }
    };
    function apply(push) {
      var shown = 0;
      cards.sort(sorters[st.sort] || sorters.move).forEach(function (c) {
        var ok = (!st.r || c.dataset.r === st.r) && (!st.sido || c.dataset.sido === st.sido) &&
          (st.done === '' || c.dataset.done === st.done) && (!st.p || c.dataset.p === st.p);
        c.hidden = !ok;
        if (ok) shown++;
        grid.appendChild(c);
      });
      Array.prototype.forEach.call(pills, function (b) { b.classList.toggle('on', b.dataset.fR === st.r); });
      countEl.textContent = shown + '곳';
      emptyEl.hidden = shown > 0;
      if (push) {
        var q = st.r ? '?r=' + st.r : location.pathname;
        history.replaceState(null, '', q);
      }
    }
    Array.prototype.forEach.call(pills, function (b) {
      b.addEventListener('click', function () { st.r = b.dataset.fR; st.sido = ''; selSido.value = ''; apply(true); });
    });
    selSido.addEventListener('change', function () { st.sido = selSido.value; apply(); });
    selDone.addEventListener('change', function () { st.done = selDone.value; apply(); });
    selP.addEventListener('change', function () { st.p = selP.value; apply(); });
    selSort.addEventListener('change', function () { st.sort = selSort.value; apply(); });
    apply();
  }

  // ---- 카드에 '상담사 n명' 표시 (목록·상세의 관련 단지)
  var cardEls = document.querySelectorAll('.jj-card[data-key]');
  var box = document.querySelector('[data-agent-list]');
  if (cardEls.length || box) {
    Promise.all([getJSON(AGENTS_URL), getHolds()]).then(function (r) {
      var act = activeAgents(r[0]);
      var holds = activeHolds(r[1]);
      var cnt = {};
      act.forEach(function (a) { cnt[a.site] = (cnt[a.site] || 0) + 1; });
      Array.prototype.forEach.call(cardEls, function (c) {
        var n = cnt[c.dataset.key];
        var el = c.querySelector('[data-agents]');
        if (n && el) { el.textContent = '상담사 ' + n + '명'; el.hidden = false; }
      });
      if (box) renderAgents(box, act, holds);
    }).catch(function () { /* 목록을 못 읽으면 정적 빈 칸을 그대로 둔다 */ });
  }

  function renderAgents(box, act, holds) {
    var sec = box.closest('[data-site]');
    var site = sec.dataset.site, slots = +sec.dataset.slots || 3, open = sec.dataset.open === '1';
    var mine = act.filter(function (a) { return a.site === site; }).slice(0, slots);
    var html = mine.map(function (a) { return agentCard(a); }).join('');
    if (open) {
      var held = (holds || []).filter(function (h) { return h.site === site; }).length;
      var free = slots - mine.length - held;
      if (held > 0) html += '<p class="jj-note">입금 확인을 기다리는 신청 ' + held + '건이 칸을 맡아 두었습니다.</p>';
      var slotEl = box.querySelector('.jj-slot');
      if (free > 0 && slotEl) {
        var em = slotEl.querySelector('[data-free]');
        if (em) em.textContent = slots + '칸 중 ' + free + '칸 비어 있음';
        html += slotEl.outerHTML;
      }
      if (free <= 0) html += '<p class="jj-note">이 단지 상담사 카드 ' + slots + '칸이 모두 찼습니다. 기간이 끝나는 칸이 생기면 다시 열립니다.</p>';
    } else if (!mine.length) {
      html = box.innerHTML;
    }
    box.innerHTML = html;
  }
})();
