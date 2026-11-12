# 可用性测评修复实施记录

## 第 1 批 · 演示看得清

日期为 2026-11-12，工作目录为 `~/Downloads/vibocoding-audit-fix`，分支为 `audit-fixes`。

### U01 · 页面与视图演示溢出和文字对比度

- 在 `动效速查-src/build_motion_glossary.py` 中精简交叉淡化、方向滑移、幕布揭示，每个视图保留标题和一行说明。
- 在 `动效速查-src/motion_template.html` 中统一为 14px 标题、13px 说明和白字，底色使用演示紫色及深紫色令牌。卡片高 112px，宽度最大 260px。同步检查共享元素和错落入场的源结构，调整共享元素闭合卡片尺寸、容器高度、文字与溢出规则，给位置标签留出空间。
- `动效速查.html` 由构建器重新生成，栏目页与条目页从同一源结构提取演示。
- `tests/test_audit_fix_batch1.py` 检查精简后的节点结构、字号规则、渐变端点与白字对比度。白字对紫色各端点均达到 4.5∶1。
- 已准备 `tests/audit_fix_batch1.cjs`，覆盖 1440、1024、768、390 宽度下五种视图演示的条目页、栏目页卡片及内部文字的水平和垂直溢出。当前沙箱禁止 Chromium 所需的 MachPort 注册，浏览器尚未启动，实际 `scrollHeight ≤ clientHeight` 检查待用户执行。

### U02 · 演示控件边框

- 新增 `site-src/redesign/demo-accessibility.css`，由 `site-src/redesign/demos.py` 追加到 UI、动效、指南、技能参考和令牌五类演示的 Shadow DOM 样式中。
- 输入框、文本域、选择框、按钮、可聚焦交互区域及搜索框、标签输入、步进器、上传区、拖动区等复合控件的边框统一引用 `--demo-border`。开关轨道补充可见边框。复选框、单选按钮及滑动条轨道和滑块使用显式边框，复选框保留勾选和半选的区分。
- 在 Shadow DOM 内补齐 `--demo-border` 的规范值。次要按钮按下时使用更深边框，以满足本批 U03 的状态差异要求。
- Python 回归测试覆盖五类生成样式中的边框令牌、复合输入、原生选择控件和滑动条规则，并验证边框相对舞台达到 3∶1。无界面脚本另有五个栏目的控件计算样式检查，待浏览器环境允许时执行。

### U03 · 按钮按下态

- `site-src/redesign/states.css` 为主要、次要和危险按钮补齐固定按下态。主要按钮使用 `--demo-primary-active`，危险按钮使用 `--demo-danger-active`，次要按钮使用 `--demo-line` 底色和 `--demo-ink` 边框，保留 1px 下移。
- `site-src/redesign/demo-accessibility.css` 同步真实 `:active` 和栏目自动预览的按下规则。次要按钮悬停底色使用 `--demo-soft`。
- `site-src/redesign/states.py` 更新按下态说明，并同步 U02 后输入控件的聚焦说明。
- Python 测试解析生成规则并代入令牌，逐个验证默认、悬停、按下底色两两不同，固定状态和真实状态规则使用相同颜色。浏览器脚本包含真实鼠标按下和状态切换的计算色检查，尚待执行。

### U05 · 演示操作提示

- 在 `site-src/redesign/demo-accessibility.css` 中将 `.stage-label`、`.canvas .ctl`、手势说明、预览说明、滚动提示和指针操作提示等统一为 13px、1.5 行高、`#4B5563`。
- 覆盖在动态背景上的操作提示增加舞台色底，避免背景变化降低文字对比度。调整舞台顶部内边距，给放大后的提示留出空间。
- Python 测试检查共用字号和颜色规则，并验证提示文字相对舞台达到 4.5∶1。五栏目提示字的实际计算样式检查已写入无界面脚本，尚待执行。

### U09 · 装饰性英文大写标签

- `动效速查-src/build_motion_glossary.py` 删除 `stage-live` 和 `stage-signature` 节点，精简视图演示内的大写装饰行。
- `动效速查-src/extra_demos.py` 删除共用场景的英文装饰标题参数及相同用途的附加小字。`motion-demo-gallery.html` 将装饰性英文页眉替换为有信息作用的中文作品数量。
- `site-src/site.css` 删除两类装饰标签的定位和层级规则。
- Python 测试扫描生成站点页面与动效样式，确认两类节点、`LIVE DEMO` 和 `MOTION STUDY` 已移除。历史测评样例继续由现有源文件一致性测试验证。

