"""Design-system reference, rendered from the current CSS declarations."""
from html import escape
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
PAGE = 'design-system/index.html'


def declarations(source):
    source = re.sub(r'/\*.*?\*/', '', source, flags=re.S)
    return re.findall(r'(--[\w-]+)\s*:\s*([^;{}]+)', source)


def token_sets():
    shell = (HERE / 'tokens.css').read_text(encoding='utf-8').split('.demo-scope')[0]
    demo = (HERE / 'demo-spec.css').read_text(encoding='utf-8')
    host = demo.split(':host {', 1)[1].split('}', 1)[0]
    return dict(declarations(shell)), dict(declarations(host))


def luminance(color):
    channels = [int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4 for c in channels]
    return sum(c * weight for c, weight in zip(linear, (.2126, .7152, .0722)))


def contrast(foreground, background):
    light, dark = sorted((luminance(foreground), luminance(background)), reverse=True)
    return (light + .05) / (dark + .05)


COLOR_USES = {
    '--white': '页面与卡片表面', '--stage': '外框中的演示容器底色', '--soft': '芯片与悬停浅底',
    '--line': '装饰分隔线，不承担控件识别', '--control': '输入框与可点控件边框',
    '--ink': '正文、标题与主按钮', '--secondary': '说明与次级文字', '--muted': '白底上的辅助文字',
    '--blue': '网站链接与键盘焦点环', '--blue-hover': '网站链接悬停', '--black-hover': '墨黑主按钮悬停',
    '--ds-ink': '演示正文与图标', '--ds-ink-2': '舞台上的说明文字', '--ds-ink-3': '白底上的辅助文字',
    '--ds-line': '演示装饰分隔线', '--ds-border': '演示输入框与控件描边', '--ds-fill': '演示中性浅底',
    '--ds-surface': '白色承托面与卡片', '--ds-stage': '演示点阵舞台底色',
    '--ds-accent-50': '选中状态浅底', '--ds-accent-100': '柔和标签浅底', '--ds-accent-200': '进度轨道与装饰光晕',
    '--ds-accent-400': '装饰与图表次色', '--ds-accent': '演示主按钮、选中与焦点环',
    '--ds-accent-hover': '演示主按钮悬停', '--ds-accent-active': '演示主按钮按下',
    '--ds-success': '成功状态文字', '--ds-success-soft': '成功状态浅底',
    '--ds-warning': '警告状态文字', '--ds-warning-soft': '警告状态浅底',
    '--ds-danger': '危险操作与错误文字', '--ds-danger-soft': '错误状态浅底',
    '--ds-chart-1': '图表第一序列', '--ds-chart-2': '图表第二序列',
    '--ds-chart-3': '图表第三序列', '--ds-chart-4': '图表第四序列',
}

SHELL_TYPE = (
    ('--text-xs', '1.7', '400', '辅助说明与导航编号'), ('--text-label', '1.5', '500', '标签与条数'),
    ('--text-small', '1.7', '400', '说明与表格'), ('--text-body', '1.7', '400', '正文与提示词'),
    ('--text-lead', '1.7', '400', '条目一句话定义'), ('--text-section', '1.3', '600', '区块标题'),
    ('--text-title', '1.3', '650', '条目标题'), ('--text-hero', '1.3', '650', '首页大标题'),
)
DEMO_TYPE = tuple((f'--ds-text-{name}', None, None, use) for name, use in (
    ('caption', '提示与注释'), ('label', '标签与表头'), ('body', '正文与输入内容'),
    ('strong', '卡片标题与列表主文字'), ('title', '弹窗与区块标题'), ('display', '大数字与展示标题')))


