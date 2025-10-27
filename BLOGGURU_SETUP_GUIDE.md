# BlogGuru Setup Guide for Digital Ocean

## What BlogGuru Does

BlogGuru is an **automated blog content generator** that:

1. **Discovers Content Sources** (`expand_sources.py`)
   - Crawls trusted health websites (CDC, NIH, Mayo Clinic, etc.)
   - Finds RSS feeds and sitemaps
   - Extracts recent articles (last 14 days)
   - Maintains a pool of up to 300 source URLs

2. **Generates Blog Posts** (`blogbot.py`)
   - Takes 3 new links from the source pool
   - Scrapes and cleans the article content
   - Uses Ollama AI to:
     - Summarize key takeaways
     - Create an outline
     - Write a 900-1300 word blog post
     - Generate SEO title and meta description
   - Injects affiliate offers (ClickBank links)
   - Creates HTML files in `/blog/` directory
   - Updates sitemap.xml

3. **Runs on Schedule**
   - 3 times per day (9 AM, 2 PM, 8 PM ET)
   - Automatically commits and pushes to GitHub
   - GitHub Pages publishes the updates

## Requirements for Digital Ocean Droplet

### System Requirements
- **OS**: Ubuntu 20.04+ or Debian 11+
- **RAM**: 4GB minimum (8GB recommended for llama3.2:3b)
- **Storage**: 10GB minimum
- **CPU**: 2+ cores

### Software Stack
```bash
# Python 3.8+
sudo apt update
sudo apt install python3 python3-pip git -y

# Python dependencies
pip3 install trafilatura readability-lxml beautifulsoup4 requests pyyaml python-slugify python-frontmatter markdownify feedparser

# Ollama (AI model server)
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.2:3b
```

### GitHub Setup
```bash
# Install GitHub CLI
sudo apt install gh -y

# Authenticate
gh auth login

# Clone your repo
gh repo clone mrm413/wellness-funnels-site
cd wellness-funnels-site
```

## Running BlogGuru on Digital Ocean

### Option 1: Manual Execution
```bash
cd wellness-funnels-site

# Step 1: Discover new sources
python3 bot/expand_sources.py bot/config.yml

# Step 2: Generate blog posts
python3 bot/blogbot.py bot/config.yml

# Step 3: Push to GitHub
git add -A
git commit -m "Auto blog build: $(date -u +'%Y-%m-%dT%H:%M:%SZ')"
git push
```

### Option 2: Automated with Cron (Recommended)
Create a script `/home/yourusername/run-blogguru.sh`:

```bash
#!/bin/bash
cd /home/yourusername/wellness-funnels-site

# Ensure Ollama is running
if ! pgrep -x "ollama" > /dev/null; then
    ollama serve &amp;
    sleep 5
fi

# Pull latest changes
git pull

# Run BlogGuru
python3 bot/expand_sources.py bot/config.yml
python3 bot/blogbot.py bot/config.yml

# Push changes
git config user.name "BlogGuru Bot"
git config user.email "bot@yourdomain.com"
git add -A
if ! git diff --cached --quiet; then
    git commit -m "Auto blog build: $(date -u +'%Y-%m-%dT%H:%M:%SZ')"
    git push
fi
```

Make it executable:
```bash
chmod +x /home/yourusername/run-blogguru.sh
```

Add to crontab (`crontab -e`):
```cron
# Run BlogGuru 3 times per day (9 AM, 2 PM, 8 PM ET)
0 13 * * * /home/yourusername/run-blogguru.sh >> /home/yourusername/blogguru.log 2>&amp;1
0 18 * * * /home/yourusername/run-blogguru.sh >> /home/yourusername/blogguru.log 2>&amp;1
0 0 * * * /home/yourusername/run-blogguru.sh >> /home/yourusername/blogguru.log 2>&amp;1
```

### Option 3: Systemd Service (Most Reliable)
Create `/etc/systemd/system/blogguru.service`:

```ini
[Unit]
Description=BlogGuru Automated Blog Generator
After=network.target

[Service]
Type=oneshot
User=yourusername
WorkingDirectory=/home/yourusername/wellness-funnels-site
ExecStart=/home/yourusername/run-blogguru.sh
StandardOutput=append:/home/yourusername/blogguru.log
StandardError=append:/home/yourusername/blogguru.log

[Install]
WantedBy=multi-user.target
```

Create timer `/etc/systemd/system/blogguru.timer`:

```ini
[Unit]
Description=Run BlogGuru 3 times daily

[Timer]
OnCalendar=*-*-* 13:00:00
OnCalendar=*-*-* 18:00:00
OnCalendar=*-*-* 00:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable blogguru.timer
sudo systemctl start blogguru.timer
sudo systemctl status blogguru.timer
```

## Configuration

Edit `bot/config.yml`:

```yaml
site:
  base_url: "https://mrm413.github.io/wellness-funnels-site"
  out_dir: "./"
  author: "Wellness Funnels"
  category: "Wellness"
  min_words: 900

llm:
  host: "http://127.0.0.1:11434"  # Ollama default
  model: "llama3.2:3b"
  temperature: 0.6

curation:
  sources:
    - "https://www.cdc.gov/healthyweight/index.html"
    - "https://www.nih.gov/news-events/nih-research-matters"
    # More sources added automatically by expand_sources.py
  max_new_links: 3  # Blog posts per run
  max_pool: 300     # Total sources to track

offers:
  clickbank_id: "YOURNICKNAME"  # Update with your ClickBank ID
  items:
    - name: "Probiotic Health Booster"
      hoplink: "https://{id}.vendor.hop.clickbank.net/?tid=BLOG"
      blurb: "Clinically studied strains for gut balance."
```

## Monitoring

### Check logs:
```bash
tail -f /home/yourusername/blogguru.log
```

### Check Ollama:
```bash
curl http://127.0.0.1:11434/api/tags
```

### Check cron/timer:
```bash
# Cron
crontab -l

# Systemd
sudo systemctl status blogguru.timer
sudo journalctl -u blogguru.service -f
```

## Troubleshooting

### Ollama not responding:
```bash
sudo systemctl restart ollama
# or
ollama serve
```

### Git push fails:
```bash
# Setup GitHub token
gh auth login
# or use SSH keys
```

### Python dependencies missing:
```bash
pip3 install -r bot/requirements.txt
```

## Cost Estimate

**Digital Ocean Droplet:**
- Basic Droplet (2GB RAM): $12/month
- General Purpose (8GB RAM): $48/month (recommended for better AI performance)

**vs GitHub Actions Self-Hosted Runner:**
- Same droplet, same cost
- But you get full control and can run other services too

## Next Steps

1. Spin up Digital Ocean droplet
2. Install dependencies
3. Clone repo and configure
4. Test manual run
5. Setup automated scheduling
6. Monitor first few runs
7. Disable GitHub Actions workflow (or keep as backup)