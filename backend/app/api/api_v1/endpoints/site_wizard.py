"""
Site wizard endpoints for adding new e-commerce sites
"""

from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
import httpx
from urllib.parse import urlparse

from app.core.database import get_db
from app.models.product import Site
from app.scraper.parsers.generic_parser import SiteWizard, create_dynamic_parser
from app.scraper.parsers.base_parser import SiteParserRegistry
from app.schemas.site_wizard import (
    SiteAnalysisRequest, SiteAnalysisResponse, 
    NewSiteConfig, SiteTestRequest, SiteTestResponse
)

router = APIRouter()


@router.post("/analyze-site", response_model=SiteAnalysisResponse)
async def analyze_site(
    request: SiteAnalysisRequest,
    db: Session = Depends(get_db)
):
    """
    Analyze a website and suggest configuration
    """
    try:
        # Validate URL
        # Cast Pydantic HttpUrl to plain string to avoid decode errors
        parsed = urlparse(str(request.url))
        if not parsed.scheme or not parsed.netloc:
            raise HTTPException(status_code=400, detail="Invalid URL")
        
        domain = parsed.netloc.replace('www.', '')
        
        # Check if site already exists
        existing_site = db.query(Site).filter(Site.domain == domain).first()
        if existing_site:
            raise HTTPException(
                status_code=400, 
                detail=f"Site {domain} already exists in the system"
            )
        
        # Fetch page content for analysis
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(
                    str(request.url),
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                    }
                )
                response.raise_for_status()
                html_content = response.text
                
            except httpx.RequestError as e:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Could not fetch website: {str(e)}"
                )
        
        # Analyze HTML and suggest selectors
        suggested_selectors = SiteWizard.suggest_selectors(html_content)
        
        # Create basic config
        basic_config = SiteWizard.create_config_from_url(str(request.url))
        
        return SiteAnalysisResponse(
            domain=domain,
            site_name=basic_config['name'],
            suggested_config=basic_config,
            suggested_selectors=suggested_selectors,
            requires_javascript=basic_config['use_javascript'],
            analysis_successful=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Analysis failed: {str(e)}"
        )


@router.post("/test-configuration", response_model=SiteTestResponse)
async def test_site_configuration(
    request: SiteTestRequest,
    background_tasks: BackgroundTasks
):
    """
    Test a site configuration by attempting to scrape
    """
    try:
        # Create temporary parser
        parser = create_dynamic_parser(request.domain, request.config.dict())
        
        # Perform test scrape
        from app.scraper.base import ScraperFactory, ScrapeRequest
        
        scraper = ScraperFactory.create_scraper(parser.get_config().__dict__)
        
        # Ensure url is plain string (Pydantic HttpUrl -> str)
        scrape_request = ScrapeRequest(
            url=str(request.test_url),
            site_config=parser.get_config().__dict__
        )
        
        async with scraper:
            scraped_data = await scraper.scrape(scrape_request)
        
        # Analyze results
        test_successful = (
            scraped_data.error_message is None and
            (scraped_data.price is not None or scraped_data.is_in_stock is not None)
        )
        
        issues = []
        if scraped_data.error_message:
            issues.append(f"Scraping error: {scraped_data.error_message}")
        if scraped_data.price is None:
            issues.append("Could not extract price")
        if scraped_data.is_in_stock is None:
            issues.append("Could not extract stock status")
        
        suggestions = []
        if not test_successful:
            suggestions.append("Try adjusting CSS selectors")
            if request.config.use_javascript:
                suggestions.append("Site might need more wait time for JavaScript")
            else:
                suggestions.append("Site might require JavaScript rendering")
        
        return SiteTestResponse(
            test_successful=test_successful,
            extracted_data={
                'price': float(scraped_data.price) if scraped_data.price else None,
                'currency': scraped_data.currency,
                'in_stock': scraped_data.is_in_stock,
                'product_name': scraped_data.product_name,
                'page_title': scraped_data.page_title
            },
            response_time_ms=scraped_data.response_time_ms,
            issues=issues,
            suggestions=suggestions,
            http_status_code=scraped_data.http_status_code
        )
        
    except Exception as e:
        return SiteTestResponse(
            test_successful=False,
            extracted_data={},
            issues=[f"Test failed: {str(e)}"],
            suggestions=["Check URL and selectors", "Verify site is accessible"]
        )


@router.post("/create-site")
async def create_new_site(
    config: NewSiteConfig,
    db: Session = Depends(get_db)
):
    """
    Create a new site configuration
    """
    try:
        # Check if domain already exists
        existing_site = db.query(Site).filter(Site.domain == config.domain).first()
        if existing_site:
            raise HTTPException(
                status_code=400,
                detail="Site already exists"
            )
        
        # Create site record
        site = Site(
            name=config.name,
            domain=config.domain,
            base_url=f"https://{config.domain}",
            use_javascript=config.use_javascript,
            requires_proxy=config.requires_proxy,
            request_delay=config.request_delay,
            selectors=config.selectors
        )
        
        db.add(site)
        db.commit()
        db.refresh(site)
        
        # Register dynamic parser
        parser = create_dynamic_parser(config.domain, config.dict())
        SiteParserRegistry.register(config.domain, parser)
        
        return {
            "message": "Site created successfully",
            "site_id": site.id,
            "domain": site.domain
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create site: {str(e)}"
        )


@router.get("/supported-sites")
async def get_supported_sites():
    """
    Get list of all supported sites
    """
    try:
        # Get from parser registry
        parser_sites = SiteParserRegistry.get_all_supported_sites()
        
        # Get from database
        from app.core.database import get_db
        db = next(get_db())
        db_sites = db.query(Site).filter(Site.is_active == True).all()
        
        supported_sites = []
        
        # Add parser-based sites
        for domain, name in parser_sites.items():
            supported_sites.append({
                'domain': domain,
                'name': name,
                'type': 'predefined',
                'parser_available': True
            })
        
        # Add database sites that aren't in parsers
        for site in db_sites:
            if site.domain not in parser_sites:
                supported_sites.append({
                    'domain': site.domain,
                    'name': site.name,
                    'type': 'dynamic',
                    'parser_available': False
                })
        
        return {
            'total_sites': len(supported_sites),
            'predefined_sites': len([s for s in supported_sites if s['type'] == 'predefined']),
            'dynamic_sites': len([s for s in supported_sites if s['type'] == 'dynamic']),
            'sites': supported_sites
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get supported sites: {str(e)}"
        )

