"""实现规范分区：控制 AI 动画质量的参数、词汇与验收规则。

内容整理自外部资料《Part 1：视觉、Motion & 基础组件交互》与《Vibe Coding 网页动效词典》
（上 / 中 / 下三篇）的比对结论（见 图像资料比对-2026-09-27.md），话术按站点风格改写：
描述目标与验收，不锁死具体数值。此分区不计入动效条目总数（同 /flows/ 先例）。
"""

from html import escape


def _esc(value):
    return escape(str(value), quote=True)


def _table(headers, rows):
    head = "".join(f"<th>{_esc(cell)}</th>" for cell in headers)
    # 单元格已由 _td() 生成为 <td> 字符串，这里不再二次包裹。
    body = "".join(
        "<tr>" + "".join(cell if cell.startswith("<td") else f"<td>{cell}</td>" for cell in row) + "</tr>"
        for row in rows
    )
    return (
        '<div class="spec-table-wrap"><table class="spec-table">'
        f"<thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>"
    )


def _prompt(text):
    return (
        '<details class="card-prompt spec-prompt"><summary>查看并复制实现规范提示词</summary>'
        f'<p class="prompt-text">{_esc(text)}</p>'
        '<button class="copy-prompt" type="button">复制提示词</button></details>'
    )


def _td(text, mono=False):
    value = _esc(text)
    return f'<td class="spec-mono">{value}</td>' if mono else f"<td>{value}</td>"


