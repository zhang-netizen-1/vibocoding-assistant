# 演示重做 A 段实施记录

日期：2026-11-13。工作区：`~/Downloads/vibocoding-demo-redesign`，分支：`demo-redesign`。

公共规格接入和四套样板代码已完成，构建与相关自动测试通过。**1440 / 390 截图、视觉评分和全部演示的浏览器几何验收未完成，不能据此宣称已达到最终视觉验收标准。** 本轮沙箱同时阻止本地监听与 Headless Chromium 启动，具体证据及复核命令见末节。

## 变更文件

| 文件 | 职责 |
|---|---|
| `site-src/redesign/demo-spec.css` | 全部 `--ds-*` 令牌、兼容别名及五种公共外壳类 |
| `site-src/redesign/demos.py` | 来源样式与无障碍样式拆分；按 kind/slug 选择皮肤与 HTML；图片路径替换；保留来源锚点；发布皮肤；smoke fixture 使用最终皮肤；复制反馈适配；减少动态门控修复 |
| `site-src/redesign/templates.py` | 正文、栏目和动效映射卡片传递 slug；新增 `data-demo-slug`；支持嵌套皮肤目录发布 |
| `site-src/redesign/demo-runtime.js` | 顺序加载并保留多层样式；每份 CSS 和图片加载后重测；按实际宽度布置栏目预览；lift 触屏切换 |
| `site-src/redesign/demo-accessibility.css` | 与统一舞台兼容；提示胶囊和留白；触屏输入高度；去除旧画布尺寸干扰 |
| `site-src/redesign/states.css`、`states.py`、`site.js` | 固定成功态、0.98 按下、0.45 禁用、14px 加载图标；布局宽度锁定；栏目重播间隔 1.2 秒 |
| `site-src/redesign/site.css` | 外层舞台取消重复底色/裁切；栏目操作区适配；搜索 fallback 改为 64×48 |
| `scripts/build_site.py` | 图片 manifest 白名单复制和严格输出清单 |
| `site-src/redesign/demo-skins/ui-button.css/html` | 按钮样板 |
| `site-src/redesign/demo-skins/ui-input.css/html` | 输入框样板 |
| `site-src/redesign/demo-skins/motion-component-lift.css/html` | 卡片上浮样板 |
| `site-src/redesign/demo-skins/motion-view-crossfade.css/html` | 交叉淡化样板 |
| `tests/test_redesign_tokens.py` | 演示令牌、对比度、阴影与舞台断点校验 |
| `tests/test_site_build.py` | 新样式链及 srcset 路径校验；194 份演示外壳；四套契约；全部图片字节和尺寸；减少动态门控回归 |
| `tests/audit_fix_batch3.cjs` | DOM 模型同步多层样式生命周期；加载宽度使用布局尺寸，并以 0.98 变换模拟回归场景 |
| `tests/demo_redesign_headless.cjs` | 双尺寸截图、状态、图片、样式顺序、栏目与 secondary 的浏览器复核入口 |

`dist/`、`build/`、`output/` 为现有忽略的生成目录。图片库沿用已有 `site-src/demo-assets/`，没有改动原图。未执行 `git add`、commit、push，没有访问两个禁止仓库，没有使用用户 Chrome、open 或 AppleScript，没有占用 4180 / 4181。

## 公共层机制

每个 ShadowRoot 依次挂载：

1. `demo-<kind>.css`：来源样式和原行为兼容规则。
2. `demo-spec.css`：公共令牌与舞台。
3. 可选 `demo-skins/<kind>-<slug>.css`。
4. `demo-accessibility.css`。
5. 适用正文的 `states.css`。
6. 演示 DOM。

重播、复原、状态切换保留已加载的样式节点，避免重建 DOM 时短暂丢失皮肤。独立 `.ds-overlays` 仅裁切浮层动画边界，防止关闭的抽屉移出舞台后撑宽页面；主体内容继续自然增高。五类适配器均使用 `.demo-root.ds-stage`；192 个条目加两处 secondary 共 194 份演示都通过外壳与原锚点测试。元数据、提示词、验收要求和内容 JSON 没有修改；五份内容 JSON 的 SHA-256 与落地计划中的基线相同。

