# UI 层 + 交互层走查报告

**对象**：vibocoding助手（dist/ 全站 12 页）
**时间**：2026-09-25
**方式**：Playwright 实测（桌面 1440px + 移动 390px 触屏模拟、键盘走查、减动效模拟）+ 静态代码审查（HTML 四维度 / CSS token / JS 行为）+ WCAG 2.1 AA 基线比对
**结论**：**无 P0 阻断问题**。P1 共 4 项（1 项移动端视觉 bug、1 项触控目标、2 项可访问性），P2 共 8 项打磨项。

> **修复记录（2026-09-25 同日）**：P1 全部修复并回归验证通过。P1-1 眉标移动端隐藏（site.css 760px 断点）；P1-3 八处色值加深（site.css `--muted/--faint`、home.css directory-card-top、theme.css site-nav-section、guides.css guide-card-head span、ui 页 `--faint`、motion_extra.css 两处、site.css stagger-kicker），复测 5.3~5.6:1 全过 AA；P1-2 motion 页移动端触控目标 26→0（FAQ 行 44px、演示按钮 30px/24px，🔍/面包屑/暂停/页脚链接用伪元素扩展命中区，视觉不变）；P1-4 星星 `#6b7280`（4.3:1）+ label 改"评 N 星"。涉及源文件：site.css / home.css / theme.css / guides.css / motion_extra.css / 网页UI元素速查.html。桌面端视觉无回归，测试 6/6 通过。P2 8 项仍待办。

---

## 先说做得好的（走查通过项）

| 检查项 | 结果 |
|---|---|
| 地标结构 header/nav/main/footer | 9/10 页齐全（例外见 P2-1） |
| 键盘焦点可见性 | 每个 Tab 落点均有 2px 实线描边 + box-shadow 双保险，全站 35 条 `:focus-visible` 规则 |
| 跳转链接 | "跳到主要内容"存在且焦点可达 |
| 搜索交互承诺兑现 | Enter 打开首条结果（实测跳到 `/ui/#c-button`）✓，Esc 清空 ✓ |
| 复制链接反馈 | 按钮原地变"已复制 ✓"（2.5s 复原），guide 页另有 `role=status` + `aria-live=polite` 状态区，剪贴板实测写入成功 |
| 锚点直达 | 三个 README 示例锚点全部落位在粘性导航下方（scroll-margin 生效） |
| 标题结构 | 每页恰好 1 个 h1，无跳级 |
| 图片/表单 | 0 个图片缺 alt，0 个输入缺 label |
| prefers-reduced-motion | reduce 模拟下 motion 页循环动画全部暂停（0 个 running） |
| 横向溢出 | 12 页在 390px/1440px 下均为 0px 溢出 |
| 控制台 | 全站 0 报错 |
| flows 注册表单 demo | `label for` + `aria-describedby` + `aria-invalid` + 校验反馈齐全，教科书级 |
| 状态语义 | 筛选 chip 有 `aria-pressed`、暂停按钮有 `aria-pressed`、导航有 `aria-current`、折叠菜单为原生 `details/summary` |

---

## P1 — 应尽快修（4 项）

### P1-1 移动端 motion 页眉标与 H1 重叠（视觉 bug）

**现象**：390px 视口下，`02 / MOTION` 眉标横穿标题"页面 / 网站 / App 动效速查"，呈删除线状叠字。
**证据**：截图 `mobile-motion-hero.png`（耳标明显压在 H1 上）。
**根因**：`site-src/site.css` 中

```css
body.site-reference[data-section="motion"] .brand:before {
  content: "02 / MOTION"; color: var(--coral);
  position: absolute; top: 27px;  /* 按桌面 brand 高度硬编码 */
}
```

桌面端 `.brand` 高度恰好容纳 `top:27px` 的绝对定位眉标；移动端 H1 折成两行、布局高度变化，眉标位置不再正确。
**修复建议**：窄屏直接隐藏，或改为文档流内元素：

```css
@media (max-width: 720px) {
  [data-section="motion"] .brand::before { display: none; }
}
```

**影响面**：仅 `/motion/`（全站唯一用此模式的页面，已验证）。

### P1-2 触控目标过小（WCAG 2.5.8 最低 24px / iOS HIG 44px）

**实测**（390px 视口，点击区域 < 26px 的可见可点元素）：

| 页面 | 数量 | 最小样本 |
|---|---|---|
| /motion/ | **26 个** | FAQ 手风琴"如何开始？⌄"高 23px；演示控制按钮"重置/01/02/03"高 23px |
| /ui/ | 4 个 | 搜索演示 🔍 按钮 20×25.6px |
| 全站各页 | 各 1 个 | "回到顶部 ↑" 63×19px |

