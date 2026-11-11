"""Build the public field guide from an explicit source allowlist."""

from pathlib import Path
import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parent.parent
SITE_SOURCE = ROOT / "site-src"
OUTPUT = ROOT / "dist"
MARKER = ".generated-site"
GUIDE_MODULE_SPEC = importlib.util.spec_from_file_location("guide_pages", SITE_SOURCE / "guide_pages.py")
GUIDE_MODULE = importlib.util.module_from_spec(GUIDE_MODULE_SPEC)
GUIDE_MODULE_SPEC.loader.exec_module(GUIDE_MODULE)
GUIDES = GUIDE_MODULE.GUIDES
SKILL_MODULE_SPEC = importlib.util.spec_from_file_location("skill_catalog", SITE_SOURCE / "skill_catalog.py")
SKILL_MODULE = importlib.util.module_from_spec(SKILL_MODULE_SPEC)
SKILL_MODULE_SPEC.loader.exec_module(SKILL_MODULE)
SEARCH_MODULE_SPEC = importlib.util.spec_from_file_location("search_index", SITE_SOURCE / "search_index.py")
SEARCH_MODULE = importlib.util.module_from_spec(SEARCH_MODULE_SPEC)
SEARCH_MODULE_SPEC.loader.exec_module(SEARCH_MODULE)
BENCH_MODULE_SPEC = importlib.util.spec_from_file_location("bench_pages", SITE_SOURCE / "bench_pages.py")
BENCH_MODULE = importlib.util.module_from_spec(BENCH_MODULE_SPEC)
BENCH_MODULE_SPEC.loader.exec_module(BENCH_MODULE)


ENTRY_MODULE = importlib.util.spec_from_file_location("entries", SITE_SOURCE / "entries.py")
ENTRY_ADAPTER = importlib.util.module_from_spec(ENTRY_MODULE)
ENTRY_MODULE.loader.exec_module(ENTRY_ADAPTER)


REDESIGN_SPEC = importlib.util.spec_from_file_location("redesign_templates", SITE_SOURCE / "redesign/templates.py")
REDESIGN = importlib.util.module_from_spec(REDESIGN_SPEC)
REDESIGN_SPEC.loader.exec_module(REDESIGN)
import redirects

LEGACY_ASSETS = ("favicon.svg", "bench.css")


def expected_build_files(entries):
    bench = SITE_SOURCE / "bench"
    files = {MARKER, "index.html", "skills/index.html", *(f"{section}/index.html" for section, *_ in PAGES), *(f"{slug}/index.html" for slug in GUIDES), *(f"assets/{name}" for name in LEGACY_ASSETS)}
    files.update("motion/" + name for name in ("motion-demo-gallery.html", "motion-demo-detail.html"))
    reports = json.loads((bench / "data/narrative.json").read_text())["entries"]
    files.update({"bench/index.html", *(f"bench/{slug}/index.html" for slug in reports)})
    files.update(f"bench/assets/img/{path.name}" for path in (bench/"img").glob("*.jpg"))
    files.update(f"bench/{path.relative_to(bench)}" for path in (bench/"demos").rglob("*.html"))
    files.update(REDESIGN.generated_files(entries))
    return files


def asset_version(name: str) -> str:
    return hashlib.sha256((SITE_SOURCE / name).read_bytes()).hexdigest()[:8]

PAGES = (
    ("ui", ROOT / "网页UI元素速查.html", "UI 元素", "70 个可交互网页 UI 元素示例。看形态与状态，复制清楚的组件实现需求。", 'class="cmp"', 70),
    ("motion", ROOT / "动效速查.html", "动效", "79 种可交互动效，附实现规范分区。看触发和变化，复制清楚的动效实现需求。", 'class="effect-card"', 79),
)


