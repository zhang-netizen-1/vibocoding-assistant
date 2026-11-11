"""Extract only the five approved UI demos, with scoped CSS and JS.

The original markup and labels stay untouched. Palette, radii and sizing adapt
through scoped styles. No legacy shell CSS or unrelated demo JS is included.
"""
import re

ALLOWED = {'canvas', 'ctl', 'btn', 'btn-pri', 'btn-ghost', 'btn-danger', 'ie-hint',
           'hold-demo', 'holdbtn', 'holdfill', 'holdlabel', 'hold-alt',
           'splitbtn-demo', 'splitbtn', 'split-main', 'split-caret', 'split-menu',
           'fab-demo', 'fab-actions', 'fab-mini-wrap', 'fab-label', 'fab-mini', 'fab',
           'btt-demo', 'btt-page', 'btt-btn'}
COLORS = {
    '#fff':'white', '#ffffff':'white', '#ed462d':'primary', '#ff5b41':'primary-hover',
    '#c73a24':'primary-active', '#dc2626':'danger', '#b91c1c':'danger',
    '#fca5a5':'danger', '#fee2e2':'soft', '#d1fae5':'soft', '#10b981':'primary', '#0f766e':'primary',
    '#1a1d21':'ink', '#1f2937':'ink', '#374151':'secondary', '#4b5563':'secondary',
    '#9a2e1a':'primary-active', '#e2e5ea':'line', '#e5e7eb':'line', '#d1d5db':'border',
    '#d7dbe0':'border', '#f9fafb':'soft', '#fdeeea':'soft', '#f4f2ec':'stage',
    '#e5e2da':'line', '#a2a2b0':'secondary', '#94a3ab':'secondary',
}


def css(source):
    style = re.search(r'<style>(.*?)</style>', source, re.S)[1]
    style = re.sub(r'/\*.*?\*/', '', style, flags=re.S)
    rules = []
    for selector, body in re.findall(r'([^{}]+)\{([^{}]*)\}', style):
        selector = selector.strip()
        if not selector.startswith('.') or '@' in selector:
            continue
        selector_classes = re.findall(r'\.([\w-]+)', selector)
        if not selector_classes or not set(selector_classes) <= ALLOWED:
            continue
        # Only these demos' rules; don't flatten old responsive shell rules.
        if selector == '.canvas' and any('.demo-scope .canvas {' in rule for rule in rules):
            continue
        scoped = ', '.join('.demo-scope ' + part.strip() for part in selector.split(','))
        if 'split-menu' not in selector:
            body = re.sub(r'box-shadow\s*:[^;}]*(?:;|$)', '', body)
        else:
            body = re.sub(r'box-shadow\s*:[^;}]*(?:;|$)', 'box-shadow:var(--shadow);', body)
        body = re.sub(r'#[\da-fA-F]{3,8}\b', lambda m: 'var(--demo-' + COLORS[m[0].lower()] + ')', body)
        body = re.sub(r'rgba\([^)]*\)', 'var(--demo-line)', body)
        body = re.sub(r'border-radius:9px', 'border-radius:8px', body)
        rules.append(f'{scoped} {{{body.strip()}}}')
    rules += [
        '.demo-scope {color:var(--demo-ink); width:100%; min-width:0;}',
        '.demo-scope .demo-feedback {display:block; padding:12px; text-align:center; font-size:14px; color:var(--demo-ink); background:var(--demo-soft);}',
        '.demo-scope .canvas {border:0; background:var(--demo-stage); background-image:none; min-height:224px; padding:48px 16px 24px; border-radius:12px;}',
        '.demo-scope :focus-visible {outline:2px solid var(--demo-focus); outline-offset:2px;}',
        '.demo-scope .ie-hint {color:var(--demo-secondary); font-size:12px; text-align:center;}',
        '.demo-scope .split-caret[aria-expanded="true"] {background:var(--demo-primary-active); border-color:var(--demo-primary-active);}',
        '.demo-scope .btn-danger:hover {background:var(--demo-danger-hover);}',
        '.demo-scope .btn-pri:active, .demo-scope .split-main:active {background:var(--demo-primary-active);}',
        '.demo-scope .btn-danger:active {background:var(--demo-danger-active);}',
        '.demo-scope .btn:disabled {background:var(--demo-line); color:var(--demo-secondary);}',
    ]
    return '\n'.join(rules) + '\n'


