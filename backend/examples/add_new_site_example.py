"""
Yeni E-ticaret Sitesi Ekleme Örnekleri
"""

import asyncio
import httpx
from pprint import pprint


async def example_add_new_site():
    """
    Yeni bir e-ticaret sitesi ekleme örneği
    """
    
    # 1. Önce siteyi analiz et
    analysis_response = await analyze_site("https://www.example-eticaret.com/urun/laptop-123")
    
    # 2. Önerilen konfigürasyonu düzenle
    config = analysis_response['suggested_config']
    config['selectors'] = {
        'price': '.product-price, .price-current',
        'currency': '.price-currency, .currency',
        'stock_status': '.stock-info, .availability',
        'availability_text': '.stock-message',
        'product_name': 'h1.product-title, .product-name'
    }
    
    # 3. Konfigürasyonu test et
    test_response = await test_configuration(
        domain="example-eticaret.com",
        test_url="https://www.example-eticaret.com/urun/laptop-123",
        config=config
    )
    
    if test_response['test_successful']:
        # 4. Site'ı sisteme ekle
        create_response = await create_site(config)
        print(f"Site başarıyla eklendi: {create_response}")
    else:
        print("Test başarısız, konfigürasyon düzeltilmeli:")
        pprint(test_response['issues'])


async def analyze_site(url: str):
    """Site analizi"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/site-wizard/analyze-site",
            json={"url": url}
        )
        return response.json()


async def test_configuration(domain: str, test_url: str, config: dict):
    """Konfigürasyon testi"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/site-wizard/test-configuration",
            json={
                "domain": domain,
                "test_url": test_url,
                "config": config
            }
        )
        return response.json()


async def create_site(config: dict):
    """Site oluşturma"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/site-wizard/create-site",
            json=config
        )
        return response.json()


# Manuel site ekleme örneği
MANUAL_SITE_EXAMPLES = {
    "teknosa": {
        "name": "Teknosa",
        "domain": "teknosa.com",
        "use_javascript": True,
        "requires_proxy": False,
        "request_delay": 1.5,
        "selectors": {
            "price": ".prc, .product-price, .current-price",
            "currency": ".prc, .product-price",
            "stock_status": ".stck-info, .stock-status",
            "availability_text": ".delivery-info, .stock-message",
            "product_name": ".product-name h1, .prd-title",
            "discount_price": ".sale-price, .discounted-price",
            "original_price": ".old-price, .regular-price"
        },
        "headers": {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.8",
            "Referer": "https://www.teknosa.com/"
        }
    },
    
    "mediamarkt": {
        "name": "MediaMarkt",
        "domain": "mediamarkt.com.tr",
        "use_javascript": True,
        "requires_proxy": False,
        "request_delay": 2.0,
        "selectors": {
            "price": ".price, .product-price-value",
            "currency": ".price-currency, .currency-symbol",
            "stock_status": ".availability, .stock-info",
            "availability_text": ".availability-text",
            "product_name": "h1.product-title, .product-name"
        }
    },
    
    "ciceksepeti": {
        "name": "ÇiçekSepeti",
        "domain": "ciceksepeti.com",
        "use_javascript": True,
        "requires_proxy": False,
        "request_delay": 1.0,
        "selectors": {
            "price": ".price-current, .product-price",
            "currency": ".price-currency",
            "stock_status": ".stock-status, .availability",
            "product_name": ".product-title h1"
        }
    }
}


def print_usage_examples():
    """
    Kullanım örnekleri
    """
    print("""
🔧 YENİ E-TİCARET SİTESİ EKLEME REHBERİ

1️⃣ OTOMATİK ANALİZ (Önerilen):
   POST /api/v1/site-wizard/analyze-site
   {
     "url": "https://example-shop.com/product/123"
   }

2️⃣ KONFIGÜRASYON TESTİ:
   POST /api/v1/site-wizard/test-configuration
   {
     "domain": "example-shop.com",
     "test_url": "https://example-shop.com/product/123",
     "config": { ... }
   }

3️⃣ SİTE OLUŞTURMA:
   POST /api/v1/site-wizard/create-site
   {
     "name": "Example Shop",
     "domain": "example-shop.com",
     "selectors": { ... }
   }

4️⃣ DESTEKLENEN SİTELER LİSTESİ:
   GET /api/v1/site-wizard/supported-sites

🎯 CSS SELECTOR ÖRNEKLERİ:

Fiyat için:
- .price, .product-price, .current-price
- [data-price], [data-cost]
- .prc, .amount, .tutar

Stok için:
- .stock, .availability, .in-stock
- .stok, .mevcut, .var
- [data-stock], [data-availability]

Ürün adı için:
- h1, h2, .product-title, .product-name
- .prd-title, .item-name

⚡ HIZLI EKLEME:
Sistem otomatik olarak:
- CSS selector'ları önerir
- JavaScript gereksinimini tespit eder
- Proxy ihtiyacını belirler
- Test scraping yapar
    """)


if __name__ == "__main__":
    print_usage_examples()
    
    # Test için çalıştır (backend çalışıyor olmalı)
    # asyncio.run(example_add_new_site())


