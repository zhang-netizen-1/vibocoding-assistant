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


## F 段

2026-11-13。本段依照指定顺序完成表单与反馈分组的 19 个条目，每个条目提供独立的 `ui-<slug>.css` 与 `.html`，共 38 份新增皮肤文件。前六批各完成 3 项后构建，第七批完成最后的 popover 后构建，共七批构建通过。最终站点为 217 页、192 条目，主演示及 secondary 合计 194 份。

### 完成的 slug

| 顺序 | slug | 演示场景与精修内容 |
|---|---|---|
| 1 | `checkbox` | 通知与登录设置，父级行与三个子项分层，44px 标签点击区，保留全选、半选和原选项文字 |
| 2 | `radio` | 工作室方案，基础版与专业版各有说明，选中描边与浅紫底，保留同组单选关系 |
| 3 | `slider` | 播放音量，常驻标签、滑块和等宽百分比，保留范围、初值、方向键与实时数值更新 |
| 4 | `otp` | 手机号码验证，六格验证码、手机号上下文和原状态说明，保留自动前进、退格与整段粘贴 |
| 5 | `search` | 工作室资料搜索，标签、完整输入区和查询示例，保留搜索按钮、回车命令及错误状态反馈 |
| 6 | `segmented` | 浏览偏好，原生 fieldset / legend、列表和网格选项，选中底、44px 标签和焦点环 |
| 7 | `password-strength` | 设置账号密码，常驻标签、四段强度条和原实时说明，弱、中、强使用语义色，保留原五档评分 |
| 8 | `tag-input` | 项目标签，常驻标签、可换行输入区和说明，44px 删除按钮，保留回车、逗号、去重、退格与失焦添加 |
| 9 | `stepper` | 样册订购数量，48px 增减按钮、居中数量与下限说明，保留最小值和直接输入 |
| 10 | `rating` | 服务满意度，五个独立星级操作与评分说明，紫色表示已选星级，保留 aria-pressed 更新 |
| 11 | `upload` | 项目附件，文件标签、浅灰拖放区和结果说明，保留原文件选择、拖放与键盘操作 |
| 12 | `combobox` | 收货地址，城市标签、原生建议输入和说明，保留北京、上海、深圳、广州全部建议值 |
| 13 | `date` | 项目会议，日期标签、完整原生日期控件和键盘说明，使用浅色系统日历 |
| 14 | `form` | 工作室账号，用户名与密码各有标签和说明，主按钮全宽，保留本地模拟注册命令 |
| 15 | `alert` | 项目状态通知，保留四条原状态消息，增加具体说明，信息使用中性灰，警告、错误和成功使用语义色 |
| 16 | `empty` | 工作室项目空态，保留原图标、原引导文字和创建操作，补充下一步说明 |
| 17 | `loader` | 项目资料加载，中性灰转圈、加载标签和等待说明，减少动态时静止显示，保留原重播生命周期 |
| 18 | `drawer` | 项目筛选，入口承托面、右侧面板、筛选范围说明，16px 圆角和 shadow-3，保留遮罩、关闭与 Esc 命令 |
| 19 | `popover` | 项目共享说明，常驻标签、原触发按钮与原浮层内容，shadow-3 和展开占位，保留外点关闭与 Esc |

跳过条目为零。以上为样式、结构与自动测试完成情况，1440 / 390 的浏览器视觉验收待完成。

### 尺寸、状态与提示定位

各主体继续使用 `width:min(100%,var(--ds-subject-width))`。按现有页面布局推算，1440px 页面对应约 725.33px 舞台、435.16px 主体，主体占舞台约 60%。390px 页面对应 358px 舞台、320px 主体，两侧各约 19px。承托面使用 16px 圆角与双层 shadow-1，浮层使用 shadow-3，控件采用 8px 圆角和 8 / 12 / 16 / 24px 间距。文字使用 16 / 14 / 12px 三级层级。

验证码在窄舞台下采用三列两行，保持六个输入格的原 DOM 顺序、自动跳格与粘贴行为，为每格保留至少 44px 点击尺寸。桌面显示一行六格。标签输入支持内容换行，日期控件和建议输入区使用可收缩宽度。Popover 展开后增加 168px 流式占位，使浮层和底部说明自然推高主体。上述尺寸属于规则与静态推算，最终字体排版和像素边界仍待浏览器复核。

现有状态切换机制继续负责固定展示与原生禁用。独立皮肤补充可用控件的悬停、按下、焦点、禁用和 aria-invalid 样式，禁用时退出悬停反馈，减少动态时停用皮肤过渡。密码强度使用错误、警告和成功语义色。信息提示、标签、加载转圈和次要按钮使用中性色，紫色用于选中、主操作与规格要求的焦点环。

全部提示仍为 `.canvas` 的直接子项，沿用公共左下角绝对定位和底部预留空间。抽屉 HTML 覆盖层显式保留 `.ds-overlays`，其直接子项保持 `dmask`、`dpanel` 顺序，关闭状态的面板由原公共容器裁切。

本轮对原有 184 份 `site-src` 文件逐一核对 SHA-256，全部一致。新增范围为本段 38 份皮肤。来源控件的 id、class、data 命令、原文本、placeholder、原生约束与无障碍属性均有回归断言。条目数据与外框在上述原文件哈希校验范围内。

### 测试同步与结果

既有测试保留。类型皮肤覆盖数量同步为 ui 35、motion 68、guide 21、token 4、skill-reference 9，独立样板 49、特殊风格排除 6，总计 192。

`test_site_build.py` 增加 F 段发布一致性、来源节点和原文保留、标签关联、六位验证码、全部城市建议、四种提示、浮层命令和提示父容器检查。`test_redesign_tokens.py` 增加全部 19 份独立皮肤的令牌、尺寸、状态与减少动态检查。JavaScript 初始化测试复用原 Node DOM 模型，补充父级半选、滑块输出、验证码粘贴与退格、五档密码强度、标签去重与删除、数量下限、评分、文件选择、抽屉和浮层交互回归。

| 验证项目 | 结果 |
|---|---|
| 七批构建与最终 `scripts/build_site.py` | 通过，217 页、192 条目 |
| `test_demo_audit` | 1 项通过 |
| `test_redesign_tokens` | 16 项通过 |
| `test_site_build` | 33 项通过，含全部 150 个提示的双尺寸静态校核 |
| `node tests/token_demos.cjs` | 五类 token 的交互、对比度、主题和存储回退通过 |
| `test_redesign_javascript` | 13 项通过，含 194 份演示初始化与 F 段交互回归 |
| `node tests/audit_fix_batch3.cjs` | 十组状态回调与减少动态生命周期通过 |
| CSS / HTML / Python / JS | 19 份 CSS 解析及令牌引用通过，19 份 HTML 标签平衡与 ID 唯一，修改测试 AST、JS 语法及 42 份代码文件行尾空白检查通过 |
| 浏览器 1440 / 390 | 环境阻塞，0 张截图，实际渲染待验 |

