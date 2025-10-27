"""
Test script to demonstrate complaint reporting mechanism
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from blogguru.core.content_generator import ContentGenerator
import yaml

# Sample product with manual affiliate link
sample_product = {
    'name': 'HealthMax Probiotics',
    'platform': 'clickbank',
    'product_id': 'healthmax-probio',
    'landing_page': 'https://healthmax-probiotics.com',
    'affiliate_link': 'https://fuelaura.health.hop.clickbank.net/?tid=BLOGGURU',
    'category': 'health',
    'keywords': ['probiotics', 'gut health', 'digestive health']
}

# Sample research data
sample_research = {
    'product_name': 'HealthMax Probiotics',
    'trust_score': 75,
    'approved': True,
    'claims': [
        'Supports digestive health',
        'Boosts immune system function',
        'Promotes gut microbiome balance'
    ],
    'benefits': [
        'Improves digestive health and regularity',
        'Strengthens immune system response',
        'Supports mental health through gut-brain connection'
    ],
    'ingredients': ['Lactobacillus acidophilus', 'Bifidobacterium bifidum', 'Streptococcus thermophilus'],
    'evidence': [
        {
            'claim': 'Probiotics support digestive health',
            'source': 'nih.gov',
            'title': 'Probiotics for digestive health',
            'url': 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3707649/',
            'snippet': 'Research shows probiotics can improve digestive function'
        }
    ],
    'reviews': {
        'positive': ['Great for gut health', 'Noticeable improvement in digestion'],
        'negative': ['Too expensive for some users'],
        'neutral': [],
        'fake_detected': False,
        'sentiment_score': 0.7
    },
    'scam_check': {
        'scam_reports_found': False,
        'bbb_rating': 'A+',
        'complaint_count': 0,
        'sources': []
    },
    'red_flags': [],
    'recommendation': 'Highly recommended - Strong evidence and positive reviews',
    'researched_at': '2025-10-27T16:15:00.000000'
}

# Sample content
sample_content = """
# HealthMax Probiotics: The Key to Better Digestive Health

## Introduction

In today's health-conscious world, probiotics have gained significant attention for their potential benefits to digestive health and overall well-being.

## Benefits of HealthMax Probiotics

### Improved Digestive Health

HealthMax Probiotics can help improve digestive regularity and reduce common digestive issues.

### Enhanced Immune System

Probiotics support immune system function through the gut-immune connection.

## Conclusion

HealthMax Probiotics offer promising benefits for digestive and immune health.
"""

# Load config
with open('blogguru/config.yml', 'r') as f:
    config = yaml.safe_load(f)

# Create content generator
generator = ContentGenerator(config)

# Generate complete HTML to test complaint mechanism
html_content = generator._format_as_html(
    title="HealthMax Probiotics: The Key to Better Digestive Health",
    meta_description="Discover the benefits of HealthMax Probiotics for digestive health and immune function.",
    content=sample_content,
    product=sample_product,
    research=sample_research
)

# Save to file
with open('blogguru/test_output.html', 'w') as f:
    f.write(html_content)

print("Generated complete HTML with complaint mechanism:")
print("=" * 50)
print("Check the generated file: blogguru/test_output.html")
print("=" * 50)

# Verify complaint section is included
if 'complaint-section' in html_content:
    print("✅ Complaint reporting mechanism is working correctly")
else:
    print("❌ Complaint reporting mechanism is not working")

# Verify medical disclaimer is enhanced
if 'healthcare provider' in html_content:
    print("✅ Enhanced medical disclaimer is working correctly")
else:
    print("❌ Enhanced medical disclaimer is not working")
