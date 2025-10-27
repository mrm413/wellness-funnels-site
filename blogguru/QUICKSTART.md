# BlogGuru Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Verify Installation

BlogGuru is already installed in your repository. Check that these files exist:
```bash
ls blogguru/
# Should show: README.md, config.yml, run.py, core/, etc.
```

### Step 2: Set Your OpenAI API Key

```bash
export OPENAI_API_KEY="sk-your-key-here"
```

Or add to your `~/.blogguru-env` file:
```bash
echo 'export OPENAI_API_KEY="sk-your-key-here"' >> ~/.blogguru-env
source ~/.blogguru-env
```

### Step 3: Configure Your Products

Edit `blogguru/config.yml`:

```yaml
# Update your ClickBank nickname
platforms:
  clickbank:
    nickname: YOUR_CLICKBANK_NICKNAME  # Change this!

# Add your products
products:
  - name: "Your Product Name"
    platform: clickbank
    product_id: "your-product-id"
    landing_page: "https://product-landing-page.com"  # Important!
    hoplink: "https://{id}.vendor.hop.clickbank.net/?tid=BLOG"
    category: health
    keywords:
      - keyword1
      - keyword2
```

### Step 4: Run BlogGuru

**Research a product (dry run):**
```bash
python3 blogguru/run.py --dry-run
```

**Generate content for all approved products:**
```bash
python3 blogguru/run.py
```

**Generate content for specific product:**
```bash
python3 blogguru/run.py --product "Product Name"
```

### Step 5: Review Output

Generated content is saved to:
```
blogguru/output/blog/YYYY-MM-DD-product-name.html
```

Research data is saved to:
```
blogguru/data/research_product-name.json
```

### Step 6: Publish to Your Site

**Option A: Manual Copy**
```bash
cp blogguru/output/blog/*.html blog/
git add blog/
git commit -m "Add new affiliate content"
git push
```

**Option B: Auto-publish (coming soon)**
Set `output.auto_publish: true` in config.yml

---

## 📋 Common Commands

```bash
# Research all products
python3 blogguru/run.py --dry-run

# Generate content for all products
python3 blogguru/run.py

# Generate for specific product
python3 blogguru/run.py --product "Probiotic 50B CFU"

# Check logs
tail -f blogguru/logs/blogguru.log

# View research data
cat blogguru/data/research_*.json | jq

# View blacklist
cat blogguru/data/blacklist.json | jq
```

---

## 🎯 What BlogGuru Does

### 1. Product Research (Automatic)
- ✅ Scrapes product landing page
- ✅ Extracts claims and benefits
- ✅ Searches for reviews (positive & negative)
- ✅ Checks for scam reports
- ✅ Finds supporting evidence from trusted sources
- ✅ Calculates trust score (0-100)
- ✅ Rejects low-quality products

### 2. Content Generation (If Approved)
- ✅ Creates SEO-optimized outline
- ✅ Generates 1200-2000 word article
- ✅ Adds backlinks to authority sites
- ✅ Includes FAQ section
- ✅ Adds pros/cons
- ✅ Creates compelling CTA
- ✅ Includes FTC-compliant disclaimer

### 3. Quality Control
- ✅ Checks readability score
- ✅ Validates keyword density
- ✅ Ensures proper formatting
- ✅ Verifies backlinks work

---

## ⚙️ Configuration Tips

### Adjust Trust Score Threshold

Lower = more products approved, higher = stricter quality control

```yaml
research:
  trust_score_threshold: 60  # Default: 60
```

### Change Content Length

```yaml
content:
  min_words: 1200  # Minimum words
  max_words: 2000  # Maximum words
```

### Change Tone

```yaml
content:
  tone: professional  # Options: professional, casual, friendly, authoritative
```

### Disable BlogGuru

```yaml
system:
  enabled: false  # Set to false to disable completely
```

---

## 🔍 Understanding Trust Scores

| Score | Meaning | Action |
|-------|---------|--------|
| 80-100 | Excellent | Highly recommended |
| 60-79 | Good | Recommended |
| 40-59 | Fair | Proceed with caution |
| 0-39 | Poor | Rejected |

Trust score is calculated based on:
- Supporting evidence from trusted sources (+15-20 points)
- Positive reviews (+10-20 points)
- No scam reports (+15 points)
- Red flags detected (-5 points each)
- Scam reports found (-30 points)
- Fake reviews detected (-20 points)

---

## 🛠️ Troubleshooting

### "OpenAI API key not found"
```bash
export OPENAI_API_KEY="sk-your-key-here"
```

### "Product rejected"
Check research data:
```bash
cat blogguru/data/research_product-name.json
```

Lower trust threshold in config.yml if needed.

### "No products found"
Make sure products are enabled in config.yml:
```yaml
products:
  - name: "Product Name"
    enabled: true  # Add this if missing
```

### Content quality issues
Adjust settings in config.yml:
```yaml
content:
  min_words: 1500  # Increase for longer content
  tone: authoritative  # Change tone
```

---

## 📊 Monitoring

### View Recent Runs
```bash
ls -lt blogguru/logs/run_*.json | head -5
cat blogguru/logs/run_YYYYMMDD_HHMMSS.json | jq
```

### Check Errors
```bash
tail -f blogguru/logs/errors.log
```

### View Blacklist
```bash
cat blogguru/data/blacklist.json | jq
```

---

## 🎓 Best Practices

1. **Start with dry run** - Research products first before generating content
2. **Review research data** - Check trust scores and evidence before publishing
3. **Update landing pages** - Keep product URLs current in config
4. **Monitor blacklist** - Review rejected products periodically
5. **Test content** - Read generated content before publishing
6. **Update regularly** - Re-research products every few months

---

## 🔐 Safety Features

- ✅ **Isolated system** - Won't break your main site
- ✅ **Quality control** - Rejects low-quality products
- ✅ **FTC compliance** - Includes required disclaimers
- ✅ **Medical safety** - Avoids medical claims
- ✅ **Scam detection** - Checks for fraud reports
- ✅ **Review validation** - Detects fake reviews

---

## 📞 Need Help?

1. Check logs: `blogguru/logs/`
2. Review config: `blogguru/config.yml`
3. Read full docs: `blogguru/README.md`
4. Check research data: `blogguru/data/`

---

**You're ready to go! Start with a dry run to see how it works:**

```bash
python3 blogguru/run.py --dry-run
```