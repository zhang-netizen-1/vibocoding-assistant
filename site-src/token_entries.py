"""Native basics entries, independent of the frozen legacy source anchors."""
import re
TOKENS = [
    ('color', '颜色与对比度', 'Color & Contrast', '用统一色板区分用途，并确保文字和控件可辨认。',
     '试一试：改变文字色和底色，查看实时对比度与达标结果。', ['components/button', 'components/color']),
    ('typography', '字体与字号', 'Typography / Type Scale', '用一套字号和行高区分标题、正文与说明。',
     '试一试：切换正文基准字号，比较整套层级与行高。', ['components/card']),
    ('spacing', '间距', 'Spacing', '用固定间距刻度组织内容的疏密与分组。',
     '试一试：切换 4 或 8 的倍数，观察卡片内外留白。', ['components/card', 'basics/grid']),
    ('radius-shadow', '圆角与阴影', 'Radius & Shadow / Elevation', '用圆角统一形态，用阴影表达浮层的前后关系。',
     '试一试：分别切换圆角和阴影，比较形态与层级。', ['components/card', 'components/popover']),
    ('dark-mode', '深色模式', 'Dark Mode', '用两套语义颜色让同一内容适应浅色和深色环境。',
     '试一试：选择浅色、深色或跟随系统，刷新后保留手动选择。', ['components/switch', 'basics/color']),
]


def demo_markup(slug):
    controls = {
        'color': '''<div class="token-controls"><label>文字色 <input type="color" data-token-control="foreground" value="#6D28D9"></label><label>底色 <input type="color" data-token-control="background" value="#FFFFFF"></label></div><div class="contrast-sample" data-token-sample><strong>颜色与对比度</strong><p>让内容在实际底色上可辨认。</p></div><output data-token-output aria-live="polite">对比度 7.10:1 · 正文达标 · 大字达标 · 控件边界达标</output>''',
        'typography': '''<label>正文基准 <span class="ds-select-wrap"><select data-token-control="type"><option value="14">14px</option><option value="16" selected>16px</option></select></span></label><div class="type-ladder" data-token-sample><strong data-type-size="36">页面标题 36px</strong><strong data-type-size="28">条目标题 28px</strong><strong data-type-size="22">区块标题 22px</strong><span data-type-size="18">一句话 18px</span><span data-type-size="16">正文 16px</span><span data-type-size="14">说明 14px</span><span data-type-size="13">标签 13px</span><span data-type-size="12">提示 12px</span></div><output data-token-output aria-live="polite">正文 16px · 行高 1.7 · 标签和提示行高 1.5</output>''',
        'spacing': '''<label>间距方案 <span class="ds-select-wrap"><select data-token-control="space"><option value="4">4 的倍数 · 内 16 / 外 12px</option><option value="8">8 的倍数 · 内 24 / 外 16px</option></select></span></label><div class="space-ruler" aria-label="间距刻度">4 / 8 / 12 / 16 / 24 / 32 / 48 / 64 px</div><div class="space-frame"><div class="token-card spacing-card" data-token-sample><strong>内容分组</strong><p>内边距让文字离开边界，外边距隔开相邻内容。</p></div></div><output data-token-output aria-live="polite">内边距 16px · 外边距 12px</output>''',
        'radius-shadow': '''<div class="token-controls"><label>圆角 <span class="ds-select-wrap"><select data-token-control="radius"><option value="6">小 6px</option><option value="8">中 8px</option><option value="12" selected>大 12px</option><option value="16">特大 16px</option></select></span></label><label>阴影 <span class="ds-select-wrap"><select data-token-control="shadow"><option value="none">无阴影</option><option value="soft">轻阴影（教学对照）</option><option value="overlay">浮层阴影（本站）</option></select></span></label></div><div class="elevation-frame"><div class="token-card elevation-card" data-token-sample><strong>形态与层级</strong><p>普通卡片靠边界分组，浮层用一层阴影。</p></div></div><output data-token-output aria-live="polite">圆角 12px · 无阴影</output>''',
        'dark-mode': '''<label>演示主题 <span class="ds-select-wrap"><select data-token-control="theme"><option value="system">跟随系统</option><option value="light">浅色</option><option value="dark">深色</option></select></span></label><div class="theme-sample token-card" data-token-sample data-theme="light"><strong>项目主题预览</strong><p>同一内容使用两套语义颜色。</p><button type="button" data-token-action>保存设置</button></div><output data-token-output aria-live="polite">仅切换此演示卡片 · 当前浅色</output>''',
    }
    html = controls[slug]
    if slug == 'typography':
        html = re.sub(r'data-type-size="(\d+)"', lambda m: f'data-type-size="{m[1]}" style="font-size:{m[1]}px"', html)
    return f'<div class="token-demo" data-token="{slug}">{html}</div>'


def entries():
    for slug, zh, en, definition, hint, related in TOKENS:
        yield dict(id='t-' + slug, column='basics', group='tokens', slug=slug, zh=zh, en=en,
                   definition=definition, terms='', prompt='实现' + zh + '并沿用项目现有设计规范。',
                   acceptance=[], old_anchors=[], source=dict(path='site-src/token_entries.py'),
                   demo=dict(kind='token', key=slug, html=demo_markup(slug)), demo_hint=hint,
                   related=related)
