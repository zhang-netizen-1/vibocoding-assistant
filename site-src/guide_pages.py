"""Content and markup for the five companion field guides."""

from html import escape


def item(title, english, description, fit, avoid, demo, labels, check):
    return dict(title=title, english=english, description=description, fit=fit,
                avoid=avoid, demo=demo, labels=labels, check=check)


GUIDES = {
    "layout": {
        "number": "03", "name": "布局与响应式", "short": "布局", "english": "LAYOUT",
        "intro": "让内容在不同宽度下保持清晰的顺序与关系。",
        "groups": [
            ("结构与空间", [
                item("响应式网格", "Responsive Grid", "容器变窄时减少列数，卡片顺序保持不变。", "卡片目录、搜索结果", "把宽表格强行改成卡片", "grid", ("宽布局", "窄布局"), "两种宽度均无横向溢出，阅读顺序一致。"),
                item("侧栏工作区", "Sidebar Shell", "主内容与工具导航分工，窄屏时侧栏收起。", "管理后台、编辑器", "内容很少的单页", "sidebar", ("展开侧栏", "收起侧栏"), "主内容始终可见，侧栏收起后仍有导航入口。"),
                item("主次分栏", "Split View", "主要任务占更多宽度，辅助信息靠侧排列。", "详情与目录、预览与属性", "两块信息都需要同等注意力", "split", ("并列显示", "上下排列"), "窄屏改为上下顺序，主要内容先出现。"),
            ]),
            ("适配与密度", [
                item("容器内适配", "Container Query", "组件根据所在容器宽度调整，而非只看整页宽度。", "可复用卡片、嵌入模块", "组件尺寸永远固定的场景", "container", ("宽容器", "窄容器"), "同一组件放入不同列宽仍可读、可操作。"),
                item("信息密度", "Content Density", "用间距、行高和信息分组控制页面密度。", "列表、仪表盘、工作台", "靠缩小文字塞入内容", "density", ("舒适", "紧凑"), "紧凑模式仍保留可辨认文字和操作空间。"),
                item("吸顶阅读区", "Sticky Reading Header", "滚动内容时保留必要的标题与定位信息。", "长文章、长列表", "页头占据大部分手机屏幕", "sticky", ("开始阅读", "向下阅读"), "滚动时标题可见，内容不会被吸顶区域遮挡。"),
            ]),
        ],
    },
    "visual": {
        "number": "04", "name": "视觉风格", "short": "视觉", "english": "VISUAL",
        "intro": "用同一份内容，对照六种完整的视觉方向与组件语言。",
        "groups": [
            ("克制与叙事", [
                item("极简主义", "Minimalism", "用留白、少量颜色和明确层级，让核心内容先被看见。", "工具产品、作品集、信息精简的官网", "把必要信息和操作一起删掉", "minimal", ("页面预览", "组件细节"), "减少装饰后，标题、正文、操作和焦点仍清晰。"),
                item("编辑式排版", "Editorial", "借用出版物的标题对比、网格和编排节奏，强化内容叙事。", "文化品牌、专题文章、内容型产品", "需要连续快速操作的密集后台", "editorial", ("页面预览", "组件细节"), "窄屏时保留阅读顺序，装饰字不遮挡正文。"),
                item("自然有机", "Organic", "用大地色、柔和曲线和轻质感，表达亲近与温度。", "生活方式、健康内容、可持续主题", "需要强烈警示和高密度查数的界面", "organic", ("页面预览", "组件细节"), "自然形状只作装饰，正文与操作始终可读。"),
            ]),
            ("材质与态度", [
                item("玻璃拟态", "Glassmorphism", "在有层次的背景上使用半透明表面、柔和模糊与清晰边界。", "品牌展示、媒体封面、轻量浮层", "长篇正文或对比度难控制的数据界面", "glass", ("页面预览", "组件细节"), "透明层在复杂背景上仍有足够文字对比，并提供模糊降级。"),
                item("新粗野主义", "Neo-brutalism", "以硬边框、高饱和色和偏移阴影，形成直接鲜明的表达。", "创意活动、实验性工具、青年品牌", "要求平静与审慎的高风险任务", "brutalist", ("页面预览", "组件细节"), "强视觉之下仍保留明确层级、可见焦点与可读文字。"),
                item("新拟态", "Neumorphism", "用柔和的凸起与内凹表面，营造一体成形的控件质感。", "轻量控制面板、低密度展示", "只靠阴影区分按钮和状态", "neumorphic", ("页面预览", "组件细节"), "控件同时具有文字、边界和焦点提示，不依赖阴影传达状态。"),
            ]),
        ],
    },
    "interaction": {
        "number": "05", "name": "交互规则", "short": "交互", "english": "BEHAVIOR",
        "intro": "说明操作条件、结果和异常，让界面行为可预期。",
        "groups": [
            ("输入与反馈", [
                item("字段就地校验", "Inline Validation", "在字段旁说明错误原因，并保留已输入的内容。", "登录、创建、编辑表单", "只弹一条模糊的错误提示", "validation", ("有效输入", "触发错误"), "错误文本与字段关联，修正后可继续。"),
                item("提交状态链", "Submission States", "提交过程清楚区分等待、完成和失败。", "保存、发送、付款前步骤", "点击后按钮毫无变化", "submit", ("提交成功", "请求失败"), "提交中防止重复操作，失败时保留输入。"),
                item("撤销操作", "Undo Action", "可恢复的删除先给出明确撤销机会。", "清单、标签、轻量编辑", "不可逆且高风险的删除", "undo", ("删除条目", "撤销删除"), "撤销恢复原位置与内容，提示有明确期限。"),
            ]),
            ("选择与恢复", [
                item("批量选择", "Bulk Selection", "选择数量与批量动作同步出现和消失。", "列表管理、文件管理", "只有一项可操作的页面", "bulk", ("选中项目", "清除选择"), "键盘和指针均可选择，数量准确更新。"),
                item("乐观更新", "Optimistic Update", "先显示预期结果，失败时回滚并解释。", "收藏、点赞、轻量排序", "无法可靠回滚的关键交易", "optimistic", ("保存成功", "模拟失败"), "失败后恢复原状态，不把本地演示误报为真实保存。"),
                item("键盘焦点", "Keyboard Focus", "焦点可见，进入和离开组件的路径清楚。", "菜单、弹窗、密集控件", "只设计鼠标悬停态", "focus", ("移动焦点", "返回起点"), "Tab 可到达每个操作，焦点顺序符合阅读顺序。"),
            ]),
        ],
    },
    "pages": {
        "number": "06", "name": "页面类型", "short": "页面", "english": "PAGE TYPES",
        "intro": "从页面目标出发，理解信息和操作如何组成完整结构。",
        "groups": [
            ("呈现与浏览", [
                item("落地页", "Landing Page", "一句核心价值、证据和主动作形成清晰路径。", "介绍产品或活动", "需要密集管理数据的任务", "landing", ("桌面", "手机"), "主动作在首屏可发现，证据内容有明确来源。"),
                item("仪表盘", "Dashboard", "关键指标优先，图表和待办解释变化。", "日常监测和运营", "单次提交任务", "dashboard", ("桌面", "手机"), "指标注明时间与单位，异常状态有解释。"),
                item("结果列表页", "Results List", "搜索、筛选、排序和结果数量保持一致。", "查找项目、商品或文章", "只展示一个固定对象", "list", ("桌面", "手机"), "空结果有恢复入口，筛选状态可见。"),
            ]),
            ("查看与操作", [
                item("详情页", "Detail Page", "核心内容先行，辅助信息与操作保持可达。", "商品、作品、任务详情", "集合浏览为主要任务", "detail", ("桌面", "手机"), "返回时保留列表上下文，长内容有层级。"),
                item("设置页", "Settings Page", "按主题分组设置，并说明修改何时生效。", "偏好、账户、通知", "高频浏览内容", "settings", ("桌面", "手机"), "保存结果明确，危险操作与普通设置分开。"),
                item("分步表单", "Step-by-step Form", "长任务分段完成，显示当前位置与剩余步骤。", "开户、申请、复杂创建", "只有两三个简单字段", "wizard", ("桌面", "手机"), "前后步骤保留输入，最终提交前可检查。"),
            ]),
        ],
    },
    "data": {
        "number": "07", "name": "数据可视化", "short": "数据", "english": "DATA VIS",
        "intro": "用合适的图形表达趋势、对比、构成与异常。",
        "groups": [
            ("变化与比较", [
                item("趋势折线", "Trend Line", "沿连续时间轴观察方向、峰值和异常。", "日、周、月趋势", "无顺序的独立分类", "line", ("本周", "上周"), "时间范围、单位和数值都有文字说明。"),
                item("柱状对比", "Bar Comparison", "用统一基线比较不同类别的大小。", "渠道、地区、产品对比", "类别过多且标签无法读清", "bar", ("访问量", "转化量"), "柱形从同一零基线开始，标签与单位可见。"),
                item("构成堆叠", "Stacked Composition", "看总量同时看各部分占比。", "来源构成、预算分配", "需要精确比较细小差异", "stacked", ("本期", "上期"), "图例与部分数值对应，总量可核对。"),
            ]),
            ("分布与明细", [
                item("占比环图", "Donut Share", "呈现少量类别的整体占比。", "三到五个主要部分", "大量类别或接近的细分值", "donut", ("本月", "上月"), "百分比合计为 100%，提供文字列表。"),
                item("热力矩阵", "Heatmap", "用二维位置查看高低分布。", "星期与时段、区域与指标", "只有一维分类", "heatmap", ("活跃度", "完成率"), "颜色深浅有图例，也能读取具体数值。"),
                item("可排序数据表", "Sortable Table", "保留精确值并允许按列比较。", "需要查数和核对明细", "只需表达总体趋势", "table", ("按名称", "按数值"), "排序方向可见，表头与数据列关联。"),
            ]),
        ],
    },
}


