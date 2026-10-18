const navigation = document.querySelector('.proposal-nav');
const secondSection = document.querySelector('.assembly-story');

if (navigation && secondSection) {
 let frame = 0;

 function syncVisibility() {
  frame = 0;
  const hidden = secondSection.getBoundingClientRect().top > 1;
  if (navigation.hidden !== hidden) navigation.hidden = hidden;
 }

 function schedule() {
  if (!frame) frame = requestAnimationFrame(syncVisibility);
 }

 window.addEventListener('scroll', schedule, { passive: true });
 window.addEventListener('resize', schedule);
 window.addEventListener('pageshow', schedule);
 window.addEventListener('hashchange', schedule);
 syncVisibility();
}
