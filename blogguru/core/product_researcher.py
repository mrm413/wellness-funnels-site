"""
Product Researcher Module
Researches and validates affiliate products before content creation
"""

import os
import re
import json
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from typing import Dict, List, Tuple
import openai

class ProductResearcher:
    def __init__(self, config: dict):
        self.config = config
        self.openai_key = os.environ.get(config['openai']['api_key_env'])
        if not self.openai_key:
            raise ValueError(f"OpenAI API key not found in environment variable: {config['openai']['api_key_env']}")
        
        openai.api_key = self.openai_key
        self.headers = {'User-Agent': 'Mozilla/5.0 (compatible; BlogGuru/1.0)'}
    
    def research_product(self, product: dict) -> Dict:
        """
        Complete product research workflow
        Returns: {
            'product_name': str,
            'trust_score': int (0-100),
            'approved': bool,
            'claims': list,
            'evidence': list,
            'reviews': dict,
            'red_flags': list,
            'recommendation': str
        }
        """
        print(f"\n🔍 Researching: {product['name']}")
        
        # Step 1: Scrape product landing page
        product_data = self._scrape_landing_page(product['landing_page'])
        
        # Step 2: Search for reviews
        reviews = self._search_reviews(product['name'])
        
        # Step 3: Check for scam reports
        scam_check = self._check_scam_reports(product['name'])
        
        # Step 4: Find supporting evidence
        evidence = self._find_evidence(product_data['claims'], product.get('keywords', []))
        
        # Step 5: Calculate trust score
        trust_score = self._calculate_trust_score(product_data, reviews, scam_check, evidence)
        
        # Step 6: Generate recommendation
        approved = trust_score >= self.config['research']['trust_score_threshold']
        
        result = {
            'product_name': product['name'],
            'trust_score': trust_score,
            'approved': approved,
            'claims': product_data['claims'],
            'benefits': product_data['benefits'],
            'ingredients': product_data.get('ingredients', []),
            'evidence': evidence,
            'reviews': reviews,
            'scam_check': scam_check,
            'red_flags': product_data.get('red_flags', []),
            'recommendation': self._generate_recommendation(trust_score, approved),
            'researched_at': datetime.utcnow().isoformat()
        }
        
        print(f"✅ Trust Score: {trust_score}/100 - {'APPROVED' if approved else 'REJECTED'}")
        
        return result
    
    def _scrape_landing_page(self, url: str) -> Dict:
        """Scrape and analyze product landing page"""
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract text content
            text = soup.get_text(separator=' ', strip=True)
            
            # Use AI to extract claims and benefits
            prompt = f"""Analyze this product landing page and extract:
1. Main product claims (what it promises to do)
2. Key benefits listed
3. Any ingredients or components mentioned
4. Any red flags (unrealistic claims, pressure tactics, fake urgency)

Product page text:
{text[:5000]}

Return as JSON:
{{
    "claims": ["claim1", "claim2"],
    "benefits": ["benefit1", "benefit2"],
    "ingredients": ["ingredient1", "ingredient2"],
    "red_flags": ["flag1", "flag2"]
}}
"""
            
            result = self._call_openai(prompt)
            return json.loads(result)
            
        except Exception as e:
            print(f"⚠️ Error scraping landing page: {e}")
            return {
                'claims': [],
                'benefits': [],
                'ingredients': [],
                'red_flags': ['Unable to scrape landing page']
            }
    
    def _search_reviews(self, product_name: str) -> Dict:
        """Search for product reviews across multiple platforms"""
        reviews = {
            'positive': [],
            'negative': [],
            'neutral': [],
            'fake_detected': False,
            'sentiment_score': 0
        }
        
        # Search queries
        queries = [
            f'"{product_name}" review',
            f'"{product_name}" scam',
            f'"{product_name}" complaints',
            f'"{product_name}" reddit',
            f'"{product_name}" trustpilot'
        ]
        
        all_reviews = []
        
        for query in queries:
            try:
                # Use web search to find reviews
                search_results = self._web_search(query, num_results=5)
                
                for result in search_results:
                    # Extract review content
                    review_text = self._extract_review_content(result['url'])
                    if review_text:
                        all_reviews.append(review_text)
                        
            except Exception as e:
                print(f"⚠️ Error searching reviews for '{query}': {e}")
        
        if all_reviews:
            # Analyze reviews with AI
            analysis = self._analyze_reviews_with_ai(all_reviews, product_name)
            reviews.update(analysis)
        
        return reviews
    
    def _check_scam_reports(self, product_name: str) -> Dict:
        """Check for scam reports and complaints"""
        scam_check = {
            'scam_reports_found': False,
            'bbb_rating': None,
            'complaint_count': 0,
            'sources': []
        }
        
        # Search for scam reports
        scam_queries = [
            f'"{product_name}" scam',
            f'"{product_name}" fraud',
            f'"{product_name}" BBB',
            f'"{product_name}" FTC complaint'
        ]
        
        for query in scam_queries:
            try:
                results = self._web_search(query, num_results=3)
                
                for result in results:
                    # Check if result indicates scam
                    if any(word in result['title'].lower() or word in result.get('snippet', '').lower() 
                           for word in ['scam', 'fraud', 'fake', 'ripoff']):
                        scam_check['scam_reports_found'] = True
                        scam_check['sources'].append({
                            'url': result['url'],
                            'title': result['title']
                        })
                        
            except Exception as e:
                print(f"⚠️ Error checking scam reports: {e}")
        
        return scam_check
    
    def _find_evidence(self, claims: List[str], keywords: List[str]) -> List[Dict]:
        """Find scientific evidence supporting product claims"""
        evidence = []
        
        # Search trusted sources
        trusted_sources = self.config['research']['evidence_sources']
        
        for claim in claims[:3]:  # Limit to top 3 claims
            for source in trusted_sources[:3]:  # Limit to top 3 sources
                try:
                    query = f'site:{source} {" ".join(keywords[:2])} {claim[:50]}'
                    results = self._web_search(query, num_results=2)
                    
                    for result in results:
                        evidence.append({
                            'claim': claim,
                            'source': source,
                            'title': result['title'],
                            'url': result['url'],
                            'snippet': result.get('snippet', '')
                        })
                        
                except Exception as e:
                    print(f"⚠️ Error finding evidence: {e}")
        
        return evidence
    
    def _calculate_trust_score(self, product_data: Dict, reviews: Dict, 
                               scam_check: Dict, evidence: List) -> int:
        """Calculate overall trust score (0-100)"""
        score = 50  # Start at neutral
        
        # Positive factors
        if len(evidence) >= 3:
            score += 15
        elif len(evidence) >= 1:
            score += 10
        
        if reviews['sentiment_score'] > 0.6:
            score += 20
        elif reviews['sentiment_score'] > 0.3:
            score += 10
        
        if not scam_check['scam_reports_found']:
            score += 15
        
        # Negative factors
        if product_data.get('red_flags'):
            score -= len(product_data['red_flags']) * 5
        
        if scam_check['scam_reports_found']:
            score -= 30
        
        if reviews['fake_detected']:
            score -= 20
        
        if reviews['sentiment_score'] < 0:
            score -= 20
        
        # Clamp between 0-100
        return max(0, min(100, score))
    
    def _generate_recommendation(self, trust_score: int, approved: bool) -> str:
        """Generate human-readable recommendation"""
        if trust_score >= 80:
            return "Highly recommended - Strong evidence and positive reviews"
        elif trust_score >= 60:
            return "Recommended - Sufficient evidence and generally positive feedback"
        elif trust_score >= 40:
            return "Proceed with caution - Mixed reviews or limited evidence"
        else:
            return "Not recommended - Insufficient evidence or negative indicators"
    
    def _web_search(self, query: str, num_results: int = 5) -> List[Dict]:
        """Perform web search (placeholder - implement with actual search API)"""
        # TODO: Implement with actual search API (Google Custom Search, Bing, etc.)
        # For now, return empty list
        return []
    
    def _extract_review_content(self, url: str) -> str:
        """Extract review content from URL"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            text = soup.get_text(separator=' ', strip=True)
            return text[:2000]  # Limit to 2000 chars
            
        except Exception:
            return ""
    
    def _analyze_reviews_with_ai(self, reviews: List[str], product_name: str) -> Dict:
        """Analyze reviews using AI"""
        combined_reviews = "\n\n".join(reviews[:10])  # Limit to 10 reviews
        
        prompt = f"""Analyze these reviews for "{product_name}" and provide:
