"""Build a site-wide search index from the same sources as the detail pages."""

from html import unescape
from html.parser import HTMLParser
import re


class ReferenceCardParser(HTMLParser):
    def __init__(self, card_class):
        super().__init__()
        self.card_class = card_class
        self.cards = []
        self.current = None
        self.article_depth = 0
        self.capture = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = attrs.get("class", "").split()
        if tag == "article":
            if self.current is not None:
                self.article_depth += 1
            elif self.card_class in classes:
                self.current = {"id": attrs.get("id", ""), "terms": unescape(attrs.get("data-name", "")),
                                "title": "", "description": ""}
                self.article_depth = 1
        if self.current is None:
            return
        if tag in ("h2", "h3") and not self.current["title"]:
            self.capture = "title"
        elif "where" in classes or "card-note" in classes:
            self.capture = "description"

    def handle_data(self, data):
        if self.current is not None and self.capture:
            self.current[self.capture] += data

    def handle_endtag(self, tag):
        if self.current is None:
            return
        if tag in ("h2", "h3") and self.capture == "title":
            self.capture = None
        elif tag in ("p", "div") and self.capture == "description":
            self.capture = None
        if tag == "article":
            self.article_depth -= 1
            if self.article_depth == 0:
                for field in ("title", "description"):
                    self.current[field] = re.sub(r"\s+", " ", self.current[field]).strip()
                self.cards.append(self.current)
                self.current = None
                self.capture = None


def reference_entries(source, section, category, card_class):
    parser = ReferenceCardParser(card_class)
    parser.feed(source)
    entries = []
    for card in parser.cards:
        if not card["id"] or not card["title"]:
            raise ValueError(f"Incomplete search card in {section}: {card}")
        entries.append({"title": card["title"], "category": category,
                        "description": card["description"], "href": f"./{section}/#{card['id']}",
                        "terms": card["terms"]})
    return entries


def build_search_index(ui_html, motion_html, guides, guide_module, skills):
    entries = reference_entries(ui_html, "ui", "UI 元素", "cmp")
    entries += reference_entries(motion_html, "motion", "动效", "effect-card")
    for slug, guide in guides.items():
        for item in guide_module.all_items(guide):
            entries.append({"title": item["title"], "category": guide["name"],
                            "description": item["description"], "href": f"./{slug}/#g-{slug}-{item['demo']}",
                            "terms": " ".join((item["english"], item["fit"], item["avoid"]))})
    for skill in skills:
        entries.append({"title": skill["title"], "category": "UI 与交互 Skills",
                        "description": skill["summary"], "href": f"./skills/#skill-{skill['slug']}",
                        "terms": " ".join((skill["slug"], skill["repo"], skill["use"], *skill["tags"]))})
    if len(entries) != 189 or len({entry["href"] for entry in entries}) != 189:
        raise ValueError("Search index must contain 189 unique destination entries")
    return entries
