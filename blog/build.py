#!/usr/bin/env python3
"""
Juraj Orwell — Blog Build Script
Generates HTML post pages, category pages, and updates the posts index.

Usage:
    python build.py                    # Build all posts from drafts/
    python build.py --post draft.json  # Build a single post from a draft JSON file

Post JSON format:
{
    "title": "Názov článku",
    "slug": "nazov-clanku",
    "date": "2026-03-18",
    "tags": ["politika", "európa"],
    "excerpt": "Krátky popis článku...",
    "content": "<p>HTML obsah článku...</p>",
    "source_url": "https://youtube.com/watch?v=..."
}
"""

import json
import os
import argparse
from datetime import datetime
from collections import defaultdict


BLOG_DIR = os.path.dirname(os.path.abspath(__file__))
POSTS_DIR = os.path.join(BLOG_DIR, "posts")
DRAFTS_DIR = os.path.join(BLOG_DIR, "drafts")
CATEGORY_DIR = os.path.join(BLOG_DIR, "kategoria")
TEMPLATE_PATH = os.path.join(BLOG_DIR, "post-template.html")
CATEGORY_TEMPLATE_PATH = os.path.join(BLOG_DIR, "category-template.html")
CSS_PATH = os.path.join(BLOG_DIR, "css", "style.css")
POSTS_JSON_PATH = os.path.join(BLOG_DIR, "posts.json")

MONTHS_SK = [
    "januára", "februára", "marca", "apríla", "mája", "júna",
    "júla", "augusta", "septembra", "októbra", "novembra", "decembra"
]


def format_date_sk(date_str):
    d = datetime.strptime(date_str, "%Y-%m-%d")
    return f"{d.day}. {MONTHS_SK[d.month - 1]} {d.year}"


def load_css():
    if os.path.exists(CSS_PATH):
        with open(CSS_PATH, "r", encoding="utf-8") as f:
            return f.read()
    return ""


def load_template(path):
    """Load an HTML template and inline the CSS."""
    with open(path, "r", encoding="utf-8") as f:
        template = f.read()
    css = load_css()
    if css:
        template = template.replace(
            '<link rel="stylesheet" href="../css/style.css">',
            f'<style>\n{css}\n</style>'
        )
    return template


def load_posts_index():
    if os.path.exists(POSTS_JSON_PATH):
        with open(POSTS_JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_posts_index(posts):
    posts.sort(key=lambda p: p["date"], reverse=True)
    with open(POSTS_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)
    print(f"  ✓ Aktualizovaný posts.json ({len(posts)} článkov)")


# ── Post card HTML (shared by index and category pages) ──────────────────────
def render_post_card(post, path_prefix="../"):
    """Render a post card HTML snippet. path_prefix adjusts relative links."""
    tags_html = " ".join(
        f'<span class="tag">{tag}</span>' for tag in post.get("tags", [])
    )
    return f"""
        <div class="post-card">
            <div class="post-card-meta">{format_date_sk(post['date'])}</div>
            <h2><a href="{path_prefix}posts/{post['slug']}.html">{post['title']}</a></h2>
            <p class="post-card-excerpt">{post.get('excerpt', '')}</p>
            <div class="post-card-tags">{tags_html}</div>
        </div>"""


# ── Build a single post HTML page ─────────────────────────────────────────────
def build_post_html(template, post):
    tags_html = " ".join(
        f'<span class="tag">{tag}</span>' for tag in post.get("tags", [])
    )
    html = template
    html = html.replace("{{TITLE}}", post["title"])
    html = html.replace("{{DATE}}", format_date_sk(post["date"]))
    html = html.replace("{{EXCERPT}}", post.get("excerpt", ""))
    html = html.replace("{{TAGS}}", ", ".join(post.get("tags", [])))
    html = html.replace("{{TAGS_HTML}}", tags_html)
    html = html.replace("{{CONTENT}}", post.get("content", ""))
    html = html.replace("{{SOURCE_URL}}", post.get("source_url", "#"))

    output_path = os.path.join(POSTS_DIR, f"{post['slug']}.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  ✓ Post: posts/{post['slug']}.html")


# ── Build all category pages ──────────────────────────────────────────────────
def build_category_pages(all_posts):
    """Generate one HTML page per tag from the full posts index."""
    os.makedirs(CATEGORY_DIR, exist_ok=True)

    cat_template = load_template(CATEGORY_TEMPLATE_PATH)

    # Group posts by tag
    by_tag = defaultdict(list)
    for post in all_posts:
        for tag in post.get("tags", []):
            by_tag[tag].append(post)

    for tag, posts in by_tag.items():
        # Sort posts newest first
        posts_sorted = sorted(posts, key=lambda p: p["date"], reverse=True)

        # Capitalize label nicely
        label = tag.capitalize()
        count = len(posts_sorted)

        posts_html = "".join(render_post_card(p, path_prefix="../") for p in posts_sorted)

        html = cat_template
        html = html.replace("{{CATEGORY_SLUG}}", tag)
        html = html.replace("{{CATEGORY_LABEL}}", label)
        html = html.replace("{{POST_COUNT}}", str(count))
        html = html.replace("{{POSTS_HTML}}", posts_html)

        # Slugify the tag for the filename (replace spaces/special chars)
        slug = tag.lower().replace(" ", "-")
        output_path = os.path.join(CATEGORY_DIR, f"{slug}.html")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"  ✓ Kategória: kategoria/{slug}.html ({count} článkov)")


