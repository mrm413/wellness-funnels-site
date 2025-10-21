import os, re, sys, time, yaml, requests, datetime, xml.etree.ElementTree as ET
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

# Usage: python expand_sources.py F:\BlogGuru\config.yml
CFG_PATH = sys.argv[1]

with open(CFG_PATH, "r", encoding="utf-8") as f:
    CFG = yaml.safe_load(f)

OUT_CFG_MAX = int(CFG.get("curation",{}).get("max_pool", 300))  # cap the pool in config (optional)
CURATION = CFG.setdefault("curation", {})
SEEDS    = set(CURATION.get("sources", []) or [])

# Built-in trusted seeds (gov/org/hospitals) – added once, de-duplicated automatically
TRUSTED = [
  # Gov / Agencies
  "https://www.cdc.gov/", "https://www.nih.gov/news-events/nih-research-matters",
  "https://www.fda.gov/news-events/press-announcements",
  "https://www.epa.gov/environmental-topics/health-and-environmental-effects",
  "https://www.who.int/news-room/releases",

  # Hospitals / Academic
  "https://www.mayoclinic.org/", "https://health.clevelandclinic.org/",
  "https://www.hopkinsmedicine.org/news/", "https://www.stanfordmedicine.org/news/",
  "https://www.harvardhealth.harvard.edu/blog",

  # Wellness publishers (non-spammy)
  "https://www.health.harvard.edu/", "https://www.medicalnewstoday.com/",
]

for u in TRUSTED:
    SEEDS.add(u)

HEADERS = {"User-Agent":"Mozilla/5.0 (compatible; BlogGuru/1.0)"}

def get(url, timeout=15):
    try:
        return requests.get(url, headers=HEADERS, timeout=timeout)
    except Exception:
        return None

def discover_feeds(html, base):
    feeds = set()
    if not html: return feeds
    soup = BeautifulSoup(html, "html.parser")
    for link in soup.find_all("link", attrs={"rel": lambda x: x and "alternate" in x}):
        t = (link.get("type") or "").lower()
        if "rss" in t or "atom" in t or "xml" in t:
            href = link.get("href")
            if href:
                feeds.add(urljoin(base, href))
    # common feed paths
    for path in ["/feed", "/rss", "/rss.xml", "/atom.xml", "/feeds", "/news/rss.xml", "/feed.xml"]:
        feeds.add(urljoin(base, path))
    return feeds

def recent_from_feed(url, days=14, limit=15):
    items = []
    try:
        import feedparser
    except Exception:
        return items
    d = feedparser.parse(url)
    cutoff = time.time() - days*86400
    for e in d.entries[:limit]:
        link = e.get("link")
        if not link: continue
        # recency best-effort
        ts = None
        for k in ("published_parsed", "updated_parsed"):
            if getattr(e, k, None):
                ts = time.mktime(getattr(e, k))
                break
        if ts and ts < cutoff: continue
        items.append(link)
    return items

def recent_from_sitemap(root_url, days=14, limit=30):
    urls = set()
    # try /sitemap.xml
    site = urljoin(root_url, "/sitemap.xml")
    r = get(site, 15)
    if not r or r.status_code >= 400: return []
    try:
        tree = ET.fromstring(r.content)
    except Exception:
        return []
    ns = {"sm":"http://www.sitemaps.org/schemas/sitemap/0.9"}
    cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=days)
    # sitemapindex or urlset
    if tree.tag.endswith("sitemapindex"):
        for sm in tree.findall(".//sm:sitemap", ns):
            loc = sm.findtext("sm:loc", default="", namespaces=ns).strip()
            if not loc: continue
            rr = get(loc, 15)
            if not rr or rr.status_code >= 400: continue
            try:
                t2 = ET.fromstring(rr.content)
            except Exception:
                continue
            for u in t2.findall(".//sm:url", ns):
                loc2 = u.findtext("sm:loc", default="", namespaces=ns).strip()
                if not loc2: continue
                lastmod = u.findtext("sm:lastmod", default="", namespaces=ns)
                if lastmod:
                    try:
                        dt = datetime.datetime.fromisoformat(lastmod.replace("Z","+00:00")).replace(tzinfo=None)
                        if dt < cutoff: continue
                    except Exception:
                        pass
                urls.add(loc2)
                if len(urls) >= limit: break
    else:
        for u in tree.findall(".//sm:url", ns):
            loc = u.findtext("sm:loc", default="", namespaces=ns).strip()
            if not loc: continue
            lastmod = u.findtext("sm:lastmod", default="", namespaces=ns)
            if lastmod:
                try:
                    dt = datetime.datetime.fromisoformat(lastmod.replace("Z","+00:00")).replace(tzinfo=None)
                    if dt < cutoff: continue
                except Exception:
                    pass
            urls.add(loc)
            if len(urls) >= limit: break

    # topical filter
    KEEP = re.compile(r"(health|wellness|nutrition|fitness|sleep|mental|obesity|diabetes|heart|cardio|immune|environment|air|water|toxins|food|diet)", re.I)
    return [u for u in urls if KEEP.search(urlparse(u).path or "")]

def normalize(u):
    u = u.strip()
    if u.endswith("/"): u = u[:-1]
    return u

def root_of(u):
    p = urlparse(u)
    return f"{p.scheme}://{p.netloc}"

def auto_discover(seeds):
    discovered = set()
    for s in list(seeds):
        base = root_of(s)
        # 1) page feeds
        r = get(s, 12)
        if r and r.ok:
            feeds = discover_feeds(r.text, base)
            for f in feeds:
                for item in recent_from_feed(f):
                    discovered.add(normalize(item))
        # 2) site sitemap
        for item in recent_from_sitemap(base):
            discovered.add(normalize(item))
    return discovered

# Run discovery
found = auto_discover(SEEDS)

# Merge into config curation.sources
existing = [normalize(u) for u in (CURATION.get("sources") or [])]
pool = []
seen = set()
# keep existing first (stable order)
for u in existing:
    if u not in seen:
        pool.append(u); seen.add(u)
# then new ones
for u in sorted(found):
    if u not in seen:
        pool.append(u); seen.add(u)

# keep cap
if OUT_CFG_MAX and len(pool) > OUT_CFG_MAX:
    pool = pool[-OUT_CFG_MAX:]  # keep newest chunk

CURATION["sources"] = pool

with open(CFG_PATH, "w", encoding="utf-8") as f:
    yaml.safe_dump(CFG, f, sort_keys=False, allow_unicode=True)

print(f"Discovered {len(found)} new URLs. Now tracking {len(pool)} total sources.")
