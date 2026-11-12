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

## 第 4 批 · 手机、平板及短中文错字

日期为 2026-11-12，工作目录为 `~/Downloads/vibocoding-audit-fix`，分支为 `audit-fixes`。

### U20 · 平板页头及触屏快捷键提示

- `site-src/redesign/site.css` 删除 761–1000px 的双行导航规则，统一在小于 1024px 时显示手机搜索按钮和「目录」，隐藏桌面导航与大下拉。该断点的导航内层为 63px，加 1px 底边框后为 64px；≥1024px 保留桌面导航规则。
- `site-src/redesign/site.js` 将页头模式及抽屉清理的媒体查询同步为 `max-width:1023px`，沿用右侧抽屉、关闭及焦点归还逻辑。
- `site-src/redesign/templates.py` 将导航、首页搜索及五个栏目搜索入口的快捷键拆为 `.shortcut-hint` 节点。共用 CSS 在窄屏、`hover:none` 或 `pointer:coarse` 任一条件成立时隐藏这些节点及搜索底部键盘提示，鼠标桌面仍显示。
- `site-src/redesign/demos.py` 另将命令面板演示的快捷键文字拆为独立节点，`demo-accessibility.css` 在触屏下隐藏该节点、演示内的 `kbd` 和命令面板底部键盘提示。没有修改条目正文、验收要求或别名。
- Python 回归检查断点、旧双行规则移除、所有搜索入口的提示节点及运行时一致性。实际 768px 页头高度、抽屉开关和触屏显示效果待浏览器验证。

### U12 · 手机及触屏点击区

- `site-src/redesign/site.css` 在小于 1024px 或触屏条件下，为所有可见链接、按钮及 summary 提供 44px 最小高度；行内链接保留段落排版。面包屑、抽屉「首页 →」、分组、相关条目、播放、状态切换和页头操作沿用共用规则，顶部搜索另有显式高度覆盖，以覆盖宽屏触屏时原来的 40px。
- 链接使用实际布局高度，按钮补充 44px 最小宽度，没有使用负外边距或扩大伪元素制造点击区。原有分组及状态按钮的 gap 保留，抽屉首页与下方分组另留 8px 间隔。
- `site-src/redesign/demo-accessibility.css` 同步为交互演示内的链接、按钮和 summary 提供真实最小尺寸；非交互缩略内容保持 inert。轮播的箭头、暂停和圆点改为分行网格，避免按钮放大后互相重叠；移除触屏下轮播暂停、面包屑和搜索按钮原有的外扩伪元素。
- Python 回归检查共用尺寸规则、五类演示样式覆盖及轮播分行结构。实际点击区高度、相邻重叠及点击命中待浏览器验证。

### U10 · 演示字号及缩略格放大

- `site-src/redesign/demos.py` 在共用演示样式适配层将 `font-size` 和 `font` 简写内不足 12px 的 px 值提升至 12px，包括小数值；只对演示模板的 style 属性做同样处理，不替换说明文字。五类演示及跨文档转场的两个演示页面统一使用此处理，间距及图形尺寸不受字号替换影响。
- `site-src/redesign/states.css` 将浮动标签的固定聚焦态从 11px 提升为 12px。`demo-accessibility.css` 为浏览器默认的 small/sub/sup 提供 12px 字号，允许小卡片及按钮组换行，并保持表格的内部滚动。
- 交叉淡化两层改用同一网格单元，卡片高度由较长内容决定；方向滑移轨道保留双面板宽度，面板与幕布卡片允许随文字增高。小尺寸 micro-card 允许增高并增加内边距。
- 缩略演示在 Shadow DOM 内以 `zoom:1.35` 放大，真实参与尺寸计算，播放按钮及条目链接不随之缩放。外层缩略舞台使用卡片容器宽度的 75% 作为高度下限，且至少 240px，内容较多时允许继续增高；为独立播放按钮预留 60px 底部空间。原有两列/三列布局保留。
- `site-src/redesign/site.css` 删除无法穿透 Shadow DOM 的旧缩略内部选择器，实际缩略规则统一放入 `demo-accessibility.css`。
- **残留统计：**扫描八份生成演示/状态 CSS 及全站 464 个演示模板，显式小于 12px 的字号声明为 **0**。没有保留小字号例外。此统计不是浏览器可读文字段数；浏览器实际仍小于 12px 的文字数量目前未知，不能将源码统计当作实际渲染为零。历史测评样本属于冻结证据，保持原样，不纳入统一条目演示的字号修改。
- Python 回归逐份扫描样式和所有生成演示模板，并检查放大、自动增高及卡片换行规则。实际缩略效果、文字裁切、横向溢出和 U01 三例仍待浏览器验证。

### U21 补充 · 两字中文名称的容错

