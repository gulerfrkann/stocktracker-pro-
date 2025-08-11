"""
Scraping service for managing web scraping operations
"""

import asyncio
from datetime import datetime
from typing import List, Optional, Dict, Any
from urllib.parse import urlparse
from sqlalchemy.orm import Session
from sqlalchemy import and_
import structlog

from app.models.product import Product, ProductSnapshot, Site, ScrapingJob
from app.scraper.base import ScraperFactory, ScrapeRequest, ScrapedData, rate_limiter
from app.scraper.parsers import SiteParserRegistry
from app.services.alert_service import AlertService
from app.models.custom_fields import UserDataPreferences, CustomFieldMapping, ProductCustomData
from app.scraper.custom_extractor import CustomFieldExtractor

logger = structlog.get_logger()


class ScrapingService:
    """
    Service for managing web scraping operations
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.alert_service = AlertService(db)
    
    async def scrape_single_product(self, product_id: int, user_id: str = None) -> Optional[ProductSnapshot]:
        """
        Scrape a single product and save the snapshot
        """
        try:
            # Get product with site info
            product = self.db.query(Product).join(Site).filter(
                Product.id == product_id
            ).first()
            
            if not product:
                logger.error("Product not found", product_id=product_id)
                return None
            
            # Get site parser configuration
            site_config = self._get_site_config(product.site)
            
            # Create scrape request
            request = ScrapeRequest(
                url=product.url,
                site_config=site_config,
                product_id=product_id
            )
            
            # Create appropriate scraper
            scraper = ScraperFactory.create_scraper(site_config)
            
            # Perform scraping
            async with scraper:
                # Apply rate limiting
                await rate_limiter.acquire()
                
                scraped_data = await scraper.scrape(request)
                
                # Save snapshot
                snapshot = await self._save_snapshot(product, scraped_data)
                
                # Extract and save custom fields if user_id provided
                if snapshot and user_id and not snapshot.error_message:
                    await self._extract_and_save_custom_fields(
                        product, snapshot, scraped_data, user_id
                    )
                
                # Check for alerts
                if snapshot and not snapshot.error_message:
                    await self.alert_service.check_and_create_alerts(product, snapshot)
                
                # Update product current values
                if snapshot and not snapshot.error_message:
                    self._update_product_current_values(product, snapshot)
                
                logger.info(
                    "Product scraped successfully",
                    product_id=product_id,
                    price=scraped_data.price,
                    in_stock=scraped_data.is_in_stock,
                    response_time=scraped_data.response_time_ms
                )
                
                return snapshot
                
        except Exception as e:
            logger.error(
                "Failed to scrape product",
                product_id=product_id,
                error=str(e),
                error_type=type(e).__name__
            )
            
            # Save error snapshot
            error_data = ScrapedData(
                url=product.url if product else "unknown",
                timestamp=datetime.utcnow(),
                error_message=str(e)
            )
            
            if product:
                await self._save_snapshot(product, error_data)
            
            return None
    
    async def scrape_multiple_products(self, product_ids: List[int]) -> List[ProductSnapshot]:
        """
        Scrape multiple products concurrently with rate limiting
        """
        logger.info("Starting bulk scraping", product_count=len(product_ids))
        
        # Create scraping tasks
        tasks = []
        for product_id in product_ids:
            task = asyncio.create_task(self.scrape_single_product(product_id))
            tasks.append(task)
        
        # Execute with concurrency limit
        semaphore = asyncio.Semaphore(5)  # Max 5 concurrent scrapes
        
        async def limited_scrape(task):
            async with semaphore:
                return await task
        
        limited_tasks = [limited_scrape(task) for task in tasks]
        snapshots = await asyncio.gather(*limited_tasks, return_exceptions=True)
        
        # Filter out exceptions and None results
        valid_snapshots = [s for s in snapshots if isinstance(s, ProductSnapshot)]
        
        logger.info(
            "Bulk scraping completed",
            total_products=len(product_ids),
            successful_scrapes=len(valid_snapshots),
            failed_scrapes=len(product_ids) - len(valid_snapshots)
        )
        
        return valid_snapshots
    
    async def execute_job(self, job_id: int):
        """
        Execute a scraping job
        """
        try:
            # Get job
            job = self.db.query(ScrapingJob).filter(ScrapingJob.id == job_id).first()
            if not job:
                logger.error("Scraping job not found", job_id=job_id)
                return
            
            # Update job status
            job.status = "running"
            job.started_at = datetime.utcnow()
            self.db.commit()
            
            logger.info("Starting scraping job", job_id=job_id, product_count=len(job.product_ids))
            
            # Execute scraping
            start_time = datetime.utcnow()
            snapshots = await self.scrape_multiple_products(job.product_ids)
            end_time = datetime.utcnow()
            
            # Update job with results
            job.completed_at = end_time
            job.successful_scrapes = len(snapshots)
            job.failed_scrapes = job.total_products - len(snapshots)
            job.progress = 100
            job.status = "completed"
            job.avg_scrape_time_ms = int((end_time - start_time).total_seconds() * 1000 / job.total_products) if job.total_products > 0 else 0
            
            self.db.commit()
            
            logger.info(
                "Scraping job completed",
                job_id=job_id,
                successful=job.successful_scrapes,
                failed=job.failed_scrapes,
                duration_seconds=(end_time - start_time).total_seconds()
            )
            
        except Exception as e:
            logger.error("Scraping job failed", job_id=job_id, error=str(e))
            
            # Update job with error
            if job:
                job.status = "failed"
                job.error_message = str(e)
                job.completed_at = datetime.utcnow()
                self.db.commit()
    
    def _get_site_config(self, site: Site) -> Dict[str, Any]:
        """
        Get configuration for a site
        """
        # Start with site's database configuration
        config = {
            'name': site.name,
            'domain': site.domain,
            'request_delay': float(site.request_delay),
            'use_javascript': site.use_javascript,
            'requires_proxy': site.requires_proxy,
            'selectors': site.selectors or {}
        }
        
        # Try to get more detailed configuration from parser registry
        domain = urlparse(site.base_url).netloc.replace('www.', '')
        parser = SiteParserRegistry.get_parser(domain)
        
        if parser:
            parser_config = parser.get_config()
            config.update({
                'selectors': parser_config.selectors,
                'use_javascript': parser_config.use_javascript,
                'requires_proxy': parser_config.requires_proxy,
                'request_delay': parser_config.request_delay,
                'headers': parser_config.headers,
                'custom_logic': parser_config.custom_logic
            })
        
        return config
    
    async def _save_snapshot(self, product: Product, scraped_data: ScrapedData) -> ProductSnapshot:
        """
        Save scraped data as a product snapshot
        """
        try:
            snapshot = ProductSnapshot(
                product_id=product.id,
                price=scraped_data.price,
                currency=scraped_data.currency,
                is_in_stock=scraped_data.is_in_stock,
                stock_quantity=scraped_data.stock_quantity,
                page_title=scraped_data.page_title,
                availability_text=scraped_data.availability_text,
                scrape_duration_ms=scraped_data.response_time_ms,
                http_status_code=scraped_data.http_status_code,
                error_message=scraped_data.error_message,
                raw_html_hash=scraped_data.content_hash
            )
            
            self.db.add(snapshot)
            self.db.commit()
            self.db.refresh(snapshot)
            
            return snapshot
            
        except Exception as e:
            self.db.rollback()
            logger.error(
                "Failed to save snapshot",
                product_id=product.id,
                error=str(e)
            )
            raise
    
    def _update_product_current_values(self, product: Product, snapshot: ProductSnapshot):
        """
        Update product's current values from snapshot
        """
        try:
            product.current_price = snapshot.price
            product.current_currency = snapshot.currency
            product.is_in_stock = snapshot.is_in_stock
            product.stock_quantity = snapshot.stock_quantity
            product.last_checked = snapshot.created_at
            product.updated_at = datetime.utcnow()
            
            self.db.commit()
            
        except Exception as e:
            self.db.rollback()
            logger.error(
                "Failed to update product current values",
                product_id=product.id,
                error=str(e)
            )
    
    def get_scraping_stats(self, days: int = 7) -> Dict[str, Any]:
        """
        Get scraping statistics for the last N days
        """
        from datetime import timedelta
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get snapshot counts
        total_snapshots = self.db.query(ProductSnapshot).filter(
            ProductSnapshot.created_at >= start_date
        ).count()
        
        successful_snapshots = self.db.query(ProductSnapshot).filter(
            and_(
                ProductSnapshot.created_at >= start_date,
                ProductSnapshot.error_message.is_(None)
            )
        ).count()
        
        failed_snapshots = total_snapshots - successful_snapshots
        
        # Get average response time
        avg_response_time = self.db.query(
            ProductSnapshot.scrape_duration_ms
        ).filter(
            and_(
                ProductSnapshot.created_at >= start_date,
                ProductSnapshot.scrape_duration_ms.isnot(None)
            )
        ).all()
        
        avg_time = sum(s[0] for s in avg_response_time) / len(avg_response_time) if avg_response_time else 0
        
        return {
            'days': days,
            'total_snapshots': total_snapshots,
            'successful_snapshots': successful_snapshots,
            'failed_snapshots': failed_snapshots,
            'success_rate': (successful_snapshots / total_snapshots * 100) if total_snapshots > 0 else 0,
            'avg_response_time_ms': int(avg_time),
            'snapshots_per_day': total_snapshots / days if days > 0 else 0
        }
    
    async def _extract_and_save_custom_fields(
        self, 
        product: Product, 
        snapshot: ProductSnapshot, 
        scraped_data: ScrapedData, 
        user_id: str
    ):
        """
        Extract and save custom fields for a user
        """
        try:
            # Get user preferences for this site
            preferences = self.db.query(UserDataPreferences).filter(
                UserDataPreferences.user_id == user_id,
                UserDataPreferences.site_id == product.site_id
            ).first()
            
            if not preferences:
                return  # No custom preferences set
            
            # Get custom field mappings for this site and user
            mappings = self.db.query(CustomFieldMapping).join(
                CustomFieldMapping.field_definition
            ).filter(
                CustomFieldMapping.site_id == product.site_id,
                CustomFieldMapping.user_id == user_id
            ).all()
            
            if not mappings:
                return  # No custom field mappings
            
            # Prepare mapping data for extractor
            mapping_configs = []
            for mapping in mappings:
                field_definition = mapping.field_definition
                
                # Check if this field is enabled in user preferences
                enabled_fields = preferences.enabled_custom_fields or []
                if str(field_definition.field_uuid) not in enabled_fields:
                    continue
                
                mapping_configs.append({
                    'field_id': field_definition.id,
                    'field_name': field_definition.field_name,
                    'field_type': field_definition.field_type,
                    'css_selector': mapping.css_selector,
                    'attribute': mapping.attribute,
                    'regex_pattern': mapping.regex_pattern,
                    'preprocessing_rules': mapping.preprocessing_rules or {}
                })
            
            if not mapping_configs:
                return  # No enabled custom fields
            
            # Extract custom fields from raw HTML
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(scraped_data.raw_html, 'html.parser')
            
            extractor = CustomFieldExtractor()
            
            # Convert user preferences to dict for extractor
            user_prefs = {
                f'extract_{config["field_name"]}': True 
                for config in mapping_configs
            }
            
            extraction_results = extractor.extract_custom_fields(
                parser=None,  # We're using BeautifulSoup
                soup=soup,
                custom_field_mappings=mapping_configs,
                user_preferences=user_prefs
            )
            
            # Save extraction results
            for result in extraction_results:
                # Find the corresponding mapping
                mapping = next(
                    (m for m in mappings 
                     if m.field_definition.field_name == result.field_name), 
                    None
                )
                
                if mapping:
                    custom_data = ProductCustomData(
                        product_id=product.id,
                        field_id=mapping.field_definition.id,
                        snapshot_id=snapshot.id,
                        field_value=str(result.processed_value) if result.processed_value is not None else None,
                        raw_value=result.raw_value,
                        extraction_successful=result.extraction_successful,
                        extraction_error=result.error_message
                    )
                    
                    self.db.add(custom_data)
            
            self.db.commit()
            
            logger.info(
                "Custom fields extracted",
                product_id=product.id,
                user_id=user_id,
                extracted_fields=len(extraction_results),
                successful_extractions=len([r for r in extraction_results if r.extraction_successful])
            )
            
        except Exception as e:
            self.db.rollback()
            logger.error(
                "Failed to extract custom fields",
                product_id=product.id,
                user_id=user_id,
                error=str(e)
            )
