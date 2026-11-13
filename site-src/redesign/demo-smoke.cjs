/* Node DOM model: source initialization only, never a browser acceptance test.
   Input JSON is produced by demos.smoke_fixture(). No network or dependencies. */
'use strict';
const fs=require('node:fs'),vm=require('node:vm');
const data=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
function simple(el,selector){
  if(selector==='*')return true;
  if(!el||!selector)return false;
  selector=selector.replace(/:not\(([^)]+)\)/g,(_,s)=>simple(el,s)?'!NO!':'');
  selector=selector.replace(/:checked/g,()=>el.checked?'':'!NO!');
  selector=selector.replace(/:last-child/g,()=>el.parentNode?.children.at(-1)===el?'':'!NO!');
  selector=selector.replace(/:first-child/g,()=>el.parentNode?.children[0]===el?'':'!NO!');
  if(selector.includes('!NO!'))return false;
  for(const m of selector.matchAll(/\[([^\]=~^$*]+)(?:([~^$*]?=)["']?([^"'\]]*)["']?)?\]/g)){
    const value=el.getAttribute(m[1]);if(value===null)return false;
    if(m[2]&&!(m[2]==='^='?value.startsWith(m[3]):m[2]==='$='?value.endsWith(m[3]):m[2]==='*='?value.includes(m[3]):value===m[3]))return false;
  }
  selector=selector.replace(/\[[^\]]+\]/g,'');
  const tag=selector.match(/^[a-z][\w-]*/i);if(tag&&el.tagName.toLowerCase()!==tag[0].toLowerCase())return false;
  for(const m of selector.matchAll(/([.#])([\w-]+)/g))if(m[1]==='#'?el.id!==m[2]:!el.classList.contains(m[2]))return false;
  return true;
}
function matches(el,selector){
  return selector.split(',').some(part=>{
    const tokens=part.trim().replace(/\s*>\s*/g,' > ').split(/\s+(?![^\[]*\])/).filter(Boolean);
    let node=el;if(!simple(node,tokens.pop()))return false;
    while(tokens.length){let token=tokens.pop();if(token==='>'){node=node.parentNode;if(!simple(node,tokens.pop()))return false;}else{node=node.parentNode;while(node&&!simple(node,token))node=node.parentNode;if(!node)return false;}}
    return true;
  });
}
class Element{
 constructor(tag,attrs={},children=[]){this.tagName=tag.toUpperCase();this.attrs={...attrs};this.children=[];this.listeners=new Map();this.value=attrs.value||'';this.checked='checked'in attrs;this.hidden='hidden'in attrs;this.scrollTop=0;this.clientHeight=136;this.clientWidth=320;this.scrollHeight=1000;this.style={setProperty(){},removeProperty(){}};this.classList={contains:c=>(this.attrs.class||'').split(' ').includes(c),add:(...cs)=>this.attrs.class=[...new Set((this.attrs.class||'').split(' ').concat(cs))].join(' '),remove:(...cs)=>this.attrs.class=(this.attrs.class||'').split(' ').filter(c=>!cs.includes(c)).join(' '),toggle:(c,on)=>{const next=on===undefined?!this.classList.contains(c):on;next?this.classList.add(c):this.classList.remove(c);return next;}};children.forEach(c=>this.append(make(c)));if(tag==='select'){const selected=this.children.find(c=>c.getAttribute('selected')!==null)||this.children[0];this.value=selected?.getAttribute('value')||'';}this.dataset=new Proxy({},{get:(_,k)=>this.attrs['data-'+String(k).replace(/[A-Z]/g,c=>'-'+c.toLowerCase())],set:(_,k,v)=>(this.attrs['data-'+String(k).replace(/[A-Z]/g,c=>'-'+c.toLowerCase())]=String(v),true)});}
 get id(){return this.attrs.id||'';}get className(){return this.attrs.class||'';}set className(v){this.attrs.class=v;}
 get rows(){return this.querySelectorAll('tr');}get cells(){return this.children.filter(c=>['TD','TH'].includes(c.tagName));}get tHead(){return this.querySelector('thead');}
 get firstElementChild(){return this.children[0];}get lastElementChild(){return this.children.at(-1);}get nextElementSibling(){return this.parentNode?.children[this.parentNode.children.indexOf(this)+1];}get previousElementSibling(){return this.parentNode?.children[this.parentNode.children.indexOf(this)-1];}
 get innerHTML(){return '';}set innerHTML(v){this.children=[];}get textContent(){return this.attrs._text||this.children.map(x=>x.textContent).join('');}set textContent(v){this.attrs._text=String(v);this.children=[];}
 getAttribute(k){return Object.hasOwn(this.attrs,k)?this.attrs[k]:null;}setAttribute(k,v){this.attrs[k]=String(v);}removeAttribute(k){delete this.attrs[k];}
 append(...els){els.forEach(el=>{el.remove();el.parentNode=el.parentElement=this;this.children.push(el);});}appendChild(el){this.append(el);return el;}
 insertBefore(el,ref){el.remove();el.parentNode=el.parentElement=this;const i=this.children.indexOf(ref);this.children.splice(i<0?this.children.length:i,0,el);}
 remove(){if(this.parentNode){this.parentNode.children=this.parentNode.children.filter(x=>x!==this);this.parentNode=this.parentElement=null;}}
 querySelectorAll(s){const result=[];for(const el of this.children){if(matches(el,s))result.push(el);result.push(...el.querySelectorAll(s));}return result;}querySelector(s){return this.querySelectorAll(s)[0]||null;}closest(s){for(let e=this;e;e=e.parentNode)if(matches(e,s))return e;return null;}matches(s){return matches(this,s);}contains(el){return el===this||this.children.some(c=>c.contains(el));}
 addEventListener(k,fn){const a=this.listeners.get(k)||[];a.push(fn);this.listeners.set(k,a);}removeEventListener(){}focus(){}select(){}getBoundingClientRect(){return {top:0,left:0,bottom:100,right:200,width:200,height:100};}setPointerCapture(){}animate(){return {cancel(){}};}
}
function make(n){return new Element(n.tag,n.attrs,n.children);}
const installers=new Map();const context={window:{VibeDemos:{register:(k,fn)=>installers.set(k,fn)}},performance,console,Event,Math};
vm.createContext(context);for(const source of Object.values(data.sources))vm.runInContext(source,context);
let total=0;const errors=[];
for(const row of data.demos){
 try{
  const body=make(row.node),root=new Element('root',{},[]);root.append(body);
  const doc={body,querySelector:s=>root.querySelector(s),querySelectorAll:s=>root.querySelectorAll(s),getElementById:id=>root.querySelector('#'+id),createElement:t=>new Element(t),addEventListener(){},get activeElement(){return body;},hidden:false};
  let id=0;const timers=new Set();const schedule=()=>{timers.add(++id);return id;};const clear=n=>timers.delete(n);
  const env={scope:{dataset:{demoSection:row.section}},document:doc,window:{},performance,toast(){},matchMedia:()=>({matches:false,addEventListener(){}}),setTimeout:schedule,setInterval:schedule,requestAnimationFrame:schedule,clearTimeout:clear,clearInterval:clear,cancelAnimationFrame:clear,animate:(el,k,o)=>el.animate(k,o)};
  installers.get(row.kind)(env);timers.clear();total++;
 }catch(error){errors.push(row.anchor+': '+error.stack);}
}
if(errors.length){console.error(errors.join('\n'));process.exit(1);}console.log('Initialized '+total+' original demos in a Node DOM model; no browser or visual claim.');

const assert=require('node:assert/strict');
function interactiveModel(anchor, reduced=false) {
 const row=data.demos.find(row=>row.anchor===anchor),body=make(row.node),root=new Element('root');root.append(body);
 let focused=body;const delegates=new Map(),navigated=[];
 context.location={assign:url=>navigated.push(url)};
 Element.prototype.focus=function(){focused=this;};
 const doc={body,querySelector:s=>root.querySelector(s),querySelectorAll:s=>root.querySelectorAll(s),getElementById:id=>root.querySelector('#'+id),createElement:t=>new Element(t),addEventListener:(type,fn)=>{const a=delegates.get(type)||[];a.push(fn);delegates.set(type,a);},get activeElement(){return focused;},hidden:false};
 let id=0;
 const timeouts=new Map();
 const schedule=(callback,delay)=>{timeouts.set(++id,{callback,delay});return id;};
 const env={scope:{dataset:{demoSection:row.section}},document:doc,window:{},performance,toast(){},
  matchMedia:()=>({matches:reduced,addEventListener(){}}),setTimeout:schedule,setInterval:()=>++id,
  requestAnimationFrame:()=>++id,clearTimeout:timer=>timeouts.delete(timer),clearInterval(){},cancelAnimationFrame(){},animate:(el,k,o)=>el.animate(k,o)};
 installers.get(row.kind)(env);
 function fire(target,type,properties={}){const event={target,currentTarget:target,preventDefault(){},stopPropagation(){},...properties};for(const fn of target.listeners.get(type)||[])fn(event);target['on'+type]?.(event);for(const fn of delegates.get(type)||[])fn(event);}
 return {root,body,doc,fire,navigated,timeouts,get focused(){return focused;},
  flushTimeouts(){const pending=[...timeouts.values()];timeouts.clear();pending.forEach(timer=>timer.callback());}};
}
const cmd=interactiveModel('c-cmdk'),panel=cmd.doc.getElementById('cmdk'),input=cmd.doc.getElementById('cmdkInput'),list=cmd.doc.getElementById('cmdkList');
assert.equal(JSON.parse(panel.dataset.demoCommands).length,70);
cmd.fire(cmd.root.querySelector('[data-cmd="openCmdk"]'),'click');
assert(panel.classList.contains('show'));assert.equal(list.querySelectorAll('.cmdk-item').length,8);assert.equal(cmd.focused,input);
cmd.fire(input,'keydown',{key:'ArrowDown'});assert(list.querySelectorAll('.cmdk-item')[1].classList.contains('sel'));
cmd.fire(input,'keydown',{key:'ArrowUp'});assert(list.querySelectorAll('.cmdk-item')[0].classList.contains('sel'));
input.value='stepper';cmd.fire(input,'input');assert.equal(list.querySelectorAll('.cmdk-item').length,1);assert(list.textContent.includes(JSON.parse(panel.dataset.demoCommands).find(command=>command.keys.includes('stepper')).name));
cmd.fire(input,'keydown',{key:'Enter'});assert.equal(cmd.navigated.at(-1),'../../components/stepper/');assert(!panel.classList.contains('show'));
cmd.fire(cmd.root.querySelector('[data-cmd="openCmdk"]'),'click');input.value='__no_existing_source_name__';cmd.fire(input,'input');assert.equal(list.querySelectorAll('.cmdk-item').length,0);assert.equal(list.querySelector('.cmdk-empty').textContent,'没有匹配的组件');
const count=cmd.navigated.length;cmd.fire(input,'keydown',{key:'Enter'});assert.equal(cmd.navigated.length,count);cmd.fire(input,'keydown',{key:'Escape'});assert(!panel.classList.contains('show'));
console.log('Command palette: 70 real candidates; open/filter/arrows/Enter/Escape/no-match passed.');
const modal=interactiveModel('e-overlay-modal'),open=modal.root.querySelector('[data-action="open"]'),shade=modal.root.querySelector('.overlay-shade');
modal.fire(open,'click');assert.equal(shade.hidden,false);assert.equal(open.inert,true);
const focusables=shade.querySelectorAll('button:not([disabled]),[tabindex]:not([tabindex="-1"])');assert(focusables.length>0);
focusables.at(-1).focus();modal.fire(focusables.at(-1),'keydown',{key:'Tab',shiftKey:false});assert.equal(modal.focused,focusables[0]);
modal.fire(focusables[0],'keydown',{key:'Tab',shiftKey:true});assert.equal(modal.focused,focusables.at(-1));
modal.fire(focusables.at(-1),'keydown',{key:'Escape'});assert.equal(shade.hidden,true);assert.equal(open.inert,false);
console.log('Motion modal: local sibling inert; Tab/Shift+Tab loop; Escape/restore passed.');

const uiModal=interactiveModel('c-modal');
const modalTrigger=uiModal.root.querySelector('[data-cmd="openModal"]');
modalTrigger.isConnected=true;modalTrigger.focus();
uiModal.fire(modalTrigger,'click');
assert.equal(uiModal.doc.getElementById('modal').style.display,'flex');
uiModal.fire(uiModal.root.querySelector('.modal-actions button'),'keydown',{key:'Escape'});
assert.equal(uiModal.doc.getElementById('modal').style.display,'none');
assert.equal(uiModal.focused,modalTrigger);
const skeleton=interactiveModel('c-skeleton');
const skeletonCard=skeleton.root.querySelector('.ds-skeleton-card');
const skeletonImage=skeletonCard.querySelector('img');
assert.equal(skeletonCard.getAttribute('aria-busy'),'true');
assert([...skeleton.timeouts.values()].some(timer=>timer.delay===1400));
skeletonImage.complete=true;skeletonImage.naturalWidth=640;
skeleton.flushTimeouts();
assert(skeletonCard.classList.contains('is-loaded'));
assert.equal(skeletonCard.getAttribute('aria-busy'),'false');
assert.equal(skeletonCard.querySelector('.ds-skeleton-content').getAttribute('aria-hidden'),'false');
const reducedSkeleton=interactiveModel('c-skeleton',true);
const reducedCard=reducedSkeleton.root.querySelector('.ds-skeleton-card');
assert.equal(reducedSkeleton.timeouts.size,0);
reducedSkeleton.fire(reducedCard.querySelector('img'),'load');
assert(reducedCard.classList.contains('is-loaded'));
const carousel=interactiveModel('c-carousel');
carousel.fire(carousel.doc.getElementById('carNext'),'click');
assert.equal(carousel.doc.getElementById('carTrack').style.transform,'translateX(-100%)');
assert.equal(carousel.doc.getElementById('carDots').children[1].getAttribute('aria-current'),'true');
carousel.fire(carousel.doc.getElementById('carPause'),'click');
assert.equal(carousel.doc.getElementById('carPause').getAttribute('aria-pressed'),'true');
carousel.fire(carousel.doc.getElementById('carPrev'),'click');
assert.equal(carousel.doc.getElementById('carDots').children[0].getAttribute('aria-current'),'true');
const reveal=interactiveModel('e-scroll-reveal');
const scroller=reveal.root.querySelector('.mini-scroll');
const revealCards=reveal.root.querySelectorAll('.ds-reveal-card');
scroller.getBoundingClientRect=()=>({top:0,bottom:380});
revealCards.forEach((card,index)=>{
 card.classList.remove('ds-revealed');
 card.getBoundingClientRect=()=>({top:150+250*index,bottom:350+250*index});
});
reveal.fire(scroller,'scroll');
assert.deepEqual(revealCards.map(card=>card.classList.contains('ds-revealed')),[true,false,false]);
revealCards[1].getBoundingClientRect=()=>({top:300,bottom:500});
reveal.fire(scroller,'scroll');
assert.deepEqual(revealCards.map(card=>card.classList.contains('ds-revealed')),[true,true,false]);
const grid=interactiveModel('g-layout-grid');
grid.fire(grid.root.querySelector('[data-guide-mode="1"]'),'click');
assert.equal(grid.root.querySelector('.guide-card-stage').dataset.mode,'1');
grid.fire(grid.root.querySelector('[data-guide-mode="0"]'),'click');
assert.equal(grid.root.querySelector('.guide-card-stage').dataset.mode,'0');
console.log('Batch B: skeleton loading/reduced motion, carousel arrows/pause/dots, independent scroll reveal and grid state controls passed.');
