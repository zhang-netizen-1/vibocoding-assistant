"""Curated UI and interaction Agent Skills with verified GitHub source paths."""

from html import escape


VERIFIED_DATE = "2026-09-25"


def skill(slug, title, repo, path, summary, use, scope, tags):
    return dict(slug=slug, title=title, repo=repo, path=path, summary=summary,
                use=use, scope=scope, tags=tags)


GROUPS = [
    ("视觉与设计系统", [
        skill("frontend-design", "前端视觉设计", "anthropics/skills", "skills/frontend-design",
              "从产品内容出发确定视觉方向，处理字体、色彩、版式和页面整体表现。",
              "新建页面、重做首页、摆脱模板化视觉", "通用 Web UI", ("视觉方向", "页面实现")),
        skill("ui-ux-pro-max", "UI/UX 设计检索", "nextlevelbuilder/ui-ux-pro-max-skill", ".claude/skills/ui-ux-pro-max",
              "提供可搜索的风格、配色、字体、图表与多技术栈 UI 指引，并可生成设计系统建议。",
              "需要系统性筛选风格或搭建跨页面规范", "含脚本和数据；需 Python 3", ("设计系统", "多技术栈")),
        skill("baseline-ui", "界面基础打磨", "ibelick/ui-skills", "skills/baseline-ui",
              "集中检查间距、层级、排版与常见的粗糙界面细节。",
              "现有界面能用，但密度、对齐和层级不稳", "通用 Web UI", ("细节优化", "视觉层级")),
        skill("create-design-md", "提取设计规范", "ibelick/ui-skills", "skills/create-design-md",
              "从现有产品或网站提炼设计语言，形成供 Coding Agent 持续参考的 DESIGN.md。",
              "已有界面需要统一组件和后续页面的视觉规则", "仅编写 DESIGN.md", ("设计文档", "一致性")),
    ]),
    ("交互与可用性", [
        skill("fixing-accessibility", "无障碍交互修复", "ibelick/ui-skills", "skills/fixing-accessibility",
              "检查控件名称、键盘路径、焦点、表单错误、语义和颜色对比。",
              "表单、菜单、弹窗等交互需要可访问性修复", "Web HTML 与 ARIA", ("键盘交互", "可访问性")),
        skill("fixing-motion-performance", "动效性能修复", "ibelick/ui-skills", "skills/fixing-motion-performance",
              "定位布局抖动、滚动动画和高成本模糊等造成的卡顿。",
              "动效掉帧、滚动不流畅或过渡性能不稳定", "CSS/JS 动画", ("动效", "性能")),
        skill("vercel-react-view-transitions", "React 视图转场", "vercel-labs/agent-skills", "skills/react-view-transitions",
              "使用 React View Transition API 实现路由、列表和共享元素的状态转场。",
              "React 项目需要页面切换或内容状态变化的连续感", "仅适合支持相关 API 的 React 项目", ("React", "转场")),
    ]),
    ("审计与验证", [
        skill("web-design-guidelines", "Web 界面规范审计", "vercel-labs/agent-skills", "skills/web-design-guidelines",
              "按 Vercel 的 Web Interface Guidelines 检查界面代码并给出定位清楚的建议。",
              "上线前复核可用性、响应式和前端实现细节", "审计时会读取在线规则", ("规范审计", "问题定位")),
        skill("webapp-testing", "真实浏览器测试", "anthropics/skills", "skills/webapp-testing",
              "借助 Playwright 操作本地网页，验证交互流程并检查截图、控制台信息。",
              "需要证明按钮、表单、导航和窄屏布局确实工作", "需要可用浏览器测试环境", ("交互验证", "浏览器")),
        skill("vercel-composition-patterns", "React 组件组合", "vercel-labs/agent-skills", "skills/composition-patterns",
              "用组合式组件和清晰的状态归属改善复杂 React 组件的扩展性。",
              "组件出现大量布尔属性或可复用交互接口难维护", "仅适合 React", ("组件 API", "React")),
    ]),
]


def all_skills():
    return [entry for _, entries in GROUPS for entry in entries]


def install_prompt(entry):
    url = f'https://github.com/{entry["repo"]}/tree/main/{entry["path"]}'
    source_name = entry['path'].rsplit('/', 1)[-1]
    name_option = (f'源目录名为 {source_name}，调用安装器时明确指定 --name {entry["slug"]}，确保安装目录名称正确。'
                   if source_name != entry['slug'] else '')
    return (f'请在 Codex 中安装「{entry["slug"]}」Skill，来源：{url}。'
            '先打开该 GitHub 目录，核对 SKILL.md、引用的脚本或资料及安装说明；'
            f'使用 Codex 的 skill-installer 只安装这个 Skill 到全局 ~/.codex/skills/{entry["slug"]}/，不要安装整个仓库。'
            f'{name_option}'
            '如果本机已有同名 Skill，先核对来源和版本，不能直接覆盖。'
            '安装后检查 SKILL.md 与附属文件均可读取，说明如何在新会话中调用；不要修改当前项目代码。')


