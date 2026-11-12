/* One physical ShadowRoot and one disposable lifecycle per source example. */
(() => {
  'use strict';
  const installers = new Map(), controllers = new WeakMap();
  let activePreview = null;
  function init(scope) {
    if (controllers.has(scope)) return controllers.get(scope);
    const template = [...scope.children].find(node => node.matches('template[data-demo-template]'));
    if (!template) return {reset() {}, preview() {return false;}};
    const shadow = scope.shadowRoot || scope.attachShadow({mode: 'open'});
    let previewMode = false, playbackSpeed = 1, playbackStart = performance.now();
    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
    let motionTimer = null, motionDuration = 3000, manualPhase = 0;
    const virtualNow=()=>playbackStart+(performance.now()-playbackStart)*playbackSpeed;
    function applyPlayback(){body?.getAnimations?.({subtree:true}).forEach(animation=>{animation.playbackRate=playbackSpeed;});}
    let lifetime = null, implementation = null, body = null, dead = false;
    const timers = new Set(), intervals = new Set(), frames = new Set(), cleanup = [];
    const nativeWindow = window, nativeDocument = document;
    function clearResources({preserveCssAnimations = false, preserveFrames = false} = {}) {
      nativeWindow.clearTimeout(motionTimer); motionTimer = null;
      lifetime?.abort(); lifetime = null;
      timers.forEach(id => nativeWindow.clearTimeout(id)); timers.clear();
      intervals.forEach(id => nativeWindow.clearInterval(id)); intervals.clear();
      frames.forEach(id => nativeWindow.cancelAnimationFrame(id)); frames.clear();
      cleanup.splice(0).forEach(dispose => dispose());
      if (!preserveCssAnimations) shadow.getAnimations?.({subtree: true}).forEach(animation => animation.cancel());
      if (!preserveFrames) shadow.querySelectorAll('iframe').forEach(frame => {frame.src = 'about:blank';});
      implementation = null;
    }
    const setTimeout = (fn, ms, ...args) => {
      const id = nativeWindow.setTimeout(() => {timers.delete(id); if (!dead) {fn(...args);applyPlayback();}}, ms/playbackSpeed);
      timers.add(id); return id;
    };
    const clearTimeout = id => {nativeWindow.clearTimeout(id); timers.delete(id);};
    const setInterval = (fn, ms, ...args) => {
      if (reduced.matches && !previewMode) return 0;
      const id = nativeWindow.setInterval(() => {if (!dead) {fn(...args);applyPlayback();}}, ms/playbackSpeed);
      intervals.add(id);
      return id;
    };
    const clearInterval = id => {nativeWindow.clearInterval(id); intervals.delete(id);};
    const requestAnimationFrame = fn => {
      if(reduced.matches&&!previewMode)return 0;
      const id = nativeWindow.requestAnimationFrame(now => {frames.delete(id); if (!dead) {fn(virtualNow());applyPlayback();}});
      frames.add(id); return id;
    };
    const cancelAnimationFrame = id => {nativeWindow.cancelAnimationFrame(id); frames.delete(id);};
    function matchMedia(query) {
      const media = nativeWindow.matchMedia(query);
      return {
        get matches() {
          const previewQuery = query.includes('pointer: coarse') || query.includes('prefers-reduced-motion');
          return previewMode && previewQuery ? false : media.matches;
        },
        media: media.media,
        addEventListener(type, listener, options) {media.addEventListener(type, listener, options); cleanup.push(() => media.removeEventListener(type, listener, options));},
        removeEventListener(type, listener, options) {media.removeEventListener(type, listener, options);}
      };
    }
    const localDocument = {
      querySelector: selector => shadow.querySelector(selector),
      querySelectorAll: selector => shadow.querySelectorAll(selector),
      getElementById: id => shadow.getElementById(id),
      createElement: name => nativeDocument.createElement(name),
      elementFromPoint: (x, y) => shadow.elementFromPoint?.(x, y) || null,
      get activeElement() {return shadow.activeElement || body;},
      get body() {return body;},
      get documentElement() {return body;},
      get hidden() {return nativeDocument.hidden;},
      addEventListener(type, listener, options) {
        // Visibility is owned by site.js. Every source keyboard/click delegate
        // listens inside its example, never on the real document or window.
        if (type === 'visibilitychange') return;
        const opts = typeof options === 'boolean' ? {capture: options} : (options || {});
        shadow.addEventListener(type, listener, {...opts, signal: lifetime.signal});
      }
    };
    const localWindow = {setTimeout,clearTimeout,setInterval,clearInterval,requestAnimationFrame,cancelAnimationFrame,
      getSelection: () => nativeWindow.getSelection(), clipboardData: nativeWindow.clipboardData};
    function toast(message) {
      let output = shadow.querySelector('.demo-status');
      if (!output) {output = nativeDocument.createElement('output');output.className = 'demo-status';output.setAttribute('aria-live', 'polite');body.append(output);}
      output.textContent = message;
    }
    function mount() {
      shadow.replaceChildren();
      const link = nativeDocument.createElement('link');link.rel = 'stylesheet';link.href = template.dataset.demoCss;
      shadow.append(link);
      if(template.dataset.stateCss){const states=nativeDocument.createElement('link');states.rel='stylesheet';states.href=template.dataset.stateCss;shadow.append(states);}
      shadow.append(template.content.cloneNode(true));
      body = shadow.querySelector('.demo-root');
      scope.removeAttribute('data-demo-playing');
      scope.dataset.demoStatic=template.dataset.demoStatic||'false';
      scope.dataset.demoCategory=template.dataset.demoCategory||'';
      // Frames are local documents; keep their source URL for preview/reset.
      shadow.querySelectorAll('iframe').forEach(frame => {frame.dataset.initialSrc ||= frame.getAttribute('src');});
      // No cross-page navigation is performed by a component mock-up.
      shadow.addEventListener('click', preventExampleNavigation);
      primeVirtualList();
      particlePreview(false);
      fitGallery();
      link.addEventListener('load', () => {
        if (!shadow.contains(link)) return;
        if (!scope.hasAttribute('data-demo-playing')) primeVirtualList();
        fitGallery();
        if (scope.hasAttribute('data-demo-motion-once')) scheduleMotionEnd();
        if (scope.hasAttribute('data-demo-motion-step')) renderManualPhase();
      }, {once:true});
      const miniStage=scope.closest('.mini-stage');
      if(miniStage&&typeof ResizeObserver!=='undefined'){const observer=new ResizeObserver(()=>{if(!scope.isConnected){observer.disconnect();return;}fitGallery();});observer.observe(miniStage);cleanup.push(()=>observer.disconnect());}
    }
    function primeVirtualList() {
      if (!shadow.querySelector('#vlList') || !installers.has(scope.dataset.demoKind)) return;
      // The source computes its real rows from the current CSS viewport. Run
      // that initializer once, then discard every listener and scheduled task.
      // Rebuild from the source template so stylesheet-load priming cannot add
      // a second spacer or retain rows calculated before dimensions settled.
      const original = template.content.querySelector('.demo-root');
      if (!original) return;
      const fresh = original.cloneNode(true);
      body.replaceWith(fresh);body = fresh;
      const retainedCleanup = cleanup.splice(0);
      activate();
      const still = body.cloneNode(true);
      still.setAttribute('data-demo-primed','');
      clearResources();
      cleanup.push(...retainedCleanup);
      body.replaceWith(still);body = still;
      scope.removeAttribute('data-demo-playing');
    }
    function fitGallery() {
      const stage=scope.closest('.mini-stage');
      if(!stage||!body)return;
      const style=getComputedStyle(stage),width=scope.clientWidth||stage.clientWidth;
      scope.style.display='flex';scope.style.alignItems='center';scope.style.justifyContent='center';
      body.style.width='312px';body.style.flexShrink='0';body.style.zoom='1';
      const natural=body.scrollHeight||224;
      // Let an auto-height cell grow at the requested width scale before
      // measuring its height limit. Reading the old height would shrink every
      // preview back down and can oscillate during ResizeObserver callbacks.
      body.style.zoom=String(Math.min(1.35,width/312));
      const height=stage.clientHeight-parseFloat(style.paddingTop||0)-parseFloat(style.paddingBottom||0);
      const scale=Math.min(1.35,width/312,height>0?height/natural:1.35);
      body.style.zoom=String(scale);
    }
    function preventExampleNavigation(event) {
      if (event.target.closest?.('a')) event.preventDefault();
    }
    function activate() {
      if (implementation) return implementation;
      if(body?.hasAttribute('data-demo-primed')){const fresh=template.content.querySelector('.demo-root').cloneNode(true),style=body.getAttribute('style');if(style)fresh.setAttribute('style',style);body.replaceWith(fresh);body=fresh;}
      dead = false; lifetime = new AbortController();
      const installer = installers.get(scope.dataset.demoKind);
      implementation = installer ? (installer({scope,document: localDocument,window: localWindow,matchMedia,
        setTimeout,clearTimeout,setInterval,clearInterval,requestAnimationFrame,cancelAnimationFrame,performance:{now:virtualNow},animate:(el,keys,options)=>{const opts=typeof options==='number'?{duration:options}:options;const animation=el.animate(keys,opts);animation.playbackRate=playbackSpeed;cleanup.push(()=>animation.cancel());return animation;},toast}) || {}) : {};
      // CSS animations run only after an explicit preview or inside detail.
      scope.dataset.demoPlaying = 'true';
      return implementation;
    }
    function reset() {
      dead = true;
      clearResources();
      previewMode = false;
      scope.removeAttribute('data-demo-motion-once');
      scope.removeAttribute('data-demo-motion-step');
      mount();
      if (activePreview === controller) activePreview = null;
      scope.querySelectorAll(':scope > .demo-secondary').forEach(child => init(child).reset());
    }
    function pointer(el, type, x, y) {
      if (!el) return;
      const r = el.getBoundingClientRect();
      el.dispatchEvent(new PointerEvent(type, {bubbles:true,composed:true,pointerType:'mouse',button:0,
        clientX:r.left+r.width*x,clientY:r.top+r.height*y,pointerId:97}));
    }
    function scrollPreview() {
      const scroller = shadow.querySelector('.mini-scroll,.seq-scroll,.hidehead-scroll,.extra-header-scroll,.extra-section-scroll,.extra-highlight-scroll,.extra-snap-scroll,.tblfix-demo,#bttPage,#infList,#vlList,.mini-layout');
      if (!scroller) return false;
      const start = virtualNow(), distance = Math.max(100, scroller.scrollHeight-scroller.clientHeight), horizontal = Math.max(0, scroller.scrollWidth-scroller.clientWidth);
      function tick(now) {const p=Math.min(1,(now-start)/1050);scroller.scrollTop=distance*p;scroller.scrollLeft=horizontal*p;scroller.dispatchEvent(new Event('scroll'));if(p<1)requestAnimationFrame(tick);}
      requestAnimationFrame(tick);return true;
    }
    function previewPointers() {
      const magnifier = shadow.querySelector('.extra-magnifier-art');
      if(scope.dataset.demoCategory!=='依赖鼠标指针'&&!magnifier)return false;
      const target = magnifier || shadow.querySelector('.micro-card,.cursor-wave,.magnet-wrap,.cf-stage,.trail-stage,.eyes-stage,.obj-stage,.extra-magnifier-art');
      if (!target) return false;
      // Replay the source's pointer listeners along a local virtual path.
      // Preview's matchMedia facade permits this path on coarse devices.
      pointer(target, 'pointerenter', .25, .45);
      let step = 0;
      function move() {pointer(target,'pointermove',.5+Math.sin(step/7)*.3,.5+Math.cos(step/7)*.23);if((step+=playbackSpeed)<45)requestAnimationFrame(move);}
      requestAnimationFrame(move);return true;
    }
    function particlePreview(loop=true, phase=0) {
      const canvas = shadow.querySelector('.particles canvas,canvas.particle-canvas,canvas');
      if (!canvas) return false;
      const context = canvas.getContext('2d');if (!context) return false;
      const dots=Array.from({length:32},(_,i)=>({x:((i*71+phase*87)%616)+2,y:((i*53+phase*43)%256)+2,vx:(i%5-2)*.14,vy:(i%3-1)*.17,r:(i%3)+1}));
      const color=getComputedStyle(scope).getPropertyValue('--demo-primary').trim()||'#6D28D9';
      function draw() {context.clearRect(0,0,canvas.width,canvas.height);context.fillStyle=color;dots.forEach(d=>{context.beginPath();context.arc(d.x,d.y,d.r,0,Math.PI*2);context.fill();d.x=(d.x+d.vx*playbackSpeed+620)%620;d.y=(d.y+d.vy*playbackSpeed+260)%260;});if(loop&&(!reduced.matches||previewMode))requestAnimationFrame(draw);}
      draw();return true;
    }
    function finishMotionOnce() {
      // Retain the resulting DOM while disposing all source loops and listeners.
      dead = true; clearResources({preserveFrames:true}); previewMode = false;
      scope.removeAttribute('data-demo-playing');
      scope.removeAttribute('data-demo-motion-once');
      if (activePreview === controller) activePreview = null;
      scope.dispatchEvent(new CustomEvent('demo-playback-end'));
    }
    function scheduleMotionEnd() {
      if (!reduced.matches) return;
      nativeWindow.clearTimeout(motionTimer);
      // Include delayed keyframes and one full cycle of a continuous effect.
      const ends = body.getAnimations?.({subtree:true}).map(animation =>
        animation.effect?.getComputedTiming().endTime).filter(Number.isFinite) || [];
      motionDuration = (Math.max(3000, ...ends) + 100) / playbackSpeed;
      motionTimer = nativeWindow.setTimeout(finishMotionOnce, motionDuration);
    }
    function preview(speed=1) {
      if (activePreview && activePreview !== controller) activePreview.reset();
      reset();manualPhase=0;activePreview=controller;playbackSpeed=speed===.25?.25:1;playbackStart=performance.now();
      if (scope.dataset.demoStatic === 'true') return false;
      if(playbackSpeed!==1&&shadow.querySelector('iframe')) return false;
      previewMode=true;
      if (reduced.matches) scope.setAttribute('data-demo-motion-once','');
      const source=activate();
      scheduleMotionEnd();
      requestAnimationFrame(scheduleMotionEnd);
      if (source.preview) {source.preview();requestAnimationFrame(applyPlayback);return true;}
      const stage=shadow.querySelector('.stage');
      if (stage) source.replay?.(stage);
      requestAnimationFrame(applyPlayback);
      shadow.querySelectorAll('*').forEach(el=>{el.setAttribute('data-preview-hover','');el.setAttribute('data-preview-active','');});
      setTimeout(()=>shadow.querySelectorAll('[data-preview-active]').forEach(el=>el.removeAttribute('data-preview-active')),500);
      if (particlePreview()||previewPointers()) return true;
      const drag=shadow.querySelector('[data-drag]:not([data-drag="sheet"]),#reTbl th,.colgrip');
      if(drag){const r=drag.getBoundingClientRect(),horizontal=['swipe','rubber','pager'].includes(drag.dataset.drag)||drag.matches('#reTbl th,.colgrip'),dx=horizontal?(drag.dataset.drag==='swipe'||drag.dataset.drag==='pager'?-100:70):0,dy=horizontal?0:85;const send=(type,x,y)=>drag.dispatchEvent(new PointerEvent(type,{bubbles:true,pointerType:'mouse',button:0,pointerId:97,clientX:r.left+r.width/2+x,clientY:r.top+r.height/2+y}));send('pointerdown',0,0);setTimeout(()=>send('pointermove',dx,dy),150);setTimeout(()=>send('pointerup',dx,dy),500);return true;}
      if (scrollPreview()) return true;
      const hold=shadow.querySelector('#holdBtn');
      if (hold) {pointer(hold,'pointerdown',.5,.5);setTimeout(()=>pointer(hold,'pointerup',.5,.5),1050);return true;}
      const preferred = shadow.querySelector('[data-extra-action="accordion"],[data-extra-action="filter"][data-value]:not([aria-pressed="true"]),[data-extra-action="delete"],[data-extra-action="submit"],[data-extra-action="add-toast"],[data-extra-action="tab"]:not([aria-selected="true"]),[data-extra-action="drop"],[data-extra-action="roll"],[data-extra-action="expand"],[data-extra-action="chart"]:not([aria-pressed="true"]),[data-extra-action="load-content"],.shake-go,#splitCaret,#fabBtn,#advToggle,#lmBtn,[data-action="next"],[data-action="toggle"],[data-action="open"],[data-action="sort"],[data-cmd="openModal"],[data-cmd="openDrawer"],[data-cmd="openCmdk"],[data-cmd="toggleInfoPopover"],[data-cmd="toggleDD"],[data-cmd="toggleAcc"],[data-cmd="switchTab"][data-arg="1"],.switch-demo,.ripple-btn,.uline:not(.on),#copyDemoBtn,#megaTrigger,.segb:not(.on),.bdg,[data-cmd="stepNum"][data-arg="1"],[data-cmd="setStep"][data-arg="2"],.st:last-child,[data-cmd="removeParent"],#carNext');
      if (preferred) {const r=preferred.getBoundingClientRect();preferred.dispatchEvent(new MouseEvent('click',{bubbles:true,composed:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2}));return true;}
      const select=shadow.querySelector('select');
      if(select){select.selectedIndex=Math.min(select.options.length-1,select.selectedIndex+1);select.dispatchEvent(new Event('change',{bubbles:true}));return true;}
      const field=shadow.querySelector('input[type="radio"]:not(:checked),input:not([type="file"]):not([type="hidden"]),textarea');
      if (field) {
        if (field.type==='checkbox'||field.type==='radio') field.click();
        else {field.value=field.type==='range'?String(Math.min(Number(field.max||100),Number(field.value||0)+10)):field.type==='color'?'#6d28d9':(field.value||field.placeholder||'');field.dispatchEvent(new Event('input',{bubbles:true}));field.dispatchEvent(new Event('change',{bubbles:true}));}
        return true;
      }
      const edit=shadow.querySelector('#ieText,.edittarget,.ctxzone');
      if(edit){const key=edit.matches('.ctxzone')?'ContextMenu':'Enter';edit.dispatchEvent(new KeyboardEvent('keydown',{bubbles:true,key}));return true;}
      const frame=shadow.querySelector('iframe');
      if(frame){setTimeout(()=>{const link=frame.contentDocument?.querySelector('a');link?.click();},650);return true;}
      // CSS-only examples already run their source hover/keyframe rules.
      return true;
    }
    function restore(){reset();previewMode=false;playbackSpeed=1;playbackStart=performance.now();activate();particlePreview();}
    function renderManualPhase() {
      shadow.querySelector('.stage')?.classList.add('run');
      body.getAnimations?.({subtree:true}).forEach(animation => {
        const timing = animation.effect.getTiming();
        animation.pause();
        animation.currentTime = Number(timing.delay) + Number(timing.duration) * manualPhase / 4;
      });
      particlePreview(false,manualPhase);
    }
    function step() {
      const frame = shadow.querySelector('iframe');
      if (frame) {frame.contentDocument?.querySelector('a')?.click();return;}
      const morph = shadow.querySelector('.morph-stage');
      const carousel = shadow.querySelector('.carousel');
      if (morph || carousel) {
        // These source-driven loops also support a static next item.
        dead = true; clearResources(); previewMode = false;
        scope.removeAttribute('data-demo-motion-once');
        scope.removeAttribute('data-demo-playing');
        scope.setAttribute('data-demo-motion-step','');
        if (morph) {
          const words = JSON.parse(morph.dataset.demoWords);
          const current = morph.querySelector('.mw-cur');
          morph.querySelector('.morph-word').classList.remove('morphing');
          current.textContent = words[(words.indexOf(current.textContent) + 1) % words.length];
        } else {
          shadow.querySelector('#carNext').click();
          clearResources({preserveCssAnimations:true});
        }
        return;
      }
      // Four static phases expose continuous CSS/canvas effects without motion.
      manualPhase = (manualPhase + 1) % 5;
      reset(); scope.setAttribute('data-demo-motion-step','');
      activate(); scope.removeAttribute('data-demo-playing');
      renderManualPhase();
      dead = true; clearResources({preserveCssAnimations:true});
    }
    const controller = {
      reset, restore, preview, step, root:shadow,
      get motionDuration() {return motionDuration;},
      get supportsSlow() {return !shadow.querySelector('iframe');},
      get supportsStep() {return template.dataset.demoLoop === 'true' || !!shadow.querySelector('iframe');}
    };
    controllers.set(scope,controller);
    mount();
    reduced.addEventListener('change', () => {if(scope.hasAttribute('data-interactive'))restore();else reset();});
    nativeDocument.addEventListener('visibilitychange', () => {if(nativeDocument.hidden&&previewMode)finishMotionOnce();});
    nativeWindow.addEventListener('pagehide', () => {if(previewMode)finishMotionOnce();});
    if(scope.hasAttribute('data-interactive')) {activate();particlePreview();}
    return controller;
  }
  function mount(scope) {return init(scope);}
  function mountAll(root=document) {root.querySelectorAll('.demo-scope[data-demo-kind]').forEach(mount);}
  window.VibeDemos={register:(kind,installer)=>installers.set(kind,installer),init,mount,mountAll};
})();