### U22 · 演示危险色

- `网页UI元素速查.html` 将危险按钮及其他使用旧危险色的状态文字改为 `#B91C1C`，危险按钮悬停改为 `#991B1B`。
- `site-src/redesign/demos.py` 将危险色适配为 `--demo-danger`、`--demo-danger-hover`、`--demo-danger-active`，并在 Shadow DOM 内定义规范值。
- `site-src/redesign/demo-accessibility.css` 与 `states.css` 分别覆盖真实按下、自动预览和固定按下态，同时为上下文菜单危险项和长按删除按钮补充危险色交互规则。
- Python 测试扫描五类演示样式及 UI 脚本，确认旧危险色已清除，并验证危险按钮三态规则。浏览器三态计算色检查尚待执行。

### 验证记录与待验证项

- `python3 scripts/build_site.py` 构建成功，生成 216 个页面、192 个统一条目。
- `python3 -m unittest discover -s tests -p 'test_*.py'` 完整结果见下方最终验证记录。本批增加 8 项回归测试，原有断言全部保留。
- `node --check tests/audit_fix_batch1.cjs` 语法检查通过。
- 无界面验证脚本使用临时 Chromium 配置和本地文件响应，模拟 `/vibocoding-assistant/` 部署子路径，阻止外部请求。安装了 Playwright 的环境可在本工作目录执行 `node tests/audit_fix_batch1.cjs`。当前机器的缓存模块可用 `NODE_PATH=/Users/zhiguang/.npm/_npx/e41f203b7505f1fb/node_modules node tests/audit_fix_batch1.cjs` 调用。
- 当前沙箱回环监听返回 `EPERM`。脚本改用本地文件响应后，无界面 Chromium 在启动时返回 `bootstrap_check_in ... MachPortRendezvousServer ... Permission denied (1100)`。因此浏览器尺寸、计算样式及最终视觉验收仍待用户执行。

#### 最终验证记录

- 构建命令退出码为 0，输出为 216 个页面、192 个统一条目。
- 完整单元测试共 73 项，全部通过。口语搜索既有回归用例为 60/60 命中。
- `git diff --check` 和无界面脚本的 Node 语法检查通过。
- 浏览器验证受上述沙箱启动限制，四档宽度溢出、控件计算边框、提示字计算样式和按钮真实三态颜色仍待验证。

## 第 2 批 · 搜索与使用卡

日期为 2026-11-12，工作目录为 `~/Downloads/vibocoding-audit-fix`，分支为 `audit-fixes`。

### U06 · 搜索结果整行可点

- `site-src/redesign/site.js` 将结果名称改为真实链接，`site-src/redesign/site.css` 使用链接的 `::after` 覆盖整行，包括名称、别名、说明、缩略图及空白处。整行增加指针手势、悬停高亮与链接焦点环。
- 右侧操作置于链接覆盖层上方，复制按钮在搜索浮层的事件委托中执行复制并阻止冒泡。「打开」继续显示，与名称链接指向同一条目，Tab 顺序保留一个打开入口及复制按钮。
- `tests/audit_fix_batch2.cjs` 直接运行站点脚本，验证结果链接、复制载荷、阻止冒泡、复制过程无跳转，以及上下键和 Enter 行为。Python 回归检查伸展链接与覆盖层规则。
- 实际鼠标点击覆盖范围及触屏点击待用户浏览器验收，原因见本批验证记录。

### U07 · 使用卡展开后的高度约束

- `site-src/redesign/site.css` 在桌面断点 `min-width:1024px` 将使用卡改为纵向弹性布局，最大高度使用 `calc(100dvh - var(--nav-height) - 32px)`，对应页头下方及视口底部各 16px 间距。
- 卡片标题、顶部复制主按钮及辅助操作保留各自高度，展开的验收区在卡片内部滚动。验收区标题吸附在内部滚动区顶部。
- `tests/test_audit_fix_batch2.py` 检查桌面断点、高度限制和内部滚动规则。1440×900 下展开后的实际卡片高度、滚动至末条时复制按钮可见性仍待用户浏览器验收。

