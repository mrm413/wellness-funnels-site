import os, re, sys, json, time, yaml, requests, frontmatter, markdownify
from datetime import datetime
from urllib.parse import urlparse
from slugify import slugify
from bs4 import BeautifulSoup
import trafilatura

CFG = yaml.safe_load(open(sys.argv[1], "r", encoding="utf-8"))

# OpenAI Configuration
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable not set")

OPENAI_MODEL = CFG["llm"].get("model", "gpt-4o-mini")  # Default to gpt-4o-mini for cost efficiency
TEMP = CFG["llm"].get("temperature", 0.7)

OUT_DIR = CFG["site"]["out_dir"]
BASE_URL = CFG["site"]["base_url"].rstrip("/")
AUTHOR = CFG["site"]["author"]
MINW = CFG["site"]["min_words"]
TEMPLATE = open(os.path.join(os.path.dirname(sys.argv[1]), "template.html"), "r", encoding="utf-8").read()

def main():
    sources = CFG["curation"]["sources"]
    links = find_new_links(sources, limit=CFG["curation"].get("max_new_links", 3))
    if not links:
        print("No new links found; exiting.")
        return

    offers_html = build_offers_html(CFG["offers"])

    for url in links:
        base_text = fetch_clean(url)
        if not base_text or len(base_text.split()) < 200:
            continue

        # Summarize → outline → article
        summary = openai_chat(f"Summarize the key takeaways in 6 bullets from this text for a general audience:\n\n{base_text[:8000]}")
        outline = openai_chat(f"Create an outline for a high-quality health blog post from these takeaways. Include H2/H3 sections, FAQs, and a CTA section that can host affiliate recommendations.\n\nTakeaways:\n{summary}")
        article = openai_chat(f"""Write a {MINW}-{MINW+400} word, evidence-aware blog post based on this outline. 
Use friendly, credible tone, short paragraphs, subheads, and a brief intro & conclusion. 
Avoid medical advice; encourage consulting professionals. 
Do not invent studies; if uncertain say so.

Outline:
{outline}
""")

        # SEO bits
        title = openai_chat(f"Write an SEO title (max 62 chars) for this article:\n\n{article}").strip().strip('"')
        desc = openai_chat(f"Write a compelling meta description (max 155 chars) for this article:\n\n{article}").strip().strip('"')

        # Slug: safe chars, trimmed dashes, 70-char max, and prepend date
        slug = slugify(re.sub(r"[^a-zA-Z0-9 -]", "", title)).strip("-")[:70]
        if not slug:
            slug = (slugify(urlparse(url).path) or "post")
        date_prefix = datetime.utcnow().strftime("%Y-%m-%d")
        slug = f"{date_prefix}-{slug}"

        front = {
            "title": title,
            "description": desc,
            "date": datetime.utcnow().strftime("%Y-%m-%d"),
            "source": url,
            "author": AUTHOR,
            "category": CFG["site"]["category"]
        }

        write_html(front, article, offers_html, slug)
        print(f"Wrote /blog/{slug}.html")
    
    # Drop a simple funnels index from offers
    funnels_dir = os.path.join(OUT_DIR, "funnels")
    os.makedirs(funnels_dir, exist_ok=True)
    fhtml = "<h1>Recommended</h1>\n" + offers_html
    with open(os.path.join(funnels_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(fhtml)

    update_sitemap()
    print("Sitemap updated.")

# ---- OpenAI helper ----
def openai_chat(prompt, max_tokens=1000, timeout=60):
    """Call OpenAI Chat API"""
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": OPENAI_MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": TEMP,
        "max_tokens": max_tokens
    }
    
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=timeout
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return ""

# ---- helpers (auto-injected) ----
import json
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import trafilatura
import requests
import re
import os

def fetch_clean(url):
    try:
        r = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        if not r.ok:
            return None
        text = trafilatura.extract(r.content, include_comments=False, include_tables=False)
        return text or ""
    except Exception:
        return None

def find_new_links(sources, limit=3):
    """Return up to 'limit' URLs from sources that haven't been used yet"""
    used_file = os.path.join(OUT_DIR, ".used_sources.txt")
    used = set()
    if os.path.exists(used_file):
        with open(used_file, "r", encoding="utf-8") as f:
            used = set(line.strip() for line in f if line.strip())
    
    available = [s for s in sources if s not in used]
    selected = available[:limit]
    
    # Mark as used
    with open(used_file, "a", encoding="utf-8") as f:
        for s in selected:
            f.write(s + "\n")
    
    return selected

def build_offers_html(offers_cfg):
    clickbank_id = offers_cfg.get("clickbank_id", "YOURNICKNAME")
    items = offers_cfg.get("items", [])
    html = ""
    for item in items:
        name = item.get("name", "Product")
        hoplink = item.get("hoplink", "").replace("{id}", clickbank_id)
        blurb = item.get("blurb", "")
        html += f'<div style="margin:20px 0;padding:15px;border:1px solid #ddd;border-radius:5px">\n'
        html += f'  <h3>{name}</h3>\n'
        html += f'  <p>{blurb}</p>\n'
        html += f'  <a href="{hoplink}" target="_blank" rel="nofollow sponsored" style="display:inline-block;padding:10px 20px;background:#007bff;color:#fff;text-decoration:none;border-radius:3px">Learn More</a>\n'
        html += f'</div>\n'
    return html

def write_html(front, article, offers_html, slug):
    blog_dir = os.path.join(OUT_DIR, "blog")
    os.makedirs(blog_dir, exist_ok=True)
    
    canonical = f"{BASE_URL}/blog/{slug}.html"
    year = datetime.utcnow().year
    
    html = TEMPLATE
    html = html.replace("{{TITLE}}", front["title"])
    html = html.replace("{{META}}", front["description"])
    html = html.replace("{{CANONICAL}}", canonical)
    html = html.replace("{{AUTHOR}}", front["author"])
    html = html.replace("{{CONTENT}}", article)
    html = html.replace("{{OFFERS}}", offers_html)
    html = html.replace("{{YEAR}}", str(year))
    html = html.replace("{{BASE}}", BASE_URL)
    
    filepath = os.path.join(blog_dir, f"{slug}.html")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)

