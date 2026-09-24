from pathlib import Path
import html, json, math

SOURCE=Path(__file__).resolve().parent
ROOT=SOURCE.parent
entries=json.loads((SOURCE/'motion_entries.json').read_text(encoding='utf-8'))
assert len(entries)==47 and len({e[0] for e in entries})==47

CATS={
'view':('页面与视图','整块界面如何进入、离开和衔接'),
'scroll':('滚动与空间','滚动到达与滚动进度是两种不同触发'),
'background':('背景与氛围','让空间有生命感，而不抢走内容'),
'text':('文字与图形','让信息本身被逐步看见'),
'media':('图片与媒介','视觉内容进场、切换与对照'),
'component':('组件与微交互','按钮、卡片和控件对操作的回应'),
'overlay':('导航与浮层','层级如何打开、退出和返回'),
'data':('数据与状态','内容更新与操作结果如何被理解'),
'mobile':('移动与手势','让拖动、松手和边界都有反馈')
}

def esc(s): return html.escape(str(s),quote=True)
def btn(label, action='play', extra=''):
    return f'<button type="button" data-action="{action}" {extra}>{esc(label)}</button>'
def shell(text='动效预览'):
    return f'<div class="specimen"><span class="s-icon">◈</span><strong>{esc(text)}</strong><span class="s-line"></span></div>'

