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


## C 段与类型级皮肤

2026-11-13。本轮范围为演示内部的 `demo-spec.css`、`demo-skins/`、`demos.py` 与 `demo-runtime.js` 注入链，以及对应测试。沿用给定规格，按主体放大、手机网格、滚动显现、C 段样板、类型级皮肤的顺序实施。每一项完成后均执行 `PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/build_site.py`，四个 C 段样板分别构建，后续修订也重新构建。

### 主体放大与两项修复

- 实际演示容器宽度达到 640px 后，主体宽度令牌切换为 `clamp(420px,66%,560px)`。标题 22–24px、正文 16px、按钮 15px，控件高 48px，承托面内边距 32px，按钮组间距 16px。十个既有样板共用宽度令牌。触发条件使用容器查询，手机维持原字号与宽度档位。
- 1440px 页面按既有双栏计算，舞台宽约 725.33px，可用内容宽约 659.33px，主体宽约 435.16px。该数值为 CSS 推导，实际排版待浏览器复核。
- `guide/grid` 在手机上固定两列，显示前四张，第五、六张通过 CSS 隐藏展示。六张图片与卡片仍在 DOM 中，原状态切换保留。手机承托面内边距 16px，卡片间距 12px。
- `motion/scroll-reveal` 将首段空白从 160px 收至 16px，补充「发现庭院之美」标题和一行正文。第一张卡初始带 `ds-revealed`，首屏直接可见，后续两张继续由原滚动监听逐张显现。滚动进度、重播、图片、减少动态处理沿用原机制。

### C 段四个样板

| 位置与 kind | 实现 |
|---|---|
| `basics/color` · token | 白色承托面、双列色盘、中文标签、对比度样本和结果反馈；保留前景／背景两项 `data-token-control`、`data-token-sample`、`data-token-output` 与原计算逻辑。 |
| `components/color` · ui | 「项目强调色」中文场景、色盘和实时十六进制色值，默认紫色；保留 `input[type=color]`、原 aria-label、`#hexc` 和输入事件。皮肤名称为 `ui-color`，与 `token-color` 分开解析。 |
| `scenarios/dashboard` · guide | 浅色「内容工作台」、本周访问 1,280、内容转化率 24%、七日访问柱状图。七日示例数据为 80、160、120、240、160、280、240，总数为 1,280。图表有完整中文无障碍说明，保留 `.mini-page*`、`data-demo="dashboard"`、`data-mode` 和两项状态按钮。 |
| `ai/skills/frontend-design` · skill-reference | 白色技能卡、浅灰信息块、紫色标签、双层阴影与清晰文字层级。演示内的技能名称、概述、适用情境、范围与能力标签沿用来源内容。手机信息块竖排，`dt` 明确使用深紫色，覆盖旧无障碍层的浅紫文字。 |

### 已单独重做的样板

共 14 个 kind/slug 组合，`color` 按 kind 区分。

- `ui` 共 7 个，包括 `button`、`input`、`color`、`modal`、`tooltip`、`skeleton`、`carousel`。
- `motion` 共 3 个，包括 `view-crossfade`、`scroll-reveal`、`component-lift`。
- `guide` 共 2 个，包括 `grid`、`dashboard`。
- `token` 共 1 个，包括 `color`。
- `skill-reference` 共 1 个，包括 `frontend-design`。

### 类型级注入与覆盖范围

新增 `_kind-motion.css`、`_kind-ui.css`、`_kind-guide.css`、`_kind-token.css`、`_kind-skill-reference.css`。`demos.py` 为适用演示输出 `data-kind-css` 与 `data-ds-kind`，已有单独皮肤优先。样式加载顺序为来源、公共规格、适用类型层、适用单独皮肤、无障碍层、适用状态层。重播和复原保留已加载的全部样式节点。

- UI 类型统一白色承托面、按钮和表单控件、卡片、标签、导航演示、表格以及语义提示。既有卡片主体省去额外承托面，浮层保留原定位与开关。
- Motion 类型统一适用卡片、列表和扩展演示的白底、圆角、双层阴影、文字与紫色控件。绘图、遮罩、指针坐标平面和滚动内容沿用来源几何。
- Guide 类型统一布局、表单、页面与数据示例的浅色面、字号、圆角和控件。内容自然增高，sticky 单独保留 260px 的局部滚动视口。
- Token 类型统一外部承托面与控件。圆角／阴影样本和主题样本跳过通用内卡片覆盖，保留 `--sample-radius`、`--sample-shadow`、`--sample-padding` 与主题变量的教学变化。
- Skill-reference 类型将其余九张技能卡套用同一浅色体系，保持来源文字。

