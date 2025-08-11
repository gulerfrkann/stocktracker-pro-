"""
Base parser class for site-specific configurations
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class SiteConfig:
    """
    Site configuration for scraping
    """
    name: str
    domain: str
    selectors: Dict[str, str]
    use_javascript: bool = False
    requires_proxy: bool = False
    request_delay: float = 1.0
    headers: Optional[Dict[str, str]] = None
    custom_logic: Optional[Dict[str, Any]] = None


class BaseSiteParser(ABC):
    """
    Base class for site-specific parsers
    """
    
    def __init__(self):
        self.config = self.get_config()
    
    @abstractmethod
    def get_config(self) -> SiteConfig:
        """Return site configuration"""
        pass
    
    def get_selectors(self) -> Dict[str, str]:
        """Get CSS selectors for this site"""
        return self.config.selectors
    
    def get_headers(self) -> Dict[str, str]:
        """Get custom headers for this site"""
        return self.config.headers or {}
    
    def requires_javascript(self) -> bool:
        """Check if site requires JavaScript"""
        return self.config.use_javascript
    
    def needs_proxy(self) -> bool:
        """Check if site requires proxy"""
        return self.config.requires_proxy
    
    def get_request_delay(self) -> float:
        """Get delay between requests"""
        return self.config.request_delay


class SiteParserRegistry:
    """
    Registry for site parsers
    """
    
    _parsers: Dict[str, BaseSiteParser] = {}
    
    @classmethod
    def register(cls, domain: str, parser: BaseSiteParser):
        """Register a parser for a domain"""
        cls._parsers[domain] = parser
    
    @classmethod
    def get_parser(cls, domain: str) -> Optional[BaseSiteParser]:
        """Get parser for a domain"""
        # Exact match first
        if domain in cls._parsers:
            return cls._parsers[domain]
        
        # Try partial matches (subdomain support)
        for registered_domain, parser in cls._parsers.items():
            if domain.endswith(registered_domain) or registered_domain in domain:
                return parser
        
        return None
    
    @classmethod
    def get_all_supported_sites(cls) -> Dict[str, str]:
        """Get all supported sites"""
        return {domain: parser.config.name for domain, parser in cls._parsers.items()}