`demo_redesign_headless.cjs` 已加入本段全部 19 条详情路径、主体几何和对应交互检查。通过工作区 `dist/` 的 file URL 尝试执行，192 条目 / 194 演示的入口盘点通过，Chromium 启动阶段收到 `MachPortRendezvousServer ... Permission denied (1100)`，页面渲染前退出。浏览器接入通道同时返回 `The browser access host is unavailable`。本段未形成实际浏览器截图或像素验收结论。

最终测试串行执行，避免多个测试入口各自重建 `dist/` 时争用产物。日志及汇总保存在 `output/demo-redesign/F/`，包括 `verification.json`、`source-check.json`、`css-parse.log`、`html-check.log`、`headless-attempt.log` 与 `headless-report.json`。

工作窗口起点为本地时间 02:34:40，24 分钟截止为 02:58:40，进程强制终止截止为 03:00:40。`output/demo-redesign/F/run.py` 在工作截止后拒绝启动新任务，并为本轮启动的构建与测试设置进程组强制终止上限。

本段最终复核于本地时间 02:50:22 完成，工作耗时约 15.7 分钟，处于 24 分钟工作窗口内。

## G 段

日期为 2026-11-13。本段完成 26 个条目的独立 CSS 与 HTML 皮肤，共 52 份新增皮肤。前八批分别完成 3 项后构建，第九批完成最后 2 项后构建，九批均通过。最终构建为 217 页、192 条目，主演示与 secondary 合计 194 份。

### 完成的 slug

| 分组 | 完成条目 |
|---|---|
| navigation | `cmdk`、`sidebar`、`accordion`、`breadcrumb`、`pagination`、`steps`、`dropdown`、`context-menu`、`mega-menu`、`footer` |
| content | `badge`、`chip`、`avatar`、`kpi`、`timeline`、`badge-dot`、`view-switch`、`card-link` |
| actions | `split-button`、`fab`、`back-to-top` |
| tables | `table-fixed`、`table-columns`、`table-edit`、`sortable-table`、`load-more` |

跳过条目为零。25 个 UI 演示使用 `ui-<slug>.css/html`。`components/sortable-table` 的源安装器为 guide，因此沿用 `guide-sortable-table.css/html`，保持源演示身份与状态切换入口。`components/sidebar` 使用 `ui-sidebar`，`basics/sidebar` 继续使用原 guide 类型皮肤，构建测试覆盖两者的区分。

全部原条目文字、提示词、验收要求、源演示文案、id、class、data、ARIA、原生控件约束和提示父容器均保留。新增中文上下文覆盖工作室项目、订单、配送、文件交付、成员与渠道统计。承托面为 16px 圆角、中性白底、双层 shadow-1，浮层为 shadow-3。文字按标题、主体与说明建立三级层级。紫色用于选中、主操作与焦点，完成、风险、未读和趋势使用对应语义色。表格内部继续保留演示所需的双向滚动，页面与舞台保持自然高度。

### 公共边距与交互修复

公共 `demo-spec.css` 的提示父容器改为 `flex:1 0 auto`、`min-height:min-content`，使用安全居中，并显式设置 `padding-top:max(16px,var(--ds-stage-inset))!important`。主体按固有内容撑高，提示继续以原父容器为定位参考，保留舞台左下角 13px 外边缘净距及原 56 / 76px 底部占位。这组公共规则覆盖独立皮肤与类型皮肤。

命令面板展开时通过 `.demo-root.ds-stage:has(.cmdk-mask.show)` 提高舞台最小高度至 560px，选择器优先级覆盖手机公共舞台规则。下拉菜单与分裂按钮菜单分别预留 188px 与 176px，右键区域最小高度 192px，确保展开矩形位于舞台内。大型菜单使用流式两列布局，快捷操作展开后自然增高。固定表格保留吸顶表头与吸左首列，列宽表允许文字换行，编辑输入框保持可收缩宽度。

浏览器交互检查发现两处既有脚本问题，均在 `demos.py` 的源适配层修复。

- guide 函数提取的终点原先命中了 `setText` 之前的卡片筛选循环，导致生成脚本缺少 `updateInteraction` 与 `updateData`。终点搜索现从函数起点开始，恢复原函数体。排序表按访问量降序与按渠道名称升序的切换通过回归。
- 单元格输入框 Enter 保存后，事件继续冒泡至单元格，导致再次进入编辑。单元格开始编辑的键盘入口增加 `e.target===cell`，保留 Enter / 失焦保存与 Esc 取消，并避免重复进入。

### 验证与证据

既有测试保留。类型皮肤覆盖数量同步为 ui 10、motion 68、guide 20、token 4、skill-reference 9，独立皮肤 75、特殊风格排除 6，总计 192。新增回归覆盖全部 26 份皮肤的发布内容、来源属性与原文、提示父容器、同名 sidebar、命令浮层归属、公共固有高度和安全居中、浮层占位及手机命令面板规则优先级。

`tests/demo_g_browser.js` 提供真实 DOM 交互检查，并接入原 `demo_redesign_headless.cjs`。覆盖搜索空态、折叠展开、步骤选中、菜单打开与关闭、标签删除、未读清除、视图切换、独立分享、快捷创建、返回顶部、表头与首列固定、列显隐与调宽、单元格提交与取消、渠道排序和追加加载终态。原 Headless 入口增加全部 G 段路径与四边几何检查。

| 验证项目 | 结果 |
|---|---|
| 九批构建与最终构建 | 通过，217 页、192 条目 |
| `test_demo_audit` | 1 项通过 |
| `test_redesign_tokens` | 19 项通过 |
| `test_site_build` | 35 项通过 |
| `node tests/token_demos.cjs` | 五类 token 的交互、计算、主题与存储回退通过 |
| `test_redesign_javascript` | 13 项通过，包含 194 份演示初始化和 guide 排序回归 |
| `node tests/audit_fix_batch3.cjs` | 十组状态回调与减少动态生命周期通过 |
| CSS / HTML / Python / JS | 26 份独立 CSS 与公共 CSS 经 PostCSS 解析，26 份 HTML 标签平衡与 ID 唯一，修改 Python AST 与两份浏览器脚本语法检查通过 |
| 原生 Chrome 的舞台双尺寸夹具 | 28 个条目 × 2，56 项几何、106 条交互断言通过，包含原 `hold-confirm` 与 `states` |
| 原生 Chrome 的 UI 类型皮肤 | 10 个剩余 UI 类型皮肤在 390 档全部通过，最小顶距 20.953px、最小侧距 39px |
| 真实构建详情页双尺寸夹具 | 56 个真实详情页舞台与 106 条交互断言通过，390 档最小顶距 17px、最小侧距 19px，1440 档主体约占舞台 59.994% |

舞台夹具实测，390 档主体最小顶距为 17px、最小侧距 19px，1440 档主体占舞台约 59.994%。该夹具加载当前真实 markup、公共 / 独立 / 无障碍样式和原安装器。原公共规则的对照夹具中，`hold-confirm` 与 `states` 的约 4px 顶距现象未复现，修复后的边距以当前 Chromium 实测值为准。

Headless Chromium 启动时仍收到 `MachPortRendezvousServer ... Permission denied (1100)`，浏览器接入服务返回 `The browser access host is unavailable`。本段通过原生 Chrome 打开工作区的本地核验文件，完成上述浏览器检查。详情页夹具直接读取最终 `dist/components/<slug>/index.html`，保留完整外框、状态样式与脚本执行顺序，将资源内联以支持本地 file 协议。页面截图在 CUA 工具输出中可查看，独立 PNG 文件未导出。

