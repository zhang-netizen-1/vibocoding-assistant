# 演示重做 · 进度（供下一段接续）

更新：2026-11-12 23:40 前后（Asia/Shanghai）

## 已完成（第 1 段）
- 规格 `demo-spec.md` v1 已写好：box `/workspace/bench/demo-redesign/demo-spec.md`，Mac `~/Downloads/设计意图测评台/demo-redesign-work/demo-spec.md`。worktree 建好后复制到 `docs/demo-spec.md`。
- 图片库：17 张 × 2 种宽度（640/1280）webp，共 2.1MB，单张都不超过 183KB。位置 `~/Downloads/设计意图测评台/demo-redesign-work/demo-assets/`，含 `manifest.json`（来源路径、选用理由、主色）。之后复制到 `site-src/demo-assets/`。
  - 来源：`~/Downloads/晚风视频生成资料/100+3D建模场景图/古风` 9 张、`/现代` 6 张、`~/Pictures/下载图片` 2 张（宫崎骏风插画）。全部为 AI/3D 生成的场景，没有真人。
  - 排除：`封面图/封面素材汇总-拍摄`（真人模特商拍）、`封面素材汇总- AI`（以人物为主）、`游戏素材`（第三方品牌美术）、作品集、截图等。另外两张（红门、金色城市）实际是分镜稿，已删。
  - 缺口：没有产品图、头像、纯抽象或 UI 类素材，按规格用渐变代替；头像用字母圆形。
  - 图库总览：box `/workspace/bench/demo-redesign/image-library-sheet.jpg`。
- 只读调研（Codex）已完成：`~/Downloads/设计意图测评台/demo-redesign-work/impl-plan.md`（56KB）。要点：
  - `demo-{kind}.css` 里已经合并了无障碍补丁，要拆开才能排对层叠顺序。
  - `SHADOW_BASE`、无障碍补丁、外层 `.mini-stage` 里有旧的舞台尺寸和裁切规则，会盖掉新令牌。
  - UI 演示没有 `demo.key`，皮肤要按 slug 加 kind 来区分；`color`、`sidebar`、`accordion` 三个 slug 有重名。
  - 搜索缩略图现在只是 56×56 的栏目符号。
  - 预览方式：在临时目录里建一个指向 dist 的软链接，名字叫 vibocoding-assistant，再用 `python3 -m http.server 4181` 提供服务。
  - Playwright：用 `NODE_PATH=/Users/zhiguang/.npm/_npx/e41f203b7505f1fb/node_modules`，或 `~/Downloads/Kreator/node_modules`（只读引用）。
- 改前截图已完成：13 个样板，1440 和 390 两种宽度，共 26 张，在 `demo-redesign-work/shots/before/`，截自 4180 上的 audit-fixes 构建，脚本是 `shoot.cjs <base> <out>`。总览图在 box `/workspace/bench/demo-redesign/before_sheet_1440.jpg`。注意 AI 条目的路径是 `ai/skills/<slug>/`。
- Codex A 段任务说明已写好：`demo-redesign-work/codex_brief_A.md`（公共层，加上 button、input、component-lift、view-crossfade 四个样板）。

## 样板（13 个，第 2 段做）
button、input、component-lift、view-crossfade、modal、tooltip、scroll-reveal、grid（basics）、skeleton、carousel（图片多）、color（basics token）、dashboard（scenarios）、frontend-design（ai）。

## 下一段要做
1. 检查 `~/Downloads/vibocoding-audit-fix` 的 git log 里有没有 'audit-fixes final'。到 23:40 为止最新提交是 09fb34e「走查修复第 6 批」，工作区还有未提交改动，说明还没做完。如果到 03:00 还没有，就从最新的干净提交拉分支。
2. `git -C ~/Downloads/vibocoding知识梳理 worktree add ~/Downloads/vibocoding-demo-redesign -b demo-redesign audit-fixes`
3. 复制 demo-spec.md 到 docs/，demo-assets 到 site-src/demo-assets/，本文件到 docs/demo-redesign-progress.md，提交一次。
4. 给 Codex 跑 A 段：`cd ~/Downloads/vibocoding-demo-redesign && nohup perl -e 'alarm 2400; exec @ARGV' ~/.codex/plugins/.plugin-appserver/codex-cli/bin/codex exec -C "$PWD" -s workspace-write - < ~/Downloads/设计意图测评台/demo-redesign-work/codex_brief_A.md > ~/Downloads/设计意图测评台/demo-redesign-work/codex_log_A.txt 2>&1 &`（Mac 上没有 timeout 命令，用 perl alarm 限时）。之后的 B 段做 modal、tooltip、scroll-reveal、grid、skeleton、carousel；C 段做两个 color、dashboard、frontend-design；再往后按栏目铺开。原计划是按 impl-plan.md 给 Codex 下任务：先做 demo-spec.css、注入和皮肤机制，再做 13 个样板；每批由我提交（Codex 写不了 git index）。
5. 先截改前的图：用 audit-fixes 的构建，1440 和 390 两种宽度，每个样板一张。

