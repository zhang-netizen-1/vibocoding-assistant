"""Render the four benchmark pages from the supplied results and narrative."""

from html import escape
import json
from pathlib import Path
import shutil


ENTRIES = ("button", "crossfade", "grid")
AGENTS = {"codex": "Codex", "hermes": "Hermes"}
RELATED_TERMS = {
    "button": ("对比度", "焦点环", "设计令牌（CSS 变量）", "按下态"),
    "crossfade": ("缓动", "时长", "减弱动态"),
    "grid": ("设计令牌（CSS 变量）", "横向溢出", "断点 / 列数"),
}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_round(path):
    data = read_json(path)
    # Explicitly select the two published agents; never render run metadata.
    return {
        "scores": {slug: {agent: data["scores"][slug][agent] for agent in AGENTS} for slug in ENTRIES},
        "times": {slug: {agent: data["agents_runs"][f"{slug}/{agent}"]["wall_s"] for agent in AGENTS} for slug in ENTRIES},
    }


def paragraphs(lines):
    return "".join(f"<p>{escape(line)}</p>" for line in lines)


def bullet_list(lines):
    return "<ul>" + "".join(f"<li>{escape(line)}</li>" for line in lines) + "</ul>"


def section(title, body):
    return f'<section class="bench-section"><h2>{escape(title)}</h2>{body}</section>'


def table(caption, headings, rows, footer=""):
    head = "".join(f'<th scope="col">{escape(heading)}</th>' for heading in headings)
    return (
        f'<div class="bench-table-scroll" role="region" aria-label="{escape(caption)}，可横向滚动" tabindex="0">'
        f'<table><caption>{escape(caption)}</caption><thead><tr>{head}</tr></thead>'
        f'<tbody>{"".join(rows)}</tbody>{footer}</table></div>'
    )


def glossary(narrative, slug=None):
    terms = narrative["glossary"]
    if slug:
        terms = [item for item in terms if item["term"] in RELATED_TERMS[slug]]
    body = "".join(f'<div><dt>{escape(item["term"])}</dt><dd>{escape(item["text"])}</dd></div>' for item in terms)
    return section("名词小抄", f'<dl class="bench-glossary">{body}</dl>')


def format_time(seconds):
    minutes, seconds = divmod(int(seconds + 0.5), 60)
    return f"{minutes} 分 {seconds} 秒"


def overview(narrative, rounds):
    hero = (
        '<header class="bench-hero">'
        f'<h1>{escape(narrative["title"])}</h1><p class="bench-lead">{escape(narrative["lead"])}</p></header>'
    )
    lesson = section("主结论", f'<p class="bench-lesson">{escape(narrative["main_lesson"])}</p>' + bullet_list(narrative["lesson_points"]))
    rows = []
    for slug in ENTRIES:
        entry = narrative["entries"][slug]
        note = '<small>同一提示词重跑</small>' if slug == "crossfade" else ""
        cells = "".join(f'<td>{rounds[0]["scores"][slug][agent]["total"]} → {rounds[1]["scores"][slug][agent]["total"]} /16</td>' for agent in AGENTS)
        rows.append(f'<tr><th scope="row"><a href="./{slug}/">{escape(entry["name"])}</a>{note}</th>{cells}</tr>')
    totals = section("总分对比", table("第 1 轮 → 第 2 轮，满分 16", ("条目", *AGENTS.values()), rows))
    time_rows = []
    for slug in ENTRIES:
        for agent, label in AGENTS.items():
            times = "".join(f'<td>{format_time(data["times"][slug][agent])}</td>' for data in rounds)
            time_rows.append(f'<tr><th scope="row">{escape(narrative["entries"][slug]["name"])} · {label}</th>{times}</tr>')
    times = section("运行用时", table("实际墙钟时间（wall_s，四舍五入到秒）", ("条目 / AI", "第 1 轮", "第 2 轮"), time_rows) + paragraphs([narrative["time_note"]]))
    cards = "".join(
        f'<a class="bench-entry-card" href="./{slug}/"><h3>{escape(narrative["entries"][slug]["name"])}</h3>'
        f'<p>{escape(narrative["entries"][slug]["rounds_note"])}</p><span>查看测评详情 →</span></a>' for slug in ENTRIES
    )
    return (
        hero + lesson + totals + section("三个试点条目", f'<div class="bench-entry-grid">{cards}</div>') + times
        + section("评分规则", paragraphs([narrative["scale"], narrative["eye_note"]]))
        + section("方法", bullet_list(narrative["method"]))
        + section("测量局限", bullet_list(narrative["limits"])) + glossary(narrative)
    )


