"""Conservative static demo triage. No browser, execution, or inferred behavior.

Evidence is limited to selectors present in each demo, matching CSS declarations,
source IDs, explicit data-action/data-cmd hooks and matching JS initialization
blocks. Shared replay/run gates do not change a CSS animation into a JS renderer.
Ambiguous/native-only specimens and skill references are marked for review.
"""
from collections import Counter
from pathlib import Path
import importlib.util
import re

ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location('audit_entries', ROOT / 'site-src/entries.py')
ADAPTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ADAPTER)


def assets():
    ui = (ROOT / '网页UI元素速查.html').read_text()
    motion = (ROOT / '动效速查-src/motion_template.html').read_text()
    return dict(
        ui=('\n'.join(re.findall(r'<style>(.*?)</style>', ui, re.S)), '\n'.join(re.findall(r'<script[^>]*>(.*?)</script>', ui, re.S))),
        motion=('\n'.join(re.findall(r'<style>(.*?)</style>', motion, re.S)) + (ROOT / '动效速查-src/motion_extra.css').read_text(),
                '\n'.join(re.findall(r'<script[^>]*>(.*?)</script>', motion, re.S)) + (ROOT / '动效速查-src/motion_extra.js').read_text()),
        guide=((ROOT / 'site-src/guides.css').read_text() + (ROOT / 'site-src/visual-styles.css').read_text(), (ROOT / 'site-src/guides.js').read_text()))


def classify(demo, sources):
    kind = demo['kind']
    if kind == 'skill-reference':
        return '需人工确认', '来源是技能说明卡，没有独立交互演示，不推断为动画'
    css, js = sources[kind]
    html = demo['html']
    doc = ADAPTER.Document(html).root
    nodes = doc.find_all()
    classes = {c for n in nodes for c in n.attrs.get('class', '').split()}
    ids = {n.attrs['id'] for n in nodes if 'id' in n.attrs}
    # Each querySelectorAll initializer ends at the next initializer. Restrict
    # pointer classification to selectors actually used by this specimen.
    initializers = re.split(r'(?=document\.querySelectorAll\()', js)
    for block in initializers[1:]:
        match = re.match(r'document\.querySelectorAll\([\'"]\.([\w-]+)[\'"]\)', block)
        if match and match[1] in classes and re.search(r'addEventListener\([\'"](?:pointermove|mousemove)', block):
            return '依赖鼠标指针', f'.{match[1]} 初始化块含 pointermove（触屏替代仍需人工确认）'
    if kind == 'motion':
        key = demo['key']
        if key in ('component-tilt', 'component-spotlight'):
            line = next(line for line in js.splitlines() if "['component-tilt','component-spotlight']" in line)
            if 'pointermove' in line:
                return '依赖鼠标指针', f'{key} 共用初始化行含 pointermove'
        if 'cursor-wave' in classes and re.search(r'const wave=.*?pointermove', js, re.S):
            return '依赖鼠标指针', '.cursor-wave 绑定 pointermove'
    hooks = sorted({name for n in nodes for name in n.attrs if name in ('data-cmd', 'data-action', 'data-extra-action', 'data-drag')})
    matched_ids = [i for i in sorted(ids) if re.search(r'(?:getElementById\([\'"]|#[\w-]*\b)' + re.escape(i), js)]
    if hooks:
        return '需要 JS 驱动', '演示标记含 ' + '、'.join(hooks) + '；来源脚本有对应委托/拖动处理'
    if matched_ids:
        return '需要 JS 驱动', '来源脚本引用演示 ID：' + '、'.join(matched_ids)
    if kind == 'guide':
        return '需要 JS 驱动', f'guides.js 以 data-demo / data-mode 切换 {demo["section"]}/{demo["key"]} 的原预览状态'
    if '<canvas' in html:
        return '需要 JS 驱动', 'canvas 标记；来源脚本含 getContext / requestAnimationFrame'
    if kind == 'motion':
        key = demo['key']
        if re.search(r'[\'"]' + re.escape(key) + r'[\'"]', js):
            return '需要 JS 驱动', f'来源脚本显式分派 {key}；具体初始化/暂停须复核'
        if 'mini-scroll' in classes or any(c.endswith('-scroll') for c in classes):
            return '需要 JS 驱动', '局部滚动标记；脚本读取 scrollTop 并写进度/帧'
    for selector, body in re.findall(r'([^{}]+)\{([^{}]*)\}', css):
        matched = classes.intersection(re.findall(r'\.([\w-]+)', selector))
        if matched and re.search(r'\b(?:animation|transition)(?:-\w+)?\s*:', body):
            # A JS initializer containing the class might control this rule;
            # do not classify it as pure CSS without accounting for that hook.
            specific = [c for c in matched if re.search(r'[\'"]\.' + re.escape(c) + r'[\'"]', js)]
            if specific:
                return '需人工确认', 'CSS 动画/过渡与 JS 选择器均命中：' + '、'.join(sorted(specific))
            return '纯 CSS 动画', '匹配规则 ' + selector.strip()[:110] + ' 含 animation/transition；未发现专用 JS 钩子'
    return '需人工确认', '未找到足以确认的局部动画或专用脚本钩子；可能仅有原生状态/静态展示'


