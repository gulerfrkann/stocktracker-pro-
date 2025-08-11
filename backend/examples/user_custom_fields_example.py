"""
Kullanıcı Özel Alan Sistemi Kullanım Örnekleri
"""

import asyncio
import httpx
from pprint import pprint


async def example_custom_field_workflow():
    """
    Kullanıcı özel alan sistemi tam workflow örneği
    """
    
    print("🎛️ KULLANICI ÖZEL ALAN SİSTEMİ ÖRNEĞİ")
    print("=" * 50)
    
    # 1. Kullanıcı özel alanları oluşturur
    print("\n1️⃣ Özel Alan Tanımları Oluşturma:")
    
    custom_fields = [
        {
            "field_name": "stok_kodu",
            "field_label": "Stok Kodu",
            "field_type": "text",
            "description": "Mağaza stok kodu",
            "is_required": True
        },
        {
            "field_name": "renk",
            "field_label": "Ürün Rengi",
            "field_type": "text",
            "description": "Ürün renk bilgisi"
        },
        {
            "field_name": "indirim_orani",
            "field_label": "İndirim Oranı",
            "field_type": "number",
            "description": "İndirim yüzdesi"
        },
        {
            "field_name": "kargo_ucreti",
            "field_label": "Kargo Ücreti",
            "field_type": "price",
            "description": "Kargo maliyeti"
        }
    ]
    
    field_ids = {}
    for field in custom_fields:
        response = await create_custom_field(field)
        field_ids[field['field_name']] = response['id']
        print(f"✅ {field['field_label']} oluşturuldu (ID: {response['id']})")
    
    # 2. Site için veri tercihleri ayarlar
    print("\n2️⃣ Site Veri Tercihleri:")
    
    site_id = 1  # Trendyol örneği
    
    preferences = {
        "site_id": site_id,
        # Standart alanlar
        "extract_price": True,
        "extract_stock_status": True,
        "extract_product_name": True,
        "extract_brand": True,         # AÇIK
        "extract_model": False,        # KAPALI  
        "extract_rating": True,        # AÇIK
        "extract_reviews": False,      # KAPALI
        # Özel alanlar (UUID'ler)
        "enabled_custom_fields": [
            field_ids["stok_kodu"],
            field_ids["renk"],
            field_ids["indirim_orani"]
            # kargo_ucreti dahil edilmedi
        ]
    }
    
    await set_user_preferences(preferences)
    print("✅ Kullanıcı tercihleri ayarlandı")
    
    # 3. Her özel alan için CSS selector'ları tanımlar
    print("\n3️⃣ CSS Selector Mappings:")
    
    mappings = [
        {
            "field_id": field_ids["stok_kodu"],
            "site_id": site_id,
            "css_selector": ".product-code, .sku, [data-sku]",
            "attribute": "text",
            "preprocessing_rules": {
                "trim": True,
                "uppercase": True
            }
        },
        {
            "field_id": field_ids["renk"],
            "site_id": site_id, 
            "css_selector": ".variant-color, .color-option.selected",
            "attribute": "text",
            "preprocessing_rules": {
                "trim": True,
                "title_case": True
            }
        },
        {
            "field_id": field_ids["indirim_orani"],
            "site_id": site_id,
            "css_selector": ".discount-rate, .sale-percent",
            "attribute": "text",
            "regex_pattern": r"(%?\d+)",
            "preprocessing_rules": {
                "numbers_only": True
            }
        }
    ]
    
    for mapping in mappings:
        await create_field_mapping(mapping)
        print(f"✅ {mapping['css_selector']} selector'ı eşlendi")
    
    # 4. Test scraping
    print("\n4️⃣ Test Scraping:")
    
    test_url = "https://www.trendyol.com/samsung/galaxy-s23-128gb-akilli-telefon-p-123456"
    
    # Önce mapping'leri test eder
    for mapping in mappings:
        test_result = await test_field_mapping({
            "url": test_url,
            "css_selector": mapping["css_selector"],
            "attribute": mapping["attribute"],
            "field_type": "text"
        })
        print(f"Test: {mapping['css_selector']} -> {test_result}")
    
    # 5. Gerçek scraping (user_id ile)
    print("\n5️⃣ Gerçek Scraping:")
    
    # Bu product scraping'te user_id geçildiğinde
    # sistem otomatik olarak kullanıcının tercihlerine göre
    # özel alanları da çeker
    
    print("Scraping başlatıldı... (user_id='test_user' ile)")
    print("Sistem şunları çekecek:")
    print("📦 Standart: Fiyat, Stok, İsim, Marka, Rating")
    print("🎨 Özel: Stok Kodu, Renk, İndirim Oranı")
    print("🚫 Çekmeyecek: Model, Reviews, Kargo Ücreti")


