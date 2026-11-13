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

## 第 6 段（02:08–02:45）
- b4428f8（E 段）：16 条单独精修，审过改前改后截图后提交。对比图在 box：`contact_sheet_E1.jpg`、`contact_sheet_E2.jpg`，改后截图在 Mac `shots/after4`。
  - 16 条是：states、landing、card、toast、navbar、table、tabs、switch、select、hold-confirm、view-slide、view-curtain、media-wipe、media-blur、scroll-parallax、scroll-pin。
  - 动效类的纯色块都换成了图片库里的真图；表单类用的是真实场景文案（如「设置所在城市」「编辑偏好」），层级分明。
  - scroll-pin 在 390 下上沿被截的问题已不存在，截图里外框完整。
  - 小毛病：hold-confirm 和 states 在 390 下承托面离舞台上边太近（约 4px），以后统一处理。
- **单独精修累计 30 / 192**：A–C 的 14 条，加 E 的 16 条。其余 162 条中，156 条用的是类型级皮肤，6 条视觉风格演示保留原风格。
- **F 段 Codex 正在跑**：02:34 启动，perl alarm 26 分钟，约 03:00 结束。说明在 `codex_brief_F.md`，日志在 `codex_log_F.txt`。
  - 先做 components/forms：checkbox、radio、slider、otp、search、segmented、password-strength、tag-input、stepper、rating、upload、combobox、date、form；
  - 再做 feedback：alert、empty、loader、drawer、popover。
  - 改前截图已拍好，在 `shots/before5`。截图脚本是 `shoot5.cjs`（文件里已写死这 19 条）。
  - **下一段开头**：确认 F 段已结束，然后运行 `node shoot5.cjs http://127.0.0.1:4181/vibocoding-assistant/ shots/after5`，再用 `mksheet.sh` 生成对比图，审过后提交。
- 再往后：
  - components 还剩：navigation 的 sidebar、accordion、breadcrumb、pagination、steps、footer、dropdown、mega-menu、context-menu、cmdk；content 的 badge、chip、badge-dot、timeline、kpi、avatar、view-switch、card-link；tables 的其余条目；actions 的 split-button、fab、back-to-top。
  - interactions 的 component、text、data、overlay、mobile、cursor、background 分组。

## 第 7 段（02:35–03:10）
- 7105fd4（F 段）：19 条单独精修，审过改前改后截图后提交。对比图在 box：`contact_sheet_F1.jpg`、`contact_sheet_F2.jpg`，改后截图在 Mac `shots/after5`。
  - forms 14 条：checkbox、radio、slider、otp、search、segmented、password-strength、tag-input、stepper、rating、upload、combobox、date、form。
  - feedback 5 条：alert、empty、loader、drawer、popover。
  - 全部用了真实场景标题和说明（如「通知与登录设置」「选择工作室方案」「填写收货地址」），层级一致。
- **单独精修累计 49 / 192**。
- **G 段 Codex 正在跑**：03:02 启动，约 03:28 结束。说明在 `codex_brief_G.md`，日志在 `codex_log_G.txt`。
  - 第一项是全局修复：390 宽下主体离舞台四边至少 16px，解决之前离上边只有约 4px 的问题。
  - 然后精修 navigation 10 条、content 8 条、actions 3 条、tables 5 条，共 26 条。
  - 改前截图已拍好，在 `shots/before6`，脚本 `shoot6.cjs`，里面也包含 hold-confirm 和 states，用来核对间距修复。
  - **下一段开头**：确认 G 段已结束，运行 `node shoot6.cjs http://127.0.0.1:4181/vibocoding-assistant/ shots/after6`，再用 `mksheet.sh` 生成对比图，审过后提交。
- 剩余时间安排：
  - 03:30–04:10：审 G 段，然后跑 H 段。H 段做 interactions 的 component、text、data、overlay 分组。
  - 04:10–04:50：审 H 段；只在时间够时再跑 I 段（interactions 的 mobile、cursor、background、media、scroll，加 interactions/rules）。
  - **04:50–05:30 必须做完整验证**：
    - 跑全部测试；
    - 全站页面在 1440 / 768 / 390 三种宽度下检查溢出和报错（`allpages.cjs`）；
    - 189 个旧链接的跳转（`tests/test_old_anchors.py` 和相关 headless 测试）；
    - 口语别名命中（`tests/search_queries.cjs`）；
    - 生成 `/workspace/bench/demo-redesign/morning_summary.jpg`：挑 16 组最好的改前改后对比，4 列 × 8 行，每格是改前 1440 和改后 1440。

