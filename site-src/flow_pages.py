"""Three practical UI flows that complement the component glossary."""

from html import escape


FLOWS = (
    {
        "slug": "search", "title": "搜索与筛选", "route": "搜索框 → 筛选 → 结果列表 → 空状态",
        "steps": (("输入", "关键词、状态筛选"), ("动作", "输入即筛选，清空后恢复全部"),
                  ("结果", "列表与数量同步更新"), ("异常", "无匹配时显示空状态和清除筛选入口")),
        "prompt": "做一个可搜索的任务列表：顶部放关键词输入框和状态筛选，输入后实时过滤列表并更新结果数量。没有匹配项时显示空状态和「清除筛选」按钮；清空条件后恢复全部。先用 8 条示例数据，不接后端。请让我实际测试搜索、筛选和空状态。",
    },
    {
        "slug": "register", "title": "注册表单", "route": "输入框 → 校验 → 提交中 → 成功/错误",
        "steps": (("输入", "邮箱、密码"), ("动作", "提交前检查必填和邮箱格式"),
                  ("结果", "提交中禁用按钮；完成后显示明确结果"), ("异常", "错误提示放在对应输入框旁，保留已填内容")),
        "prompt": "做一个注册表单原型：邮箱和密码都有可见标签。空值和邮箱格式错误时在对应字段下方显示原因，不只弹 Toast；通过校验后展示短暂提交中状态，再明确提示「模拟注册成功，尚未创建真实账号」。提交中不能重复提交，失败时保留已填内容。不接真实账号系统。",
    },
    {
        "slug": "upload", "title": "文件选择与预览", "route": "选择/拖入 → 校验 → 文件预览 → 确认上传",
        "steps": (("输入", "一张图片文件"), ("动作", "检查类型与大小，再生成本地预览"),
                  ("结果", "展示文件名和预览，允许重新选择"), ("异常", "格式或大小不符时解释原因，不声称已上传")),
        "prompt": "做一个图片上传原型：支持点击选择或拖入，只接收 PNG/JPEG，大小不超过 5MB。选择后先显示文件名和本地预览，提供移除/重选；不合规时说明具体原因。只有接入真实服务并收到成功响应，才能显示「上传成功」；当前原型只演示本地选择和预览。",
    },
)


def render_flow(flow, index):
    steps = ''.join(f'<div><dt>{escape(label)}</dt><dd>{escape(value)}</dd></div>' for label, value in flow["steps"])
    return f'''<article class="flow-card" id="flow-{flow["slug"]}">
      <div class="flow-card-main"><div class="flow-card-heading"><span class="flow-number">{index:02d} / FLOW</span><h2>{escape(flow["title"])}</h2></div>
      <p class="flow-route">{escape(flow["route"])}</p><dl class="flow-steps">{steps}</dl></div>
      <div class="flow-card-prompt"><div class="flow-prompt-heading"><span>交给 Coding Agent</span><small>先替换为你自己的项目内容</small></div>
      <p class="flow-prompt-text">{escape(flow["prompt"])}</p><button class="flow-copy" type="button">复制实现提示词 <span aria-hidden="true">↗</span></button></div>
    </article>'''


def render_page(nav_html, site_css_version, guides_css_version, flows_css_version, theme_css_version, js_version):
    cards = '\n'.join(render_flow(flow, index) for index, flow in enumerate(FLOWS, 1))
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="三个组合流程示例：搜索与筛选、注册表单、文件选择与预览。了解多个 UI 组件如何组成完整任务，并复制实现提示词。">
<meta name="theme-color" content="#f7f7fd"><title>组合流程示例 · vibocoding助手</title>
<link rel="icon" href="../assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="../assets/site.css?v={site_css_version}"><link rel="stylesheet" href="../assets/guides.css?v={guides_css_version}"><link rel="stylesheet" href="../assets/flows.css?v={flows_css_version}"><link rel="stylesheet" href="../assets/theme.css?v={theme_css_version}">
<script defer src="../assets/flows.js?v={js_version}"></script></head><body class="site-guide site-flows">{nav_html}
<main id="flows-main" class="guide-page"><header class="guide-hero"><div><p><a href="../ui/">UI 元素</a> / COMPOSED FLOWS</p><h1>从组件到<span>可用流程</span></h1><div class="guide-hero-lead">看多个组件如何串成完整任务，再把自己的页面、字段和动作写清楚。</div></div><div class="guide-hero-count"><strong>03</strong><span>组示例流程<br>看状态 · 复制提示词</span></div></header>
<div class="flows-intro"><p>下面三段是示例流程，用来看多个组件怎么串成完整任务。复制前请把页面、字段和动作替换成你自己项目的内容；它们不是现成需求，也不代表已接入后端。</p><a href="../ui/">返回 UI 元素速查 <span aria-hidden="true">↗</span></a></div>
<p id="flow-copy-status" class="site-announcement" role="status" aria-live="polite" aria-atomic="true"></p>
<div class="flow-list">{cards}</div>
<section class="flow-lab" aria-labelledby="flow-lab-title"><div class="flow-lab-copy"><span class="flow-number">LOCAL STUDY / FORM STATES</span><h2 id="flow-lab-title">状态实测：一个表单，不只一个正常画面</h2><p>先空着提交，观察字段旁的错误；再填测试字符提交，观察按钮禁用、提交中与模拟结果。这个演示不会发出请求，也不会创建账号。</p><ul><li>默认：可填写，按钮可点</li><li>错误：告诉用户哪个字段、为什么不对</li><li>进行中：阻止重复提交</li><li>结果：明确标注为本地模拟，而非真实注册成功</li></ul></div>
<form id="sample-register" class="flow-form" novalidate><p class="flow-form-note">仅本地演示，请勿输入真实密码。</p><div class="flow-form-field"><label for="flow-email">邮箱</label><input id="flow-email" name="email" type="email" placeholder="name@example.com" autocomplete="off" aria-describedby="flow-email-error"><span id="flow-email-error" class="flow-error" data-error="email"></span></div>
<div class="flow-form-field"><label for="flow-password">密码（至少 8 位）</label><input id="flow-password" name="password" type="password" placeholder="仅输入测试字符" autocomplete="off" aria-describedby="flow-password-error"><span id="flow-password-error" class="flow-error" data-error="password"></span></div><button type="submit">模拟提交 <span aria-hidden="true">↗</span></button><p class="flow-form-status" role="status" aria-live="polite"></p></form></section>
</main><footer class="site-home-footer"><div><strong>vibocoding助手</strong><span>让界面的表达更准确。</span></div><a href="../">回到首页 ↑</a></footer></body></html>'''
