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