对 212 份既有 `site-src` 文件逐一核对 SHA-256，修改文件为 `demo-spec.css` 与 `demos.py` 两份，其余 210 份一致。52 份独立皮肤为新增。验证日志、九批构建日志、`source-check.json`、`verification.json`、本地舞台夹具与真实详情页夹具位于 `output/demo-redesign/G/`。

工作起点为本地时间 03:02:20，24 分钟工作截止为 03:26:20，26 分钟进程截止为 03:28:20。`output/demo-redesign/G/run.py` 在工作截止后拒绝启动新任务，并在进程截止时强制结束本轮构建与测试子进程组。本段最终复核于本地时间 03:22:11 完成，耗时约 19.86 分钟，处于 24 分钟工作窗口内。

## H 段

日期为 2026-11-13。本段按指定顺序完成 37 个交互与动效条目的独立 CSS 与 HTML 皮肤，共新增 74 份皮肤文件。前十二批各完成 3 个条目后构建，第十三批完成最后 1 个条目后构建，13 批均通过。精修与测试同步后另行执行最终构建，产物为 217 页、192 条目，主演示与 secondary 合计 194 份。

### 完成的 slug

| 分组 | 完成条目 |
|---|---|
| component，14 条 | `component-tilt`、`component-spotlight`、`component-flip`、`component-press`、`component-switch`、`component-morph`、`tab-indicator`、`inline-expand`、`component-magnetic`、`component-hover-preview`、`component-hover-action`、`component-ripple`、`component-underline`、`accordion` |
| overlay，6 条 | `overlay-menu`、`overlay-drawer`、`overlay-modal`、`overlay-tooltip`、`overlay-sheet`、`toast-stack` |
| data，9 条 | `data-count`、`data-bars`、`data-reorder`、`data-success`、`filter-grid`、`chart-morph`、`skeleton-handoff`、`data-input-shake`、`data-skeleton` |
| text，8 条 | `text-stagger`、`text-mask`、`text-typewriter`、`text-scramble`、`text-draw`、`odometer`、`scroll-highlight`、`text-text-morph` |

跳过条目为零。全部采用 `motion-<slug>.css/html`。交互栏目中的手风琴使用 `motion-accordion`，组件栏目的 `ui-accordion` 沿用现有文件，测试覆盖两者的独立接入。

### 主体与视觉精修

倾斜与聚光应用于工作室、会客厅图片卡片。翻面展示庭院采风计划与行程说明。按压按钮放入文件交付卡片，开关放入通知偏好设置，按钮变形用于项目资料分享。标签指示器、行内展开、手风琴分别承载项目概览、任务看板与完整问题说明。悬停预览展示手册封面与页数，悬停操作栏承载真实庭院封面与编辑、复制、删除操作。磁吸与涟漪按钮分别放入项目创建与灵感收录场景，下划线沿用工作室导航。

浮层使用工作室项目上下文、真实素材缩略图与完整面板内容。菜单展开时预留 224px 流式空间，抽屉、弹窗限制在承托面内部，面板采用 shadow-3。底部弹层保留拖动手柄和原关闭阈值，手柄命中区域增至 64×24px。通知列表按实际内容增高，继续保持最多三条的原逻辑。

数据动效使用收藏统计、工作日访问图表、任务优先级、交付结果、带图片的作品筛选、资料加载与成员邀请表单。文字动效放入有配图、分类和正文的中文内容卡片，路径描画嵌入采风路线卡，数字滚动承载实时互动统计，随读高亮保留内部滚动容器，文字变形承载项目工作流。

所有图片均来自已有 `site-src/demo-assets/`，带 640 / 1280 的 srcset、中文 alt、清单中的主色背景和 cover 裁切。主体使用 `width:min(100%,var(--ds-subject-width))`，沿用原公共舞台与提示胶囊机制。按现有外框与 CSS 规则推算，1440 档主体约占舞台 60%，390 档主体两侧约为 19px。四边实际像素净距、字体排版、图片裁切与视觉精致度尚待浏览器核验。

### 行为、时序与减少动态

来源动效生成器、原始 CSS / JS、条目数据、提示词、验收文字与公共舞台规格均保持原文件内容。37 条回归逐节点核对原 id、class、data、ARIA、内联样式、控件属性和文字，提示仍为原 `.stage` 的直接子项。原有链接规范化继续将演示中的 `javascript:void 0` 转为 `#`。

独立皮肤没有新增关键帧，也没有覆盖正常模式中的原动画时长或曲线。按压的 80ms、翻面的 500ms、标签指示器的 320ms 与原曲线、图表的 550ms 与原曲线均继续来自来源样式。JavaScript 回归核对按钮变形的 420 / 1050ms、资料交接的 520 / 230ms 和数字滚动的 850ms，数字轨道继续使用原 47px 步长。

现有 `demo-runtime.js` 增加仅针对 `.ds-h-demo` 五种悬停主体的触屏点按复原、键盘 Enter / Space、Esc 关闭和状态同步。原生按钮保留原键盘触发方式，鼠标进入与重新聚焦会恢复悬停可见性。手机提示通过现有 `data-touch-hint` 机制切换。其余栏目、外框样式与公共胶囊规则沿用现状。

减少动态模式下，倾斜、磁吸、排序位移停止，文字、柱状图与描画保留来源最终状态。两类骨架演示显示已准备好的资料内容，随读文字显示最终高亮。所有新增减少动态规则沿用 `data-demo-motion-once` / `data-demo-motion-step` 门控，主动播放入口继续由原生命周期处理。

### 测试同步与结果

既有测试保留。类型皮肤数量同步为 ui 10、motion 31、guide 20、token 4、skill-reference 9，独立皮肤 112、特殊风格排除 6，总计 192。

新增测试覆盖 37 条独立皮肤的发布、来源节点和原文、提示父容器、同名手风琴、四层相对资源路径、令牌引用和减少动态门控。JavaScript 测试补充来源交互与明确时序，并直接执行新触屏监听器，核对五种主体的首次点按、再次点按、键盘关闭、原生按钮按键以及鼠标和聚焦恢复。

`tests/demo_h_browser.js` 已接入原 `demo_redesign_headless.cjs`，包含 H 段 37 条路径、主体四边与提示净距、桌面宽度比例及可交互状态断言。原 G 段手风琴检查增加组件栏目范围，以分别检查两个同名条目。浏览器脚本通过语法检查，实际浏览器断言尚未执行。

| 验证项目 | 结果 |
|---|---|
| 13 批构建与最终构建 | 通过，217 页、192 条目 |
| `test_demo_audit` | 1 项通过 |
| `test_redesign_tokens` | 20 项通过 |
| `test_site_build` | 37 项通过 |
| `node tests/token_demos.cjs` | 五类 token 的交互、对比度、主题与存储回退通过 |
| `test_redesign_javascript` | 15 项通过，含 194 份演示初始化与 H 段交互、时序和触屏监听器回归 |
| `node tests/audit_fix_batch3.cjs` | 十组状态回调与减少动态生命周期通过 |
| CSS / HTML / Python / JS | 37 份独立 CSS 经 PostCSS 解析及令牌核对，37 份 HTML 标签平衡与 ID 唯一，3 份 Python 测试 AST 与两份浏览器脚本语法检查通过 |
| 浏览器 1440 / 390 | 沙箱阻止启动，0 张截图，实际视觉与像素几何待验收 |

