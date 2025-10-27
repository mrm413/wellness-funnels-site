"""
Content Generator Module
Creates high-quality, SEO-optimized affiliate content
"""

import os
import re
import json
from datetime import datetime
from typing import Dict, List
import openai

class ContentGenerator:
    def __init__(self, config: dict):
        self.config = config
        self.openai_key = os.environ.get(config['openai']['api_key_env'])
        if not self.openai_key:
            raise ValueError(f"OpenAI API key not found in environment variable: {config['openai']['api_key_env']}")
        
        openai.api_key = self.openai_key

    def generate_content(self, product: dict, research: dict) -> Dict:
        """
        Generate complete blog post content
        Returns: {
            'title': str,
            'meta_description': str,
            'slug': str,
            'content': str (HTML),
            'word_count': int,
            'backlinks': list,
            'keywords': list
        }
        """
        print(f"\n✍️ Generating content for: {product['name']}")
        
        # Step 1: Create outline
        outline = self._create_outline(product, research)
        
        # Step 2: Generate main content
        content = self._generate_main_content(product, research, outline)
        
        # Step 3: Add backlinks
        content_with_backlinks = self._add_backlinks(content, research['evidence'])
        
        # Step 4: Generate SEO elements
        title = self._generate_seo_title(product, research)
        meta_description = self._generate_meta_description(product, research)
        slug = self._generate_slug(title)
        
        # Step 5: Format as HTML
        html_content = self._format_as_html(
            title=title,
            meta_description=meta_description,
            content=content_with_backlinks,
            product=product,
            research=research
        )
        
        # Step 6: Count words
        word_count = len(content.split())
        
        result = {
            'title': title,
            'meta_description': meta_description,
            'slug': slug,
            'content': html_content,
            'word_count': word_count,
            'backlinks': self._extract_backlinks(content_with_backlinks),
            'keywords': product.get('keywords', []),
            'generated_at': datetime.utcnow().isoformat()
        }
        
        print(f"✅ Content generated: {word_count} words")
        
        return result

    def _create_outline(self, product: dict, research: dict) -> str:
        """Create content outline"""
        prompt = f"""Create a detailed outline for a blog post about "{product['name']}".
        
        Product Information:
        - Claims: {', '.join(research['claims'][:3])}
        - Benefits: {', '.join(research['benefits'][:3])}
        - Trust Score: {research['trust_score']}/100
        
        Requirements:
        - {self.config['content']['min_words']}-{self.config['content']['max_words']} words
        - Tone: {self.config['content']['tone']}
        - Include: Introduction, Benefits, Evidence, How It Works, Who It's For, FAQ, Conclusion
        - Pre-sell approach (build value before affiliate link)
        - Include sections for backlinks to authority sites
        
        Create an outline with H2 and H3 headings."""
        
        return self._call_openai(prompt, max_tokens=800)

    def _generate_main_content(self, product: dict, research: dict, outline: str) -> str:
        """Generate main article content"""
        evidence_summary = "\n".join([
            f"- {e['title']} ({e['source']})"
            for e in research['evidence'][:5]
        ])
        
        prompt = f"""Write a comprehensive, engaging blog post about "{product['name']}" based on this outline.
        
        Outline:
        {outline}
        
        Product Details:
        - Claims: {', '.join(research['claims'])}
        - Benefits: {', '.join(research['benefits'])}
        - Supporting Evidence: {evidence_summary}
        
        Requirements:
        - {self.config['content']['min_words']}-{self.config['content']['max_words']} words
        - Tone: {self.config['content']['tone']}
        - Use short paragraphs (2-3 sentences)
        - Include subheadings (H2, H3)
        - Pre-sell approach: Build value and trust before mentioning the product
        - Include evidence from research
        - Natural, conversational style
        - SEO-optimized but not keyword-stuffed
        - Include FAQ section if enabled: {self.config['content']['include_faq']}
        - Include pros/cons if enabled: {self.config['content']['include_pros_cons']}
        
        Important:
        - DO NOT make medical claims
        - Encourage consulting healthcare professionals
        - Be honest about limitations
        - Include disclaimer about affiliate relationship
        
        Write the complete article in markdown format."""
        
        return self._call_openai(prompt, max_tokens=2500)

    def _add_backlinks(self, content: str, evidence: List[Dict]) -> str:
        """Add strategic backlinks to authority sites"""
        if not self.config['backlinks']['enabled']:
            return content
        
        # Find opportunities to add backlinks
        backlink_count = 0
        max_backlinks = self.config['backlinks']['max_backlinks']
        
        for ev in evidence:
            if backlink_count >= max_backlinks:
                break
            
            # Find relevant sentence to add link
            # This is a simplified approach - in production, use more sophisticated matching
            if ev['claim'] in content:
                # Add link to the claim
                link_text = f"[according to research]({ev['url']})"
                content = content.replace(
                    ev['claim'],
                    f"{ev['claim']} {link_text}",
                    1  # Replace only first occurrence
                )
                backlink_count += 1
        
        return content

    def _generate_seo_title(self, product: dict, research: dict) -> str:
        """Generate SEO-optimized title (max 60 chars)"""
        prompt = f"""Create an SEO-optimized title (max 60 characters) for a blog post about "{product['name']}".
        
        Product benefits: {', '.join(research['benefits'][:2])}
        Keywords: {', '.join(product.get('keywords', [])[:2])}
        
        Requirements:
        - Compelling and click-worthy
        - Include main keyword
        - Under 60 characters
        - No clickbait
        
        Return only the title, nothing else."""
        
        title = self._call_openai(prompt, max_tokens=50)
        return title.strip('"').strip()[:60]

    def _generate_meta_description(self, product: dict, research: dict) -> str:
        """Generate meta description (max 155 chars)"""
        prompt = f"""Create a compelling meta description (max 155 characters) for a blog post about "{product['name']}".
        
        Product benefits: {', '.join(research['benefits'][:2])}
        
        Requirements:
        - Compelling and informative
        - Include call-to-action
        - Under 155 characters
        
        Return only the description, nothing else."""
        
        desc = self._call_openai(prompt, max_tokens=100)
        return desc.strip('"').strip()[:155]

    def _generate_slug(self, title: str) -> str:
        """Generate URL-friendly slug"""
        slug = title.lower()
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        slug = re.sub(r'\s+', '-', slug)
        slug = slug.strip('-')[:70]
        
        # Add date prefix
        date_prefix = datetime.utcnow().strftime("%Y-%m-%d")
        return f"{date_prefix}-{slug}"

    def _format_as_html(self, title: str, meta_description: str, 
                       content: str, product: dict, research: dict) -> str:
        """Format content as HTML"""
        # Convert markdown to HTML (simplified)
        html_content = self._markdown_to_html(content)
        
        # Add affiliate section
        affiliate_section = self._create_affiliate_section(product, research)
        
        # Add disclaimer
        disclaimer = self.config['safety']['disclaimer_text']
        
        # Build complete HTML
        html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>{title}</title>
