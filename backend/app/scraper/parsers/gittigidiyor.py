"""
GittiGidiyor.com parser configuration
"""

from app.scraper.parsers.base_parser import BaseSiteParser, SiteConfig, SiteParserRegistry


class GittiGidiyorParser(BaseSiteParser):
    """
    Parser for GittiGidiyor.com - eBay Turkey
    """
    
    def get_config(self) -> SiteConfig:
        return SiteConfig(
            name="GittiGidiyor",
            domain="gittigidiyor.com",
            use_javascript=True,
            requires_proxy=False,
            request_delay=1.5,
            selectors={
                'price': '.product-price, .price-current',
                'currency': '.product-price, .price-current',
                'stock_status': '.stock-info, .availability',
                'availability_text': '.stock-status, .delivery-info',
                'product_name': '.product-title, h1.title',
                'stock_quantity': '.stock-count, .quantity-available',
                'rating': '.rating-score',
                'review_count': '.review-count'
            },
            headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'tr-TR,tr;q=0.9,en;q=0.8'
            }
        )


# Register parser
SiteParserRegistry.register("gittigidiyor.com", GittiGidiyorParser())