按 192 个主条目去重，类型皮肤覆盖 **172 个**。连同 14 个单独样板，共影响 **186 个主条目**。`submit` 与 `undo` 两处 secondary motion 演示也加载类型皮肤，因此类型层共作用于 **174 份演示实例**。

#### motion · 74 个主条目

`view-slide`、`view-curtain`、`view-shared`、`view-stagger`、`scroll-parallax`、`scroll-pin`、`scroll-horizontal`、`scroll-progress`、`background-aurora`、`background-wave`、`background-particles`、`background-cursorwave`、`background-fluid`、`text-stagger`、`text-mask`、`text-typewriter`、`text-scramble`、`text-draw`、`media-wipe`、`media-carousel`、`media-blur`、`media-compare`、`media-glitch`、`component-tilt`、`component-spotlight`、`component-flip`、`component-press`、`component-switch`、`component-morph`、`overlay-menu`、`overlay-drawer`、`overlay-modal`、`overlay-tooltip`、`overlay-sheet`、`data-count`、`data-skeleton`、`data-bars`、`data-reorder`、`data-success`、`mobile-swipe`、`mobile-drag`、`mobile-pull`、`mobile-rubber`、`mobile-pager`、`filter-grid`、`accordion`、`toast-stack`、`tab-indicator`、`drop-snap`、`odometer`、`cross-page`、`inline-expand`、`shrink-header`、`section-nav`、`scroll-highlight`、`snap-sections`、`image-magnifier`、`timeline-preview`、`chart-morph`、`skeleton-handoff`、`component-magnetic`、`component-hover-preview`、`component-hover-action`、`text-text-morph`、`scroll-scroll-zoom`、`media-image-sequence`、`data-input-shake`、`cursor-cursor-follower`、`cursor-cursor-trail`、`cursor-cursor-eyes`、`cursor-object-follow`、`scroll-hide-header`、`component-ripple`、`component-underline`。

#### ui · 63 个主条目

`textarea`、`select`、`checkbox`、`radio`、`switch`、`slider`、`stepper`、`date`、`rating`、`search`、`cmdk`、`form`、`progress`、`toast`、`states`、`alert`、`loader`、`empty`、`drawer`、`navbar`、`sidebar`、`tabs`、`accordion`、`breadcrumb`、`pagination`、`steps`、`footer`、`dropdown`、`badge`、`chip`、`table`、`card`、`badge-dot`、`timeline`、`kpi`、`avatar`、`upload`、`combobox`、`segmented`、`popover`、`password-strength`、`tag-input`、`otp`、`inline-edit`、`hold-confirm`、`split-button`、`fab`、`mega-menu`、`context-menu`、`view-switch`、`table-fixed`、`table-columns`、`table-reorder`、`table-edit`、`infinite-scroll`、`load-more`、`back-to-top`、`conditional-step`、`advanced-settings`、`context-options`、`auto-save`、`virtual-list`、`card-link`。

#### guide · 22 个主条目

`sidebar`、`split`、`container`、`density`、`sticky`、`validation`、`submit`、`undo`、`bulk`、`optimistic`、`focus`、`landing`、`list`、`detail`、`settings`、`wizard`、`line`、`bar`、`stacked`、`donut`、`heatmap`、`sortable-table`。

#### token · 4 个主条目

`typography`、`spacing`、`radius-shadow`、`dark-mode`。

#### skill-reference · 9 个主条目

`ui-ux-pro-max`、`baseline-ui`、`create-design-md`、`fixing-accessibility`、`fixing-motion-performance`、`vercel-react-view-transitions`、`web-design-guidelines`、`webapp-testing`、`vercel-composition-patterns`。

### 结构与教学特例

