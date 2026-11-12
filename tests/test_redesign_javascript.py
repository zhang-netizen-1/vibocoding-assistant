"""Node syntax/pure-function checks only. These do not launch a browser."""
import json
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parent.parent


class RedesignJavaScriptTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not shutil.which('node'):
            raise unittest.SkipTest('Node is unavailable; no JS runtime checks')
        subprocess.run(['python3', 'scripts/build_site.py'], cwd=ROOT, check=True, capture_output=True)

    def test_javascript_syntax(self):
        for asset in (ROOT/'dist/assets/redesign').glob('*.js'):
            result = subprocess.run(['node','--check',str(asset)], text=True, capture_output=True)
            self.assertEqual(result.returncode,0,result.stderr)

    def test_all_source_demos_initialize_without_browser(self):
        import importlib.util
        import tempfile
        import sys
        sys.path.insert(0,str(ROOT/'site-src'))
        import entries
        spec=importlib.util.spec_from_file_location('demo_smoke_assets',ROOT/'site-src/redesign/demos.py')
        demos=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(demos)
        with tempfile.TemporaryDirectory() as folder:
            fixture=Path(folder)/'demos.json'
            fixture.write_text(json.dumps(demos.smoke_fixture(entries.load_entries()),ensure_ascii=False))
            runner = Path(folder) / 'demo-smoke.cjs'
            runner.write_text((ROOT / 'site-src/redesign/demo-smoke.cjs').read_text() + r'''
const checks = interactiveModel('c-checkbox');
const all = checks.doc.getElementById('ckAll');
const children = checks.root.querySelectorAll('.ck-child');
assert.equal(all.indeterminate, true);
all.checked = true;
checks.fire(all, 'change');
assert(children.every(child => child.checked));
children[0].checked = false;
checks.fire(children[0], 'change');
assert.equal(all.indeterminate, true);
assert.equal(all.checked, false);

const slider = interactiveModel('c-slider');
const range = slider.root.querySelector('[data-cmd="rangeLabel"]');
range.value = '73';
slider.fire(range, 'input');
assert.equal(range.nextElementSibling.textContent, '73%');

const otp = interactiveModel('c-otp');
const cells = otp.doc.getElementById('otpRow').querySelectorAll('input');
otp.fire(cells[0], 'paste', {clipboardData:{getData:() => '123456'}});
assert.equal(cells.map(cell => cell.value).join(''), '123456');
assert.equal(otp.focused, cells[5]);
assert.equal(otp.root.querySelector('.otp-hint').textContent, '已填完，可提交。');
cells[5].value = '';
otp.fire(cells[5], 'keydown', {key:'Backspace'});
assert.equal(otp.focused, cells[4]);
assert.equal(cells[4].value, '');

const password = interactiveModel('c-password-strength');
const passwordInput = password.doc.getElementById('pwInput');
for (const [value, level] of [['', '0'], ['abcdefgh', '1'], ['abc12345', '2'], ['Abcd1234!', '3'], ['Project2026!', '4']]) {
  passwordInput.value = value;
  password.fire(passwordInput, 'input');
  assert.equal(password.root.querySelector('.pw-demo').dataset.level, level);
}

const tags = interactiveModel('c-tag-input');
const tagInput = tags.doc.getElementById('tagInput');
tagInput.value = '提案';
tags.fire(tagInput, 'keydown', {key:'Enter'});
assert.equal(tags.root.querySelectorAll('.tagchip').length, 2);
tagInput.value = '提案';
tags.fire(tagInput, 'keydown', {key:'Enter'});
assert.equal(tags.root.querySelectorAll('.tagchip').length, 2);
tags.fire(tags.root.querySelectorAll('.tagx').at(-1), 'click');
assert.equal(tags.root.querySelectorAll('.tagchip').length, 1);

const stepper = interactiveModel('c-stepper');
stepper.fire(stepper.root.querySelector('[data-arg="1"]'), 'click');
assert.equal(Number(stepper.doc.getElementById('num').value), 3);
stepper.doc.getElementById('num').value = '0';
stepper.fire(stepper.root.querySelector('[data-arg="-1"]'), 'click');
assert.equal(Number(stepper.doc.getElementById('num').value), 0);

const rating = interactiveModel('c-rating');
rating.fire(rating.root.querySelectorAll('.st')[3], 'click');
assert.equal(rating.root.querySelectorAll('.st.on').length, 4);
assert.equal(rating.root.querySelectorAll('.st[aria-pressed="true"]').length, 1);

const upload = interactiveModel('c-upload');
const file = upload.doc.getElementById('filei');
file.files = [{name:'项目资料.pdf'}];
upload.fire(file, 'change');
assert.equal(upload.doc.getElementById('dz-text').textContent, '已选择：项目资料.pdf（未上传；点击可重选）');

const drawer = interactiveModel('c-drawer');
drawer.fire(drawer.root.querySelector('[data-cmd="openDrawer"]'), 'click');
assert(drawer.doc.getElementById('dmask').classList.contains('show'));
drawer.fire(drawer.root.querySelector('.drawer-head button'), 'click');
assert(!drawer.doc.getElementById('dmask').classList.contains('show'));

const popover = interactiveModel('c-popover');
const popoverTrigger = popover.doc.getElementById('popover-trigger');
popover.fire(popoverTrigger, 'click');
assert.equal(popover.doc.getElementById('popover-box').hidden, false);
assert.equal(popoverTrigger.getAttribute('aria-expanded'), 'true');
popover.fire(popoverTrigger, 'click');
assert.equal(popover.doc.getElementById('popover-box').hidden, true);
assert.equal(popoverTrigger.getAttribute('aria-expanded'), 'false');
console.log('Batch F: checkbox, slider, OTP paste/backspace, five password levels, tag dedup/removal, stepper bounds, rating, file choice, drawer and popover passed.');
const sortable = interactiveModel('g-data-table');
const sourceRows = [['自然搜索','68'],['推荐内容','42'],['直接访问','82']];
sortable.root.querySelectorAll('tbody tr').forEach((row,index) => row.cells.forEach((cell,column) => {cell.textContent=sourceRows[index][column];}));
sortable.fire(sortable.root.querySelector('[data-guide-mode="1"]'), 'click');
assert.equal(sortable.root.querySelector('.guide-card-stage').dataset.mode, '1');
assert.equal(sortable.root.querySelectorAll('tbody tr').map(row => Number(row.cells[1].textContent)).join(','), '82,68,42');
sortable.fire(sortable.root.querySelector('[data-guide-mode="0"]'), 'click');
assert.equal(sortable.root.querySelectorAll('th')[0].getAttribute('aria-sort'), 'ascending');
console.log('Batch G: extracted guide table sorting and reset passed.');
const flipH = interactiveModel('e-component-flip');
const flipButtonH = flipH.root.querySelector('.flip-card');
flipH.fire(flipButtonH, 'click');
assert.equal(flipButtonH.getAttribute('aria-pressed'), 'true');
flipH.fire(flipButtonH, 'click');
assert.equal(flipButtonH.getAttribute('aria-pressed'), 'false');
const switchH = interactiveModel('e-component-switch');
const switchButtonH = switchH.root.querySelector('.switch-demo');
switchH.fire(switchButtonH, 'click');
assert.equal(switchButtonH.getAttribute('aria-checked'), 'true');
switchH.fire(switchButtonH, 'click');
assert.equal(switchButtonH.getAttribute('aria-checked'), 'false');
const morphH = interactiveModel('e-component-morph');
const morphButtonH = morphH.root.querySelector('.morph-demo');
morphH.fire(morphButtonH, 'click');
assert(morphButtonH.disabled);
assert([...morphH.timeouts.values()].some(timer => timer.delay === 420));
morphH.flushTimeouts();
assert(morphButtonH.classList.contains('done'));
assert.equal(morphButtonH.disabled, false);
assert([...morphH.timeouts.values()].some(timer => timer.delay === 1050));
morphH.flushTimeouts();
assert.equal(morphButtonH.textContent, '执行动作 →');
const menuH = interactiveModel('e-overlay-menu');
menuH.fire(menuH.root.querySelector('[data-action="toggle"]'), 'click');
assert.equal(menuH.root.querySelector('.menu-items').hidden, false);
menuH.fire(menuH.root.querySelector('[role="menuitem"]'), 'click');
assert.equal(menuH.root.querySelector('.menu-items').hidden, true);
const tabH = interactiveModel('e-extra-tab-indicator');
tabH.fire(tabH.root.querySelector('#extra-tab-activity'), 'click');
assert.equal(tabH.root.querySelector('#extra-tab-activity').getAttribute('aria-selected'), 'true');
assert.equal(tabH.root.querySelector('.extra-tab-indicator').style.transform, 'translateX(100%)');
const inlineH = interactiveModel('e-extra-inline-expand');
const inlineButtonH = inlineH.root.querySelector('.extra-inline-card');
inlineH.fire(inlineButtonH, 'click');
assert.equal(inlineButtonH.getAttribute('aria-expanded'), 'true');
inlineH.fire(inlineButtonH, 'click');
assert.equal(inlineButtonH.getAttribute('aria-expanded'), 'false');
const faqH = interactiveModel('e-extra-accordion');
const faqButtonsH = faqH.root.querySelectorAll('[data-extra-action="accordion"]');
faqH.fire(faqButtonsH[1], 'click');
assert.equal(faqButtonsH[1].getAttribute('aria-expanded'), 'true');
assert.equal(faqButtonsH[0].getAttribute('aria-expanded'), 'false');
const reorderH = interactiveModel('e-data-reorder');
const listH = reorderH.root.querySelector('.sort-list');
const firstH = listH.firstElementChild;
reorderH.fire(reorderH.root.querySelector('[data-action="sort"]'), 'click');
assert.equal(listH.lastElementChild, firstH);
const filterH = interactiveModel('e-extra-filter-grid');
filterH.fire(filterH.root.querySelector('[data-value="摄影"]'), 'click');
filterH.flushTimeouts();
assert.equal(filterH.root.querySelector('.extra-filter-empty').hidden, false);
assert(filterH.root.querySelectorAll('.extra-gallery-tile').every(node => node.hidden));
filterH.fire(filterH.root.querySelector('[data-value="全部"]'), 'click');
filterH.flushTimeouts();
assert(filterH.root.querySelectorAll('.extra-gallery-tile').every(node => !node.hidden));
const chartH = interactiveModel('e-extra-chart-morph');
chartH.fire(chartH.root.querySelector('[data-value="previous"]'), 'click');
assert(chartH.root.querySelector('.extra-chart').getAttribute('aria-label').startsWith('上周'));
assert(chartH.root.querySelector('.extra-status').textContent.includes('260'));
const handoffH = interactiveModel('e-extra-skeleton-handoff');
handoffH.fire(handoffH.root.querySelector('[data-extra-action="load-content"]'), 'click');
assert([...handoffH.timeouts.values()].some(timer => timer.delay === 520));
handoffH.flushTimeouts();
assert([...handoffH.timeouts.values()].some(timer => timer.delay === 230));
handoffH.flushTimeouts();
assert.equal(handoffH.root.querySelector('.extra-content-skeleton').hidden, true);
assert.equal(handoffH.root.querySelector('.extra-content-real').hidden, false);
const shakeH = interactiveModel('e-data-input-shake');
shakeH.fire(shakeH.root.querySelector('.shake-go'), 'click');
assert.equal(shakeH.root.querySelector('.shake-err').hidden, false);
shakeH.root.querySelector('.shake-input').value = 'studio@example.com';
shakeH.fire(shakeH.root.querySelector('.shake-go'), 'click');
assert.equal(shakeH.root.querySelector('.shake-err').hidden, true);
const rollH = interactiveModel('e-extra-odometer');
rollH.fire(rollH.root.querySelector('[data-extra-action="roll"]'), 'click');
assert([...rollH.timeouts.values()].some(timer => timer.delay === 850));
rollH.flushTimeouts();
assert.equal(rollH.root.querySelector('.extra-digits').getAttribute('aria-label'), '当前数值 205');
console.log('Batch H: flip, switch, 420/1050ms morph, menu, tab indicator, inline expansion, accordion, reorder, filtering, chart, 520/230ms handoff, email and 850ms odometer passed.');


''')
            result=subprocess.run(['node',str(runner),str(fixture)],cwd=ROOT,text=True,capture_output=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertIn('194',result.stdout)
        self.assertIn('Command palette: 70 real candidates',result.stdout)
        self.assertIn('Motion modal: local sibling inert',result.stdout)
        self.assertIn('Batch B: skeleton loading/reduced motion',result.stdout)
        self.assertIn('Batch F: checkbox, slider, OTP paste/backspace', result.stdout)
        self.assertIn('Batch G: extracted guide table sorting and reset passed.', result.stdout)
        self.assertIn('Batch H: flip, switch, 420/1050ms morph', result.stdout)

    def test_real_index_matching_ranking_and_near_names(self):
        code = r'''
const assert = require('node:assert/strict');
const fs = require('node:fs');
const search = require('./site-src/redesign/search.js');
const entries = JSON.parse(fs.readFileSync('./build/entries.json','utf8'));
assert.equal(search.match(entries,'按钮')[0].entry.zh,'按钮');
assert.equal(search.match(entries,'  sPLit  BUtton  ')[0].entry.zh,'分裂按钮');
assert.equal(search.match(entries,'速度拨盘')[0].entry.zh,'悬浮按钮');
assert.equal(search.match(entries,'霓虹灯').length,0);
assert.equal(search.match(entries,'提交反馈状态链')[0].entry.slug,'submit');
assert.equal(search.match(entries,'删除退出与撤销')[0].entry.slug,'undo');
assert.equal(search.match(entries,'').length,0);
assert.deepEqual(search.similar(entries,'霓虹灯'),[]);
assert.equal(search.similar(entries,'交叉淡华')[0].zh,'交叉淡化');
const sample = [
 {zh:'q',en:'Other',terms:'',definition:''},
 {zh:'其他',en:'Q',terms:'',definition:''},
 {zh:'别名',en:'Other',terms:'q',definition:''},
 {zh:'描述',en:'Other',terms:'',definition:'q'}
];
assert.deepEqual(search.match(sample,'Q').map(row=>row.rank),[0,1,5,6]);
assert.equal(search.normalize('Ｂｕｔｔｏｎ '),'button');
console.log('Search matching and ranking passed');
'''
        result = subprocess.run(['node','-e',code], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(result.returncode,0,result.stderr)

    def test_demo_css_is_scoped_and_uses_local_palette(self):
        import re
        css = (ROOT / 'dist/assets/redesign/demos.css').read_text()
        self.assertNotIn('#1d4ed8',css.lower())
        self.assertNotRegex(css, r'#[0-9a-fA-F]{3,8}')
        self.assertNotRegex(css.lower(),r'dark|https?://|@import')
        for selector in re.findall(r'([^{}]+)\{[^{}]*\}',css):
            for part in selector.split(','):
                self.assertTrue(part.strip().startswith(('.demo-scope','.demo-secondary')),part)
        runtime=(ROOT/'dist/assets/redesign/demo-runtime.js').read_text()
        self.assertIn("attachShadow({mode: 'open'})",runtime)
        self.assertIn('shadow.querySelector',runtime)
        for kind in ('ui','motion','guide','skill-reference','token'):
            source=(ROOT/f'dist/assets/redesign/demo-{kind}.css').read_text()
            self.assertNotIn('#1d4ed8',source.lower())
            self.assertNotRegex(source,r'@import|https?://')
        for hook in ('holdBtn','splitCaret','fabBtn','copyDemoBtn','bttPage'):
            self.assertIn(hook,(ROOT/'dist/assets/redesign/demo-ui.js').read_text())

    def test_shared_search_accessibility_hooks_and_payloads(self):
        script=(ROOT/'site-src/redesign/site.js').read_text()
        self.assertIn("event.composedPath()[0]",script)
        self.assertIn("input.setAttribute('aria-activedescendant','result-' + selected)",script)
        self.assertIn('role="grid"',script)
        self.assertIn('aria-selected="${index === 0}"',script)
        home=(ROOT/'dist/index.html').read_text()
        self.assertIn('role="combobox"',home)
        data=json.loads((ROOT/'dist/assets/search-index.json').read_text())
        original=json.loads((ROOT/'build/entries.json').read_text())
        for row in data['entries']:
            entry = next(e for e in original if e['zh'] == row['zh'] and e['en'] == row['en'])
            self.assertEqual(row['terms'],entry['terms'])
            self.assertEqual(row['aliases'],entry.get('aliases',[]))
            self.assertIn(entry['prompt'],row['prompt'])
            for criterion in entry['acceptance']:self.assertIn(criterion,row['prompt'])
            if entry.get('prompt_secondary') and not entry.get('prompt_edit'):self.assertIn(entry['prompt_secondary'],row['prompt'])

    def test_redirect_scripts_execute_for_every_frozen_hash(self):
        code=r'''const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
let checked=0;
for(const old of ['ui','motion','layout','visual','interaction','pages','data','skills']){
 const html=fs.readFileSync('dist/'+old+'/index.html','utf8');
 const text=html.match(/id="redirect-map">(.*?)<\/script>/s)[1];
 const mapping=JSON.parse(text),script=html.match(/<script>(.*?)<\/script>/s)[1];
 const fallback=html.match(/content="0;url=([^"]+)"/)[1];
 for(const [anchor,target] of [...Object.entries(mapping),['',fallback],['unknown',fallback],['toString',fallback],['constructor',fallback],['__proto__',fallback],['%invalid',fallback]]){
  let actual;
  vm.runInNewContext(script,{document:{getElementById(){return {textContent:text}}},location:{hash:anchor?'#'+encodeURIComponent(anchor):'',replace(value){actual=value}}});
  assert.equal(actual,target,old+'#'+anchor);checked++;
 }
}
console.log('Redirect scripts passed '+checked+' hashes');'''
        result=subprocess.run(['node','-e',code],cwd=ROOT,text=True,capture_output=True)
        self.assertEqual(result.returncode,0,result.stderr)

    def test_preview_first_frames_and_long_running_action_guards(self):
        runtime=(ROOT/'site-src/redesign/demo-runtime.js').read_text()
        site=(ROOT/'site-src/redesign/site.js').read_text()
        self.assertIn('particlePreview(false)',runtime)
        self.assertIn('primeVirtualList()',runtime)
        self.assertIn('.tblfix-demo',runtime)
        self.assertIn('scrollLeft',runtime)
        self.assertIn('.extra-magnifier-art',runtime)
        self.assertIn("scope.dataset.demoKey === 'text-text-morph' ? 3000 : 2400",site)
        self.assertIn('clearResources()',runtime)
        self.assertIn('body.cloneNode(true)',runtime)


class AliasSearchTest(unittest.TestCase):
    def test_all_seven_ranks_and_alias_labels_in_node(self):
        code = r"""
const assert = require('node:assert/strict');
const search = require('./site-src/redesign/search.js');
const rows = [
 {zh:'末项', terms:'q'},
 {zh:'解释', definition:'contains q'},
 {zh:'口语包含', aliases:['prefix q suffix']},
 {zh:'名称包含q'},
 {zh:'英文包含', en:'prefix Q suffix'},
 {zh:'口语', aliases:['q']},
 {zh:'英文', en:'Other / Q'},
 {zh:'q'}
];
const result = search.match(rows,' Q ');
assert.deepEqual(result.map(row => row.rank), [0,1,2,3,3,4,5,6]);
assert.equal(search.aliasLabel(result[2]), '也叫：q');
assert.equal(search.aliasLabel(result[5]), '也叫：prefix q suffix');
assert.equal(search.aliasLabel(result[0]), '');
assert.equal(search.aliasLabel(result[1]), '');
assert.equal(search.aliasLabel(search.match([{zh:'q',aliases:['q']}],'q')[0]),'');
assert.equal(search.match([{zh:'a',en:'foo Q bar'}],'q')[0].rank,3);
assert.equal(search.match([{zh:'a',en:'One / Two'}],'tWo')[0].rank,1);
assert.deepEqual(search.match([{zh:'aq'},{zh:'bq'}],'q').map(row=>row.entry.zh),['aq','bq']);
assert.equal(search.match(rows,'').length,0);
"""
        result = subprocess.run(['node','-e',code], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        site = (ROOT/'site-src/redesign/site.js').read_text()
        self.assertIn('escape(VibeSearch.aliasLabel(row))', site)


class FuzzySearchTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run(['python3', 'scripts/build_site.py'], cwd=ROOT, check=True, capture_output=True)

    def run_node(self, code):
        result = subprocess.run(['node', '-e', code], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_strict_results_gate_fuzzy_append_and_keep_original_order(self):
        self.run_node(r"""
const assert = require('node:assert/strict');
const search = require('./site-src/redesign/search.js');
const strict = [{zh:'开关按钮'}, {en:'开关按钮'}, {aliases:['开关按钮']}];
const fuzzy = Array.from({length:12}, (_,i) => ({zh:'开关',slug:String(i)}));
const enough = search.match([...fuzzy,...strict],'开关按钮');
assert.deepEqual(enough.map(row=>row.rank),[0,1,2]);
assert.deepEqual(enough.map(row=>row.index),[12,13,14]);
for (const count of [0,1,2]) {
 const rows = search.match([...fuzzy,...strict.slice(0,count)],'开关按钮');
 assert.deepEqual(rows.slice(0,count).map(row=>row.rank),[0,1].slice(0,count));
 assert.equal(rows.filter(row=>row.rank === 7).length,8);
 assert.ok(rows.slice(count).every(row=>row.rank === 7));
 assert.equal(new Set(rows.map(row=>row.index)).size,rows.length);
 assert.deepEqual(rows.slice(count).map(row=>row.index),[0,1,2,3,4,5,6,7]);
}
""")

    def test_spoken_queries_hit_generated_homepage_index(self):
        self.run_node(r"""
const assert = require('node:assert/strict');
const fs = require('node:fs');
const search = require('./dist/assets/redesign/search.js');
const entries = JSON.parse(fs.readFileSync('dist/assets/search-index.json','utf8')).entries;
for (const [query,keys] of [
 ['开关按钮',['components/switch']],
 ['侧边滑出来的面板',['components/drawer','interactions/overlay-drawer']],
 ['输错了抖一下',['interactions/data-input-shake']],
 ['没有数据的时候显示什么',['components/empty']]
]) {
 const rows = search.match(entries,query);
 const top3 = rows.slice(0,3).map(row=>row.entry.href.replace(/^\.\//,'').replace(/\/$/,''));
 assert.ok(keys.some(key=>top3.includes(key)),query+' '+JSON.stringify(top3));
 assert.ok(rows.some(row=>row.rank === 7),query);
}
for (const query of ['qzxv','的的的','怎么的呢啊','霓虹灯','']) {
 assert.deepEqual(search.match(entries,query),[],query);
}
""")

    def test_fuzzy_field_weights_tokens_aliases_and_noise(self):
        self.run_node(r"""
const assert = require('node:assert/strict');
const search = require('./site-src/redesign/search.js');
const fields = [
 {definition:'侧边'}, {terms:'侧边'}, {aliases:['其他名称','侧边']}, {zh:'侧边'}
];
const rows = search.match(fields,'侧边面');
assert.deepEqual(rows.map(row=>row.index),[2,3,1,0]);
assert.ok(rows.every(row=>row.rank === 7));
assert.equal(rows[0].alias,'侧边');
assert.equal(search.aliasLabel(rows[0]),'也叫：侧边');
assert.equal(rows[1].alias,'');
assert.deepEqual(search.match([{zh:'侧滑'},{aliases:['边栏']}],'侧边浮层'),[]);
assert.deepEqual(search.match([{terms:'侧边'},{definition:'侧边'}],'侧边浮层'),[]);
assert.deepEqual(search.match([{zh:'面'},{aliases:['板']}],'侧边面板'),[]);
const english = [{en:'Toggle Switch'},{terms:'toggle switch'},{definition:'toggle switch'}];
assert.deepEqual(search.match(english,'please TOGGLE SWITCH now').map(row=>row.index),[0,1,2]);
assert.deepEqual(search.match(english,'please ＴＯＧＧＬＥ switch now'),search.match(english,'PLEASE toggle SWITCH NOW'));
assert.deepEqual(search.match([{en:'ToggleSwitch'}],'please toggle now'),[]);
const fragments = search.match([{aliases:['填错后输入框抖一下']},{aliases:['抖一下']}],'输错了抖一下');
assert.equal(fragments.length,1);
assert.equal(fragments[0].alias,'填错后输入框抖一下');
assert.equal(search.match([{zh:'浮起',aliases:['浮起来']}],'浮起来')[0].rank,2);
assert.equal(search.match([{zh:'悬浮',aliases:['鼠标放上去']}],'鼠标放上去')[0].rank,2);
""")


class SampleSearchTest(unittest.TestCase):
    def test_three_spoken_queries_hit_correct_entry_in_top_three(self):
        code = r"""
const assert = require('node:assert/strict');
const fs = require('node:fs');
const search = require('./site-src/redesign/search.js');
const entries = JSON.parse(fs.readFileSync('build/entries.json','utf8'));
const index = JSON.parse(fs.readFileSync('dist/assets/search-index.json','utf8')).entries;
for (const [query,slug] of [['浮起来','component-lift'],['弹出来的小黑框','tooltip'],['点了会变的按钮','button']]) {
 const expected = entries.find(entry=>entry.slug === slug);
 const result = search.match(index,query);
 assert.ok(result.slice(0,3).some(row=>row.entry.zh === expected.zh),query);
 assert.equal(search.aliasLabel(result.find(row=>row.entry.zh === expected.zh)), '也叫：'+query);
}
"""
        result = subprocess.run(['node','-e',code],cwd=ROOT,text=True,capture_output=True)
        self.assertEqual(result.returncode,0,result.stderr)


class BatchEToastRuntimeTest(unittest.TestCase):
    def test_toast_structure_is_scoped_and_reuses_the_existing_output(self):
        code = r'''
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const runtime = fs.readFileSync('site-src/redesign/demo-runtime.js','utf8');
const start = runtime.indexOf('    function toast(message) {');
const end = runtime.indexOf('    function mount() {',start);
assert.ok(start>=0 && end>start);
class Element {
  constructor(tag) { this.tag=tag; this.children=[]; this.attrs={}; this.dataset={}; }
  setAttribute(name,value) { this.attrs[name]=value; }
  set textContent(value) { this.text=String(value); this.children=[]; }
  get textContent() { return this.text || this.children.map(child=>child.textContent).join(''); }
  append(...children) { this.children.push(...children); }
}
function model(withPreview) {
  const body = new Element('article');
  const preview = withPreview ? new Element('div') : null;
  if (preview) { preview.dataset.toastDescription='操作已完成，可以继续当前工作。'; body.append(preview); }
  const shadow = {querySelector(selector) {
    if (selector==='.ds-toast-output') return preview;
    return [...body.children,...(preview?.children || [])].find(node=>node.className==='demo-status') || null;
  }};
  const context = {shadow,body,nativeDocument:{createElement:tag=>new Element(tag)}};
  vm.createContext(context);
  vm.runInContext(runtime.slice(start,end)+'this.renderToast=toast;',context);
  return {body,preview,render:context.renderToast};
}
const plain = model(false);
plain.render('已开启'); plain.render('已关闭');
assert.equal(plain.body.children.length,1);
assert.equal(plain.body.children[0].textContent,'已关闭');
assert.equal(plain.body.children[0].attrs['aria-live'],'polite');
const specimen = model(true);
const message = '<b>这是一条提示 ✔</b>';
specimen.render(message);
const output = specimen.preview.children[0];
assert.equal(output.children.length,3);
assert.equal(output.children[0].className,'ds-toast-icon');
assert.equal(output.children[0].attrs['aria-hidden'],'true');
assert.equal(output.children[1].className,'ds-toast-title');
assert.equal(output.children[1].textContent,message);
assert.equal(output.children[2].className,'ds-toast-description');
assert.equal(output.children[2].textContent,specimen.preview.dataset.toastDescription);
specimen.render('第二条反馈');
assert.equal(specimen.preview.children.length,1);
assert.equal(specimen.preview.children[0],output);
assert.equal(output.children[1].textContent,'第二条反馈');
console.log('Scoped toast icon/title/description, plain feedback and output reuse passed.');
'''
        result = subprocess.run(['node', '-e', code], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


class BatchHRuntimeTest(unittest.TestCase):
    def test_h_touch_preview_is_scoped_and_keeps_keyboard_actions(self):
        runtime = (ROOT / 'site-src/redesign/demo-runtime.js').read_text()
        self.assertIn("'.ds-h-demo .tilt-card,.ds-h-demo .spot-card,.ds-h-demo .hvp-link,.ds-h-demo .hact-card,.ds-h-demo .magnet-btn'", runtime)
        self.assertIn("target.classList.toggle('touch-closed', !open)", runtime)
        self.assertIn("target.setAttribute('aria-expanded', String(open))", runtime)
        self.assertIn("event.target !== target || target.tagName === 'BUTTON'", runtime)

    def test_h_touch_and_keyboard_listener_behavior_in_node(self):
        code = r'''
const fs = require('node:fs'), assert = require('node:assert/strict');
const runtime = fs.readFileSync('site-src/redesign/demo-runtime.js', 'utf8');
const marker = runtime.indexOf("        shadow.querySelectorAll('.ds-h-demo");
const start = runtime.lastIndexOf("      if (scope.hasAttribute('data-interactive')) {", marker);
const end = runtime.indexOf("      const tooltip =", marker);
const source = runtime.slice(start, end);
let touch = true;
function target(tagName = 'DIV') {
  const classes = new Set(), listeners = new Map(), attrs = {};
  return {tagName, attrs, listeners,
    classList:{
      contains:name => classes.has(name),
      add:name => classes.add(name),
      remove:name => classes.delete(name),
      toggle(name, force) {const value = force === undefined ? !classes.has(name) : force; value ? classes.add(name) : classes.delete(name); return value;}
    },
    setAttribute(name, value) {attrs[name] = value;},
    addEventListener(name, callback) {listeners.set(name, callback);},
    closest() {return null;}
  };
}
const targets = [target(), target(), target('SPAN'), target(), target('BUTTON')];
new Function('scope','shadow','nativeWindow',source)(
  {hasAttribute:name => name === 'data-interactive'},
  {querySelectorAll:() => targets},
  {matchMedia:() => ({matches:touch})}
);
for (const node of targets) {
  node.listeners.get('click')({target:node});
  assert(node.classList.contains('touch-open'));
  assert.equal(node.attrs['aria-expanded'], 'true');
  node.listeners.get('click')({target:node});
  assert(!node.classList.contains('touch-open'));
  assert(node.classList.contains('touch-closed'));
  node.listeners.get('pointerenter')({pointerType:'mouse'});
  assert(!node.classList.contains('touch-closed'));
}
touch = false;
const node = targets[0];
node.listeners.get('click')({target:node});
assert(!node.classList.contains('touch-open'));
let prevented = false;
node.listeners.get('keydown')({target:node,key:'Enter',preventDefault(){prevented=true;}});
assert(prevented && node.classList.contains('touch-open'));
node.listeners.get('keydown')({target:node,key:'Escape'});
assert(!node.classList.contains('touch-open'));
assert.equal(node.attrs['aria-expanded'], 'false');
node.listeners.get('focusin')();
assert(!node.classList.contains('touch-closed'));
const button = targets[4];
button.listeners.get('keydown')({target:button,key:'Enter',preventDefault(){throw new Error('Native button key was intercepted');}});
assert(!button.classList.contains('touch-open'));
console.log('Five H touch targets, second-tap close, keyboard open/Escape, native button keys and pointer/focus restoration passed.');
'''
        result = subprocess.run(['node', '-e', code], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
