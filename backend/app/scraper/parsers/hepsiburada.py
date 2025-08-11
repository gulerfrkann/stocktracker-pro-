"""
Hepsiburada.com parser configuration
"""

from app.scraper.parsers.base_parser import BaseSiteParser, SiteConfig, SiteParserRegistry


class HepsiburadaParser(BaseSiteParser):
    """
    Parser for Hepsiburada.com - Major Turkish e-commerce platform
    """
    
    def get_config(self) -> SiteConfig:
        return SiteConfig(
            name="Hepsiburada",
            domain="hepsiburada.com",
            use_javascript=True,
            requires_proxy=False,
            request_delay=1.0,
            selectors={
                'price': '[data-test-id="price-current-price"], .price-value, .notranslate',
                'currency': '[data-test-id="price-current-price"], .price-value',
                'stock_status': '[data-test-id="shipping-info"], .stock-info, .delivery-info',
                'availability_text': '[data-test-id="shipping-info"] span, .stock-status-text',
                'product_name': '[data-test-id="product-name"], h1.product-name',
                'stock_quantity': '.quantity-selector option, .variant-item',
                'discount_price': '[data-test-id="price-current-price"]',
                'original_price': '[data-test-id="price-old-price"]',
                'rating': '.rating-score, .average-rating',
                'review_count': '.rating-count, .review-count'
            },
            headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'tr-TR,tr;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Referer': 'https://www.hepsiburada.com/',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate'
            },
            custom_logic={
                'wait_for_element': '[data-test-id="price-current-price"]',
                'block_ads': True,
                'wait_time': 1500
            }
        )


# Register parser
SiteParserRegistry.register("hepsiburada.com", HepsiburadaParser())