- 六个视觉材质样板完整跳过类型皮肤，分别为 `minimal`、`editorial`、`organic`、`glass`、`brutalist`、`neumorphic`。这些条目的字体、底色、边框或阴影本身属于演示主题，继续使用公共规格与来源样式。
- UI 中 `card`、`card-link`、`empty`、`upload`、`kpi`、`navbar`、`sidebar`、`footer`、`accordion` 由原卡片提供白色主体，跳过新增外围承托面，继续应用类型皮肤。
- Motion 的背景类 `background-aurora`、`background-wave`、`background-particles`、`background-cursorwave`、`background-fluid`，媒体类 `media-wipe`、`media-carousel`、`media-blur`、`media-compare`、`media-glitch`、`media-image-sequence`，指针类 `cursor-cursor-follower`、`cursor-cursor-trail`、`cursor-cursor-eyes`、`cursor-object-follow`，以及 `component-flip`、`text-mask`、`text-draw`、`scroll-parallax`、`scroll-pin`、`scroll-horizontal`、`scroll-progress`、`scroll-scroll-zoom`、`scroll-hide-header` 保留自身画面／坐标／裁切结构，跳过额外白底包裹。这些条目仍加载类型层，类型层仅处理命中的安全文字或控件规则。
- Token 中 `radius-shadow` 的样本内卡片和 `dark-mode` 的主题样本跳过通用圆角／阴影覆盖，继续展示参数切换。

### 验证与待验收范围

| 检查 | 结果 |
|---|---|
| 构建 | 通过，217 页、192 条目 |
| `test_demo_audit` | 1 项通过 |
| `test_redesign_tokens` | 10 项通过 |
| `test_site_build` | 26 项通过 |
| `token_demos.cjs` | 五类交互、对比度、主题、存储回退及类型层教学变量保护通过 |
| `test_redesign_javascript` | 12 项通过，包含 194 份最终演示初始化 |
| `audit_fix_batch3.cjs` | 十组状态与减少动态生命周期通过，补充六层样式顺序及复原后节点保留断言 |
| CSS 与 JS 语法 | 20 份演示样式经 PostCSS 解析；浏览器复核脚本通过 Node 语法检查 |

浏览器复核入口 `tests/demo_redesign_headless.cjs` 已扩充到 14 个样板，增加 C 段交互、640px 主体宽度、首卡可见、手机四张两列网格与类型样式链断言，截图默认目录为 `output/demo-redesign/C/`。

当前环境监听 `127.0.0.1:4182` 返回 `EPERM`，本地文件入口启动 Chromium 返回 `MachPortRendezvousServer ... Permission denied (1100)`，浏览器接入另返回 `The browser access host is unavailable`。因此本轮没有形成 1440／390 截图，全部演示的实际溢出、截断与视觉效果仍待浏览器验收。自动初始化与静态几何断言的通过情况见上表。

覆盖明细同时保存于 `output/demo-redesign/C-coverage.json`。执行使用本轮工作区内的截止时间包装器，为启动的构建和测试子进程设置整组强制终止上限。


## D 段

2026-11-13。本段修复提示定位并恢复 ui、motion 类型皮肤。按公共定位、类型皮肤恢复、展开浮层占位、测试同步的顺序逐步构建，产物继续输出至 `dist/`，共 217 页、192 条目。

### 舞台与提示定位

带直接提示子项的 `.canvas`、`.stage`、`.guide-card-stage` 使用 `position:relative`、`flex:1 1 auto`、`min-height:100%` 和 `box-sizing:border-box`，填满 flex 列舞台。原舞台的内容内边距转移到该子容器，外舞台在此条件下使用零内边距，使定位父容器的边缘与舞台内边缘重合。桌面、平板、手机的内容内缩继续分别为 32、24、16px。

主体通过 `justify-content:center`、`align-items:center`、`align-content:center` 居中，按自身内容自然增高。内部容器保留可见溢出与原有定位上下文。已清理公共规格和无障碍层中样板容器的静态定位覆盖。提示继续使用 `inset:auto auto 12px 12px`。外舞台的 1px 边框使提示矩形相对舞台外边缘的实测目标为左侧、底部各 13px。

底部基本占位为 56px。实际舞台宽度不超过 380px 时采用 76px，为两行提示提供空间。guide 的状态按钮和运行时反馈输出在 flex 排序中位于主体前方，主体成为最后一个流式子项，提示随主体容器抵达舞台底部。

### 类型皮肤与展开状态

`demo-skins-wip/_kind-ui.css` 和 `_kind-motion.css` 经修复后复制回 `demo-skins/`，两份草稿及空目录已删除。