def javascript(source):
    ids = ['holdBtn', 'splitCaret', 'fabBtn', 'copyDemoBtn', 'bttPage']
    scripts = []
    for identifier in ids:
        expression = r"\(function\(\)\{\s*const \w+=document\.getElementById\('" + identifier + r"'\);.*?\}\)\(\);"
        match = re.search(expression, source, re.S)
        if not match:
            raise ValueError(f'Missing original demo script: {identifier}')
        scripts.append(match[0])
    return '''/* Generated from the original UI page by redesign/demos.py. */
'use strict';
window.VibeDemos = (() => {
  const controllers = new WeakMap();
  function init(scope) {
    if (controllers.has(scope)) return controllers.get(scope);
    const initial = scope.innerHTML, timers = new Set(), intervals = new Set();
    const lifetime = new AbortController();
    const setTimeout = (fn, ms) => { const id = window.setTimeout(() => {timers.delete(id); fn();}, ms); timers.add(id); return id; };
    const setInterval = (fn, ms) => { const id = window.setInterval(fn, ms); intervals.add(id); return id; };
    const clearTimeout = id => { window.clearTimeout(id); timers.delete(id); };
    const clearInterval = id => { window.clearInterval(id); intervals.delete(id); };
    const document = {
      getElementById: id => scope.querySelector('#' + id),
      addEventListener: (name, fn) => window.document.addEventListener(name, fn, {signal:lifetime.signal})
    };
    const toast = message => {
      if (scope.closest('.gallery-card')) return;
      let output = scope.querySelector('.demo-feedback');
      if (!output) { output = window.document.createElement('output'); output.className = 'demo-feedback'; output.setAttribute('aria-live','polite'); scope.append(output); }
      output.textContent = message;
    };
    scope.addEventListener('click', e => {
      const button = e.target.closest('[data-cmd="toast"]');
      if (button && scope.contains(button)) toast(button.dataset.arg);
    }, {signal:lifetime.signal});
''' + '\n'.join(scripts) + '''
    const caret = scope.querySelector('#splitCaret'), menu = scope.querySelector('#splitMenu');
    menu?.addEventListener('keydown', e => {
      const items = [...menu.querySelectorAll('button')], index = items.indexOf(e.target);
      if (['ArrowDown','ArrowUp','Home','End'].includes(e.key)) {
        e.preventDefault();
        const next = e.key === 'Home' ? 0 : e.key === 'End' ? items.length - 1 : (index + (e.key === 'ArrowDown' ? 1 : items.length - 1)) % items.length;
        items[next].focus();
      }
    });
    scope.querySelector('#holdBtn')?.addEventListener('blur', e => e.target.dispatchEvent(new Event('pointercancel')));
    function reset() {
      timers.forEach(id => window.clearTimeout(id)); intervals.forEach(id => window.clearInterval(id));
      lifetime.abort(); scope.innerHTML = initial; controllers.delete(scope);
    }
    function preview() {
      if (scope.querySelector('#holdBtn')) scope.querySelector('#holdBtn').dispatchEvent(new PointerEvent('pointerdown', {button:0, pointerType:'mouse'}));
      else if (caret) { caret.click(); caret.blur(); }
      else if (scope.querySelector('#fabBtn')) scope.querySelector('#fabBtn').click();
      else if (scope.querySelector('#bttPage')) { const page = scope.querySelector('#bttPage'); page.scrollTop = 160; page.dispatchEvent(new Event('scroll')); setTimeout(() => scope.querySelector('#bttBtn').click(), 900); }
      else { scope.querySelector('#copyDemoBtn')?.click(); scope.querySelector('.btn-pri')?.classList.add('preview-pressed'); }
    }
    const controller = {reset, preview}; controllers.set(scope, controller); return controller;
  }
  return {init};
})();
'''