GROUPS = [
    {
        "id": "structure",
        "title": "四层结构：怎么向 AI 描述一个动效",
        "keywords": "四层结构 技术工具 触发方式 动效类型 UX 规则 描述方法 结构提示词",
        "note": "看到一个动效可以沿四层往下拆：每层回答一个问题。把层混在一起描述，AI 容易选错实现方式或漏掉移动端处理。工具名称只帮 AI 选实现路径，仍然要说明由什么触发、画面怎样变化。简单动效优先使用 CSS，不为一个淡入或悬停额外安装大型动画库。",
        "content": _table(
            ("层", "回答的问题", "例子"),
            [
                (_td("第一层 · 技术工具"), _td("用什么实现？"), _td("CSS · Motion · GSAP · Three.js · Lottie · Rive")),
                (_td("第二层 · 触发方式"), _td("什么时候开始？"), _td("Hover · Scroll · Pointer · Gesture · Route")),
                (_td("第三层 · 动效类型"), _td("画面具体怎么动？"), _td("Fade · Stagger · Parallax · 磁吸按钮")),
                (_td("第四层 · UX 规则"), _td("怎样动才好用？"), _td("Feedback · Affordance · Focus · Reduced motion")),
            ],
        ),
        "prompt": (
            "使用项目现有的动画工具实现商品详情交互。用户点击商品卡片时，用共享元素转场把卡片主图连续放大到详情页，返回时按原路径恢复；加入购物车后，按钮先显示短暂加载，再变成成功对勾，同时从页面底部出现“已加入购物车”的轻提示。"
            "弹窗和抽屉打开后要锁定背景滚动，并正确移动键盘焦点。手机端把悬停操作改为点击；用户开启减少动态时，取消大幅位移和缩放，改用短促淡入淡出。"
        ),
    },
    {
        "id": "feel",
        "title": "控制手感的五个参数",
        "keywords": "手感参数 easing duration delay stagger spring 缓动 时长 延迟 错峰 弹簧",
        "note": "这组参数不决定元素往哪里移动，只控制速度、等待、顺序和回弹。同样的位移换一套时长和缓动，感受完全不同。",
        "content": _table(
            ("参数", "控制什么", "常用写法", "提醒"),
            [
                (_td("Easing 缓动"), _td("加速与减速节奏"), _td("进场用 ease-out，离场用 ease-in，来回切换用 ease-in-out；进度条、持续旋转、跑马灯保持 linear"), _td("全站不要只用同一种缓动，匀速物体像被机器拖动")),
                (_td("Duration 时长"), _td("一次动画持续多久"), _td("三档：短促（按钮、图标、开关）、适中（卡片进入、菜单、弹窗）、偏慢（大图揭示、品牌首屏、页面转场）"), _td("页面里要有统一的快慢关系，避免一个按钮很快、旁边另一个慢吞吞")),
                (_td("Delay 延迟"), _td("触发后等待多久"), _td("用来建立阅读顺序：标题先出现，正文随后，按钮最后"), _td("按钮点击、加载和错误反馈不要随意增加延迟，等待太久像卡住")),
                (_td("Stagger 错峰"), _td("一组元素依次开始"), _td("卡片从左到右、列表从上到下依次进入；常用写法 staggered reveal / stagger children / cascade"), _td("间隔太大会变成排队等候，整组要像连续动作")),
                (_td("Spring 弹簧"), _td("惯性与回弹"), _td("少量回弹（越过终点很快停稳）、偏硬（按钮、开关）、偏软（卡片拖拽回位）"), _td("拖拽回位、按压反馈最常用，比普通缓动更有重量")),
            ],
        ),
        "prompt": (
            "请为页面建立统一的动效手感：按钮、图标和开关用短促时长，卡片、菜单和弹窗用适中时长，大图揭示和页面转场可以偏慢；内容进场用减速缓动，元素离场用加速缓动，进度条和持续旋转保持匀速；同一组元素按阅读顺序小间隔错峰进入，整组动画连贯轻快，连续操作不让用户等待。"
            "减弱动态时保留状态变化，取消装饰性位移。沿用项目现有设计规范。"
        ),
    },
    {
        "id": "tokens",
        "title": "动效 Interaction Token",
        "keywords": "interaction token 动效变量 设计令牌 duration easing distance scale 全局变量",
        "note": "把时长、缓动、距离和缩放比例定义成全局变量，所有动画只引用 token。修改一处即可全局生效，也避免每处动画各写一套数值。",
        "content": _table(
            ("Token", "含义", "参考取值"),
            [
                (_td("duration-fast", True), _td("按钮、图标、按下反馈"), _td("120–180ms")),
                (_td("duration-normal", True), _td("卡片进入、菜单展开"), _td("200–260ms")),
                (_td("duration-medium", True), _td("弹窗、抽屉、底部面板"), _td("280–360ms")),
                (_td("duration-slow", True), _td("大图揭示、页面转场"), _td("400–600ms")),
                (_td("easing-enter", True), _td("内容进入"), _td("ease-out 系")),
                (_td("easing-exit", True), _td("内容离开"), _td("ease-in 系")),
                (_td("easing-move", True), _td("位置移动、跟随"), _td("ease-in-out 或 spring")),
                (_td("distance-xs / sm / md", True), _td("位移幅度三档"), _td("8px / 16px / 24px")),
                (_td("scale-press", True), _td("按压缩放"), _td("0.96–0.98")),
                (_td("scale-hover", True), _td("悬停放大"), _td("1.02–1.05")),
            ],
        ),
        "prompt": (
            "为项目建立动效 token：定义快、中、慢三档时长变量与进、出场缓动变量，位移类动效引用近、中、远三档距离变量，按压与悬停的缩放比例单独建变量；之后所有动画声明只引用这些变量，不再逐处写死数值，修改一处即可全局生效。"
            "完成后全局检查，不残留游离于 token 之外的动画数值。沿用项目现有设计规范。"
        ),
    },
    {
        "id": "overlay",
        "title": "浮层定位系统",
        "keywords": "浮层定位 popover tooltip 下拉菜单 翻转 碰撞检测 portal 视口 箭头 嵌套浮层 auto placement flip shift offset",
        "note": "AI 经常把 Popover、Tooltip 做出屏幕。浮层定位不是一种动效，而是一组必须写进需求的定位规则。",
        "content": _table(
            ("术语", "效果说明", "给 AI 的描述话术"),
            [
                (_td("Auto Placement 自动方向"), _td("默认方位"), _td("优先向下显示，空间不足自动翻转")), 
                (_td("Collision Detection 碰撞检测"), _td("不出屏"), _td("浮层任何情况下不可超出视口")),
                (_td("Flip 自动翻转"), _td("上下换边"), _td("下方空间不足切换到上方")),
                (_td("Shift 自动偏移"), _td("水平修正"), _td("靠近页面边缘时水平移动保持可见")),
                (_td("Offset 间距"), _td("与触发点的距离"), _td("触发点与浮层保持固定小间距")),
                (_td("Portal 渲染"), _td("脱离文档流"), _td("浮层渲染到顶层容器，避免被 overflow 裁剪")),
                (_td("Arrow Position 箭头定位"), _td("指向关系"), _td("箭头始终指向触发点")),
                (_td("Nested Overlay 嵌套浮层"), _td("层级关系"), _td("子浮层打开时不误关父级菜单")),
            ],
        ),
        "prompt": (
            "为页面里所有 Tooltip、Popover 和下拉菜单实现可靠的浮层定位：默认在触发点下方显示，上下空间不足自动翻转；靠近视口边缘时水平偏移保持完全可见，任何情况下浮层不可超出视口、不被容器裁剪；触发点与浮层保持固定小间距，箭头始终指向触发点；子级浮层打开时不关闭父级。"
            "触屏与键盘同样能打开和关闭浮层。沿用项目现有设计规范。"
        ),
    },
    {
        "id": "layer",
        "title": "z-index 层级系统",
        "keywords": "z-index 层级 系统 layer token 遮罩 弹窗 toast tooltip 99999",
        "note": "层级混乱是浮层互相遮挡的根源。按用途分层并统一管理，不随意写大数值。",
        "content": _table(
            ("层级", "内容", "给 AI 的描述话术"),
            [
                (_td("Base Layer 基础层"), _td("页面正常内容"), _td("页面正常内容位于最底层")),
                (_td("Sticky Layer 吸顶层"), _td("吸顶导航、吸顶表头"), _td("吸顶元素高于普通内容")),
                (_td("Dropdown Layer 下拉层"), _td("下拉菜单、组合框列表"), _td("下拉内容高于吸顶元素")),
                (_td("Overlay Layer 遮罩层"), _td("弹窗背景遮罩"), _td("遮罩覆盖页面全部内容")),
                (_td("Modal Layer 弹窗层"), _td("弹窗本体"), _td("弹窗高于遮罩")),
                (_td("Toast Layer 提示层"), _td("全局轻提示"), _td("Toast 保持高于普通弹窗，或按系统规范统一管理")),
                (_td("Tooltip Layer 提示层"), _td("悬停提示"), _td("Tooltip 不应被普通卡片遮挡")),
            ],
        ),
        "prompt": (
            "为项目建立统一的 z-index 分层：按基础内容、吸顶导航、下拉菜单、遮罩、弹窗、全局提示、Tooltip 的固定顺序定义层级变量，所有浮层引用对应变量，不出现临时写死的大数值；新浮层按用途归入对应层级，Toast 始终在普通弹窗之上，Tooltip 不被卡片遮挡。"
            "完成后全局检查，不残留游离于层级变量之外的 z-index。沿用项目现有设计规范。"
        ),
    },
    {
        "id": "triggers",
        "title": "触发方式词汇表",
        "keywords": "触发方式 hover focus click pointer 滚动触发 手势 路由 状态变化 定时 空闲 hover intent once replay scrub",
        "note": "同一种动效可以配不同触发。描述动效时先说清触发方式，AI 才不会漏掉移动端和键盘路径。关键区分：进入视口像按下播放键，触发后动画自己播完；跟随滚动像拖动进度条，滚到哪里就播放到哪里。",
        "content": _table(
            ("触发族", "常用细分写法", "提醒"),
            [
                (_td("悬停 Hover"), _td("进入 / 离开 / 持续 / 悬停意图（停留片刻再展开，防误触）/ 父级悬停 / 临近触发"), _td("悬停意图用于菜单；临近触发只给少量重点元素")),
                (_td("键盘焦点 Focus"), _td("可见焦点（仅键盘操作显示焦点环）/ 内部焦点（子元素聚焦容器高亮）"), _td("焦点反馈与悬停共用一套颜色语言，但不能只靠位移表示")),
                (_td("点击 Click / Tap / Press"), _td("按下状态 / 开关切换 / 长按 / 双击"), _td("按下要有收缩反馈；双击网页里应少用；长按主要给触屏")),
                (_td("指针 Pointer"), _td("位置映射 / 距离感应 / 移动方向 / 移动速度"), _td("触屏没有持续悬停，指针类动效要交代降级")),
                (_td("进入视口 In view"), _td("进入 / 离开复位 / 只播一次 / 每次进入重播"), _td("先说清播一次还是每次重播，回滚行为要明确")),
                (_td("跟随滚动 Scroll-linked"), _td("滚动驱动 / 进度同步 / 固定内容"), _td("与“进入视口”区分：一个像播放键，一个像进度条")),
                (_td("手势 Gesture"), _td("拖拽开始 / 拖拽中 / 松手吸附或回位 / 快速滑动"), _td("元素跟手移动，松手后有归宿")),
                (_td("页面加载与路由 Route"), _td("页面加载 / 组件挂载 / 进入页面 / 离开页面 / 数据就绪"), _td("切换页面时取消未完成的动画，不能阻塞导航")),
                (_td("状态变化 State"), _td("展开收起 / 选中取消 / 加载成功失败 / 内容更新 / 数值变化"), _td("状态动效解释“刚才的操作带来了什么变化”，比装饰更重要")),
                (_td("定时与空闲 Timer"), _td("延时开始 / 自动播放 / 定时切换 / 空闲触发 / 循环"), _td("自动播放不抢控制权：用户操作、切走标签页或减少动态时暂停")),
            ],
        ),
        "prompt": (
            "为导航菜单加入悬停意图：光标在菜单项上停留片刻才展开下级，快速划过不触发；移出后稍有延迟再收起，避免误触。键盘聚焦同样能展开，Esc 关闭；触屏改为点击切换；减弱动态时展开收起改为短促淡化。"
            "沿用项目现有设计规范。"
        ),
    },
    {
        "id": "ux",
        "title": "UX 规则：怎样动才好用",
        "keywords": "UX 规则 feedback affordance focus reduced motion 减少动态 反馈 操作暗示 焦点 可访问性",
        "note": "第四层不再增加视觉花样，它约束前面所有动效：用户能不能看懂、能不能继续操作、手机和键盘能不能完成同一件事。",
        "content": _table(
            ("规则", "检查内容", "给 AI 的描述话术"),
            [
                (_td("Feedback 反馈"), _td("操作前看得出哪里能点；操作时有按下或加载状态；操作后明确成功失败；失败后知道怎么修正重试"), _td("给所有可操作组件补齐反馈：悬停、聚焦和按下有状态变化；异步操作显示加载，完成后显示结果和下一步")),
                (_td("Affordance 操作暗示"), _td("按钮有边界和文字；链接有下划线或颜色；可拖拽有把手；可展开有箭头；输入框有标签"), _td("动效不能替代操作暗示：无论动效是否播放，控件本身要能看出可以操作")),
                (_td("Focus 焦点与注意力"), _td("视觉聚焦（弹窗打开背景变暗）与键盘焦点（焦点进入弹窗）是两件事；关闭后焦点回到原按钮"), _td("弹窗打开后弱化背景并把键盘焦点移入，关闭后焦点还给触发按钮；所有可操作元素保留清楚的键盘聚焦样式")),
                (_td("Reduced motion 减少动态"), _td("优先减弱：大幅视差和滚动缩放、长距离飞入飞出、自动循环和持续旋转、光标拖尾与强烈闪烁、无法停止的轮播"), _td("读取系统减少动态偏好：取消大幅位移和循环动画，保留短促淡化、颜色变化和进度提示，功能不受影响")),
            ],
        ),
        "prompt": (
            "检查并补齐页面动效的可用性：每个操作有按下或加载反馈，结果有成功失败提示；控件保留边界、文字等操作暗示，不依赖动效表达可点击；弹窗打开后键盘焦点移入、关闭后还给触发按钮；读取减少动态偏好，优先取消大幅视差、滚动缩放、长距离飞入与自动轮播，保留短促淡化与状态提示。"
            "仅用键盘也能完成主要操作路径。沿用项目现有设计规范。"
        ),
    },
    {
        "id": "checklist",
        "title": "触发描述五步检查",
        "keywords": "五步检查 描述模板 触发 恢复 降级 提示词模板",
        "note": "描述任何动效时，沿这五步检查一遍，四层结构就齐了。缺一步，AI 就会自行发挥。",
        "content": (
            '<ol class="spec-steps">'
            "<li><strong>谁触发</strong>——对象与角色：哪个元素、在什么身份下被操作。</li>"
            "<li><strong>在什么条件下开始</strong>——时机与状态：悬停、点击、进入视口还是状态变化。</li>"
            "<li><strong>触发后使用什么动效</strong>——画面变化：位移、缩放、淡化还是重排。</li>"
            "<li><strong>结束或离开后怎样恢复</strong>——还原路径：回原位、保持终态还是等待下一次触发。</li>"
            "<li><strong>键盘和触屏怎样替代</strong>——可访问性：等价操作与减少动态降级。</li>"
            "</ol>"
        ),
        "prompt": (
            "我想在【页面位置】实现一个动效：由【对象】在【触发条件】触发，使用【动效类型】；触发时【画面怎样变化】，结束或离开后【怎样恢复原状】。键盘和触屏要有等价操作；用户开启减少动态时退化为简短淡入淡出。请在当前代码仓库中直接实现，并沿用项目现有设计规范。"
        ),
    },
]


def render_spec_section():
    groups = []
    for group in GROUPS:
        prompt = _prompt(group["prompt"]) if group.get("prompt") else ""
        groups.append(
            f'<article class="spec-group" data-spec-item data-cat="spec" '
            f'data-name="{_esc(group["title"] + " " + group["keywords"])}" '
            f'id="spec-{_esc(group["id"])}">'
            f'<div class="spec-group-head"><h3>{_esc(group["title"])}</h3>'
            f'<span class="spec-group-tag">规范</span></div>'
            f'<p class="spec-note">{_esc(group["note"])}</p>'
            f'{group["content"]}{prompt}</article>'
        )
    return (
        '<section class="category-section spec-section" id="section-spec" data-cat="spec" aria-labelledby="spec-title">'
        '<div class="section-head"><div><h2 id="spec-title">实现规范</h2>'
        '<p>不是动效效果，而是控制 AI 动画质量的参数、词汇与验收规则——让效果做对。</p></div>'
        f'<span class="section-count">{len(GROUPS)} 组</span></div>'
        '<div class="spec-list">' + "".join(groups) + "</div></section>"
    )


SPEC_CHIP = '<button class="chip" data-filter="spec" aria-pressed="false" type="button">实现规范</button>'
