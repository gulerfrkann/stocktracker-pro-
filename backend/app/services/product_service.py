"""
Product management service
"""

from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
import structlog

from app.models.product import Product, ProductSnapshot, Site
from app.schemas.product import ProductCreate, ProductUpdate
from app.services.scraping_service import ScrapingService

logger = structlog.get_logger()


class ProductService:
    """
    Service for product management and operations
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.scraping_service = ScrapingService(db)
    
    async def create_product(self, product_data: ProductCreate) -> Product:
        """
        Create a new product for tracking
        """
        try:
            product = Product(**product_data.dict())
            self.db.add(product)
            self.db.commit()
            self.db.refresh(product)
            
            logger.info(
                "Product created",
                product_id=product.id,
                name=product.name,
                url=product.url
            )
            
            return product
            
        except Exception as e:
            self.db.rollback()
            logger.error("Failed to create product", error=str(e))
            raise
    
    async def update_product(self, product: Product, product_data: ProductUpdate) -> Product:
        """
        Update an existing product
        """
        try:
            for field, value in product_data.dict(exclude_unset=True).items():
                setattr(product, field, value)
            
            product.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(product)
            
            logger.info(
                "Product updated",
                product_id=product.id,
                updated_fields=list(product_data.dict(exclude_unset=True).keys())
            )
            
            return product
            
        except Exception as e:
            self.db.rollback()
            logger.error("Failed to update product", product_id=product.id, error=str(e))
            raise
    
    def get_products_for_scraping(self, limit: int = 100) -> List[Product]:
        """
        Get products that need to be scraped based on their check intervals
        """
        now = datetime.utcnow()
        
        # Calculate which products need scraping based on their intervals
        products = self.db.query(Product).filter(
            and_(
                Product.is_active == True,
                Product.track_stock == True or Product.track_price == True
            )
        ).all()
        
        products_to_scrape = []
        
        for product in products:
            # Check if enough time has passed since last check
            if product.last_checked is None:
                products_to_scrape.append(product)
            else:
                time_since_last_check = now - product.last_checked
                if time_since_last_check.total_seconds() >= (product.check_interval * 60):
                    products_to_scrape.append(product)
        
        return products_to_scrape[:limit]
    
    async def schedule_initial_scrape(self, product_id: int):
        """
        Schedule an initial scrape for a newly created product
        """
        try:
            await self.scraping_service.scrape_single_product(product_id)
        except Exception as e:
            logger.error(
                "Failed to schedule initial scrape",
                product_id=product_id,
                error=str(e)
            )
    
    async def scrape_single_product(self, product_id: int):
        """
        Scrape a single product immediately
        """
        return await self.scraping_service.scrape_single_product(product_id)
    
    def update_product_from_snapshot(self, product: Product, snapshot: ProductSnapshot):
        """
        Update product's current values from latest snapshot
        """
        try:
            product.current_price = snapshot.price
            product.current_currency = snapshot.currency
            product.is_in_stock = snapshot.is_in_stock
            product.stock_quantity = snapshot.stock_quantity
            product.last_checked = snapshot.created_at
            product.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            logger.info(
                "Product updated from snapshot",
                product_id=product.id,
                price=snapshot.price,
                in_stock=snapshot.is_in_stock
            )
            
        except Exception as e:
            self.db.rollback()
            logger.error(
                "Failed to update product from snapshot",
                product_id=product.id,
                error=str(e)
            )
            raise
    
    def get_price_history(self, product_id: int, days: int = 30) -> List[ProductSnapshot]:
        """
        Get price history for a product
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        snapshots = self.db.query(ProductSnapshot).filter(
            and_(
                ProductSnapshot.product_id == product_id,
                ProductSnapshot.created_at >= start_date,
                ProductSnapshot.price.isnot(None)
            )
        ).order_by(ProductSnapshot.created_at.asc()).all()
        
        return snapshots
    
    def get_stock_changes(self, product_id: int, days: int = 7) -> List[ProductSnapshot]:
        """
        Get stock status changes for a product
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        snapshots = self.db.query(ProductSnapshot).filter(
            and_(
                ProductSnapshot.product_id == product_id,
                ProductSnapshot.created_at >= start_date,
                ProductSnapshot.is_in_stock.isnot(None)
            )
        ).order_by(ProductSnapshot.created_at.asc()).all()
        
        # Filter to only include changes
        changes = []
        last_stock_status = None
        
        for snapshot in snapshots:
            if last_stock_status is None or snapshot.is_in_stock != last_stock_status:
                changes.append(snapshot)
                last_stock_status = snapshot.is_in_stock
        
        return changes
    
    def get_products_by_site(self, site_id: int, active_only: bool = True) -> List[Product]:
        """
        Get all products for a specific site
        """
        query = self.db.query(Product).filter(Product.site_id == site_id)
        
        if active_only:
            query = query.filter(Product.is_active == True)
        
        return query.all()
    
    def get_low_stock_products(self, threshold: int = 5) -> List[Product]:
        """
        Get products with low stock
        """
        return self.db.query(Product).filter(
            and_(
                Product.is_active == True,
                Product.stock_quantity.isnot(None),
                Product.stock_quantity <= threshold,
                Product.stock_quantity > 0
            )
        ).all()
    
    def get_out_of_stock_products(self) -> List[Product]:
        """
        Get products that are out of stock
        """
        return self.db.query(Product).filter(
            and_(
                Product.is_active == True,
                Product.is_in_stock == False
            )
        ).all()
    
    def get_products_with_price_changes(self, hours: int = 24) -> List[dict]:
        """
        Get products that had price changes in the last N hours
        """
        start_time = datetime.utcnow() - timedelta(hours=hours)
        
        # Get recent snapshots with price changes
        recent_snapshots = self.db.query(ProductSnapshot).filter(
            and_(
                ProductSnapshot.created_at >= start_time,
                ProductSnapshot.price.isnot(None)
            )
        ).order_by(ProductSnapshot.product_id, ProductSnapshot.created_at.desc()).all()
        
        # Group by product and find price changes
        price_changes = []
        product_snapshots = {}
        
        for snapshot in recent_snapshots:
            if snapshot.product_id not in product_snapshots:
                product_snapshots[snapshot.product_id] = []
            product_snapshots[snapshot.product_id].append(snapshot)
        
        for product_id, snapshots in product_snapshots.items():
            if len(snapshots) >= 2:
                latest = snapshots[0]
                previous = snapshots[-1]
                
                if latest.price != previous.price:
                    product = self.db.query(Product).filter(Product.id == product_id).first()
                    if product:
                        price_changes.append({
                            'product': product,
                            'old_price': previous.price,
                            'new_price': latest.price,
                            'change_percent': float((latest.price - previous.price) / previous.price * 100) if previous.price else 0,
                            'changed_at': latest.created_at
                        })
        
        return price_changes


