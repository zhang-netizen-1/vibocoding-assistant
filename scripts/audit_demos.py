"""Conservative static demo triage. No browser, execution, or inferred behavior.

Evidence is limited to selectors present in each demo, matching CSS declarations,
source IDs, explicit data-action/data-cmd hooks and matching JS initialization
blocks. Shared replay/run gates do not change a CSS animation into a JS renderer.
The 55 formerly ambiguous specimens have explicit source-reviewed decisions.
Static examples and native controls remain truthful; no animation is invented.
"""
from collections import Counter
from pathlib import Path
import importlib.util
import re

ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location('audit_entries', ROOT / 'site-src/entries.py')
ADAPTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ADAPTER)


def assets():
    ui = (ROOT / '网页UI元素速查.html').read_text()
    motion = (ROOT / '动效速查-src/motion_template.html').read_text()
    return dict(
        ui=('\n'.join(re.findall(r'<style>(.*?)</style>', ui, re.S)), '\n'.join(re.findall(r'<script[^>]*>(.*?)</script>', ui, re.S))),
        motion=('\n'.join(re.findall(r'<style>(.*?)</style>', motion, re.S)) + (ROOT / '动效速查-src/motion_extra.css').read_text(),
                '\n'.join(re.findall(r'<script[^>]*>(.*?)</script>', motion, re.S)) + (ROOT / '动效速查-src/motion_extra.js').read_text()),
        guide=((ROOT / 'site-src/guides.css').read_text() + (ROOT / 'site-src/visual-styles.css').read_text(), (ROOT / 'site-src/guides.js').read_text()))


def automatic_classify(demo, sources):
    kind = demo['kind']
    if kind == 'token':
        return '需要 JS 驱动', 'token-demo.js 通过局部输入事件更新色值、字号、间距、圆角阴影或演示主题'
    if kind == 'skill-reference':
        return '需人工确认', '来源是技能说明卡，没有独立交互演示，不推断为动画'
    css, js = sources[kind]
    html = demo['html']
    doc = ADAPTER.Document(html).root
    nodes = doc.find_all()
    classes = {c for n in nodes for c in n.attrs.get('class', '').split()}
    ids = {n.attrs['id'] for n in nodes if 'id' in n.attrs}
    # The extended motion source uses one standalone initializer per block.
    # Require its multiline shape and its own closing line; never let a query
    # absorb subsequent unrelated functions (UI .segb / motion .mini-scroll).
    initializers = re.finditer(
        r"^document\.querySelectorAll\(['\"]\.([\w-]+)['\"]\)\.forEach\(\w+=>\{\n(.*?)^\}\);",
        js, re.M | re.S)
    for match in initializers:
        if match[1] in classes and re.search(r'addEventListener\([\'"](?:pointermove|mousemove)', match[2]):
            return '依赖鼠标指针', f'.{match[1]} 专用初始化块绑定 pointermove，coarse 指针沿用原静态降级'
    if kind == 'motion':
        key = demo['key']
        if key in ('component-tilt', 'component-spotlight'):
            line = next(line for line in js.splitlines() if "['component-tilt','component-spotlight']" in line)
            if 'pointermove' in line:
                return '依赖鼠标指针', f'{key} 共用初始化行含 pointermove'
        if 'cursor-wave' in classes and re.search(r'const wave=.*?pointermove', js, re.S):
            return '依赖鼠标指针', '.cursor-wave 绑定 pointermove'
    hooks = sorted({name for n in nodes for name in n.attrs if name in ('data-cmd', 'data-action', 'data-extra-action', 'data-drag')})
    matched_ids = [i for i in sorted(ids) if re.search(r'(?:getElementById\([\'"]|#[\w-]*\b)' + re.escape(i), js)]
    if hooks:
        return '需要 JS 驱动', '演示标记含 ' + '、'.join(hooks) + '；来源脚本有对应委托/拖动处理'
    if matched_ids:
        return '需要 JS 驱动', '来源脚本引用演示 ID：' + '、'.join(matched_ids)
    if kind == 'guide':
        return '需要 JS 驱动', f'guides.js 以 data-demo / data-mode 切换 {demo["section"]}/{demo["key"]} 的原预览状态'
    if '<canvas' in html:
        return '需要 JS 驱动', 'canvas 标记；来源脚本含 getContext / requestAnimationFrame'
    if kind == 'motion':
        key = demo['key']
        if re.search(r'[\'"]' + re.escape(key) + r'[\'"]', js):
            return '需要 JS 驱动', f'来源脚本显式分派 {key}，由对应函数计算状态并更新当前 stage'
        if 'mini-scroll' in classes or any(c.endswith('-scroll') for c in classes):
            return '需要 JS 驱动', '局部滚动标记；脚本读取 scrollTop 并写进度/帧'
    for selector, body in re.findall(r'([^{}]+)\{([^{}]*)\}', css):
        matched = classes.intersection(re.findall(r'\.([\w-]+)', selector))
        if matched and re.search(r'\b(?:animation|transition)(?:-\w+)?\s*:', body):
            # A JS initializer containing the class might control this rule;
            # do not classify it as pure CSS without accounting for that hook.
            specific = [c for c in matched if re.search(r'[\'"]\.' + re.escape(c) + r'[\'"]', js)]
            if specific:
                return '需人工确认', 'CSS 动画/过渡与 JS 选择器均命中：' + '、'.join(sorted(specific))
            return '纯 CSS 动画', '匹配规则 ' + selector.strip()[:110] + ' 含 animation/transition；未发现专用 JS 钩子'
    return '需人工确认', '未找到足以确认的局部动画或专用脚本钩子；可能仅有原生状态/静态展示'



