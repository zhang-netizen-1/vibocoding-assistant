"""Browser smoke audit for the eighteen additional motion studies."""

from pathlib import Path

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[2]


def card(page, name):
    return page.locator(f'#e-extra-{name}')


with sync_playwright() as pw:
    browser = pw.chromium.launch()
    page = browser.new_page(viewport={'width': 1440, 'height': 900})
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.goto((ROOT / '动效速查.html').as_uri())
    page.evaluate('document.documentElement.style.scrollBehavior = "auto"')
    assert page.locator('.effect-card').count() == 65

    grid = card(page, 'filter-grid')
    grid.locator('[data-value="界面"]').click()
    page.wait_for_timeout(240)
    assert grid.locator('.extra-gallery-tile:visible').count() == 2
    grid.locator('[data-value="摄影"]').click()
    page.wait_for_timeout(240)
    assert grid.locator('.extra-filter-empty').is_visible()
    assert '0 个作品' in grid.locator('.extra-status').inner_text()

    deletion = card(page, 'delete-undo')
    deletion.locator('[data-extra-action=delete]').first.click()
    page.wait_for_timeout(260)
    assert deletion.locator('.extra-task:visible').count() == 2
    deletion.locator('[data-extra-action=undo]').click()
    assert deletion.locator('.extra-task:visible').count() == 3

    faq = card(page, 'accordion')
    faq.locator('.extra-faq button').nth(1).click()
    assert faq.locator('.extra-faq button').nth(1).get_attribute('aria-expanded') == 'true'
    assert faq.locator('.extra-faq button').first.get_attribute('aria-expanded') == 'false'

    form = card(page, 'submit-flow')
    form.locator('[data-value=invalid]').click()
    form.locator('[data-extra-action=submit]').click()
    page.wait_for_timeout(560)
    assert '至少 4 个字符' in form.locator('.extra-field-error').inner_text()
    form.locator('input').fill('完整名称')
    form.locator('[data-extra-action=submit]').click()
    page.wait_for_timeout(560)
    assert '成功' in form.locator('.extra-status').inner_text()

    notices = card(page, 'toast-stack')
    notices.locator('[data-extra-action=add-toast]').click()
    assert notices.locator('.extra-notice').count() == 2
    notices.locator('[data-extra-action=remove-toast]').first.click()
    page.wait_for_timeout(240)
    assert notices.locator('.extra-notice').count() == 1

    tabs = card(page, 'tab-indicator')
    tabs.locator('[role=tab]').first.focus()
    page.keyboard.press('ArrowRight')
    assert tabs.locator('[role=tab][aria-selected=true]').inner_text() == '活动'

    drop = card(page, 'drop-snap')
    chip = drop.locator('.extra-drag-chip')
    target = drop.locator('.extra-drop-target[data-target="稍后"]')
    chip.scroll_into_view_if_needed()
    start, end = chip.bounding_box(), target.bounding_box()
    page.mouse.move(start['x'] + start['width'] / 2, start['y'] + start['height'] / 2)
    page.mouse.down()
    page.mouse.move(end['x'] + end['width'] / 2, end['y'] + end['height'] / 2, steps=10)
    page.mouse.up()
    assert chip.evaluate('(e) => e.parentElement.dataset.target') == '稍后'
    drop.locator('[data-extra-action=reset-drop]').click()
    assert chip.evaluate('(e) => e.parentElement.classList.contains("extra-drop-source")')

    digits = card(page, 'odometer')
    digits.locator('[data-extra-action=roll]').click()
    page.wait_for_timeout(880)
    assert digits.locator('.extra-digits').get_attribute('aria-label') == '当前数值 205'

    frame = card(page, 'cross-page').frame_locator('iframe')
    frame.locator('a[href="motion-demo-detail.html"]').click()
    frame.get_by_role('heading', name='山间日落').wait_for()
    frame.locator('a[href="motion-demo-gallery.html"]').click()
    frame.get_by_role('heading', name='选择一张作品').wait_for()

    expanded = card(page, 'inline-expand').locator('.extra-inline-card')
    old_height = expanded.bounding_box()['height']
    expanded.click()
    page.wait_for_timeout(400)
    assert expanded.bounding_box()['height'] > old_height + 10

    header = card(page, 'shrink-header').locator('.extra-header-scroll')
    header.evaluate('(e) => e.scrollTop = 80')
    page.wait_for_timeout(70)
    assert header.locator('.extra-scroll-header').evaluate('(e) => parseFloat(e.style.minHeight)') < 70

    sections = card(page, 'section-nav')
    sections.locator('.extra-section-scroll').evaluate('(e) => e.scrollTop = 170')
    page.wait_for_timeout(70)
    assert sections.locator('.extra-section-links [aria-current=true]').inner_text() == '02'

    highlighting = card(page, 'scroll-highlight')
    highlighting.locator('.extra-highlight-scroll').evaluate('(e) => e.scrollTop = e.scrollHeight')
    page.wait_for_timeout(70)
    assert highlighting.locator('.extra-highlight-text .lit').count() == 4

    snapping = card(page, 'snap-sections')
    snapping.locator('.extra-snap-scroll').evaluate('(e) => e.scrollTop = 168')
    page.wait_for_timeout(170)
    assert '02 / 03' in snapping.locator('.extra-snap-status').inner_text()

    magnifier = card(page, 'image-magnifier').locator('.extra-magnifier-art')
    magnifier.scroll_into_view_if_needed()
    bounds = magnifier.bounding_box()
    page.mouse.move(bounds['x'] + bounds['width'] / 2, bounds['y'] + bounds['height'] / 2)
    assert magnifier.locator('.extra-magnifier-lens').is_visible()

    timeline = card(page, 'timeline-preview')
    timeline.locator('input[type=range]').evaluate('''(e) => {e.value = 30; e.dispatchEvent(new Event('input', {bubbles:true})); e.dispatchEvent(new Event('change', {bubbles:true}));}''')
    assert '00:30' in timeline.locator('.extra-video-time').inner_text()

    chart = card(page, 'chart-morph')
    chart.locator('[data-value=previous]').click()
    assert '260' in chart.locator('.extra-status').inner_text()

    content = card(page, 'skeleton-handoff')
    content.locator('[data-extra-action=load-content]').click()
    page.wait_for_timeout(800)
    assert content.locator('.extra-content-real').is_visible()

    assert not errors, errors
    for width in (1440, 768, 390, 344):
        page.set_viewport_size({'width': width, 'height': 850})
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), width

    reduced = browser.new_page(viewport={'width': 390, 'height': 844}, reduced_motion='reduce')
    reduced.goto((ROOT / '动效速查.html').as_uri())
    reduced_grid = card(reduced, 'filter-grid')
    reduced_grid.locator('[data-value="摄影"]').click()
    assert reduced_grid.locator('.extra-filter-empty').is_visible()
    reduced_art = card(reduced, 'image-magnifier').locator('.extra-magnifier-art')
    reduced_art.scroll_into_view_if_needed()
    bounds = reduced_art.bounding_box()
    reduced.mouse.move(bounds['x'] + bounds['width'] / 2, bounds['y'] + bounds['height'] / 2)
    assert reduced_art.locator('.extra-magnifier-lens').is_visible()
    reduced_header = card(reduced, 'shrink-header').locator('.extra-header-scroll')
    reduced_header.evaluate('(e) => e.scrollTop = 80')
    reduced.wait_for_timeout(70)
    assert reduced_header.locator('.extra-scroll-header').evaluate('(e) => parseFloat(e.style.minHeight)') == 94
    browser.close()

print('PASS 18 new motion interactions, responsive layout, and reduced motion')