# ── Publish a draft ───────────────────────────────────────────────────────────
def publish_draft(draft_path):
    with open(draft_path, "r", encoding="utf-8") as f:
        post = json.load(f)

    post_template = load_template(TEMPLATE_PATH)
    posts = load_posts_index()

    # Remove existing entry with same slug (allows rebuilding)
    posts = [p for p in posts if p["slug"] != post["slug"]]

    # Build the post HTML
    build_post_html(post_template, post)

    # Add to index (metadata only, no full content)
    index_entry = {
        "title": post["title"],
        "slug": post["slug"],
        "date": post["date"],
        "tags": post.get("tags", []),
        "excerpt": post.get("excerpt", ""),
        "source_url": post.get("source_url", "")
    }
    posts.append(index_entry)
    save_posts_index(posts)

    # Rebuild all category pages with updated index
    build_category_pages(posts)

    return True


# ── Build all drafts ──────────────────────────────────────────────────────────
def build_all():
    if not os.path.exists(DRAFTS_DIR):
        print("Priečinok drafts/ neexistuje.")
        return

    draft_files = [f for f in os.listdir(DRAFTS_DIR) if f.endswith(".json")]
    if not draft_files:
        print("Žiadne návrhy na publikovanie.")
        return

    print(f"Nájdených {len(draft_files)} návrhov...\n")
    post_template = load_template(TEMPLATE_PATH)
    posts = load_posts_index()

    for filename in sorted(draft_files):
        path = os.path.join(DRAFTS_DIR, filename)
        print(f"Publikujem: {filename}")
        with open(path, "r", encoding="utf-8") as f:
            post = json.load(f)

        posts = [p for p in posts if p["slug"] != post["slug"]]
        build_post_html(post_template, post)

        posts.append({
            "title": post["title"],
            "slug": post["slug"],
            "date": post["date"],
            "tags": post.get("tags", []),
            "excerpt": post.get("excerpt", ""),
            "source_url": post.get("source_url", "")
        })

        published_dir = os.path.join(DRAFTS_DIR, "published")
        os.makedirs(published_dir, exist_ok=True)
        os.rename(path, os.path.join(published_dir, filename))
        print(f"  ✓ Presunutý do drafts/published/\n")

    save_posts_index(posts)

    print("Generujem stránky kategórií...")
    build_category_pages(posts)


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Juraj Orwell — Build script")
    parser.add_argument("--post", help="Cesta k JSON súboru s článkom")
    parser.add_argument("--categories", action="store_true",
                        help="Rebuild category pages only (no new posts)")
    args = parser.parse_args()

    os.makedirs(POSTS_DIR, exist_ok=True)
    os.makedirs(CATEGORY_DIR, exist_ok=True)

    if args.categories:
        print("Prebudovávam stránky kategórií...")
        build_category_pages(load_posts_index())
    elif args.post:
        print(f"Publikujem článok: {args.post}")
        publish_draft(args.post)
    else:
        build_all()

    print("\nHotovo!")