- ui 类型的 `.canvas` 承担透明布局。按钮、表单控件、卡片、导航、表格、标签和浮层采用原稿中的字体、颜色、圆角及阴影。白色承托面施加于具体组件，并显式排除 `.ds-hint`。
- motion 类型沿用原稿的组件承托面、文字和操作按钮样式。主体组件显式排除 `.ds-hint`，舞台继续承担提示的定位。
- 展开的 dropdown、popover、split-button 分别增加 176、144、152px 底部外边距，容纳其绝对定位浮层。菜单、按钮和浮层的原父子关系与定位方式继续生效。
- motion 菜单展开时的主体最小高度为 181px。悬停预览主体最小高度为 152px，容纳预览卡的完整矩形。

### 双尺寸推算与规则核查

宽度沿用现有页面布局计算。下列数据均以 border-box 为基准。

| 校核项 | 1440px 页面 | 390px 页面 |
|---|---:|---:|
| 主舞台宽度 | 725.33px | 358px |
| 舞台比例最小高度 | 453.33px | 268.5px |
| 主体可用宽度 | 659.33px | 324px |
| 样板主体宽度 | 435.16px | 320px |
| 子容器底部占位 P | 56px | 76px |
| 提示高度校核 h | 32px，单行 | 50px，两行上界 |
| 主体与提示最小净距 | 12px | 14px |
| 提示相对外边缘左 / 下净距 | 13 / 13px | 13 / 13px |

令子容器实际高度为 H、顶部内边距为 T、主体全部流式内容高度为 B。自然增高满足 `H >= T + B + P`。内容居中后主体底边最多抵达 `H - P`，提示顶边为 `H - 12 - h`，因此两者净距下界为 `P - 12 - h`。以上两档分别得到 12px 和 14px。自动测试对 B 为 44、48、120、260、600、1200px 的情形逐一核查，覆盖单行控件、常规卡片和长内容增高。

| 类型规则 | 矩形或尺寸校核 |
|---|---|
| 提示父容器 | 填满舞台并承担内边距，提示左下定位参考完整舞台内部矩形 |
| ui 按钮 | 桌面 `15×1.5+20+2=44.5px`，纳入 48px 最小高度。手机 `14×1.5+20+2=43px`，纳入 44px 最小高度 |
| ui dropdown | 三项菜单、分隔项、边框、内边距和 6px 偏移合计上界 171.2px，纳入 176px 占位 |
| ui popover | 250px 宽度下按标题加三行正文、行高 1.6、内边距、边框、段距和偏移计算，上界 125.2px，纳入 144px 占位 |
| ui split-button | 三个 44px 手机操作、容器内边距与边框、5px 偏移共 149px，纳入 152px 占位 |
| motion 展开菜单 | `39+10+3×44=181px`，由主体最小高度完整容纳 |
| motion 悬停预览 | 顶部偏移、内边距、边框、两档文字与间距合计 145px，纳入 152px 最小高度 |
| 组件承托面 | 沿用源组件宽度并受公共 `max-width:100%` 约束，外层按内容增高、保持可见溢出 |
| 颜色、圆角与阴影规则 | 沿用各组件矩形，提示通过独立的绝对定位和底部占位布局 |

上述推算针对公共主体和提示的布局边界。源演示的滚动视口、图片裁切和浮层遮罩继续由各自组件控制。真实字体排版、全部交互状态和浏览器最终像素边界仍需浏览器运行验证。

### 测试同步与验证

`test_redesign_tokens.py` 新增提示父容器定位、类型皮肤恢复、展开浮层占位和双尺寸矩形计算回归。先验证缺失规则导致失败，再修复并复测。`test_site_build.py` 补充 ui、motion 发布皮肤与生成资产内容一致的断言，并逐一核查全部 150 个提示的父容器和双尺寸文本高度上界。既有测试保留。

`demo_redesign_headless.cjs` 补充全部 ui、motion 详情页的双尺寸几何检查，检查提示左下偏移、主体净距、定位父容器、水平溢出，以及五种展开浮层的完整矩形。样板主体宽度计算同步使用主体父容器的实际内容区。

本轮 Headless 通过 `file://` 入口执行，启动 Chromium 时收到 `MachPortRendezvousServer ... Permission denied (1100)`，在页面渲染前退出。报告位于 `output/demo-redesign/headless-report.json`。本段采用尺寸推算和自动测试交付，浏览器截图与实际像素验收仍待执行。