def color_cards(tokens, stage, group):
    cards = []
    for token, raw in tokens.items():
        value = raw.strip()
        if not re.fullmatch(r'#[\da-fA-F]{6}', value):
            continue
        white_ratio = contrast(value, '#FFFFFF')
        stage_ratio = contrast(value, stage)
        use = COLOR_USES[token]
        cards.append(f'''<article class="ds-color" data-color-token="{token}" data-color="{value}" data-color-group="{group}" data-stage="{stage}" data-white-contrast="{white_ratio:.2f}" data-stage-contrast="{stage_ratio:.2f}">
<div class="ds-swatch" style="background:{value}" aria-hidden="true"></div>
<div class="ds-color-copy"><code>{token}</code><strong>{value}</strong><p>什么时候用 · {use}。</p>
<p class="ds-ratios">白底 {white_ratio:.2f}:1 · 舞台 {stage_ratio:.2f}:1</p></div></article>''')
    return '<div class="ds-color-grid">' + ''.join(cards) + '</div>'


def typography(tokens, rows, group):
    items = []
    for token, line, weight, use in rows:
        line = line or tokens[token + '-line-height'].strip()
        weight = weight or tokens[token + '-weight'].strip()
        size = tokens[token].strip()
        items.append(f'''<div class="ds-type-row" data-type-group="{group}" data-type-size="{size[:-2]}">
<div class="ds-type-sample" style="font-size:{size};line-height:{line};font-weight:{weight}">设计让信息清晰可读</div>
<div class="ds-type-meta"><code>{token}</code><span>{size} / {line} / {weight}</span><p>什么时候用 · {use}。</p></div></div>''')
    return '<div class="ds-type-list">' + ''.join(items) + '</div>'


def geometry(tokens, group):
    spaces, radii, shadows = [], [], []
    for token, value in tokens.items():
        value = value.strip()
        if token.startswith(('--space-', '--ds-space-')):
            spaces.append(f'<div class="ds-measure"><code>{token}</code><div class="ds-ruler" style="width:{value}"></div><span>{value}</span><p>什么时候用 · {spacing_use(value)}。</p></div>')
        elif token.startswith(('--radius-', '--ds-radius-')) and not token.startswith('--ds-r-'):
            radii.append(f'<div class="ds-radius-item"><div class="ds-radius-box" style="border-radius:{value}">{value}</div><code>{token}</code><p>什么时候用 · {radius_use(value)}。</p></div>')
        elif token == '--shadow' or token.startswith('--ds-shadow-'):
            use = '外框搜索浮层与大下拉' if group == 'shell' else {'--ds-shadow-1': '静止卡片与承托面', '--ds-shadow-2': '悬停与浮起', '--ds-shadow-3': '弹窗、下拉与提示浮层'}[token]
            shadows.append(f'<article class="ds-shadow-card" style="box-shadow:{value}"><h4>{"外框浮层" if group == "shell" else "层级 " + token[-1]}</h4><code>{token}</code><code class="ds-shadow-value">{escape(value)}</code><p>什么时候用 · {use}。</p></article>')
    return f'<h4>间距</h4><div class="ds-measures">{"".join(spaces)}</div><h4>圆角</h4><div class="ds-radius-grid">{"".join(radii)}</div><h4>阴影</h4><div class="ds-shadow-grid">{"".join(shadows)}</div>'


NESTED_LEVELS = [
    ('--ds-r-stage', '16px', '演示舞台外框（条目页）'),
    ('--ds-r-surface', '16px', '承托面、弹窗；与舞台间隔 ≥ 16px 时可同为 16'),
    ('--ds-r-panel', '12px', '承托面里的面板、列表、预览框'),
    ('--ds-r-control', '8px', '按钮、输入框、分段按钮组两端'),
    ('--ds-r-chip', '6px', '标签、角内小框、行内高亮'),
    ('--ds-r-min', '6px', '内外间隙很小时的下限，不再往下减'),
]