async def example_different_user_preferences():
    """
    Farklı kullanıcı tercihlerini gösteren örnek
    """
    
    print("\n" + "="*50)
    print("👥 FARKLI KULLANICI TERCİHLERİ ÖRNEĞİ")
    print("="*50)
    
    users = {
        "tedarik_muduru": {
            "extract_price": True,
            "extract_stock_status": True,
            "extract_stock_quantity": True,  # Adet önemli
            "extract_brand": True,
            "extract_model": True,           # Model önemli
            "custom_fields": ["stok_kodu", "kargo_ucreti"]  # Tedarik odaklı
        },
        
        "pazarlama_uzmani": {
            "extract_price": True,
            "extract_stock_status": False,   # Stok önemsiz
            "extract_rating": True,          # Rating önemli
            "extract_reviews": True,         # Yorumlar önemli
            "extract_brand": True,
            "custom_fields": ["renk", "indirim_orani"]  # Pazarlama odaklı
        },
        
        "muhasebe": {
            "extract_price": True,
            "extract_stock_status": False,
            "extract_brand": False,
            "extract_rating": False,
            "custom_fields": ["kargo_ucreti", "stok_kodu"]  # Maliyet odaklı
        }
    }
    
    for user_type, prefs in users.items():
        print(f"\n👤 {user_type.upper()}:")
        enabled_standard = [k for k, v in prefs.items() if k.startswith('extract_') and v]
        print(f"   📊 Standart alanlar: {', '.join(enabled_standard)}")
        print(f"   🎛️ Özel alanlar: {', '.join(prefs['custom_fields'])}")


def print_api_usage_examples():
    """
    API kullanım örnekleri
    """
    
    print("\n" + "="*60)
    print("🔧 API KULLANIM ÖRNEKLERİ")
    print("="*60)
    
    examples = {
        "1. Özel Alan Oluşturma": """
POST /api/v1/user-preferences/custom-fields
{
  "field_name": "stok_kodu",
  "field_label": "Stok Kodu", 
  "field_type": "text",
  "description": "Mağaza stok kodu",
  "is_required": true
}""",
        
        "2. Hazır Template'leri Görme": """
GET /api/v1/user-preferences/field-templates
# Döner: stok_kodu, renk, beden, marka, model, indirim_orani, kargo_ucreti""",
        
        "3. Site Tercihleri Ayarlama": """
POST /api/v1/user-preferences/site-preferences  
{
  "site_id": 1,
  "extract_price": true,
  "extract_stock_status": true,
  "extract_brand": false,     // KAPALI
  "extract_rating": true,     // AÇIK
  "enabled_custom_fields": ["field-uuid-1", "field-uuid-2"]
}""",
        
        "4. CSS Selector Mapping": """
POST /api/v1/user-preferences/field-mappings
{
  "field_id": 123,
  "site_id": 1,
  "css_selector": ".product-sku, [data-sku]",
  "attribute": "text",
  "regex_pattern": "SKU: (\\w+)",
  "preprocessing_rules": {
    "trim": true,
    "uppercase": true,
    "remove_chars": ["-", "_"]
  }
}""",
        
        "5. Mapping Test Etme": """
POST /api/v1/user-preferences/test-field-mapping
{
  "url": "https://example.com/product/123",
  "css_selector": ".product-sku",
  "attribute": "text",
  "field_type": "text"
}""",
        
        "6. İstatistikleri Görme": """
GET /api/v1/user-preferences/extraction-stats/1?days=7
# Döner: başarı oranları, alan bazlı istatistikler"""
    }
    
    for title, example in examples.items():
        print(f"\n{title}:")
        print(example)


# API helper functions
async def create_custom_field(field_data):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/user-preferences/custom-fields",
            json=field_data
        )
        return response.json()


async def set_user_preferences(prefs_data):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/user-preferences/site-preferences",
            json=prefs_data
        )
        return response.json()


async def create_field_mapping(mapping_data):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/user-preferences/field-mappings",
            json=mapping_data
        )
        return response.json()


async def test_field_mapping(test_data):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/user-preferences/test-field-mapping",
            json=test_data
        )
        return response.json()


if __name__ == "__main__":
    print_api_usage_examples()
    example_different_user_preferences()
    
    # Test için çalıştır (backend çalışıyor olmalı)
    # asyncio.run(example_custom_field_workflow())


