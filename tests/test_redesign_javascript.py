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
            result=subprocess.run(['node',str(ROOT/'site-src/redesign/demo-smoke.cjs'),str(fixture)],cwd=ROOT,text=True,capture_output=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertIn('189',result.stdout)

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
assert.equal(search.similar(entries,'霓虹灯').length,3);
const sample = [
 {zh:'q',en:'Other',terms:'',definition:''},
 {zh:'其他',en:'Q',terms:'',definition:''},
 {zh:'别名',en:'Other',terms:'q',definition:''},
 {zh:'描述',en:'Other',terms:'',definition:'q'}
];
assert.deepEqual(search.match(sample,'Q').map(row=>row.rank),[0,1,2,3]);
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
        for kind in ('ui','motion','guide','skill-reference'):
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
        import re
        data=json.loads(re.search(r'id="redesign-search-index">(.*?)</script>',home,re.S)[1])
        original=json.loads((ROOT/'build/entries.json').read_text())
        for row,entry in zip(data['entries'],original):
            self.assertEqual(row['terms'],entry['terms'])
            self.assertIn(entry['prompt'],row['prompt'])
            for criterion in entry['acceptance']:self.assertIn(criterion,row['prompt'])
            if entry.get('prompt_secondary'):self.assertIn(entry['prompt_secondary'],row['prompt'])

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