def site_navigation(section: str) -> str:
    links = (("首页", "../", "home"), ("UI 元素", "../ui/", "ui"), ("动效", "../motion/", "motion")) + tuple(
        (guide["name"], f"../{slug}/", slug) for slug, guide in GUIDES.items()
    ) + (("Skills", "../skills/", "skills"), ("测评结果", "../bench/", "bench"))
    parts = []
    for label, href, key in links:
        current = ' aria-current="page"' if key == section else ""
        parts.append(f'<a href="{href}"{current}>{label}</a>')
    items = "".join(parts)
    more = f'<details class="site-more"><summary>分类目录</summary><div class="site-more-menu">{items}</div></details>'
    skip_target = "skills-main" if section == "skills" else "guide-main" if section in GUIDES else "site-content"
    return (
        f'<a class="site-skip" href="#{skip_target}">跳到主要内容</a>'
        '<nav class="site-nav" aria-label="网站导航"><div class="site-nav-inner">'
        '<a class="site-brand" href="../" aria-label="vibocoding助手首页">'
        '<span class="site-brand-icon" aria-hidden="true"><i></i><i></i><i></i></span>'
        '<span>vibocoding助手<small>INTERFACE FIELD GUIDE</small></span></a>'
        f'<div class="site-nav-links"><span class="site-nav-section">浏览目录</span>{items}{more}</div></div></nav>'
    )


def wrap_reference(source: str, section: str, description: str, card_class: str, expected_cards: int) -> str:
    if source.count(card_class) != expected_cards:
        raise ValueError(f"{section}: expected {expected_cards} cards, found {source.count(card_class)}")
    if source.count("<body>") != 1 or source.count('<main class="wrap">') != 1:
        raise ValueError(f"{section}: source page structure changed")

    head = (
        f'<meta name="description" content="{description}">\n'
        '<meta name="theme-color" content="#f7f7fd">\n'
        '<link rel="icon" href="../assets/favicon.svg" type="image/svg+xml">\n'
        f'<link rel="stylesheet" href="../assets/site.css?v={asset_version("site.css")}">\n'
        f'<link rel="stylesheet" href="../assets/theme.css?v={asset_version("theme.css")}">\n'
    )
    page = source.replace("</head>", head + "</head>", 1)
    page_title = "UI 元素速查" if section == "ui" else "动效速查"
    page, title_count = re.subn(r"<title>[^<]*</title>", f"<title>{page_title} · vibocoding助手</title>", page, count=1)
    if title_count != 1:
        raise ValueError(f"{section}: expected one page title")
    page = page.replace("<body>", f'<body class="site-reference" data-section="{section}">' + site_navigation(section) + '<div class="site-reference-workspace">', 1)
    page = page.replace('<main class="wrap">', '<main class="wrap" id="site-content">', 1)
    page = page.replace("</body>", f'</div>\n<script defer src="../assets/site.js?v={asset_version("site.js")}"></script>\n</body>', 1)
    return page


def prepare_output() -> None:
    if OUTPUT.exists():
        if not (OUTPUT / MARKER).is_file():
            raise RuntimeError(f"Refusing to replace non-generated directory: {OUTPUT}")
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir()
    (OUTPUT / MARKER).write_text("Generated by scripts/build_site.py\n", encoding="utf-8")


def build() -> None:
    subprocess.run([sys.executable, str(ROOT / "动效速查-src" / "build_motion_glossary.py")], check=True, cwd=ROOT)
    entries = ENTRY_ADAPTER.write_entries()
    prepare_output()
    assets = OUTPUT / "assets"
    assets.mkdir()
    for name in LEGACY_ASSETS:
        shutil.copy2(SITE_SOURCE / name, assets / name)
    for old in redirects.DEFAULTS:
        (OUTPUT / old).mkdir()
    redirects.build(OUTPUT, entries, ENTRY_ADAPTER.taxonomy(), ENTRY_ADAPTER)
    for name in ("motion-demo-gallery.html", "motion-demo-detail.html"):
        shutil.copy2(ROOT / name, OUTPUT / "motion" / name)
    BENCH_MODULE.build(OUTPUT, SITE_SOURCE / "bench", entries, ENTRY_ADAPTER.taxonomy(), REDESIGN)
    REDESIGN.build(OUTPUT, entries, ENTRY_ADAPTER.taxonomy())
    files = {str(path.relative_to(OUTPUT)) for path in OUTPUT.rglob("*") if path.is_file()}
    expected = expected_build_files(entries)
    if files != expected:
        raise RuntimeError(f"Unexpected build files: missing={expected-files}, extra={files-expected}")
    page_count = sum(name.endswith(".html") and "/demos/" not in name for name in files)
    print(f"Built site: {page_count} pages, {len(entries)} unified entries; legacy addresses redirected")


if __name__ == "__main__":
    build()
