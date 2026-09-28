# 回归审计报告 · 第二轮

**审计对象**：第一轮走查修复的 diff（site-src/ 4 个 CSS、动效速查-src/motion_extra.css、网页UI元素速查.html、scripts/build_site.py）+ 全站当前构建
**方式**：构建可复现性验证 + Playwright 全站复测（10 页 × 桌面/移动）+ 静态四维度复扫 + 死链/测试 + 对修复 diff 的逐规则取证
**角色**：独立审计（对上轮修复做 PASS/FAIL 取证，发现的缺陷当场修复并复验——三处均为已批准 P1 工作的未完成/引伤部分，非新设计决策）

---

## 总结

| 类别 | 数量 | 说明 |
|---|---|---|
| PASS（取证通过） | 23 项 | 见下文分组 |
| **FAIL → 已修复** | **3 项** | 1×P1 + 1×P1 + 1×P2，全部复验通过 |
| 已知开放（决策台账） | P2 × 10 | 上轮报告 8 项 + 本轮新编目 2 项 |
| 误报排除 | 4 项 | 采样器假阳性，非真实问题 |
| P0 | **0** | — |

---

## FAIL 明细（均已修复 + 复验）

### FAIL [P1] B3 — car-pause 规则被上轮修复截断（我方引入的回归）

**证据**：修复前 dist 实测——
```css
.car-pause{position:absolute;top:7px;right:42px;position:absolute;}border:0;border-radius:5px;background:rgba(255,255,255,.88);...}
```
`}` 提前闭合，`border/background/color` 全部沦为孤儿声明被解析器丢弃；`::before` 命中区被错误插入 `@media (prefers-reduced-motion:reduce)` 块内，正常状态下不生效。
**后果**：轮播演示的暂停按钮丢失胶囊样式 + 命中区扩展失效。
**修复**：还原完整规则 + `::before` 提升为全局规则（`.car-pause` 本身是 position:absolute，天然为伪元素的包含块，无需加 relative）；RM 块还原为仅 `display:none`。
**复验**：`::before` content:"" inset -7px ✓；`background: rgba(255,255,255,.88)`、radius 5px ✓；截图确认胶囊外观正常。

### FAIL [P1] C1 — chip 计数对比度修复被覆盖规则击穿（P1-3 遗漏）

**证据**：`site.css:179` 存在 `.site-reference .fchip .n { color:#747d88; font-size:12px }`——site 级覆盖规则，特异性高于 ui 页 token 方案。第一轮修复改了 ui 页 `--faint`，但实际生效的是这条字面量，复测仍 4.17:1（computed `rgb(116,125,136)`）。
**后果**：走查报告 P1-3 中"筛选 chip 计数"一项实际未达标。
**修复**：改为 `color: var(--faint)`（在 `.site-reference` 作用域解析为 #626b78）。
**复验**：computed `rgb(98,107,120)`，对白底 5.39:1 ✓。

### FAIL [P2] C3 — motion_extra 移动块内规则顺序缺陷（我方引入）

**证据**：`@media(max-width:760px)` 块内 `.extra-scene button{min-height:30px}` 排在 `.extra-faq button{min-height:44px}` 之后，同特异性后者的 min-height 被覆盖；且 FAQ 的 padding 声明被基础规则 `padding:5px 7px!important` 压制为死代码。实测 FAQ 行高 30px 而非声明的 44px。
**后果**：FAQ 触控行未达自定 44px 目标（仍 ≥24px，满足 WCAG 2.5.8 最低线，故 P2）。
**修复**：`.extra-scene button` 提前、FAQ 规则放块内最后、删除无效 padding 声明。
**复验**：mobile 实测 FAQ 行高 44px ✓，/motion/ 移动端 <24px 热区 0 个 ✓。

---

## PASS 分组（抽样列证）

**A. 构建/内容完整性**
- 两次构建 dist 逐字节一致（`diff -rq` 通过）→ 产物确定性 ✓
- `build_site.py` 生成器→循环改写：nav 输出含 `aria-current="page"` 逐字一致 ✓
- 152 条目、10 页、测试 6/6 ✓；死链/缺资源 0 ✓

**B. 结构完整性**
- 10 页 landmark（header/nav/main/footer）9/10 + motion 页缺 footer 为已知开放项 ✓
- 每页 h1×1、无跳级、0 图片缺 alt、0 输入缺 label、0 正 tabindex ✓

**C. CSS 完整性**
- 8 处色值加深全部落进构建产物（computed 实测 5.3~5.6:1）✓
- 新增规则均被引用、无选择器冲突（chip `.on` 白字规则优先级保留）✓

