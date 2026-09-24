/*
  포스팅 피드 렌더러 — posts-data.js의 POSTS 배열을 읽어
  data-feed 속성이 있는 컨테이너 안에 카드 목록을 그립니다.

  사용법 (HTML):
  <div data-feed
       data-category="realestate"   ← 생략하면 전체 카테고리
       data-page-size="5"           ← 한 번에 보여줄 개수
       data-region-filter="true"    ← realestate 전용, 지역 필터 알약(pill) 표시
       data-empty-text="아직 포스팅이 없습니다."></div>

  동작:
  - 최신순(date 내림차순) 정렬
  - 처음엔 data-page-size개만 표시, "더보기" 클릭 시 다음 묶음 표시
  - 각 카드는 미리보기(.feed-preview)가 일정 높이에서 잘리고
    아래쪽이 흐려지는 효과(.feed-fade) 적용, 카드 전체가 포스팅 링크
  - category가 없는(전체) 피드에서는 브랜드 이야기 카드에 .feed-card--brand
    클래스를 붙여 살짝 다른 카테고리임을 표시
  - data-region-filter="true"이면 등장하는 region 값들로 "전체" + 지역 알약을
    만들어, 클릭 시 해당 지역 포스팅만 다시 표시
*/
(function () {
  function renderFeed(container) {
    var category = container.getAttribute("data-category");
    var pageSize = parseInt(container.getAttribute("data-page-size") || "5", 10);
    var emptyText = container.getAttribute("data-empty-text") || "곧 새로운 이야기로 찾아올게요.";
    var regionFilterEnabled = container.getAttribute("data-region-filter") === "true";

    var basePosts = (typeof POSTS !== "undefined" ? POSTS.slice() : []);
    if (category) {
      basePosts = basePosts.filter(function (p) { return p.category === category; });
    }
    basePosts.sort(function (a, b) {
      return (b.date || "").localeCompare(a.date || "");
    });

    if (basePosts.length === 0) {
      var placeholder = document.createElement("div");
      placeholder.className = "placeholder-card";
      placeholder.textContent = emptyText;
      container.appendChild(placeholder);
      return;
    }

    var activeRegion = "";

    if (regionFilterEnabled) {
      var regions = [];
      basePosts.forEach(function (p) {
        if (p.region && regions.indexOf(p.region) === -1) regions.push(p.region);
      });
      if (regions.length > 1) {
        var pillRow = document.createElement("div");
        pillRow.className = "region-pills";

        function makePill(label, value) {
          var pill = document.createElement("button");
          pill.type = "button";
          pill.className = "region-pill" + (value === "" ? " active" : "");
          pill.textContent = label;
          pill.addEventListener("click", function () {
            if (activeRegion === value) return;
            activeRegion = value;
            var allPills = pillRow.querySelectorAll(".region-pill");
            for (var i = 0; i < allPills.length; i++) allPills[i].classList.remove("active");
            pill.classList.add("active");
            resetAndRender();
          });
          return pill;
        }

        pillRow.appendChild(makePill("전체", ""));
        regions.forEach(function (r) { pillRow.appendChild(makePill(r, r)); });
        container.appendChild(pillRow);
      }
    }

    var list = document.createElement("div");
    list.className = "feed-list";
    container.appendChild(list);

    var moreWrap = document.createElement("div");
    moreWrap.className = "load-more-wrap";
    var moreBtn = document.createElement("button");
    moreBtn.type = "button";
    moreBtn.className = "load-more-btn";
    moreBtn.textContent = "이전 포스팅 더보기";
    moreWrap.appendChild(moreBtn);

    var posts = basePosts;
    var shown = 0;

    function renderNext() {
      var next = posts.slice(shown, shown + pageSize);
      next.forEach(function (post) {
        var card = document.createElement("a");
        card.className = "feed-card" + (!category && post.category === "brand" ? " feed-card--brand" : "");
        card.href = post.url;

        var tag = document.createElement("span");
        tag.className = "post-tag";
        tag.textContent = post.tag || "";

        var title = document.createElement("div");
        title.className = "post-title";
        title.textContent = post.title || "";

        var meta = document.createElement("div");
        meta.className = "post-meta";
        meta.textContent = post.dateLabel || "";

        var preview = document.createElement("div");
        preview.className = "feed-preview";
        preview.innerHTML = post.preview || "";
        var fade = document.createElement("div");
        fade.className = "feed-fade";
        preview.appendChild(fade);

        var more = document.createElement("span");
        more.className = "feed-more";
        more.textContent = "전체보기 →";

        card.appendChild(tag);
        card.appendChild(title);
        card.appendChild(meta);
        card.appendChild(preview);
        card.appendChild(more);
        list.appendChild(card);
      });
      shown += next.length;
      if (shown >= posts.length && moreWrap.parentNode) {
        moreWrap.parentNode.removeChild(moreWrap);
      } else if (shown < posts.length && !moreWrap.parentNode) {
        container.appendChild(moreWrap);
      }
    }

    function resetAndRender() {
      posts = activeRegion ? basePosts.filter(function (p) { return p.region === activeRegion; }) : basePosts;
      list.innerHTML = "";
      shown = 0;
      if (moreWrap.parentNode) moreWrap.parentNode.removeChild(moreWrap);
      if (posts.length === 0) {
        var empty = document.createElement("div");
        empty.className = "placeholder-card";
        empty.textContent = emptyText;
        list.appendChild(empty);
        return;
      }
      renderNext();
    }

    renderNext();
    if (shown < posts.length) {
      moreBtn.addEventListener("click", renderNext);
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    var containers = document.querySelectorAll("[data-feed]");
    for (var i = 0; i < containers.length; i++) {
      renderFeed(containers[i]);
    }
  });
})();
