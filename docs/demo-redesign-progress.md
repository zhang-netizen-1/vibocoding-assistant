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