## 第 8 段（03:02–03:40）
- 2533faa（G 段）：
  - 全局修复：390 宽下主体离舞台四边至少 16px，实测上边最小 17px、两侧最小 19px。
  - 单独精修 26 条：navigation 10 条（cmdk、sidebar、accordion、breadcrumb、pagination、steps、dropdown、context-menu、mega-menu、footer），content 8 条（badge、chip、avatar、kpi、timeline、badge-dot、view-switch、card-link），actions 3 条（split-button、fab、back-to-top），tables 5 条（table-fixed、table-columns、table-edit、sortable-table、load-more）。
  - 审过改前改后截图，对比图在 box：`contact_sheet_G1.jpg` 到 `G3.jpg`。
- **单独精修累计 75 / 192**。components 栏目的 ui 演示基本做完，还剩 tables 里的 table-reorder、infinite-scroll、virtual-list，content 里的 carousel 早已完成。
- **⚠ 违规发现**：Codex 的 C、E、F、G 四段都调用过它自带的电脑操控工具 `cua_repl`（来自 `unified-computer-use` 和 `codex-app-tools` 插件）。G 段的验证报告直接写着 `"browser":"native Google Chrome via CUA"`，说明它驱动了用户的真实 Chrome，违反「只用无界面浏览器、不碰用户的 Chrome、不用 computer-use」。日志里只能看到 started/completed，看不到它具体做了什么。没有看到推送、发送一类的外部操作。
  - 处理：H 段起，启动 Codex 时用 `-c 'plugins."unified-computer-use@openai-bundled".enabled=false' -c 'plugins."codex-app-tools@openai-bundled".enabled=false'` 关掉这两个插件，说明里也写明禁止。用户的 `~/.codex/config.toml` 没有改。**以后每次跑 Codex 都必须带这两个参数。**
- **H 段 Codex 正在跑**：03:32 启动，约 03:58 结束。说明在 `codex_brief_H.md`，日志在 `codex_log_H.txt`。范围是 interactions 的 component（14 条）、overlay（6 条）、data（9 条）、text（8 条），按顺序能做多少做多少。改前截图在 `shots/before7`，脚本 `shoot7.cjs`。
  - **下一段开头**：先用 `grep -c cua_repl codex_log_H.txt` 确认是 0，再确认 Codex 已结束，然后运行 `node shoot7.cjs http://127.0.0.1:4181/vibocoding-assistant/ shots/after7`，用 `mksheet.sh` 生成对比图，审过后提交。

## 第 9–10 段（03:40–04:58）
- 87fcdb4（H 段）：interactions 的 component 14、overlay 6、data 9、text 8，共 37 条单独精修。对比图 box `contact_sheet_H1.jpg`–`H4.jpg`。H 段日志 `mcp: cua_repl` 计数 0。
- **单独精修累计 112 / 192**。其余 80 条走类型级皮肤（6 个视觉风格指南保留原样式）。按要求跳过 I 段。
- 未单独精修：interactions 的 mobile、cursor、background、rules 及剩余 media/scroll；components tables 的 table-reorder、infinite-scroll、virtual-list；basics 的 layout/visual；其余 scenarios、ai；components charts。
- b09f1d2：Codex（插件已关，日志 cua_repl 0 次）同步 11 个旧审计单测到新资产结构；触屏下 role=button 点击区 ≥44px。没有删测试。
- 063c89a：幽灵按钮按下态边框加深（#4B5563，与悬停可区分）；batch1 无头测试同步新规格（按下 scale .98、语义色边框、图片卡片的装饰性细边框豁免，均附注释）。
- 验证（04:30 前后）：
  - Python 单测 147 项全部通过（含旧链接跳转 test_old_anchors）。
  - 口语别名命中 62/62（100%）；token_demos、batch1/2/3、batch3/5 无头测试通过。
  - allpages：212 页 × 3 宽，无溢出、无 JS 报错；唯一一条失败请求 lake-teal-02-640.webp 复查返回 200，属懒加载被切页中断。
  - 未通过：batch6 无头（悬停预览弹层在 interactions 画廊格内底部超出 16px 余量）；demo_redesign_headless 24 项（相关演示格缺 skin 注入 / states 与 a11y 顺序 / 按钮页 390 下 morph、magnetic、ripple 窄格横向溢出 等）。已派短时 Codex（T2，插件关闭）修。batch4 完整无头在跑。