1. Sentiment score (-1 to 1, where -1 is very negative, 0 is neutral, 1 is very positive)
2. Are there signs of fake reviews? (yes/no)
3. Categorize reviews into positive, negative, neutral (provide counts)
4. Key themes in positive reviews
5. Key themes in negative reviews

Reviews:
{combined_reviews}

Return as JSON:
{{
    "sentiment_score": 0.5,
    "fake_detected": false,
    "positive_count": 5,
    "negative_count": 2,
    "neutral_count": 3,
    "positive_themes": ["theme1", "theme2"],
    "negative_themes": ["theme1", "theme2"]
}}
"""
        
        try:
            result = self._call_openai(prompt)
            analysis = json.loads(result)
            
            return {
                'sentiment_score': analysis.get('sentiment_score', 0),
                'fake_detected': analysis.get('fake_detected', False),
                'positive': analysis.get('positive_themes', []),
                'negative': analysis.get('negative_themes', []),
                'neutral': []
            }
        except Exception as e:
            print(f"⚠️ Error analyzing reviews: {e}")
            return {
                'sentiment_score': 0,
                'fake_detected': False,
                'positive': [],
                'negative': [],
                'neutral': []
            }
    
    def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API"""
        try:
            response = openai.ChatCompletion.create(
                model=self.config['openai']['model'],
                messages=[
                    {"role": "system", "content": "You are a product research analyst. Provide accurate, objective analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config['openai']['temperature'],
                max_tokens=self.config['openai']['max_tokens']
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"⚠️ OpenAI API error: {e}")
            return "{}"