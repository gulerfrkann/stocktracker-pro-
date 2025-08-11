"""
VatanBilgisayar.com parser configuration
"""

from app.scraper.parsers.base_parser import BaseSiteParser, SiteConfig, SiteParserRegistry


class VatanBilgisayarParser(BaseSiteParser):
    """
    Parser for VatanBilgisayar.com - Technology e-commerce
    """
    
    def get_config(self) -> SiteConfig:
        return SiteConfig(
            name="Vatan Bilgisayar",
            domain="vatanbilgisayar.com",
            use_javascript=True,  # Modern site
            requires_proxy=False,
            request_delay=1.5,
            selectors={
                # Ana fiyat selektörleri
                'price': '.product-list__price, .price-current, .product-price-not-discounted',
                'currency': '.product-list__price, .price-current',
                
                # Stok durumu
                'stock_status': '.product-stock-status, .stock-info, .availability',
                'availability_text': '.product-stock-text, .stock-message',
                
                # Ürün bilgileri
                'product_name': '.product-list__product-name, .product-name h1',
                'stock_quantity': '.stock-quantity, .available-stock',
                
                # İndirim ve kampanya
                'discount_price': '.product-list__price--discounted, .discounted-price',
                'original_price': '.product-list__price--not-discounted, .original-price',
                'discount_rate': '.discount-rate, .discount-percentage',
                
                # Ek bilgiler
                'brand': '.product-brand, .brand-name',
                'model': '.product-model, .model-name',
                'rating': '.rating-score, .product-rating',
                'review_count': '.review-count, .comment-count'
            },
            headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'tr-TR,tr;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Cache-Control': 'no-cache',
                'Referer': 'https://www.vatanbilgisayar.com/',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate'
            },
            custom_logic={
                'wait_for_element': '.product-list__price, .stock-info',
                'scroll_to_load': False,
                'wait_time': 2000,
                'handle_popup': True,  # Site popup'ları varsa
                'accept_cookies': True,  # KVKK popup'ı için
                'block_ads': True
            }
        )


# Register parser
SiteParserRegistry.register("vatanbilgisayar.com", VatanBilgisayarParser())


