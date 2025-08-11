"""
Product and inventory tracking models
"""

from datetime import datetime
from decimal import Decimal
from sqlalchemy import (
    Column, String, Text, Numeric, Integer, DateTime, 
    Boolean, ForeignKey, Index, CheckConstraint, JSON
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.models.base import BaseModel


class Site(BaseModel):
    """
    E-commerce sites to scrape
    """
    __tablename__ = "sites"
    
    name = Column(String(100), nullable=False, unique=True, index=True)
    domain = Column(String(255), nullable=False, unique=True, index=True)
    base_url = Column(String(500), nullable=False)
    
    # Site configuration
    request_delay = Column(Numeric(4, 2), default=1.0, nullable=False)  # seconds
    use_javascript = Column(Boolean, default=False, nullable=False)
    requires_proxy = Column(Boolean, default=False, nullable=False)
    
    # CSS selectors for scraping
    selectors = Column(JSON, nullable=True)  # Store selectors as JSON
    
    # Relationship
    products = relationship("Product", back_populates="site")
    
    def __repr__(self):
        return f"<Site(name='{self.name}', domain='{self.domain}')>"


class Product(BaseModel):
    """
    Products to track
    """
    __tablename__ = "products"
    
    # Basic product info
    name = Column(String(500), nullable=False, index=True)
    sku = Column(String(100), nullable=True, index=True)
    url = Column(Text, nullable=False)
    
    # Site reference
    site_id = Column(Integer, ForeignKey("sites.id"), nullable=False, index=True)
    
    # Product identifiers
    barcode = Column(String(50), nullable=True, index=True)
    manufacturer_code = Column(String(100), nullable=True, index=True)
    
    # Current status (cached from latest snapshot)
    current_price = Column(Numeric(10, 2), nullable=True)
    current_currency = Column(String(3), default="TRY", nullable=False)
    is_in_stock = Column(Boolean, nullable=True, index=True)
    stock_quantity = Column(Integer, nullable=True)
    last_checked = Column(DateTime, nullable=True, index=True)
    
    # Tracking settings
    min_price_threshold = Column(Numeric(10, 2), nullable=True)
    max_price_threshold = Column(Numeric(10, 2), nullable=True)
    track_stock = Column(Boolean, default=True, nullable=False)
    track_price = Column(Boolean, default=True, nullable=False)
    
    # Monitoring frequency (in minutes)
    check_interval = Column(Integer, default=60, nullable=False)
    
    # Additional metadata
    category = Column(String(200), nullable=True, index=True)
    tags = Column(JSON, nullable=True)  # Store tags as JSON array
    
    # Relationships
    site = relationship("Site", back_populates="products")
    snapshots = relationship("ProductSnapshot", back_populates="product", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="product", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        Index('idx_product_site_sku', 'site_id', 'sku'),
        Index('idx_product_tracking', 'is_active', 'track_stock', 'track_price'),
        CheckConstraint('check_interval > 0', name='check_positive_interval'),
    )
    
    def __repr__(self):
        return f"<Product(name='{self.name}', sku='{self.sku}', site_id={self.site_id})>"


class ProductSnapshot(BaseModel):
    """
    Historical snapshots of product data
    """
    __tablename__ = "product_snapshots"
    
    # Product reference
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    
    # Snapshot data
    price = Column(Numeric(10, 2), nullable=True)
    currency = Column(String(3), nullable=False)
    is_in_stock = Column(Boolean, nullable=True)
    stock_quantity = Column(Integer, nullable=True)
    
    # Page metadata
    page_title = Column(String(500), nullable=True)
    availability_text = Column(String(200), nullable=True)
    
    # Scraping metadata
    scrape_duration_ms = Column(Integer, nullable=True)
    http_status_code = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Raw data for debugging
    raw_html_hash = Column(String(64), nullable=True)  # MD5 hash of scraped content
    
    # Relationship
    product = relationship("Product", back_populates="snapshots")
    
    # Indexes for time-series queries
    __table_args__ = (
        Index('idx_snapshot_product_time', 'product_id', 'created_at'),
        Index('idx_snapshot_time', 'created_at'),
        Index('idx_snapshot_stock_status', 'product_id', 'is_in_stock', 'created_at'),
    )
    
    def __repr__(self):
        return f"<ProductSnapshot(product_id={self.product_id}, price={self.price}, created_at={self.created_at})>"


class Alert(BaseModel):
    """
    Price and stock alerts
    """
    __tablename__ = "alerts"
    
    # Alert ID for external tracking
    alert_uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False, index=True)
    
    # Product reference
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    
    # Alert type and condition
    alert_type = Column(String(50), nullable=False, index=True)  # 'stock_out', 'stock_in', 'price_drop', 'price_rise'
    condition_value = Column(Numeric(10, 2), nullable=True)  # Threshold value for price alerts
    
    # Trigger data
    triggered_at = Column(DateTime, nullable=True, index=True)
    trigger_value = Column(Numeric(10, 2), nullable=True)  # Actual value that triggered the alert
    trigger_snapshot_id = Column(Integer, ForeignKey("product_snapshots.id"), nullable=True)
    
    # Notification status
    is_sent = Column(Boolean, default=False, nullable=False, index=True)
    sent_at = Column(DateTime, nullable=True)
    notification_channels = Column(JSON, nullable=True)  # ['email', 'slack', 'webhook']
    
    # Alert message
    message = Column(Text, nullable=True)
    
    # Relationship
    product = relationship("Product", back_populates="alerts")
    
    # Indexes
    __table_args__ = (
        Index('idx_alert_product_type', 'product_id', 'alert_type'),
        Index('idx_alert_pending', 'is_sent', 'triggered_at'),
        Index('idx_alert_triggered', 'triggered_at'),
    )
    
    def __repr__(self):
        return f"<Alert(product_id={self.product_id}, type='{self.alert_type}', triggered={self.triggered_at})>"


class ScrapingJob(BaseModel):
    """
    Scraping job tracking and scheduling
    """
    __tablename__ = "scraping_jobs"
    
    # Job identification
    job_uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False, index=True)
    
    # Job configuration
    job_type = Column(String(50), nullable=False, index=True)  # 'single_product', 'bulk_products', 'scheduled'
    product_ids = Column(JSON, nullable=False)  # List of product IDs to scrape
    
    # Scheduling
    scheduled_at = Column(DateTime, nullable=True, index=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Status tracking
    status = Column(String(20), default="pending", nullable=False, index=True)  # 'pending', 'running', 'completed', 'failed'
    progress = Column(Integer, default=0, nullable=False)  # Percentage completed
    total_products = Column(Integer, nullable=False)
    successful_scrapes = Column(Integer, default=0, nullable=False)
    failed_scrapes = Column(Integer, default=0, nullable=False)
    
    # Error tracking
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    max_retries = Column(Integer, default=3, nullable=False)
    
    # Performance metrics
    avg_scrape_time_ms = Column(Integer, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_job_status_scheduled', 'status', 'scheduled_at'),
        Index('idx_job_created', 'created_at'),
    )
    
    def __repr__(self):
        return f"<ScrapingJob(uuid='{self.job_uuid}', status='{self.status}', progress={self.progress}%)>"


