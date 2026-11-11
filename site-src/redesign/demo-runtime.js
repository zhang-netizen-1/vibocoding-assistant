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
    const virtualNow=()=>playbackStart+(performance.now()-playbackStart)*playbackSpeed;
    function applyPlayback(){body?.getAnimations?.({subtree:true}).forEach(animation=>{animation.playbackRate=playbackSpeed;});}
    let lifetime = null, implementation = null, body = null, dead = false;
    const timers = new Set(), intervals = new Set(), frames = new Set(), cleanup = [];
    const nativeWindow = window, nativeDocument = document;
    function clearResources() {
      lifetime?.abort(); lifetime = null;
      timers.forEach(id => nativeWindow.clearTimeout(id)); timers.clear();
      intervals.forEach(id => nativeWindow.clearInterval(id)); intervals.clear();
      frames.forEach(id => nativeWindow.cancelAnimationFrame(id)); frames.clear();
      cleanup.splice(0).forEach(dispose => dispose());
      shadow.getAnimations?.({subtree: true}).forEach(animation => animation.cancel());
      shadow.querySelectorAll('iframe').forEach(frame => {frame.src = 'about:blank';});
      implementation = null;
    }
    const setTimeout = (fn, ms, ...args) => {
      const id = nativeWindow.setTimeout(() => {timers.delete(id); if (!dead) {fn(...args);applyPlayback();}}, ms/playbackSpeed);
      timers.add(id); return id;
    };
    const clearTimeout = id => {nativeWindow.clearTimeout(id); timers.delete(id);};
    const setInterval = (fn, ms, ...args) => {const id = nativeWindow.setInterval(() => {if (!dead) {fn(...args);applyPlayback();}}, ms/playbackSpeed); intervals.add(id); return id;};
    const clearInterval = id => {nativeWindow.clearInterval(id); intervals.delete(id);};
    const requestAnimationFrame = fn => {
      const id = nativeWindow.requestAnimationFrame(now => {frames.delete(id); if (!dead) {fn(virtualNow());applyPlayback();}});
      frames.add(id); return id;
    };
    const cancelAnimationFrame = id => {nativeWindow.cancelAnimationFrame(id); frames.delete(id);};
    function matchMedia(query) {
      const media = nativeWindow.matchMedia(query);
      return {
        get matches() {return previewMode && query.includes('pointer: coarse') ? false : media.matches;}, media: media.media,
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
      fitGallery();
      link.addEventListener('load',fitGallery,{once:true});
      const miniStage=scope.closest('.mini-stage');
      if(miniStage&&typeof ResizeObserver!=='undefined'){const observer=new ResizeObserver(()=>{if(!scope.isConnected){observer.disconnect();return;}fitGallery();});observer.observe(miniStage);cleanup.push(()=>observer.disconnect());}
    }
    function fitGallery() {
      const stage=scope.closest('.mini-stage');
      if(!stage||!body)return;
      const style=getComputedStyle(stage),width=scope.clientWidth||stage.clientWidth;
      const height=stage.clientHeight-parseFloat(style.paddingTop||0)-parseFloat(style.paddingBottom||0);
      body.style.width='420px';body.style.zoom='1';
      const natural=Math.max(224,body.scrollHeight||224);
      const scale=Math.max(.1,Math.min(1,width/420,height>0?height/natural:1));
      body.style.zoom=String(scale);
      scope.style.display='flex';scope.style.alignItems='center';scope.style.justifyContent='center';
    }
    function preventExampleNavigation(event) {
      if (event.target.closest?.('a')) event.preventDefault();
    }
    function activate() {
      if (implementation) return implementation;
      dead = false; lifetime = new AbortController();
      const installer = installers.get(scope.dataset.demoKind);
      implementation = installer ? (installer({scope,document: localDocument,window: localWindow,matchMedia,
        setTimeout,clearTimeout,setInterval,clearInterval,requestAnimationFrame,cancelAnimationFrame,performance:{now:virtualNow},animate:(el,keys,options)=>{const opts=typeof options==='number'?{duration:options}:options;const animation=el.animate(keys,opts);animation.playbackRate=playbackSpeed;cleanup.push(()=>animation.cancel());return animation;},toast}) || {}) : {};
      // CSS animations run only after an explicit preview or inside detail.
      scope.dataset.demoPlaying = 'true';
      return implementation;
    }
    function reset() {
      dead = true;clearResources();previewMode=false;mount();
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
      const scroller = shadow.querySelector('.mini-scroll,.seq-scroll,.hidehead-scroll,.extra-header-scroll,.extra-section-scroll,.extra-highlight-scroll,.extra-snap-scroll,#bttPage,#infList,#vlList,.mini-layout');
      if (!scroller) return false;
      const start = virtualNow(), distance = Math.max(100, scroller.scrollHeight-scroller.clientHeight);
      function tick(now) {const p=Math.min(1,(now-start)/1050);scroller.scrollTop=distance*p;scroller.dispatchEvent(new Event('scroll'));if(p<1)requestAnimationFrame(tick);}
      requestAnimationFrame(tick);return true;
    }
    function previewPointers() {
      if(scope.dataset.demoCategory!=='依赖鼠标指针')return false;
      const target = shadow.querySelector('.micro-card,.cursor-wave,.magnet-wrap,.cf-stage,.trail-stage,.eyes-stage,.obj-stage,.extra-magnifier-art');
      if (!target) return false;
      // Pointer-only examples receive a deliberate virtual pointer path. Coarse
      // devices keep the source's own guard and receive an honest fallback.
      pointer(target, 'pointerenter', .25, .45);
      let step = 0;
      function move() {pointer(target,'pointermove',.5+Math.sin(step/7)*.3,.5+Math.cos(step/7)*.23);if((step+=playbackSpeed)<45)requestAnimationFrame(move);}
      requestAnimationFrame(move);return true;
    }
    function particlePreview() {
      const canvas = shadow.querySelector('.particles canvas,canvas.particle-canvas,canvas');
      if (!canvas) return false;
      const context = canvas.getContext('2d');if (!context) return false;
      const dots=Array.from({length:32},(_,i)=>({x:(i*71%616)+2,y:(i*53%256)+2,vx:(i%5-2)*.14,vy:(i%3-1)*.17,r:(i%3)+1}));
      const color=getComputedStyle(scope).getPropertyValue('--demo-primary').trim()||'#6D28D9';
      function draw() {context.clearRect(0,0,canvas.width,canvas.height);context.fillStyle=color;dots.forEach(d=>{context.beginPath();context.arc(d.x,d.y,d.r,0,Math.PI*2);context.fill();d.x=(d.x+d.vx*playbackSpeed+620)%620;d.y=(d.y+d.vy*playbackSpeed+260)%260;});if(!nativeWindow.matchMedia('(prefers-reduced-motion: reduce)').matches)requestAnimationFrame(draw);}
      draw();return true;
    }
    function preview(speed=1) {
      if (activePreview && activePreview !== controller) activePreview.reset();
      reset();activePreview=controller;playbackSpeed=speed===.25?.25:1;playbackStart=performance.now();
      if (scope.dataset.demoStatic === 'true') {toast('静态参考；请查看条目说明。');return false;}
      if (nativeWindow.matchMedia('(prefers-reduced-motion: reduce)').matches) {if(!scope.hasAttribute('data-interactive')){toast('已按系统设置减少动态；可进入条目查看演示状态。');return false;}toast('已切换演示状态；系统减少动态设置仍然生效。');}
      if(playbackSpeed!==1&&shadow.querySelector('iframe')){toast('此演示使用浏览器原生跨页转场；慢放不可用。');return false;}
      previewMode=true;
      const source=activate();
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
      if(edit){edit.dispatchEvent(new KeyboardEvent('keydown',{bubbles:true,key:'Enter'}));return true;}
      const frame=shadow.querySelector('iframe');
      if(frame){setTimeout(()=>{const link=frame.contentDocument?.querySelector('a');link?.click();},650);return true;}
      // CSS-only examples already run their source hover/keyframe rules. A
      // static reference reports its nature rather than implying a new effect.
      if (!stage && !shadow.querySelector('button,[data-cmd]')) toast('静态参考；请查看条目说明。');
      return true;
    }
    function restore(){reset();previewMode=false;playbackSpeed=1;playbackStart=performance.now();activate();particlePreview();}
    const controller={reset,restore,preview,root:shadow,get supportsSlow(){return !shadow.querySelector('iframe');}};controllers.set(scope,controller);mount();
    if(scope.hasAttribute('data-interactive')) {activate();particlePreview();}
    return controller;
  }
  function mount(scope) {return init(scope);}
  function mountAll(root=document) {root.querySelectorAll('.demo-scope[data-demo-kind]').forEach(mount);}
  window.VibeDemos={register:(kind,installer)=>installers.set(kind,installer),init,mount,mountAll};
})();
