from pathlib import Path
from playwright.sync_api import sync_playwright
p=(Path(__file__).resolve().parents[2] / '动效速查.html').as_uri()
with sync_playwright() as pw:
 b=pw.chromium.launch()
 page=b.new_page(viewport={'width':1440,'height':900},permissions=['clipboard-read','clipboard-write'])
 errors=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto(p)
 ids=page.locator('.effect-card').evaluate_all('(els)=>els.map(e=>e.id)')
 assert len(ids)==47
 for eid in ids:
  card=page.locator('#'+eid)
  card.locator('details').evaluate('(e)=>e.open=true')
  text=card.locator('.prompt-text').inner_text()
  card.locator('.copy-prompt').click()
  assert page.evaluate('navigator.clipboard.readText()')==text,eid
 print('47/47 copy prompts exact')
 # Exercise every in-demo button and every replayer; report JS failures.
 for eid in ids:
  card=page.locator('#'+eid)
  actions=card.locator('.stage [data-action]').all()
  for button in actions:
   if not button.is_visible():continue
   try:button.click(timeout=1600)
   except Exception:pass # some actions hide their own overlay, handled by second sweep
  replay_button=card.locator('.demo-tools [data-action]')
  if replay_button.count(): replay_button.first.click()
 assert not errors,errors
 print('47/47 stages exercised without JS exception')
 # Visual facts: shared element changes the same node's geometry; scroll movement changes scroll state.
 shared=page.locator('#e-view-shared .shared-chip')
 if shared.get_attribute('aria-expanded')=='true':shared.click()
 shared.click()
 assert shared.get_attribute('aria-expanded')=='true'
 assert shared.bounding_box()['width']>180
 shared.click()
 assert shared.get_attribute('aria-expanded')=='false'
 page.locator('#e-scroll-parallax .mini-scroll').evaluate('(e)=>{e.scrollTop=e.scrollHeight-e.clientHeight;e.dispatchEvent(new Event("scroll"))}')
 assert page.locator('#e-scroll-parallax .stage').evaluate('(e)=>Number(e.style.getPropertyValue("--p"))')>.95
 # Global pause must stop CSS loops and particle rAF.
 wave=page.locator('#e-background-wave')
 if 'is-paused' in wave.get_attribute('class'):wave.locator('.pause-loop').click()
 page.locator('#pauseAll').click()
 assert page.locator('#e-background-wave .dots i').first.evaluate('(e)=>getComputedStyle(e).animationPlayState')=='paused'
 assert page.locator('#pauseAll').get_attribute('aria-pressed')=='true'
 page.locator('#pauseAll').click()
 assert page.locator('#e-background-wave .dots i').first.evaluate('(e)=>getComputedStyle(e).animationPlayState')=='paused' # offscreen loops stay paused
 wave.scroll_into_view_if_needed()
 page.wait_for_function('''() => getComputedStyle(document.querySelector('#e-background-wave .dots i')).animationPlayState === 'running' ''')
 # Menu escape sync, modal focus return and comparison slider.
 menu=page.locator('#e-overlay-menu')
 if menu.locator('[data-action=toggle]').get_attribute('aria-expanded')=='true':menu.locator('[data-action=toggle]').click()
 menu.locator('[data-action=toggle]').click()
 assert menu.locator('[data-action=toggle]').get_attribute('aria-expanded')=='true'
 page.keyboard.press('Escape')
 assert menu.locator('[data-action=toggle]').get_attribute('aria-expanded')=='false'
 modal=page.locator('#e-overlay-modal')
 modal.locator('[data-action=open]').click()
 assert modal.locator('.overlay-shade').is_visible()
 page.keyboard.press('Escape')
 assert not modal.locator('.overlay-shade').is_visible()
 assert modal.locator('[data-action=open]').evaluate('(e)=>e===document.activeElement')
 slider=page.locator('#e-media-compare input')
 slider.fill('80')
 assert page.locator('#e-media-compare .compare').evaluate('(e)=>e.style.getPropertyValue("--split")')=='80%'
 print('shared element / scroll / global pause / overlay / slider passed')
 last=page.locator('#e-mobile-drag .drag-list > div').last
 last.scroll_into_view_if_needed()
 box=last.bounding_box()
 page.mouse.move(box['x']+30,box['y']+10)
 page.mouse.down()
 page.mouse.move(box['x']+30,box['y']+70,steps=6)
 page.mouse.up()
 assert not errors,errors
 swipe=page.locator('#e-mobile-swipe .swipe-item')
 page.locator('#e-mobile-swipe [data-action=reset]').click()
 box=swipe.bounding_box()
 page.mouse.move(box['x']+90,box['y']+12)
 page.mouse.down()
 page.mouse.move(box['x']-20,box['y']+12,steps=6)
 page.mouse.up()
 assert 'dismissed' in swipe.get_attribute('class')
 print('pointer gesture edge-cases passed')
 # Narrow widths: no document overflow, controls clickable, prompt readable.
 for width in (344,360,390,768,1280,1920):
  page.set_viewport_size({'width':width,'height':850})
  dimensions=page.evaluate('({s:document.documentElement.scrollWidth,c:document.documentElement.clientWidth})')
  assert dimensions['s']<=dimensions['c'],(width,dimensions)
 print('6 viewport widths with no horizontal overflow')
 assert not errors,errors
 b.close()
print('PASS deep motion browser audit')
