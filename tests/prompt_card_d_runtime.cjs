/* Execute production copy and IntersectionObserver logic with a controlled DOM.
   No browser, network, window automation or listening port is used. */
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const script = fs.readFileSync('site-src/redesign/site.js','utf8');
const start = script.indexOf('  async function writeClipboard(');
const end = script.indexOf("  document.addEventListener('keydown'",start);
assert.ok(start > 0 && end > start);

function boot({observer = true, mobile = true} = {}) {
  const timers = new Map(), announcements = [], clipboard = [], mediaListeners = [], listeners = {};
  let timerId = 0, io, context;
  const document = {activeElement:null,execCommand:() => false};
  function element(label = '', source) {
    const classes = new Set();
    return {
      textContent:label, dataset:source ? {copySource:source} : {}, style:{}, hidden:false, inert:false,
      rect:{top:1000,bottom:1600,width:104,height:44},
      classList:{add:name => classes.add(name),remove:name => classes.delete(name),contains:name => classes.has(name)},
      getBoundingClientRect() { return this.rect; },
      setAttribute() {}, remove() {}, select() {}, matches() {return false;},
      focus(options) {document.activeElement = this; this.focusOptions = options;},
      hasAttribute(name) {return name === 'data-copy-source' && !!source;},
      closest(selector) {return selector === 'button' ? this : null;}
    };
  }
  const cardButton = element('复制','copy-prompt'), barButton = element('复制提示词','copy-prompt');
  const card = element(), bar = element(), english = element('复制英文名','entry-english');
  card.querySelector = () => cardButton;
  bar.contains = node => node === barButton;
  const payload = '提示词全文\n\n验收要求：\n1. 键盘可以操作。\n2. 焦点应归还。';
  const sources = {'copy-prompt':{textContent:payload},'entry-english':{textContent:'Command Palette'}};
  document.getElementById = id => sources[id];
  document.createElement = () => element();
  document.body = {append() {}};
  document.addEventListener = (type,callback) => {listeners[type] = callback;};
  document.activeElement = cardButton;
  const media = {matches:mobile,addEventListener(type,callback) {mediaListeners.push(callback);}};
  const window = {innerHeight:900,addEventListener(type,callback) {listeners[type] = callback;}};
  const env = {
    document, window, mobile:media, search:{open:false}, drawer:{open:false},
    $:selector => ({'.prompt-card':card,'.bottom-bar':bar}[selector]),
    $$:() => [cardButton,barButton],
    announce:message => announcements.push(message),
    setTimeout(callback,delay) {const id = ++timerId; timers.set(id,{callback,delay}); return id;},
    clearTimeout:id => timers.delete(id),
    navigator:{clipboard:{async writeText(value) {clipboard.push(value);}}}
  };
  if (observer) env.IntersectionObserver = class {
    constructor(callback,options) {this.callback=callback; this.options=options; io=this;}
    observe(target) {this.target=target;}
  };
  context = vm.createContext(env);
  vm.runInContext(script.slice(start,end),context);
  return {
    card,bar,cardButton,barButton,english,document,media,mediaListeners,listeners,
    announcements,clipboard,payload,env,timers,io,
    click(button) {listeners.click({target:button});},
    intersect(visible) {io.callback([{target:card,isIntersecting:visible}]);},
    restore() {
      const pending = [...timers].filter(([,timer]) => timer.delay === 2000);
      assert.equal(pending.length,1);
      for (const [id,timer] of pending) {timers.delete(id); timer.callback();}
    }
  };
}
const flush = async () => {for (let i = 0; i < 12; i++) await Promise.resolve();};

(async () => {
  const app = boot();
  assert.equal(app.io.target,app.card);
  assert.equal(app.io.options.threshold,0);
  assert.equal(app.bar.hidden,false,'Offscreen mobile prompt keeps the action available');
  assert.equal(app.bar.inert,false);
  app.document.activeElement = app.barButton;
  app.intersect(true);
  assert.equal(app.bar.hidden,true);
  assert.equal(app.bar.inert,true,'Hidden actions must leave the keyboard tab sequence');
  assert.equal(app.document.activeElement,app.cardButton);
  assert.equal(app.cardButton.focusOptions.preventScroll,true);
  app.intersect(false);
  assert.equal(app.bar.hidden,false);
  assert.equal(app.bar.inert,false);
  app.card.rect = {top:200,bottom:700};
  app.listeners.resize();
  assert.equal(app.bar.hidden,true,'Resize measures the visible prompt again');
  app.media.matches = false;
  app.card.rect = {top:1000,bottom:1700};
  app.mediaListeners.forEach(callback => callback());
  assert.equal(app.bar.hidden,true,'Desktop never exposes the bottom bar');
  app.media.matches = true;
  app.mediaListeners.forEach(callback => callback());
  assert.equal(app.bar.hidden,false);

  app.click(app.cardButton);
  await flush();
  assert.deepEqual(app.clipboard,[app.payload],'Copy the unchanged hidden payload, including both acceptance rows');
  assert.equal(app.announcements.at(-1),'已复制');
  assert(app.card.classList.contains('is-copied'));
  for (const button of [app.cardButton,app.barButton]) {
    assert.equal(button.textContent,'✓ 已复制');
    assert(button.classList.contains('is-copied'));
  }
  app.click(app.barButton);
  await flush();
  assert.equal(app.clipboard.length,2);
  assert.equal(app.timers.size,1,'Repeated copy resets one shared 2000ms timer');
  app.restore();
  assert(!app.card.classList.contains('is-copied'));
  assert.equal(app.cardButton.textContent,'复制');
  assert.equal(app.barButton.textContent,'复制提示词');
  assert(!app.cardButton.classList.contains('is-copied'));

  app.click(app.english);
  await flush();
  assert.equal(app.clipboard.at(-1),'Command Palette');
  assert(!app.card.classList.contains('is-copied'),'Secondary copy does not claim prompt success');

  const failed = boot();
  failed.env.navigator.clipboard.writeText = async () => {throw new Error('Denied');};
  failed.click(failed.cardButton);
  await flush();
  assert(!failed.card.classList.contains('is-copied'));
  assert.equal(failed.cardButton.textContent,'复制');
  assert.match(failed.announcements.at(-1),/复制未完成/);
  failed.document.execCommand = command => command === 'copy';
  failed.click(failed.cardButton);
  await flush();
  assert(failed.card.classList.contains('is-copied'),'Successful fallback also triggers the card state');
  assert.equal(failed.announcements.at(-1),'已复制');

  const fallback = boot({observer:false});
  assert.equal(fallback.bar.hidden,false);
  fallback.card.rect = {top:200,bottom:700};
  fallback.listeners.scroll();
  assert.equal(fallback.bar.hidden,true);
  assert.equal(fallback.bar.inert,true);
  fallback.card.rect = {top:-700,bottom:-1};
  fallback.listeners.scroll();
  assert.equal(fallback.bar.hidden,false);
  assert.equal(fallback.bar.inert,false);
  const desktop = boot({mobile:false});
  assert.equal(desktop.bar.hidden,true);
  assert.equal(desktop.bar.inert,true);
  console.log('Option D: payload, both copy controls, purple state, 2000ms reset, failure/fallback, aria announcement, IO, inert, focus, resize and breakpoints passed.');
})().catch(error => {console.error(error);process.exitCode = 1;});
