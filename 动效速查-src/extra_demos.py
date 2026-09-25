"""Self-contained mini interfaces for the additional motion entries."""

from html import escape


def scene(kicker, title, body, modifier=""):
    return (
        f'<div class="extra-scene {modifier}">'
        f'<div class="extra-heading"><small>{escape(kicker)}</small><strong>{escape(title)}</strong></div>'
        f'{body}</div>'
    )


def tiles():
    items = (
        ("01", "界面", "工作台", "blue"),
        ("02", "插画", "晨间花园", "peach"),
        ("03", "界面", "数据面板", "mint"),
        ("04", "插画", "山间日落", "violet"),
    )
    return "".join(
        f'<div class="extra-gallery-tile {tone}" data-type="{kind}">'
        f'<i aria-hidden="true"></i><span>{num} / {title}</span></div>'
        for num, kind, title, tone in items
    )


DEMOS = {
    "extra-filter-grid": scene(
        "COLLECTION / 04", "精选作品",
        '<div class="extra-filter-tabs" aria-label="作品分类">'
        '<button type="button" data-extra-action="filter" data-value="全部" aria-pressed="true">全部</button>'
        '<button type="button" data-extra-action="filter" data-value="界面" aria-pressed="false">界面</button>'
        '<button type="button" data-extra-action="filter" data-value="插画" aria-pressed="false">插画</button>'
        '<button type="button" data-extra-action="filter" data-value="摄影" aria-pressed="false">摄影</button></div>'
        f'<div class="extra-gallery">{tiles()}<p class="extra-filter-empty" hidden>暂无匹配作品</p></div>'
        '<p class="extra-status" role="status">显示 4 个作品</p>', "filter-scene"
    ),
    "extra-delete-undo": scene(
        "TODAY / TASKS", "今日清单",
        '<div class="extra-task-list">'
        '<div class="extra-task" data-task="0"><span class="extra-task-check">✓</span><span>整理页面结构</span><button type="button" data-extra-action="delete" aria-label="删除整理页面结构">删除</button></div>'
        '<div class="extra-task" data-task="1"><span class="extra-task-check">○</span><span>检查动效细节</span><button type="button" data-extra-action="delete" aria-label="删除检查动效细节">删除</button></div>'
        '<div class="extra-task" data-task="2"><span class="extra-task-check">○</span><span>记录新的灵感</span><button type="button" data-extra-action="delete" aria-label="删除记录新的灵感">删除</button></div>'
        '</div><div class="extra-undo" hidden><span role="status">已移除条目</span><button type="button" data-extra-action="undo">撤销 <b>5</b>s</button></div>',
        "delete-scene"
    ),
    "extra-accordion": scene(
        "SUPPORT / FAQ", "常见问题",
        '<div class="extra-accordion">'
        '<div class="extra-faq"><button type="button" data-extra-action="accordion" aria-expanded="true" aria-controls="extra-faq-a">如何开始？<i aria-hidden="true">⌄</i></button><div id="extra-faq-a" class="extra-faq-panel"><div><p>先选一个场景，再观察触发、变化和结束状态。</p></div></div></div>'
        '<div class="extra-faq"><button type="button" data-extra-action="accordion" aria-expanded="false" aria-controls="extra-faq-b">可以随时调整吗？<i aria-hidden="true">⌄</i></button><div id="extra-faq-b" class="extra-faq-panel" aria-hidden="true"><div><p>可以。改变选项后，内容会在原位置连续展开。</p></div></div></div>'
        '<div class="extra-faq"><button type="button" data-extra-action="accordion" aria-expanded="false" aria-controls="extra-faq-c">如何回到初始状态？<i aria-hidden="true">⌄</i></button><div id="extra-faq-c" class="extra-faq-panel" aria-hidden="true"><div><p>再次点击当前问题，内容就会平稳收起。</p></div></div></div>'
        '</div>', "accordion-scene"
    ),
    "extra-submit-flow": scene(
        "FORM / STATUS", "提交反馈",
        '<div class="extra-outcomes" aria-label="选择演示结果">'
        '<button type="button" data-extra-action="outcome" data-value="success" aria-pressed="true">成功</button>'
        '<button type="button" data-extra-action="outcome" data-value="invalid" aria-pressed="false">校验错误</button>'
        '<button type="button" data-extra-action="outcome" data-value="network" aria-pressed="false">网络失败</button></div>'
        '<label class="extra-field">项目名称<input type="text" value="新的灵感" aria-describedby="extra-submit-error"></label>'
        '<span id="extra-submit-error" class="extra-field-error" role="alert"></span>'
        '<button class="extra-primary" type="button" data-extra-action="submit">模拟提交 <span>↗</span></button>'
        '<p class="extra-status" role="status">选择结果后提交，观察完整状态。</p>', "submit-scene"
    ),
    "extra-toast-stack": scene(
        "ACTIVITY / LIVE", "通知中心",
        '<div class="extra-toast-list" aria-live="polite"><div class="extra-notice"><span>灵感已收录</span><button type="button" data-extra-action="remove-toast" aria-label="关闭通知">×</button></div></div>'
        '<button class="extra-primary" type="button" data-extra-action="add-toast">新增通知 <span>＋</span></button>',
        "toast-scene"
    ),
    "extra-tab-indicator": scene(
        "WORKSPACE / 03", "项目概览",
        '<div class="extra-tabs" role="tablist" aria-label="仪表盘视图">'
        '<span class="extra-tab-indicator" aria-hidden="true"></span>'
        '<button type="button" id="extra-tab-overview" role="tab" data-extra-action="tab" aria-controls="extra-tab-panel" aria-selected="true" tabindex="0">概览</button>'
        '<button type="button" id="extra-tab-activity" role="tab" data-extra-action="tab" aria-controls="extra-tab-panel" aria-selected="false" tabindex="-1">活动</button>'
        '<button type="button" id="extra-tab-settings" role="tab" data-extra-action="tab" aria-controls="extra-tab-panel" aria-selected="false" tabindex="-1">设置</button></div>'
        '<div id="extra-tab-panel" class="extra-tab-content" role="tabpanel" aria-labelledby="extra-tab-overview"><span class="extra-stat-number">24</span><div><strong>本周浏览</strong><small>较上周 ↑ 12%</small></div></div>',
        "tabs-scene"
    ),
    "extra-drop-snap": scene(
        "BOARD / DRAG", "安排任务",
        '<div class="extra-drop-board"><div class="extra-drop-source"><span class="extra-drag-chip" tabindex="0" role="button" aria-label="拖动任务卡" aria-describedby="extra-drop-instruction">◈ 设计评审</span></div>'
        '<div class="extra-drop-targets"><div class="extra-drop-target" data-target="今天"><small>01 / TODAY</small><strong>今天</strong></div>'
        '<div class="extra-drop-target" data-target="稍后"><small>02 / LATER</small><strong>稍后</strong></div></div></div>'
        '<div class="extra-drop-controls"><button type="button" data-extra-action="drop" data-value="今天">放入今天</button><button type="button" data-extra-action="drop" data-value="稍后">放入稍后</button><button type="button" data-extra-action="reset-drop">重置</button></div>'
        '<p id="extra-drop-instruction" class="extra-status" role="status">拖到目标区域，或使用下方按钮。</p>', "drop-scene"
    ),
    "extra-odometer": scene(
        "METRIC / ROLLING", "实时总览",
        '<div class="extra-number-line"><span class="extra-digits" role="status" aria-label="当前数值 198"></span><span class="extra-number-suffix">次互动</span></div>'
        '<div class="extra-number-footer"><span>较上次 <b>＋7</b></span><button type="button" data-extra-action="roll">更新数值 ↗</button></div>',
        "odometer-scene"
    ),
    "extra-cross-page": scene(
        "NAVIGATION / 02", "跨页图片",
        '<iframe class="extra-page-frame" src="motion-demo-gallery.html" title="跨页图片连续转场演示"></iframe>'
        '<div class="extra-page-controls"><span>在画廊中点开作品，再返回</span><button type="button" data-extra-action="reset-page">重置</button></div>',
        "page-scene"
    ),
    "extra-inline-expand": scene(
        "PROJECT / BOARD", "项目看板",
        '<div class="extra-inline-list"><button type="button" class="extra-inline-card" data-extra-action="expand" aria-expanded="false">'
        '<span class="extra-inline-art"></span><span class="extra-inline-copy"><strong>探索新布局</strong><small>界面设计 · 进行中</small></span><i aria-hidden="true">⌄</i>'
        '<span class="extra-inline-detail">拆解主要模块与页面层级。<em>查看任务说明 ↗</em></span></button>'
        '<div class="extra-inline-neighbor">○　动效细节检查 <span>下一项</span></div>'
        '<div class="extra-inline-neighbor">○　完善交互文案 <span>待开始</span></div></div>',
        "inline-scene"
    ),
    "extra-shrink-header": scene(
        "ARTICLE / SCROLL", "收缩页头",
        '<div class="extra-scroll extra-header-scroll" tabindex="0" aria-label="滚动观察页头压缩">'
        '<div class="extra-scroll-header"><small>FIELD NOTES / 01</small><strong>设计中的<br>细节观察</strong><span>阅读约 3 分钟</span></div>'
        '<div class="extra-article-copy"><h4>从整体到细节</h4><p>内容经过页头时，空间逐渐收紧，导航仍留在可见位置。</p><p>继续向下阅读，标题保留为简短的定位信息。</p><p>页面结构保持稳定，阅读的上下文不会丢失。</p><p>向上滚动，页头就会恢复原来的宽松形态。</p></div></div>',
        "header-scroll-scene"
    ),
    "extra-section-nav": scene(
        "READING / INDEX", "章节导航",
        '<div class="extra-section-layout"><div class="extra-scroll extra-section-scroll" tabindex="0" aria-label="滚动文章章节">'
        '<section id="extra-section-1"><small>01 / 序章</small><strong>从问题开始</strong><p>先明确要解决的核心问题。</p></section>'
        '<section id="extra-section-2"><small>02 / 探索</small><strong>寻找可能</strong><p>对照不同路径与重要线索。</p></section>'
        '<section id="extra-section-3"><small>03 / 决定</small><strong>形成方案</strong><p>把判断收束成可以执行的步骤。</p></section></div>'
        '<div class="extra-section-links" aria-label="章节目录"><button type="button" data-extra-action="section" data-target="1" aria-current="true">01</button><button type="button" data-extra-action="section" data-target="2">02</button><button type="button" data-extra-action="section" data-target="3">03</button></div></div>',
        "section-scene"
    ),
    "extra-scroll-highlight": scene(
        "STORY / READ", "随读高亮",
        '<div class="extra-scroll extra-highlight-scroll" tabindex="0" aria-label="滚动文字高亮演示">'
        '<div class="extra-highlight-spacer">向下滚动，观察文字</div>'
        '<p class="extra-highlight-text"><span>好的动效</span><span>让变化有迹可循，</span><span>也让每一次操作</span><span>得到明确回应。</span></p>'
        '<div class="extra-highlight-spacer">向上滚动可以撤回高亮</div></div>',
        "highlight-scene"
    ),
    "extra-snap-sections": scene(
        "CHAPTER / SNAP", "章节停靠",
        '<div class="extra-scroll extra-snap-scroll" tabindex="0" aria-label="滚动到不同章节">'
        '<section><small>01 / START</small><strong>起点</strong><p>从这里开始观察。</p></section>'
        '<section><small>02 / EXPLORE</small><strong>探索</strong><p>滚动会停靠在章节边界。</p></section>'
        '<section><small>03 / FINISH</small><strong>抵达</strong><p>编号跟随当前章节。</p></section></div>'
        '<span class="extra-snap-status" role="status">当前章节 01 / 03</span>',
        "snap-scene"
    ),
    "extra-image-magnifier": scene(
        "GALLERY / DETAIL", "查看画面细节",
        '<div class="extra-magnifier-art" tabindex="0" role="img" aria-label="山间日落插画，可移动指针查看细节"><span class="extra-magnifier-lens" aria-hidden="true"></span><small>移动或点击画面</small></div>'
        '<button type="button" data-extra-action="reset-magnifier">复位放大镜</button>',
        "magnifier-scene"
    ),
    "extra-timeline-preview": scene(
        "VIDEO / PREVIEW", "时间轴预览",
        '<div class="extra-video-frame"><div class="extra-video-landscape"><span class="extra-video-play">▶</span></div><span class="extra-video-time">00:12 / 00:48</span></div>'
        '<div class="extra-preview-bubble" aria-hidden="true"><div class="extra-preview-image"></div><span>00:12</span></div>'
        '<label class="extra-timeline-label">播放位置<input type="range" min="0" max="48" value="12" aria-label="预览并调整播放位置"></label>'
        '<p class="extra-status" role="status">拖动预览，松手确认；Esc 取消。</p>',
        "timeline-scene"
    ),
    "extra-chart-morph": scene(
        "ANALYTICS / WEEK", "访问趋势",
        '<div class="extra-chart-controls"><button type="button" data-extra-action="chart" data-value="current" aria-pressed="true">本周</button><button type="button" data-extra-action="chart" data-value="previous" aria-pressed="false">上周</button></div>'
        '<div class="extra-chart" role="img" aria-label="本周访问趋势：周一 42，周二 68，周三 54，周四 82，周五 63">'
        '<div><i style="--bar:42%"></i><small>一</small></div><div><i style="--bar:68%"></i><small>二</small></div><div><i style="--bar:54%"></i><small>三</small></div><div><i style="--bar:82%"></i><small>四</small></div><div><i style="--bar:63%"></i><small>五</small></div></div>'
        '<span class="extra-status" role="status">本周访问总量 309</span>',
        "chart-scene"
    ),
    "extra-skeleton-handoff": scene(
        "CONTENT / LOADING", "内容交接",
        '<div class="extra-content-card" aria-live="polite">'
        '<div class="extra-content-skeleton"><i></i><span><b></b><b></b><b></b></span></div>'
        '<div class="extra-content-real" hidden><i></i><span><strong>灵感资料库</strong><small>12 个条目 · 已准备就绪</small><em>打开内容 ↗</em></span></div></div>'
        '<button type="button" data-extra-action="load-content">模拟加载</button>',
        "handoff-scene"
    ),
}
