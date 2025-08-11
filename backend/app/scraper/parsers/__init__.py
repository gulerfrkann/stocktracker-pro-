# Site-specific parsers module

# Import all parsers to register them
from .trendyol import TrendyolParser, TrendyolGoParser
from .hepsiburada import HepsiburadaParser
from .n11 import N11Parser
from .amazon_tr import AmazonTRParser
from .gittigidiyor import GittiGidiyorParser

# Import registry for easy access
from .base_parser import SiteParserRegistry

__all__ = [
    'SiteParserRegistry',
    'TrendyolParser',
    'TrendyolGoParser', 
    'HepsiburadaParser',
    'N11Parser',
    'AmazonTRParser',
    'GittiGidiyorParser'
]