def all_items(guide):
    return [entry for _, entries in guide["groups"] for entry in entries]


# Each instruction describes work an agent can perform in a real repository. The
# card description remains editorial guidance; it is not used as implementation text.
PROMPT_STEPS = {
    "layout": {
        "grid": ["把同类内容放入 CSS Grid，宽容器显示多列，空间不足时逐级减少列数；根据卡片最小可读宽度设置断点或 auto-fit，不写死卡片数量。", "保持 DOM 顺序与视觉顺序一致；卡片内长标题、按钮和图片允许收缩或换行。"],
        "sidebar": ["在桌面宽度建立导航侧栏与主内容区；窄屏收起侧栏时提供可通过键盘打开的导航入口。", "主内容区设置 min-width: 0；切换侧栏状态后，标题、导航和当前操作仍可见。"],
        "split": ["按任务优先级建立主内容和辅助内容两栏，主栏获得更多宽度。", "空间不足时按主内容在前、辅助内容在后的阅读顺序改为单列，避免用 CSS order 改乱键盘顺序。"],
        "container": ["将目标组件设为可复用容器，根据自身容器宽度调整内部布局，而非只依赖视口媒体查询。", "分别把同一组件放入宽、窄容器验证标题、正文和操作不会溢出。"],
        "density": ["为列表或工作区提供舒适、紧凑两档密度，并统一调整行高、间距、分组和控件尺寸。", "紧凑档保留可读字号、操作命中区和明确分隔；选择状态要能识别。"],
        "sticky": ["只把阅读定位必需的标题或工具设为吸顶；控制吸顶高度与层级。", "为锚点和内容设置合适的 scroll-margin 或偏移，确保手机上滚动后正文不会被遮挡。"],
    },
    "visual": {
        "minimal": ["建立一套克制的视觉变量：暖白 #FAF9F4、深墨 #20241E、强调色 #B94F33；颜色主要用于主操作和关键状态。", "用明确的标题层级、宽松留白、细分隔线组织首屏、内容区和页尾；保留必要的信息与操作。", "将按钮、输入框、卡片和焦点态统一到这套语言：轻边框、少阴影、清晰标签，交互状态不只靠颜色区分。"],
        "editorial": ["以纸张色 #EFE8D8、深棕 #2B211B、陶土色 #BD5739 建立配色变量。", "用有辨识度的衬线展示标题搭配清晰的正文字体，安排大小标题、引言、细线和不对称网格，形成可阅读的编排节奏。", "把卡片、按钮、输入框与页尾纳入同一出版物语言；装饰字不得覆盖正文。"],
        "organic": ["使用柔和底色 #E8E7D8、森林绿 #2F3E2D、橄榄绿 #8CA581 和主操作色 #415B3B。", "以温和曲线、自然形状、克制的纸张质感与舒展间距组织页面；形状只作辅助层。", "让按钮、表单与卡片共享圆角和色彩规则，保持正文对比度与操作辨识度。"],
        "glass": ["建立深蓝 #142944 至 #294665 的背景层次，并用半透明面板、清晰描边和有限的背景模糊形成前后关系。", "正文与操作始终放在具有足够对比度的表面上；为不支持 backdrop-filter 的环境提供不透明回退。", "统一导航、卡片、按钮、输入框和焦点态；不要把长篇正文直接铺在复杂背景上。"],
        "brutalist": ["建立亮黄 #F6E15C、近黑 #171414、粉色 #F19CA7 与橙色 #FF8B73 的高对比调色板。", "使用硬边框、偏移实体阴影、强字体层级与清楚的版块分割，重点突出一个主操作。", "按钮、输入框、卡片与状态提示采用一致的边框和阴影规则，焦点态要明显，避免色彩争抢正文。"],
        "neumorphic": ["以浅灰紫 #E6EAF2、文字色 #29344F 和蓝色 #839AD4 建立低密度的控制面板。", "用轻微外凸和内凹表达表面层级，控制阴影范围，避免大面积模糊造成灰蒙。", "每个可操作控件同时保留文字标签、可辨边界、按下态和独立焦点态，不依赖阴影传达状态。"],
    },
    "interaction": {
        "validation": ["使用真实表单字段和明确规则，在输入或失焦时显示具体错误；不要清空用户已输入内容。", "把错误消息与对应字段用 aria-describedby 关联，设置 aria-invalid，修正后立即清除错误状态。"],
        "submit": ["实现待提交、提交中、成功、失败四种状态，并接入项目现有提交函数或接口。", "提交中阻止重复请求；失败后保留输入、解释原因并允许重试；成功后显示可确认的结果。"],
        "undo": ["对可恢复删除保留被删项目的内容与原位置，显示限时撤销入口。", "撤销时恢复原位置和状态；到期后再完成最终删除。不可逆操作仍按项目现有确认流程处理。"],
        "bulk": ["为列表项提供原生复选框、全选或清除入口，并从选择集合实时计算数量。", "只有存在选中项时显示可用的批量动作；筛选或分页变化后核对选中范围，键盘可完成全流程。"],
        "optimistic": ["针对可回滚的轻量操作先更新界面，再调用真实保存接口。", "请求失败时恢复原状态、说明失败并提供重试；连续点击要避免旧响应覆盖新状态。"],
        "focus": ["梳理目标区域的 Tab 顺序，所有按钮、链接、表单和弹层入口都使用可聚焦语义元素。", "提供清晰的 :focus-visible 样式；若包含弹窗，打开时移入焦点、关闭时归还触发控件。"],
    },
    "pages": {
        "landing": ["首屏呈现一句可核实的核心价值、一个主动作和对应说明；主动作连接到实际可用的路径。", "在后续区块展示真实功能或证据与清楚的下一步，手机宽度保持标题、证据和 CTA 的阅读顺序。"],
        "dashboard": ["按使用频率和重要度排布指标、趋势与待办；每个指标注明单位、时间范围和来源。", "处理加载、空数据与异常状态；图表变化给出文字解释，窄屏按优先级纵向排列。"],
        "list": ["建立可实际使用的搜索、筛选和排序，并让结果数量与当前查询条件同步。", "筛选条件保持可见且可清除；无结果时提供恢复入口，返回详情后保留列表上下文。"],
        "detail": ["将标题、核心内容与主要操作放在前部，辅助元数据和相关内容按清晰层级分组。", "长内容提供结构化标题；从列表进入并返回时保留原筛选、滚动或页码上下文。"],
        "settings": ["按主题划分设置组，使用适合字段类型的真实控件，并说明每项是即时生效还是保存后生效。", "保存成功与失败给出明确反馈；未保存更改有保护，危险操作单独分区并按风险确认。"],
        "wizard": ["将长表单分为有名称的步骤，显示当前步骤与总步数；前后导航保留已输入内容。", "每步就地校验，最终提交前提供汇总检查；提交中防重复，失败时仍能返回修改。"],
    },
    "data": {
        "line": ["使用项目数据按时间顺序绘制折线，标注时间范围、单位与关键刻度。", "切换时间段时同步更新图形和文字摘要；空值不要连接成虚假连续趋势，并提供可读数值。"],
        "bar": ["按统一的零基线绘制不同类别的柱形，类别标签和单位完整可读。", "切换指标时同步更新数值、标题与摘要；过多类别允许滚动或调整布局，避免截断标签。"],
        "stacked": ["从同一份数据计算各部分及总量，让堆叠长度和图例数值一致。", "给出每部分名称、数量或比例；切换周期时同步更新图形、总量与文字说明。"],
        "donut": ["仅对少量类别计算占比，明确分母、时间范围和舍入方式，使展示百分比总和可核对。", "图旁提供包含名称、数值和比例的文字列表；类别过多时改用更适合比较的图形。"],
        "heatmap": ["从二维数据生成行列标题、色阶和每格数值，并说明色阶代表的范围与单位。", "颜色之外提供数值或可访问名称；缺失数据用独立状态表示，不能当作零值。"],
        "table": ["使用语义化 table 和列头，按真实字段实现稳定排序，显示当前排序列与升降方向。", "数值按数值比较而非字符串比较；表格在窄屏可横向滚动，保留列名和单位。"],
    },
}


