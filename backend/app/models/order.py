"""
Order management models for marketplace integrations
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    Boolean,
    ForeignKey,
    Numeric,
    JSON,
    Index,
)
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class MarketplaceAccount(BaseModel):
    """
    Seller account configuration per marketplace (e.g., Trendyol, Hepsiburada, N11).
    Stores credentials and sync/webhook settings.
    """

    __tablename__ = "marketplace_accounts"

    platform = Column(String(50), nullable=False, index=True)  # trendyol, hepsiburada, n11, pazarama, epttavm, ciceksepeti, idefix
    name = Column(String(100), nullable=False, index=True)  # Friendly name

    # Credentials and configuration
    credentials = Column(JSON, nullable=False)  # API keys, secrets, seller IDs
    configuration = Column(JSON, nullable=True)  # Optional extra configuration per platform

    # Sync & webhook
    last_synced_at = Column(DateTime, nullable=True, index=True)
    webhook_secret = Column(String(255), nullable=True)
    webhook_enabled = Column(Boolean, default=False, nullable=False)

    # Ownership
    created_by = Column(String(64), nullable=True, index=True)  # Reference to User.user_uuid (string)

    def __repr__(self) -> str:
        return f"<MarketplaceAccount(platform='{self.platform}', name='{self.name}')>"


class Order(BaseModel):
    """
    Top-level order entity fetched from marketplaces
    """

    __tablename__ = "orders"

    # Identification
    account_id = Column(Integer, ForeignKey("marketplace_accounts.id"), nullable=False, index=True)
    external_order_id = Column(String(100), nullable=False, index=True)  # Order ID on marketplace

    # Buyer & shipping
    buyer_name = Column(String(200), nullable=True)
    buyer_email = Column(String(255), nullable=True)
    buyer_phone = Column(String(50), nullable=True)
    shipping_address = Column(JSON, nullable=True)
    billing_address = Column(JSON, nullable=True)

    # Amounts
    total_amount = Column(Numeric(12, 2), nullable=True)
    currency = Column(String(3), default="TRY", nullable=False)
    shipment_cost = Column(Numeric(12, 2), nullable=True)
    discount_total = Column(Numeric(12, 2), nullable=True)

    # Status
    order_status = Column(String(50), nullable=True, index=True)  # created, confirmed, shipped, delivered, cancelled, returned
    payment_status = Column(String(50), nullable=True, index=True)
    fulfillment_status = Column(String(50), nullable=True, index=True)

    # Timestamps from marketplace
    placed_at = Column(DateTime, nullable=True, index=True)
    paid_at: Optional[datetime] = Column(DateTime, nullable=True)
    shipped_at: Optional[datetime] = Column(DateTime, nullable=True)

    # Relationships
    account = relationship("MarketplaceAccount")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    events = relationship("OrderEvent", back_populates="order", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_order_account_external", "account_id", "external_order_id", unique=True),
        Index("idx_order_status_placed", "order_status", "placed_at"),
    )

    def __repr__(self) -> str:
        return f"<Order(account_id={self.account_id}, external_order_id='{self.external_order_id}', status='{self.order_status}')>"


class OrderItem(BaseModel):
    """
    Line items for an order
    """

    __tablename__ = "order_items"

    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)

    # Product info (marketplace-level; may differ from internal product table)
    external_product_id = Column(String(100), nullable=True, index=True)
    sku = Column(String(100), nullable=True, index=True)
    product_name = Column(String(500), nullable=False)
    product_url = Column(String(1000), nullable=True)

    # Quantities & prices
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Numeric(12, 2), nullable=True)
    line_total = Column(Numeric(12, 2), nullable=True)
    currency = Column(String(3), default="TRY", nullable=False)

    order = relationship("Order", back_populates="items")

    def __repr__(self) -> str:
        return f"<OrderItem(order_id={self.order_id}, sku='{self.sku}', qty={self.quantity})>"


class OrderEvent(BaseModel):
    """
    Order lifecycle events (created, status_changed, shipment updates, etc.)
    """

    __tablename__ = "order_events"

    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    event_type = Column(String(50), nullable=False, index=True)  # created, status_changed, shipment_updated
    occurred_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    payload = Column(JSON, nullable=True)  # Raw data from marketplace

    # Notification status
    is_notified = Column(Boolean, default=False, nullable=False, index=True)
    notified_at = Column(DateTime, nullable=True)
    notification_channels = Column(JSON, nullable=True)  # ['email','slack','webhook']

    order = relationship("Order", back_populates="events")

    def __repr__(self) -> str:
        return f"<OrderEvent(order_id={self.order_id}, type='{self.event_type}', occurred_at={self.occurred_at})>"



