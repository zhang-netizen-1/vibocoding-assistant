/* All queries and mutations stay inside the demonstration's ShadowRoot. */
window.VibeDemos.register('token', ({document, scope, matchMedia}) => {
  const root = document.querySelector('[data-token]');
  const sample = root.querySelector('[data-token-sample]');
  const output = root.querySelector('[data-token-output]');
  const control = name => root.querySelector(`[data-token-control="${name}"]`);
  const key = root.dataset.token;
  const storageKey = 'vibe-token-demo-theme';
  const systemTheme = matchMedia('(prefers-color-scheme: dark)');
  const persistent = scope.hasAttribute?.('data-interactive');

  function luminance(hex) {
    const rgb = hex.match(/[a-f\d]{2}/gi).map(channel => {
      const value = parseInt(channel, 16) / 255;
      return value <= 0.04045 ? value / 12.92 : ((value + 0.055) / 1.055) ** 2.4;
    });
    return rgb[0] * 0.2126 + rgb[1] * 0.7152 + rgb[2] * 0.0722;
  }

  function updateColor() {
    const foreground = control('foreground').value;
    const background = control('background').value;
    const values = [luminance(foreground), luminance(background)];
    const ratio = (Math.max(...values) + 0.05) / (Math.min(...values) + 0.05);
    sample.style.setProperty('--sample-fg', foreground);
    sample.style.setProperty('--sample-bg', background);
    output.textContent = `对比度 ${ratio.toFixed(2)}:1 · 正文${ratio >= 4.5 ? '达标' : '未达标'} · 大字${ratio >= 3 ? '达标' : '未达标'} · 控件边界${ratio >= 3 ? '达标' : '未达标'}`;
  }

  function updateType() {
    const base = Number(control('type').value);
    root.querySelectorAll('[data-type-size]').forEach(item => {
      const original = Number(item.dataset.typeSize);
      // Preserve the PRD scale and its 12px floor when the body base changes.
      const scale = [12, 13, 14, 16, 18, 22, 28, 36];
      const size = scale[Math.max(0, scale.indexOf(original) - (base === 14 ? 1 : 0))];
      item.dataset.typeLabel ||= item.textContent.replace(/\s\d+px$/, '');
      item.style.fontSize = `${size}px`;
      item.style.lineHeight = original <= 13 ? '1.5' : original >= 22 ? '1.3' : '1.7';
      item.textContent = `${item.dataset.typeLabel} ${size}px`;
    });
    output.textContent = `正文 ${base}px · 行高 1.7 · 最小字号 12px`;
  }

  function updateSpacing() {
    const step = Number(control('space').value);
    const padding = step === 8 ? 24 : 16;
    const margin = step === 8 ? 16 : 12;
    sample.style.setProperty('--sample-padding', `${padding}px`);
    sample.style.setProperty('--sample-margin', `${margin}px`);
    output.textContent = `内边距 ${padding}px · 外边距 ${margin}px · 均为 ${step} 的倍数`;
  }

  function updateElevation() {
    const radius = control('radius').value;
    const shadows = {none: 'none', soft: '0 4px 12px rgb(17 24 39 / .08)', overlay: '0 16px 48px rgb(17 24 39 / .12)'};
    const labels = {none: '无阴影', soft: '轻阴影（教学对照）', overlay: '浮层阴影（本站）'};
    sample.style.setProperty('--sample-radius', `${radius}px`);
    sample.style.setProperty('--sample-shadow', shadows[control('shadow').value]);
    output.textContent = `圆角 ${radius}px · ${labels[control('shadow').value]}`;
  }

  function updateTheme() {
    const mode = control('theme').value;
    const dark = mode === 'dark' || (mode === 'system' && systemTheme.matches);
    sample.dataset.theme = dark ? 'dark' : 'light';
    output.textContent = `仅切换此演示卡片 · 当前${dark ? '深色' : '浅色'} · ${mode === 'system' ? '跟随系统' : '手动选择'}`;
  }

  const updates = {color: updateColor, typography: updateType, spacing: updateSpacing, 'radius-shadow': updateElevation, 'dark-mode': updateTheme};
  if (key === 'dark-mode') {
    if (persistent) {
      try {
        const saved = globalThis.localStorage.getItem(storageKey);
        if (['system', 'light', 'dark'].includes(saved)) control('theme').value = saved;
      } catch { /* Storage may be disabled. The demo still responds locally. */ }
    }
    systemTheme.addEventListener('change', updateTheme);
  }
  updates[key]();
  function change(event) {
    if (!event.target.matches('[data-token-control]')) return;
    updates[key]();
    if (key === 'dark-mode' && persistent) {
      try { globalThis.localStorage.setItem(storageKey, control('theme').value); } catch { /* Keep local state usable. */ }
    }
  }
  document.addEventListener('input', change);
  document.addEventListener('change', change);
  document.addEventListener('click', event => {
    if (event.target.matches('[data-token-action]')) output.textContent = '演示设置已保存';
  });
  return {
    preview() {
      const field = root.querySelector('select');
      if (field) {
        field.value = {typography: '14', spacing: '8', 'radius-shadow': '16', 'dark-mode': 'dark'}[key];
      } else {
        control('foreground').value = '#868E9C';
      }
      updates[key]();
    }
  };
});
