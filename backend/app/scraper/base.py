"""
Base scraper classes and interfaces
"""

import asyncio
import time
import hashlib
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from decimal import Decimal
import structlog

from app.core.config import settings

logger = structlog.get_logger()


@dataclass
class ScrapedData:
    """
    Standardized scraped data structure
    """
    url: str
    timestamp: datetime
    
    # Product data
    price: Optional[Decimal] = None
    currency: str = "TRY"
    is_in_stock: Optional[bool] = None
    stock_quantity: Optional[int] = None
    
    # Page metadata
    page_title: Optional[str] = None
    availability_text: Optional[str] = None
    product_name: Optional[str] = None
    
    # Technical metadata
    http_status_code: Optional[int] = None
    response_time_ms: Optional[int] = None
    content_hash: Optional[str] = None
    error_message: Optional[str] = None
    
    # Raw data for debugging
    raw_html: Optional[str] = None
    
    def __post_init__(self):
        """Generate content hash if raw_html is available"""
        if self.raw_html and not self.content_hash:
            self.content_hash = hashlib.md5(self.raw_html.encode()).hexdigest()


@dataclass
class ScrapeRequest:
    """
    Scrape request configuration
    """
    url: str
    site_config: Dict[str, Any]
    product_id: Optional[int] = None
    retry_count: int = 0
    max_retries: int = 3
    timeout: int = 30
    use_proxy: bool = False
    headers: Optional[Dict[str, str]] = None


class BaseScraper(ABC):
    """
    Abstract base class for all scrapers
    """
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logger.bind(scraper=name)
        self._session_active = False
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize scraper resources"""
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """Cleanup scraper resources"""
        pass
    
    @abstractmethod
    async def scrape(self, request: ScrapeRequest) -> ScrapedData:
        """
        Scrape data from the given request
        
        Args:
            request: ScrapeRequest with URL and configuration
            
        Returns:
            ScrapedData: Extracted data
            
        Raises:
            ScrapingError: When scraping fails
        """
        pass
    
    async def scrape_multiple(self, requests: List[ScrapeRequest]) -> List[ScrapedData]:
        """
        Scrape multiple URLs with rate limiting
        
        Args:
            requests: List of scrape requests
            
        Returns:
            List of scraped data
        """
        results = []
        
        for i, request in enumerate(requests):
            try:
                # Rate limiting
                if i > 0:
                    delay = request.site_config.get('request_delay', settings.DEFAULT_REQUEST_DELAY)
                    await asyncio.sleep(delay)
                
                result = await self.scrape(request)
                results.append(result)
                
                self.logger.info(
                    "Scrape completed",
                    url=request.url,
                    status="success",
                    price=result.price,
                    in_stock=result.is_in_stock
                )
                
            except Exception as e:
                error_result = ScrapedData(
                    url=request.url,
                    timestamp=datetime.utcnow(),
                    error_message=str(e)
                )
                results.append(error_result)
                
                self.logger.error(
                    "Scrape failed",
                    url=request.url,
                    error=str(e),
                    retry_count=request.retry_count
                )
        
        return results
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.cleanup()


class ScrapingError(Exception):
    """Custom exception for scraping errors"""
    
    def __init__(self, message: str, url: str = None, status_code: int = None):
        self.message = message
        self.url = url
        self.status_code = status_code
        super().__init__(self.message)


class RetryableError(ScrapingError):
    """Error that should be retried"""
    pass


class PermanentError(ScrapingError):
    """Error that should not be retried"""
    pass


class ScraperFactory:
    """
    Factory for creating appropriate scrapers based on site configuration
    """
    
    _scrapers: Dict[str, type] = {}
    
    @classmethod
    def register_scraper(cls, scraper_type: str, scraper_class: type):
        """Register a scraper class"""
        cls._scrapers[scraper_type] = scraper_class
    
    @classmethod
    def create_scraper(cls, site_config: Dict[str, Any]) -> BaseScraper:
        """
        Create appropriate scraper based on site configuration
        
        Args:
            site_config: Site configuration dictionary
            
        Returns:
            BaseScraper instance
        """
        use_javascript = site_config.get('use_javascript', False)
        scraper_type = 'playwright' if use_javascript else 'http'
        
        scraper_class = cls._scrapers.get(scraper_type)
        if not scraper_class:
            raise ValueError(f"Unknown scraper type: {scraper_type}")
        
        return scraper_class(name=f"{scraper_type}_scraper")


class RateLimiter:
    """
    Rate limiter for controlling request frequency
    """
    
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests = []
        self.lock = asyncio.Lock()
    
    async def acquire(self):
        """Acquire permission to make a request"""
        async with self.lock:
            now = time.time()
            
            # Remove old requests (older than 1 minute)
            self.requests = [req_time for req_time in self.requests if now - req_time < 60]
            
            # Check if we need to wait
            if len(self.requests) >= self.requests_per_minute:
                oldest_request = min(self.requests)
                wait_time = 60 - (now - oldest_request)
                
                if wait_time > 0:
                    logger.info(f"Rate limit reached, waiting {wait_time:.2f} seconds")
                    await asyncio.sleep(wait_time)
            
            # Record this request
            self.requests.append(now)


# Global rate limiter instance
rate_limiter = RateLimiter(settings.RATE_LIMIT_PER_MINUTE)


