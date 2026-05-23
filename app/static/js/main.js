/* =====================================================================
   MERVE CAFÉ — luxury motion & interactions
   ===================================================================== */
(function () {
  "use strict";
  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => Array.from(c.querySelectorAll(s));

  /* ---------- Lenis smooth scroll ---------- */
  let lenis = null;
  function initLenis() {
    if (typeof Lenis === "undefined") return;
    lenis = new Lenis({ duration: 1.15, easing: t => Math.min(1, 1.001 - Math.pow(2, -10 * t)), smoothWheel: true });
    function raf(t) { lenis.raf(t); requestAnimationFrame(raf); }
    requestAnimationFrame(raf);
    if (window.gsap && window.ScrollTrigger) {
      lenis.on("scroll", ScrollTrigger.update);
      gsap.ticker.add(t => lenis.raf(t * 1000));
      gsap.ticker.lagSmoothing(0);
    }
  }

  /* ---------- header scroll state ---------- */
  function initHeader() {
    const h = $(".site-header");
    if (!h) return;
    const on = () => h.classList.toggle("scrolled", window.scrollY > 40);
    on(); window.addEventListener("scroll", on, { passive: true });
  }

  /* ---------- mobile nav ---------- */
  function initNav() {
    const t = $(".nav-toggle"), links = $(".nav-links");
    if (!t || !links) return;
    t.addEventListener("click", () => {
      t.classList.toggle("open"); links.classList.toggle("open");
      document.body.classList.toggle("no-scroll");
    });
    $$(".nav-links a").forEach(a => a.addEventListener("click", () => {
      t.classList.remove("open"); links.classList.remove("open");
      document.body.classList.remove("no-scroll");
    }));
  }

  /* ---------- reveal on scroll (GSAP or IO fallback) ---------- */
  function initReveal() {
    if (window.gsap && window.ScrollTrigger) {
      gsap.registerPlugin(ScrollTrigger);
      $$(".reveal").forEach(el => {
        gsap.fromTo(el, { opacity: 0, y: 40 },
          { opacity: 1, y: 0, duration: 1.1, ease: "power3.out",
            scrollTrigger: { trigger: el, start: "top 88%" } });
      });
    } else {
      const io = new IntersectionObserver(es => es.forEach(e => {
        if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
      }), { threshold: 0.15 });
      $$(".reveal").forEach(el => io.observe(el));
    }
  }

  /* ---------- animated counters ---------- */
  function initCounters() {
    $$("[data-count]").forEach(el => {
      const target = parseFloat(el.dataset.count);
      const run = () => {
        let v = 0; const step = target / 60;
        const t = setInterval(() => {
          v += step;
          if (v >= target) { v = target; clearInterval(t); }
          el.textContent = Math.round(v).toLocaleString();
        }, 16);
      };
      if (window.gsap && window.ScrollTrigger) {
        ScrollTrigger.create({ trigger: el, start: "top 90%", once: true, onEnter: run });
      } else { run(); }
    });
  }

  /* ---------- magnetic buttons ---------- */
  function initMagnetic() {
    $$(".magnetic").forEach(m => {
      m.addEventListener("mousemove", e => {
        const r = m.getBoundingClientRect();
        const x = e.clientX - r.left - r.width / 2;
        const y = e.clientY - r.top - r.height / 2;
        m.style.transform = `translate(${x * 0.3}px,${y * 0.4}px)`;
      });
      m.addEventListener("mouseleave", () => m.style.transform = "translate(0,0)");
    });
  }

  /* ---------- 3D tilt on dish cards ---------- */
  function initTilt() {
    $$(".dish").forEach(card => {
      card.addEventListener("mousemove", e => {
        const r = card.getBoundingClientRect();
        const px = (e.clientX - r.left) / r.width - 0.5;
        const py = (e.clientY - r.top) / r.height - 0.5;
        card.style.transform = `translateY(-6px) rotateY(${px * 7}deg) rotateX(${-py * 7}deg)`;
      });
      card.addEventListener("mouseleave", () => card.style.transform = "");
    });
  }

  /* ---------- hero particles (luxury gold dust) ---------- */
  function initParticles() {
    const canvas = $("#hero-canvas");
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    let w, h, particles = [];
    const resize = () => {
      w = canvas.width = canvas.offsetWidth;
      h = canvas.height = canvas.offsetHeight;
    };
    const make = () => {
      particles = Array.from({ length: Math.min(90, Math.floor(w / 16)) }, () => ({
        x: Math.random() * w, y: Math.random() * h,
        r: Math.random() * 1.8 + 0.4,
        vx: (Math.random() - 0.5) * 0.25, vy: -(Math.random() * 0.35 + 0.05),
        a: Math.random() * 0.6 + 0.1
      }));
    };
    const draw = () => {
      ctx.clearRect(0, 0, w, h);
      particles.forEach(p => {
        p.x += p.vx; p.y += p.vy;
        if (p.y < -10) { p.y = h + 10; p.x = Math.random() * w; }
        if (p.x < 0 || p.x > w) p.vx *= -1;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(201,162,90,${p.a})`;
        ctx.shadowBlur = 8; ctx.shadowColor = "rgba(230,200,134,.7)";
        ctx.fill();
      });
      requestAnimationFrame(draw);
    };
    resize(); make(); draw();
    window.addEventListener("resize", () => { resize(); make(); });
  }

  /* ---------- cart ---------- */
  async function api(url, opt) {
    const r = await fetch(url, Object.assign({ headers: { "Content-Type": "application/json" } }, opt));
    return r.json();
  }
  function updateCartCount(n) {
    let el = $(".cart-count");
    if (n > 0) {
      if (!el) {
        const btn = $(".cart-btn"); if (!btn) return;
        el = document.createElement("span"); el.className = "cart-count"; btn.appendChild(el);
      }
      el.textContent = n;
    } else if (el) { el.remove(); }
  }
  function initCart() {
    document.addEventListener("click", async e => {
      const add = e.target.closest("[data-add]");
      if (add) {
        const data = await api("/api/cart/add", { method: "POST", body: JSON.stringify({ id: add.dataset.add, qty: 1 }) });
        updateCartCount(data.count);
        add.classList.add("added"); add.textContent = "Добавлено ✓";
        setTimeout(() => { add.classList.remove("added"); add.textContent = "В корзину"; }, 1300);
      }
    });
  }

  /* ---------- favorites ---------- */
  function initFav() {
    document.addEventListener("click", async e => {
      const f = e.target.closest(".fav-btn");
      if (!f) return;
      const res = await api("/api/favorite/" + f.dataset.fav, { method: "POST" });
      if (res.error) { window.location = "/login"; return; }
      f.classList.toggle("active", res.favorite);
    });
  }

  /* ---------- lightbox ---------- */
  function initLightbox() {
    const lb = $(".lightbox"); if (!lb) return;
    const img = $("img", lb);
    $$(".gal-item").forEach(g => g.addEventListener("click", () => {
      img.src = g.dataset.full || $("img", g).src;
      lb.classList.add("open"); document.body.classList.add("no-scroll");
    }));
    const close = () => { lb.classList.remove("open"); document.body.classList.remove("no-scroll"); };
    $(".close", lb).addEventListener("click", close);
    lb.addEventListener("click", e => { if (e.target === lb) close(); });
    document.addEventListener("keydown", e => e.key === "Escape" && close());
  }

  /* ---------- gallery filter ---------- */
  function initGalFilter() {
    const filters = $$(".gal-filters .chip");
    if (!filters.length) return;
    filters.forEach(c => c.addEventListener("click", () => {
      filters.forEach(x => x.classList.remove("active")); c.classList.add("active");
      const sec = c.dataset.section;
      $$(".gal-item").forEach(it => {
        it.style.display = (sec === "all" || it.dataset.section === sec) ? "" : "none";
      });
    }));
  }

  /* ---------- menu live search/filter ---------- */
  function initMenuSearch() {
    const grid = $("#menu-grid"); if (!grid) return;
    const search = $("#menu-search"), sort = $("#menu-sort");
    const chips = $$(".menu-controls .chip");
    let state = { q: "", category: "all", sort: "popular" };

    const render = items => {
      if (!items.length) { grid.innerHTML = '<p class="muted" style="grid-column:1/-1;text-align:center;padding:3rem">Ничего не найдено.</p>'; return; }
      grid.innerHTML = items.map(cardHTML).join("");
      initTilt();
    };
    const fetchItems = async () => {
      const p = new URLSearchParams(state);
      const items = await api("/api/menu/search?" + p.toString());
      render(items);
    };
    let timer;
    if (search) search.addEventListener("input", () => {
      clearTimeout(timer); state.q = search.value;
      timer = setTimeout(fetchItems, 220);
    });
    if (sort) sort.addEventListener("change", () => { state.sort = sort.value; fetchItems(); });
    chips.forEach(c => c.addEventListener("click", () => {
      chips.forEach(x => x.classList.remove("active")); c.classList.add("active");
      state.category = c.dataset.category; fetchItems();
    }));
  }
  function badgeHTML(b) {
    const map = { best: ["badge-best", "Best Seller"], premium: ["badge-premium", "Premium"], new: ["badge-new", "New"] };
    return map[b] ? `<span class="badge ${map[b][0]}">${map[b][1]}</span>` : "";
  }
  function cardHTML(i) {
    return `<article class="dish reveal in">
      <div class="dish-media">
        ${badgeHTML(i.badge)}
        <button class="fav-btn" data-fav="${i.id}" aria-label="В избранное">♥</button>
        <img src="/static/${i.photo_url}" alt="${i.title}" loading="lazy">
      </div>
      <div class="dish-body">
        <div class="dish-head"><h3>${i.title}</h3><span class="dish-price">${i.price} сом.</span></div>
        <p class="dish-desc">${i.description || ""}</p>
        <div class="dish-meta">
          <span>${i.calories || 0} <b>ккал</b></span>
          <span><b>★</b> ${i.popularity}%</span>
          ${i.ingredients ? `<span>${i.ingredients}</span>` : ""}
        </div>
        <div class="pop-bar"><i style="width:${i.popularity}%"></i></div>
        <div class="dish-actions"><button class="btn btn-gold btn-sm btn-block" data-add="${i.id}">В корзину</button></div>
      </div>
    </article>`;
  }

  /* ---------- flash auto-dismiss ---------- */
  function initFlash() {
    $$(".flash").forEach(f => setTimeout(() => {
      f.style.transition = "opacity .5s, transform .5s";
      f.style.opacity = "0"; f.style.transform = "translateX(40px)";
      setTimeout(() => f.remove(), 500);
    }, 4200));
  }

  /* ---------- hero load animation ---------- */
  function initHeroIntro() {
    if (!window.gsap) return;
    const tl = gsap.timeline({ defaults: { ease: "power3.out" } });
    tl.from(".hero .eyebrow", { y: 24, opacity: 0, duration: 0.9 })
      .from(".hero h1 .ln", { y: 60, opacity: 0, duration: 1.1, stagger: 0.12 }, "-=0.5")
      .from(".hero-sub", { y: 24, opacity: 0, duration: 0.9 }, "-=0.6")
      .from(".hero-cta .btn", { y: 24, opacity: 0, duration: 0.8, stagger: 0.12 }, "-=0.6");
  }

  /* ---------- parallax hero ---------- */
  function initParallax() {
    if (!(window.gsap && window.ScrollTrigger)) return;
    gsap.to(".hero-content", { yPercent: 30, opacity: 0.4, ease: "none",
      scrollTrigger: { trigger: ".hero", start: "top top", end: "bottom top", scrub: true } });
  }

  document.addEventListener("DOMContentLoaded", () => {
    initLenis(); initHeader(); initNav(); initReveal(); initCounters();
    initMagnetic(); initTilt(); initParticles(); initCart(); initFav();
    initLightbox(); initGalFilter(); initMenuSearch(); initFlash();
    initHeroIntro(); initParallax();
  });
})();
