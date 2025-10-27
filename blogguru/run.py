"""
BlogGuru Main Runner
Orchestrates the complete affiliate content generation workflow
"""

import os
import sys
import yaml
import json
import argparse
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from blogguru.core.product_researcher import ProductResearcher
from blogguru.core.content_generator import ContentGenerator


class BlogGuru:
    def __init__(self, config_path: str = 'blogguru/config.yml'):
        self.config_path = config_path
        self.config = self._load_config()
        
        # Check if system is enabled
        if not self.config['system']['enabled']:
            print("⚠️ BlogGuru is disabled in config. Set 'system.enabled: true' to enable.")
            sys.exit(0)
        
        # Initialize components
        self.researcher = ProductResearcher(self.config)
        self.generator = ContentGenerator(self.config)
        
        # Setup directories
        self._setup_directories()
    
    def _load_config(self) -> dict:
        """Load configuration file"""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"❌ Error loading config: {e}")
            sys.exit(1)
    
    def _setup_directories(self):
        """Create necessary directories"""
        dirs = [
            'blogguru/data',
            'blogguru/output/blog',
            'blogguru/logs'
        ]
        for d in dirs:
            Path(d).mkdir(parents=True, exist_ok=True)
    
    def run(self, product_name: str = None, dry_run: bool = False):
        """
        Main execution workflow
        
        Args:
            product_name: Specific product to process (None = all products)
            dry_run: If True, only research products without generating content
        """
        print("=" * 60)
        print("🚀 BlogGuru - Advanced Affiliate Content System")
        print("=" * 60)
        
        # Get products to process
        products = self._get_products(product_name)
        
        if not products:
            print("❌ No products found to process")
            return
        
        print(f"\n📦 Processing {len(products)} product(s)...")
        
        results = []
        
        for product in products:
            try:
                result = self._process_product(product, dry_run)
                results.append(result)
            except Exception as e:
                print(f"❌ Error processing {product['name']}: {e}")
                self._log_error(product['name'], str(e))
        
        # Summary
        self._print_summary(results)
        
        # Save results
        self._save_results(results)
    
    def _get_products(self, product_name: str = None) -> list:
        """Get products to process"""
        all_products = self.config.get('products', [])
        
        if product_name:
            # Filter by name
            products = [p for p in all_products if p['name'].lower() == product_name.lower()]
        else:
            # Get all enabled products
            products = [p for p in all_products if p.get('enabled', True)]
        
        return products
    
    def _process_product(self, product: dict, dry_run: bool) -> dict:
        """Process a single product"""
        print(f"\n{'=' * 60}")
        print(f"📦 Product: {product['name']}")
        print(f"{'=' * 60}")
        
        # Step 1: Research product
        research = self.researcher.research_product(product)
        
        # Save research data
        self._save_research(product['name'], research)
        
        # Check if approved
        if not research['approved']:
            print(f"❌ Product REJECTED - Trust score: {research['trust_score']}/100")
            print(f"   Reason: {research['recommendation']}")
            
            # Add to blacklist
            self._add_to_blacklist(product['name'], research)
            
            return {
                'product': product['name'],
                'status': 'rejected',
                'trust_score': research['trust_score'],
                'reason': research['recommendation']
            }
        
        print(f"✅ Product APPROVED - Trust score: {research['trust_score']}/100")
        
        # If dry run, stop here
        if dry_run:
            print("ℹ️ Dry run mode - skipping content generation")
            return {
                'product': product['name'],
                'status': 'approved',
                'trust_score': research['trust_score'],
                'content_generated': False
            }
        
        # Step 2: Generate content
        content = self.generator.generate_content(product, research)
        
        # Step 3: Save content
        output_path = self._save_content(content)
        
        print(f"✅ Content saved: {output_path}")
        
        return {
            'product': product['name'],
            'status': 'completed',
            'trust_score': research['trust_score'],
            'content_generated': True,
            'output_path': output_path,
            'word_count': content['word_count']
        }
    
    def _save_research(self, product_name: str, research: dict):
        """Save research data"""
        filename = f"blogguru/data/research_{self._slugify(product_name)}.json"
        with open(filename, 'w') as f:
            json.dump(research, f, indent=2)
    
    def _save_content(self, content: dict) -> str:
        """Save generated content"""
        filename = f"blogguru/output/blog/{content['slug']}.html"
        with open(filename, 'w') as f:
            f.write(content['content'])
        return filename
    
    def _add_to_blacklist(self, product_name: str, research: dict):
        """Add rejected product to blacklist"""
        blacklist_file = 'blogguru/data/blacklist.json'
        
        # Load existing blacklist
        if os.path.exists(blacklist_file):
            with open(blacklist_file, 'r') as f:
                blacklist = json.load(f)
        else:
            blacklist = []
        
        # Add product
        blacklist.append({
            'product': product_name,
            'trust_score': research['trust_score'],
            'reason': research['recommendation'],
            'rejected_at': datetime.utcnow().isoformat()
        })
        
        # Save
        with open(blacklist_file, 'w') as f:
            json.dump(blacklist, f, indent=2)
    
    def _save_results(self, results: list):
        """Save execution results"""
        filename = f"blogguru/logs/run_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
    
    def _print_summary(self, results: list):
        """Print execution summary"""
        print("\n" + "=" * 60)
        print("📊 EXECUTION SUMMARY")
        print("=" * 60)
        
        total = len(results)
        completed = len([r for r in results if r['status'] == 'completed'])
        rejected = len([r for r in results if r['status'] == 'rejected'])
        
        print(f"\nTotal Products: {total}")
        print(f"✅ Completed: {completed}")
        print(f"❌ Rejected: {rejected}")
        
        if completed > 0:
            print("\n✅ Completed Products:")
            for r in results:
                if r['status'] == 'completed':
                    print(f"   - {r['product']} ({r['word_count']} words)")
        
        if rejected > 0:
            print("\n❌ Rejected Products:")
            for r in results:
                if r['status'] == 'rejected':
                    print(f"   - {r['product']} (Score: {r['trust_score']}/100)")
                    print(f"     Reason: {r['reason']}")
    
    def _log_error(self, product_name: str, error: str):
        """Log error"""
        log_file = 'blogguru/logs/errors.log'
        with open(log_file, 'a') as f:
            f.write(f"[{datetime.utcnow().isoformat()}] {product_name}: {error}\n")
    
    def _slugify(self, text: str) -> str:
        """Convert text to slug"""
        import re
        slug = text.lower()
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        slug = re.sub(r'\s+', '-', slug)
        return slug.strip('-')


def main():
    parser = argparse.ArgumentParser(description='BlogGuru - Advanced Affiliate Content System')
    parser.add_argument('--product', type=str, help='Specific product name to process')
    parser.add_argument('--dry-run', action='store_true', help='Research only, no content generation')
    parser.add_argument('--config', type=str, default='blogguru/config.yml', help='Config file path')
    
    args = parser.parse_args()
    
    # Initialize and run
    blogguru = BlogGuru(config_path=args.config)
    blogguru.run(product_name=args.product, dry_run=args.dry_run)


if __name__ == '__main__':
    main()