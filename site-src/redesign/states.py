"""D20 state options and faithful visual descriptions for the ten source demos."""
from html import escape

STATES = {
    'button': (
        ('free', '自由试', '按钮可直接点击，悬停时底色变化，按下时轻微下移。'),
        ('hover', '悬停', '主要按钮底色变浅，次要按钮显示浅色底，危险按钮底色加深。'),
        ('pressed', '按下', '按钮保持向下移动一像素的按下效果。'),
        ('focus', '聚焦', '第一个按钮周围显示清晰的焦点轮廓。'),
    ),
    'input': (
        ('free', '自由试', '输入框可直接输入，邮箱字段聚焦或有内容时标签上浮。'),
        ('focus', '聚焦', '输入框边框变为演示主色，邮箱标签上浮。'),
    ),
    'textarea': (
        ('free', '自由试', '文本域可直接输入，右下角同步显示字数。'),
        ('focus', '聚焦', '文本域边框变为演示主色，并显示外侧焦点环。'),
    ),
    'select': (
        ('free', '自由试', '选择框可打开原生城市选项。'),
        ('focus', '聚焦', '选择框边框变为演示主色，并显示外侧焦点环。'),
    ),
    'checkbox': (
        ('free', '自由试', '复选框可分别切换，父级随子项显示全选或半选。'),
        ('selected', '选中', '所有复选框固定显示选中标记。'),
        ('unselected', '未选中', '所有复选框固定显示空框。'),
        ('focus', '聚焦', '父级复选框周围显示焦点轮廓。'),
    ),
    'radio': (
        ('free', '自由试', '两个单选项可切换，同一时间选中一项。'),
        ('selected', '选中', '第二个单选项固定显示选中圆点。'),
        ('focus', '聚焦', '第一个单选项周围显示焦点轮廓。'),
    ),
    'switch': (
        ('free', '自由试', '开关可点击切换，滑块位置和轨道底色同步变化。'),
        ('selected', '选中', '轨道显示演示主色，白色滑块固定在右侧。'),
        ('unselected', '未选中', '轨道显示灰色，白色滑块固定在左侧。'),
        ('focus', '聚焦', '开关轨道周围显示焦点轮廓。'),
    ),
    'slider': (
        ('free', '自由试', '滑动条可拖动或用方向键调整，百分比同步变化。'),
        ('focus', '聚焦', '滑动条周围显示焦点轮廓。'),
    ),
    'search': (
        ('free', '自由试', '搜索框可输入，回车或点击搜索按钮显示演示反馈。'),
        ('focus', '聚焦', '搜索输入区周围显示焦点轮廓。'),
    ),
    'tabs': (
        ('free', '自由试', '点击或用方向键切换标签页，选中标记与内容同步更新。'),
        ('selected', '选中', '评价标签固定显示选中底边，内容区显示评价内容。'),
        ('focus', '聚焦', '简介标签周围显示焦点轮廓。'),
    ),
}


def render(slug):
    options = STATES.get(slug)
    if not options:
        return ''
    buttons = ''.join(f'<button type="button" data-state="{key}" data-state-class="force-{key}" aria-pressed="{str(key == "free").lower()}" aria-describedby="state-description-{key}">{label}</button>' for key,label,_ in options)
    captions = ''.join(f'<p class="state-caption" id="state-description-{key}" data-description="{key}"{" hidden" if key != "free" else ""}>{escape(description)}</p>' for key,_,description in options)
    return f'<div class="state-picker"><h2 id="state-title">状态切换</h2><div class="chips" role="group" aria-labelledby="state-title">{buttons}</div><div aria-live="polite">{captions}</div></div>'