舞台使用 `#F7F7F8`、24px 淡点阵、12px 圆角和 1px 装饰边，不加舞台阴影。正文按 viewport 使用 16:10 / 3:2 / 4:3，最小高度为 320 / 300 / 260px，内边距为 32 / 24 / 16px。舞台允许内容增高，不用固定高度或外层 hidden 裁掉内容。提示在样板的唯一外舞台左下锚定，内部为提示预留空间。

栏目预览复用同一份皮肤和 DOM，采用 4:3 的首选比例，按实际可用宽度排版；不再用 312px 画布无条件缩小文字。四样板的 inert 预览收起辅助说明或次要操作，DOM 和行为钩子保留。长内容可增高。搜索当前使用 4:3 栏目图形 fallback；本轮没有生成静态搜索截图。

全部颜色、字体六档、行高/字重、间距、圆角、双层阴影、五档时长、四条曲线、语义浅底、图表颜色均有 `--ds-*` 定义；旧 `--demo-*` 桥接到对应新令牌。样板使用系统中文字体，单个样板选择三档字号。

HTML 皮肤中的 `{{demo-assets}}` 由页面的资源前缀推导，替换到 `src` 和每个 `srcset` 候选，不使用站点根绝对路径。图片清单的 17 张图、34 份 WebP 和 manifest 复制至 `dist/demo-assets/`，纳入严格输出白名单；测试验证复制字节一致、实际宽度及相应高度。0 至 3 层页面前缀均有路径测试。

## 四个样板

| 样板 | 变化与保留 |
|---|---|
| button | 白色操作承托面、真实中文操作、两列按钮、紫色主操作与语义危险色；保留四个 `.btn` 的顺序、用途 class、`data-cmd/data-arg` 和 `#copyDemoBtn`。按下颜色继续变深并缩放至 0.98。固定成功态可观察；自由操作中的复制反馈显示绿色并在 1600ms 后恢复。加载使用布局宽度，避免从按下态进入加载态时缩短 2%。 |
| input | 白色表单承托面、常驻姓名标签与邮箱浮动标签、正确边框和提示层级。保留两个 `input.i` 的 aria-label、空格 placeholder 和 `input + .fflabel` 关系。浮动标签通过 transform 变化；保留输入值、固定出错/禁用/聚焦，并补固定悬停、按下和成功。没有新增失焦校验行为。 |
| component-lift | `studio-bright-01` 真实工作室图、短标题、双层静止/悬停阴影、160ms 过渡；保留 `.stage[data-effect="component-lift"]` 和 button `.micro-card.lift-card`。支持原 hover、预览属性和触屏点按复原，`aria-pressed` 同步。减少动态去除位移。 |
| view-crossfade | `garden-dusk-01/02` 两幅真实庭院图、中文标题与说明、底部遮罩；两层始终共存于同一 grid cell，保留 `.view-a/.view-b`、`.scene-description`、`[data-action="next"]` 及来源的 380ms 交叉淡化与 aria-hidden 切换。容器清除额外承托面 padding，避免图片周边出现重复白框。 |

## 迭代及规格核对

进行了初版后的静态复核和修订，修复：重复 `:host` 导致减少动态规则不匹配；错误拆开 `:is()` 内逗号；自由操作中的复制成功样式遗漏；按下到加载的宽度跳变；图片容器额外 padding；提示定位；窄栏目预览内容密度。减少动态门控回归测试先复现失败，修复后通过。

以下为静态实施评分，**不属于看图后的视觉评分**：2＝有针对性的自动证据，1＝代码已实现但仍依赖浏览器验收，0＝未完成。视觉精致度暂不评分。

