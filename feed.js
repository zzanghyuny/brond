/*
  포스팅 피드 렌더러 — posts-data.js의 POSTS 배열을 읽어
  data-feed 속성이 있는 컨테이너 안에 카드 목록을 그립니다.

  사용법 (HTML):
  <div data-feed
       data-category="realestate"   ← 생략하면 전체 카테고리
       data-page-size="5"           ← 한 번에 보여줄 개수
       data-empty-text="아직 포스팅이 없습니다."></div>

  동작:
  - 최신순(date 내림차순) 정렬
  - 처음엔 data-page-size개만 표시, "더보기" 클릭 시 다음 묶음 표시
  - 각 카드는 미리보기(.feed-preview)가 일정 높이에서 잘리고
    아래쪽이 흐려지는 효과(.feed-fade) 적용, 카드 전체가 포스팅 링크
*/
(function () {
  function renderFeed(container) {
    var category = container.getAttribute("data-category");
    var pageSize = parseInt(container.getAttribute("data-page-size") || "5", 10);
    var emptyText = container.getAttribute("data-empty-text") || "곧 새로운 이야기로 찾아올게요.";

    var posts = (typeof POSTS !== "undefined" ? POSTS.slice() : []);
    if (category) {
      posts = posts.filter(function (p) { return p.category === category; });
    }
    posts.sort(function (a, b) {
      return (b.date || "").localeCompare(a.date || "");
    });

    if (posts.length === 0) {
      var placeholder = document.createElement("div");
      placeholder.className = "placeholder-card";
      placeholder.textContent = emptyText;
      container.appendChild(placeholder);
      return;
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

    var shown = 0;

    function renderNext() {
      var next = posts.slice(shown, shown + pageSize);
      next.forEach(function (post) {
        var card = document.createElement("a");
        card.className = "feed-card";
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
      }
    }

    renderNext();
    if (shown < posts.length) {
      container.appendChild(moreWrap);
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
