/* Execute the shared state callbacks and actual runtime with controlled DOM/timers.
   Rendering and hit testing are covered separately by the headless check. */
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

class Element {
  constructor(tag = 'div') {
    this.tagName = tag.toUpperCase(); this.dataset = {}; this.style = {};
    this.attributes = new Map(); this.listeners = new Map(); this.children = [];
    this.classes = new Set(); this.classList = {
      add:key => this.classes.add(key), remove:key => this.classes.delete(key),
      contains:key => this.classes.has(key)
    };
  }
  setAttribute(key, value) { this.attributes.set(key,String(value)); }
  getAttribute(key) { return this.attributes.get(key) ?? null; }
  hasAttribute(key) { return this.attributes.has(key); }
  removeAttribute(key) { this.attributes.delete(key); }
  addEventListener(type, fn) { this.listeners.set(type,[...(this.listeners.get(type) || []),fn]); }
  fire(type) { for (const fn of this.listeners.get(type) || []) fn(); }
  append(...children) { this.children.push(...children); }
  before(wrapper) { this.wrapper = wrapper; }
  closest() { return null; }
  querySelectorAll() { return []; }
  querySelector() { return null; }
  getBoundingClientRect() { return {width:94,height:40}; }
  dispatchEvent() {}
}

function testStates(kind) {
  let fields, buttons, root;
  function fresh() {
    fields = ['input','textarea','select','search','checkbox','radio','switch','slider'].includes(kind)
      ? [new Element(kind === 'textarea' ? 'textarea' : kind === 'select' ? 'select' : 'input')] : [];
    fields.forEach(field => {
      field.value = '已输入的内容'; field.checked = true;
      field.setAttribute('aria-label',kind === 'textarea' ? '备注' : kind === 'select' ? '城市' : kind === 'search' ? '搜索词' : '姓名');
    });
    buttons = kind === 'button' ? Array.from({length:4}, () => new Element('button'))
      : kind === 'tabs' ? Array.from({length:3}, () => new Element('button'))
      : kind === 'search' ? [new Element('button')] : [];
    root = new Element();
    root.querySelectorAll = selector => {
      if (selector === '.btn') return kind === 'button' ? buttons : [];
      if (selector === 'button,input,select,textarea') return [...buttons,...fields];
      if (selector === 'input,textarea,select') return fields;
      if (selector === 'input[type="checkbox"],input[type="radio"]') return ['checkbox','radio','switch'].includes(kind) ? fields : [];
      if (selector.startsWith('input:not(')) return fields;
      return [];
    };
    root.querySelector = selector => selector === '[role="tablist"]' && kind === 'tabs' ? new Element() : null;
  }
  fresh();
  const scope = new Element(), picker = new Element();
  const options = ['free','disabled','loading','error'].map(state => {
    const option = new Element('button'); option.dataset = {state,stateClass:'force-' + state}; return option;
  });
  picker.closest = () => ({querySelector:() => scope});
  picker.querySelectorAll = selector => selector === '[data-state]' ? options : [];
  const controller = {get root() {return root;},restore:fresh};
  const site = fs.readFileSync('site-src/redesign/site.js','utf8');
  const start = site.indexOf("  $$('.state-picker')");
  const end = site.indexOf("  $$('[data-demo-replay]",start);
  vm.runInNewContext(site.slice(start,end), {
    $$:() => [picker], window:{VibeDemos:{init:() => controller}},
    document:{createElement:tag => new Element(tag)}, Event
  });
  if (['checkbox','radio','switch'].includes(kind)) fields[0].checked = false;
  options[1].fire('click');
  if (['checkbox','radio','switch'].includes(kind)) assert.equal(fields[0].checked,false,'Disabling must preserve the current value');
  assert.equal(scope.inert,false,'Native disabled cursors must remain reachable');
  assert.ok([...fields,...buttons].filter((_,index) => kind !== 'tabs' || index === 2).every(el => el.disabled));
  if (kind === 'tabs') assert.ok(!buttons[0].disabled && !buttons[1].disabled && buttons[2].disabled);
  options[0].fire('click');
  assert.ok([...fields,...buttons].every(el => !el.disabled),'Free state restores native input');
  if (kind === 'button') {
    options[2].fire('click');
    for (const button of buttons) {
      assert.ok(button.disabled); assert.equal(button.style.width,'94px');
      assert.equal(button.getAttribute('aria-busy'),'true');
      assert.match(button.innerHTML,/提交中…/);
    }
    options[0].fire('click'); assert.ok(buttons.every(button => !button.disabled && !button.hasAttribute('aria-busy')));
  }
  if (['input','textarea','select','search'].includes(kind)) {
    fields[0].value = '切换前保留的输入';
    options[3].fire('click');
    assert.equal(fields[0].value,'切换前保留的输入');
    assert.equal(fields[0].getAttribute('aria-invalid'),'true');
    const error = fields[0].wrapper.children[1];
    assert.equal(fields[0].getAttribute('aria-describedby'),error.id);
    assert.ok(error.textContent.length > 5);
    options[0].fire('click');
    assert.equal(fields[0].hasAttribute('aria-invalid'),false);
    assert.equal(fields[0].value,'切换前保留的输入');
  }
}
for (const kind of ['button','input','textarea','select','search','checkbox','radio','switch','slider','tabs']) testStates(kind);