对 279 份基线文件逐一核对 SHA-256，唯一变化的既有源文件为 `site-src/redesign/demo-runtime.js`。74 份 H 段皮肤为新增。基线覆盖现有 `site-src`、演示规格与来源动效文件，外框和原有皮肤通过哈希核对。

### 未完成事项与时间边界

37 个指定条目的皮肤与自动测试已经完成。1440 / 390 截图、真实渲染的四边 16px 与 55–66% 主体比例验收、看图后的逐条视觉复核仍待执行。

本轮仅尝试 Playwright 自带的 `chrome-headless-shell`，使用独立临时配置目录。启动阶段收到 `MachPortRendezvousServer ... Permission denied (1100)`，进程在渲染前退出。按本轮约束跳过浏览器验证。证据保存在 `output/demo-redesign/H/headless-attempt.log`，构建、测试、CSS / HTML 校核、基线摘要与完成清单位于同目录。

工作起点为本地时间 03:32:16，24 分钟工作截止为 03:56:16，26 分钟进程截止为 03:58:16。`output/demo-redesign/H/run.py` 在工作截止后拒绝启动新任务，并在进程截止时强制终止本轮构建与测试子进程组。

本段最终复核于本地时间 03:52:32 完成，工作耗时约 20.28 分钟，处于 24 分钟工作窗口内。

## 测试同步

2026-11-13，本轮按 `/tmp/demo_full_tests.log` 逐项复现并同步 11 个旧测试。基线定向运行共 24 项，复现 11 项失败。最终完整套件共 147 项，全部通过。

### 逐项判断与处理

| 旧测试 | 失败原因与意图判断 | 处理方式 |
|---|---|---|
| `test_button_background_values_are_distinct_after_token_resolution` | 按下规则已拆入独立无障碍资产，按钮皮肤使用 `--ds-*`，旧测试仅从 `demo-ui.css` 获取规则及字面令牌。现有三类按钮的默认、悬停、按下颜色各自不同，满足意图。 | 按来源、规格、kind、skin、无障碍的顺序读取资产，递归解析 `--demo-*` 到 `--ds-*` 的颜色别名。对三类按钮分别断言三态颜色互异、按下的规范值，以及固定态、真实伪类、预览属性颜色一致。 |
| `test_danger_palette_is_canonical` | 危险按下规则迁至 `demo-accessibility.css`，按钮皮肤使用新令牌和规范红色色值，满足统一危险色意图。 | 递归扫描皮肤及公共 CSS，继续排查旧红色。断言危险色三档为 `#B91C1C`、`#991B1B`、`#7F1D1D`，并核对实际按钮皮肤的默认、悬停、按下声明。 |
| `test_interactive_borders_use_control_token_in_every_demo_family` | 控件边框补丁已从五类 `demo-<kind>.css` 拆出。共享边框 `#868E9C` 在新舞台、白色承托面和浅底上的对比度均达到 3∶1，满足意图。 | 从独立无障碍资产校验控件集合、`!important` 优先级、复选框、单选框及两类 range 轨道的真实边框声明。五类样式链分别计算对比度，并检查所有生成演示模板均引用公共规格和无障碍资产，覆盖五个 kind。 |
| `test_operation_hints_are_readable` | 旧测试要求分族 CSS 内的 13px 补丁，当前规格 §9 明确提示下限为 12px，统一提示由 `.ds-hint` 提供。现有 12px 提示与白色底的对比度满足 4.5∶1。 | 对 UI、动效、指南三类读取完整样式链，定位最终 `.demo-root.ds-stage .ds-hint`，断言字号至少 12px，解析真实前景与背景后计算至少 4.5∶1，并保留旧提示类的补丁覆盖检查。 |
| `test_pressed_and_real_active_have_independent_colors` | 真实按下规则迁入独立无障碍资产，按钮皮肤提供独立真实态与固定态，按下变换按规格使用 0.98，满足颜色分档意图。 | 分别检查 `states.css`、无障碍资产和按钮皮肤中的真实及固定按下钩子与 active 令牌，按当前规格校验变换。具体三态色值由上述颜色解析测试逐一核对。 |
| `test_static_thumbnails_have_small_metadata_and_a_fallback` | 搜索缩略图已按新方向改为 64×48，旧测试仍锁定 56×56。轻量元数据和未知类型首字回退机制均满足原意图。 | 保留 192 条索引的类型及元数据体积限制，读取 `.result-thumb` 的实际尺寸并断言 64×48、4∶3。用 Node 执行生产缩略图函数，检查五类有效元数据、缺失/null/未知元数据回退、首字与转义。 |
| `test_gallery_zoom_is_shadow_local_and_stage_can_grow` | 栏目预览改为实际可用宽度排版，统一舞台使用 `75cqi` 首选最小高度并允许增高。旧测试仍锁定外层 240px、旧 padding 及 312px 画布缩放公式。当前结构满足宽度约束与文字可读性意图。 | 校验外层自动高度、可见溢出及操作区留白，五类统一舞台的最小高度、自动比例、自动高度、可见溢出和文字换行。确认实际运行函数仅处理 `.mini-stage`，采用 host/stage 可用宽度并使用 `zoom=1`。 |
| `test_touch_targets_use_layout_space_and_keep_inline_prose_links` | 点击区补丁已拆出，旧文件读取失效。核对发现角色按钮缺少统一 44px 高度约束，44px 按钮经 0.98 按下变换后仅剩 43.12px，这两处需要 CSS 修复。 | 仅修改 `site-src/redesign/demo-accessibility.css`。在原触屏/窄屏媒体条件内将角色按钮纳入 44px 高度约束，提供 inline-flex 布局与 44px 最小宽度，真实按下和固定按下保持完整命中矩形。轮播箭头保留 `translateY(-50%)` 定位。测试继续检查正文内联链接例外、轮播操作分行及点击区，并补充角色按钮和按下变换断言。 |
| `test_gallery_runtime_width_scale_height_limit_and_repeat_stability` | 旧运行时测试假定固定 312px 画布和固定高度压缩。新结构通过实际宽度重排和自动增高保持字号，当前实现满足防越界、复测稳定及可读性意图。 | 在 Node VM 中执行真实 `fitGallery()`。覆盖 140/180/336/436px、四档内容高度、每种宽度重复四次、往返 resize、初始 host 零宽、stage 零宽及正文无 mini-stage 的分支。断言实际布局宽度、`zoom=1`、禁止 flex 收缩及居中样式。自动增高和可见溢出另由对应 CSS 测试约束。 |
| `test_hover_card_stage_reserves_clearance_in_both_entry_points` | 公共 272px 舞台留白迁入无障碍资产，独立皮肤另以 408/416px 面板承载预览。现有结构满足预览留白意图。 | 从正确资产校验舞台留白、对齐与规则顺序。读取皮肤的宽窄两档面板高度、浮层 top、112px 图片、图片间距和 padding，计入两行文字、标题间距及边框后断言浮层下方至少预留 12px。检查动效详情、组件卡片和动效画廊三个入口均引用对应皮肤与无障碍资产。 |
| `test_skill_and_component_small_text_contrast` | 旧测试从分族文件读取无障碍补丁，并将技能标签视为旧暗底。新技能皮肤的高优先级紫色标签置于浅底，浮动标签与 chip 也使用新承托面，现有对比度满足意图。 | 使用真实皮肤选择器和新背景，递归解析颜色，检查技能标签、浮动标签、字数计数、chip 删除按钮均达到 4.5∶1，同时覆盖浮动标签聚焦态和 chip 删除按钮悬停态。 |