| D 段最终验证 | 结果 |
|---|---|
| `PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/build_site.py` | 通过，217 页、192 条目 |
| `test_demo_audit` | 1 项通过 |
| `test_redesign_tokens` | 14 项通过 |
| `test_site_build` | 27 项通过，含 150 个提示的双尺寸校核 |
| `node tests/token_demos.cjs` | 五类 token 交互、对比度、主题及存储回退通过 |
| `test_redesign_javascript` | 12 项通过，包含 194 份演示初始化 |
| `node tests/audit_fix_batch3.cjs` | 十组状态回调及减少动态生命周期通过 |
| CSS / JS / Python | 四份修改的 CSS 通过 PostCSS 解析，复核脚本通过 Node 语法检查，Python AST 与修改文件行尾空白检查通过 |
| 修改范围核对 | 154 份 `site-src` 基线中，四份目标 CSS 修改、两份 wip CSS 删除，其余 148 份文件 SHA-256 一致 |
| 浏览器 1440 / 390 | Chromium 启动被沙箱拒绝，实际渲染待验 |

执行期间使用 `output/demo-redesign/D/run.py` 包装构建和测试子进程，24 分钟后拒绝启动工作，26 分钟截止时强制结束对应进程组。本段全部工作在 24 分钟时限内结束。

# 演示重做 E 段实施记录

日期为 2026-11-13。本段按清单顺序完成 16 个 slug，每个条目各有独立 CSS 与 HTML 皮肤，共新增 32 份皮肤文件。六批分别完成 3、3、3、3、2、2 项，每批末尾均构建通过，最终重新构建与验证通过。生成站点仍为 217 页、192 条目，194 份主演示及 secondary 保留来源身份。

## 完成的 slug 清单

| 顺序 | 路径 / slug | 皮肤 | 精修内容 |
|---|---|---|---|
| 1 | `components/states` | `ui-states.css/html` | 保留全部 12 态及原标签顺序，统一按钮尺寸，12px 灰色状态标签，桌面四列、手机三列、窄缩略图两列网格 |
| 2 | `scenarios/landing` | `guide-landing.css/html` | 中文创作工具落地页，价值说明、主动作、工作室图片与三个创作步骤，保留状态切换与窄版机制 |
| 3 | `components/card` | `ui-card.css/html` | 工作室实图、阅读信息、中文标题与说明，16px 外圆角和双层静止 / 悬停阴影 |
| 4 | `components/toast` | `ui-toast.css/html` | 触发后使用白底、shadow-3、成功图标、原提示标题及说明，连续触发复用同一反馈输出 |
| 5 | `components/navbar` | `ui-navbar.css/html` | 中文站点名称、当前入口、登录入口和内容层级，保留 `.navbar`、`.brandw`、`.links` 及原导航项 |
| 6 | `components/table` | `ui-table.css/html` | 成员表格承托面、表头、成员头像字、在线状态和页脚说明，保留原行列数据 |
| 7 | `components/tabs` | `ui-tabs.css/html` | 白色信息面板、等宽标签、紫色选中指示、稳定内容区，保留全部 tab ID、键盘关系及命令 |
| 8 | `components/switch` | `ui-switch.css/html` | 加入「自动保存」标签和说明，关联可读标签、44px 点击区、焦点环和原开启 / 关闭反馈 |
| 9 | `components/select` | `ui-select.css/html` | 城市选择表单、常驻标签和说明，保留原生选择器、全部原选项与键盘交互 |
| 10 | `components/hold-confirm` | `ui-hold-confirm.css/html` | 草稿上下文、危险操作按钮、进度填充、取消说明与等价入口，保留原长按时序及键盘处理 |
| 11 | `interactions/view-slide` | `motion-view-slide.css/html` | 庭院与湖景双图、底部文字遮罩，保留双面板、200% 轨道和前进 / 返回方向切换 |
| 12 | `interactions/view-curtain` | `motion-view-curtain.css/html` | 庭院主图与湖景图片幕布，保留原 curtain 遮罩动画和重播机制 |
| 13 | `interactions/media-wipe` | `motion-media-wipe.css/html` | 庭院实图、中文标题和原说明，保留原遮罩揭示动画 |
| 14 | `interactions/media-blur` | `motion-media-blur.css/html` | 客厅实图、中文标题和原说明，保留原模糊到清晰动画 |
| 15 | `interactions/scroll-parallax` | `motion-scroll-parallax.css/html` | 同源庭院图片的远景层与渐变蒙版前景层，保留两层原滚动速度、滚动容器与进度条 |
| 16 | `interactions/scroll-pin` | `motion-scroll-pin.css/html` | 三幅庭院图片按原滚动进度切换，保留 sticky 场景、三幕文字及退出路径，减弱动态下使用流式位置 |