def demo(kind):
    if kind=='view-crossfade': return '<div class="view-stack"><div class="mini-view view-a">视图 A</div><div class="mini-view view-b" aria-hidden="true">视图 B</div></div>'+btn('切换视图','next')
    if kind=='view-slide': return f'<div class="view-window"><div class="view-track"><div>视图 A</div><div>视图 B</div></div></div>{btn("前进 / 返回","next")}'
    if kind=='view-curtain': return '<div class="mini-view curtain-target">下一层内容<span class="curtain"></span></div>'
    if kind=='view-shared': return '<div class="shared-box"><span class="shared-origin-label">概览位置</span><span class="shared-destination-label">详情位置</span><button class="shared-chip" type="button" data-action="toggle" aria-expanded="false"><strong>展开详情 ↗</strong><span>同一元素跨位置衔接</span></button></div>'
    if kind=='view-stagger': return '<div class="stagger-box"><strong>主标题</strong><span>辅助说明随后出现</span><i>操作入口 →</i></div>'
    if kind.startswith('scroll-'):
        body={
         'scroll-reveal':'<div class="scroll-target reveal-target">进入视口才显现</div>',
         'scroll-parallax':'<div class="parallax-sky"><div class="parallax-back">◆</div><div class="parallax-front">视差</div></div>',
         'scroll-pin':'<div class="pin-scene"><strong>第一幕</strong><span>沿进度切换章节</span></div>',
         'scroll-horizontal':'<div class="horizontal-window"><div class="horizontal-track"><span>01</span><span>02</span><span>03</span></div></div>',
         'scroll-progress':'<div class="reading"><strong>阅读进度</strong><span>向下滚动查看内容</span></div>'
        }[kind]
        return f'<div class="mini-scroll" tabindex="0" aria-label="可滚动的动效预览"><div class="scroll-top">向下滚动 ↓</div><div class="scroll-spacer"></div>{body}<div class="scroll-spacer end"></div></div><div class="scroll-meter"><i></i></div>'
    if kind=='background-aurora': return '<div class="ambient aurora"><span></span><span></span><b>色带缓慢流动</b></div>'
    if kind=='background-wave':
        dots=''.join(f'<i style="--x:{x};--y:{y};--phase:{(x+y)*.13:.2f}s"></i>' for y in range(6) for x in range(10))
        return '<div class="ambient wave-matrix"><span class="dots">'+dots+'</span><b>波浪矩阵</b></div>'
    if kind=='background-particles': return '<div class="ambient particles"><canvas width="620" height="260" aria-hidden="true"></canvas><b>局部粒子场</b></div>'
    if kind=='background-cursorwave':
        dots=''.join(f'<i data-x="{x}" data-y="{y}"></i>' for y in range(6) for x in range(10))
        return '<div class="ambient cursor-wave"><span class="dots">'+dots+'</span><b>移动鼠标</b></div>'
    if kind=='background-fluid': return '<div class="ambient flow-ribbons"><span class="ribbon r1"></span><span class="ribbon r2"></span><span class="ribbon r3"></span><b>柔性色带交错</b></div>'
    if kind=='text-stagger': return '<div class="type-line">'+''.join(f'<span style="--i:{i}">{c}</span>' for i,c in enumerate('文字依次登场'))+'</div>'
    if kind=='text-mask': return '<div class="text-mask"><span>让文字从下方升起</span></div>'
    if kind=='text-typewriter': return '<div class="typewriter" data-final="一字一句，逐渐写出。" aria-label="一字一句，逐渐写出。">一字一句，逐渐写出。</div>'
    if kind=='text-scramble': return '<div class="scramble" data-final="从混沌到清晰" aria-label="从混沌到清晰">从混沌到清晰</div>'
    if kind=='text-draw': return '<svg class="draw-svg" viewBox="0 0 210 90" role="img" aria-label="弧形路径描画"><path d="M12 66 C52 6 103 9 124 46 S174 94 201 20" fill="none" stroke="currentColor" stroke-width="4" stroke-linecap="round"/><circle cx="201" cy="20" r="5" fill="currentColor"/></svg>'
    if kind=='media-wipe': return '<div class="art art-a wipe-art"><span>色彩在遮罩下出现</span></div>'
    if kind=='media-carousel': return f'<div class="media-frame"><div class="media-track"><div class="art art-a" aria-current="true">画面 A</div><div class="art art-b">画面 B</div><div class="art art-c">画面 C</div></div></div><div class="media-actions">{btn("上一张","prev")}{btn("下一张","next")}</div><span class="carousel-status" role="status" aria-live="polite">第 1 / 3 张</span>'
    if kind=='media-blur': return '<div class="art art-b focus-art">逐渐清晰</div>'
    if kind=='media-compare': return '<div class="compare" style="--split:50%"><div class="art compare-art"><span class="compare-sun"></span><span class="compare-hill"></span><b>明亮</b></div><div class="art compare-art compare-top compare-after"><span class="compare-sun"></span><span class="compare-hill"></span><b>深色</b></div></div><label class="compare-label">拖动分界 <input type="range" min="0" max="100" value="50" aria-label="前后对比分界线"></label>'
    if kind=='media-glitch': return '<div class="art art-c glitch-art" data-text="GLITCH">GLITCH</div>'
    if kind=='component-lift': return f'<button class="micro-card lift-card" type="button"><strong>悬停在这里</strong><span>离开后平稳归位</span></button>'
    if kind=='component-tilt': return '<div class="micro-card tilt-card" tabindex="0"><strong>移动鼠标</strong><span>卡片跟手倾斜</span></div>'
    if kind=='component-spotlight': return '<div class="micro-card spot-card" tabindex="0"><strong>局部聚光</strong><span>光斑跟随指针位置</span></div>'
    if kind=='component-flip': return f'<button class="flip-card" data-action="toggle" type="button" aria-pressed="false" aria-label="正面，点击翻面"><span class="face front" aria-hidden="true">正面 ↻</span><span class="face back" aria-hidden="true">背面 ↻</span></button>'
    if kind=='component-press': return '<button class="press-card" type="button">按住我，感受回弹</button>'
    if kind=='component-switch': return '<button class="switch-demo" role="switch" aria-checked="false" aria-label="演示开关" type="button"><span></span></button>'
    if kind=='component-morph': return '<button class="morph-demo" type="button" data-action="toggle">执行动作 →</button>'
    if kind=='overlay-menu': return '<div class="mini-menu">'+btn('展开菜单','toggle','aria-expanded="false" aria-haspopup="menu"')+'<div class="menu-items" role="menu" hidden><button type="button" role="menuitem">选项一</button><button type="button" role="menuitem">选项二</button><button type="button" role="menuitem">选项三</button></div></div>'
    if kind=='overlay-drawer': return f'{btn("打开抽屉","open")}<div class="overlay-shade" hidden><div class="mini-drawer" role="dialog" aria-modal="true" aria-label="演示抽屉"><strong>侧边抽屉</strong>{btn("关闭","close")}</div></div>'
    if kind=='overlay-modal': return f'{btn("打开弹窗","open")}<div class="overlay-shade" hidden><div class="mini-modal" role="dialog" aria-modal="true" aria-label="演示弹窗"><strong>弹窗内容</strong><span>背景被遮罩弱化</span>{btn("关闭","close")}</div></div>'
    if kind=='overlay-tooltip': return '<button class="tooltip-trigger" type="button" aria-describedby="tooltip-demo">悬停或聚焦我<span role="tooltip" id="tooltip-demo">补充说明</span></button>'
    if kind=='overlay-sheet': return '<div class="mini-phone"><button type="button" data-action="open">打开底部弹层</button><div class="sheet" role="dialog" aria-modal="true" aria-label="演示底部弹层" hidden><span class="sheet-handle" data-drag="sheet"></span><strong>底部弹层</strong><button type="button" data-action="close">关闭</button></div></div>'
    if kind=='data-count': return '<div class="counter" data-target="128">128</div>'
    if kind=='data-skeleton': return '<div class="skeleton"><span></span><span></span><span></span></div>'
    if kind=='data-bars': return '<div class="bar-chart"><i style="--h:45%"></i><i style="--h:75%"></i><i style="--h:55%"></i><i style="--h:90%"></i><i style="--h:62%"></i></div>'
    if kind=='data-reorder': return f'<div class="sort-list"><span>第一项</span><span>第二项</span><span>第三项</span></div>{btn("调整顺序","sort")}'
    if kind=='data-success': return '<svg class="success-svg" viewBox="0 0 80 80" role="img" aria-label="完成标记"><circle cx="40" cy="40" r="32"/><path d="M24 40 L35 51 L57 28"/></svg>'
    if kind=='mobile-swipe': return '<div class="phone-demo swipe-demo"><div class="swipe-list"><div class="swipe-slot"><div class="swipe-item" data-drag="swipe" tabindex="0">向左滑动 / 按 Delete</div></div><div class="swipe-next">相邻条目会向上让位</div></div><button type="button" data-action="reset">恢复条目</button></div>'
    if kind=='mobile-drag': return '<div class="phone-demo"><div class="drag-list"><div data-drag="reorder" tabindex="0">≡ 第一项</div><div data-drag="reorder" tabindex="0">≡ 第二项</div><div data-drag="reorder" tabindex="0">≡ 第三项</div></div><button type="button" data-action="sort">键盘替代：下移首项</button></div>'
    if kind=='mobile-pull': return '<div class="phone-demo pull-zone" data-drag="pull" data-refresh-count="0" tabindex="0" aria-label="可滚动的下拉刷新演示"><span class="pull-indicator">到顶下拉刷新</span><div class="pull-result" role="status">列表版本 0</div><div>列表项一</div><div>列表项二</div><div>列表项三</div><div>列表项四</div><div>列表项五</div></div>'
    if kind=='mobile-rubber': return '<div class="phone-demo rubber-zone" data-drag="rubber" tabindex="0"><div class="rubber-item">沿水平方向拖动我</div><small>松手回到合法边界</small></div>'
    if kind=='mobile-pager': return f'<div class="phone-demo pager" data-drag="pager"><div class="pager-track"><div>01</div><div>02</div><div>03</div></div></div><div class="pager-actions">{btn("上一页","prev")}{btn("下一页","next")}</div>'
    raise ValueError(kind)