def render_card(entry, number):
    slug = escape(entry['slug'], quote=True)
    source = f'https://github.com/{entry["repo"]}/blob/main/{entry["path"]}/SKILL.md'
    search = escape(' '.join((entry['slug'], entry['title'], entry['repo'], entry['summary'], entry['use'], *entry['tags'])), quote=True)
    tags = ''.join(f'<span>{escape(tag)}</span>' for tag in entry['tags'])
    return f'''<article class="skill-card" id="skill-{slug}" data-search="{search}">
      <div class="skill-card-top"><span>{number:02d} / SKILL</span><span>{escape(entry['repo'])}</span></div>
      <div class="skill-card-body"><h3>{escape(entry['title'])}<small>{escape(entry['slug'])}</small></h3>
        <p class="skill-summary">{escape(entry['summary'])}</p>
        <dl><div><dt>适合什么时候用</dt><dd>{escape(entry['use'])}</dd></div><div><dt>适用范围</dt><dd>{escape(entry['scope'])}</dd></div></dl>
        <div class="skill-tags" aria-label="能力标签">{tags}</div>
      </div>
      <div class="skill-card-source"><a href="{escape(source, quote=True)}" target="_blank" rel="noopener noreferrer">查看 GitHub 上的 SKILL.md ↗</a><span>已核对 · {VERIFIED_DATE}</span></div>
      <details class="skill-install" open><summary>查看并复制 Skill 安装提示词</summary><div class="skill-install-text">{escape(install_prompt(entry))}</div><button type="button" class="skill-copy">复制安装提示词</button></details>
    </article>'''


def render_page(nav_html, site_css_version, skills_css_version, theme_css_version, js_version):
    sections = '\n'.join(
        f'<section class="skill-section"><div class="skill-section-title"><div><span>SECTION / {index:02d}</span><h2>{escape(group)}</h2></div><small>{len(entries)} 个 Skill</small></div><div class="skill-grid">' +
        '\n'.join(render_card(entry, number) for number, entry in enumerate(entries, sum(len(items) for _, items in GROUPS[:index-1]) + 1)) +
        '</div></section>'
        for index, (group, entries) in enumerate(GROUPS, 1)
    )
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="精选 GitHub 上的 UI 与交互 Agent Skills，查看用途、来源，并复制可直接交给 Codex 的安装提示词。">
<meta name="theme-color" content="#f7f7fd"><title>UI 与交互 Skills · vibocoding助手</title>
<link rel="icon" href="../assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="../assets/site.css?v={site_css_version}"><link rel="stylesheet" href="../assets/skills.css?v={skills_css_version}"><link rel="stylesheet" href="../assets/theme.css?v={theme_css_version}">
<script defer src="../assets/skills.js?v={js_version}"></script></head><body class="site-skills">{nav_html}
<main id="skills-main" class="skills-page"><header class="skills-hero"><div><p>08 / AGENT TOOLKIT</p><h1>UI 与交互<br><span>Skills</span></h1><div class="skills-hero-lead">从视觉设计到交互验证，挑选真正能放进 Coding Agent 工作流的 Skill。</div></div><div class="skills-hero-count"><strong>{len(all_skills()):02d}</strong><span>个已核对的 GitHub Skill<br>查看用途 · 复制安装提示词</span></div></header>
<div class="skills-toolbar"><label for="skill-search">搜索 Skill</label><input id="skill-search" type="search" placeholder="按名称、场景或来源搜索…" autocomplete="off"><span id="skill-count" role="status" aria-live="polite">{len(all_skills())} / {len(all_skills())} 个 Skill</span></div>
<p id="skill-copy-status" class="site-announcement" role="status" aria-live="polite" aria-atomic="true"></p>
<div id="skill-sections">{sections}</div><div id="skill-empty" class="skill-empty" hidden><strong>没有匹配的 Skill</strong><p>换个关键词，或清空搜索内容。</p><button type="button" id="skill-clear">清空搜索</button></div>
<p class="skills-footnote">来源核对日期：{VERIFIED_DATE}。GitHub 内容和安装方式可能更新，实际安装时应重新核对仓库文件。</p></main>
<footer class="site-home-footer"><div><strong>vibocoding助手</strong><span>让界面的表达更准确。</span></div><a href="../">回到首页 ↑</a></footer></body></html>'''
