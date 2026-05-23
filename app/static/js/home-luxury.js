/* =====================================================================
   MERVE CAFÉ — HOME PREMIUM SCROLL  (home page only)
   Loaded AFTER main.js and ONLY on index.html.

   IMPORTANT — coexistence with main.js (which is NOT modified):
   • Lenis smooth scroll is already created in main.js and synced to
     GSAP. We DO NOT create another Lenis here (that would cause
     scroll-shake / double easing). We simply read the resulting
     scroll position.
   • main.js animates elements with the ".reveal" class; here we use a
     separate "data-reveal" attribute, so the two never collide.
   • The hero intro, gold-dust canvas, counters, cart, favourites and
     lightbox all remain owned by main.js.

   Everything below is GPU-friendly (transform/opacity only), runs in a
   single passive rAF loop, and degrades gracefully.
   ===================================================================== */
(function () {
  "use strict";

  var home = document.querySelector(".hl-home");
  if (!home) return; // safety: only run on the home page

  var reduceMotion = window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var isMobile = window.matchMedia && window.matchMedia("(max-width: 760px)").matches;

  /* -------------------------------------------------------------------
     1. REVEALS  — IntersectionObserver, one-shot, with elegant stagger.
        We add the hidden state via <html class="hl-ready"> which was set
        synchronously in <head>, so there is no flash of hidden content
        if this script fails to load.
     ------------------------------------------------------------------- */
  function initReveals() {
    var items = Array.prototype.slice.call(home.querySelectorAll("[data-reveal]"));
    if (!items.length) return;

    // assign stagger delays inside explicit groups
    home.querySelectorAll("[data-reveal-group]").forEach(function (group) {
      var base = parseInt(group.getAttribute("data-reveal-group"), 10) || 110;
      var kids = group.querySelectorAll("[data-reveal]");
      Array.prototype.forEach.call(kids, function (el, i) {
        el.style.setProperty("--hl-delay", (i * base) + "ms");
      });
    });

    if (reduceMotion || !("IntersectionObserver" in window)) {
      items.forEach(function (el) { el.classList.add("is-visible"); });
      return;
    }

    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) {
          e.target.classList.add("is-visible");
          io.unobserve(e.target);
        }
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -8% 0px" });

    items.forEach(function (el) { io.observe(el); });
  }

  /* -------------------------------------------------------------------
     2. SCROLL PROGRESS LINE + 3. DEPTH PARALLAX
        Both handled in ONE passive rAF loop, only doing layout work when
        the page has actually scrolled (dirty flag) => smooth & cheap.
     ------------------------------------------------------------------- */
  var progressFill = document.querySelector(".hl-progress > i");
  var parallaxEls = [];
  if (!reduceMotion && !isMobile) {
    parallaxEls = Array.prototype.slice.call(home.querySelectorAll("[data-parallax]"))
      .map(function (el) {
        return { el: el, speed: parseFloat(el.getAttribute("data-parallax")) || 0.12 };
      });
  }

  var ticking = false;
  var lastY = -1;

  function update() {
    ticking = false;
    var y = window.pageYOffset || document.documentElement.scrollTop || 0;

    // progress line
    if (progressFill) {
      var docH = document.documentElement.scrollHeight - window.innerHeight;
      var p = docH > 0 ? Math.min(1, Math.max(0, y / docH)) : 0;
      progressFill.style.transform = "scaleX(" + p.toFixed(4) + ")";
    }

    // depth parallax (subtle, transform-only, GPU)
    if (parallaxEls.length) {
      var vh = window.innerHeight;
      for (var i = 0; i < parallaxEls.length; i++) {
        var item = parallaxEls[i];
        var rect = item.el.getBoundingClientRect();
        // distance of element centre from viewport centre
        var centre = rect.top + rect.height / 2 - vh / 2;
        var shift = -(centre * item.speed);
        // clamp to avoid extreme offsets on very tall elements
        if (shift > 80) shift = 80; else if (shift < -80) shift = -80;
        item.el.style.transform = "translate3d(0," + shift.toFixed(2) + "px,0)";
      }
    }
  }

  function onScroll() {
    var y = window.pageYOffset || document.documentElement.scrollTop || 0;
    if (y === lastY) return;
    lastY = y;
    if (!ticking) { ticking = true; requestAnimationFrame(update); }
  }

  function initScrollFx() {
    if (!progressFill && !parallaxEls.length) return;
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", function () { lastY = -1; onScroll(); }, { passive: true });
    update(); // initial paint
  }

  /* -------------------------------------------------------------------
     run
     ------------------------------------------------------------------- */
  function boot() {
    initReveals();
    initScrollFx();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