<meta name="description" content="{meta_description}">
<style>
body {{
    font-family: system-ui, -apple-system, sans-serif;
    max-width: 800px;
    margin: 40px auto;
    padding: 0 20px;
    line-height: 1.6;
    color: #333;
}}
h1, h2, h3 {{ color: #2c3e50; }}
h1 {{ font-size: 2.2em; margin-bottom: 0.5em; }}
h2 {{ font-size: 1.8em; margin-top: 1.5em; }}
h3 {{ font-size: 1.4em; margin-top: 1.2em; }}
p {{ margin: 1em 0; }}
a {{ color: #3498db; text-decoration: none; }}
a:hover {{ text-decoration: underline; }}
.affiliate-box {{
    background: #f8f9fa;
    border: 2px solid #3498db;
    border-radius: 8px;
    padding: 20px;
    margin: 30px 0;
}}
.cta-button {{
    display: inline-block;
    background: #3498db;
    color: white;
    padding: 12px 30px;
    border-radius: 5px;
    text-decoration: none;
    font-weight: bold;
    margin: 10px 0;
}}
.cta-button:hover {{
    background: #2980b9;
    text-decoration: none;
}}
.disclaimer {{
    background: #fff3cd;
    border-left: 4px solid #ffc107;
    padding: 15px;
    margin: 30px 0;
    font-size: 0.9em;
}}
.trust-score {{
    background: #d4edda;
    border: 1px solid #c3e6cb;
    padding: 10px;
    border-radius: 5px;
    margin: 20px 0;
}}
.complaint-section {{
    background: #f8d7da;
    border: 1px solid #f5c6cb;
    border-radius: 5px;
    padding: 15px;
    margin: 20px 0;
    font-size: 0.9em;
}}
</style>
</head>
<body>
<article>
<h1>{title}</h1>

{html_content}

{affiliate_section}

<div class="complaint-section">
<h3>Report Issues with Affiliate Links</h3>
<p>If you encounter any problems with the affiliate links above, or if you believe they lead to unsafe or misleading products, please let us know immediately. We investigate all complaints and remove problematic links.</p>
<p><strong>Contact us:</strong> <a href="mailto:affiliate-complaints@example.com">affiliate-complaints@example.com</a></p>
</div>

<div class="disclaimer">
{disclaimer}
</div>

</article>
</body>
</html>"""
        
        return html

    def _create_affiliate_section(self, product: dict, research: dict) -> str:
        """Create affiliate product section"""
        platform = product['platform']
        
        # Get affiliate link
        if 'affiliate_link' in product:
            # Use manually provided affiliate link
            affiliate_link = product['affiliate_link']
        elif platform == 'clickbank':
            # Generate hoplink if nickname is provided
            affiliate_id = self.config['platforms']['clickbank'].get('nickname', 'YOURNICKNAME')
            affiliate_link = product['hoplink'].replace('{id}', affiliate_id)
        else:
            affiliate_link = product.get('hoplink', '#')
        
        return f"""
<div class="affiliate-box">
<h2>Ready to Try {product['name']}?</h2>

<div class="trust-score">
<strong>Our Research Score:</strong> {research['trust_score']}/100<br>
<em>{research['recommendation']}</em>
</div>

<p>Based on our research, {product['name']} shows promising results. Here's what we found:</p>
<ul>
{''.join([f'<li>{benefit}</li>' for benefit in research['benefits'][:3]])}
</ul>

<p style="text-align: center;">
<a href="{affiliate_link}" class="cta-button" target="_blank" rel="nofollow sponsored">
Learn More About {product['name']} →
</a>
</p>

<p style="font-size: 0.9em; color: #666;">
<strong>Note:</strong> This is an affiliate link. We may earn a commission if you make a purchase, 
at no additional cost to you. We only recommend products we've thoroughly researched.
</p>

<p style="font-size: 0.8em; color: #888;">
<strong>Medical Disclaimer:</strong> Before using any supplement, including {product['name']}, 
you should consult with your healthcare provider to ensure it's appropriate for your 
specific health conditions and doesn't interact with any medications you're taking.
</p>
</div>
"""

    def _markdown_to_html(self, markdown: str) -> str:
        """Convert markdown to HTML (simplified)"""
        html = markdown
        
        # Headers
        html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        
        # Links
        html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank">\1</a>', html)
        
        # Bold
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        
        # Italic
        html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
        
        # Lists
        html = re.sub(r'^\- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        html = re.sub(r'(<li>.*</li>)', r'<ul>\1</ul>', html, flags=re.DOTALL)
        
        # Paragraphs
        paragraphs = html.split('\n\n')
        html = '\n'.join([f'<p>{p}</p>' if not p.startswith('<') else p for p in paragraphs if p.strip()])
        
        return html

    def _extract_backlinks(self, content: str) -> List[str]:
        """Extract all backlinks from content"""
        links = re.findall(r'href="([^"]+)"', content)
        return [link for link in links if link.startswith('http')]

    def _call_openai(self, prompt: str, max_tokens: int = 2000) -> str:
        """Call OpenAI API"""
        try:
            response = openai.ChatCompletion.create(
                model=self.config['openai']['model'],
                messages=[
                    {"role": "system", "content": "You are an expert content writer specializing in health and wellness. Write engaging, accurate, SEO-optimized content."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config['openai']['temperature'],
                max_tokens=max_tokens
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"⚠️ OpenAI API error: {e}")
            return ""