def build_prompt(section, entry):
    steps = PROMPT_STEPS[section][entry["demo"]]
    target = "当前正在开发的页面或组件；如果上下文没有指定目标，选择项目首页中的对应区域"
    if section == "visual":
        target = "当前正在开发的页面；如果上下文没有指定目标，选择项目首页"
    elif section == "data":
        target = "当前页面中的相关图表；如果尚无图表，选择最合适的数据展示区域"
    lines = [
        f'请在当前代码仓库中直接实现「{entry["title"]}」。先检查项目技术栈、路由、现有组件和相关数据。目标定位：{target}。完成代码修改，不要只给设计建议。',
        '',
        '实施要求：',
        *(f'{index}. {step}' for index, step in enumerate(steps, 1)),
        '',
        '边界与验收：',
        '- 保留现有业务文案、功能和真实数据口径；没有可用数据时使用明确标注的示例数据，不能伪装为真实指标。',
        f'- 验证关键结果：{entry["check"]}',
        '- 检查桌面与约 390px 手机宽度，确认无横向溢出，键盘可操作且焦点可见；运行项目现有构建或相关测试。',
        '- 完成后列出修改文件、实际验证结果及仍存在的限制。',
    ]
    return '\n'.join(lines)


def demo_markup(section, entry):
    demo = entry["demo"]
    if section == "layout":
        return ('<div class="mini-layout" tabindex="0" aria-label="可滚动的布局预览">'
                '<div class="mini-layout-top"><b>FIELD / GUIDE</b><span>◯ ◯ ◯</span></div>'
                '<div class="mini-layout-body"><aside class="mini-layout-side"><i></i><i></i><i></i></aside>'
                '<div class="mini-layout-main"><div class="mini-layout-heading"><b>项目概览</b><small>清晰排列内容</small></div>'
                '<div class="mini-layout-items"><span>01<br>资料</span><span>02<br>任务</span><span>03<br>进展</span></div>'
                '<p>内容保持顺序，空间随宽度变化。</p><div class="mini-layout-tail">更多内容 · 继续阅读</div>'
                '</div></div><div class="mini-layout-bottom">首页　项目　设置</div></div>')
    if section == "visual":
        return (f'<div class="style-preview style-{demo}" role="img" aria-label="{escape(entry["title"])}：页面预览">'
                '<div class="style-page">'
                '<div class="style-top"><span class="style-logo">FORM<span class="style-logo-mark">✳</span>STUDIO</span><span>INDEX / 01</span></div>'
                '<div class="style-main"><div class="style-copy"><span class="style-eyebrow">IDEA JOURNAL · 2026</span>'
                '<strong class="style-title">让灵感，<br>有迹可循。</strong>'
                '<p>把日常想法整理成值得回看的作品。</p>'
                '<span class="style-action">探索作品 <i aria-hidden="true">↗</i></span></div>'
                '<div class="style-art" aria-hidden="true"><span class="style-art-shape"></span><span class="style-art-detail"></span><small>01 / FORM</small></div></div>'
                '<div class="style-bottom"><span>SELECTED STORIES</span><span>SCROLL TO EXPLORE ↓</span></div></div>'
                '<div class="style-detail"><div class="style-detail-top">FORM / COMPONENT SET <span>02</span></div>'
                '<div class="style-detail-card"><span class="style-chip">新系列 · 2026</span><strong>灵感手记</strong>'
                '<p>收集片段、整理想法，把下一步放在眼前。</p>'
                '<div class="style-field">输入项目名称 <span aria-hidden="true">＋</span></div>'
                '<span class="style-action">创建项目 <i aria-hidden="true">↗</i></span></div>'
                '<div class="style-detail-foot">TYPE　/　COLOR　/　SURFACE　/　SPACE</div></div></div>')
    if section == "interaction":
        if demo == "validation":
            return '<div class="mini-interaction"><label>项目名称<input data-field type="text" value="新的灵感" aria-describedby="guide-validation-message"></label><p id="guide-validation-message" data-message role="status">名称已填写，可以继续。</p><span class="mini-action">下一步 ↗</span></div>'
        if demo == "submit":
            return '<div class="mini-interaction"><b>保存项目</b><p data-message role="status">尚未提交。</p><span class="mini-action">提交项目 ↗</span></div>'
        if demo == "undo":
            return '<div class="mini-interaction"><b>今日清单</b><div class="mini-task" data-task>整理页面结构 <span>待完成</span></div><p data-message role="status">条目仍在清单中。</p></div>'
        if demo == "bulk":
            return '<div class="mini-interaction"><b>文件列表</b><div class="mini-task">□　首页草图</div><div class="mini-task">□　组件说明</div><p data-message role="status">未选择项目。</p></div>'
        if demo == "optimistic":
            return '<div class="mini-interaction"><b>灵感卡片</b><div class="mini-task">设计片段 <span data-state-label>未收藏</span></div><p data-message role="status">尚未操作。</p></div>'
        return '<div class="mini-interaction mini-focus"><b>焦点顺序</b><button type="button">第一项</button><button type="button">第二项</button><button type="button">第三项</button><p data-message role="status">使用下方按钮移动焦点。</p></div>'
    if section == "pages":
        content = {
            "landing": '<div class="mini-page-hero"><small>PRODUCT / 01</small><b>把想法变成作品。</b><p>清楚呈现价值与下一步。</p><span>开始体验 ↗</span></div><div class="mini-page-tiles"><i></i><i></i><i></i></div>',
            "dashboard": '<div class="mini-page-metrics"><span><b>1,280</b><small>访问</small></span><span><b>24%</b><small>转化</small></span></div><div class="mini-page-chart">▂ ▄ ▃ ▆ ▅ ▇ ▆</div>',
            "list": '<div class="mini-page-search">⌕　搜索与筛选</div><div class="mini-page-list"><p>01　工作台设计 <span>进行中</span></p><p>02　页面梳理 <span>已完成</span></p><p>03　动效检查 <span>待开始</span></p></div>',
            "detail": '<div class="mini-page-media"></div><h4>山间日落</h4><p>作品说明与关键细节。</p><span class="mini-page-cta">收藏作品 ↗</span>',
            "settings": '<div class="mini-page-settings"><p>通知偏好 <span>已开启</span></p><p>显示方式 <span>跟随系统</span></p><p>账户安全 <span>查看 ↗</span></p></div>',
            "wizard": '<div class="mini-page-steps">●────●────○<small>信息　验证　完成</small></div><div class="mini-page-field">项目名称</div><div class="mini-page-field">项目类型</div><span class="mini-page-cta">下一步 ↗</span>',
        }[demo]
        return f'<div class="mini-page"><div class="mini-page-top">NORTH / STUDIO <span>☰</span></div><div class="mini-page-content">{content}</div><div class="mini-page-foot">概览　　内容　　我的</div></div>'
    if demo == "line":
        graphic = '<svg viewBox="0 0 260 130" role="img" aria-label="六日趋势折线：42、58、49、74、66、88"><path d="M12 115H248M12 74H248M12 33H248" class="chart-grid"/><polyline class="chart-line" points="16,94 60,78 104,87 148,62 192,70 240,46"/></svg>'
    elif demo == "bar":
        graphic = '<div class="mini-bars" role="img" aria-label="四类数据柱状对比：42、68、54、82"><i style="--h:42%"></i><i style="--h:68%"></i><i style="--h:54%"></i><i style="--h:82%"></i></div>'
    elif demo == "stacked":
        graphic = '<div class="mini-stacked" role="img" aria-label="总量 100，三部分占比 45、35、20"><i></i><i></i><i></i></div><div class="mini-legend">● 自然 45%　● 推荐 35%　● 直接 20%</div>'
    elif demo == "donut":
        graphic = '<div class="mini-donut" role="img" aria-label="三类占比：45%、35%、20%"><b>100%</b></div><div class="mini-legend">自然 45% · 推荐 35% · 直接 20%</div>'
    elif demo == "heatmap":
        graphic = '<div class="mini-heatmap" role="img" aria-label="星期与时段的活跃度矩阵">' + ''.join(f'<i data-level="{(n * 7 + n // 4 * 3) % 5}"></i>' for n in range(28)) + '</div><div class="mini-legend">周一至周日 · 四个时段</div>'
    else:
        graphic = '<table class="mini-table"><thead><tr><th scope="col">渠道</th><th scope="col">访问</th></tr></thead><tbody><tr><td>自然搜索</td><td>68</td></tr><tr><td>推荐内容</td><td>42</td></tr><tr><td>直接访问</td><td>82</td></tr></tbody></table>'
    return f'<div class="mini-data"><div class="mini-data-title">ANALYTICS <span data-period>本周</span></div>{graphic}<p data-summary>演示数据 · 单位与口径请按项目替换</p></div>'


