"""
N11.com parser configuration
"""

from app.scraper.parsers.base_parser import BaseSiteParser, SiteConfig, SiteParserRegistry


class N11Parser(BaseSiteParser):
    """
    Parser for N11.com - Turkish e-commerce platform
    """
    
    def get_config(self) -> SiteConfig:
        return SiteConfig(
            name="N11",
            domain="n11.com",
            use_javascript=False,  # Mostly server-side rendered
            requires_proxy=False,
            request_delay=1.0,
            selectors={
                'price': '.newPrice, .priceContainer .price, .current-price',
                'currency': '.newPrice, .priceContainer .price',
                'stock_status': '.stockStatus, .availability-info',
                'availability_text': '.stockStatus span, .availability-text',
                'product_name': '.proName, .product-name h1',
                'stock_quantity': '.quantity-selector option',
                'discount_price': '.newPrice',
                'original_price': '.oldPrice, .old-price',
                'rating': '.ratingScore, .rating-value',
                'review_count': '.ratingCount, .review-count'
            },
            headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'tr-TR,tr;q=0.9,en;q=0.8',
                'Cache-Control': 'max-age=0',
                'Connection': 'keep-alive'
            }
        )


# Register parser
SiteParserRegistry.register("n11.com", N11Parser())