# Source review of every one of the original 55 unresolved entries. The key is
# the source anchor (never a translated title), so this is usable by migration.
# Values: category, evidence, still, play, phone. These are implementation plans,
# not claims that the unified runtime already implements them.
REVIEWED = {}


def reviewed(anchor, category, evidence, still, play, phone):
    if anchor in REVIEWED:
        raise ValueError(f'Duplicate reviewed anchor: {anchor}')
    REVIEWED[anchor] = (category, evidence, still, play, phone)


STATIC_UI = {
    'alert': '四个 .alert 状态横幅，无关闭控件或局部事件',
    'navbar': '.navbar 内为 Logo 与 .links span；仅颜色 hover，无页面链接或切换脚本',
    'sidebar': '.sidebar .menu div.active 固定概览状态，无菜单切换处理',
    'pagination': '.pager button.on 固定第 2 页；无分页事件或数据更新',
    'footer': '.foot-cols 与 .foot-cr 仅文本布局，无演示动作',
    'badge': '四个 .badge span 固定状态标签，无动态状态变更',
    'table': 'table.t 固定两行示例数据，无排序、编辑或脚本',
    'card': '.card2 内 .img/.body 为固定内容，无翻转、进入或点击处理',
    'timeline': '.tl-item done/cur 为固定物流节点，未定义节点推进事件',
    'kpi': '.kpi .vl 为固定 1,286/3.2%，未实现数字递增',
    'avatar': '.avatar 内固定字母 Z，仅渐变底色，无动画',
}
for key, evidence in STATIC_UI.items():
    reviewed('c-' + key, '静态演示', '网页UI元素速查.html：' + evidence,
             '原样保留固定内容；无需启动器或循环', '无播放动作；标明静态演示，不生成状态变化',
             '直接阅读原示例；不提供伪播放按钮')