def render_card(section, entry):
    title = escape(entry["title"])
    labels = [escape(label) for label in entry["labels"]]
    prompt = build_prompt(section, entry)
    search = escape(' '.join((entry["title"], entry["english"], entry["description"], entry["fit"])), quote=True)
    return f'''<article class="guide-card" id="g-{section}-{entry["demo"]}" data-search="{search}">
      <div class="guide-card-head"><div><h3>{title}</h3><span>{escape(entry["english"])}</span></div><span class="guide-card-type">LIVE STUDY</span></div>
      <div class="guide-card-stage" data-demo="{entry["demo"]}" data-mode="0">{demo_markup(section, entry)}</div>
      <div class="guide-card-controls" role="group" aria-label="{title}预览状态"><button type="button" data-mode="0" aria-pressed="true">{labels[0]}</button><button type="button" data-mode="1" aria-pressed="false">{labels[1]}</button></div>
      <p class="guide-card-description">{escape(entry["description"])}</p>
      <dl class="guide-card-advice"><div><dt>适合</dt><dd>{escape(entry["fit"])}</dd></div><div><dt>避免</dt><dd>{escape(entry["avoid"])}</dd></div></dl>
      <details class="guide-card-prompt"><summary>可直接交给 Coding Agent 的提示词</summary><div class="guide-prompt-text">{escape(prompt)}</div><button type="button" class="guide-copy">复制提示词</button></details>
      <div class="guide-card-footer"><a href="#g-{section}-{entry["demo"]}" aria-label="定位到{title}"># 直达此条</a><button type="button" class="guide-copy-link" aria-label="复制{title}的链接">复制链接</button></div>
    </article>'''


