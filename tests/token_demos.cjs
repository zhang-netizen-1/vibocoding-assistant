/* Execute the real token installer with local controls, storage and media models. */
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const entries = JSON.parse(fs.readFileSync('build/entries.json', 'utf8'));
let install;
const stored = new Map();
const context = {
  window: {VibeDemos: {register(kind, callback) {assert.equal(kind, 'token'); install = callback;}}},
  localStorage: {getItem: key => stored.get(key), setItem: (key, value) => stored.set(key, value)}
};
vm.runInNewContext(fs.readFileSync('dist/assets/redesign/demo-token.js', 'utf8'), context);
function node(value = '', dataset = {}) {
  return {value, dataset, style: {setProperty(key, next) {this[key] = next;}},
    textContent: '', matches: selector => selector === '[data-token-control]'};
}
function model(slug, interactive = true, dark = false) {
  const html = entries.find(e => e.column === 'basics' && e.slug === slug).demo.html;
  const controls = new Map();
  for (const m of html.matchAll(/<(input|select)\b([^>]*data-token-control="([^"]+)"[^>]*)>/g)) {
    const body = html.slice(m.index + m[0].length).split('</select>')[0];
    const options = [...body.matchAll(/<option value="([^"]+)"([^>]*)>/g)];
    const value = m[1] === 'input' ? m[2].match(/value="([^"]+)"/)[1] : (options.find(o => o[2].includes('selected')) || options[0])[1];
    controls.set(m[3], node(value));
  }
  const typeNodes = [...html.matchAll(/data-type-size="(\d+)"/g)].map(m => node('', {typeSize: m[1]}));
  const sample = node(), output = node(), listeners = new Map();
  const root = {dataset: {token: slug}, querySelector(selector) {
    if (selector === '[data-token-sample]') return sample;
    if (selector === '[data-token-output]') return output;
    if (selector === 'select') return slug === 'color' ? null : [...controls.values()][0];
    return controls.get(selector.match(/data-token-control="([^"]+)"/)[1]);
  }, querySelectorAll() {return typeNodes;}};
  const media = {matches: dark, addEventListener(type, callback) {this.change = callback;}};
  const document = {querySelector: () => root, addEventListener(type, callback) {listeners.set(type, callback);}};
  const implementation = install({document, scope: {hasAttribute: () => interactive}, matchMedia: () => media});
  return {sample, output, media, typeNodes, implementation, controls,
    change(key, value, type = 'change') {const field = controls.get(key); field.value = value; listeners.get(type)({target: field});}};
}
const color = model('color');
assert.match(color.output.textContent, /7\.10:1.*正文达标/);
color.change('foreground', '#FFFFFF', 'input');
assert.match(color.output.textContent, /1\.00:1.*正文未达标.*大字未达标/);
assert.equal(color.sample.style['--sample-fg'], '#FFFFFF');
color.change('foreground', '#868E9C');
assert.match(color.output.textContent, /正文未达标.*大字达标.*控件边界达标/);
color.change('foreground', '#111827');
assert.match(color.output.textContent, /17\.74:1.*正文达标/);
const type = model('typography');
type.change('type', '14');
assert.equal(type.typeNodes.find(n => n.dataset.typeSize === '16').style.fontSize, '14px');
assert.equal(type.typeNodes.at(-1).style.fontSize, '12px');
for (const item of type.typeNodes) assert.ok([12,13,14,16,18,22,28,36].includes(parseInt(item.style.fontSize, 10)));
type.change('type', '16');
assert.equal(type.typeNodes[0].style.fontSize, '36px');
const spacing = model('spacing');
spacing.change('space', '8');
assert.equal(spacing.sample.style['--sample-padding'], '24px');
assert.equal(spacing.sample.style['--sample-margin'], '16px');
spacing.change('space', '4');
assert.equal(spacing.sample.style['--sample-padding'], '16px');
const elevation = model('radius-shadow');
elevation.change('radius', '6');
assert.equal(elevation.sample.style['--sample-radius'], '6px');
elevation.change('shadow', 'overlay');
assert.equal(elevation.sample.style['--sample-shadow'], '0 16px 48px rgb(17 24 39 / .12)');
elevation.change('shadow', 'none');
assert.equal(elevation.sample.style['--sample-shadow'], 'none');
const theme = model('dark-mode', true, true);
assert.equal(theme.sample.dataset.theme, 'dark');
theme.change('theme', 'light');
theme.media.matches = true; theme.media.change();
assert.equal(theme.sample.dataset.theme, 'light');
assert.equal(model('dark-mode', true, true).sample.dataset.theme, 'light');
theme.change('theme', 'dark');
assert.equal(model('dark-mode').sample.dataset.theme, 'dark');
theme.change('theme', 'system');
theme.media.matches = false; theme.media.change();
assert.equal(theme.sample.dataset.theme, 'light');
theme.media.matches = true; theme.media.change();
assert.equal(theme.sample.dataset.theme, 'dark');
const before = stored.get('vibe-token-demo-theme');
const gallery = model('dark-mode', false);
gallery.implementation.preview();
assert.equal(gallery.sample.dataset.theme, 'dark');
assert.equal(stored.get('vibe-token-demo-theme'), before);
stored.set('vibe-token-demo-theme', 'invalid');
assert.equal(model('dark-mode', true, false).sample.dataset.theme, 'light');
context.localStorage = {getItem() {throw Error('unavailable');}, setItem() {throw Error('unavailable');}};
const noStorage = model('dark-mode');
noStorage.change('theme', 'dark');
assert.equal(noStorage.sample.dataset.theme, 'dark');
for (const slug of ['color', 'typography', 'spacing', 'radius-shadow']) model(slug, false).implementation.preview();
const typeSkin = fs.readFileSync('dist/assets/redesign/demo-skins/_kind-token.css', 'utf8');
assert.match(typeSkin, /\.token-card:not\(\.elevation-card\):not\(\.theme-sample\)/);
assert.doesNotMatch(typeSkin, /--(?:sample-radius|sample-shadow|sample-padding|theme-bg)\s*:/);
const colorPage = fs.readFileSync('dist/basics/color/index.html', 'utf8');
assert.match(colorPage, /data-skin-css="[^" ]*demo-skins\/token-color\.css"/);
assert.match(colorPage, /data-token-control="foreground"/);
assert.match(colorPage, /data-token-control="background"/);
console.log('Five token demos: controls, contrast, scale, spacing, elevation, system theme, persistence and storage fallback passed.');