### U08 · Esc 一次关闭

- `site-src/redesign/site.js` 在搜索浮层的 keydown 中优先处理 Escape，并阻止搜索输入框的默认清空行为，随即关闭浮层，沿用 close 事件中的焦点归还逻辑。
- `tests/audit_fix_batch2.cjs` 覆盖索引加载中及已有非空查询时的一次 Escape 关闭、默认行为取消、焦点回到原触发元素，以及请求稍后完成时保持关闭状态。
- 代码与自动行为测试已完成，原生浏览器按键表现待用户验收。

### U13 · 触屏及窄屏键盘提示

- `site-src/redesign/site.css` 在 `max-width:1023px`、`hover:none` 或 `pointer:coarse` 任一条件成立时隐藏搜索底部键盘提示。
- `tests/test_audit_fix_batch2.py` 检查三个条件采用并集，触屏桌面宽度同样适用。
- 实际媒体特征下的显示效果待用户浏览器验收。

### U23 · 轻量静态缩略

- 栏目格的实现来自 `templates.py` 的 `gallery_card` 和 `demo_scope`，使用实际演示节点及 Shadow DOM 运行时。
- 本批采用 56×56px 的静态类型示意图。索引仅附带栏目类型，`site-src/redesign/site.js` 输出三个静态节点，`site-src/redesign/site.css` 分别呈现布局网格、组件控件、位移层、页面结构及提示词文本行。配色使用共用灰阶令牌。
- 未提供或无法识别缩略类型时，统一显示栏目首字占位。手机结果采用 56px 缩略列与 `minmax(0,1fr)` 文字列，操作排在文字列下方。
- `tests/test_audit_fix_batch2.py` 检查尺寸、类型覆盖及轻量元数据，`tests/audit_fix_batch2.cjs` 验证缺少缩略元数据时的栏目首字占位，以及结果中没有演示节点、图片请求或脚本。
- 实际手机横向溢出及视觉辨识效果待用户浏览器验收。

### U21 · 口语别名及相近名称阈值

- `site-src/content/interactions.json` 为多层视差追加「滚动时背景动得慢」「滚动视差」，原有「背景滚得慢」继续参与匹配。为卡片聚光跟随追加「鼠标光晕」「光晕跟随鼠标」。
- `tests/fixtures/search_queries.json` 增加用户指定的两句查询，二者均排第 1。`tests/search_queries.cjs` 和 `tests/test_search_queries.py` 更新为 62 条查询，并将通过要求提升为全部命中前三。
- `site-src/redesign/search.js` 的相近名称改用规范化编辑距离。查询至少 3 字符，候选最多允许 1 次编辑，并须达到 `1 - 编辑距离 / 较长文本长度 ≥ 2/3`。名称、独立英文名及别名分别计算，取最高分。
- `site-src/redesign/site.js` 仅在存在达标候选时显示「相近的名称」。`asdfgh`、`qwerty`、`zzzz` 等查询没有匹配或补充候选，保留没找到提示、换说法建议和栏目入口。
- 新增回归覆盖乱码、空查询及「交叉淡华」「搜索匡」「buton」等合理错字。既有 60 条查询全部命中，原有 50 条排名基线断言继续执行。新增冻结摘要检查验收要求与别名，仅扣除本批四个获准新增别名后与批前数据比较。
- 本项实现及自动验证已完成。

### U15 · 独立搜索索引与按需缓存

