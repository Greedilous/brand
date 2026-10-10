(() => {
  'use strict';
  const root = document.documentElement;
  const chapters = Array.from(document.querySelectorAll('[data-chapter]'));
  const motionToggle = document.getElementById('motion-toggle');
  const motionLabel = document.getElementById('motion-label');
  const indexToggle = document.getElementById('index-toggle');
  const indexDialog = document.getElementById('index-dialog');
  const presentToggle = document.getElementById('present-toggle');
  const previous = document.getElementById('prev-chapter');
  const next = document.getElementById('next-chapter');
  const meaning = document.getElementById('meaning');
  const sticky = meaning.querySelector('.meaning-sticky');
  const panels = Array.from(document.querySelectorAll('.story-panel'));
  const storyButtons = Array.from(document.querySelectorAll('[data-story-step]'));
  const chapterNumber = document.getElementById('chapter-number');
  const chapterName = document.getElementById('chapter-name');
  const storyLabel = document.getElementById('story-progress-label');
  const progressBar = document.getElementById('reading-progress');
  const systemMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const mobileLayout = window.matchMedia('(max-width: 700px)');
  const clamp = (value, minimum = 0, maximum = 1) => Math.min(maximum, Math.max(minimum, value));
  let activeChapter = 0;
  let storyStep = -1;
  let queued = false;
  let preference = null;
  try { preference = localStorage.getItem('greedilous-motion'); } catch (_) { /* Storage can be unavailable in private mode. */ }
  let motionEnabled = preference === null ? !systemMotion.matches : preference === 'on';
  const scrollBehavior = () => motionEnabled && !systemMotion.matches ? 'smooth' : 'instant';
  const headerHeight = () => parseFloat(getComputedStyle(root).getPropertyValue('--header')) || 76;

  // Use one frame per scroll update. The visual follows the native scroll position.
  function renderScroll() {
    queued = false;
    const scrollPosition = window.scrollY;
    const screenHeight = window.innerHeight;
    const probe = headerHeight() + (screenHeight - headerHeight()) * .28;
    let selected = 0;
    chapters.forEach((chapter, index) => {
      if (chapter.getBoundingClientRect().top <= probe) selected = index;
    });
    if (selected !== activeChapter || chapterNumber.textContent === '01') {
      activeChapter = selected;
      chapterNumber.textContent = String(selected + 1).padStart(2, '0');
      chapterName.textContent = chapters[selected].dataset.chapter;
      previous.disabled = selected === 0;
      next.disabled = selected === chapters.length - 1;
      previous.setAttribute('aria-label', selected > 0 ? `이전 장: ${chapters[selected - 1].dataset.chapter}` : '이전 장');
      next.setAttribute('aria-label', selected < chapters.length - 1 ? `다음 장: ${chapters[selected + 1].dataset.chapter}` : '다음 장');
    }
    const total = Math.max(1, document.documentElement.scrollHeight - screenHeight);
    progressBar.style.transform = `scaleX(${clamp(scrollPosition / total)})`;
    if (!motionEnabled) return;
    const heroProgress = clamp(scrollPosition / Math.max(1, chapters[0].offsetHeight));
    chapters[0].style.setProperty('--hero-shift', heroProgress.toFixed(4));
    if (!mobileLayout.matches) {
      const start = meaning.offsetTop - headerHeight();
      const range = Math.max(1, meaning.offsetHeight - sticky.offsetHeight);
      const progress = clamp((scrollPosition - start) / range);
      meaning.style.setProperty('--story', progress.toFixed(4));
      const step = Math.min(2, Math.floor(progress * 3));
      setStory(step);
    }
  }
  function scheduleScroll() {
    if (!queued) { queued = true; requestAnimationFrame(renderScroll); }
  }
  function setStory(step) {
    if (storyStep === step) return;
    storyStep = step;
    panels.forEach((panel, index) => panel.classList.toggle('is-current', step === index));
    storyButtons.forEach((button, index) => button.setAttribute('aria-pressed', String(step === index)));
    storyLabel.textContent = `${String(step + 1).padStart(2, '0')} / ${['표현', '반복', '각인'][step]}`;
  }
  function goToChapter(index) {
    const target = chapters[clamp(index, 0, chapters.length - 1)];
    window.scrollTo({ top: Math.max(0, target.offsetTop - headerHeight()), behavior: scrollBehavior() });
  }
  function applyMotion() {
    root.classList.toggle('motion-off', !motionEnabled);
    root.style.scrollBehavior = scrollBehavior() === 'smooth' ? 'smooth' : 'auto';
    motionToggle.setAttribute('aria-pressed', String(motionEnabled));
    motionLabel.textContent = motionEnabled ? '모션 켜짐' : '모션 꺼짐';
    scheduleScroll();
  }
  motionToggle.addEventListener('click', () => {
    const wasInStory = activeChapter === 3 && !mobileLayout.matches;
    motionEnabled = !motionEnabled;
    preference = motionEnabled ? 'on' : 'off';
    try { localStorage.setItem('greedilous-motion', preference); } catch (_) { /* Keep the choice for this page session. */ }
    applyMotion();
    if (wasInStory) window.scrollTo({ top: Math.max(0, meaning.offsetTop - headerHeight()), behavior: 'instant' });
  });
  systemMotion.addEventListener('change', () => {
    if (preference === null) motionEnabled = !systemMotion.matches;
    applyMotion();
  });
  mobileLayout.addEventListener('change', scheduleScroll);
  storyButtons.forEach((button, index) => button.addEventListener('click', () => {
    if (!motionEnabled || mobileLayout.matches) return;
    const start = meaning.offsetTop - headerHeight();
    const range = Math.max(1, meaning.offsetHeight - sticky.offsetHeight);
    const targetProgress = index === 0 ? .04 : (index + .2) / 3;
    window.scrollTo({ top: start + range * targetProgress, behavior: scrollBehavior() });
  }));
  previous.addEventListener('click', () => goToChapter(activeChapter - 1));
  next.addEventListener('click', () => goToChapter(activeChapter + 1));

  function closeIndex() { if (indexDialog.open) indexDialog.close(); }
  indexToggle.addEventListener('click', () => {
    indexDialog.showModal();
    document.body.classList.add('is-modal');
    indexToggle.setAttribute('aria-expanded', 'true');
  });
  document.getElementById('index-close').addEventListener('click', closeIndex);
  indexDialog.addEventListener('close', () => {
    document.body.classList.remove('is-modal');
    indexToggle.setAttribute('aria-expanded', 'false');
    indexToggle.focus({ preventScroll: true });
  });
  indexDialog.addEventListener('click', (event) => {
    if (event.target !== indexDialog) return;
    const box = indexDialog.getBoundingClientRect();
    if (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom) closeIndex();
  });
  document.querySelectorAll('a[href^="#"]').forEach((link) => {
    link.addEventListener('click', (event) => {
      const target = document.getElementById(link.getAttribute('href').slice(1));
      if (!target) return;
      event.preventDefault();
      if (indexDialog.contains(link)) closeIndex();
      window.scrollTo({ top: Math.max(0, target.offsetTop - headerHeight()), behavior: scrollBehavior() });
      if (link.classList.contains('skip')) {
        target.setAttribute('tabindex', '-1');
        target.focus({ preventScroll: true });
      }
      try { history.replaceState(null, '', link.getAttribute('href')); } catch (_) { /* Scrolling still works on a local file. */ }
    });
  });

  function setPresenting(enabled) {
    root.classList.toggle('is-presenting', enabled);
    presentToggle.setAttribute('aria-pressed', String(enabled));
    presentToggle.innerHTML = enabled ? '발표 종료 <span aria-hidden="true">⛶</span>' : '발표 모드 <span aria-hidden="true">⛶</span>';
  }
  presentToggle.title = '전체 화면 · 좌우 방향키로 장 이동 · Escape로 종료';
  presentToggle.addEventListener('click', async () => {
    const enable = !root.classList.contains('is-presenting');
    setPresenting(enable);
    try {
      if (enable && root.requestFullscreen) await root.requestFullscreen();
      if (!enable && document.fullscreenElement && document.exitFullscreen) await document.exitFullscreen();
    } catch (_) { /* The presentation controls remain available when fullscreen is blocked. */ }
  });
  document.addEventListener('fullscreenchange', () => {
    if (!document.fullscreenElement) setPresenting(false);
    scheduleScroll();
  });
  document.addEventListener('keydown', (event) => {
    if (event.defaultPrevented || indexDialog.open) return;
    if (event.key === 'Escape') { setPresenting(false); return; }
    if (event.altKey || event.metaKey || event.ctrlKey || event.shiftKey) return;
    const focused = event.target;
    if (focused instanceof Element && focused.closest('input,textarea,select,button,a,summary,[contenteditable="true"],[role="tab"]')) return;
    if (event.key === 'ArrowRight' || event.key === 'PageDown') { event.preventDefault(); goToChapter(activeChapter + 1); }
    if (event.key === 'ArrowLeft' || event.key === 'PageUp') { event.preventDefault(); goToChapter(activeChapter - 1); }
    if (root.classList.contains('is-presenting') && event.key === 'Home') { event.preventDefault(); goToChapter(0); }
    if (root.classList.contains('is-presenting') && event.key === 'End') { event.preventDefault(); goToChapter(chapters.length - 1); }
  });

  const tabs = Array.from(document.querySelectorAll('[role="tab"]'));
  function selectTab(selectedIndex, focus = false) {
    tabs.forEach((tab, index) => {
      const selected = selectedIndex === index;
      tab.setAttribute('aria-selected', String(selected));
      tab.tabIndex = selected ? 0 : -1;
      document.getElementById(tab.getAttribute('aria-controls')).hidden = !selected;
    });
    if (focus) tabs[selectedIndex].focus();
    scheduleScroll();
  }
  tabs.forEach((tab, index) => {
    tab.addEventListener('click', () => selectTab(index));
    tab.addEventListener('keydown', (event) => {
      const key = event.key;
      if (!['ArrowRight', 'ArrowLeft', 'Home', 'End'].includes(key)) return;
      event.preventDefault();
      event.stopPropagation();
      const target = key === 'Home' ? 0 : key === 'End' ? tabs.length - 1 : (index + (key === 'ArrowRight' ? 1 : -1) + tabs.length) % tabs.length;
      selectTab(target, true);
    });
  });

  // Keep the motif constant while visitors explore its scale and palette.
  const patternStage = document.getElementById('pattern-stage');
  const patternUnit = document.getElementById('live-echo');
  const patternSize = document.getElementById('pattern-size');
  const densityLabel = document.getElementById('pattern-density-label');
  const paletteButtons = Array.from(document.querySelectorAll('[data-palette]'));
  const palettes = {
    signature: ['#ed4ca6', '#e8fa48', '#6c43d7', '#17121d'],
    night: ['#17121d', '#ed4ca6', '#e8fa48', '#f4f2ed']
  };
  paletteButtons.forEach(button => button.addEventListener('click', () => {
    const colors = palettes[button.dataset.palette];
    ['--tile-bg', '--tile-a', '--tile-b', '--tile-c'].forEach((property, index) => {
      patternStage.style.setProperty(property, colors[index]);
    });
    paletteButtons.forEach(item => item.setAttribute('aria-pressed', String(item === button)));
  }));
  function updatePatternSize() {
    const size = Number(patternSize.value);
    patternUnit.setAttribute('patternTransform', `scale(${size / 192})`);
    densityLabel.textContent = size < 120 ? '촘촘하게' : size > 175 ? '대담하게' : '기본';
    patternSize.setAttribute('aria-valuetext', `${densityLabel.textContent}, ${size}`);
  }
  patternSize.addEventListener('input', updatePatternSize);
  updatePatternSize();

  // Repetition is illustrated as a shared petal form, rather than a finalized logo.
  document.querySelectorAll('.petal-ring').forEach((ring) => {
    for (let index = 0; index < 12; index++) {
      const petal = document.createElementNS('http://www.w3.org/2000/svg', 'ellipse');
      petal.setAttribute('cx', '100'); petal.setAttribute('cy', '49');
      petal.setAttribute('rx', '15'); petal.setAttribute('ry', '43');
      petal.setAttribute('fill', 'currentColor');
      petal.setAttribute('transform', `rotate(${index * 30} 100 100)`);
      ring.appendChild(petal);
    }
  });
  if ('IntersectionObserver' in window) {
    const reveal = new IntersectionObserver((entries, observer) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-revealed');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: .07, rootMargin: '0px 0px -5% 0px' });
    document.querySelectorAll('[data-reveal]').forEach((element) => reveal.observe(element));
    const rotation = new IntersectionObserver((entries) => {
      entries.forEach((entry) => { entry.target.style.animationPlayState = entry.isIntersecting ? 'running' : 'paused'; });
    });
    document.querySelectorAll('.rosette,.campaign-lines>span,.campaign-pattern').forEach((element) => rotation.observe(element));
  } else {
    document.querySelectorAll('[data-reveal]').forEach((element) => element.classList.add('is-revealed'));
  }
  root.classList.add('js');
  applyMotion();
  window.addEventListener('scroll', scheduleScroll, { passive: true });
  window.addEventListener('resize', scheduleScroll, { passive: true });
  window.addEventListener('pageshow', scheduleScroll);
  window.addEventListener('load', scheduleScroll);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(scheduleScroll);
})();