def nested_radius():
    rows = ''.join(f'<tr><td><code>{t}</code></td><td>{v}</td><td>{u}</td></tr>' for t, v, u in NESTED_LEVELS)
    return (
        '<p>什么时候用 · 框里再套框时都要套用：外圆角 = 内圆角 + 间隙，内圆角永远不超过外圆角；间隙很大时内圆角取 6px 下限。'
        '胶囊与圆形按形状定义，不受此限，但离外框圆角至少一个外圆角半径。</p>'
        '<div class="ds-nest-pair">'
        '<figure class="ds-nest ds-nest-good"><div class="ds-nest-outer"><div class="ds-nest-inner">内 8 · 间隙 8</div></div>'
        '<figcaption>✓ 外 16 = 内 8 + 间隙 8，弧线同心</figcaption></figure>'
        '<figure class="ds-nest ds-nest-bad"><div class="ds-nest-outer"><div class="ds-nest-inner">内 20 · 间隙 8</div></div>'
        '<figcaption>✗ 内 20 大于外 16，角上出现鼓包（旧 cmdk 的问题）</figcaption></figure>'
        '</div>'
        f'<table class="ds-nest-table"><thead><tr><th>变量</th><th>值</th><th>什么时候用</th></tr></thead><tbody>{rows}</tbody></table>'
        '<p>缩略图：卡片 16 − 1px 边框 = 舞台 15，舞台里的承托面 14。</p>'
        '<h4>按钮间距</h4><p>什么时候用 · 各自带边框的独立按钮之间留 8px，按钮与预览框之间至少 12px；'
        '只有共用外边框、中间有分隔线、两端才有圆角的分段按钮组可以 0 间隙。</p>'
        '<div class="ds-gap-pair"><div class="ds-gap-sep"><button type="button">初始状态</button><button type="button">切换状态</button></div>'
        '<div class="ds-gap-seg" role="group" aria-label="分段按钮示例"><button type="button" aria-pressed="true">日</button><button type="button" aria-pressed="false">周</button><button type="button" aria-pressed="false">月</button></div></div>'
        '<p class="ds-note">自动检查：tests/geometry_headless.cjs 在 1440 / 768 / 390 三个宽度检查全部条目演示的圆角嵌套、按钮间距、文字裁切和指示条偏移。</p>'
    )


def spacing_use(value):
    return {'4px': '图标与文字的紧凑间隙', '8px': '同组控件间隙', '12px': '标签组与小控件间隙',
            '16px': '手机安全内边距与小卡片', '24px': '卡片内边距与内容分组',
            '32px': '桌面舞台内边距与双栏间隙', '48px': '区块之间的留白', '64px': '页面底部与大区块留白'}[value]


def radius_use(value):
    return {'6px': '标签与小控件', '8px': '按钮与输入框', '12px': '卡片与舞台',
            '16px': '承托面与弹窗', '999px': '提示胶囊与头像'}[value]


def motion(tokens):
    uses = {'instant': '按下与勾选反馈', 'fast': '悬停与焦点反馈', 'base': '提示框与下拉出现',
            'slow': '弹窗与抽屉展开', 'scene': '整块交叉淡化与页面切换',
            'standard': '常规状态变化', 'out': '元素进入', 'in': '元素离开', 'spring': '小元素的轻弹性反馈'}
    cards = []
    for token, value in tokens.items():
        if not token.startswith(('--ds-dur-', '--ds-ease-')):
            continue
        duration = value if token.startswith('--ds-dur-') else tokens['--ds-dur-scene']
        easing = value if token.startswith('--ds-ease-') else tokens['--ds-ease-standard']
        cards.append(f'''<article class="ds-motion-card" style="--sample-duration:{duration};--sample-easing:{easing}">
<code>{token}</code><strong>{escape(value.strip())}</strong><p>什么时候用 · {uses[token.rsplit('-', 1)[1]]}。</p>
<div class="ds-motion-track" aria-hidden="true"><span class="ds-motion-box"></span></div>
<button type="button" class="ds-motion-play" aria-label="播放 {token}">播放</button><span class="ds-motion-status" role="status">待播放</span></article>''')
    return '<div class="ds-motion-grid">' + ''.join(cards) + '</div>'