NATIVE_UI = {
    'select': ('select.i/option 原生城市选择，无专用 JS', '保留默认“请选择城市…”', '直接操作 select；退出恢复 selectedIndex=0', '使用系统原生选择器'),
    'radio': ('同名 name=plan 的 radio 原生互斥，首项 checked', '保留基础版 checked', '直接点击或方向键选择；退出恢复基础版', '点按 label 使用原生单选'),
    'date': ('input[type=date] 调用浏览器/系统日期控件', '保留空日期值', '点击日期控件并选择；退出清空 value', '使用系统日期选择器，不模拟日历动画'),
    'combobox': ('input[list=city-options] + datalist 原生建议列表，无筛选 JS', '保留空输入和原四城市选项', '输入“上”或“深”查看浏览器建议；退出清空 value', '保留原生输入；建议面板依浏览器支持，不虚构一致效果'),
    'segmented': ('radio name=viewmode + :checked+span 改变选中样式；未实现下方列表/网格内容切换', '保留列表 radio checked', '直接选择列表/网格，仅展示选择状态；退出恢复列表', '点按对应 label，不生成列表/网格内容'),
}
for key, (evidence, still, play, phone) in NATIVE_UI.items():
    reviewed('c-' + key, '原生交互', '网页UI元素速查.html：' + evidence, still, play, phone)
reviewed('c-color', '原生交互',
         '网页UI元素速查.html：input[type=color] 为原生色盘；邻接 span 的 id 属性损坏，脚本 getElementById(hexc) 无匹配节点，不能声称十六进制文案会同步',
         '保留原色 #ed462d 与源标签；不初始化失配的同步脚本',
         '直接点开原生色盘；退出恢复 #ed462d；hex 文本保持原稿，失配单独列为源码缺陷',
         '使用系统色盘；不新增配色动画或声称 hex 同步已修复')
reviewed('c-table-fixed', 'CSS 滚动布局',
         '网页UI元素速查.html：.tblfix-demo overflow:auto/max-height:148px，thead th sticky top:0，.fixcol sticky left:0；无需 JS',
         '滚动容器 scrollTop=0、scrollLeft=0；固定表头与首列仍由 CSS 呈现',
         '直接双向滚动观察 sticky；退出仅重置滚动位置，不补造计时动画',
         '保留 overflow:auto 的双向触摸滚动和容器 tabindex 键盘入口')
reviewed('c-table-edit', '需要 JS 驱动',
         '网页UI元素速查.html：.edittarget 初始化绑定 dblclick/Enter，创建 .cell-input；blur/Enter 保存，Escape 取消',
         '保留原三行六格文字；不创建编辑输入框',
         '绑定原 start/save/cancel；编辑由双击/Enter 触发；退出移除输入框并恢复原文和 aria-label',
         '源入口为双击/Enter；窄屏保留原表格和键盘入口；双击触控可达性须后续浏览器验收，不声称单击可编辑')

# CSS owns these renderers. Shared replay(stage) only toggles .run.
CSS_REPLAY = {
    'view-curtain': ('.run .curtain → curtain 1.05s；translateX(-101% → 101%)', '幕布归位到 translateX(-101%)，保留原场景'),
    'view-stagger': ('.run .stagger-box>* → stagger .55s，子项 --i 延迟', '移除 run，原文与按钮示意完整可见'),
    'text-stagger': ('.run .type-line span → char-in .55s，--i*.065s 延迟', '移除 run，逐字 span 原文完整可见'),
    'text-mask': ('.run .text-mask span → mask-rise .75s，translateY(110% → 0)', '移除 run，原文可见；不留下遮住的首帧'),
    'text-draw': ('.run .draw-svg path → draw 1.35s，stroke-dashoffset 300 → 0；circle 延迟显示', '移除 run，路径 dashoffset=0 与终点完整显示'),
    'media-wipe': ('.run .wipe-art → wipe .95s，clip-path 从全遮到无遮挡', '移除 run，保留原渐变画面且不遮挡文字'),
    'media-blur': ('.run .focus-art → focus .85s，blur(15px) → 0', '移除 run，保留清晰原画面'),
    'media-glitch': ('.run .glitch-art → glitch .5s，steps(3,end) 位移与色相闪切', '移除 run，清除临时 transform/filter，保留 GLITCH 原画面'),
    'data-bars': ('.run .bar-chart i → bar-grow .9s，scaleY(.02 → 1)', '移除 run，保留原 --h 柱高'),
    'data-success': ('.run .success-svg path → draw-check .8s，dashoffset 52 → 0', '移除 run，完整勾形与圆环可见'),
}
for key, (evidence, still) in CSS_REPLAY.items():
    reviewed('e-' + key, '纯 CSS 动画', '动效速查-src/motion_template.html：' + evidence,
             still + '；禁用过渡/动画',
             '仅对当前 stage 清除后添加 run，播放原关键帧一次；退出移除 run 并回到静态样式',
             '显式播放按钮运行同一段 CSS 一次；减弱动态保持完整静态内容')
