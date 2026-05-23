/* ===== MERVE CAFE — main.js ===== */

document.addEventListener('DOMContentLoaded', () => {

  /* ── Custom Cursor ── */
  const cursor = document.getElementById('cursor');
  const follower = document.getElementById('cursor-follower');
  let fx = 0, fy = 0, cx = 0, cy = 0;

  document.addEventListener('mousemove', e => {
    cx = e.clientX; cy = e.clientY;
    if (cursor) { cursor.style.left = cx + 'px'; cursor.style.top = cy + 'px'; }
  });

  function animateCursor() {
    fx += (cx - fx) * 0.12;
    fy += (cy - fy) * 0.12;
    if (follower) { follower.style.left = fx + 'px'; follower.style.top = fy + 'px'; }
    requestAnimationFrame(animateCursor);
  }
  animateCursor();

  /* ── Navbar Scroll ── */
  const navbar = document.getElementById('navbar');
  window.addEventListener('scroll', () => {
    if (navbar) navbar.classList.toggle('scrolled', window.scrollY > 60);
  }, { passive: true });

  /* ── Mobile Burger ── */
  const burger = document.getElementById('burger');
  const navLinks = document.getElementById('nav-links');
  if (burger && navLinks) {
    burger.addEventListener('click', () => {
      navLinks.classList.toggle('open');
      const spans = burger.querySelectorAll('span');
      const isOpen = navLinks.classList.contains('open');
      spans[0].style.transform = isOpen ? 'rotate(45deg) translate(4px, 4px)' : '';
      spans[1].style.opacity = isOpen ? '0' : '';
      spans[2].style.transform = isOpen ? 'rotate(-45deg) translate(4px, -4px)' : '';
    });
    navLinks.querySelectorAll('.nav-link').forEach(link => {
      link.addEventListener('click', () => {
        navLinks.classList.remove('open');
        burger.querySelectorAll('span').forEach(s => { s.style.transform = ''; s.style.opacity = ''; });
      });
    });
  }

  /* ── Scroll Reveal ── */
  const revealEls = document.querySelectorAll('.reveal-up, .reveal-left, .reveal-right');

  const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const el = entry.target;
        const delay = parseFloat(el.style.animationDelay) || 0;
        setTimeout(() => el.classList.add('revealed'), delay * 1000);
        revealObserver.unobserve(el);
      }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -60px 0px' });

  revealEls.forEach(el => revealObserver.observe(el));

  /* ── Counter Animation ── */
  function animateCounter(el, target, duration = 2000) {
    const start = performance.now();
    const update = (time) => {
      const progress = Math.min((time - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      el.textContent = Math.round(eased * target);
      if (progress < 1) requestAnimationFrame(update);
      else el.textContent = target;
    };
    requestAnimationFrame(update);
  }

  const counters = document.querySelectorAll('.stat-num, .big-num');
  const counterObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const el = entry.target;
        const target = parseInt(el.dataset.target || el.textContent);
        animateCounter(el, target);
        counterObserver.unobserve(el);
      }
    });
  }, { threshold: 0.5 });

  counters.forEach(el => {
    const target = parseInt(el.dataset.target || el.textContent);
    el.dataset.target = target;
    el.textContent = '0';
    counterObserver.observe(el);
  });

  /* ── 3D Tilt Cards ── */
  document.querySelectorAll('.tilt-card').forEach(card => {
    card.addEventListener('mousemove', e => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      const cx2 = rect.width / 2;
      const cy2 = rect.height / 2;
      const rotY = ((x - cx2) / cx2) * 8;
      const rotX = -((y - cy2) / cy2) * 8;
      card.style.transform = `perspective(1000px) rotateX(${rotX}deg) rotateY(${rotY}deg) translateY(-6px)`;
    });
    card.addEventListener('mouseleave', () => {
      card.style.transform = '';
      card.style.transition = 'transform 0.5s ease';
    });
    card.addEventListener('mouseenter', () => {
      card.style.transition = 'transform 0.1s ease';
    });
  });

  /* ── Flash Auto-dismiss ── */
  document.querySelectorAll('.flash').forEach(flash => {
    setTimeout(() => {
      flash.style.opacity = '0';
      flash.style.transform = 'translateX(20px)';
      flash.style.transition = '0.4s ease';
      setTimeout(() => flash.remove(), 400);
    }, 4000);
  });

  /* ── GSAP + ScrollTrigger ── */
  if (window.gsap && window.ScrollTrigger) {
    gsap.registerPlugin(ScrollTrigger);

    /* Marquee pulse */
    const marqueeTrack = document.querySelector('.marquee-track');
    if (marqueeTrack) {
      ScrollTrigger.create({
        trigger: '.marquee-bar',
        start: 'top bottom',
        onEnter: () => gsap.fromTo(marqueeTrack,
          { opacity: 0, y: 20 },
          { opacity: 1, y: 0, duration: 0.6 }
        )
      });
    }

    /* Parallax on experience section bg */
    const expBg = document.querySelector('.experience-bg');
    if (expBg) {
      gsap.to(expBg, {
        yPercent: 30,
        ease: 'none',
        scrollTrigger: { trigger: '.experience-section', start: 'top bottom', end: 'bottom top', scrub: true }
      });
    }

    /* About orb rotation on scroll */
    const orb = document.querySelector('.about-orb-main');
    if (orb) {
      gsap.to(orb, {
        rotation: 360,
        ease: 'none',
        scrollTrigger: { trigger: '.about-orb-container', start: 'top bottom', end: 'bottom top', scrub: true }
      });
    }

    /* Floating visual cards stagger */
    gsap.utils.toArray('.visual-card').forEach((card, i) => {
      gsap.to(card, {
        y: -10,
        duration: 2 + i * 0.5,
        ease: 'sine.inOut',
        yoyo: true,
        repeat: -1,
        delay: i * 0.4
      });
    });
  }

  /* ── Hero Reveal Stagger ── */
  const heroItems = document.querySelectorAll('.hero-content .reveal-up');
  heroItems.forEach((el, i) => {
    setTimeout(() => {
      el.classList.add('revealed');
    }, 300 + i * 180);
  });

  /* ── Page transition: fade in on load ── */
  document.body.style.opacity = '0';
  document.body.style.transition = 'opacity 0.5s ease';
  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      document.body.style.opacity = '1';
    });
  });

  /* ── Input date min = today ── */
  const dateInput = document.querySelector('input[type="date"]');
  if (dateInput) {
    const today = new Date().toISOString().split('T')[0];
    dateInput.min = today;
    if (!dateInput.value) dateInput.value = today;
  }

  /* ── Review form star preview ── */
  const starLabels = document.querySelectorAll('.star-rating label');
  starLabels.forEach(label => {
    label.addEventListener('mouseenter', () => {
      const idx = [...starLabels].indexOf(label);
      starLabels.forEach((l, i) => {
        l.style.color = i >= idx ? 'var(--gold)' : '';
      });
    });
  });
  const starContainer = document.querySelector('.star-rating');
  if (starContainer) {
    starContainer.addEventListener('mouseleave', () => {
      starLabels.forEach(l => l.style.color = '');
    });
  }

});
