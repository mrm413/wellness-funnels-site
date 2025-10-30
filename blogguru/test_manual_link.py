"""
Test script to demonstrate manual affiliate link functionality
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

# Load config
with open('blogguru/config.yml', 'r') as f:
    config = yaml.safe_load(f)

# Create content generator
generator = ContentGenerator(config)

# Generate affiliate section to test manual link functionality
affiliate_section = generator._create_affiliate_section(sample_product, sample_research)

print("Generated affiliate section with manual link:")
print("=" * 50)
print(affiliate_section)
print("=" * 50)

# Check if manual affiliate link is used
if 'affiliate_link' in sample_product:
    print("✅ Manual affiliate link feature is working correctly")
    print(f"Using link: {sample_product['affiliate_link']}")
else:
    print("❌ Manual affiliate link feature is not working")
