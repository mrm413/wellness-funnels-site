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

### ⚡ Multi-Platform Support
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
│   ├── product_researcher.py    # Product validation and research
│   └── content_generator.py    # Content creation
├── data/                    # Research data and logs
│   ├── research_*.json      # Product research results
│   └── blacklist.json       # Rejected products
├── logs/                    # Execution logs
│   └── run_*.json           # Run results
└── output/                  # Generated content
    └── blog/                # HTML blog posts
```

## Configuration

Edit `blogguru/config.yml` to customize settings and add products.

### ClickBank Configuration

Update your ClickBank nickname in the configuration:

```yaml
platforms:
  clickbank:
    enabled: true
    nickname: fuelaura  # Your actual ClickBank nickname
    tracking_id: BLOG
```

### Product Configuration

You can configure products in two ways:

#### Option 1: Automatic Hoplink Generation (Legacy)
```yaml
products:
  - name: "Product Name"
    platform: clickbank
    product_id: "product-id"
    landing_page: "https://product-landing-page.com"
    hoplink: "https://{id}.vendor.hop.clickbank.net/?tid=BLOG"  # Template
```

#### Option 2: Manual Affiliate Link Entry (Recommended)
```yaml
products:
  - name: "Product Name"
    platform: clickbank
    product_id: "product-id"
    landing_page: "https://product-landing-page.com"
    affiliate_link: "https://your-manually-collected-link.com"  # Actual link
```

When you provide an `affiliate_link`, it will be used instead of generating a hoplink from the template.

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
- Saves content as HTML in `blogguru/output/blog/`
- Saves research data in `blogguru/data/`
- Logs execution results in `blogguru/logs/`

## Enhanced Features

### Manual Affiliate Link Collection
BlogGuru now supports manually collected affiliate links, which is especially useful for ClickBank's current workflow:

1. Visit ClickBank Marketplace
2. Find your product
3. Click "Promote" and copy the encrypted affiliate link
4. Add it to your product configuration as `affiliate_link`

### Complaint Reporting Mechanism
All generated content includes a section for users to report issues with affiliate links:

```html
<div class="complaint-section">
<h3>Report Issues with Affiliate Links</h3>
<p>If you encounter any problems with the affiliate links above, or if you believe they lead to unsafe or misleading products, please let us know immediately. We investigate all complaints and remove problematic links.</p>
<p><strong>Contact us:</strong> <a href="mailto:affiliate-complaints@example.com">affiliate-complaints@example.com</a></p>
</div>
```

### Enhanced Medical Disclaimers
BlogGuru automatically includes enhanced medical disclaimers in all content:

```
Medical Disclaimer: Before using any supplement, including [Product Name], 
you should consult with your healthcare provider to ensure it's appropriate for your 
specific health conditions and doesn't interact with any medications you're taking.
```

## Trust Score System

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

## Safety Features

- ✅ **Isolated system** - Won't break your main site
- ✅ **Quality control** - Rejects low-quality products
- ✅ **FTC compliance** - Includes required disclaimers
- ✅ **Medical safety** - Avoids medical claims
- ✅ **Scam detection** - Checks for fraud reports
- ✅ **Review validation** - Detects fake reviews

## Best Practices

1. **Start with dry run** - Research products first before generating content
2. **Review research data** - Check trust scores and evidence before publishing
3. **Update landing pages** - Keep product URLs current in config
4. **Monitor blacklist** - Review rejected products periodically
5. **Test content** - Read generated content before publishing
6. **Update regularly** - Re-research products every few months

## Troubleshooting

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