loop={'background-aurora','background-wave','background-particles','background-fluid','data-skeleton'}
replay={'view-curtain','view-stagger','text-stagger','text-mask','text-typewriter','text-scramble','text-draw','media-wipe','media-blur','media-glitch','data-count','data-bars','data-success'}
scroll={x[0] for x in entries if x[1]=='scroll'}

def card(e):
    kind,cat,name,en,trigger,description,prompt=e
    tools = ('<button class="run-demo" type="button" data-action="scroll-play">模拟滚动</button>' if kind in scroll else '<button class="run-demo" type="button" data-action="replay">重播效果</button>' if kind in replay else '<button class="run-demo pause-loop" type="button" data-action="pause" aria-pressed="false">暂停动画</button>' if kind in loop else '')
    if not tools: tools='<span class="gesture-note">'+esc(trigger)+'</span>'
    return f'''<article class="effect-card" id="e-{esc(kind)}" data-cat="{esc(cat)}" data-name="{esc(name+' '+en+' '+trigger+' '+description)}">
      <div class="card-head"><div><h3>{esc(name)}</h3><button class="english" type="button" data-copy="{esc(en)}" aria-label="复制英文名称：{esc(en)}">{esc(en)}</button></div><span class="tag">{esc(trigger)}</span></div>
      <div class="stage {'dark-stage' if cat=='background' else ''}" data-effect="{esc(kind)}"><span class="stage-label">{esc(trigger)}</span>{demo(kind)}</div>
      <div class="demo-tools">{tools}<span class="preview-label">真实交互演示</span></div>
      <div class="card-note">{esc(description)}</div>
      <details class="card-prompt"><summary>给 coding agent 的组件实现需求</summary><p class="prompt-text">{esc(prompt)}</p><button class="copy-prompt" type="button">复制需求</button></details>
    </article>'''

chips='<button class="chip active" data-filter="all" aria-pressed="true" type="button">全部</button>'+''.join(f'<button class="chip" data-filter="{key}" aria-pressed="false" type="button">{name}</button>' for key,(name,_) in CATS.items())
sections=[]
for key,(name,description) in CATS.items():
    items=[e for e in entries if e[1]==key]
    assert items
    sections.append(f'<section class="category-section" id="section-{key}" data-cat="{key}"><div class="section-head"><div><h2>{name}</h2><p>{description}</p></div><span class="section-count">{len(items)} 种效果</span></div><div class="grid">'+''.join(card(e) for e in items)+'</div></section>')
source=(SOURCE/'motion_template.html').read_text(encoding='utf-8')
assert all(source.count(token)==1 for token in ('__CHIPS__','__SECTIONS__'))
output=source.replace('__CHIPS__',chips).replace('__SECTIONS__','\n'.join(sections))
target=ROOT/'动效速查.html'
target.write_text(output,encoding='utf-8')
print(f'Built {target}: {len(entries)} effect cards, {len(CATS)} categories, {target.stat().st_size} bytes')