def inventory(tokens, group):
    overrides = {}
    if group == 'demo':
        for name, value in declarations((HERE / 'demo-spec.css').read_text(encoding='utf-8')):
            if name.startswith('--ds-') and value.strip() != tokens.get(name, '').strip():
                overrides.setdefault(name, [])
                if value.strip() not in overrides[name]:
                    overrides[name].append(value.strip())
    rows = ''.join(f'<div class="ds-token-row"><code>{escape(name)}</code><code>{escape(value.strip())}</code></div>'
                   for name, value in tokens.items() if group == 'shell' or name.startswith('--ds-'))
    more = ''.join(f'<div class="ds-token-row"><code>{escape(name)}</code><code>{escape(" / ".join(values))}</code></div>' for name, values in overrides.items())
    return f'<details class="ds-inventory"><summary>全部变量与上下文覆盖值</summary><div class="ds-token-table">{rows}</div>' + (f'<h4>响应式与舞台局部覆盖</h4><div class="ds-token-table">{more}</div>' if more else '') + '</details>'


def button_states():
    rows = []
    for name, primary in [('墨黑主按钮', True), ('次按钮', False)]:
        cells = []
        for label, state in [('默认', ''), ('悬停', 'force-hover'), ('按下', 'force-pressed'), ('聚焦', 'force-focus'), ('禁用', 'force-disabled')]:
            disabled = ' disabled' if state == 'force-disabled' else ''
            cells.append(f'<div class="ds-button-cell"><span>{label}</span><button type="button" class="ds-example-button {"btn-primary" if primary else "ds-secondary"} {state}"{disabled}>保存修改</button></div>')
        rows.append(f'<h4>{name}</h4><p>什么时候用 · {"提交、保存与复制等页面主操作" if primary else "预览、返回与取消等辅助操作"}。</p><div class="ds-button-states">{"".join(cells)}</div>')
    return ''.join(rows)


