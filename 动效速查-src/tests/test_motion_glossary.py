from pathlib import Path
from playwright.sync_api import sync_playwright

FILE = Path(__file__).resolve().parents[2] / '动效速查.html'
EXPECTED = {'view','scroll','background','text','media','component','overlay','data','mobile'}


def test_motion_glossary():
    assert FILE.exists(), '动效速查.html 尚未创建（预期 RED）'
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        errors = []
        context = browser.new_context(viewport={'width':1440,'height':900}, permissions=['clipboard-read','clipboard-write'])
        page = context.new_page()
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.goto(FILE.as_uri())
        cards = page.locator('article.effect-card')
        assert cards.count() == 65, f'效果卡数：{cards.count()}'
        assert set(cards.evaluate_all('(els)=>els.map(e=>e.dataset.cat)')) == EXPECTED
        assert page.get_by_text('波浪矩阵', exact=True).count() >= 1
        assert page.locator('article.effect-card .stage').count() == 65
        prompts = cards.locator('.prompt-text').all_text_contents()
        assert len(prompts) == len(set(prompts)) == 65
        forbidden = ['订单','报销','购物车','用户资料','登录页','商品详情','虚构接口']
        assert all(not any(w in s for w in forbidden) for s in prompts)
        assert all('沿用项目现有设计规范' in s for s in prompts)
        for i in (0,4,12,21,31,40,46):
            card = cards.nth(i)
            card.locator('details').evaluate('(e)=>e.open=true')
            card.locator('button.copy-prompt').click()
            copied = page.evaluate('navigator.clipboard.readText()')
            assert copied == card.locator('.prompt-text').text_content(), (i, copied)
        # 真交互而非 toast 充数
        switch = page.locator('#e-component-switch [role=switch]')
        assert switch.count() == 1
        old = switch.get_attribute('aria-checked')
        switch.click()
        assert switch.get_attribute('aria-checked') != old
        nav = page.locator('#e-view-crossfade [data-action=next]')
        stack = page.locator('#e-view-crossfade .view-stack')
        assert stack.locator('.view-a, .view-b').count() == 2, '交叉淡化必须有同时存在的出入场层'
        before = stack.locator('.view-a').evaluate('(e)=>getComputedStyle(e).opacity')
        nav.click()
        page.wait_for_timeout(650)
        assert float(stack.locator('.view-a').evaluate('(e)=>getComputedStyle(e).opacity')) < float(before)
        assert float(stack.locator('.view-b').evaluate('(e)=>getComputedStyle(e).opacity')) > 0.9
        page.locator('#q').fill('波浪')
        assert page.locator('article.effect-card:visible').count() >= 1
        page.locator('#q').fill('不可能匹配的字符xyz')
        assert page.locator('#empty').is_visible()
        page.locator('#q').fill('')
        assert page.locator('article.effect-card:visible').count() == 65
        assert not errors, errors
        for width in (1440,390,344):
            page.set_viewport_size({'width':width,'height':860})
            page.wait_for_timeout(120)
            over = page.evaluate('document.documentElement.scrollWidth-innerWidth')
            assert over == 0, (width,over)
        context.close()
        reduced = browser.new_context(reduced_motion='reduce',viewport={'width':390,'height':844})
        pr = reduced.new_page()
        pr.goto(FILE.as_uri())
        assert pr.locator('article.effect-card').count() == 65
        assert pr.locator('#e-background-particles .stage').is_visible()
        reduced.close()
        browser.close()
    print('PASS: 9 类 / 65 真实演示 / 复制逐字一致 / 交互 / 筛选 / 移动 / 减弱动态')

if __name__ == '__main__':
    test_motion_glossary()