// Real demo-runtime lifecycle, including CSS timing and JS matchMedia facades.
const timeouts = new Map(), intervals = new Map(), frames = new Map();
let serial = 0, sourceMedia, replayCount = 0;
const schedule = collection => (fn,ms) => { collection.set(++serial,{fn,ms}); return serial; };
const clear = collection => id => collection.delete(id);
const media = new Element(); media.matches = true;
const document = new Element();
document.createElement = tag => new Element(tag);
const window = new Element();
Object.assign(window, {matchMedia:() => media, setTimeout:schedule(timeouts), clearTimeout:clear(timeouts),
  setInterval:schedule(intervals), clearInterval:clear(intervals),
  requestAnimationFrame:schedule(frames), cancelAnimationFrame:clear(frames)});
vm.runInNewContext(fs.readFileSync('site-src/redesign/demo-runtime.js','utf8'), {
  window,document,performance,AbortController,Number,Event,CustomEvent:Event,
});
function scopeFixture(interactive = true, withFrame = false) {
  const scope = new Element(), shadow = new Element(), template = new Element('template');
  scope.dataset.demoKind = 'fixture';
  if (interactive) scope.setAttribute('data-interactive','');
  template.matches = selector => selector === 'template[data-demo-template]';
  template.dataset = {demoCss:'./demo.css'};
  template.content = {cloneNode() {
    const body = new Element();
    body.animation = {pause() {this.paused = true;},effect:{getComputedTiming:() => ({endTime:8000}),getTiming:() => ({duration:8000,delay:0})}};
    body.getAnimations = () => [body.animation];
    shadow.body = body; return body;
  }};
  shadow.replaceChildren = () => { shadow.children = []; };
  const frame = withFrame ? new Element('iframe') : null;
  if (frame) {
    frame.src = './gallery.html'; frame.setAttribute('src','./gallery.html');
    frame.contentDocument = {querySelector:() => ({click() {frame.advances = (frame.advances || 0) + 1;}})};
  }
  shadow.querySelectorAll = selector => selector === 'iframe' && frame ? [frame] : [];
  shadow.querySelector = selector => selector === '.demo-root' ? shadow.body : selector === 'iframe' ? frame : null;
  shadow.contains = child => shadow.children.includes(child);
  template.dataset.demoLoop = 'true';
  scope.children = [template]; scope.attachShadow = () => shadow; scope.shadowRoot = shadow;
  return scope;
}
window.VibeDemos.register('fixture', env => {
  sourceMedia = env.matchMedia('(prefers-reduced-motion: reduce)');
  env.setInterval(() => {},500); env.requestAnimationFrame(() => {});
  return {preview() { replayCount++; }};
});
const scope = scopeFixture();
const demo = window.VibeDemos.init(scope);
assert.equal(sourceMedia.matches,true);
assert.equal(intervals.size,0,'Reduced motion initialization must not install an automatic loop');
assert.equal(frames.size,0,'Reduced motion initialization must not request moving frames');
assert.ok(!scope.hasAttribute('data-demo-motion-once'));
assert.equal(demo.preview(),true);
assert.ok(scope.hasAttribute('data-demo-motion-once'));
assert.equal(sourceMedia.matches,false,'Explicit playback releases source JS guards');
assert.equal(replayCount,1); assert.equal(intervals.size,1);
assert.equal(demo.motionDuration,8100,'One long CSS cycle must complete');
const finish = [...timeouts.values()].find(timer => timer.ms === 8100);
finish.fn();
assert.ok(!scope.hasAttribute('data-demo-motion-once'));
assert.equal(sourceMedia.matches,true);
assert.equal(intervals.size,0); assert.equal(frames.size,0);
demo.preview(.25);
assert.equal(demo.motionDuration,32400,'Slow playback includes a complete quarter-speed cycle');
demo.reset();
assert.equal(timeouts.size,0); assert.equal(intervals.size,0); assert.equal(frames.size,0);
assert.ok(!scope.hasAttribute('data-demo-motion-once'));
const gallery = scopeFixture(false);
assert.equal(window.VibeDemos.init(gallery).preview(),true,'Explicit gallery play is permitted under reduce');
document.hidden = true; document.fire('visibilitychange');
assert.ok(!gallery.hasAttribute('data-demo-motion-once'));
assert.equal(intervals.size,0); assert.equal(frames.size,0);
demo.step();
assert.equal(demo.supportsStep,true);
assert.ok(scope.hasAttribute('data-demo-motion-step'));
assert.ok(!scope.hasAttribute('data-demo-motion-once'));
assert.equal(scope.shadowRoot.body.animation.paused,true);
assert.equal(scope.shadowRoot.body.animation.currentTime,2000);
demo.step(); assert.equal(scope.shadowRoot.body.animation.currentTime,4000);
assert.equal(intervals.size,0); assert.equal(frames.size,0);
demo.reset(); assert.ok(!scope.hasAttribute('data-demo-motion-step'));
media.matches = false;
demo.restore();
assert.equal(intervals.size,1,'Normal-motion source behavior remains enabled');
demo.reset();
media.matches = true;
const framedScope = scopeFixture(true,true), framed = window.VibeDemos.init(framedScope);
assert.equal(framed.supportsSlow,false);
framed.preview();
const frame = framedScope.shadowRoot.querySelector('iframe');
frame.src = './detail.html';
[...timeouts.values()].find(timer => timer.ms === 8100).fn();
assert.equal(frame.src,'./detail.html','Playback completion preserves the after page');
framed.step(); assert.equal(frame.advances,1,'Manual navigation remains available after playback');
console.log('10 state callbacks and reduced-motion runtime lifecycle passed.');
