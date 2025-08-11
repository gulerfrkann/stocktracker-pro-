"""
Generic parser for unknown e-commerce sites
"""

from typing import Dict, Any, List
from app.scraper.parsers.base_parser import BaseSiteParser, SiteConfig


class GenericEcommerceParser(BaseSiteParser):
    """
    Generic parser that can be configured for any e-commerce site
    """
    
    def __init__(self, site_config: Dict[str, Any]):
        self.custom_config = site_config
        super().__init__()
    
    def get_config(self) -> SiteConfig:
        # Default selectors that work for many sites
        default_selectors = {
            # Common price selectors
            'price': '.price, .product-price, .current-price, .sale-price, [class*="price"], [data-price]',
            
            # Common currency selectors  
            'currency': '.price, .product-price, .currency',
            
            # Common stock selectors
            'stock_status': '.stock, .availability, .in-stock, .out-of-stock, [class*="stock"]',
            'availability_text': '.stock-text, .availability-text, .stock-message',
            
            # Common product info selectors
            'product_name': 'h1, .product-title, .product-name, [class*="title"], [class*="name"]',
            'stock_quantity': '.quantity, .stock-count, [class*="quantity"]',
            
            # Common discount selectors
            'discount_price': '.sale-price, .discounted-price, .special-price',
            'original_price': '.original-price, .regular-price, .was-price',
            
            # Reviews and ratings
            'rating': '.rating, .stars, .score, [class*="rating"]',
            'review_count': '.review-count, .reviews, [class*="review"]'
        }
        
        # Merge with custom selectors
        selectors = {**default_selectors, **self.custom_config.get('selectors', {})}
        
        return SiteConfig(
            name=self.custom_config.get('name', 'Generic E-commerce'),
            domain=self.custom_config['domain'],
            use_javascript=self.custom_config.get('use_javascript', True),  # Default to JS for safety
            requires_proxy=self.custom_config.get('requires_proxy', False),
            request_delay=self.custom_config.get('request_delay', 2.0),  # Conservative default
            selectors=selectors,
            headers=self.custom_config.get('headers', {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'tr-TR,tr;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br'
            }),
            custom_logic=self.custom_config.get('custom_logic', {
                'wait_time': 3000,
                'scroll_to_load': False,
                'handle_popup': True
            })
        )


class SiteWizard:
    """
    Wizard to help create configurations for new sites
    """
    
    @staticmethod
    def create_config_from_url(url: str, manual_selectors: Dict[str, str] = None) -> Dict[str, Any]:
        """
        Create a basic configuration from URL analysis
        """
        from urllib.parse import urlparse
        
        parsed = urlparse(url)
        domain = parsed.netloc.replace('www.', '')
        
        # Determine if JavaScript is likely needed based on domain patterns
        js_domains = ['react', 'vue', 'angular', 'spa', 'app']
        likely_needs_js = any(term in domain.lower() for term in js_domains)
        
        config = {
            'name': domain.split('.')[0].title(),
            'domain': domain,
            'use_javascript': likely_needs_js,
            'requires_proxy': False,
            'request_delay': 2.0,
            'selectors': manual_selectors or {},
            'headers': {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'tr-TR,tr;q=0.9,en;q=0.8',
                'Referer': f'https://{domain}/'
            }
        }
        
        return config
    
    @staticmethod
    def suggest_selectors(html_content: str) -> Dict[str, List[str]]:
        """
        Analyze HTML and suggest possible selectors
        """
        from bs4 import BeautifulSoup
        import re
        
        soup = BeautifulSoup(html_content, 'html.parser')
        suggestions = {
            'price': [],
            'stock_status': [],
            'product_name': [],
            'availability_text': []
        }
        
        # Price selectors - look for elements with price-related classes or text patterns
        price_patterns = [
            r'price', r'fiyat', r'tutar', r'amount', r'cost', r'₺', r'tl', r'try'
        ]
        
        for element in soup.find_all(attrs={'class': True}):
            classes = ' '.join(element.get('class', []))
            
            # Check for price indicators
            if any(re.search(pattern, classes, re.I) for pattern in price_patterns):
                selector = f".{' '.join(element.get('class', []))}"
                if selector not in suggestions['price']:
                    suggestions['price'].append(selector)
        
        # Stock selectors
        stock_patterns = [
            r'stock', r'stok', r'availability', r'mevcut', r'var', r'yok', r'available'
        ]
        
        for element in soup.find_all(attrs={'class': True}):
            classes = ' '.join(element.get('class', []))
            
            if any(re.search(pattern, classes, re.I) for pattern in stock_patterns):
                selector = f".{' '.join(element.get('class', []))}"
                if selector not in suggestions['stock_status']:
                    suggestions['stock_status'].append(selector)
        
        # Product name - usually h1, h2 or elements with "title", "name" in class
        name_patterns = [r'title', r'name', r'product', r'ürün', r'başlık']
        
        # Check h1, h2 first
        for tag in ['h1', 'h2', 'h3']:
            elements = soup.find_all(tag)
            if elements:
                suggestions['product_name'].append(tag)
        
        # Check class-based selectors
        for element in soup.find_all(attrs={'class': True}):
            classes = ' '.join(element.get('class', []))
            
            if any(re.search(pattern, classes, re.I) for pattern in name_patterns):
                selector = f".{' '.join(element.get('class', []))}"
                if selector not in suggestions['product_name']:
                    suggestions['product_name'].append(selector)
        
        # Limit suggestions to top 5 per category
        for key in suggestions:
            suggestions[key] = suggestions[key][:5]
        
        return suggestions


def create_dynamic_parser(domain: str, config: Dict[str, Any]) -> GenericEcommerceParser:
    """
    Factory function to create a parser for any domain
    """
    config['domain'] = domain
    return GenericEcommerceParser(config)