- `site-src/redesign/search.js` 将查询最小长度由 3 改为 2。中文候选要求共享至少一个汉字、编辑距离至多 1；两字查询的相似度下限为 0.5，其余仍为 2/3。候选按相似度降序及原始条目顺序排序。
- 非中文查询要求与候选连续共有至少 4 个字符，或连续共有片段占查询长度至少 0.6，同时保留一次编辑及 2/3 相似度要求。「buton」的既有英文容错保持通过。长度差检查放在片段计算之前，避免对长的无关查询进行无效比较。
- `tests/test_audit_fix_batch4.py` 验证「按扭 → 按钮」「输人框 → 输入框」「滑东条 → 滑动条」「轮拨图 → 轮播图」均为相近名称第一项；`asdfgh`、`qwerty`、`zzzz`、`jkl;`、`xyzxyz` 在正常结果和相近名称中均为空。既有第 2 批错字及全部 62 条口语查询继续执行。
- 本项自动行为验证完成；本批没有新增或改写任何别名和验收要求。

### 本批验证记录与待验证项

- `python3 scripts/build_site.py` 构建成功，生成 216 个页面、192 个统一条目。`python3 -m unittest discover -s tests -p 'test_*.py'` 共 94 项通过，包含本批新增 6 项回归；62/62 条口语查询命中前三，原有测试断言保留。
- `git diff --check` 及 `node --check tests/audit_fix_batch4_headless.cjs` 通过。
- 新增可选无界面验证脚本 `tests/audit_fix_batch4_headless.cjs`：只用临时 Chromium 配置、本地文件响应和 `/vibocoding-assistant/` 子路径，阻止外部请求。覆盖 390、768、1023、1024、1440px 及宽屏触屏；扫描五栏目、192 条目及状态切换的实际文字字号、点击高度、同级按钮重叠、U01/小卡片文字边界、页面横向溢出，并检查抽屉焦点和播放按钮命中。正常执行后报告写入 `output/playwright/audit-fix-batch4.json`。
- 无界面 Chromium 启动探测返回 `bootstrap_check_in ... MachPortRendezvousServer ... Permission denied (1100)`，尚未进入页面。上述浏览器脚本目前仅完成语法检查；实际渲染统计、页头高度、文字裁切及点击命中均未完成验证，留给用户最终浏览器验收。可在允许启动无界面 Chromium 的环境中运行 `NODE_PATH=/Users/zhiguang/.npm/_npx/e41f203b7505f1fb/node_modules node tests/audit_fix_batch4_headless.cjs`。
- 本批只改当前工作区中的共用源文件、测试和本记录，未手改 dist，未执行暂存、提交、推送或发布。

## 第 5 批 · 细节与规范

日期为 2026-11-12，工作目录为 `~/Downloads/vibocoding-audit-fix`，分支为 `audit-fixes`。

### U14 · 中文 404 与深层网址恢复

- `site-src/redesign/templates.py` 新增 `not_found_page()`，加入生成页面和构建允许清单，生成 `dist/404.html`。页面包含中文说明「这个页面不存在，可能是网址输错了或条目改名了」、全站搜索按钮及回首页按钮，复用站点页头、页脚、目录与搜索浮层。
- 本项选择绝对子路径方案。仅在生成 `404.html` 时，路径生成函数输出 `/vibocoding-assistant/...`，涵盖导航、资源、搜索 JSON 与搜索结果根路径。页内跳转继续使用 `#main`。任意深度错误网址均使用同一部署前缀，其余页面继续使用相对路径。
- `tests/test_audit_fix_batch5.py` 验证中文、外框、两个恢复入口，并分别以三种深度错误网址解析全部资源、栏目、搜索索引和 192 个搜索条目地址，检查目标存在。`tests/audit_fix_batch2.cjs` 读取真实 404 页的搜索配置，验证加载共享 JSON、渲染按钮搜索结果及 Enter 跳转。`tests/test_site_build.py`、`tests/test_audit_fix_batch2.py` 为唯一的 404 绝对子路径例外增加精确断言，保留其他页面的相对路径与目标存在检查。
- 实现和自动化路径、脚本行为验证已完成。GitHub Pages 错误响应及真实浏览器搜索入口待用户最终验收。

### U16 · 首页标题末行

- `site-src/redesign/templates.py` 将标题末尾「提示词。」整体包进 `span.nowrap`。`site-src/redesign/base.css` 使用 `white-space: nowrap`，让词语和句号一起换行。
- `tests/test_audit_fix_batch5.py` 断言生成结构与不断行规则。`tests/audit_fix_batch5_headless.cjs` 为 1440、1024、768、390px 准备逐字测量行位置的检查，要求末行除空白和标点后超过两个字符。
- 实现和结构验证已完成。四个宽度的实际换行待用户最终验收，无界面浏览器启动受沙箱阻止。

### U17 · 页脚分隔线对齐

