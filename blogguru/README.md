# BlogGuru - Advanced Affiliate Content System

## Overview

BlogGuru is an **isolated, modular affiliate content generation system** designed to:
- Research and validate affiliate products before promotion
- Create high-quality, SEO-optimized content
- Support multiple affiliate platforms
- Operate independently without affecting your main site

## Key Features

### 🔍 Intelligent Product Research
- Scrapes affiliate product pages
- Analyzes product claims and benefits
- Searches for reviews (positive AND negative)
- Detects fake reviews vs legitimate complaints
- Generates trust score (0-100)
- Only proceeds if product passes quality threshold

### 📝 Advanced Content Creation
- Researches supporting evidence from authoritative sources
- Creates strategic backlinks to trusted sites
- Writes compelling, pre-sell content
- SEO-optimized titles and meta descriptions
- Natural product integration (not spammy)

### 🔌 Multi-Platform Support
- ClickBank
- Amazon Associates
- ShareASale
- CJ Affiliate
- Impact
- Custom affiliate programs
- Easy configuration for new platforms

### 🛡️ Fail-Safe Design
- Completely isolated from main site
- Can be disabled with one switch
- Independent configuration
- Separate logging and error handling
- Won't break your site if it fails

## Directory Structure

```
blogguru/
├── README.md                 # This file
├── config.yml               # Main configuration
├── core/
│   ├── __init__.py
│   ├── product_researcher.py    # Product validation and research
│   ├── content_generator.py     # AI content creation
│   ├── affiliate_manager.py     # Multi-platform affiliate support
│   └── quality_checker.py       # Content quality validation
├── platforms/
│   ├── __init__.py
│   ├── clickbank.py            # ClickBank integration
│   ├── amazon.py               # Amazon Associates
│   ├── shareasale.py           # ShareASale
│   ├── cj.py                   # CJ Affiliate
│   └── custom.py               # Custom affiliate programs
├── data/
│   ├── products.json           # Product database
│   ├── trust_scores.json       # Product trust scores
│   └── blacklist.json          # Rejected products
├── output/
│   └── blog/                   # Generated blog posts
└── logs/
    └── blogguru.log            # System logs
```

## Installation

BlogGuru is already included in your repository. No additional installation needed.

## Configuration

Edit `blogguru/config.yml` to customize settings and add products.

## Usage

### Basic Usage

```bash
# Run BlogGuru
python3 blogguru/run.py

# Run with specific product
python3 blogguru/run.py --product "Product Name"

# Run with specific platform
python3 blogguru/run.py --platform clickbank

# Dry run (research only, no content generation)
python3 blogguru/run.py --dry-run
```

### Disabling BlogGuru

Set `enabled: false` in `blogguru/config.yml` to completely disable the system.

## How It Works

### 1. Product Research Phase
- Scrapes product landing page
- Extracts claims, benefits, ingredients
- Searches for reviews across multiple platforms
- Analyzes sentiment (positive vs negative)
- Detects fake reviews using AI
- Calculates trust score

### 2. Quality Check
- If trust score less than threshold: Product rejected
- If trust score greater than or equal to threshold: Proceed to content generation
- Logs decision and reasoning

### 3. Content Generation
- Researches supporting evidence from trusted sources
- Creates outline with strategic sections
- Generates SEO-optimized content
- Adds backlinks to authoritative sites
- Integrates affiliate links naturally
- Creates compelling call-to-action

### 4. Output
- Saves blog post to `blogguru/output/blog/`
- Updates product database
- Logs all actions

## Safety Features

### Isolation
- Runs in separate directory
- Independent configuration
- Separate error handling
- Won't affect main site if it crashes

### Quality Control
- Trust score validation
- Content quality checks
- Spam detection
- Duplicate content prevention

### Monitoring
- Detailed logging
- Error tracking
- Performance metrics
- Product rejection reasons

## Integration with Main Site

BlogGuru outputs are stored in `blogguru/output/blog/`. To publish to your main site:

```bash
# Copy approved posts to main blog directory
cp blogguru/output/blog/*.html blog/

# Or use the publish script
python3 blogguru/publish.py
```

## Troubleshooting

### BlogGuru not running
- Check `blogguru/config.yml` - ensure `enabled: true`
- Check logs: `tail -f blogguru/logs/blogguru.log`

### Products being rejected
- Check trust scores: `cat blogguru/data/trust_scores.json`
- Lower quality threshold in config
- Review rejection reasons in logs

### Content quality issues
- Adjust `min_words` and `max_words` in config
- Change `tone` setting
- Review generated content in `blogguru/output/blog/`

## Maintenance

### Update Product Database
```bash
python3 blogguru/maintenance.py --update-products
```

### Clean Old Data
```bash
python3 blogguru/maintenance.py --clean --days 30
```

### Backup
```bash
python3 blogguru/maintenance.py --backup
```

## Support

For issues or questions, check:
1. Logs: `blogguru/logs/blogguru.log`
2. Configuration: `blogguru/config.yml`
3. Product database: `blogguru/data/products.json`