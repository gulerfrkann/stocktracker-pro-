StockTracker Pro 

E-ticaret Stok & Fiyat Takip Sistemi**

[![GitHub stars](https://img.shields.io/github/stars/KULLANICI_ADIN/stocktracker-pro?style=social)](https://github.com/KULLANICI_ADIN/stocktracker-pro)
[![GitHub forks](https://img.shields.io/github/forks/KULLANICI_ADIN/stocktracker-pro?style=social)](https://github.com/KULLANICI_ADIN/stocktracker-pro)
[![GitHub issues](https://img.shields.io/github/issues/KULLANICI_ADIN/stocktracker-pro)](https://github.com/KULLANICI_ADIN/stocktracker-pro/issues)
[![GitHub license](https://img.shields.io/github/license/KULLANICI_ADIN/stocktracker-pro)](https://github.com/KULLANICI_ADIN/stocktracker-pro/blob/main/LICENSE)

 Proje Özeti

StockTracker Pro, e-ticaret sitelerinden ürün stok durumu ve fiyat bilgilerini otomatik olarak takip eden, değişikliklerde uyarı gönderen ve raporlama yapan web tabanlı bir sistemdir.

##  Temel Özellikler

 MVP (v1.0)
-  **Otomatik Web Scraping**: Playwright ile JavaScript-heavy siteler dahil
-  **Zamanlanmış Tarama**: Esnek cron-benzeri planlama (15dk-günlük)
-  **Gerçek Zamanlı Dashboard**: Ürün durumu, fiyat değişimleri
-  **Akıllı Uyarılar**: Email/Slack - stok bitimi, fiyat değişimleri
-  **Excel/CSV Export**: Özelleştirilebilir raporlar
-  **Çoklu Kullanıcı**: Rol tabanlı erişim (Admin/Operatör/Görüntüleyici)
-  **Proxy Desteği**: IP rotasyonu ve bot koruması

Gelecek Sürümler (v1.1+)
-  **Gelişmiş Analitik**: Grafik ve trend analizi
-  **API Entegrasyonları**: ERP/WMS bağlantıları
-  **Çoklu Para Birimi**: KDV/kur hesaplamaları
-  **Mobil Bildirimler**: Push/SMS/WhatsApp

 Teknik Stack

- Backend**: Python + FastAPI + PostgreSQL
- Scraping**: Playwright + httpx + BeautifulSoup
- Queue/Scheduling**: Celery + Redis
- Frontend**: React + TypeScript + Tailwind CSS
- Deployment**: Docker + Docker Compose

  Proje Yapısı

```
stocktracker-pro/
├── backend/                 # Python FastAPI Backend
│   ├── app/
│   │   ├── core/           # Konfigürasyon, güvenlik
│   │   ├── models/         # SQLAlchemy modelleri
│   │   ├── api/            # REST API endpoints
│   │   ├── services/       # İş mantığı katmanı
│   │   ├── scraper/        # Scraping motorları
│   │   ├── notifications/  # Email/Slack uyarıları
│   │   └── utils/          # Yardımcı fonksiyonlar
│   ├── migrations/         # Alembic DB migrations
│   └── tests/              # Backend testleri
├── frontend/               # React SPA
│   ├── src/
│   │   ├── components/     # Yeniden kullanılabilir bileşenler
│   │   ├── pages/          # Sayfa bileşenleri
│   │   ├── hooks/          # Custom React hooks
│   │   ├── services/       # API çağrıları
│   │   └── utils/          # Frontend yardımcıları
│   └── public/
├── docker/                 # Docker konfigürasyonları
├── docs/                   # API dokümantasyonu
└── scripts/               # Deploy ve maintenance scriptleri
```

 Hızlı Başlangıç

 Gereksinimler
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (önerilen)

 Kurulum

 1. Repository'yi klonla
```bash
git clone https://github.com/KULLANICI_ADIN/stocktracker-pro.git
cd stocktracker-pro
```

#### 2. Docker ile çalıştır (Önerilen)
```bash
# Tüm servisleri başlat
docker-compose up -d

# Servisleri kontrol et
docker-compose ps

# Logları görüntüle
docker-compose logs -f
```

 3. Manuel kurulum
```bash
# Backend kurulumu
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend kurulumu
cd ../frontend
npm install
npm run dev
```

 Erişim URL'leri
- Frontend**: http://localhost:3000
- Backend API**: http://localhost:8000
- API Dokümantasyonu**: http://localhost:8000/docs
- Adminer (Database)**: http://localhost:8080

 API Dokümantasyonu

Backend çalıştıktan sonra: `http://localhost:8000/docs`

 Konfigürasyon

Ana konfigürasyon dosyaları:
- `backend/app/core/config.py` - Backend ayarları
- `docker-compose.yml` - Container ayarları
- `frontend/.env` - Frontend environment

### Environment Variables
```bash
# Backend (.env)
DATABASE_URL=postgresql://user:pass@localhost:5432/stocktracker
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-here

# Frontend (.env)
REACT_APP_API_URL=http://localhost:8000/api/v1
```

## 🛒 Desteklenen E-ticaret Platformları

- **Trendyol** - API entegrasyonu + Web scraping
- **Hepsiburada** - API entegrasyonu + Web scraping  
- **N11** - API entegrasyonu + Web scraping
- **Pazarama** - API entegrasyonu
- **EpttAVM** - API entegrasyonu
- **ÇiçekSepeti** - API entegrasyonu
- **Idefix** - API entegrasyonu

## 📊 Özellikler

### Web Scraping
- **Playwright** ile JavaScript-heavy siteler
- **HTTP Scraper** ile basit siteler
- **Proxy rotasyonu** desteği
- **Rate limiting** ve bot koruması
- **Otomatik retry** mekanizması

### Sipariş Takibi
- **Gerçek zamanlı** sipariş bildirimleri
- **Webhook** entegrasyonu
- **Sipariş geçmişi** ve analitik
- **Otomatik senkronizasyon**

### Uyarı Sistemi
- **Email** bildirimleri
- **Slack** entegrasyonu
- **Webhook** bildirimleri
- **Özelleştirilebilir** uyarı kuralları

##  Katkıda Bulunma

1. Fork et
2. Feature branch oluştur (`git checkout -b feature/amazing-feature`)
3. Commit yap (`git commit -m 'Add amazing feature'`)
4. Push et (`git push origin feature/amazing-feature`)
5. Pull Request oluştur

### Geliştirme Kurulumu
```bash
# Development dependencies
cd backend && pip install -r requirements-dev.txt
cd ../frontend && npm install

# Pre-commit hooks
pre-commit install

# Tests
cd backend && pytest
cd ../frontend && npm test
```

## Lisans

MIT License - Detaylar için `LICENSE` dosyasına bakınız.

## İletişim

- **GitHub Issues**: [Proje Issues](https://github.com/KULLANICI_ADIN/stocktracker-pro/issues)
- **Email**: [İletişim Bilgisi]

##  Teşekkürler

Bu proje aşağıdaki açık kaynak projeleri kullanmaktadır:
- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://reactjs.org/)
- [Playwright](https://playwright.dev/)
- [Tailwind CSS](https://tailwindcss.com/)

---

**StockTracker Pro** - E-ticaret operasyonlarınızı optimize edin! 

[⬆ Back to top](#stocktracker-pro-)