| 规格 | 分数 | 证据与限制 |
|---|---:|---|
| §0 原则 | 1 | 四样板使用真实中文和照片；精致度待看图 |
| §1 舞台 | 1 | 194 外壳与断点 CSS 通过；全部实际几何待验 |
| §2 颜色 | 2 | 令牌值及指定前景/背景对比度通过 |
| §3 字号 | 1 | 样板三档字号、最小 12px；最终渲染待验 |
| §4 圆角/阴影/间距 | 1 | 令牌和双层阴影通过；视觉层次待验 |
| §5 动效 | 1 | 四样板时序与栏目 1.2s 轮间停顿已实现；旧来源内部无限 CSS 循环仍沿用原时序 |
| §6 图片 | 2 | 本地图、srcset、dominant、尺寸和全部深度资源路径通过；浏览器解码待验 |
| §7 状态 | 1 | 状态回调与生命周期模型通过；真实触屏命中和显示待验 |
| §8 减少动态 | 1 | 门控回归与生命周期模型通过；实际媒体查询呈现待验 |
| §9 提示 | 1 | 中文胶囊、图标、左下预留；最终换行/位置待验 |
| §10 手机 | 1 | 4:3、自适应和至少 44px 控件规则已实现；390px 几何待验 |
| §11 接入 | 2 | 五类样式链、皮肤、锚点、资源输出和 194 初始化通过 |

## 测试结果

最终针对性验证结果：

| 验证 | 结果 |
|---|---|
| `PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/build_site.py` | 通过：217 页、192 条目 |
| `test_demo_audit` | 1 项通过 |
| `test_redesign_tokens` | 5 项通过 |
| `test_site_build` | 21 项通过 |
| `node tests/token_demos.cjs` | 五类 token 的交互、计算、主题与存储回退通过 |
| 补充 `test_redesign_javascript` | 12 项通过，包含 194 份最终演示初始化、命令面板和动效对话框检查 |
| 补充 `node tests/audit_fix_batch3.cjs` | 10 组状态回调及减少动态生命周期通过 |
| Node 语法、PostCSS 解析、`git diff --check` | 通过 |
| Headless 1440 / 390 | 环境阻止启动；0 张截图，未验收 |

未运行完整 `test_*.py` 套件、需要 Git 的冻结测试及其他历史批次视觉断言；没有删除测试或放松条目数量、行为、原锚点、对比度和路径边界约束。两项新增公共令牌测试与六项构建/契约测试随目标套件一起执行。

## 未完成事项与浏览器阻塞

1. 未生成 1440 / 390 截图；未执行看图后的逐项评分及视觉迭代。四样板与全部条目的实际不溢出、不截断不能仅凭静态检查宣称已验收。
2. 本轮请求监听 `127.0.0.1:4182` 返回 `listen EPERM: operation not permitted`。直接改用 `file://` 后，Headless Chromium 启动也返回 `MachPortRendezvousServer: Permission denied (1100)`。没有尝试绕过限制。证据在 `output/demo-redesign/headless-report.json` 与 `browser-blocker.txt`。
3. 用户指定截图目录位于本轮可写根之外。脚本默认输出到工作区 `output/demo-redesign/A/`，支持通过 `SHOTS_DIR` 指定原定目录，由具备权限的执行者运行。
4. 其他 188 个条目本轮只接公共层，其内部旧样式、内容密度和无限循环的内部停顿没有逐项重做。全栏目实际几何需在浏览器可启动后完成；搜索静态截图仍使用 fallback。

可用环境中的复核命令（脚本仅启动 headless，不使用用户浏览器；自动选 4182，冲突时选择空闲端口）：

```sh
NODE_PATH="$HOME/Downloads/Kreator/node_modules" \
SHOTS_DIR="$HOME/Downloads/设计意图测评台/demo-redesign-work/shots/A" \
node tests/demo_redesign_headless.cjs
```

若已有独立服务，可提供 `DEMO_URL=http://127.0.0.1:4182/vibocoding-assistant/` 验证部署子路径，脚本禁止 4180 和 4181。也支持以 `DEMO_URL=file:///.../dist/` 读取文件，但仍需环境允许启动 Headless Chromium。

## A 段返工

2026-11-13，根据窄屏截图反馈修订公共舞台与样板皮肤。