CSS_LOOPS = {
    'background-aurora': '.aurora → aurora 8s；子 span → float-a 6s/8s，无逐帧 JS',
    'background-wave': '.wave-matrix .dots i → wave 2.4s infinite；--phase 错峰，无逐帧 JS',
    'background-fluid': '.flow-ribbons .ribbon → flow 7s/9s/11s infinite alternate，无逐帧 JS',
    'data-skeleton': '.skeleton span → shimmer 1.4s infinite；原 is-paused/offscreen-paused 仅控制播放状态',
}
for key, evidence in CSS_LOOPS.items():
    reviewed('e-' + key, '纯 CSS 动画', '动效速查-src/motion_template.html：' + evidence,
             '动画禁用并呈现 CSS 基础样式；保留原形状/渐变，不启动观察器循环',
             '当前条目启用原 CSS 循环；退出禁用动画并重置，禁止后台持续播放',
             '播放按钮限定当前条目运行/暂停；减弱动态保留静态原形状')
reviewed('e-component-lift', '纯 CSS 动画',
         '动效速查-src/motion_template.html：.lift-card:hover/:focus-visible 改 transform 与 box-shadow，transition .2s；无专用 JS',
         '保持 transform:none 与基础阴影，未激活时门控伪类效果',
         '激活后由原 hover/focus-visible 触发上浮；离开恢复基础样式',
         '播放按钮用局部演示状态暂时呈现原上浮样式后复位；保留原按钮文案')
reviewed('e-component-press', '纯 CSS 动画',
         '动效速查-src/motion_template.html：.press-card:active/.pressed → translateY(6px) scale(.98)，transition .08s；无按压专用 JS',
         '清除 pressed，恢复基础 transform 与 8px 阴影',
         '原按钮按住进入 :active，松开回弹；自动预览可短暂切换现有 pressed class',
         '原生点按 :active；取消或松手立即复位')
reviewed('e-component-switch', '需要 JS 驱动',
         '动效速查-src/motion_template.html：#e-component-switch .switch-demo 点击切换 aria-checked；CSS 按该属性滑动圆点',
         'aria-checked=false；恢复圆点初位',
         '绑定原 click，切换 aria-checked；退出恢复 false，不启动循环',
         '点按原 role=switch 按钮，保留 aria-checked 与原 CSS 过渡')
reviewed('e-media-compare', '需要 JS 驱动',
         '动效速查-src/motion_template.html：#e-media-compare input 的 input 事件将 range.value 写入 .compare 的 --split；不是鼠标指针跟随',
         'range.value=50、--split:50%；保留原前后两层图',
         '绑定原 range input 处理；由实际滑块调整裁切，退出恢复50%',
         '直接点按/拖动原 range；保留方向键控制，无需模拟鼠标')
reviewed('e-overlay-tooltip', '需要 JS 驱动',
         '动效速查-src/motion_template.html：hover/focus-visible 为 CSS 浮现；coarse 点击委托切换 .tooltip-trigger.touch-open，外点/Escape 关闭',
         '移除 touch-open，气泡 opacity=0，保留原触发按钮',
         '桌面沿用 hover/focus-visible；激活时启用局部触屏点击与关闭处理',
         '沿用源码 touch-open 点按开关；外点/Escape 关闭，退出清除 class')
