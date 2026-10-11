(() => {
  'use strict';
  const root = document.documentElement;
  const chapters = [...document.querySelectorAll('.chapter')];
  const motionButton = document.getElementById('motion-toggle');
  const media = matchMedia('(prefers-reduced-motion: reduce)');
  const dialog = document.getElementById('index-dialog');
  const indexButton = document.getElementById('index-toggle');
  const previous = document.getElementById('prev-chapter');
  const next = document.getElementById('next-chapter');
  const present = document.getElementById('present-toggle');
  let preference = null;
  try { preference = localStorage.getItem('greedilous-motion'); } catch (_) {}
  let motion = preference === null ? !media.matches : preference === 'on';
  let active = 0;
  let queued = false;
  const clamp = (n, a, b) => Math.min(b, Math.max(a, n));
  const behavior = () => motion && !media.matches ? 'smooth' : 'instant';
  const header = () => parseFloat(getComputedStyle(root).getPropertyValue('--header')) || 64;
  function applyMotion() {
    root.classList.toggle('motion-off', !motion);
    motionButton.setAttribute('aria-pressed', String(motion));
    document.getElementById('motion-label').textContent = motion ? '모션 ON' : '모션 OFF';
  }
  motionButton.addEventListener('click', () => {
    motion = !motion; preference = motion ? 'on' : 'off';
    try { localStorage.setItem('greedilous-motion', preference); } catch (_) {}
    applyMotion();
  });
  media.addEventListener('change', () => { if (preference === null) motion = !media.matches; applyMotion(); });
  function render() {
    queued = false;
    const probe = header() + innerHeight * .3;
    active = 0;
    chapters.forEach((section, index) => { if (section.getBoundingClientRect().top <= probe) active = index; });
    document.getElementById('chapter-number').textContent = String(active + 1).padStart(2, '0');
    document.getElementById('chapter-name').textContent = chapters[active].dataset.chapter;
    previous.disabled = active === 0; next.disabled = active === chapters.length - 1;
    const progress = scrollY / Math.max(1, root.scrollHeight - innerHeight);
    document.getElementById('reading-progress').style.transform = `scaleX(${clamp(progress, 0, 1)})`;
  }
  function schedule() { if (!queued) { queued = true; requestAnimationFrame(render); } }
  function go(index) { chapters[clamp(index, 0, chapters.length - 1)].scrollIntoView({ behavior: behavior(), block: 'start' }); }
  previous.addEventListener('click', () => go(active - 1));
  next.addEventListener('click', () => go(active + 1));
  indexButton.addEventListener('click', () => {
    dialog.showModal(); document.body.classList.add('is-modal'); indexButton.setAttribute('aria-expanded', 'true');
  });
  document.getElementById('index-close').addEventListener('click', () => dialog.close());
  dialog.addEventListener('close', () => {
    document.body.classList.remove('is-modal'); indexButton.setAttribute('aria-expanded', 'false'); indexButton.focus({ preventScroll: true });
  });
  dialog.addEventListener('click', (event) => {
    if (event.target !== dialog) return;
    const r = dialog.getBoundingClientRect();
    if (event.clientX < r.left || event.clientX > r.right || event.clientY < r.top || event.clientY > r.bottom) dialog.close();
  });
  document.querySelectorAll('a[href^="#"]').forEach(link => link.addEventListener('click', event => {
    const target = document.getElementById(link.hash.slice(1));
    if (!target) return;
    event.preventDefault(); if (dialog.open) dialog.close();
    target.scrollIntoView({ behavior: behavior(), block: 'start' });
    if (link.classList.contains('skip')) { target.tabIndex = -1; target.focus({ preventScroll: true }); }
    try { history.replaceState(null, '', link.hash); } catch (_) {}
  }));
  const countButtons = [...document.querySelectorAll('.signature-controls button')];
  const captions = { 1: 'G 하나로 나의 취향과 존재를 드러냅니다.', 2: '같은 G를 거듭하며 표현을 이어갑니다.', 3: '반복된 표현이 하나의 인상을 만듭니다.' };
  countButtons.forEach(button => button.addEventListener('click', () => {
    document.querySelector('.signature-canvas').dataset.count = button.dataset.count;
    countButtons.forEach(item => item.setAttribute('aria-pressed', String(item === button)));
    document.getElementById('signature-caption').textContent = captions[button.dataset.count];
  }));
  const palettes = [...document.querySelectorAll('.palette-controls button')];
  palettes.forEach(button => button.addEventListener('click', () => {
    document.getElementById('pattern-stage').dataset.palette = button.dataset.palette;
    palettes.forEach(item => item.setAttribute('aria-pressed', String(item === button)));
  }));
  const size = document.getElementById('pattern-size');
  function resizePattern() {
    document.getElementById('live-echo').setAttribute('patternTransform', `scale(${Number(size.value) / 226})`);
    size.setAttribute('aria-valuetext', Number(size.value) < 150 ? '작은 반복' : Number(size.value) > 205 ? '큰 반복' : '기본 반복');
  }
  size.addEventListener('input', resizePattern); resizePattern();
  function setPresentation(enabled) {
    root.classList.toggle('is-presenting', enabled);
    present.setAttribute('aria-pressed', String(enabled));
    present.innerHTML = (enabled ? '발표 종료' : '발표 모드') + ' <span aria-hidden="true">⛶</span>';
  }
  present.addEventListener('click', async () => {
    const enabled = !root.classList.contains('is-presenting'); setPresentation(enabled);
    try {
      if (enabled && root.requestFullscreen) await root.requestFullscreen();
      if (!enabled && document.fullscreenElement) await document.exitFullscreen();
    } catch (_) {}
  });
  document.addEventListener('fullscreenchange', () => { if (!document.fullscreenElement) setPresentation(false); schedule(); });
  document.addEventListener('keydown', event => {
    if (event.defaultPrevented || dialog.open) return;
    if (event.key === 'Escape') { setPresentation(false); return; }
    if (event.ctrlKey || event.metaKey || event.altKey || event.shiftKey) return;
    if (event.target instanceof Element && event.target.closest('button,a,input,textarea,select,summary,[contenteditable="true"]')) return;
    if (['ArrowRight', 'PageDown'].includes(event.key)) { event.preventDefault(); go(active + 1); }
    if (['ArrowLeft', 'PageUp'].includes(event.key)) { event.preventDefault(); go(active - 1); }
  });
  if ('IntersectionObserver' in window) {
    const reveal = new IntersectionObserver((entries, observer) => entries.forEach(entry => {
      if (entry.isIntersecting) { entry.target.classList.add('is-revealed'); observer.unobserve(entry.target); }
    }), { threshold: .08 });
    document.querySelectorAll('[data-reveal]').forEach(el => reveal.observe(el));
    const animation = new IntersectionObserver(entries => entries.forEach(entry => entry.target.classList.toggle('offscreen-animation', !entry.isIntersecting)));
    document.querySelectorAll('.cover-symbol,.attitude-ribbon,.kv-stage').forEach(el => animation.observe(el));
  } else { document.querySelectorAll('[data-reveal]').forEach(el => el.classList.add('is-revealed')); }
  const updateVisibility = () => root.classList.toggle('page-inactive', document.hidden);
  document.addEventListener('visibilitychange', updateVisibility); updateVisibility();
  root.classList.add('js'); applyMotion(); render();
  addEventListener('scroll', schedule, { passive: true }); addEventListener('resize', schedule, { passive: true });
  addEventListener('pageshow', schedule); addEventListener('load', schedule);
  document.fonts?.ready.then(schedule);
})();