- 公共提示胶囊改为流式布局的最后一项，按实际换行高度占位，与内容至少相隔 12px。覆盖后加载的绝对定位及样板底部固定留白。旧版横排 canvas 为提示单独换行。舞台保留手机 16px 内边距，直接内容禁止 flex 收缩，容器保持自然高度和可见溢出。
- 点阵调整为 `rgb(17 24 39 / .07)`，点直径 1px，间距 20px，仅绘制于公共舞台背景。白色承托面保持不透明。
- component-lift 卡片以更高优先级的 `1px solid var(--ds-line)` 覆盖公共控件边框，并消除旧版 micro-card 内边距。静止和悬停分别沿用 `--ds-shadow-1`、`--ds-shadow-2`，保留上浮交互。图片容器顶部圆角为 15px，对应外层 16px 减去 1px 边框，图片继承该圆角。
- 邮箱浮动标签与姓名标签统一为 13px、500 字重，明确标签的显示、层级与 44px 容器高度。空值静止时显示在框内，聚焦或有内容时上浮，保留 `input + .fflabel` 关系。补充邮箱 label 与 input 的显式关联。说明文字按输入框宽度左对齐。
- 其他旧演示继续沿用现有主体样式。公共层的可见溢出与提示占位适用于全部演示。

验证结果如下。

- `PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/build_site.py` 通过，输出 217 页、192 条目。
- `PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -p test_site_build.py` 通过，共 21 项。
- 修改的 CSS 经 PostCSS 解析通过。
- 本轮 Headless Chromium 启动被沙箱拒绝，错误为 `MachPortRendezvousServer ... Permission denied (1100)`。390px 截图、实际提示间距及全部演示的浏览器几何尚待视觉复核。

## A 段精修 + B 段

2026-11-13，按本轮评审完成 A 段三项精修与 B 段六个样板。实现沿用 Shadow DOM 样式链、原交互适配器和内容数据。每项交付后均执行构建，最终产物为 `dist/`，共 217 页、192 条目。

### A 段公共调整

- 公共主体宽度令牌为 `--ds-subject-width:clamp(320px,52%,640px)`，承托面和十个样板的主体均使用 `min(100%,var(--ds-subject-width))`。手机可用宽度小于 320px 时受父容器约束。
- 新增 `--ds-demo-body/heading/title/button/control`。默认分别为 14/16/20/14/44px，实际舞台宽度达到 768px 后切换为 16/22/24/15/48px。现有桌面双栏中，1440px 页面主演示实际宽约 725px，因此额外为桌面详情页启用大字号档位。
- 舞台使用 `aspect-ratio:auto`，通过 `min-height:max(320px,62.5cqi)`、`max(300px,66.667cqi)`、`max(260px,75cqi)` 保留比例下限。正文、表单和网格按内容自然增高。
- 提示胶囊使用舞台内部左侧和底部各 12px 的绝对定位。舞台底部内边距为 76px，提供两行提示的实际布局空间。样板外包装采用静态定位，使提示统一锚定公共舞台。手机横向内边距保持 16px。
- 双层阴影继续使用墨色低透明度令牌。点阵恢复为 24px 间距、`rgb(17 24 39 / .05)`。按钮网格间距统一为 12px，表单组间距为 24px。
- 上浮卡片、交叉淡化和新图片样板设置裁切焦点。交叉淡化和轮播的文字区域采用透明至 `rgb(0 0 0 / .6)` 的遮罩，45% 高度之后保持该不透明度。纯白原图经过该遮罩后的最亮背景为 `#666666`，与白字对比度约 5.74∶1。

### 尺寸计算

下表按现有 `.wrap` 最大宽度 1184px、桌面左右内边距 32px、移动端左右内边距 16px，以及桌面主栏与使用卡 2∶1、栏间距 32px 计算。

| 页面宽度 | 主演示宽度 | 舞台内容区宽度 | 主体宽度 | 主体左右净距 | 网格列数 |
|---|---:|---:|---:|---:|---:|
| 1440px | 725.33px | 659.33px | 342.85px | 191.24px | 2 |
| 390px | 358px | 324px | 320px | 19px | 1 |

桌面主体占舞台内容区 52%。移动端承托面占用可用宽度，并由内容决定高度。两行提示的高度上限为 `2×12×1.5+2×6+2=50px`，加上底部偏移 12px 和正文间距 12px，共 74px，纳入 76px 底部预留。

以上为 CSS 尺寸推导与自动断言。字体实际排版、图片解码后的构图和视觉精致度由执行者通过截图复核。

