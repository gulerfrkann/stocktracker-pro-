"""
Playwright-based scraper for JavaScript-heavy sites
"""

import asyncio
import random
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Dict, List, Optional, Any
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, TimeoutError as PlaywrightTimeoutError
import structlog

from app.scraper.base import BaseScraper, ScrapedData, ScrapeRequest, ScrapingError, RetryableError, PermanentError
from app.core.config import settings

logger = structlog.get_logger()


class PlaywrightScraper(BaseScraper):
    """
    Advanced scraper using Playwright for JavaScript-heavy e-commerce sites
    """
    
    def __init__(self, name: str = "playwright_scraper"):
        super().__init__(name)
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.playwright = None
        
        # User agents for rotation
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15"
        ]
    
    async def initialize(self) -> None:
        """Initialize Playwright browser"""
        try:
            self.playwright = await async_playwright().start()
            
            # Launch browser with stealth settings
            self.browser = await self.playwright.chromium.launch(
                headless=settings.BROWSER_HEADLESS,
                args=[
                    '--no-sandbox',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor',
                    '--disable-dev-shm-usage',
                    '--no-first-run',
                    '--disable-extensions',
                    '--disable-plugins',
                    '--disable-images',  # Speed optimization
                ]
            )
            
            # Create browser context with random user agent
            self.context = await self.browser.new_context(
                user_agent=random.choice(self.user_agents),
                viewport={'width': 1920, 'height': 1080},
                locale='tr-TR',
                timezone_id='Europe/Istanbul',
                # Block unnecessary resources for speed
                bypass_csp=True,
            )
            
            # Block unnecessary resources
            await self.context.route("**/*.{png,jpg,jpeg,gif,svg,css,woff,woff2}", 
                                   lambda route: route.abort())
            
            self.logger.info("Playwright browser initialized")
            
        except Exception as e:
            self.logger.error("Failed to initialize Playwright", error=str(e))
            raise ScrapingError(f"Browser initialization failed: {str(e)}")
    
    async def cleanup(self) -> None:
        """Cleanup Playwright resources"""
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            
            self.logger.info("Playwright resources cleaned up")
            
        except Exception as e:
            self.logger.error("Error during cleanup", error=str(e))
    
    async def scrape(self, request: ScrapeRequest) -> ScrapedData:
        """
        Scrape a single URL using Playwright
        """
        start_time = datetime.utcnow()
        page = None
        
        try:
            # Create new page
            page = await self.context.new_page()
            
            # Set additional headers if provided
            if request.headers:
                await page.set_extra_http_headers(request.headers)
            
            # Navigate to page with timeout
            response = await page.goto(
                request.url,
                wait_until='domcontentloaded',
                timeout=request.timeout * 1000
            )
            
            # Wait for page to stabilize
            await page.wait_for_timeout(random.randint(1000, 3000))
            
            # Check if page loaded successfully
            if not response or response.status >= 400:
                raise RetryableError(
                    f"HTTP {response.status if response else 'unknown'} error",
                    url=request.url,
                    status_code=response.status if response else None
                )
            
            # Extract data using site-specific selectors
            scraped_data = await self._extract_product_data(page, request)
            
            # Calculate response time
            response_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            scraped_data.response_time_ms = response_time
            scraped_data.http_status_code = response.status
            
            return scraped_data
            
        except PlaywrightTimeoutError:
            raise RetryableError(f"Page load timeout", url=request.url)
            
        except Exception as e:
            self.logger.error(
                "Scraping failed",
                url=request.url,
                error=str(e),
                error_type=type(e).__name__
            )
            
            # Return error data
            return ScrapedData(
                url=request.url,
                timestamp=start_time,
                error_message=str(e),
                http_status_code=getattr(e, 'status_code', None)
            )
            
        finally:
            if page:
                await page.close()
    
    async def _extract_product_data(self, page: Page, request: ScrapeRequest) -> ScrapedData:
        """
        Extract product data from page using site configuration
        """
        site_config = request.site_config
        selectors = site_config.get('selectors', {})
        
        # Get page content for hash
        content = await page.content()
        
        # Initialize scraped data
        data = ScrapedData(
            url=request.url,
            timestamp=datetime.utcnow(),
            raw_html=content
        )
        
        try:
            # Extract page title
            data.page_title = await page.title()
            
            # Extract price
            price_selector = selectors.get('price')
            if price_selector:
                data.price = await self._extract_price(page, price_selector)
            
            # Extract stock status
            stock_selector = selectors.get('stock_status')
            availability_selector = selectors.get('availability_text')
            
            if stock_selector:
                data.is_in_stock = await self._extract_stock_status(page, stock_selector)
            
            if availability_selector:
                data.availability_text = await self._extract_text(page, availability_selector)
                
                # Try to determine stock from availability text if not already determined
                if data.is_in_stock is None and data.availability_text:
                    data.is_in_stock = self._parse_stock_from_text(data.availability_text)
            
            # Extract stock quantity
            quantity_selector = selectors.get('stock_quantity')
            if quantity_selector:
                data.stock_quantity = await self._extract_stock_quantity(page, quantity_selector)
            
            # Extract product name if available
            name_selector = selectors.get('product_name')
            if name_selector:
                data.product_name = await self._extract_text(page, name_selector)
            
            # Extract currency
            currency_selector = selectors.get('currency')
            if currency_selector:
                currency_text = await self._extract_text(page, currency_selector)
                if currency_text:
                    data.currency = self._parse_currency(currency_text)
            
        except Exception as e:
            self.logger.warning(
                "Data extraction error",
                url=request.url,
                error=str(e),
                selector_error=True
            )
            data.error_message = f"Data extraction error: {str(e)}"
        
        return data
    
    async def _extract_price(self, page: Page, selector: str) -> Optional[Decimal]:
        """Extract price from page"""
        try:
            # Try to get price element
            element = await page.query_selector(selector)
            if not element:
                return None
            
            # Get text content
            price_text = await element.inner_text()
            if not price_text:
                # Try attribute values
                for attr in ['data-price', 'value', 'content']:
                    price_text = await element.get_attribute(attr)
                    if price_text:
                        break
            
            if price_text:
                return self._parse_price(price_text)
            
        except Exception as e:
            self.logger.warning("Price extraction failed", selector=selector, error=str(e))
        
        return None
    
    async def _extract_stock_status(self, page: Page, selector: str) -> Optional[bool]:
        """Extract stock status from page"""
        try:
            element = await page.query_selector(selector)
            if not element:
                return None
            
            # Check various attributes and text content
            text = await element.inner_text()
            
            # Common stock indicators
            in_stock_indicators = ['stokta', 'mevcut', 'var', 'available', 'in stock']
            out_of_stock_indicators = ['stokta yok', 'tükendi', 'mevcut değil', 'out of stock', 'sold out']
            
            text_lower = text.lower()
            
            for indicator in out_of_stock_indicators:
                if indicator in text_lower:
                    return False
            
            for indicator in in_stock_indicators:
                if indicator in text_lower:
                    return True
            
            # Check CSS classes for common patterns
            class_name = await element.get_attribute('class')
            if class_name:
                class_lower = class_name.lower()
                if any(cls in class_lower for cls in ['out-of-stock', 'sold-out', 'unavailable']):
                    return False
                if any(cls in class_lower for cls in ['in-stock', 'available']):
                    return True
            
        except Exception as e:
            self.logger.warning("Stock status extraction failed", selector=selector, error=str(e))
        
        return None
    
    async def _extract_stock_quantity(self, page: Page, selector: str) -> Optional[int]:
        """Extract stock quantity from page"""
        try:
            element = await page.query_selector(selector)
            if not element:
                return None
            
            text = await element.inner_text()
            if not text:
                text = await element.get_attribute('value')
            
            if text:
                # Extract numbers from text
                import re
                numbers = re.findall(r'\d+', text)
                if numbers:
                    return int(numbers[0])
            
        except Exception as e:
            self.logger.warning("Stock quantity extraction failed", selector=selector, error=str(e))
        
        return None
    
    async def _extract_text(self, page: Page, selector: str) -> Optional[str]:
        """Extract text content from element"""
        try:
            element = await page.query_selector(selector)
            if element:
                text = await element.inner_text()
                return text.strip() if text else None
        except Exception:
            pass
        return None
    
    def _parse_price(self, price_text: str) -> Optional[Decimal]:
        """Parse price from text"""
        try:
            import re
            
            # Remove common price separators and currency symbols
            cleaned = re.sub(r'[^\d,.]', '', price_text)
            
            # Handle Turkish number format (1.234,56)
            if ',' in cleaned and '.' in cleaned:
                # Turkish format: 1.234,56
                if cleaned.rindex(',') > cleaned.rindex('.'):
                    cleaned = cleaned.replace('.', '').replace(',', '.')
                # US format: 1,234.56
                else:
                    cleaned = cleaned.replace(',', '')
            elif ',' in cleaned:
                # Could be either decimal separator or thousands separator
                parts = cleaned.split(',')
                if len(parts) == 2 and len(parts[1]) <= 2:
                    # Decimal separator
                    cleaned = cleaned.replace(',', '.')
                else:
                    # Thousands separator
                    cleaned = cleaned.replace(',', '')
            
            return Decimal(cleaned)
            
        except (InvalidOperation, ValueError) as e:
            self.logger.warning("Price parsing failed", price_text=price_text, error=str(e))
            return None
    
    def _parse_stock_from_text(self, text: str) -> Optional[bool]:
        """Parse stock status from availability text"""
        text_lower = text.lower()
        
        out_of_stock_patterns = [
            'stokta yok', 'tükendi', 'mevcut değil', 'kargo yok',
            'out of stock', 'sold out', 'unavailable', 'not available'
        ]
        
        in_stock_patterns = [
            'stokta', 'mevcut', 'hazır', 'kargo var',
            'in stock', 'available', 'ready'
        ]
        
        for pattern in out_of_stock_patterns:
            if pattern in text_lower:
                return False
        
        for pattern in in_stock_patterns:
            if pattern in text_lower:
                return True
        
        return None
    
    def _parse_currency(self, currency_text: str) -> str:
        """Parse currency from text"""
        currency_map = {
            '₺': 'TRY',
            'tl': 'TRY',
            'try': 'TRY',
            '$': 'USD',
            'usd': 'USD',
            '€': 'EUR',
            'eur': 'EUR',
            '£': 'GBP',
            'gbp': 'GBP'
        }
        
        text_lower = currency_text.lower().strip()
        return currency_map.get(text_lower, 'TRY')


# Register the scraper
from app.scraper.base import ScraperFactory
ScraperFactory.register_scraper('playwright', PlaywrightScraper)