- 晨间总览：box `/workspace/bench/demo-redesign/morning_summary.jpg`（16 组改前/改后 1440）。
- 04:52 补记：
  - batch4 完整无头（1473 项）未通过 55 项，全是触屏点击区：components/button 一行四个按钮高 25px、components/search 的 🔍 按钮高 28px、components/tabs 三个标签高 25px（390/768/1023/1440 触屏模式都有）。未修。
  - Codex T2（插件关，cua_repl 0 次）做了静态修复：morph/magnetic/ripple 窄格收缩、悬停预览弹层位置、lift 顶部留白；demo_redesign_headless 的样式链断言改为按 skin 文件是否存在来要求，并改成严格 deepEqual。单测 147 项仍全过。
  - 修复后重跑 demo_redesign_headless 与 batch6 时两者并发、被 280 秒超时打断，结果无效，**需要单独顺序重跑确认**。
  - 下一步：顺序重跑 `tests/demo_redesign_headless.cjs`、`audit_fix_batch6_headless.cjs`、`audit_fix_batch4_headless.cjs`（各给 ≥15 分钟，且期间不要重新构建）；修 button/search/tabs 触屏点击区。

## 第 11 段（04:48–05:25）
- 触屏点击区问题定位：不是尺寸规则缺失，是点状态按钮时演示重挂载，把已加载的样式表 `<link>` 重新 append，浏览器丢弃后重新拉取，测试在无缓存时量到无样式按钮（25px）。真实用户在慢网下也会看到一帧无样式闪烁。
- 97075e7：`demo-runtime.js` 重挂载时保留已连接的 link 不移动。无可见外观变化，所以 morning_summary 不需要重拍。
- 结果：单测 147/147；batch4 完整无头 1473/1473 通过（小于 12px 的文字 0 段）。
- demo_redesign_headless → batch6 正在后台按顺序跑（期间不重新构建），结果写在 Mac `/tmp/r2.txt`，日志 `/tmp/r2_dr.log`、`/tmp/r2_b6.log`。
- 本段没有跑 Codex。caffeinate 原进程 06:06 到期，04:49 已另起一个 `caffeinate -i -t 12060`，持续到约 08:10。

## 第 12 段（05:25–06:02）
- 上一轮结果：batch4 通过；demo_redesign 4 项失败（component-lift 触屏点按、basics/components/interactions 三个画廊在 390 下 11 个缩略格横向溢出）；batch6 通过。
- Codex T3（插件关，cua_repl 0 次）：11 个缩略格加 `@container demo-stage (max-width:240px)` 收缩规则，只影响窄格，1440 外观不变（总览图无需重拍）。
- component-lift：功能正常（点按切换 touch-open 和 aria-pressed），失败来自测试取样时机；测试改为等点击生效后再取样，并把亚像素过渡尾巴视为静止。
- 9a7cc88 提交。最终：单测 147/147；demo_redesign 1887/1887；batch6 通过；batch4 1473/1473（上一轮，之后只改了 240px 以下容器规则和测试）。
- 晨间报告：box `/workspace/bench/demo-redesign/morning_report.md`。

