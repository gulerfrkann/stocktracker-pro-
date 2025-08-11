"""
Product-related Pydantic schemas
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, HttpUrl, validator


class ProductBase(BaseModel):
    name: str
    sku: Optional[str] = None
    url: HttpUrl
    barcode: Optional[str] = None
    manufacturer_code: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    min_price_threshold: Optional[Decimal] = None
    max_price_threshold: Optional[Decimal] = None
    track_stock: bool = True
    track_price: bool = True
    check_interval: int = 60  # minutes


class ProductCreate(ProductBase):
    site_id: int


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    sku: Optional[str] = None
    url: Optional[HttpUrl] = None
    barcode: Optional[str] = None
    manufacturer_code: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    min_price_threshold: Optional[Decimal] = None
    max_price_threshold: Optional[Decimal] = None
    track_stock: Optional[bool] = None
    track_price: Optional[bool] = None
    check_interval: Optional[int] = None


class ProductResponse(ProductBase):
    id: int
    site_id: int
    current_price: Optional[Decimal] = None
    current_currency: str = "TRY"
    is_in_stock: Optional[bool] = None
    stock_quantity: Optional[int] = None
    last_checked: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    products: List[ProductResponse]
    total: int
    skip: int
    limit: int


class ProductSnapshotResponse(BaseModel):
    id: int
    product_id: int
    price: Optional[Decimal] = None
    currency: str
    is_in_stock: Optional[bool] = None
    stock_quantity: Optional[int] = None
    page_title: Optional[str] = None
    availability_text: Optional[str] = None
    scrape_duration_ms: Optional[int] = None
    http_status_code: Optional[int] = None
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


