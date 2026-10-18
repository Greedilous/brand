const story = document.querySelector('.assembly-story');
const stage = document.querySelector('.assembly-stage');
const canvas = document.querySelector('#assembly-canvas');
const context = canvas.getContext('2d', { alpha: true });
const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
const clamp = n => Math.min(1, Math.max(0, n));
const FRAME_COUNT = 80;
const MOBILE = matchMedia('(max-width: 700px)').matches;
const FRAME_ROOT = './assets/metal-20261018/' + (MOBILE ? '640' : '1200') + '/';
const blobs = new Map(), bitmaps = new Map(), requests = new Map(), decoding = new Map();
const failed = new Set();
let queue = [], active = 0, frameRequest = 0, current = 0, target = 0;
let visible = true, ready = false, stopped = false, width = 1, height = 1, lastTime = 0;

function frameURL(index) { return FRAME_ROOT + 'frame-' + String(index).padStart(3, '0') + '.webp'; }
function desiredFrame() { return Math.round(current * (FRAME_COUNT - 1)); }
function scrollProgress() {
 if (reducedMotion.matches) return 1;
 return clamp(-story.getBoundingClientRect().top / Math.max(1, story.offsetHeight - stage.offsetHeight));
}
function pump() {
 if (stopped) return;
 while (active < 4 && queue.length) {
  const index = queue.shift();
  if (blobs.has(index) || failed.has(index)) continue;
  active++;
  fetch(frameURL(index)).then(response => {
   if (!response.ok) throw new Error('Frame unavailable');
   return response.blob();
  }).then(blob => {
   blobs.set(index, blob);
   requests.get(index)?.resolve(blob);
   if (Math.abs(index - desiredFrame()) <= 2) prepare(index);
  }).catch(() => {
   failed.add(index);requests.get(index)?.resolve(null);
  }).finally(() => { active--;pump(); });
 }
}
function fetchFrame(index, urgent = false) {
 if (blobs.has(index)) return Promise.resolve(blobs.get(index));
 if (failed.has(index)) return Promise.resolve(null);
 if (!requests.has(index)) {
  let resolve;
  const promise = new Promise(done => { resolve = done; });
  requests.set(index, { promise, resolve });
  queue.push(index);
 }
 if (urgent && queue.includes(index)) queue = [index, ...queue.filter(i => i !== index)];
 pump();
 return requests.get(index).promise;
}
async function decodeBlob(blob) {
 if ('createImageBitmap' in window) return createImageBitmap(blob);
 const url = URL.createObjectURL(blob);
 try { const image = new Image();image.src=url;await image.decode();return image; }
 finally { URL.revokeObjectURL(url); }
}
function trimCache() {
 const keep = desiredFrame();
 for (const [index, image] of bitmaps) {
  if (bitmaps.size <= 12) break;
  if (index === 0 || index === FRAME_COUNT - 1 || Math.abs(index - keep) <= 3) continue;
  image.close?.();bitmaps.delete(index);
 }
}
function prepare(index) {
 index = Math.max(0, Math.min(FRAME_COUNT - 1, index));
 if (bitmaps.has(index)) return Promise.resolve(bitmaps.get(index));
 if (decoding.has(index)) return decoding.get(index);
 const pending = fetchFrame(index, true).then(async blob => {
  if (!blob || stopped) return null;
  try {
   const image = await decodeBlob(blob);
   if (stopped) { image.close?.();return null; }
   bitmaps.set(index, image);trimCache();
   if (ready && visible && !document.hidden) paint();
   return image;
  } catch { failed.add(index);return null; }
 }).finally(() => decoding.delete(index));
 decoding.set(index, pending);
 return pending;
}
function paint() {
 if (!context || !bitmaps.size) return;
 const desired = desiredFrame();
 let selected = bitmaps.has(desired) ? desired : [...bitmaps.keys()].reduce((a,b) => Math.abs(a-desired)<Math.abs(b-desired)?a:b);
 const image = bitmaps.get(selected);
 context.clearRect(0,0,width,height);
 // Each frame is one physically rendered assembly, never a crossfade between parts.
 const size = Math.min(width < 701 ? width * 1.12 : width * .85, height * (width < 701 ? .7 : .92));
 const x=(width-size)/2, y=(height-size)/2-height*(width < 701 ? .055 : .025);
 context.drawImage(image,x,y,size,size);
 canvas.dataset.frame=String(selected);
 canvas.dataset.progress=current.toFixed(4);
 canvas.dataset.loaded=String(blobs.size);
}
function tick(time) {
 frameRequest=0;
 if (!ready || !visible || document.hidden || stopped) return;
 const delta=Math.min(50,lastTime ? time-lastTime : 16);lastTime=time;
 current=reducedMotion.matches ? 1 : current+(target-current)*(1-Math.exp(-delta/85));
 if(Math.abs(current-target)<.0001)current=target;
 const index=desiredFrame();
 prepare(index);
 if(!reducedMotion.matches){prepare(index+1);prepare(index-1);}
 paint();
 if(current!==target)frameRequest=requestAnimationFrame(tick);
}
function schedule() {
 target=scrollProgress();
 if(ready && visible && !document.hidden && !frameRequest){lastTime=0;frameRequest=requestAnimationFrame(tick);}
}
function resize() {
 width=stage.clientWidth;height=stage.clientHeight;
 const density=Math.min(devicePixelRatio,2);
 canvas.width=Math.round(width*density);canvas.height=Math.round(height*density);
 context?.setTransform(density,0,0,density,0,0);
 target=scrollProgress();current=target;paint();schedule();
}
function preferenceChanged() {
 document.documentElement.classList.toggle('motion-ready',!reducedMotion.matches);
 resize();
 if(!reducedMotion.matches)preload();
}
function preload() {
 if(reducedMotion.matches || stopped) return;
 for(let index=0;index<FRAME_COUNT;index++)fetchFrame(index);
}
const observer=new IntersectionObserver(entries=>{
 visible=entries[0].isIntersecting;
 if(visible)schedule();else{cancelAnimationFrame(frameRequest);frameRequest=0;}
},{rootMargin:'80px'});
async function start() {
 if(!context)throw new Error('Canvas unavailable');
 const initial=reducedMotion.matches?FRAME_COUNT-1:0;
 const first=await prepare(initial);
 if(!first)throw new Error('Image sequence unavailable');
 current=reducedMotion.matches?1:0;
 document.documentElement.classList.toggle('motion-ready',!reducedMotion.matches);
 ready=true;resize();prepare(desiredFrame());
 document.documentElement.classList.add('scene-ready');
 canvas.dataset.state='ready';
 observer.observe(story);
 addEventListener('scroll',schedule,{passive:true});
 addEventListener('resize',resize,{passive:true});
 document.addEventListener('visibilitychange',schedule);
 reducedMotion.addEventListener('change',preferenceChanged);
 if(!reducedMotion.matches){await prepare(FRAME_COUNT-1);preload();}
}
start().catch(()=>{
 document.documentElement.classList.remove('scene-ready','motion-ready');
 canvas.dataset.state='fallback';
});
addEventListener('pagehide',event=>{
 if(event.persisted)return;
 stopped=true;cancelAnimationFrame(frameRequest);observer.disconnect();
 for(const image of bitmaps.values())image.close?.();
 bitmaps.clear();blobs.clear();
});