### 验证记录

测试辅助模块 `tests/demo_css.py` 统一处理选择器列表中的函数内逗号、同一选择器声明的 `!important` 优先级和颜色别名。断言定位明确的公共规则与实际皮肤选择器，验证采用静态 CSS 检查和 Node 运行时执行。

- 11 个失败测试的方法全部保留，完整套件仍为 147 项。
- 点击区回归断言先运行并复现失败，修复后定向 24 项通过。
- 对 11 项同步测试分别进行进程内故障注入，颜色合并、危险色漂移、低对比度边框、11px 提示、按下规则缺失、43px 点击区、固定高度裁切、缩略图错误回退、画廊缩小、预览留白不足及低对比度小字均被对应断言检出，共 11/11。
- 最后完整验证使用用户指定命令，147 项通过，耗时 27.250 秒，退出码 0。口语搜索前 3 条命中 62/62。

```text
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -p 'test_*.py'
Ran 147 tests in 27.250s
OK
```

完整套件内既有 `test_all_content_acceptance_and_aliases_are_frozen` 使用只读 `git show HEAD:site-src/content/...` 进行内容冻结校验，该调用随用户指定的完整测试命令执行。

## 无头测试修复

2026-11-13。本轮依据 `demo_redesign_headless_fail.log` 的 24 项失败及 `batch6_fail.log` 的悬停预览越界记录实施静态修复。工作起点为北京时间 04:33:00，工作截止为 04:44:00，进程截止为 04:45:00。此次检查限于源码、内存中的模板输出、CSS 解析及断言执行，渲染几何与实际触屏结果待后续无头回归确认。

### 逐项原因与处理

| 序号 | 日志中的失败 | 原因 | 处理 |
|---|---|---|---|
| 1 | 1440，按钮页样式链，scope 1 | `requireStates` 被应用于按钮页所有相关缩略演示，按压回弹缩略演示没有状态切换器。 | 状态样式的必需条件限定到交互正文，已有状态样式仍必须位于 a11y 之后。 |
| 2 | 1440，轮播页样式链，scope 1 | `media-carousel` 使用 `_kind-motion.css`，测试却无条件要求独立皮肤。 | 按实际皮肤文件检查必需引用，正文样板仍要求独立皮肤，相关演示保留 kind 层校验。 |
| 3 | 1440，组件状态页样式链，scope 0 | `/state/` 子串匹配将 `ui-states.css` 皮肤误归类为状态样式。 | 优先使用运行时的明确 sheet kind，文件回退仅将文件名 `states.css` 识别为状态层。 |
| 4 | 1440，导航栏页样式链，scope 1 | `shrink-header` 使用类型级皮肤，测试强制要求独立文件。 | 根据实际独立皮肤清单断言引用及顺序。 |
| 5 | 1440，表格页样式链，scope 3 | `mobile-drag` 使用类型级皮肤，独立皮肤断言不适用。 | 校验实际存在的独立皮肤及完整样式链。 |
| 6 | 1440，固定表头页样式链，scope 3 | 同一 `mobile-drag` 相关演示触发独立皮肤误判。 | 同第 5 项，逐格按自身 kind、slug 检查。 |
| 7 | 1440，列宽调整页样式链，scope 3 | 同一 `mobile-drag` 相关演示触发独立皮肤误判。 | 同第 5 项，保留真实缺项和乱序失败。 |
| 8 | 1440，表格编辑页样式链，scope 3 | 同一 `mobile-drag` 相关演示触发独立皮肤误判。 | 同第 5 项，保留已有独立皮肤引用检查。 |
| 9 | 1440，可排序表格页样式链，scope 3 | 同一 `mobile-drag` 相关演示触发独立皮肤误判。 | 同第 5 项，检查类型级皮肤的顺序。 |
| 10 | 1440，加载更多页样式链，scope 3 | 同一 `mobile-drag` 相关演示触发独立皮肤误判。 | 同第 5 项，继续检查 source、spec、kind、a11y 链。 |
| 11 | 1440，组件画廊样式链，scope 31 | `ui-states.css` 同样被子串匹配误归类。 | 使用明确 kind 与精确文件名分类，要求链条严格相等，重复或乱序也会失败。 |
| 12 | 390，按钮页访问与布局审计 | 137px 内层格宽中，morph 的 136px、magnetic 的 150px、ripple 的 160px 来源最小宽度超过面板可用宽度，ripple 继续推高外层 scrollWidth。 | 三份独立皮肤增加 `max-width:240px` 容器查询，解除来源最小宽度，约束最大宽度并允许文本换行，magnetic 两侧额外预留 8px 移动空间。 |
| 13 | 390，按钮页行为审计 | 行为检查重复审计相同布局，复现第 12 项的五条溢出记录。 | 使用同一组三份皮肤修复，保留行为后的布局复查。 |
| 14 | 390，上浮卡片访问与布局审计 | 卡片上浮 7px 后，原约 17px 顶距降到日志中的 10px。 | 正文 lift 舞台顶部使用 `max(24px,var(--ds-stage-inset))`，覆盖共享顶部 padding，预留上浮行程及至少 16px 可见间距。 |
| 15 | 390，上浮卡片点按切换 | 精确矩阵比较读取了 `-6.67423px` 的过渡中间值，初始快照还可能带入焦点或悬停状态。 | 快照前移出鼠标并清除卡片焦点，强制样式结算后等待有限动画的 `finished`，继续严格检查变换发生与完全恢复，并新增 `aria-pressed` 的 false → true → false 断言。 |
| 16 | 390，轮播页样式链，scope 1 | 与第 2 项相同，类型级皮肤被要求附带独立皮肤。 | 按实际皮肤文件逐格检查，保留主样板独立皮肤要求。 |
| 17 | 390，组件状态页样式链，scope 0 | 与第 3 项相同，`ui-states.css` 被误识别。 | 精确分类并严格校验 a11y 与 states 的顺序。 |
| 18 | 390，导航栏页样式链，scope 1 | 与第 4 项相同，`shrink-header` 使用类型级皮肤。 | 检查已有独立文件引用及实际样式链。 |
| 19 | 390，表格页样式链，scope 3 | 与第 5 项相同，`mobile-drag` 无对应独立皮肤文件。 | 逐格检查文件存在性，保留缺项断言。 |
| 20 | 390，固定表头页样式链，scope 3 | 与第 6 项相同。 | 使用同一逐格样式链校验。 |
| 21 | 390，列宽调整页样式链，scope 3 | 与第 7 项相同。 | 使用同一逐格样式链校验。 |
| 22 | 390，表格编辑页样式链，scope 3 | 与第 8 项相同。 | 使用同一逐格样式链校验。 |
| 23 | 390，可排序表格页样式链，scope 3 | 与第 9 项相同。 | 使用同一逐格样式链校验。 |
| 24 | 390，加载更多页样式链，scope 3 | 与第 10 项相同。 | 使用同一逐格样式链校验。 |