## 第 13 段（11:36–12:10）新一轮：加宽 + 用户报告问题
- 新的 Codex 启动方式：`demo-redesign-work/runcodex.sh BRIEF LOG 秒数`，除用户已在配置里关掉的两项外，再用 `-c` 关闭 computer-use / chrome / browser 插件和 computer-use、kimi-cu、node_repl 三个 MCP，并覆盖 `notify=[]`。每份日志用 `cucheck.sh` 检查，必须是 0（G 段旧日志检出 42，证明检查有效）。
- 26f11d5 条目页演示区加宽：条目页外壳 1376px，使用卡固定 300/320px；1440 下舞台 725→960px，1024 下 619→628，768/390 不变。舞台 ≥880px 时主体 clamp(560px,62%,680px)。对比图 box `wide_1440_before_after.jpg`。batch4 1473/1473 通过；Python 单测 147/147。
- a26f030 用户报告的三处问题：
  - 嵌套圆角：舞台 12→16（`--ds-r-stage`），新增 `--ds-r-*` 层级变量，画廊缩略格舞台 11；规则写进 demo-spec.md。
  - 「它怎么动」卡片：最小 320px，390 下单列；播放按钮放进卡片标题行，离预览 16px、离卡片边 16px（原来离预览 −52px 即重叠、离右边 9px）。
  - 标签指示器按选中标签的实际位置和宽度放置，ResizeObserver 随尺寸重算。
  - 新增 `tests/geometry_headless.cjs`：嵌套圆角、按钮贴边/重叠、文字裁切、比内容窄、指示器偏移 >2px。
  - 对比图：box `fix_menu_card_390_before_after.jpg`、`fix_motion_cards_before_after.jpg`、`fix_radius_before_after.jpg`。
- Codex I1（组件剩余 ui 10 + 图表 5，共 15 条新皮肤）和 DS（设计系统页、docs/design-system.md、两份新测试）已写完，cua 检查都是 0，**未提交，待评审截图**。
- 排队顺序（用户定）：全量几何检查结果修复 → 复制提示词方案 D（使用卡变提示词卡，192 条共用模板）→ 390/768 全量移动端目检 → 设计系统页 → 剩余 80 条精修（I1 已做 15 条待审）。

## 第 14 段（12:10–12:58）几何修复 + 方案 D + 设计系统页评审
- 几何全量检查（192 条 × 1440/768/390 = 576 次页面加载）：
  - 第 1 轮（a26f030 后）：radius 283 / spacing 2192 / clip 0 / indicator 0 / narrow 8。
  - 第 2 轮（4dba45f 后）：radius 33 / spacing 200 / narrow 1。
  - 第 3 轮（46eb7bb + 方案 D 后）：radius 17 / spacing 0 / narrow 2。
  - 3b9faf4 修完剩余 7 处圆角和 2 处提示词悬挂空格，逐页复查为 0；全量第 4 轮放到下一段一起跑。
- 46eb7bb：玻璃/新拟态外框、角内小框 6px、卡片图 12px、分区导航 44px 列、分段按钮分隔线；检查器按百分比解析圆角（圆环、有机形状不再误报），共用外框的分段按钮组豁免 0 间隙。
- b09d1b6 方案 D：使用卡变提示词卡（全文、卡内滚动、卡头「复制」、注明「复制时自动附带 N 条验收要求」，复制后整卡 #6D28D9 + ✓ 已复制）；正文里重复的提示词块移除；≤1023 提示词块紧跟演示、块在视区内时底栏隐藏并 inert。192 条共用模板。测试同步加严（新 tests/test_prompt_card_d.py、tests/prompt_card_d_runtime.cjs、batch5 无头加 D 断言）。Codex 日志 cua/computer-use 调用 0。
  - 对比图 box：`D_before_after_1440_390.jpg`（cmdk / button / view-crossfade / dashboard，列 = 前1440 前390 后1440 后390），`D_copied_state.jpg`。
- 000ba19 I1 15 条评审通过：box `I1a_before_after.jpg`、`I1b_before_after.jpg`。
- 1ca7aff：移动端目检发现「数字滚轮」画廊缩略图只剩「次互动」（数字靠脚本生成，缩略图不跑脚本）；初始 198 直接写进标记。
- 597e621 设计系统页：补「嵌套圆角与间距」活例子，按下态示例不再缩小（无头检查的 44px 失败点）；docs/design-system.md 同步。
- 测试：Python 单测 159/159；design_system_headless 通过（6 组尺寸/动态偏好）；prompt_card_d_runtime 通过。batch4 / demo_redesign / batch6 留到最终验证顺序跑。
- 移动端目检：390 + 768 全量截图已生成（Mac `demo-redesign-work/shots/qa-mid/`，before 基线 `shots/qa-before/`），总览表 box `qa/`（43 张）。已看完 390 顶部 3/12 张 + 动效卡 1/6 张。