## 第 2 段（11-13 00:06–00:45）
- caffeinate 已开（6 小时）。`/tmp/b4full.log` 的完整 batch4 **没通过**：1449 项检查里有 4 项失败，都是 `components/states/` 在触屏模式下（390、768、1023、1440 四种宽度）有 1 个点击区小于 44px。所以**没有**打「audit-fixes final」空提交。
- worktree `~/Downloads/vibocoding-demo-redesign`，分支 `demo-redesign`，从 audit-fixes 的 e6827c5 拉出。提交：
  - f5a50b2：规格、图片库、进度记录；
  - ffe689c：A 段，公共层（demo-spec.css、皮肤机制 demo-skins/<kind>-<slug>.css/.html、图片发布）和 4 个样板；
  - a2cf161：A 段返工，提示胶囊占位、卡片描边、输入框标签、点阵。
- Codex 的沙箱起不了无界面浏览器，截图和视觉审查都由执行者在沙箱外做。Codex 的实施记录在 `docs/demo-redesign-implementation.md`。
- 预览：`http://127.0.0.1:4181/vibocoding-assistant/`。服务目录是 `demo-redesign-work/preview4181`，里面的软链指向 worktree 的 dist，需要时用 `python3 -m http.server 4181` 重启。
- 全站检查（脚本 `allpages.cjs`，212 页，1440/768/390 三种宽度）：没有横向溢出，也没有 JS 报错。只有 6 个请求失败，都是 1440 宽最先加载的几页，原因是服务刚启动、加载撞车；那几个资源单独请求都返回 200。
- 改后截图：Mac `demo-redesign-work/shots/after-A/`，box `/workspace/bench/demo-redesign/after-A/`；改前截图在 box 的 `before/`。前后对比总览：box `contact_sheet_A_before_after.jpg`。

## 下一段：先修这些
1. **390 宽内容超出 4:3 舞台**：component-lift 和 view-crossfade 的卡片贴着或超出舞台上下边，提示胶囊被截掉。要按规格「放不下就增高」，或在手机上缩小主体。改完要在 390 宽量一遍每个样板的舞台和内容边界。
2. 按钮缺一张悬停、按下、聚焦状态的截图证据（目前只截了静止状态），去状态切换页 `components/states/` 补截。
3. 然后做 B 段：modal、tooltip、scroll-reveal、grid、skeleton、carousel。说明照 codex_brief_A.md 改写成 codex_brief_B.md，跑 Codex 时用 `perl alarm` 限 25 分钟。Codex 的沙箱不能截图。

## 第 3 段（00:39–01:12）
- audit-fixes：触屏模式下，组件状态里的「长按」态原本缩到 0.96，按钮高只剩 42.24px。改成用内阴影表示按下，不再缩小。完整 batch4 跑完，1449 项全部通过（日志 `/tmp/b4full2.log`）。已提交 `c72e4ee`「audit-fixes final (full batch4 passed)…」，并已合并进 demo-redesign（`663260c`）。
- demo-redesign 的 `1cf8f1c`：A 段精修，加上 B 段 6 个样板（modal、tooltip、scroll-reveal、grid、skeleton、carousel）。截图在 `shots/after-B/`（box 上是 `after-B/`）。总览图：box `contact_sheet_A2_before_after.jpg`、`contact_sheet_B_before_after.jpg`。
- 实测 1440 宽：舞台 725px（右侧是使用卡），承托面 343px，占 47%。按百分比达标了，看起来还是小。

## 下一段要做（按优先级）
1. 1440 宽主体再放大：承托面 `width: clamp(420px, 62%, 560px)`，标题 22–24、正文 16。或者把条目页演示区加宽（要和外框布局一起看，属于外框改动，先问他）。
2. grid 在 390 宽变成一长列很小的缩略图，页面非常长。手机上改成 2 列，最多显示 4 张。
3. scroll-reveal 上半部分空白太多：首屏就露出第一张卡，并补标题和正文。
4. 再做 C 段：两个 color、dashboard、frontend-design。frontend-design 现在是深色面板，要改成本规格的浅色。

## 第 4 段（01:07–01:45）
- e185c8c（Codex）：
  - 1440 宽的主体放大到 clamp(420px, 66%, 560px)，并换用大舞台字号；
  - 网格在手机上改成 2 列、最多 4 张；
  - 滚动显现的第一张卡在首屏就能看到；
  - C 段 4 个样板：basics/color、components/color、scenarios/dashboard、ai/skills/frontend-design（改成浅色）；
  - 五种类型级皮肤 `demo-skins/_kind-*.css`。
