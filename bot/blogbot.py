import os, re, sys, json, time, yaml, requests, frontmatter, markdownify
from datetime import datetime
from urllib.parse import urlparse
from slugify import slugify
from bs4 import BeautifulSoup
import trafilatura

CFG = yaml.safe_load(open(sys.argv[1], "r", encoding="utf-8"))

LLM_HOST = CFG["llm"]["host"].rstrip("/")
LLM_MODEL= CFG["llm"]["model"]
TEMP     = CFG["llm"].get("temperature", 0.7)

OUT_DIR  = CFG["site"]["out_dir"]
BASE_URL = CFG["site"]["base_url"].rstrip("/")
AUTHOR   = CFG["site"]["author"]
MINW     = CFG["site"]["min_words"]
TEMPLATE = open(os.path.join(os.path.dirname(sys.argv[1]), "template.html"), "r", encoding="utf-8").read()

def main():
    sources = CFG["curation"]["sources"]
    links = find_new_links(sources, limit=CFG["curation"].get("max_new_links",3))
    if not links:
        print("No new links found; exiting.")
        return

    offers_html = build_offers_html(CFG["offers"])

    for url in links:
        base_text = fetch_clean(url)
        if not base_text or len(base_text.split()) < 200:
            continue

        # Summarize → outline → article
        summary = ollama(f"Summarize the key takeaways in 6 bullets from this text for a general audience:\n\n{base_text[:8000]}")
        outline = ollama(f"Create an outline for a high-quality health blog post from these takeaways. Include H2/H3 sections, FAQs, and a CTA section that can host affiliate recommendations.\n\nTakeaways:\n{summary}")
        article = ollama(f"""Write a {MINW}-{MINW+400} word, evidence-aware blog post based on this outline. 
Use friendly, credible tone, short paragraphs, subheads, and a brief intro & conclusion. 
Avoid medical advice; encourage consulting professionals. 
Do not invent studies; if uncertain say so.

Outline:
{outline}
""")

        # SEO bits
        title = ollama(f"Write an SEO title (max 62 chars) for this article:\n\n{article}").strip().strip('"')
        desc  = ollama(f"Write a compelling meta description (max 155 chars) for this article:\n\n{article}").strip().strip('"')

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
    funnels_dir = os.path.join(OUT_DIR, "funnels"); os.makedirs(funnels_dir, exist_ok=True)
    fhtml = "<h1>Recommended</h1>\n" + offers_html
    with open(os.path.join(funnels_dir, "index.html"), "w", encoding="utf-8") as f: f.write(fhtml)

    update_sitemap()
    print("Sitemap updated.")

# ---- helpers (auto-injected) ----
import json
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import trafilatura
import requests
import re
import os

def ollama(prompt, sysmsg=None, max_tokens=800, timeout=300, stream_mode=True):
    import time, json, requests
    msg = (f"<<SYS>>{sysmsg}<<SYS>>\\n" if sysmsg else "") + prompt
    payload = {
        "model": LLM_MODEL,
        "prompt": msg,
        "options": {"temperature": TEMP, "num_predict": max_tokens},
        "stream": stream_mode
    }
    # Try streaming first (handles NDJSON properly) with a watchdog
    if stream_mode:
        try:
            with requests.post(f"{LLM_HOST}/api/generate", json=payload, timeout=(20, timeout), stream=True) as r:
                r.raise_for_status()
                parts, start = [], time.time()
                for line in r.iter_lines(decode_unicode=True):
                    if not line:
                        continue
                    if time.time() - start > timeout:
                        break  # safety: don't hang forever
                    try:
                        obj = json.loads(line)
                    except Exception:
                        continue
                    if "response" in obj:
                        parts.append(obj["response"])
                    if obj.get("done"):
                        break
                text = "".join(parts).strip()
                if text:
                    return text
        except Exception:
            pass  # fall back below
    # Fallback: non-streaming single JSON (or NDJSON-in-text)
    payload["stream"] = False
    r = requests.post(f"{LLM_HOST}/api/generate", json=payload, timeout=(20, timeout), stream=False)
    r.raise_for_status()
    try:
        data = r.json()
        if isinstance(data, dict) and "response" in data:
            return data["response"].strip()
    except Exception:
        # Some servers still send NDJSON; parse lines
        lines = r.text.splitlines()
        out = []
        for ln in lines:
            try:
                obj = json.loads(ln)
                out.append(obj.get("response",""))
            except Exception:
                continue
        if out:
            return "".join(out).strip()
    return ""