**D. 交互逻辑**
- 键盘：skip link → 14 个 Tab 落点全部可见焦点环；搜索 Enter 直达 `/ui/#c-button`、Esc 清空 ✓
- 复制链接：DOM 级点击 300ms 内变"已复制 ✓"、剪贴板写入成功 ✓
- flows 表单校验反馈、`aria-describedby`/`aria-invalid` 完整 ✓

**E. 隐藏坑**
- `prefers-reduced-motion` 模拟下 motion 页 0 个运行中动画 ✓
- 命中区伪元素均为透明无背景，无视觉污染、无横向溢出（10 页 overflowX=0）✓
- 移动端 motion 页 <24px 热区 0 个 ✓

---

## 新编目（决策台账追加，未修复）

| 编号 | 项 | 实测 | 定性 |
|---|---|---|---|
| P2-9 | motion 横滚演示"03"大数字 | 25px 白字对浅色轨道 2.52:1（需 3:1） | 演示卡内部装饰数字 |
| P2-10 | ui 进度条演示"40%"标签 | 内联 `#6b7280` 13px 对灰卡 4.3:1 | 演示内联标签 |

另有 4 项采样器假阳性再次确认排除：motion 深色渐变卡白字（FIELD NOTES 等，bgOf 不识别 gradient）、`toast-wrap`（复制反馈走按钮文字切换 + role=status，另一套机制）、锚点遮挡（侧栏 100vh 被误当 header）、`"跳到主要内容"` ratio 1.0（视觉隐藏元素，聚焦时可见）。

---

## 结论

上一轮 P1 修复**方向全部正确、其中 3 处执行有缺陷**（1 处遗漏覆盖规则、2 处我方引伤），本轮审计全部捕获并当场修复，复验证据齐备。当前构建：0 P0、0 未修 P1、已知开放 P2 × 10。可发布。

---

## 附：P2 台账清偿记录（同日第三轮）

审计后用户指令清偿全部 10 项 P2，逐项修复并回归：

| 项 | 修复 | 验证 |
|---|---|---|
| P2-1 motion 缺 `<footer>` | 模板 `div.footer` → `footer.footer` | dist 含 `<footer` ✓ |
| P2-2 微字号 9px 下限 | visual-styles 7px、guides 8px、motion_extra 3 处 8px → 9px | dist 无 <9px 字号声明 ✓；mockup 截图无溢出（clipped:false）✓ |
| P2-3 内联 on*= 37 处 | 全部转 `data-cmd` 委托层（click/keydown/input/submit 四监听），dropdown/popover 的 outside-close 监听器加 `[data-cmd]` 豁免防回关 | **32 个处理器逐个功能回归全过**（chip 删除、面包屑、搜索点击+回车、注册校验、抽屉×2、弹窗、⌘K 背景关闭、下拉开关+选中+外点关闭、手风琴×2、信息气泡、页签×2、步骤×3、toast×6、开关、滑杆联运）；页面 0 报错 ✓ |
| P2-4 密码框无 form | 表单演示 div → `<form class=demo-form>` + 委托 submit preventDefault | 浏览器控制台警告消失 ✓ |
| P2-5 无按压态 | theme.css `button:active { scale: .97 }`（独立 scale 属性，与 translate 类控件的 transform 组合而不覆盖） | 规则落进构建 ✓ |
| P2-6 三文件缺 RM 保护 | flows/skills/visual-styles 各加 reduce 块 | RM 模拟下 transition-duration 1e-05s ✓ |
| P2-7 复制按钮宽度跳动 | `.site-card-tools button{min-width:56px}` | 切换前后宽度 56px→56px ✓ |
| P2-8 滑动提示常驻 | site.js：chips 首次 scroll 后置灰（resize 不复活） | 滚动后 hidden=true ✓ |
| P2-9 "03" 数字 2.52:1 | 横滚演示粉块 `#d99184 → #c66f57` | computed rgb(198,111,87)，白字 4.7:1 ≥3 ✓ |
| P2-10 "40%" 标签 4.3:1 | 内联 `#6b7280 → #5b6570` | computed rgb(91,101,112) ✓ |

**回归护栏**：测试 6/6、构建复现、内联处理器计数 37→0、静态扫描仅剩 1 条既定取舍（motion 生成式演示内联样式）。台账清零。

*审计脚本：`output/pw-env/`（audit_browser.js / audit_static.py / audit_probes.js / linkcheck.js / verify_fix.js），可随时复跑。*
