/**
 * Tambua Afrika — Home page carousels
 * Drives the Departments, Featured Works, and Shop Highlights tracks:
 * prev/next buttons, the "01 — 05" progress readout, disabled-state at
 * each end, a focus effect (the centred item stays sharp, the rest
 * blur), and gentle autoplay that pauses on hover/touch/tab-hidden.
 *
 * Pure scroll-snap under the hood, so it degrades to a plain, fully
 * visible, swipeable row if JS fails to load — the blur only turns on
 * once this script confirms it's watching.
 */
(function () {
  "use strict";

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

  function initCarousel(config) {
    var track = document.getElementById(config.trackId);
    if (!track) return;

    var root = document.querySelector(config.rootSelector);
    if (!root) return;

    var wrapper = track.parentElement;
    var prevBtn = root.querySelector(config.prevSelector);
    var nextBtn = root.querySelector(config.nextSelector);
    var currentEl = root.querySelector(config.currentSelector);
    var totalEl = root.querySelector(config.totalSelector);
    var items = Array.prototype.slice.call(track.children);
    if (!items.length) return;

    var autoplayDelay = config.autoplayDelay || 5500;
    var autoplayTimer = null;
    var autoplayPaused = false;

    if (totalEl) totalEl.textContent = pad(items.length);

    function pad(n) {
      return n < 10 ? "0" + n : String(n);
    }

    function step() {
      var card = items[0];
      var style = window.getComputedStyle(track);
      var gap = parseFloat(style.columnGap || style.gap || "0") || 0;
      return card.getBoundingClientRect().width + gap;
    }

    function currentIndex() {
      var s = step();
      return s ? Math.round(track.scrollLeft / s) : 0;
    }

    function atEnd() {
      return track.scrollLeft >= track.scrollWidth - track.clientWidth - 1;
    }

    function update() {
      var idx = Math.min(currentIndex(), items.length - 1);
      if (currentEl) currentEl.textContent = pad(idx + 1);
      if (prevBtn) prevBtn.disabled = track.scrollLeft <= 0;
      if (nextBtn) nextBtn.disabled = atEnd();
    }

    // ----- Navigation (also used by autoplay) -----
    function goNext() {
      if (atEnd()) {
        track.scrollTo({ left: 0, behavior: reduceMotion.matches ? "auto" : "smooth" });
      } else {
        track.scrollBy({ left: step(), behavior: reduceMotion.matches ? "auto" : "smooth" });
      }
    }
    function goPrev() {
      track.scrollBy({ left: -step(), behavior: reduceMotion.matches ? "auto" : "smooth" });
    }

    if (prevBtn) prevBtn.addEventListener("click", function () { pauseAutoplay(true); goPrev(); });
    if (nextBtn) nextBtn.addEventListener("click", function () { pauseAutoplay(true); goNext(); });

    track.addEventListener("scroll", debounce(update, 60), { passive: true });
    window.addEventListener("resize", debounce(update, 150));

    // ----- Focus effect: sharp centre item, blurred rest -----
    if ("IntersectionObserver" in window) {
      var ratios = new Map();
      var observer = new IntersectionObserver(
        function (entries) {
          entries.forEach(function (entry) {
            ratios.set(entry.target, entry.intersectionRatio);
          });
          var best = null;
          var bestRatio = 0;
          ratios.forEach(function (ratio, el) {
            if (ratio > bestRatio) {
              bestRatio = ratio;
              best = el;
            }
          });
          items.forEach(function (el) {
            el.classList.toggle("is-active", el === best);
          });
        },
        { root: wrapper, threshold: [0, 0.25, 0.5, 0.75, 1] }
      );
      items.forEach(function (el) { observer.observe(el); });
      track.classList.add("has-focus");
    }

    // ----- Autoplay: gentle, pausable, respects reduced motion -----
    function startAutoplay() {
      stopAutoplay();
      if (reduceMotion.matches || autoplayPaused) return;
      autoplayTimer = setInterval(goNext, autoplayDelay);
    }
    function stopAutoplay() {
      if (autoplayTimer) {
        clearInterval(autoplayTimer);
        autoplayTimer = null;
      }
    }
    function pauseAutoplay(temporarily) {
      stopAutoplay();
      if (temporarily) {
        clearTimeout(pauseAutoplay._resumeTimer);
        pauseAutoplay._resumeTimer = setTimeout(startAutoplay, 4000);
      }
    }

    var section = root; // hovering/touching anywhere in the section pauses autoplay
    section.addEventListener("mouseenter", function () { autoplayPaused = true; stopAutoplay(); });
    section.addEventListener("mouseleave", function () { autoplayPaused = false; startAutoplay(); });
    wrapper.addEventListener("touchstart", function () { pauseAutoplay(true); }, { passive: true });
    wrapper.addEventListener("focusin", function () { autoplayPaused = true; stopAutoplay(); });
    wrapper.addEventListener("focusout", function () { autoplayPaused = false; startAutoplay(); });

    document.addEventListener("visibilitychange", function () {
      if (document.hidden) stopAutoplay();
      else if (!autoplayPaused) startAutoplay();
    });
    reduceMotion.addEventListener("change", function () {
      if (reduceMotion.matches) stopAutoplay();
      else startAutoplay();
    });

    update();
    setTimeout(startAutoplay, 1200);
  }

  function debounce(fn, wait) {
    var t;
    return function () {
      clearTimeout(t);
      var args = arguments;
      t = setTimeout(function () { fn.apply(null, args); }, wait);
    };
  }

  document.addEventListener("DOMContentLoaded", function () {
    initCarousel({
      trackId: "deptsTrack",
      rootSelector: ".home-depts-carousel",
      prevSelector: ".home-depts-prev",
      nextSelector: ".home-depts-next",
      currentSelector: ".home-depts-progress .home-carousel-current",
      totalSelector: ".home-depts-progress .home-carousel-total",
      autoplayDelay: 5000
    });

    initCarousel({
      trackId: "featuredTrack",
      rootSelector: ".home-featured-carousel",
      prevSelector: ".home-featured-prev",
      nextSelector: ".home-featured-next",
      currentSelector: ".home-featured-progress .home-carousel-current",
      totalSelector: ".home-featured-progress .home-carousel-total",
      autoplayDelay: 6000
    });

    initCarousel({
      trackId: "shopTrack",
      rootSelector: ".home-shop-carousel",
      prevSelector: ".home-shop-prev",
      nextSelector: ".home-shop-next",
      currentSelector: ".home-shop-progress .home-carousel-current",
      totalSelector: ".home-shop-progress .home-carousel-total",
      autoplayDelay: 6500
    });
  });
})();