**修复建议**：移动端断点内给这些控件 `min-height: 44px`（至少 24px 保底）；FAQ 行是整行 summary，加 `padding-block` 成本最低。演示类小按钮可用 `::before` 扩大热区（`position:absolute; inset:-10px`）而不改视觉。

### P1-3 小字号文本对比度系统性未达 AA（4.5:1）

**实测**（白底计算，need=4.5）：

| 文本样本 | 实测对比度 | 来源 token |
|---|---|---|
| "浏览目录"（11px，全站导航） | 4.33:1 | `--faint: #68717e` |
| 分类卡眉标"02 / MOTION"等（10px，首页） | 4.32:1 | 同上 |
| 筛选 chip 计数"47/18/11"（12px） | 4.17:1 | guides.css 本地色 |
| 英文副标"Responsive Grid"（12px） | 4.44:1 | 同上 |
| **motion 页** `--faint:#9090a0` | **≈2.7:1** | motion 模板本地 token |
| **motion 页** `--muted:#a3a3b1` | **≈2.3:1** | motion 模板本地 token |

**修复建议**：
1. `site.css` 的 `--faint: #68717e → #626b78`（≈4.9:1，一处改动惠及全站小字标签）；
2. motion 模板的 `--faint/--muted` 是全站最浅的，对齐到 `#5e6774`/`#68717e` 档位；
3. chip 计数等 4.1-4.4 区间的本地色一并加深。

### P1-4 ★ 收藏控件：几乎不可见 + 语义含糊（/ui/）

**实测**：未选中星星 `color: rgb(209,213,219)`（≈1.3:1，need 3:1），白底上几乎看不见；`aria-label="1 星"` 让屏幕阅读器读出"1 星"，听感像状态而非操作。
**建议**：未选中态加深到 `#6b7280` 以上；label 改为"评 1 星 / 评 2 星…"；选中/未选中已有 `aria-pressed`，保留。

---

## P2 — 打磨项（8 项）

1. **motion 页缺 `<footer>` 语义**（9/10 页有，仅它用 class 代替）。统一补 `<footer>` 或复用 site-footer。
2. **7-8px 微字号**：CSS 中 48 处 <12px 声明，最小两处为 `.style-art small { font-size:7px }`（visual-styles.css:174）和 `.mini-page-hero small { font-size:8px }`（guides.css:92）。作为"作品插画内文字"可接受，但建议设 9px 下限，-currently 实测渲染出 8px 的"01 / FORM"已到可读性边缘。
3. **37 处内联 `on*=` 事件**（全部在 ui 页，如 `onclick="demoSearch(this)"`）：不利于 CSP 与维护，建议改成事件委托（其他页面已是这种写法）。
4. **/ui/ 页密码框演示不在 `<form>` 内**：浏览器控制台实测警告"Password field is not contained in a form"，密码管理器无法识别（flows 注册 demo 的密码框已正确包在 form 内，无此问题）。给演示组件加 `<form>` 包裹或 `form` 属性即可。
5. **全站 0 条 `:active` 规则**：按钮/chip 没有按压态。建议补 `:active { transform: scale(.98) }`，与现有 hover 过渡衔接。
6. **flows.css / skills.css / visual-styles.css 无 `prefers-reduced-motion` 保护**（其余 4 个 css 各有 1 处）：三处的小过渡在 reduce 模式下仍会动。把 site.css 里现成的 reduce 块复制过去即可。
7. **"已复制 ✓"按钮宽度跳动**：4 字 ↔ 5 字切换引起约 1 字宽的行内位移，给按钮 `min-width: 5.5em` 可消除。
8. **"左右滑动查看更多 →"提示（11px）常驻**：用户滑动一次后可自动淡出，减少噪音。

---

## 明确不算问题的（已排除的疑点）

- "02 / MOTION 眉标被标题盖住"在桌面端**不存在**——是移动端专属问题（见 P1-1）。
- `复制链接` 点击后"无反馈"为测量时序误判，DOM 级实测 300ms 内完成文字切换，功能正常。
- 锚点滚动"被粘性导航遮挡"为测量脚本误报（把 100vh 的侧边导航当成了 header），实际 `scroll-margin` 工作正常。
- motion 页深色演示卡内的白字对比度问题：白色文字实际压在深色渐变上，视觉正常，仅 9-10px 微字号是 P2 范畴。
- skills 卡片无 hover 抬升是**正确**设计（卡片整体不可点，只有内部链接/按钮可交互）。

---

## 建议修复顺序

1. P1-1（一行 CSS，立竿见影）→ 2. P1-3（两个 token 改色，全站受益）→ 3. P1-2（移动端 padding）→ 4. P1-4 → P2 按序。

*审计脚本存于 `output/pw-env/`（audit_browser.js / audit_static.py / audit_followup.js / audit_evidence.js），改版后可复跑回归。截图证据在 `/tmp/vibo-audit/`。*