reviewed('e-extra-timeline-preview', '需要 JS 驱动',
         '动效速查-src/motion_extra.js：#e-extra-timeline-preview range 的 input→previewTime，change 提交 hue/timecode，Escape/pointercancel 回退；画面为 CSS 示意，无真实视频',
         'range=12、committedTime=12，隐藏预览泡并恢复00:12与基础画面',
         '绑定原 input/change/cancel；拖动只预览，松手提交；退出恢复原12秒状态',
         '使用原 range 触控/键盘路径；不添加真实视频播放或声称存在帧素材')
reviewed('e-component-hover-preview', '纯 CSS 动画',
         '动效速查-src/motion_extra.css：.hvp-link:hover/:focus-visible + .hvp-pop 触发 opacity/translateY 过渡，延迟 .3s；无专用 JS',
         '保留链接原文；预览泡 opacity=0、translateY(8px)',
         '门控后沿用原 hover/focus-visible 揭示书籍说明；退出恢复隐藏',
         '播放按钮切换局部展示状态呈现同一说明；不生成书籍内容或跳转')
reviewed('e-component-hover-action', '纯 CSS 动画',
         '动效速查-src/motion_extra.css：.hact-card:hover/:focus-within 显示 .hact-bar；三个按钮没有编辑/复制/删除实现',
         '操作栏 opacity=0、translateY(7px)，保留原封面',
         '沿用 hover/focus-within 显示原操作栏；退出隐藏；按钮仅为示意，不补造业务动作',
         '播放按钮显示原操作栏以供阅读；不声称三个按钮具备业务功能')
reviewed('e-text-text-morph', '需要 JS 驱动',
         '动效速查-src/motion_extra.js：.morph-stage 每2300ms在三个原短语间轮换，.morphing 过渡后320ms提交；原 interval 未保存句柄',
         '停止局部 interval/timeout，移除 morphing，恢复“快速设计”和空 next；清除内联 width',
         '迁移时保存 interval/timeout 句柄；仅当前条目按原三短语轮换；退出清理并复位',
         '播放/暂停按钮控制同一局部轮换；减弱动态固定“快速设计”')
reviewed('e-data-input-shake', '需要 JS 驱动',
         '动效速查-src/motion_extra.js：.shake-demo 的 .shake-go 点击验证邮箱，失败加 .shake 并显示原错误；animationend 清除；成功 toast',
         '空输入、隐藏 .shake-err、移除 shake/run，不触发验证',
         '绑定原验证和 animationend；实际提交才验证；退出清空输入/错误/临时动画',
         '点按原提交按钮；减弱动态只显示原错误文案，无抖动')
reviewed('e-component-ripple', '需要 JS 驱动',
         '动效速查-src/motion_extra.js：.ripple-btn click 按坐标创建 .ripple-ink i；CSS ripple-grow .55s，animationend 删除节点',
         '清空 .ripple-ink 的临时 i；按钮保持原文',
         '绑定原 click，按原坐标创建一次涟漪；退出清理节点与监听',
         '点按沿用 click 坐标；键盘/播放入口须采用按钮中心坐标，减弱动态不建涟漪')
reviewed('e-component-underline', '需要 JS 驱动',
         '动效速查-src/motion_extra.css/.js：hover/focus-visible 是 CSS 下划线过渡；.uline-nav .uline click 切换 .on，无页面跳转',
         '恢复仅首页 .on，清除临时过渡',
         'hover/focus 沿用原 CSS；click 只切换当前链接 .on，退出恢复首页',
         '点按原链接切换 .on，保留原三项；不生成页面导航')