def update_sitemap():
    """Update sitemap.xml with all blog posts"""
    blog_dir = os.path.join(OUT_DIR, "blog")
    if not os.path.exists(blog_dir):
        return
    
    posts = []
    for filename in os.listdir(blog_dir):
        if filename.endswith(".html"):
            filepath = os.path.join(blog_dir, filename)
            mtime = os.path.getmtime(filepath)
            lastmod = datetime.utcfromtimestamp(mtime).strftime("%Y-%m-%d")
            url = f"{BASE_URL}/blog/{filename}"
            posts.append((url, lastmod))
    
    # Build sitemap
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    # Add homepage
    sitemap += f'  <url>\n'
    sitemap += f'    <loc>{BASE_URL}/</loc>\n'
    sitemap += f'    <changefreq>daily</changefreq>\n'
    sitemap += f'    <priority>1.0</priority>\n'
    sitemap += f'  </url>\n'
    
    # Add blog posts
    for url, lastmod in sorted(posts, key=lambda x: x[1], reverse=True):
        sitemap += f'  <url>\n'
        sitemap += f'    <loc>{url}</loc>\n'
        sitemap += f'    <lastmod>{lastmod}</lastmod>\n'
        sitemap += f'    <changefreq>weekly</changefreq>\n'
        sitemap += f'    <priority>0.8</priority>\n'
        sitemap += f'  </url>\n'
    
    sitemap += '</urlset>\n'
    
    sitemap_path = os.path.join(OUT_DIR, "sitemap.xml")
    with open(sitemap_path, "w", encoding="utf-8") as f:
        f.write(sitemap)

if __name__ == "__main__":
    main()