def render_guide_page(slug, nav_html, site_css_version, guide_css_version, visual_css_version, theme_css_version, js_version):
    guide = GUIDES[slug]
    count = len(all_items(guide))
    groups = '\n'.join(
        f'<section class="guide-section" data-group="{escape(group)}"><div class="guide-section-heading"><div><span>SECTION / {index:02d}</span><h2>{escape(group)}</h2></div><small>{len(entries)} 个条目</small></div><div class="guide-grid">' +
        '\n'.join(render_card(slug, entry) for entry in entries) + '</div></section>'
        for index, (group, entries) in enumerate(guide["groups"], 1)
    )
    visual_css = ('<link rel="stylesheet" href="../assets/visual-styles.css?v=' +
                  visual_css_version + '">') if slug == 'visual' else ''
    visual_note = ('<aside class="guide-visual-note" aria-label="视觉风格说明"><p><strong>怎么理解“风格”？</strong>'
                   '字体、颜色、间距与材质是构成手段。这里保持内容一致，比较它们组合后形成的整体气质；'
                   '切换到“组件细节”可检查风格是否贯穿控件。</p>'
                   '<div class="guide-foundation-list"><b>构成要素</b>'
                   '<span id="g-visual-type">字体层级</span><span id="g-visual-spacing">间距节奏</span>'
                   '<span id="g-visual-color">语义色彩</span><span id="g-visual-radius">圆角语言</span>'
                   '<span id="g-visual-elevation">层级与阴影</span><span id="g-visual-theme">明暗主题</span>'
                   '</div></aside>') if slug == 'visual' else ''
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{escape(guide["name"])}速查：{escape(guide["intro"])}可体验示例并复制可执行提示词。">
<meta name="theme-color" content="#f7f7fd"><title>{escape(guide["name"])}速查 · vibocoding助手</title>
<link rel="icon" href="../assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="../assets/site.css?v={site_css_version}"><link rel="stylesheet" href="../assets/guides.css?v={guide_css_version}">{visual_css}<link rel="stylesheet" href="../assets/theme.css?v={theme_css_version}">
<script defer src="../assets/guides.js?v={js_version}"></script></head><body class="site-guide" data-guide="{slug}">{nav_html}
<main id="guide-main" class="guide-page"><header class="guide-hero"><div><p>{guide["number"]} / {guide["english"]}</p><h1>{escape(guide["name"])}<span>速查</span></h1><div class="guide-hero-lead">{escape(guide["intro"])}</div></div><div class="guide-hero-count"><strong>{count:02d}</strong><span>个可体验条目<br>选择状态 · 复制提示词</span></div></header>
<div class="guide-toolbar"><label for="guide-search">搜索{escape(guide["short"])}条目</label><div><input id="guide-search" type="search" placeholder="输入名称或英文术语…" autocomplete="off"><kbd>/</kbd></div><span id="guide-count" role="status" aria-live="polite">{count} / {count} 个条目</span></div>
<p id="guide-copy-status" class="site-announcement" role="status" aria-live="polite" aria-atomic="true"></p>
{visual_note}<div id="guide-sections">{groups}</div><div id="guide-empty" class="guide-empty" hidden><b>没有匹配的条目</b><p>换个名称试试，或清除搜索词。</p><button type="button" id="guide-clear">清除搜索</button></div>
<p class="guide-footnote">这些是帮助辨认设计做法的本地演示。提示词可直接交给 Coding Agent；Agent 会先检查当前项目，再实施并验证。</p></main><footer class="site-home-footer"><div><strong>vibocoding助手</strong><span>让界面的表达更准确。</span></div><a href="../">回到首页 ↑</a></footer></body></html>'''