SKILL_REVIEW = {
    'frontend-design': '前端视觉设计', 'ui-ux-pro-max': 'UI/UX 设计检索',
    'baseline-ui': '界面基础打磨', 'create-design-md': '提取设计规范',
    'fixing-accessibility': '无障碍交互修复', 'fixing-motion-performance': '动效性能修复',
    'vercel-react-view-transitions': 'React 视图转场', 'web-design-guidelines': 'Web 界面规范审计',
    'webapp-testing': '真实浏览器测试', 'vercel-composition-patterns': 'React 组件组合',
}
for slug, title in SKILL_REVIEW.items():
    reviewed('skill-' + slug, '静态演示',
             f'site-src/skill_catalog.py：{title}由 render_card 输出说明、来源链接和安装提示词；没有该技能主题的交互演示',
             '保留原说明卡和来源链接，无计时器或动画',
             '无主题播放动作；原生 details 可展开阅读，复制为辅助动作，不伪造技能运行效果',
             '直接阅读与展开原说明；保留原复制入口，不显示主题播放按钮')

# Two concrete false positives found while checking shared CSS selector matches.
reviewed('c-progress', '静态演示',
         '网页UI元素速查.html：.progress>i 固定 width:35%；虽声明 transition:width .3s，但没有改变宽度的事件或动画',
         '保留原35%进度', '无播放动作；不得伪造0→100%进度', '直接展示原35%示例')
reviewed('c-badge-dot', '需要 JS 驱动',
         '网页UI元素速查.html：.bdg click 通过 remove() 删除自身 .num/.dot，更新 aria-label 并 toast 已读；无自动恢复；.step .dot 的过渡不属于此例',
         '恢复源标记中的99+与红点、原 aria-label，清理临时 toast',
         '绑定原 .bdg click；仅删除所点角标并显示原已读反馈；退出恢复源标记',
         '点按原按钮清除角标；保留原可访问名称更新与已读反馈')

ORIGINAL_REVIEW_ANCHORS = frozenset(REVIEWED) - {'c-progress', 'c-badge-dot'}
assert len(ORIGINAL_REVIEW_ANCHORS) == 55
reviewed('c-view-switch', '需要 JS 驱动',
         '网页UI元素速查.html：.segb click 切换 .on/aria-pressed 并写 #viewBody.dataset.view；其后表格 IIFE 的 pointermove 不属于此例',
         '恢复网格按钮 on/aria-pressed=true 与 viewBody data-view=grid',
         '绑定原 .segb click，只切换现有六项网格/列表排布；退出恢复网格',
         '点按原网格/列表按钮，保留原数据与 aria-pressed')


def classify(demo, sources, anchor=None):
    anchor = anchor or ('e-' + demo['key'] if demo['kind'] == 'motion' else None)
    if anchor in REVIEWED:
        return REVIEWED[anchor][:2]
    return automatic_classify(demo, sources)


def implementation_plan(entry, category):
    if entry['demo']['kind'] == 'token':
        return ('保留初始示例，列表退出后复位', '当前演示局部输入更新，预览切到对照档', '原生颜色或下拉控件可点按和键盘操作；减弱动态取消过渡')
    decision = REVIEWED.get(entry['id'])
    if decision:
        return decision[2:]
    if category == '纯 CSS 动画':
        return ('禁用局部动画与过渡，保留完整原内容',
                '悬停/聚焦启用原局部 CSS；离开禁用并复位',
                '播放按钮运行原 CSS；减弱动态保留完整原内容')
    if category == '需要 JS 驱动':
        return ('不启动循环；清理计时器/监听/临时位移并恢复原标记',
                '只初始化当前条目的原动作处理；由原控件触发，退出销毁并复位',
                '沿用原点按/拖动控件与已存在的键盘入口；不新增业务行为')
    if category == '依赖鼠标指针':
        return ('不绑定连续指针监听，清除位移/拖尾/光斑',
                '桌面当前条目绑定原 pointermove；离开解除并复位',
                '沿用源码 coarse/reduced-motion 静态降级；明确标示桌面指针效果，不伪造触屏跟随')
    raise ValueError(f'Missing concrete implementation plan: {entry["old_anchors"][0]} / {category}')