- `site-src/redesign/templates.py` 从共用条目数据生成 `dist/assets/search-index.json`，加入构建文件清单。所有使用共用外框的页面通过 `data-index-url` 引用带 SHA-256 内容摘要的版本 URL，通过 `data-site-root` 提供相对根路径。
- 页面 HTML 中移除内嵌完整索引。首页示例搜法、推荐卡片及条目数继续在构建时生成，搜索浮层从共享 JSON 读取示例词及完整复制载荷。
- `site-src/redesign/site.js` 在点击搜索、点击示例、`/` 或 `⌘K/Ctrl+K` 打开搜索时加载索引。首次显示「正在加载…」，HTTP、网络及索引结构失败显示重试按钮，并允许恢复。并发打开复用同一请求，成功后在当前页面内存复用数据。
- 索引沿用浏览器默认 HTTP 缓存策略，所有页面共享同一个带版本号的资源 URL。本批选择首次打开时加载，首屏无需索引请求。不同层级页面在内存中将根相对条目路径转换为各自的相对链接。
- `tests/test_site_build.py`、`tests/test_redesign_javascript.py`、`tests/test_search_queries.py` 和 `tests/search_queries.cjs` 改为读取独立索引，保留原有条目数量、目标存在、别名、提示词及全部验收句载荷的断言。
- `tests/test_audit_fix_batch2.py` 遍历共用外框页面，逐页检查索引版本、索引路径及所有搜索条目和栏目链接。按钮页 HTML 为 27,486 字节，小于 100KB，JSON 为 331,164 字节且可解析。
- `tests/audit_fix_batch2.cjs` 覆盖延迟响应、加载前输入、并发打开、加载失败重试、内存缓存、首页示例点击、不同页面深度的相对路径及关闭后响应返回的情况。
- 本项实现及自动验证已完成，真实浏览器网络缓存表现待用户验收。

### 本批验证记录与待验证项

- `python3 scripts/build_site.py` 构建成功，生成 216 个页面、192 个统一条目。
- `python3 -m unittest discover -s tests -p 'test_*.py'` 共 79 项通过，包含本批新增 6 项回归测试。搜索查询为 62/62 命中前三，两条新增查询均排第 1。
- `node tests/audit_fix_batch2.cjs` 的站点脚本行为测试通过，`node tests/search_queries.cjs` 的独立索引搜索测试通过，`git diff --check` 通过。
- 通过已缓存的 Playwright 模块尝试启动临时无界面 Chromium，启动阶段返回 `MachPortRendezvousServer ... Permission denied (1100)`。本批没有获得浏览器渲染结果，整行点击范围、实际键盘与触屏行为、使用卡尺寸、滚动可见性及手机溢出仍待用户完成最终浏览器验证。

## 第 3 批 · 状态补全与减弱动态

日期为 2026-11-12，工作目录为 `~/Downloads/vibocoding-audit-fix`，分支为 `audit-fixes`。

### U04 · 十个组件的有效状态

- `site-src/redesign/states.py` 为按钮补充禁用和加载中，为输入框、文本域、下拉框、搜索框补充禁用和出错，为复选框、单选按钮、开关、滑动条补充禁用。标签页采用可选方案，新增「帮助」项，并在禁用演示中只禁用该项。
- `site-src/redesign/site.js` 在演示内设置真实的 `disabled` 属性。加载中的按钮先记录原宽度，再显示图标和「提交中…」，附带 `aria-busy`。错误态保留输入内容，设置 `aria-invalid`，通过 `aria-describedby` 关联字段下方的具体修正说明。切回自由试时重建原始交互，清除临时状态，并保留字段值及勾选值。
- `site-src/redesign/states.css` 使用现有演示令牌实现灰底禁用、禁止手势、红色错误边框和 13px 错误文字。禁用态没有整组透明度衰减。加载图标在减弱动态下静止，文字继续显示。
- `网页UI元素速查.html` 的标签演示增加「帮助」及对应内容，键盘导航过滤原生禁用项，激活函数也检查禁用属性。各条目的验收要求与别名保持原文。
- `tests/audit_fix_batch3.cjs` 执行实际状态切换回调，覆盖十个组件的禁用与恢复、标签页局部禁用、错误文本关联和输入保留、加载文字与宽度锁定。`tests/test_audit_fix_batch3.py` 检查生成页面的状态覆盖、中文说明、样式和内容冻结，按 WCAG 相对亮度公式检查错误文字和加载文字至少 4.5∶1、禁用文字至少 3∶1。
- 实现和自动检查已完成。实际控件尺寸、禁用手势、键盘跳过、390px 下的错误提示布局及视觉辨识仍待用户浏览器验收，沙箱限制见本批验证记录。

### U11 · 减弱动态下主动播放一次