def render(entries, tax, templates):
    shell_tokens, demo_tokens = token_sets()
    button = next(e for e in entries if e['column'] == 'components' and e['slug'] == 'button')
    link = templates.relative(PAGE, 'components/button/')
    anchors = [('shell-colors', '外框颜色'), ('shell-type', '外框字号'), ('shell-geometry', '外框尺寸'),
               ('shell-components', '外框组件'), ('demo-colors', '演示颜色'), ('demo-type', '演示字号'),
               ('demo-geometry', '演示尺寸'), ('demo-motion', '演示动效'), ('demo-stage', '舞台与提示')]
    nav = ''.join(f'<a class="chip" href="#{anchor}">{title}</a>' for anchor, title in anchors)
    variables = ';'.join(f'{key}:{value.strip()}' for key, value in demo_tokens.items() if key.startswith('--ds-'))
    body = f'''<div class="ds-page">
<header class="ds-intro"><p class="ds-eyebrow">Vibe Design 速查</p><h1>设计系统</h1><p>从网站外框到演示舞台，查看正在使用的变量、组件和交互规则。</p><div class="ds-intro-meta"><span>浅色界面</span><span>系统中文字体</span><span>4px 间距基准</span></div></header>
<div class="ds-layout"><nav class="ds-toc" aria-label="设计系统页内目录">{nav}</nav><div class="ds-content">
<section class="ds-family" aria-labelledby="shell-title"><div class="ds-family-heading"><h2 id="shell-title">网站外框</h2><p>导航、搜索、内容卡片与网站操作使用黑白灰和链接蓝。</p></div>
<section class="ds-section" id="shell-colors"><h3>颜色</h3><p>对比度由构建时的 WCAG 相对亮度公式计算，舞台基准为 {shell_tokens['--stage'].strip()}。正文至少 4.5:1，控件识别至少 3:1。</p>
{color_cards(shell_tokens, shell_tokens['--stage'].strip(), 'shell')}
<p class="ds-note">三级文字不放浅底 {shell_tokens['--soft'].strip()}。浅灰分隔线仅用于装饰，控件轮廓使用 --control。色块属于颜色样本，名称与数值统一放在白底上。</p></section>
<section class="ds-section" id="shell-type"><h3>字号阶梯</h3><p>沿用系统中文字体栈。每级展示字号 / 行高倍数 / 字重。</p>{typography(shell_tokens, SHELL_TYPE, 'shell')}<p class="ds-note">12px 样本采用 base.css 的默认行高 1.7，13px 标签采用组件行高 1.5。首页标题在 ≤760px 时实际为 26px，本表保留 36px 阶梯样本。</p></section>
<section class="ds-section" id="shell-geometry"><h3>间距、圆角与阴影</h3>{geometry(shell_tokens, 'shell')}</section>
<section class="ds-section" id="shell-components"><h3>组件</h3>
<h4>顶部导航</h4><p>什么时候用 · 提供全站栏目入口，1024px 以下通过目录展开。</p>
<div class="ds-nav-example"><div class="nav-inner"><a class="brand" href="{templates.relative(PAGE, '')}"><span class="logo" aria-hidden="true"></span>Vibe Design 速查</a><nav class="ds-sample-links" aria-label="导航组件示例"><a class="nav-link" href="{templates.relative(PAGE, 'basics/')}">设计基础</a><a class="nav-link" href="{templates.relative(PAGE, 'components/')}">组件</a></nav></div></div>
<h4>搜索框</h4><p>什么时候用 · 按名称或自己的说法查找条目，点击打开全站搜索。</p><button class="home-search" data-search><span class="search-icon" aria-hidden="true"></span><span>搜索中文名、英文名或已有词</span></button>
<h4>条目卡片与画廊卡</h4><p>什么时候用 · 列表概览使用条目卡，需要先看效果时使用画廊卡。</p><div class="ds-card-grid"><article class="simple-card"><a href="{link}"><strong>按钮</strong><span class="english">Button</span><p>触发保存、提交或取消等操作。</p></a></article>{templates.gallery_card(button, PAGE)}</div>
<h4>标签芯片</h4><p>什么时候用 · 提供分组入口与可点击筛选条件。</p><div class="chips"><a class="chip" href="#shell-colors">颜色</a><a class="chip" href="#shell-type">排版</a><a class="chip" href="#demo-stage">演示舞台</a></div>
{button_states()}
<h4>焦点环</h4><p>什么时候用 · 键盘聚焦可点击元素时，显示 2px 链接蓝轮廓与 2px 外偏移。</p><div class="ds-focus-example"><a class="link-block force-focus" href="{link}">查看按钮条目 →</a></div>
<p class="ds-note">状态示例通过 force-hover、force-pressed、force-focus、force-disabled 类固定显示。点击示例按钮可查看反馈。</p><p class="ds-example-status" role="status" aria-live="polite">等待操作</p>
</section>{inventory(shell_tokens, 'shell')}</section>
<section class="ds-family ds-catalog" style="{escape(variables, quote=True)}" aria-labelledby="demo-title"><div class="ds-family-heading"><h2 id="demo-title">演示</h2><p>演示强调色为紫色，状态色承担成功、警告与危险语义。</p></div>
<section class="ds-section" id="demo-colors"><h3>颜色</h3><p>舞台基准为 {demo_tokens['--ds-stage'].strip()}。演示的紫色焦点环使用 --ds-accent。</p>{color_cards(demo_tokens, demo_tokens['--ds-stage'].strip(), 'demo')}
<p class="ds-note">--ds-ink-3 只放白底，不放演示舞台或浅底。浅色强调色与语义浅底用作背景，文字使用 --ds-ink 或对应深色语义色。演示主操作使用紫色。</p></section>
<section class="ds-section" id="demo-type"><h3>字号阶梯</h3><p>什么时候用 · 单个演示最多使用三级字号，数字采用等宽数字排列。</p>{typography(demo_tokens, DEMO_TYPE, 'demo')}<p class="ds-note">演示容器达到 640px 时，正文 / 标题 / 按钮 / 控件高度还有上下文覆盖值，见全部变量表。</p></section>
<section class="ds-section" id="demo-geometry"><h3>间距、圆角与阴影</h3>{geometry(demo_tokens, 'demo')}<div class="ds-control-sizes">{''.join(f'<div><button type="button" class="ds-height-example" style="height:{demo_tokens[token]}">{demo_tokens[token]}</button><code>{token}</code><p>什么时候用 · {use}。</p></div>' for token, use in [('--ds-control-small', '桌面紧凑工具条'), ('--ds-control-default', '桌面常规表单'), ('--ds-control-large', '大号操作控件')])}</div><p class="ds-note">触屏点击区至少 44×44px。32px、40px 控件在触屏环境扩展到 44px。</p></section>
<section class="ds-section" id="demo-nesting"><h3>嵌套圆角与间距</h3>{nested_radius()}</section>
<section class="ds-section" id="demo-motion"><h3>动效</h3><p>什么时候用 · 通过位移和透明度反馈状态变化。悬停或点击「播放」可重放，减弱动态时直接到终点。</p>{motion(demo_tokens)}</section>
<section class="ds-section" id="demo-stage"><h3>演示舞台与提示胶囊</h3><p>什么时候用 · 演示真实组件的操作与反馈时，复用独立作用域的舞台。</p><div class="ds-live-demo" id="design-system-live-demo">{templates.demo_scope(button['demo'], PAGE, True, 'button')}</div>
<h4>舞台结构示意</h4><p>什么时候用 · 校验舞台比例、内容安全边距和底部操作提示的位置。</p><div class="ds-stage-diagram"><div class="ds-stage-surface"><strong>内容承托面</strong><span>白底 · 16px 圆角 · 一级双层阴影</span></div><span class="ds-stage-hint"><span aria-hidden="true">↖</span> 点击组件，查看状态变化</span></div>
<div class="ds-stage-rules"><p><strong>≥1024px · 16:10</strong><span>最小高 320px · 内边距 32px</span></p><p><strong>768–1023px · 3:2</strong><span>最小高 300px · 内边距 24px</span></p><p><strong>&lt;768px · 4:3</strong><span>最小高 260px · 内边距 16px</span></p></div><p class="ds-note">比例为舞台基准，内容过多时按内容增高。390px 屏幕下，主体四边安全距离至少 16px，并为提示胶囊另留底部空间。栏目预览采用 4:3 基准。</p></section>
{inventory(demo_tokens, 'demo')}</section>
</div></div></div><script>{INTERACTION_SCRIPT}</script>'''
    return templates.shell(PAGE, '设计系统', body, entries, tax)


