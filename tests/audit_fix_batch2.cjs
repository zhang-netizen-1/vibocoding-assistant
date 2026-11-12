/* Exercise the actual site script using a minimal DOM and controlled network. */
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const searchEngine = require('../site-src/redesign/search.js');

function boot(prefix = '../../') {
  const nodes = new Map(), requests = [], clipboard = [], navigations = [];
  let document;
  class Element {
    constructor(tagName = 'DIV') {
      this.tagName = tagName; this.dataset = {}; this.style = {}; this.listeners = {};
      this.attributes = {}; this.value = ''; this.innerHTML = ''; this.open = false;
      this.classList = {toggle() {}, remove() {}};
    }
    addEventListener(type, listener) { (this.listeners[type] ||= []).push(listener); }
    fire(type, values = {}) {
      const event = {target:this, currentTarget:this, preventDefault() {this.defaultPrevented = true;},
        stopPropagation() {this.stopped = true;}, composedPath() {return [this.target];}, ...values};
      for (const listener of this.listeners[type] || []) listener(event);
      return event;
    }
    setAttribute(key, value) { this.attributes[key] = value; }
    removeAttribute(key) { delete this.attributes[key]; }
    hasAttribute(key) { return key in this.attributes; }
    focus() { document.activeElement = this; }
    showModal() { this.open = true; }
    close() { this.open = false; this.fire('close'); }
    contains(target) { return this === target; }
    querySelectorAll() { return []; }
    closest(selector) {
      if (selector === 'button' && this.tagName === 'BUTTON') return this;
      if (selector === '[data-copy-result]' && this.hasAttribute('data-copy-result')) return this;
      return null;
    }
    matches() { return false; }
    getBoundingClientRect() { return {width:120,height:40}; }
    scrollIntoView() { this.scrolled = true; }
  }
  for (const id of ['header','search-dialog','directory','search-input','search-body','nav-search','directory-toggle','live']) {
    nodes.set('#' + id, new Element(id === 'search-input' ? 'INPUT' : 'DIV'));
  }
  const dialog = nodes.get('#search-dialog');
  dialog.dataset = {indexUrl:prefix + 'assets/search-index.json?v=test', siteRoot:prefix};
  document = new Element(); document.body = new Element(); document.activeElement = new Element('BUTTON');
  document.querySelector = selector => {
    if (!nodes.has(selector) && selector.startsWith('#result-')) nodes.set(selector, new Element());
    return nodes.get(selector);
  };
  document.querySelectorAll = selector => selector === '.result-row'
    ? [...nodes].filter(([key]) => /^#result-\d+$/.test(key)).map(([,node]) => node) : [];
  const context = {document, HTMLElement:Element, VibeSearch:searchEngine, scrollY:120, scrollTo() {},
    matchMedia:() => ({matches:false,addEventListener() {}}), setTimeout:() => 1, clearTimeout() {},
    navigator:{clipboard:{async writeText(value) {clipboard.push(value);}}},
    location:{assign(value) {navigations.push(value);}},
    window:{VibeDemos:{mountAll() {}},addEventListener() {}},
    fetch(url) { return new Promise((resolve,reject) => requests.push({url,resolve,reject})); }};
  vm.runInNewContext(fs.readFileSync('site-src/redesign/site.js','utf8'), context);
  return {nodes,dialog,document,requests,clipboard,navigations,Element};
}
const flush = async () => { for (let i = 0; i < 12; i++) await Promise.resolve(); };
const payload = () => JSON.parse(fs.readFileSync('dist/assets/search-index.json','utf8'));

(async () => {
  const app = boot();
  const {nodes,dialog,document,requests,Element} = app;
  const input = nodes.get('#search-input'), body = nodes.get('#search-body');
  assert.equal(requests.length,0,'Initial page must not fetch the index');
  const trigger = document.activeElement;
  document.fire('keydown',{key:'/',target:trigger});
  assert.ok(dialog.open);
  assert.equal(requests.length,1);
  assert.equal(requests[0].url,'../../assets/search-index.json?v=test');
  assert.match(body.innerHTML,/正在加载/);
  input.value = '按钮'; input.fire('input');
  assert.equal(requests.length,1);
  nodes.get('#nav-search').fire('click');
  assert.equal(requests.length,1,'Concurrent open reuses the pending request');
  input.value = '按钮'; input.fire('input');
  const escape = dialog.fire('keydown',{key:'Escape',target:input});
  assert.ok(escape.defaultPrevented,'Prevent search input native Escape clearing');
  assert.equal(dialog.open,false);
  assert.equal(document.activeElement,trigger);
  requests[0].resolve({ok:true,json:async () => payload()}); await flush();
  assert.equal(dialog.open,false,'Pending request must not reopen dialog');
  assert.equal(document.activeElement,trigger);
  document.fire('keydown',{key:'k',ctrlKey:true,target:trigger});
  assert.equal(requests.length,1,'Reopening uses in-memory cache');
  assert.match(body.innerHTML,/常用搜法/);
  input.value = '按钮'; input.fire('input');
  assert.match(body.innerHTML,/<a class="result-name" href="\.\.\/\.\.\/components\/button\/"/);
  assert.match(body.innerHTML,/result-thumb/);
  nodes.set('#result-0',new Element());
  const arrow = dialog.fire('keydown',{key:'ArrowDown',target:input});
  assert.ok(arrow.defaultPrevented);
  assert.equal(input.attributes['aria-activedescendant'],'result-1');
  dialog.fire('keydown',{key:'ArrowUp',target:input});
  dialog.fire('keydown',{key:'Enter',target:input});
  assert.equal(app.navigations[0],'../../components/button/');
  const copy = new Element('BUTTON'); copy.dataset.copyResult = String(payload().entries.findIndex(e => e.zh === '按钮'));
  copy.setAttribute('data-copy-result',''); copy.textContent = '复制提示词';
  const click = dialog.fire('click',{target:copy}); await flush();
  assert.ok(click.stopped);
  assert.equal(app.clipboard[0],payload().entries[Number(copy.dataset.copyResult)].prompt);
  assert.equal(app.navigations.length,1,'Copy must not navigate');
  input.value = 'asdfgh'; input.fire('input');
  assert.match(body.innerHTML,/没有找到/);
  assert.doesNotMatch(body.innerHTML,/相近的名称/);
  assert.match(body.innerHTML,/换个说法/);
  assert.match(body.innerHTML,/按栏目找/);
  const example = new Element('BUTTON'); example.dataset.query = '浮起来';
  example.setAttribute('data-query',''); document.fire('click',{target:example});
  assert.equal(input.value,'浮起来');
  assert.match(body.innerHTML,/component-lift/);
  assert.equal(requests.length,1);
  dialog.fire('keydown',{key:'Escape',target:input});
  assert.equal(dialog.open,false);
  assert.equal(document.activeElement,trigger);

  const failed = boot('../../../');
  failed.nodes.get('#nav-search').fire('click');
  failed.requests[0].resolve({ok:false}); await flush();
  assert.match(failed.nodes.get('#search-body').innerHTML,/重试/);
  const retry = new failed.Element('BUTTON'); retry.setAttribute('data-search-retry','');
  failed.document.fire('click',{target:retry});
  assert.equal(failed.requests.length,2);
  assert.match(failed.nodes.get('#search-body').innerHTML,/正在加载/);
  failed.requests[1].resolve({ok:true,json:async () => payload()}); await flush();
  assert.match(failed.nodes.get('#search-body').innerHTML,/常用搜法/);
  failed.nodes.get('#search-input').value = '鼠标光晕'; failed.nodes.get('#search-input').fire('input');
  assert.match(failed.nodes.get('#search-body').innerHTML,/href="\.\.\/\.\.\/\.\.\/interactions\/component-spotlight\/"/);

  const invalid = boot('./');
  invalid.nodes.get('#nav-search').fire('click');
  invalid.requests[0].resolve({ok:true,json:async () => ({entries:[],columns:[]})}); await flush();
  assert.match(invalid.nodes.get('#search-body').innerHTML,/重试/,'Malformed JSON schema is retryable');
  const retryInvalid = new invalid.Element('BUTTON'); retryInvalid.setAttribute('data-search-retry','');
  invalid.document.fire('click',{target:retryInvalid});
  invalid.requests[1].reject(new Error('Network offline')); await flush();
  assert.match(invalid.nodes.get('#search-body').innerHTML,/重试/,'Network failures are retryable');
  invalid.document.fire('click',{target:retryInvalid});
  const fallback = payload(); fallback.entries.forEach(entry => {delete entry.thumbnail;});
  invalid.requests[2].resolve({ok:true,json:async () => fallback}); await flush();
  invalid.nodes.get('#search-input').value = '按钮'; invalid.nodes.get('#search-input').fire('input');
  assert.match(invalid.nodes.get('#search-body').innerHTML,/result-thumb-fallback/);
  assert.match(invalid.nodes.get('#search-body').innerHTML,/aria-hidden="true">组<\/span>/);
  assert.doesNotMatch(invalid.nodes.get('#search-body').innerHTML,/demo-scope|data-demo|<img|<script/);

  const errorHtml = fs.readFileSync('dist/404.html','utf8');
  const errorRoot = errorHtml.match(/data-site-root="([^"]+)"/)[1];
  const errorIndex = errorHtml.match(/data-index-url="([^"]+)"/)[1];
  const errorPage = boot(errorRoot);
  errorPage.dialog.dataset.indexUrl = errorIndex;
  errorPage.nodes.get('#nav-search').fire('click');
  assert.equal(errorPage.requests[0].url,errorIndex);
  errorPage.requests[0].resolve({ok:true,json:async () => payload()}); await flush();
  const errorInput = errorPage.nodes.get('#search-input');
  errorInput.value = '按钮'; errorInput.fire('input');
  assert.match(errorPage.nodes.get('#search-body').innerHTML,/href="\/vibocoding-assistant\/components\/button\/"/);
  errorPage.dialog.fire('keydown',{key:'Enter',target:errorInput});
  assert.equal(errorPage.navigations[0],'/vibocoding-assistant/components/button/');
  console.log('Lazy load, loading/retry/cache, relative links, copy isolation, arrows/Enter and single Escape passed');
})().catch(error => {console.error(error);process.exitCode = 1;});