- `site-src/redesign/demos.py` 为原演示的全部减弱动态 CSS 覆盖和共用安全规则增加根节点条件。`data-demo-motion-once` 允许本次主动播放恢复原时长和效果，CSS 循环限制为一次迭代。源规则中的静态 transform、opacity 和 animation 覆盖也采用同一条件。
- `site-src/redesign/demo-runtime.js` 在主动播放期间临时放行源脚本的减弱动态判断，支持重播、0.25 倍慢放和栏目缩略播放。默认减弱动态路径不启动源脚本的循环计时器和动画帧。按动画时序计算播放窗口，并计入慢放倍率，样式稍后加载时重新计算。结束后移除放行标记、取消计时器和动画帧、清理源监听及动画资源，页面隐藏或偏好切换时也执行清理。
- `site-src/redesign/site.js` 保留减弱动态下的栏目「▶ 播放」，屏蔽悬停和聚焦自动播放。缩略播放结束由运行时通知栏目恢复首帧，长周期效果可以完成本轮。`site-src/redesign/site.css` 配合显示播放入口。
- 对 CSS 循环、粒子、轮播和文字轮换增加静态「下一步」。CSS 循环按四等分相位暂停显示，粒子逐步更新静态位置，轮播与文字轮换逐项显示源内容。跨文档转场通过「下一步」切换真实演示前后页面，单次播放结束后保留目标页面，手动切换仍可使用。跨文档演示继续禁用无法准确执行的慢放，保留手动比较入口。
- `site-src/redesign/templates.py` 在共用演示控件和栏目页显示「已开启减弱动态：点播放看一次」，并为有交互的 UI、动效、指南和令牌演示统一提供播放控制。静态技能说明保持原有展示方式。
- `tests/audit_fix_batch3.cjs` 执行实际运行时，覆盖默认无循环、主动放行、源 JS 判断、8 秒动画完整窗口、0.25 倍慢放、重播和 reset 清理、栏目播放、页面隐藏、静态相位暂停和正常动态路径。Python 回归遍历五类生成 CSS 的全部减弱动态块，检查每个覆盖均具备放行条件，并检查循环演示的分步元数据。
- 实现和自动检查已完成。浏览器计算时长、实际分步画面及完整播放观感仍待用户验收，原因见下方记录。

### U07 补充 · 页面底部的复制入口

- 用户报告的复现源于 sticky 卡片受父网格底部约束，卡片高度限制无法消除该边界。
- `site-src/redesign/site.css` 在桌面断点采用视口固定的使用卡，位置和宽度按现有 1184px 外框、64px 水平内边距及 32px 网格间距计算，与右侧列对齐。顶部保持页头下方 16px，最大高度沿用 `calc(100dvh - var(--nav-height) - 32px)`，验收区继续独立滚动。该定位覆盖短页面和滚动到底部的情况。
- Python 回归保留第 2 批全部高度及内部滚动断言，新增固定定位与顶部约束断言。`tests/audit_fix_batch3_headless.cjs` 准备了 1440×900 的 `component-lift` 与五个最小生成条目页的检查，在展开验收、内部滚到底、页面顶部、中部和底部分别验证按钮坐标及 `elementFromPoint` 命中。
- 实现和结构检查已完成。实际页底命中测试因浏览器启动受限尚未执行完成，需用户最终浏览器验证。

### 本批验证记录与待验证项

- `python3 scripts/build_site.py` 构建成功，生成 216 个页面、192 个统一条目。
- `python3 -m unittest discover -s tests -p 'test_*.py'` 共 88 项通过，包含本批新增的 9 项回归。既有测试断言全部保留，搜索查询为 62/62 命中前三。
- `node tests/audit_fix_batch3.cjs` 状态与运行时行为测试通过。新增无界面脚本的 Node 语法检查及 `git diff --check` 通过。
- 无界面脚本使用临时 Chromium 配置、本地文件响应及 `/vibocoding-assistant/` 部署子路径。覆盖真实状态切换、加载宽度、错误文字、标签键盘跳过、减弱动态主动播放时长、静态相位和复制入口命中。
- 执行 `NODE_PATH=/Users/zhiguang/.npm/_npx/e41f203b7505f1fb/node_modules node tests/audit_fix_batch3_headless.cjs` 时，Chromium 在启动阶段返回 `MachPortRendezvousServer ... Permission denied (1100)`，没有进入页面验证。本批全部浏览器渲染、计算样式和命中结果均待用户验收。