`batch6_fail.log` 的补充问题来自预览弹层的绝对定位。旧皮肤使用固定 `top:176px/188px` 和固定面板最小高度，窄画廊内文字换行会增加弹层高度，却未参与面板高度计算。`motion-component-hover-preview.css` 将弹层改为 `position:relative`、`inset:auto`、100% 宽度和正常流布局，弹层与触发区保留 16px 间距。面板保留宽档 24px、窄档 16px 内边距，使展开内容随面板增高并计入舞台及 `.mini-stage` 高度。原显示、焦点、触屏和预览状态钩子沿用。

对应静态测试改为检查正常流定位、自动 inset、完整宽度、禁止收缩及两档至少 16px 的面板内边距，继续校验三个入口的皮肤引用。原无头弹层四边与底部 16px 断言保留。

### 样式注入核对

源码 `demo-runtime.js` 已按 source → spec → kind（适用时）→ skin（适用时）→ a11y → states（适用时）装载。内存中生成 192 个详情页及五个栏目页，检查 464 个演示 scope，其中 279 处引用独立皮肤。相关演示已有独立皮肤时，其引用均存在。此次源码注入链核对通过，修复落在测试的分类与适用范围。

`verifyChains` 新增 scope 的 kind 与 interactive 元数据，依据 `site-src/redesign/demo-skins/<kind>-<slug>.css` 的实际文件存在性要求正确皮肤，保留按钮和输入框正文状态层要求，并用严格数组比较检查完整顺序。无头脚本的宽度集合补齐为 1440、768、390。

### 静态验证记录

- 五份修改后的皮肤通过 PostCSS 语法解析。
- 修改后的无头脚本通过 `node --check`，Python 文件通过 AST 解析。
- 内存中的 197 个页面、464 个演示样式链校验通过，源码运行时确认 states 位于 a11y 之后。
- 五类故障注入均被拒绝，分别为遗漏已有独立皮肤、交换 a11y 与 states、删除正文 states、重复 source、替换成错误皮肤。
- 直接执行更新后的悬停预览静态断言，通过源码 CSS 和三个入口的只读 HTML 校验，跳过含构建调用的 `setUpClass`。
- 最终复核对内存生成的全部 127 份 CSS 完成 PostCSS 解析。额外注入绝对定位回退和 8px 面板内边距两类故障，悬停预览静态断言均检出失败。
- 本轮修改涉及五份独立皮肤、两个测试文件及本节文档。实际三宽渲染、无头交互与截图验收待后续执行。

最终静态复核于北京时间 04:39:58 完成，工作耗时约 7 分钟，处于 11 分钟工作窗口内。

## 390 画廊缩略格溢出

2026-11-13。依据 `dr_fail2.log`，处理 basics、components、interactions 画廊中的 11 个演示。日志中的外层 stage 约 169px，内层 canvas 或 stage 约 137px，带 16px 内边距与边框的面板内部约 103px。新增规则全部置于 `@container demo-stage (max-width:240px)` 内。独立皮肤沿用原文件，其余演示在既有 kind 皮肤中使用演示专属选择器。大于 240px 的容器继续使用原有样式。

| 演示 | 溢出元素与约束 | 窄格处理 | 样式文件 |
|---|---|---|---|
| badge-dot | `.bd-demo` 横排包含两个 56px 按钮、32px gap 与两侧 8px padding，超过面板内宽。数字角标还有 `right:-16px` 外伸及 content-box 尺寸。 | 每项占独立行，允许 flex 换行，gap 缩为 12px，按钮约束最大宽度，数字角标改为 `right:-4px` 和 border-box。 | `ui-badge-dot.css` |
| chart-morph | `.extra-chart-controls` 的双按钮内容宽度、水平 padding 与 gap 叠加，`.extra-chart` 五列各有标签最小宽度，另有四段 16px gap 和两侧 12px padding。 | 控制按钮允许换行并减小水平 padding，图表 gap 与水平 padding 均缩为 4px，柱列解除自动最小宽度，保留五列与原数据。 | `motion-chart-morph.css` |
| color | `.ds-color-field` 的 64px 色盘、16px gap、两侧 16px padding 与色值文本并排，超过约 103px 内宽。 | 色盘与色值纵向排列，gap 和 padding 缩为 8px，色盘允许随可用宽度收缩，面板 grid 使用 `minmax(0,1fr)`。 | `ui-color.css` |
| conditional-step | `.cond-demo` 来源宽度为 262px，`.cond-choice` 的两项标签及 16px gap、`.cond-steps` 的文字与 padding 仍保持单行。 | 演示宽度跟随容器，选项与步骤均允许换行，gap 缩为 8px，选项水平 padding 缩为 8px。保留企业步骤显隐钩子。 | `_kind-ui.css`，限定 `c-conditional-step` |
| cursor-object-follow | `.obj-stage` 内的 `.obj-card` 固定 150px，超过约 137px 的舞台宽度，grid 子项保留最小内容尺寸。 | 承载区设为可收缩的 100% 宽度，左右预留 8px，卡片使用 `min(150px,100%)` 并解除最小宽度。沿用指针旋转行为。 | `_kind-motion.css`，限定 `cursor-object-follow` |
| otp | 窄档 `.otp-row` 使用 `repeat(3,minmax(44px,1fr))`，三列最低 132px 加两段 8px gap，总计 148px。 | 改为两列 `minmax(0,1fr)`，六个输入框按原 DOM 顺序排列，自动跳格与粘贴逻辑沿用。 | `ui-otp.css` |
| radius-shadow | `.token-demo` 自动 grid 轨道与 flex 标签受 select 的固有内容宽度约束，阴影选项文字较长，叠加 `.elevation-frame` 和卡片内边距。 | grid 使用 `minmax(0,1fr)`，直接子项与标签解除最小宽度，select 跟随容器，控制标签逐行排布，控制 gap 与两层内边距缩为 8px。 | `_kind-token.css`，限定 `data-token="radius-shadow"` |
| spacing | `.token-demo` 自动 grid 轨道被间距方案 select 的长选项固有宽度撑大，继续扩大 `.space-frame` 与外层 shadow 根的 scrollWidth。 | grid 使用 `minmax(0,1fr)`，直接子项与标签解除最小宽度，select 使用 100% 宽度并允许收缩，面板 gap 缩为 12px。保留演示卡片的可变内外边距。 | `_kind-token.css`，限定 `data-token="spacing"` |
| table-reorder | `.tblre-wrap` 固定 262px，`.demo-tbl` 单元格使用 nowrap 与两侧 9px padding，自动表格布局的最小内容宽度继续撑开祖先。 | 外层 flex 容器与表格包装随容器收缩，表格使用 fixed 布局，单元格允许任意位置换行并将水平 padding 缩为 4px，拖动图标左 margin 归零。包装使用 visible，完整呈现换行后的内容。 | `_kind-ui.css`，限定 `c-table-reorder` |
| tabs | `.tabs` 的三个按钮具有文字最小宽度、两侧 12px padding 与 8px gap，单行布局超过面板内宽。 | tablist 允许换行，gap 缩为 4px，按钮使用可收缩的 44px flex basis、两侧 4px padding 和正常换行。保留角色、焦点顺序与切换钩子。 | `ui-tabs.css` |
| view-shared | `.shared-chip` 收起态固定 140px 且绝对定位 `left:8px`，在约 137px 的 `.shared-box` 内延伸至 148px。展开态还有 220px 宽度与 `left:32px`。 | 收起态宽度扣除两侧各 8px，展开态改用 16px 左偏移并扣除两侧各 16px，内部文字约束到按钮宽度。保留展开、收起及位置尺寸过渡。 | `_kind-motion.css`，限定 `view-shared` |