- 我的截图检查（执行者）：ui 和 motion 两种类型的皮肤会让提示胶囊压住内容（switch、tabs、toast、select、scroll-parallax、text-mask），390 宽尤其严重，所以先停用这两种。原稿在 `site-src/redesign/demo-skins-wip/`，现在的 `_kind-ui.css` 和 `_kind-motion.css` 里只剩一行注释。guide、token、skill-reference 三种保留。
- 公共层修复：带提示的 .canvas/.stage 底部留出 56px（demo-spec.css 第 53 行），提示胶囊不再压住内容。截图核对见 box `check_hintfix.jpg`。
- 全站 212 页 × 3 种宽度：没有 JS 报错。有 1 处横向溢出（1440 宽的 ai/skills/fixing-accessibility），是那次 site.css 没加载出来造成的，重测没有溢出。

## 演示清单（192 条）
- **单独重做（14 条）**：components/button、input、modal、tooltip、skeleton、carousel、color；interactions/component-lift、view-crossfade、scroll-reveal；basics/grid、basics/color；scenarios/dashboard；ai/skills/frontend-design。
- **类型级皮肤生效（约 35 条，以 implementation.md 的清单为准）**：guide、token、skill-reference 三种类型里没单独重做的条目，6 个视觉材质类演示（如 glass、brutalist）保留原来的风格。
- **只换上了统一舞台**（底色、点阵、提示胶囊、字号下限）：其余约 143 条 ui 和 motion 演示。
- **待做**：
  1. 修好 `_kind-ui.css` 和 `_kind-motion.css` 后恢复。要求是 .canvas 当承托面时，提示胶囊在承托面外、舞台左下角，不能和内容同行。
  2. 1440 宽下，提示胶囊应在舞台最底部，现在跟在内容下面。
  3. 按栏目逐条精修：components 的 ui 演示（约 62 条），interactions 的 motion 演示（约 74 条）。
- **做不到要求的**：暂时没有。

## 问用户
- 条目页的演示区要不要整体加宽？要加宽就得改外框布局，比如收窄或下移右侧的使用卡。现在 1440 宽下舞台只有 725px，靠放大舞台里的内容来弥补。

## 第 5 段（01:38–02:15）
- 8c65abd（D 段）：
  - 提示胶囊固定在舞台左下角，所有宽度都一样；带提示的 .canvas/.stage 撑满舞台高度，手机上底部留出 76px。
  - ui 和 motion 两类的类型皮肤修好并恢复，demo-skins-wip/ 已删除。
  - 抽了 37 条在 1440 和 390 下截图核对：没有重叠，也没有截断。改前改后对比图在 box：`contact_sheet_D1_kind.jpg` 到 `D4_kind.jpg`。
- **192 条现在的状态**：
  - 单独精修 14 条（见上文清单）；
  - 类型级皮肤 172 条，统一了舞台、承托面、按钮、输入框、标签、圆角、阴影和紫色强调色；
  - 6 个视觉材质类演示（basics/visual 下 minimal、editorial、organic 等）保留各自的风格。
- **E 段 Codex 正在跑**：02:07 启动，perl alarm 26 分钟，**约 02:33 结束**。说明在 `demo-redesign-work/codex_brief_E.md`，日志在 `codex_log_E.txt`。这一段逐条精修首页入口和各分组首条，共 13 项约 17 条：
  - components 下：states、card、toast、navbar、table、tabs、switch、select、hold-confirm；
  - scenarios/landing；
  - interactions 下：view-slide、view-curtain、media-wipe、media-blur、scroll-parallax、scroll-pin。
  - **下一段开头**：先确认 E 段已结束（`pgrep -f "codex exec -C"`），再用 `shoot3.cjs` 拍改后截图，存到 `shots/after4`，改前截图是 `shots/before3`。用 `mksheet.sh` 做对比图，审完再提交。
- 抽样里看到、还没处理的：
  - 390 下 scroll-pin 的上沿被截掉一点；
  - interactions/spec 是规范长页，不是演示，不用管；
  - 类型级皮肤只算统一，离「极致」还远，ui 演示尤其明显（比如按钮组和标签只是换了色）。
- 后面的安排：第 6 段（约 02:20–03:00）审 E 段并提交，然后继续 components 余下的 forms 和 feedback 分组。第 7 段（约 03:00–03:40）做 interactions 的 component、text、data、overlay 分组。最后一段（约 04:50–05:30）做完整验证：测试，全站页面在三种宽度下检查，旧链接跳转，口语别名命中。再做 16 组最佳改前改后对比，输出 `/workspace/bench/demo-redesign/morning_summary.jpg`。
