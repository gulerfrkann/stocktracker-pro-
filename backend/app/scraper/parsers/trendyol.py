"""
Trendyol.com parser configuration
"""

from app.scraper.parsers.base_parser import BaseSiteParser, SiteConfig, SiteParserRegistry


class TrendyolParser(BaseSiteParser):
    """
    Parser for Trendyol.com - Turkey's largest e-commerce platform
    """
    
    def get_config(self) -> SiteConfig:
        return SiteConfig(
            name="Trendyol",
            domain="trendyol.com",
            use_javascript=True,  # React-based site
            requires_proxy=False,  # Generally allows scraping
            request_delay=1.5,
            selectors={
                'price': '.prc-dsc, .prc-org, [data-testid="price-current-price"]',
                'currency': '.prc-dsc, .prc-org',
                'stock_status': '.pr-in-sz, [data-testid="product-variants"], .pr-in-stck',
                'availability_text': '.pr-in-sz-tx, .shipping-benefits, .cargo-message',
                'product_name': '.pr-new-br, h1[data-testid="product-name"]',
                'stock_quantity': 'select[data-testid="size-selector"] option, .pr-in-sz option',
                'discount_price': '.prc-dsc',
                'original_price': '.prc-org',
                'rating': '.rating-score',
                'review_count': '.rw-cnt'
            },
            headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'tr-TR,tr;q=0.9,en;q=0.8',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1'
            },
            custom_logic={
                'wait_for_element': '.prc-dsc, .prc-org',
                'scroll_to_load': True,
                'wait_time': 2000  # Wait 2 seconds for dynamic content
            }
        )


class TrendyolGoParser(BaseSiteParser):
    """
    Parser for TrendyolGo (grocery delivery)
    """
    
    def get_config(self) -> SiteConfig:
        return SiteConfig(
            name="TrendyolGo",
            domain="trendyolgo.com",
            use_javascript=True,
            requires_proxy=False,
            request_delay=2.0,
            selectors={
                'price': '.item-price, .price-current',
                'currency': '.item-price',
                'stock_status': '.stock-status, .availability',
                'availability_text': '.stock-info, .delivery-info',
                'product_name': '.item-name, .product-title',
                'stock_quantity': '.quantity-selector option'
            }
        )


# Register parsers
SiteParserRegistry.register("trendyol.com", TrendyolParser())
SiteParserRegistry.register("trendyolgo.com", TrendyolGoParser())