### 本轮验证

- `test_redesign_tokens.py` 的 20 项既有静态测试全部通过，退出码 0。
- 8 份修改后的 CSS 通过 PostCSS 解析，新增的 36 条规则全部位于 240px 容器查询内，未新增隐藏或裁切溢出的声明。
- 在内存中执行现有 `load_entries` 和 `demos.markup`，核对全部 11 个目标演示的皮肤引用及 kind、id、data-token、data-effect 定位。独立皮肤与类型皮肤保持原有注入路径。
- 本轮验证限于源码与静态断言。按任务限制未启动浏览器，未执行依赖浏览器及 dist 的无头脚本，实际 `scrollWidth/clientWidth` 渲染验收待后续回归确认。
- 本轮修改仅涉及上述 8 份皮肤及本节文档，文字、HTML 与行为脚本保持原稿。工作于北京时间 05:31:59 开始，全部检查与记录在 10 分钟窗口内完成。

## I1 段：剩余 UI 组件与数据图表独立皮肤

2026-11-13，本段按清单顺序完成 10 个 UI 演示与 5 个 guide 图表，共新增 15 对独立 CSS / HTML。修改范围为 `site-src/redesign/demo-skins/` 的下列新文件、本节实施记录及 `output/demo-redesign/I1/` 验证材料。

| 类型 | 完成的 slug | 视觉处理 |
|---|---|---|
| ui | `advanced-settings` | 项目通知配置；常驻字段标签、基础地址与请求参数；高级设置收起和展开沿用原逻辑。 |
| ui | `conditional-step` | 协作账户申请；两项账户选择、当前步骤和按条件追加的企业认证，隐藏步骤不占位。 |
| ui | `context-options` | 年度订阅发票；明确订单金额、企业抬头及电子发票选项，关联字段沿用原显示条件。 |
| ui | `infinite-scroll` | 带中文成员、项目与时间的更新记录；滚动列表 240px 高，追加批次及结束提示保留。 |
| ui | `inline-edit` | 官网改版交付计划；标题、负责人及日期分层，文字和编辑输入框保持相同的主体尺寸。 |
| ui | `progress` | 40 MB 项目资料归档；14 MB / 35% 数值、淡紫轨道与紫色填充，增加进度条可访问值。 |
| ui | `table-reorder` | 三位中文成员的项目排期；固定表格布局、可换行单元格、拖动高亮和抓取提示。 |
| ui | `textarea` | 项目交付备注；常驻标签、80 字计数、中文交付示例和可调整高度的文本域。 |
| ui | `virtual-list` | 官网改版同步日志；日期、业务上下文和日志级别分层，严格保留 26px 行高及原 136px 滚动窗口。 |
| ui | `auto-save` | 项目会议纪要；常驻标签、会议议题及编辑 / 保存中 / 已保存状态，警告和成功使用语义色。 |
| guide | `bar` | 四个真实渠道类别；共同零基线、0 / 50 / 100 轴标、柱顶数值与对应图例，两状态分别使用原 42 / 68 / 54 / 82 和 25 / 40 / 32 / 48。 |
| guide | `donut` | 访问来源环图；100% 中心总量、三类占比明细和色彩图例，两状态分别为 45 / 35 / 20 与 35 / 40 / 25。 |
| guide | `heatmap` | 四个中文时段 × 周一至周日；28 格全部显示 `data-level` 对应等级、0—4 图例和原悬停数值，切换后随原数据更新。 |
| guide | `line` | 六日官网访问趋势；灰阶坐标、日期和数值，极淡网格，保留原两组折线点位；网格基线与原数值口径对应。 |
| guide | `stacked` | 三类渠道构成；分段百分比、合计 100 次、0 / 50 / 100 轴标与对应图例，两状态数值及分段宽度一致。 |

### 规格与行为边界

所有新皮肤通过 `width:min(100%,var(--ds-subject-width))` 接入既有舞台规格，没有修改公共 `demo-spec.css`。按当前公开 clamp 计算，960px 舞台主体宽 560px，占舞台 58.33%；358px 舞台主体宽 320px，水平净距各 19px。239 / 220 / 200px 画廊宿主增加独立容器规则，以可收缩的网格、换行内容和较小内部留白适配；计算净距各 17px。上述数值属于源码计算，不能代替实际浏览器几何验收。

UI 的原 `.ctl` 仍是 `.canvas` 的直接子项，提示文本与胶囊生成机制未改变。原 ID、class、data、ARIA 状态钩子和隐藏节点保留。表格允许内容换行，不用裁切掩盖溢出；44px 触屏控件下限由独立皮肤与现有公共规格共同维持。虚拟列表行高与脚本定位耦合，因此保留 26px 行高；列表行本身不是点击控件。

图表轴标、图例、明细数值均使用 12—13px 灰阶文字；中心总量与卡片标题使用 16px。新 CSS 颜色全部引用现有 `--ds-*` token，系列使用紫色阶与 `--ds-chart-2`；语义状态沿用 warning / success。环图、堆叠图与柱图的切换态颜色经过独立选择器覆盖，避免回落到旧配色。减少动态规则保留 `data-demo-motion-once` / `data-demo-motion-step` 门控，显示当前完整数据。

来源 UI HTML、`guide_pages.py`、`guides.js`、`demos.py`、`demo-runtime.js`、公共舞台规格和无障碍样式均未由本段修改。演示业务样例放在覆盖 HTML 内，条目定义、提示词和验收要求保持原文件。未新增图片。

### 验证结果

- 按要求运行 `PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_demo_audit tests.test_redesign_tokens`，21 项通过，退出码 0；未改测试或断言。
- 在内存中调用 `load_entries`、`demos.markup` 和 `smoke_fixture`，生成独立验证材料，不执行网站构建、不读写 dist。194 份演示通过现有 Node DOM 模型初始化。
- 追加执行 10 个 UI 的来源交互与五个图表的双状态检查：高级字段保值、条件步骤、关联发票选项、无限滚动两次追加与结束、标题保存和取消、35% 进度、整列拖动对应、80 字上限、26px 虚拟定位、700 / 400ms 自动保存，以及图表两组数值和图例均通过。
- 15 份覆盖 HTML 通过标签解析和 ID 唯一校核；15 份 CSS 通过令牌引用、字号、括号 / 引号配对检查，并核对独立皮肤注入。未安装 CSS 解析依赖，因此不将此项称为完整 CSS 语法或浏览器验证。
- 可复核材料：`output/demo-redesign/I1/source-verification.json`、`verify-source.py`、`interactions.cjs`、`smoke-fixture.json` 及测试日志。

