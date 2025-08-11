"""
Pydantic schemas for marketplace order management
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Dict, Any

from pydantic import BaseModel


class MarketplaceAccountBase(BaseModel):
    platform: str
    name: str
    credentials: Dict[str, Any]
    configuration: Optional[Dict[str, Any]] = None
    webhook_enabled: bool = False


class MarketplaceAccountCreate(MarketplaceAccountBase):
    pass


class MarketplaceAccountUpdate(BaseModel):
    name: Optional[str] = None
    credentials: Optional[Dict[str, Any]] = None
    configuration: Optional[Dict[str, Any]] = None
    webhook_enabled: Optional[bool] = None


class MarketplaceAccountResponse(MarketplaceAccountBase):
    id: int
    last_synced_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


class OrderItemBase(BaseModel):
    external_product_id: Optional[str] = None
    sku: Optional[str] = None
    product_name: str
    product_url: Optional[str] = None
    quantity: int
    unit_price: Optional[Decimal] = None
    line_total: Optional[Decimal] = None
    currency: str = "TRY"


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemResponse(OrderItemBase):
    id: int
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


class OrderBase(BaseModel):
    account_id: int
    external_order_id: str
    buyer_name: Optional[str] = None
    buyer_email: Optional[str] = None
    buyer_phone: Optional[str] = None
    shipping_address: Optional[Dict[str, Any]] = None
    billing_address: Optional[Dict[str, Any]] = None
    total_amount: Optional[Decimal] = None
    currency: str = "TRY"
    shipment_cost: Optional[Decimal] = None
    discount_total: Optional[Decimal] = None
    order_status: Optional[str] = None
    payment_status: Optional[str] = None
    fulfillment_status: Optional[str] = None
    placed_at: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    shipped_at: Optional[datetime] = None


class OrderCreate(OrderBase):
    items: List[OrderItemCreate]


class OrderResponse(OrderBase):
    id: int
    items: List[OrderItemResponse]
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


class OrderEventResponse(BaseModel):
    id: int
    order_id: int
    event_type: str
    occurred_at: datetime
    payload: Optional[Dict[str, Any]] = None
    is_notified: bool
    notified_at: Optional[datetime] = None
    notification_channels: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        from_attributes = True



