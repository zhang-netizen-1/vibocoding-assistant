from pathlib import Path
from playwright.sync_api import sync_playwright

URL = (Path(__file__).resolve().parents[2] / '动效速查.html').as_uri()


def drag(page, locator, dx=0, dy=0, release=True):
    locator.scroll_into_view_if_needed()
    box = locator.bounding_box()
    x, y = box['x'] + box['width'] / 2, box['y'] + box['height'] / 2
    page.mouse.move(x, y)
    page.mouse.down()
    page.mouse.move(x + dx, y + dy, steps=8)
    if release:
        page.mouse.up()
    return x, y


def check(page, name, condition):
    assert condition, name
    print('PASS', name)


with sync_playwright() as pw:
    browser = pw.chromium.launch()
    page = browser.new_page(viewport={'width': 1440, 'height': 900})
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.goto(URL)
    # Keep pointer coordinates stable while the audit jumps between distant cards.
    page.evaluate('document.documentElement.style.scrollBehavior = "auto"')
    failures = []

    def run(name, fn):
        try:
            fn()
        except Exception as error:
            failures.append(f'{name}: {error}')
            print('FAIL', name, str(error)[:220])
            page.keyboard.press('Escape')

    def modal():
        opener = page.locator('#e-overlay-modal [data-action=open]')
        opener.click()
        dialog = page.locator('#e-overlay-modal [role=dialog]')
        check(page, 'modal aria', dialog.get_attribute('aria-modal') == 'true')
        page.keyboard.press('Tab')
        check(page, 'modal trap', page.evaluate('document.activeElement.closest("#e-overlay-modal [role=dialog]") !== null'))
        # Programmatic background activation should be disabled as well.
        check(page, 'modal background inert', page.locator('#e-view-crossfade .stage').evaluate('(e) => e.inert || !!e.closest("[inert]")'))
        page.keyboard.press('Escape')
        check(page, 'modal focus returned', opener.evaluate('(e) => document.activeElement === e'))
        opener = page.locator('#e-overlay-drawer [data-action=open]')
        opener.click()
        check(page, 'drawer modal', page.locator('#e-overlay-drawer [role=dialog]').get_attribute('aria-modal') == 'true')
        page.keyboard.press('Escape')
        opener = page.locator('#e-overlay-sheet [data-action=open]')
        opener.click()
        check(page, 'sheet dialog role', page.locator('#e-overlay-sheet .sheet').get_attribute('role') == 'dialog')
        page.keyboard.press('Escape')

    def menu():
        menu = page.locator('#e-overlay-menu')
        menu.locator('[data-action=toggle]').click()
        delays = menu.locator('.menu-items button').evaluate_all('(es)=>es.map(e=>parseFloat(getComputedStyle(e).animationDelay))')
        check(page, 'menu stagger', delays == sorted(delays) and len(set(delays)) == 3)
        menu.locator('.card-note').click()
        check(page, 'menu outside closes', menu.locator('.menu-items').is_hidden())

    def swipe():
        card = page.locator('#e-mobile-swipe')
        following = card.locator('.swipe-next')
        def relative_y():
            return following.evaluate('(e)=>e.getBoundingClientRect().y-e.closest(".swipe-demo").getBoundingClientRect().y')
        before = relative_y()
        drag(page, card.locator('.swipe-item'), dx=-112)
        card.locator('.swipe-slot.dismissed').wait_for(timeout=3000)
        page.wait_for_function('''() => {let e=document.querySelector('#e-mobile-swipe .swipe-next');return e.getBoundingClientRect().y-e.closest('.swipe-demo').getBoundingClientRect().y < 35}''',timeout=3000)
        after = relative_y()
        check(page, 'swipe reflow', after < before - 20)
        check(page, 'swipe accessibility', card.locator('.swipe-item').get_attribute('aria-hidden') == 'true')
        card.locator('[data-action=reset]').click()
        page.wait_for_function('''() => {let e=document.querySelector('#e-mobile-swipe .swipe-next');return e.getBoundingClientRect().y-e.closest('.swipe-demo').getBoundingClientRect().y > 53}''',timeout=3000)
        check(page, 'swipe reset', abs(relative_y() - before) < 3)

    def pull():
        zone = page.locator('#e-mobile-pull .pull-zone')
        check(page, 'pull scrollable', zone.evaluate('(e)=>e.scrollHeight > e.clientHeight && getComputedStyle(e).overflowY === "auto"'))
        zone.evaluate('(e)=>e.scrollTop = 40')
        before = zone.get_attribute('data-refresh-count')
        drag(page, zone, dy=80)
        check(page, 'pull not from middle', zone.get_attribute('data-refresh-count') == before)
        zone.evaluate('(e)=>e.scrollTop = 0')
        drag(page, zone, dy=85)
        check(page, 'pull loading feedback', '正在刷新' in zone.locator('.pull-indicator').inner_text())
        page.wait_for_function('''() => document.querySelector('#e-mobile-pull .pull-zone').dataset.refreshCount === '1' ''',timeout=3000)
        check(page, 'pull updates data', int(zone.get_attribute('data-refresh-count')) == 1)
        check(page, 'pull changes content', '已更新' in zone.inner_text())

    def live_reorder():
        rows = page.locator('#e-mobile-drag .drag-list [data-drag=reorder]')
        first = rows.first
        drag(page, first, dy=40, release=False)
        check(page, 'drag live order', '第二项' in rows.first.inner_text())
        page.mouse.up()

    def comparison():
        card = page.locator('#e-media-compare')
        sources = card.locator('.compare .art').evaluate_all('(es)=>es.map(e=>getComputedStyle(e).backgroundImage)')
        check(page, 'comparison same scene', sources[0] == sources[1] and sources[0] != 'none')

    def carousel():
        card = page.locator('#e-media-carousel')
        status = card.locator('.carousel-status')
        check(page, 'carousel initial index', '1 / 3' in status.inner_text())
        card.locator('[data-action=next]').click()
        check(page, 'carousel changes index', '2 / 3' in status.inner_text())
        check(page, 'carousel current aria', card.locator('.media-track [aria-current=true]').count() == 1)

    def shared():
        card = page.locator('#e-view-shared')
        node = card.locator('.shared-chip')
        node.scroll_into_view_if_needed()
        def relative_geom():
            return node.evaluate('(e)=>{let a=e.getBoundingClientRect(),b=e.parentElement.getBoundingClientRect();return {x:a.x-b.x,y:a.y-b.y,width:a.width,height:a.height}}')
        before = relative_geom()
        node.click()
        page.wait_for_function('''() => document.querySelector('#e-view-shared .shared-chip').getBoundingClientRect().width > 180''',timeout=3000)
        after = relative_geom()
        check(page, 'shared two-view trajectory', after['x'] - before['x'] > 15 and after['width'] - before['width'] > 80)
        check(page, 'shared overview/detail', card.locator('.shared-origin-label,.shared-destination-label').count() == 2)

    def states():
        chip = page.locator('.chip[data-filter=all]')
        check(page, 'category aria initial', chip.get_attribute('aria-pressed') == 'true')
        page.locator('.chip[data-filter=mobile]').click()
        check(page, 'category aria toggles', page.locator('.chip[data-filter=mobile]').get_attribute('aria-pressed') == 'true' and chip.get_attribute('aria-pressed') == 'false')
        chip.click()
        flip = page.locator('#e-component-flip .flip-card')
        check(page, 'flip front name', '正面' in (flip.get_attribute('aria-label') or '') and '背面' not in (flip.get_attribute('aria-label') or ''))
        flip.click()
        check(page, 'flip back name', '背面' in (flip.get_attribute('aria-label') or '') and '正面' not in (flip.get_attribute('aria-label') or ''))

    def loops():
        wave = page.locator('#e-background-wave .dots i').first
        page.evaluate('window.scrollTo(0, 0)')
        page.wait_for_timeout(250)
        check(page, 'offscreen wave paused', wave.evaluate('(e)=>getComputedStyle(e).animationPlayState === "paused"'))
        wave.scroll_into_view_if_needed()
        page.wait_for_timeout(250)
        check(page, 'onscreen wave runs', wave.evaluate('(e)=>getComputedStyle(e).animationPlayState === "running"'))

    def contrast():
        styles = page.evaluate('''() => {let s=getComputedStyle(document.documentElement);return [s.getPropertyValue('--faint').trim(),getComputedStyle(document.querySelector('.stage-label')).color]}''')
        def rgb(value):
            import re
            if value.startswith('#'):
                return [int(value[i:i+2],16)/255 for i in (1,3,5)]
            return [int(v)/255 for v in re.findall(r'\d+',value)[:3]]
        def luminance(value):
            c=rgb(value);c=[x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4 for x in c]
            return sum(x*y for x,y in zip(c,(.2126,.7152,.0722)))
        def ratio(a,b):
            lo,hi=sorted((luminance(a),luminance(b)))
            return (hi+.05)/(lo+.05)
        check(page, 'faint on input >=4.5', ratio(styles[0],'#1a1a25') >= 4.5)
        check(page, 'stage label >=4.5', ratio(styles[1],'#f6f7fb') >= 4.5)

    for name, fn in [('modal', modal),('menu',menu),('swipe',swipe),('pull',pull),('live reorder',live_reorder),('comparison',comparison),('carousel',carousel),('shared',shared),('states',states),('loops',loops),('contrast',contrast)]:
        run(name,fn)
    reduced = browser.new_page(reduced_motion='reduce')
    reduced.goto(URL)
    stack = reduced.locator('#e-view-crossfade .view-stack')
    initial = stack.evaluate('(e)=>[getComputedStyle(e.querySelector(".view-a")).opacity,getComputedStyle(e.querySelector(".view-b")).opacity]')
    if initial != ['1','0']:
        failures.append('reduced crossfade initial '+str(initial))
    reduced.locator('#e-view-crossfade [data-action=next]').click()
    final = stack.evaluate('(e)=>[getComputedStyle(e.querySelector(".view-a")).opacity,getComputedStyle(e.querySelector(".view-b")).opacity]')
    if final != ['0','1']:
        failures.append('reduced crossfade next '+str(final))
    mobile = browser.new_page(viewport={'width':390,'height':844},has_touch=True,is_mobile=True)
    mobile.goto(URL)
    trigger = mobile.locator('#e-overlay-tooltip .tooltip-trigger')
    trigger.tap()
    mobile.wait_for_function('''() => getComputedStyle(document.querySelector('#e-overlay-tooltip [role=tooltip]')).opacity === '1' ''',timeout=3000)
    if trigger.locator('[role=tooltip]').evaluate('(e)=>getComputedStyle(e).opacity') != '1':
        failures.append('touch tooltip invisible')
    if errors:
        failures.append('page errors: '+repr(errors))
    browser.close()
    if failures:
        raise AssertionError('\n'.join(failures))
    print('PASS all audit regressions')
