/* 브동산 계산기 공통 — 취득세 계산, 조정대상지역 목록, 숫자 표시
   기준(2026.11.28 확인):
   - 취득세: 지방세법 제11조 제1항 제8호(주택 유상거래 1~3%), 제13조의2(다주택 중과 8·12%),
     지방교육세(지방세법 제151조), 농어촌특별세(농어촌특별세법 제5조)
   - 생애최초 감면: 지방세특례제한법 제36조의3 (12억 이하, 200만원 한도, 2028.12.31까지)
   - 조정대상지역: 국토교통부·재정경제부 보도자료(2026.2.12 현재 지정 현황) + 2026.7.1 신규 지정(화성 동탄구·용인 기흥구·구리시)
   규정이 바뀌면 이 파일의 숫자와 ADJUSTED 목록만 고치면 세 계산기에 모두 반영된다. */
(function (w) {
  var EOK = 100000000;

  var ADJUSTED_AS_OF = "2026.7.1 지정 기준";
  var ADJUSTED = {
    "서울": ["강남구","강동구","강북구","강서구","관악구","광진구","구로구","금천구","노원구","도봉구","동대문구","동작구","마포구","서대문구","서초구","성동구","성북구","송파구","양천구","영등포구","용산구","은평구","종로구","중구","중랑구"],
    "경기": ["과천시","광명시","구리시","성남시 분당구","성남시 수정구","성남시 중원구","수원시 영통구","수원시 장안구","수원시 팔달구","안양시 동안구","용인시 수지구","용인시 기흥구","의왕시","하남시","화성시 동탄구"]
  };

  // 주택 유상취득 취득세 (원 단위)
  // o: {price, homes(이번 집 포함 세대 주택 수), adjusted, temp2(일시적 2주택), over85, first(생애최초)}
  function acqTax(o) {
    var price = Math.max(0, +o.price || 0);
    var homes = Math.max(1, +o.homes || 1);
    var heavy = 0;
    if (!o.first) {
      if (homes === 2 && o.adjusted && !o.temp2) heavy = 8;
      else if (homes === 3) heavy = o.adjusted ? 12 : 8;
      else if (homes >= 4) heavy = 12;
    }
    var rate; // 소수(0.01 = 1%)
    if (heavy) rate = heavy / 100;
    else if (price <= 6 * EOK) rate = 0.01;
    else if (price <= 9 * EOK) rate = Math.round(((price / EOK) * 2 / 3 - 3) / 100 * 10000) / 10000; // 소수점 다섯째 자리에서 반올림
    else rate = 0.03;

    var tax = Math.floor(price * rate);
    var edu = heavy ? Math.floor(price * 0.004) : Math.floor(tax * 0.1);
    var rural = 0;
    if (o.over85) rural = Math.floor(price * (heavy === 12 ? 0.010 : heavy === 8 ? 0.006 : 0.002));
    var relief = 0;
    if (o.first && price <= 12 * EOK) relief = Math.min(tax, 2000000);
    var total = tax - relief + edu + rural;
    return { rate: rate, heavy: heavy, tax: tax, relief: relief, edu: edu, rural: rural, total: total };
  }

  // 1234567 → "123만 4,567원" / 큰 금액은 "1억 2,345만원"
  function won(n) {
    n = Math.round(n || 0);
    var neg = n < 0; n = Math.abs(n);
    var eok = Math.floor(n / EOK), man = Math.floor((n % EOK) / 10000), rest = n % 10000;
    var s = "";
    if (eok) s += eok.toLocaleString("ko-KR") + "억";
    if (man) s += (s ? " " : "") + man.toLocaleString("ko-KR") + "만";
    if (!eok && !man) s = rest.toLocaleString("ko-KR");
    else if (rest && !eok) s += " " + rest.toLocaleString("ko-KR");
    return (neg ? "-" : "") + (s || "0") + "원";
  }
  // 만원 단위 반올림 표시 ("2억 3,460만원")
  function man(n) { return won(Math.round((n || 0) / 10000) * 10000); }
  function pct(r) { return (Math.round(r * 10000) / 100).toLocaleString("ko-KR", { maximumFractionDigits: 2 }) + "%"; }

  // posts-data.js의 청약 글에서 단지 목록 뽑기 (제목의 'NN㎡ (평균) 분양가 X.XX억')
  function complexes() {
    if (typeof POSTS === "undefined") return [];
    var out = [];
    POSTS.forEach(function (p) {
      if (p.category !== "realestate" || p.hidden) return;
      var m = /(\d{2,3})㎡[^,|]*?분양가\s*([\d.]+)억/.exec(p.title || "");
      if (!m || /미분양|TOP\d/.test(p.title)) return;
      var name = (p.title.split("|")[0].split(" - ")[1] || p.title).trim();
      out.push({ id: p.id, name: name, region: p.region || "", area: +m[1], price: Math.round(parseFloat(m[2]) * EOK), url: "/" + p.url, date: p.date });
    });
    out.sort(function (a, b) { return (b.date || "").localeCompare(a.date || ""); });
    return out;
  }

  w.BDS = { EOK: EOK, ADJUSTED: ADJUSTED, ADJUSTED_AS_OF: ADJUSTED_AS_OF, acqTax: acqTax, won: won, man: man, pct: pct, complexes: complexes };
})(window);
