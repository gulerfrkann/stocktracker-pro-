"""
HTTP-based scraper for simple, fast scraping without JavaScript
"""

import asyncio
import random
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Dict, List, Optional, Any
import httpx
from bs4 import BeautifulSoup
from selectolax.parser import HTMLParser
import structlog

from app.scraper.base import BaseScraper, ScrapedData, ScrapeRequest, ScrapingError, RetryableError, PermanentError
from app.core.config import settings

logger = structlog.get_logger()


class HttpScraper(BaseScraper):
    """
    Fast HTTP-based scraper for simple sites without JavaScript
    """
    
    def __init__(self, name: str = "http_scraper"):
        super().__init__(name)
        self.client: Optional[httpx.AsyncClient] = None
        
        # User agents for rotation
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
    
    async def initialize(self) -> None:
        """Initialize HTTP client"""
        try:
            # Create HTTP client with realistic browser headers
            self.client = httpx.AsyncClient(
                timeout=httpx.Timeout(settings.REQUEST_TIMEOUT),
                limits=httpx.Limits(max_connections=settings.MAX_CONCURRENT_SCRAPERS),
                headers={
                    'User-Agent': random.choice(self.user_agents),
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'tr-TR,tr;q=0.9,en;q=0.8',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                },
                follow_redirects=True
            )
            
            self.logger.info("HTTP client initialized")
            
        except Exception as e:
            self.logger.error("Failed to initialize HTTP client", error=str(e))
            raise ScrapingError(f"HTTP client initialization failed: {str(e)}")
    
    async def cleanup(self) -> None:
        """Cleanup HTTP client"""
        try:
            if self.client:
                await self.client.aclose()
            
            self.logger.info("HTTP client cleaned up")
            
        except Exception as e:
            self.logger.error("Error during cleanup", error=str(e))
    
    async def scrape(self, request: ScrapeRequest) -> ScrapedData:
        """
        Scrape a single URL using HTTP client
        """
        start_time = datetime.utcnow()
        
        try:
            # Prepare headers
            headers = {}
            if request.headers:
                headers.update(request.headers)
            
            # Add random user agent if not specified
            if 'User-Agent' not in headers:
                headers['User-Agent'] = random.choice(self.user_agents)
            
            # Make HTTP request
            response = await self.client.get(
                request.url,
                headers=headers,
                timeout=request.timeout
            )
            
            # Check response status
            if response.status_code >= 400:
                if response.status_code in [404, 410]:
                    raise PermanentError(
                        f"HTTP {response.status_code} - Page not found",
                        url=request.url,
                        status_code=response.status_code
                    )
                else:
                    raise RetryableError(
                        f"HTTP {response.status_code} error",
                        url=request.url,
                        status_code=response.status_code
                    )
            
            # Extract data from HTML
            scraped_data = await self._extract_product_data(response.text, request)
            
            # Calculate response time
            response_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            scraped_data.response_time_ms = response_time
            scraped_data.http_status_code = response.status_code
            
            return scraped_data
            
        except httpx.TimeoutException:
            raise RetryableError(f"Request timeout", url=request.url)
            
        except httpx.ConnectError:
            raise RetryableError(f"Connection error", url=request.url)
            
        except Exception as e:
            self.logger.error(
                "HTTP scraping failed",
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
    
    async def _extract_product_data(self, html_content: str, request: ScrapeRequest) -> ScrapedData:
        """
        Extract product data from HTML using site configuration
        """
        site_config = request.site_config
        selectors = site_config.get('selectors', {})
        
        # Initialize scraped data
        data = ScrapedData(
            url=request.url,
            timestamp=datetime.utcnow(),
            raw_html=html_content
        )
        
        try:
            # Parse HTML - use selectolax for speed, fallback to BeautifulSoup for complex selectors
            use_selectolax = site_config.get('use_selectolax', True)
            
            if use_selectolax:
                parser = HTMLParser(html_content)
                soup = None
            else:
                parser = None
                soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract page title
            if parser:
                title_elem = parser.css_first('title')
                data.page_title = title_elem.text() if title_elem else None
            else:
                title_elem = soup.find('title')
                data.page_title = title_elem.get_text().strip() if title_elem else None
            
            # Extract price
            price_selector = selectors.get('price')
            if price_selector:
                data.price = self._extract_price(parser, soup, price_selector)
            
            # Extract stock status
            stock_selector = selectors.get('stock_status')
            availability_selector = selectors.get('availability_text')
            
            if stock_selector:
                data.is_in_stock = self._extract_stock_status(parser, soup, stock_selector)
            
            if availability_selector:
                data.availability_text = self._extract_text(parser, soup, availability_selector)
                
                # Try to determine stock from availability text if not already determined
                if data.is_in_stock is None and data.availability_text:
                    data.is_in_stock = self._parse_stock_from_text(data.availability_text)
            
            # Extract stock quantity
            quantity_selector = selectors.get('stock_quantity')
            if quantity_selector:
                data.stock_quantity = self._extract_stock_quantity(parser, soup, quantity_selector)
            
            # Extract product name if available
            name_selector = selectors.get('product_name')
            if name_selector:
                data.product_name = self._extract_text(parser, soup, name_selector)
            
            # Extract currency
            currency_selector = selectors.get('currency')
            if currency_selector:
                currency_text = self._extract_text(parser, soup, currency_selector)
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
    
    def _extract_price(self, parser, soup, selector: str) -> Optional[Decimal]:
        """Extract price from HTML"""
        try:
            text = None
            
            if parser:
                element = parser.css_first(selector)
                if element:
                    text = element.text()
                    # Try data attributes
                    if not text:
                        for attr in ['data-price', 'value', 'content']:
                            text = element.attributes.get(attr)
                            if text:
                                break
            else:
                element = soup.select_one(selector)
                if element:
                    text = element.get_text().strip()
                    # Try data attributes
                    if not text:
                        for attr in ['data-price', 'value', 'content']:
                            text = element.get(attr)
                            if text:
                                break
            
            if text:
                return self._parse_price(text)
            
        except Exception as e:
            self.logger.warning("Price extraction failed", selector=selector, error=str(e))
        
        return None
    
    def _extract_stock_status(self, parser, soup, selector: str) -> Optional[bool]:
        """Extract stock status from HTML"""
        try:
            text = None
            class_name = None
            
            if parser:
                element = parser.css_first(selector)
                if element:
                    text = element.text()
                    class_name = element.attributes.get('class', '')
            else:
                element = soup.select_one(selector)
                if element:
                    text = element.get_text().strip()
                    class_name = ' '.join(element.get('class', []))
            
            if text:
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
            if class_name:
                class_lower = class_name.lower()
                if any(cls in class_lower for cls in ['out-of-stock', 'sold-out', 'unavailable']):
                    return False
                if any(cls in class_lower for cls in ['in-stock', 'available']):
                    return True
            
        except Exception as e:
            self.logger.warning("Stock status extraction failed", selector=selector, error=str(e))
        
        return None
    
    def _extract_stock_quantity(self, parser, soup, selector: str) -> Optional[int]:
        """Extract stock quantity from HTML"""
        try:
            text = None
            
            if parser:
                element = parser.css_first(selector)
                if element:
                    text = element.text() or element.attributes.get('value')
            else:
                element = soup.select_one(selector)
                if element:
                    text = element.get_text().strip() or element.get('value')
            
            if text:
                # Extract numbers from text
                import re
                numbers = re.findall(r'\d+', text)
                if numbers:
                    return int(numbers[0])
            
        except Exception as e:
            self.logger.warning("Stock quantity extraction failed", selector=selector, error=str(e))
        
        return None
    
    def _extract_text(self, parser, soup, selector: str) -> Optional[str]:
        """Extract text content from element"""
        try:
            if parser:
                element = parser.css_first(selector)
                if element:
                    return element.text().strip()
            else:
                element = soup.select_one(selector)
                if element:
                    return element.get_text().strip()
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
ScraperFactory.register_scraper('http', HttpScraper)


