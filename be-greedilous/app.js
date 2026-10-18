(() => {
  'use strict';
  const root = document.documentElement;
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const reveals = [...document.querySelectorAll('[data-reveal]')];
  const details = [...document.querySelectorAll('[data-drift]')];
  const values = document.querySelector('.values');
  let observer;
  let frame = 0;
  const revealAll = () => reveals.forEach(element => element.classList.add('is-visible'));
  function updateDrift() {
    frame = 0;
    if (reduced.matches || document.hidden || !values) return;
    const bounds = values.getBoundingClientRect();
    if (bounds.bottom < 0 || bounds.top > innerHeight) return;
    const progress = Math.max(-1, Math.min(1, (innerHeight / 2 - bounds.top - bounds.height / 2) / (innerHeight + bounds.height) * 2));
    details.forEach(element => element.style.setProperty('--drift', (progress * Number(element.dataset.drift)).toFixed(2) + 'px'));
  }
  function schedule() {
    if (!frame && !reduced.matches && !document.hidden) frame = requestAnimationFrame(updateDrift);
  }
  if ('IntersectionObserver' in window && !reduced.matches) {
    observer = new IntersectionObserver(entries => entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      }
    }), { threshold: .08, rootMargin: '0px 0px 30px 0px' });
    root.classList.add('enhanced');
    reveals.forEach(element => observer.observe(element));
  } else revealAll();
  reduced.addEventListener('change', () => {
    if (reduced.matches) {
      observer?.disconnect();
      revealAll();
      details.forEach(element => element.style.removeProperty('--drift'));
    } else schedule();
  });
  addEventListener('scroll', schedule, { passive: true });
  addEventListener('resize', schedule, { passive: true });
  addEventListener('pageshow', schedule);
  document.addEventListener('visibilitychange', schedule);
  schedule();
})();