def audit():
    entries = ADAPTER.load_entries()
    sources = assets()
    rows = []
    for entry in entries:
        category, evidence = classify(entry['demo'], sources, entry['id'])
        if 'secondary' in entry['demo']:
            second, why = classify(entry['demo']['secondary'], sources)
            evidence += '；第二演示：' + second + '（' + why + '）'
            if second == '依赖鼠标指针' or category == '需人工确认':
                category = second
            elif second == '需要 JS 驱动':
                category = second
        rows.append((entry, category, evidence))
    covered = {e['id'] for e, _, _ in rows}
    if not ORIGINAL_REVIEW_ANCHORS <= covered:
        raise ValueError('Reviewed source anchors disappeared')
    if any(category == '需人工确认' for _, category, _ in rows):
        raise ValueError('Source review must not leave unresolved entries')
    return rows


def report():
    tax = ADAPTER.taxonomy()
    columns = {c['slug']: c['name'] for c in tax['columns']}
    groups = {(c['slug'], g['slug']): g['name'] for c in tax['columns'] for g in c['groups']}
    rows = audit()
    counts = Counter(category for _, category, _ in rows)
    lines = ['# 一期演示体检', '', '本报告由 `python3 scripts/audit_demos.py` 依据当前工作目录源码生成；不代表浏览器交互验收。', '',
             '共 ' + str(len(rows)) + ' 条：' + '；'.join(f'{c} {counts[c]}' for c in ('静态演示', '原生交互', 'CSS 滚动布局', '纯 CSS 动画', '需要 JS 驱动', '依赖鼠标指针')) + '。', '',
             '已逐条复核原 55 条未决演示：19 条 UI、26 条动效、10 条技能说明卡。每条已按实际 HTML、CSS 与事件实现改为具体分类，并写明静止、播放、手机实现做法；另纠正固定35%进度条、通知角标与视图切换三项共享选择器/初始化块误判。原始内容与演示标记保持不变。', '',
             '分类按实际行为：固定内容为静态演示；系统选择器、radio/datalist 为原生交互；overflow/sticky 为 CSS 滚动布局；共享 run/replay 只负责触发时仍归 CSS；状态计算、DOM 更新、计时器或专用输入监听归 JS；连续 pointermove/mousemove 跟随归鼠标指针。不得仅凭文件存在 @keyframes 或相同通用 class 判定该条使用动画。', '',
             '以下静止、播放与手机列为迁移实施约束，未声称统一运行时已全部完成。列表同一时间仅允许一个动态预览；退出必须清理并恢复原样。静态条目明确显示“静态演示”，不提供伪播放。原生控件保留原生操作；减弱动态保留完整可读内容，不留下透明或裁切首帧。', '',
             '源码已发现的具体限制：颜色控件的 hex 标签 id 损坏而同步脚本仍查找 hexc；时间轴是 CSS 色相画面示意，没有真实视频帧；悬停操作栏的三个按钮没有业务动作；原单元格编辑以双击/Enter 进入。报告如实记录，未在本步骤改写来源或补造功能。', '',
             '| 栏目 | 分组 | 名称 | 旧锚点 | 分类 | 判断依据 | 列表里怎么静止（迁移做法） | 怎么播放（迁移做法） | 手机怎么办（迁移做法） |',
             '|---|---|---|---|---|---|---|---|---|']
    for e, category, evidence in rows:
        still, play, phone = implementation_plan(e, category)
        values = [columns[e['column']], groups[e['column'], e['group']], e['zh'], '、'.join(e['old_anchors']), category, evidence, still, play, phone]
        lines.append('| ' + ' | '.join(v.replace('|', '\\|').replace('\n', ' ') for v in values) + ' |')
    return '\n'.join(lines) + '\n'


if __name__ == '__main__':
    target = ROOT / 'docs/phase1-demo-audit.md'
    target.write_text(report(), encoding='utf-8')
    print(f'Wrote {target}')