def score_details(slug, narrative, rounds):
    scores = [data["scores"][slug] for data in rounds]
    columns = [(agent, rnd) for agent in AGENTS for rnd in (0, 1)]
    indexed = [{agent: {item["item"]: item for item in data[agent]["items"]} for agent in AGENTS} for data in scores]
    rows, evidence = [], []
    for item in scores[1]["codex"]["items"]:
        number = item["item"]
        eye = any("目测" in indexed[rnd][agent][number]["check"] for agent, rnd in columns)
        label = "助手目测判定" if eye else "工具"
        title = escape(item["name"])
        cells = "".join(f'<td>{indexed[rnd][agent][number]["score"]}</td>' for agent, rnd in columns)
        rows.append(f'<tr><th scope="row">{number}. {title}<small>{label}</small></th>{cells}</tr>')
        current = "".join(f'<p><strong>{name}</strong>：{escape(indexed[1][agent][number]["evidence"])}</p>' for agent, name in AGENTS.items())
        previous = "".join(f'<p><strong>{name}</strong>：{escape(indexed[0][agent][number]["evidence"])}</p>' for agent, name in AGENTS.items())
        evidence.append(
            f'<article class="bench-evidence"><h3>{number}. {title} <span class="bench-label">{label}</span></h3>'
            f'<div aria-label="第 2 轮证据">{current}</div><details><summary>第 1 轮证据</summary>{previous}</details></article>'
        )
    total_cells = "".join(f'<td>{scores[rnd][agent]["total"]} /16</td>' for agent, rnd in columns)
    footer = f'<tfoot><tr><th scope="row">总分</th>{total_cells}</tr></tfoot>'
    return (
        section("逐项分数", paragraphs([narrative["scale"], narrative["eye_note"]]) + table("8 项检查 · 每项满分 2", ("检查项 / 方式", "Codex 第 1 轮", "Codex 第 2 轮", "Hermes 第 1 轮", "Hermes 第 2 轮"), rows, footer))
        + section("逐项证据 · 第 2 轮", "".join(evidence))
    )


def prompt_html(text, highlight=False):
    if highlight and "补充验收要求：" in text:
        start = text.index("补充验收要求：")
        end = text.index("\n\n", start)
        return escape(text[:start]) + "<mark>" + escape(text[start:end]) + "</mark>" + escape(text[end:])
    return escape(text)


def detail(slug, narrative, rounds, data_dir, return_href):
    entry = narrative["entries"][slug]
    conclusion = entry["stability"]["heading"] if "stability" in entry else entry["fixes"][0]["fixed"]
    hero = (
        '<header class="bench-hero"><div class="bench-page-links"><a href="../">← 返回测评总览</a>'
        f'<a class="btn-primary" href="{escape(return_href)}">回到条目复制提示词 →</a></div>'
        f'<h1>{escape(entry["name"])}</h1>'
        f'<p class="bench-conclusion">{escape(conclusion)}</p><p class="bench-lead">{escape(entry["rounds_note"])}</p></header>'
    )
    prompts = "".join(
        f'<h3>第 {rnd} 轮提示词</h3><pre>{prompt_html((data_dir / f"round{rnd}-{slug}-prompt.txt").read_text(encoding="utf-8"), rnd == 2)}</pre>' for rnd in (1, 2)
    )
    fixes = ""
    if entry["fixes"]:
        items = "".join(f'<li><strong>{escape(fix["sentence"])}</strong><p>{escape(fix["fixed"])}</p></li>' for fix in entry["fixes"])
        fixes = section("补充的每句话修好了什么", f'<ol class="bench-fixes">{items}</ol>')
    stability = ""
    if "stability" in entry:
        info = entry["stability"]
        stability = section(info["heading"], bullet_list(info["points"]) + paragraphs([info["note"]]))
    images = "".join(
        f'<figure><img src="../assets/img/{escape(img["file"])}" loading="lazy" alt="{escape(entry["name"] + "，第 1 轮与第 2 轮对比：" + img["caption"])}">'
        f'<figcaption>{escape(img["caption"])} · 第 1 轮 | 第 2 轮</figcaption></figure>' for img in entry["images"]
    )
    demos = "".join(
        f'<li><a href="../demos/round{rnd}/{slug}/{agent}.html" target="_blank" rel="noopener">第 {rnd} 轮 · {label} ↗</a></li>'
        for rnd in (1, 2) for agent, label in AGENTS.items()
    )
    return (
        hero + score_details(slug, narrative, rounds) + section("两轮提示词原文", prompts) + fixes + stability
        + section("两轮画面对比", images)
        + section("原始演示", '<p>在新标签打开 AI 生成的原始演示</p>' + f'<ul class="bench-demo-links">{demos}</ul>')
        + glossary(narrative, slug)
    )



def build(output, source, entries, taxonomy, templates):
    source = Path(source)
    data_dir = source / "data"
    narrative = read_json(data_dir / "narrative.json")
    rounds = [load_round(data_dir / f"round{rnd}-results.json") for rnd in (1, 2)]
    destination = Path(output) / "bench"
    destination.mkdir()
    def document(page, title, body):
        content = templates.shell(page, title, '<div class="bench-page">' + body + '</div>', entries, taxonomy)
        css = templates.relative(page, "assets/bench.css")
        return content.replace("</head>", f'<link rel="stylesheet" href="{css}"></head>')
    (destination / "index.html").write_text(document("bench/index.html", narrative["title"], overview(narrative, rounds)), encoding="utf-8")
    for slug in ENTRIES:
        folder = destination / slug
        folder.mkdir()
        entry = next(item for item in entries if item.get("bench", {}).get("slug") == slug)
        return_href = templates.relative(f"bench/{slug}/index.html", templates.entry_destination(entry))
        content = detail(slug, narrative, rounds, data_dir, return_href)
        (folder / "index.html").write_text(document(f"bench/{slug}/index.html", narrative["entries"][slug]["name"] + " · 测评结果", content), encoding="utf-8")
    images = destination / "assets" / "img"
    images.mkdir(parents=True)
    for path in (source / "img").glob("*.jpg"):
        shutil.copy2(path, images / path.name)
    for path in (source / "demos").rglob("*.html"):
        target = destination / path.relative_to(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
