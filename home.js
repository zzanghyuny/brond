/*
  홈 대문 렌더러 (2026-11-21 개편) — posts-data.js의 POSTS 제목에서 숫자를 읽어
  ① 이번 주 가장 큰 저평가 박스  ② 청약 판정 카드(분양가·적정가격 막대)
  ③ 미분양 선착순 랭킹 권역별 1위  ④ 히어로 편수 를 그린다.

  손으로 고칠 것은 없다. 새 글을 posts-data.js에 등록하면 홈도 따라 바뀐다.
  - 청약 카드: tag가 "청약 언박싱"이고 제목에 "NN㎡ (평균) 분양가 X.XX억"과
    "예상 프리미엄 ±N"이 둘 다 있는 글만 쓴다. 적정가격 = 분양가 + 예상 프리미엄.
  - 판정: 프리미엄이 분양가의 ±3% 안이면 "적정", 위면 "저평가", 아래면 "고평가".
  - 랭킹: tag가 "미분양 랭킹"인 글의 제목에서 "TOPn"과 "1위 단지 예상 프리미엄은 ±N"을 읽는다.
  읽지 못한 글은 건너뛴다(정적 HTML 목록은 그대로 남는다).
*/
(function () {
  if (typeof POSTS === "undefined" || !Array.isArray(POSTS)) return;

  var MINUS = /[-−–]/;

  // "+5,960만", "−1,320만원", "+1.74억", "-1.19억", "-2억 4,550만" → 억 단위 숫자
  function parseAmount(sign, body) {
    var s = body.replace(/원/g, "").replace(/\s+/g, "");
    var eok = 0, man = 0, m;
    if ((m = s.match(/^([\d.,]+)억([\d,]+)만$/))) { eok = parseFloat(m[1].replace(/,/g, "")); man = parseFloat(m[2].replace(/,/g, "")); }
    else if ((m = s.match(/^([\d.,]+)억$/))) { eok = parseFloat(m[1].replace(/,/g, "")); }
    else if ((m = s.match(/^([\d,]+)만$/))) { man = parseFloat(m[1].replace(/,/g, "")); }
    else return null;
    var v = eok + man / 10000;
    return MINUS.test(sign) ? -v : v;
  }

  function fmtEok(v) { return v.toFixed(2) + "억"; }
  function fmtPrem(v) {
    var sign = v > 0 ? "+" : (v < 0 ? "−" : "±");
    var a = Math.abs(v);
    if (a >= 1) return sign + a.toFixed(2).replace(/0$/, "") + "억";
    return sign + Math.round(a * 10000).toLocaleString("ko-KR") + "만";
  }
  function verdict(prem, price) {
    var r = prem / price;
    if (r > 0.03) return { cls: "plus", label: "저평가" };
    if (r < -0.03) return { cls: "minus", label: "고평가" };
    return { cls: "even", label: "적정" };
  }
  function shortName(p) {
    var t = (p.title || "").split("|")[0];
    var i = t.indexOf(" - ");
    return (i >= 0 ? t.slice(i + 3) : t).trim();
  }
  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }

  // 대표사진(조감도) — posts-data.js의 thumb (scripts/build_thumbs.py)
  function thumb(p, cls) {
    if (!p.thumb) return null;
    var f = el("div", cls);
    var im = document.createElement("img");
    im.src = p.thumb; im.alt = ""; im.loading = "lazy"; im.decoding = "async";
    f.appendChild(im);
    return f;
  }

  var posts = POSTS.filter(function (p) { return p.category !== "vietnam" && p.hidden !== true; })
    .slice().sort(function (a, b) { return (b.date || "").localeCompare(a.date || ""); });

  // ---- 청약 판정 데이터
  var judged = [];
  posts.forEach(function (p) {
    if (p.category !== "realestate" || !/청약 언박싱/.test(p.tag || "")) return;
    var t = p.title || "";
    var pm = t.match(/(\d{2,3})㎡\s*(?:평균\s*)?분양가\s*([\d.]+)억/);
    var rm = t.match(/예상\s*프리미엄\s*([+\-−–])\s*([\d.,]+\s*억?\s*[\d,]*\s*만?원?)/);
    if (!pm || !rm) return;
    var price = parseFloat(pm[2]);
    var prem = parseAmount(rm[1], rm[2]);
    if (!price || prem === null || isNaN(prem)) return;
    judged.push({ post: p, area: pm[1] + "㎡", price: price, prem: prem, fair: price + prem, v: verdict(prem, price) });
  });

  // ---- 히어로 편수
  var heroMeta = document.getElementById("home-count");
  if (heroMeta) {
    var nUnbox = posts.filter(function (p) { return /청약 언박싱/.test(p.tag || ""); }).length;
    var nRank = posts.filter(function (p) { return /미분양 랭킹/.test(p.tag || ""); }).length;
    var latest = posts[0] ? posts[0].dateLabel : "";
    heroMeta.textContent = "청약 언박싱 " + nUnbox + "편 · 미분양 랭킹 " + nRank + "편 · " + latest + " 업데이트";
  }

  // ---- ① 이번 주 가장 큰 저평가
  var pick = document.getElementById("home-pick");
  if (pick && judged.length) {
    var newest = judged[0].post.date;
    var cutoff = new Date(new Date(newest + "T00:00:00").getTime() - 7 * 86400000).toISOString().slice(0, 10);
    var best = null;
    judged.forEach(function (j) {
      if (j.post.date >= cutoff && j.v.cls === "plus" && (!best || j.prem > best.prem)) best = j;
    });
    if (best) {
      pick.querySelector("[data-k=prem]").textContent = fmtPrem(best.prem);
      pick.querySelector("[data-k=name]").textContent = shortName(best.post);
      pick.querySelector("[data-k=sub]").textContent = best.area + " 평균 분양가 " + fmtEok(best.price) + " · 브동산 적정가격 " + fmtEok(best.fair);
      pick.href = best.post.url;
      var hp = thumb(best.post, "hp-photo");
      if (hp && !pick.querySelector(".hp-photo")) pick.insertBefore(hp, pick.firstChild);
      pick.hidden = false;
    }
  }

  // ---- ② 청약 판정 카드
  var grid = document.getElementById("home-judge");
  if (grid && judged.length) {
    grid.innerHTML = "";
    judged.slice(0, 6).forEach(function (j) {
      var m = Math.max(j.price, j.fair) * 1.04;
      var a = el("a", "jc");
      a.href = j.post.url;
      var ph = thumb(j.post, "jc-photo");
      if (ph) a.appendChild(ph);
      var top = el("div", "jc-top");
      top.appendChild(el("span", null, j.post.tag || ""));
      top.appendChild(el("span", null, (j.post.region || "") + " · " + j.area));
      a.appendChild(top);
      a.appendChild(el("div", "jc-name", shortName(j.post)));
      [["분양가", j.price, "ink"], ["적정가격", j.fair, "brass"]].forEach(function (row) {
        var r = el("div", "jc-bar" + (row[2] === "brass" ? " is-fair" : ""));
        r.appendChild(el("span", "jc-lbl", row[0]));
        var trk = el("span", "jc-trk");
        var fill = el("span", "jc-fill " + row[2]);
        fill.style.width = (row[1] / m * 100).toFixed(1) + "%";
        trk.appendChild(fill);
        r.appendChild(trk);
        r.appendChild(el("span", "jc-val", fmtEok(row[1])));
        a.appendChild(r);
      });
      var foot = el("div", "jc-foot");
      foot.appendChild(el("span", "jc-prem " + j.v.cls, j.v.label + " " + fmtPrem(j.prem)));
      foot.appendChild(el("span", "jc-date", j.post.dateLabel || ""));
      a.appendChild(foot);
      grid.appendChild(a);
    });
  }

  // ---- ③ 미분양 랭킹 권역별 1위 (권역마다 최신 글 하나)
  var rank = document.getElementById("home-rank");
  if (rank) {
    var seen = {}, items = [];
    posts.forEach(function (p) {
      if (!/미분양 랭킹/.test(p.tag || "")) return;
      var key = p.region || p.id;
      if (seen[key]) return;
      var t = p.title || "";
      var top = t.match(/TOP\s*(\d+)/);
      var first = t.match(/1위\s*(.+?)\s*예상\s*프리미엄은?\s*([+\-−–])\s*([\d.,]+\s*억?\s*[\d,]*\s*만?원?)/);
      if (!first) return;
      var v = parseAmount(first[2], first[3]);
      if (v === null) return;
      seen[key] = true;
      items.push({ post: p, region: p.region || "", n: top ? top[1] : "", name: first[1], prem: v });
    });
    if (items.length) {
      items.sort(function (a, b) { return b.prem - a.prem; });
      rank.innerHTML = "";
      items.forEach(function (it) {
        var a = el("a", "rk");
        a.href = it.post.url;
        var ph = thumb(it.post, "rk-photo");
        if (ph) a.appendChild(ph);
        a.appendChild(el("div", "rk-region", it.region + (it.n ? " · TOP" + it.n : "")));
        a.appendChild(el("div", "rk-name", it.name));
        var cls = Math.abs(it.prem) < 0.05 ? "even" : (it.prem > 0 ? "plus" : "minus");
        a.appendChild(el("div", "rk-prem " + cls, fmtPrem(it.prem)));
        rank.appendChild(a);
      });
    }
  }

  // ---- ④ 이야기 카테고리 최신 글
  ["realestate", "space", "brand"].forEach(function (cat) {
    var box = document.querySelector('[data-latest="' + cat + '"]');
    if (!box) return;
    var list = posts.filter(function (p) { return p.category === cat && (cat !== "realestate" || /청약 언박싱/.test(p.tag || "")); });
    var cnt = document.querySelector('[data-count="' + cat + '"]');
    if (cnt) cnt.textContent = posts.filter(function (p) { return p.category === cat; }).length + "편";
    if (list[0]) box.textContent = "최근: " + list[0].title;
  });
})();