### 未做到的与时间边界

清单内 15 个 slug 均已完成独立皮肤，没有跳过项。1440 / 1024 / 768 / 390 及窄画廊的实际渲染、横向溢出与四边像素净距、减弱动态截图仍由执行者在后续构建后验收。本段遵守禁令，未运行 `build_site.py`，未修改 dist，未执行 Git 操作，未启动端口、浏览器或应用窗口。

本段从北京时间 11:42:44 开始，24 分钟工作截止为 12:06:44，26 分钟进程截止为 12:08:44。验证命令经独立 deadline 包装器执行，工作截止后拒绝启动新任务，并对已启动子进程组设置不超过工作截止的强制终止超时。没有后台常驻进程。

检测到并行工作对 `site-src/redesign/templates.py`、`tests/test_site_build.py` 与 `docs/design-system.md` 的修改；它们未由本段写入或回退，已在验证记录中单列。

本段最终校核于北京时间 11:55:06（UTC 03:55:06）完成，耗时约 12.37 分钟，位于 24 分钟工作窗口内。完成清单与文件哈希见 `output/demo-redesign/I1/completion.json`。

## 方案 D：使用卡变成提示词卡

2026-11-13，按已选定的 `copy-prompt-options/site/components/cmdk/option-d.html` 及用户补充规格，在当前站点结构中统一实现全部 192 个条目。默认外观沿用 PRD 第 15 节的黑白灰、链接蓝及墨黑主按钮；仅复制成功后的两秒反馈按本方案使用 `#6D28D9`。

### 实施文件与行为

- `site-src/redesign/templates.py`：新增共用 `use_card()`，由现有条目入口 `detail()` 调用。每页只输出一张提示词卡，源码位置在全部演示之后、「它怎么动」和使用说明之前；桌面将其固定到现有右栏，移动端按相同阅读顺序显示。卡头为「提示词」及内联「复制」，卡体保留提示词全文；验收条数来自当前条目的真实列表，零条时省略提示。验收折叠区、逐条复制、复制英文名和复制本页链接保留。主栏原 `.prompt-box` 重复块移除，「新做一个」仍在使用说明之后，原第二演示提示词进入同一张卡。隐藏的 `#copy-prompt` 和 `copy_payload()` 内容协议保持原样。
- `site-src/redesign/site.css`：保留当前 1376px 外框、桌面固定右栏及 1024px 断点。卡片圆角 16px、内块和按钮圆角 8px、卡内留白 16px，按钮和提示词框相隔 12px，次操作间隔 8px。桌面整卡限制在视口内，全文区域独立滚动，并设置 `overscroll-behavior:contain`；移动端展示完整自然高度。相关复制操作与折叠入口至少 44px 高。复制成功时整卡紫底白字、按钮反白，白字对紫底的 WCAG 对比度超过 7.1:1；焦点环保持可辨识，减弱动态时无过渡。
- `site-src/redesign/site.js`：沿用现有剪贴板写入和回退机制，仅在写入成功后同步卡片、内联按钮及底栏按钮的状态，文字为「✓ 已复制」，2000ms 后复原，重复复制重置同一个反馈计时器。通过现有 `aria-live` 播报「已复制」。移动端使用 `IntersectionObserver`，提示词卡进入视口即设置底栏 `hidden` 和 `inert`，离开后恢复；同步处理尺寸变化、断点切换、缺少观察器时的滚动回退，以及隐藏底栏前的焦点转移。

### 测试同步

- `tests/test_site_build.py`、`tests/test_editorial_content.py`：旧提示词块及其嵌套结构断言改为唯一提示词卡、卡内完整原文、真实验收条数、主栏无重复块，并继续精确验证两版复制载荷及验收要求。
- `tests/test_audit_fix_batch2.py`、`tests/test_audit_fix_batch3.py`、`tests/test_redesign_tokens.py`：同步固定卡、独立滚动区域、卡头排版、成功配色及隐藏底栏结构。原内容冻结检查由调用 `git show` 改为本次修改前冻结的五个内容 JSON 的完整规范化 SHA-256 指纹，同时精确校验文件集合，遵守本次禁止 Git 操作的约束。
- 新增 `tests/test_prompt_card_d.py` 和 `tests/prompt_card_d_runtime.cjs`：覆盖全部 192 页的单卡结构、完整提示词、源码及移动端排序、验收条数和复制载荷；验证零验收条目、尺寸与圆角约束、紫白对比度、焦点环、减弱动态，以及实际生产 JavaScript 的复制成功、失败和回退、两个入口同步、两秒恢复、观察器显隐、`inert`、焦点转移及断点切换。Node 测试使用受控 DOM 模型，不启动浏览器。
- `tests/audit_fix_batch3_headless.cjs`、`tests/audit_fix_batch5_headless.cjs`：更新卡头复制按钮选择器，补充桌面全文与卡高、主栏无重复、移动排序、复制载荷、整卡紫色、减弱动态及底栏不可聚焦等断言。仅同步脚本并检查语法，本次未运行浏览器审计。
- 完整单测暴露的既有测试漂移一并按现有实现同步：`tests/test_design_system_page.py` 的当前页自链接精确断言改为 `./`，目标解析校验保留；`tests/test_redesign_javascript.py` 为动效指示器提供不等宽标签尺寸，替换旧的百分比假设，同时精确断言两次切换的位置、宽高和选中状态；`tests/test_site_build.py` 将独立皮肤精确计数更新为既有 I1 完成后的 127 个独立样例、59 个通用皮肤及 6 个保留材质条目，并核验 I1 的 15 个明确 slug，总数仍严格等于 192。未删测试或降低验收阈值。

### 验证与时间边界

- 运行 `PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/build_site.py`：退出码 0，生成 218 个页面、192 个统一条目页；构建产物同步到 `dist/` 及现有构建输出。
- 运行 `PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -p 'test_*.py'`：159 项全部通过，退出码 0。
- 修改前后核对 257 个皮肤文件及 5 个内容 JSON 的 SHA-256：262 个文件均未变化，皮肤文件集合也无增删。生产 JavaScript 和三份已更新 CJS 脚本通过 `node --check`。
- 本次开始于北京时间 12:19:05，24 分钟工作截止为 12:43:05，26 分钟进程上限为 12:45:05。构建及完整单测通过独立进程组运行，超时包装器以更早的 24 分钟工作截止为强制终止边界，没有后台常驻进程。
- 未执行 Git 操作、未启动端口、浏览器或任何应用窗口。实际浏览器渲染、几何与视觉验收未运行，不能由源码与 Node 模型检查替代。
- 可复核记录：`output/prompt-card-d/build.log`、`unittest.log`、`before-sha256.json` 和 `completion.json`。
