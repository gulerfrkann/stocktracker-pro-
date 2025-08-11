"""
Amazon.com.tr parser configuration
"""

from app.scraper.parsers.base_parser import BaseSiteParser, SiteConfig, SiteParserRegistry


class AmazonTRParser(BaseSiteParser):
    """
    Parser for Amazon.com.tr - Amazon Turkey
    """
    
    def get_config(self) -> SiteConfig:
        return SiteConfig(
            name="Amazon TR",
            domain="amazon.com.tr",
            use_javascript=True,
            requires_proxy=True,  # Amazon has strong anti-bot protection
            request_delay=3.0,  # Longer delay for Amazon
            selectors={
                'price': '.a-price-whole, .a-offscreen, [data-testid="price"] .a-price-whole',
                'currency': '.a-price-symbol, .a-price .a-price-symbol',
                'stock_status': '#availability span, .a-size-medium.a-color-success, .a-size-medium.a-color-price',
                'availability_text': '#availability span, .availability-info',
                'product_name': '#productTitle, .product-title',
                'stock_quantity': '#quantity option, .quantity-selector option',
                'discount_price': '.a-price.a-text-price.a-size-medium.a-color-base .a-offscreen',
                'original_price': '.a-price.a-text-price .a-offscreen',
                'rating': '.a-icon-alt, .a-star-mini .a-icon-alt',
                'review_count': '#acrCustomerReviewText, .review-count'
            },
            headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Upgrade-Insecure-Requests': '1',
                'Referer': 'https://www.amazon.com.tr/'
            },
            custom_logic={
                'wait_for_element': '.a-price-whole, #availability',
                'handle_captcha': True,
                'rotate_user_agents': True,
                'wait_time': 3000,
                'scroll_page': True
            }
        )


# Register parser
SiteParserRegistry.register("amazon.com.tr", AmazonTRParser())


