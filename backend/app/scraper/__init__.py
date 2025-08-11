"""
Scraper engine package

Ensure scraper implementations are imported so they can register
themselves with the ScraperFactory at import time.
"""

# Always load HTTP scraper (no extra deps)
from .http_scraper import HttpScraper  # noqa: F401

# Try to load Playwright scraper if dependency is available
try:
    from .playwright_scraper import PlaywrightScraper  # noqa: F401
except Exception:
    # Playwright may be optional in some deployments
    pass