def audit():
    entries = ADAPTER.load_entries()
    sources = assets()
    rows = []
    for entry in entries:
        category, evidence = classify(entry['demo'], sources)
        if 'secondary' in entry['demo']:
            second, why = classify(entry['demo']['secondary'], sources)
            evidence += '；第二演示：' + second + '（' + why + '）'
            if second == '依赖鼠标指针' or category == '需人工确认':
                category = second
            elif second == '需要 JS 驱动':
                category = second
        rows.append((entry, category, evidence))
    return rows


def report():
    tax = ADAPTER.taxonomy()
    columns = {c['slug']: c['name'] for c in tax['columns']}
    groups = {(c['slug'], g['slug']): g['name'] for c in tax['columns'] for g in c['groups']}
    rows = audit()
    counts = Counter(category for _, category, _ in rows)
    lines = ['# 一期演示体检', '', '本报告由 `python3 scripts/audit_demos.py` 静态生成；不代表浏览器交互验收。', '',
             '共 ' + str(len(rows)) + ' 条：' + '；'.join(f'{c} {counts[c]}' for c in ('纯 CSS 动画', '需要 JS 驱动', '依赖鼠标指针', '需人工确认')) + '。', '',
             '判定优先级：局部 pointermove/mousemove 初始化 > data-action/data-cmd/data-extra-action/data-drag 或明确 ID/键/滚动/canvas 钩子 > 匹配演示 class 的 animation/transition 声明。@keyframes 只证明文件内有关键帧，不能单独证明某条使用。共享 run/replay 入口不改变 CSS 渲染分类。无法静态确认、技能说明卡均保留“需人工确认”。', '',
             '下表的静止、播放与手机列是迁移实施建议，未迁移条目没有声称已实现。所有列表建议同一时间仅播一条；减弱动态保留首帧并链接条目页。', '',
             '| 栏目 | 分组 | 名称 | 旧锚点 | 分类 | 判断依据 | 列表里怎么静止（建议） | 怎么播放（建议） | 手机怎么办（建议） |',
             '|---|---|---|---|---|---|---|---|---|']
    for e, category, evidence in rows:
        if category == '纯 CSS 动画':
            still, play, phone = '禁用动画与过渡，恢复初始 class', '悬停/聚焦启用局部动画；离开重置', '播放按钮运行一次；减弱动态只显示看演示链接'
        elif category == '需要 JS 驱动':
            still, play, phone = '不初始化循环；清理计时器/监听/位移，恢复原标记', '悬停/聚焦懒初始化并调用原动作；离开销毁并复位（入口需复核）', '点按原控件或播放一次；拖动保留键盘等价入口，需人工确认'
        elif category == '依赖鼠标指针':
            still, play, phone = '不绑定指针监听，清除位移/拖尾/光斑', '桌面悬停后绑定原 pointermove；离开解除并复位', '触屏替代需人工确认；未确认前显示静态说明和看演示链接'
        else:
            still, play, phone = '保留原始静态标记，不启动推测性动画', '需人工确认原触发与复位入口', '需人工确认；技能说明卡直接阅读说明'
        values = [columns[e['column']], groups[e['column'], e['group']], e['zh'], '、'.join(e['old_anchors']), category, evidence, still, play, phone]
        lines.append('| ' + ' | '.join(v.replace('|', '\\|').replace('\n', ' ') for v in values) + ' |')
    return '\n'.join(lines) + '\n'


if __name__ == '__main__':
    target = ROOT / 'docs/phase1-demo-audit.md'
    target.write_text(report(), encoding='utf-8')
    print(f'Wrote {target}')
