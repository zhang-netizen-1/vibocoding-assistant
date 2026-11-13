"""D20 state options and faithful visual descriptions for the ten source demos."""
from html import escape

STATES = {
    'button': (
        ('free', '自由试', '按钮可直接点击，悬停时底色变化，按下时轻微缩小。'),
        ('hover', '悬停', '主要按钮和危险按钮底色变深，次要按钮显示浅色底。'),
        ('pressed', '按下', '按钮底色比悬停时更深，并保持缩放至 0.98。'),
        ('focus', '聚焦', '第一个按钮周围显示清晰的焦点轮廓。'),
        ('disabled', '禁用', '按钮显示灰色底与可辨认的文字，鼠标和键盘均无法触发。'),
        ('success', '成功', '按钮显示绿色成功反馈；此处固定状态供观察。'),
        ('loading', '加载中', '按钮显示加载图标与「提交中…」，尺寸保持不变且无法重复提交。'),
    ),
    'input': (
        ('free', '自由试', '输入框可直接输入，邮箱字段聚焦或有内容时标签上浮。'),
        ('hover', '悬停', '输入框边框加深，提示可以编辑。'),
        ('pressed', '按下', '输入框显示浅紫底与紫色边框。'),
        ('success', '成功', '输入框显示绿色边框。'),
        ('focus', '聚焦', '输入框显示清晰的焦点轮廓，邮箱标签上浮。'),
        ('disabled', '禁用', '输入框显示灰色底，已有内容可辨认且无法修改。'),
        ('error', '出错', '输入内容保留，红色边框与字段下方的文字说明修正方式。'),
    ),
    'textarea': (
        ('free', '自由试', '文本域可直接输入，右下角同步显示字数。'),
        ('focus', '聚焦', '文本域显示清晰的外侧焦点环。'),
        ('disabled', '禁用', '文本域显示灰色底，已有内容可辨认且无法修改。'),
        ('error', '出错', '备注内容保留，红色边框与下方文字说明填写要求。'),
    ),
    'select': (
        ('free', '自由试', '选择框可打开原生城市选项。'),
        ('focus', '聚焦', '选择框显示清晰的外侧焦点环。'),
        ('disabled', '禁用', '整个选择框禁用，鼠标与键盘均无法展开。'),
        ('error', '出错', '选择框显示红色边框，下方提示重新选择城市。'),
    ),
    'checkbox': (
        ('free', '自由试', '复选框可分别切换，父级随子项显示全选或半选。'),
        ('selected', '选中', '所有复选框固定显示选中标记。'),
        ('unselected', '未选中', '所有复选框固定显示空框。'),
        ('focus', '聚焦', '父级复选框周围显示焦点轮廓。'),
        ('disabled', '禁用', '所有复选框保持当前选中或半选标记，点击标签与空格均无法改变值。'),
    ),
    'radio': (
        ('free', '自由试', '两个单选项可切换，同一时间选中一项。'),
        ('selected', '选中', '第二个单选项固定显示选中圆点。'),
        ('focus', '聚焦', '第一个单选项周围显示焦点轮廓。'),
        ('disabled', '禁用', '单选项保持选中标记，点击标签与方向键均无法改变值。'),
    ),
    'switch': (
        ('free', '自由试', '开关可点击切换，滑块位置和轨道底色同步变化。'),
        ('selected', '选中', '轨道显示演示主色，白色滑块固定在右侧。'),
        ('unselected', '未选中', '轨道显示灰色，白色滑块固定在左侧。'),
        ('focus', '聚焦', '开关轨道周围显示焦点轮廓。'),
        ('disabled', '禁用', '开关轨道变灰，滑块保留当前位置，鼠标与空格均无法切换。'),
    ),
    'slider': (
        ('free', '自由试', '滑动条可拖动或用方向键调整，百分比同步变化。'),
        ('focus', '聚焦', '滑动条周围显示焦点轮廓。'),
        ('disabled', '禁用', '滑动条显示灰色滑块，拖动、点击轨道与方向键均无法改变值。'),
    ),
    'search': (
        ('free', '自由试', '搜索框可输入，回车或点击搜索按钮显示演示反馈。'),
        ('focus', '聚焦', '搜索输入区周围显示焦点轮廓。'),
        ('disabled', '禁用', '搜索输入与图标按钮均禁用，无法输入或发起搜索。'),
        ('error', '出错', '保留搜索词，红色边框与下方文字提示有效的查询示例。'),
    ),
    'tabs': (
        ('free', '自由试', '点击或用方向键切换标签页，选中标记与内容同步更新。'),
        ('selected', '选中', '评价标签固定显示选中底边，内容区显示评价内容。'),
        ('focus', '聚焦', '简介标签周围显示焦点轮廓。'),
        ('disabled', '禁用', '「帮助」标签变灰且无法选择，其余标签仍可切换。'),
    ),
}


def render(slug):
    options = STATES.get(slug)
    if not options:
        return ''
    buttons = ''.join(f'<button type="button" data-state="{key}" data-state-class="force-{key}" aria-pressed="{str(key == "free").lower()}" aria-describedby="state-description-{key}">{label}</button>' for key,label,_ in options)
    captions = ''.join(f'<p class="state-caption" id="state-description-{key}" data-description="{key}"{" hidden" if key != "free" else ""}>{escape(description)}</p>' for key,_,description in options)
    return f'<div class="state-picker"><h2 id="state-title">状态切换</h2><div class="chips" role="group" aria-labelledby="state-title">{buttons}</div><div aria-live="polite">{captions}</div></div>'