INTERACTION_SCRIPT = r"""
(() => {
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const animations = new Map();
  function play(card) {
    const box = card.querySelector('.ds-motion-box');
    animations.get(card)?.cancel();
    card.dataset.playCount = String(Number(card.dataset.playCount || 0) + 1);
    card.classList.add('is-finished');
    const status = card.querySelector('.ds-motion-status');
    if (reduced.matches) { status.textContent = '已到终点'; return; }
    const style = getComputedStyle(card);
    const width = card.querySelector('.ds-motion-track').clientWidth - 40;
    const animation = box.animate([{transform:`translateX(${-width}px)`,opacity:.4},{transform:'translateX(0)',opacity:1}], {
      duration:parseFloat(style.getPropertyValue('--sample-duration')),
      easing:style.getPropertyValue('--sample-easing').trim(), iterations:1
    });
    animations.set(card, animation);
    status.textContent = '播放中';
    animation.onfinish = () => { animations.delete(card); status.textContent = '播放完成'; };
  }
  document.querySelectorAll('.ds-motion-card').forEach(card => {
    card.querySelector('.ds-motion-play').addEventListener('click', () => play(card));
    card.addEventListener('pointerenter', event => { if (event.pointerType === 'mouse') play(card); });
  });
  reduced.addEventListener('change', () => {
    if (reduced.matches) {
      animations.forEach(animation => animation.cancel());
      animations.clear();
      document.querySelectorAll('.ds-motion-card.is-finished .ds-motion-status').forEach(node => { node.textContent = '已到终点'; });
    }
  });
  document.querySelectorAll('.ds-example-button,.ds-height-example').forEach(button => {
    button.addEventListener('click', () => {
      document.querySelector('.ds-example-status').textContent = `已触发「${button.textContent.trim()}」`;
    });
  });
})();
"""