### B 段样板

| 样板 | 实现与行为 |
|---|---|
| modal | 客厅真实图片承托面，确认弹窗保留 `#modal`、`.modal-box`、标题和描述关联、开关命令、遮罩关闭、Escape 和焦点回返。遮罩为 `rgb(17 24 39 / .45)`，背景模糊 4px，弹窗圆角 16px、shadow-3、20px 标题，次要与主要按钮右对齐。 |
| tooltip | 中文「分享」按钮与图标、深墨色白字 13px 气泡、8px 圆角、小箭头和 shadow-3。保留 `.tip/.bubble`，增加 tooltip 语义关联、键盘聚焦、Escape 收起、触屏点按切换与手机提示。 |
| scroll-reveal | 三张同系列真实庭院图与标题，保留 `.mini-scroll`、`.reveal-target`、滚动进度及重播。每张卡片进入本地滚动视口后分别淡入并上移 16px，时长 360ms，曲线为 `--ds-ease-out`。减少动态时直接显示内容。 |
| grid | 六张真实庭院和湖景卡片，保留 guide 的 `data-demo="grid"`、`data-mode`、原状态按钮及布局选择器。列宽下限 128px，使用 auto-fit，间距随实际舞台宽度采用 16/24px。原窄布局状态继续生效，内容自然增高。 |
| skeleton | 白色承托面上显示 `#E9EBEF` 骨架，微光采用白色半透明渐变的 transform 动画。模拟加载 1400ms，并等待真实图片加载后显示湖景图片、标题和正文。同步 `aria-busy`、内容可见性和加载状态播报，减少动态时直接等待图片并显示结果。 |
| carousel | 使用 `garden-dusk-01/02/03`，圆角 16px，44px 白色圆形浮钮配 shadow-2。当前指示点为紫色 24px 胶囊，独立点击区域为 44px，相邻间隔 8px。保留全部 `car*` ID、三项顺序、箭头、圆点、自动轮播、暂停与悬停/聚焦暂停行为。 |

新皮肤位于 `site-src/redesign/demo-skins/`，名称分别为 `ui-modal`、`ui-tooltip`、`motion-scroll-reveal`、`guide-grid`、`ui-skeleton`、`ui-carousel`。新增滚动与加载逻辑接入 `demos.py` 的既有生命周期，触屏提示逻辑接入 `demo-runtime.js`。

### 验证与执行者复核

| 验证 | 最终结果 |
|---|---|
| `PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/build_site.py` | 通过，217 页、192 条目 |
| `test_demo_audit` | 1 项通过 |
| `test_redesign_tokens` | 8 项通过，包含大舞台字号、比例下限、提示占位、主体比例、双尺寸网格与图片遮罩对比度 |
| `test_site_build` | 22 项通过，十套皮肤在四层资源路径下的契约、六样板选择器、真实图片和原锚点均覆盖 |
| `node tests/token_demos.cjs` | 五类 token 的交互、计算、主题及存储回退通过 |
| `test_redesign_javascript` | 12 项通过，包含 194 份演示初始化，以及骨架加载、减少动态、轮播、逐卡滚动显现、网格切换和弹窗关闭/焦点回返 |
| `node tests/audit_fix_batch3.cjs` | 10 组状态回调及减少动态生命周期通过 |
| Python AST、Node 语法、修改文件行尾空白检查 | 通过 |

测试断言随实现更新并新增针对性回归覆盖。测试初次并行运行时，共同触发重建并造成生成目录竞争，已恢复生成目录，最终验证全部串行执行。

执行者可运行已有复核入口。该入口现覆盖十个样板，并检查主体占比、手机净距、提示左下位置、内容间距和 B 段交互。

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/build_site.py
node tests/demo_redesign_headless.cjs
```

脚本沿用执行者现有 Playwright 环境，默认截图目录为 `output/demo-redesign/AB/`，报告为 `output/demo-redesign/headless-report.json`。截图覆盖 1440/390 两档，并额外记录打开状态的模态弹窗。本轮验收采用尺寸计算与 Node DOM 模型，浏览器截图及视觉验收由执行者完成。