- `site-src/redesign/templates.py` 共用外框统一改为 `footer.wrap > div.footer`，外层负责页面左右留白，内层承载原有分隔线与页脚内容。首页、栏目、条目、规范、提示词写法、测评和 404 页统一生成。
- `tests/test_audit_fix_batch5.py` 遍历所有带共用搜索浮层的页面，检查内层容器结构。无界面脚本准备按主内容左右内边距检查页脚分隔线坐标。
- 实现和全站结构验证已完成。实际像素对齐待用户最终验收。

### U18 · 提示词写法页间距与主按钮

- `site-src/redesign/site.css` 为 `.entry-section p + h3` 设置 `margin-top: var(--space-6)`，对应 24px，覆盖「动效描述的四层结构」和「完整例子 · 按钮」中的两处链接段落与后续小标题。
- `site-src/redesign/templates.py` 中「复制提示词」按钮调用共用 `copy_button(..., primary=True)`，使用墨黑主按钮样式。
- `tests/test_audit_fix_batch5.py` 检查令牌间距与实际生成按钮类。原有提示词写法测试继续逐字核对两版按钮提示词及验收要求。无界面脚本准备检查两处实际间距均为 24px、按钮背景为 `#111827`。
- 实现和静态验证已完成。实际渲染间距与按钮外观待用户最终验收。

### U19 · 相关条目链接块

- `site-src/redesign/templates.py` 将条目底部相关链接及「用在哪些组件上」互链统一生成 `a.link-block`，末尾添加向右箭头，箭头设为 `aria-hidden="true"`。
- `site-src/redesign/base.css` 定义白底、`1px solid var(--control)`（`#868E9C`）、墨黑字，悬停边框为 `var(--ink)`（`#111827`）并使用灰白舞台底色。链接沿用全站 2px 蓝色焦点环。所有尺寸下链接块最小高度 44px，长名称允许换行。`site-src/redesign/site.css` 在手机宽度下将这两组链接排成单列。
- `tests/test_audit_fix_batch5.py` 遍历 192 个条目及组件反向互链，逐个检查链接块、箭头与辅助技术属性。`tests/test_redesign_tokens.py` 断言边框、底色、文字、悬停、44px 高度及焦点规则。原有组件动效映射测试继续验证双向目标完整。
- 实现和全量结构、CSS 验证已完成。手机实际点击区、悬停与聚焦外观待用户最终验收。

### U22 · 对齐 PRD §15.4 字号表

- `site-src/redesign/site.css` 将条目区块、使用卡、验收要求和新做一个标题，以及栏目分组标题统一为 `--text-section`（22px）、行高 1.3、字重 600。
- `site-src/redesign/base.css`、`site-src/redesign/site.css` 将 chip、栏目与分组条数、首页条数、搜索结果条数和测评徽标统一为 `--text-label`（13px）、行高 1.5、字重 500。共用导航中的栏目条数改用 `.count`。
- 栏目卡片、组件关联动效卡片和首页目录卡片名称统一字重 600、行高 1.5、桌面 16px、手机 14px，移除关联动效卡片名称在桌面下的 14px 覆盖。
- `tests/test_redesign_tokens.py` 增加上述精确 CSS 值断言。`tests/test_audit_fix_batch5.py` 扫描生成 CSS、JS 和全部演示模板，确认无旧危险色 `#DC2626`。原有对比度测试继续断言 `--demo-danger: #B91C1C`。内容数据与条目验收要求、别名保持现有版本。
- 实现和静态规范验证已完成。区块标题层级、390px 等宽度的实际溢出和截断待用户最终验收。

### 本批验证结果与待验收项

- `python3 scripts/build_site.py` 通过，生成 217 个页面、192 个统一条目，包含新增 404 页。
- `python3 -m unittest discover -s tests -p 'test_*.py'` 共 101 项通过，本批新增 7 项 Python 回归测试。口语搜索仍为 62/62 命中前三。
- `node tests/audit_fix_batch2.cjs` 通过，包含新增 404 页真实配置的搜索加载、结果链接与 Enter 跳转检查。`node --check tests/audit_fix_batch5_headless.cjs`、`git diff --check` 通过。
- 新增 `tests/audit_fix_batch5_headless.cjs`，仅使用临时无界面 Chromium 配置和本地文件响应，检查 1440、1024、768、390px 的首页、五栏目、提示词写法、192 条目和三种深度错误网址，涵盖标题末行、页脚坐标、间距、计算字号与字重、链接高度、横向溢出及搜索跳转。脚本完成语法检查，实际渲染检查尚未运行成功。
- 无界面 Chromium 启动探测返回 `bootstrap_check_in ... MachPortRendezvousServer ... Permission denied (1100)`。本批未获得浏览器渲染证据，以上视觉与真实浏览器交互项留给用户最终验收。在可启动无界面 Chromium 的环境中，可执行 `NODE_PATH=/Users/zhiguang/.npm/_npx/e3e9a1d1813bae49/node_modules node tests/audit_fix_batch5_headless.cjs`，运行报告写入 `output/playwright/audit-fix-batch5.json`。