跳过条目为零。1440 / 390 的浏览器视觉验收仍待完成，具体阻塞见下文。

## 规格与范围核对

主体沿用 `--ds-subject-width`。以现有 1440px 页面对应的 725.333px 舞台计算，主体约 435.16px，占舞台约 60%。390px 页面对应 358px 舞台，主体不超过 320px，两侧各至少 19px。内容采用自然高度，长内容使舞台增高。以上为样式规则与尺寸推算，浏览器最终像素边界仍待验收。

皮肤使用现有中文字体栈、中性底色、紫色强调、语义色、16 / 12 / 8px 圆角和双层阴影。状态网格使用标题、按钮、标签三级字阶。图片主体使用标题、正文和舞台提示三级字阶。图片来自现有 `site-src/demo-assets/`，均提供 640 / 1280 的 srcset、中文替代文本或装饰图空替代文本、主色占位、cover 裁切与内描边。视差前景使用同一张原图的蒙版层，未生成独立抠图资产。

Toast 原运行时只输出纯文本。本段在 `demo-runtime.js` 中增加可选 `.ds-toast-output` 容器，仅该皮肤提供此容器。命中后构造图标、原消息标题和说明三个节点，使用 textContent 写入内容，复用原 output 与 aria-live。其他条目的反馈保持原输出路径。独立 Node 测试验证普通反馈、增强反馈、文本安全写入与连续触发复用。

公共 `demo-spec.css`、`demo-accessibility.css`、类型皮肤、外框模板、页面样式、条目源数据、提示词与验收要求文件的基线 SHA-256 一致。各皮肤保留原提示父容器及 ctl / stage-label 位置，继续由既有公共机制将提示胶囊固定在舞台左下角。全部 150 个提示的父容器和双尺寸预留空间检查通过。

## 测试同步与验证

既有测试全部保留。类型皮肤覆盖数量同步为 ui 54、motion 68、guide 21、token 4、skill-reference 9，独立样板数量由 14 更新为 30，特殊风格排除仍为 6，总计仍为 192。

新增 E 段检查覆盖全部 16 个皮肤的发布、来源选择器与交互属性、12 态标签及禁用态、表单关联、tab / hold 命令、八个图片条目在四层路径下的 srcset、主体宽度和圆角阴影。`demo_redesign_headless.cjs` 加入全部 16 条路径及状态网格、触发 Toast、开关、选择、标签、长按、滑移和滚动后的检查，保留原 A–D 段检查。

| 最终验证 | 结果 |
|---|---|
| `scripts/build_site.py` | 通过，217 页、192 条目 |
| `test_demo_audit` | 1 项通过 |
| `test_redesign_tokens` | 15 项通过 |
| `test_site_build` | 30 项通过 |
| `node tests/token_demos.cjs` | 五类 token 的交互、计算、主题与存储回退通过 |
| `test_redesign_javascript` | 13 项通过，包含 194 份演示初始化和 Toast 局部结构回归 |
| `node tests/audit_fix_batch3.cjs` | 十组状态回调与减少动态生命周期通过 |
| CSS / HTML / Python / JS | 35 份皮肤 CSS 经 PostCSS 解析通过，16 份新增 HTML 标签平衡，修改测试 Python AST、JS 语法和行尾空白检查通过 |
| 1440 / 390 浏览器验收 | 环境阻塞，0 张截图，实际视觉效果及像素边界待验收 |

最终构建与自动测试日志位于 `output/demo-redesign/E/`，汇总为 `verification.json`。Headless 使用工作区内 `dist/` 的 file URL，启动 Chromium 时收到 `MachPortRendezvousServer ... Permission denied (1100)`，在页面渲染前退出。错误保存于 `headless-attempt.log` 和 `headless-report.json`。浏览器预览通道另返回 `The browser access host is unavailable`。

执行起点为本地时间 02:07:24。`output/demo-redesign/E/run.py` 使用同目录 `deadline.json`，02:31:24 后拒绝启动工作，运行中的构建与验证进程组在 02:33:24 截止时强制结束。本段实施、构建、验证与记录均在 24 分钟工作时限内完成。
