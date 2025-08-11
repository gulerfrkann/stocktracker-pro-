"""
Order service: sync orders from marketplaces and persist in DB
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, Any, List, Optional

from sqlalchemy.orm import Session
import structlog

from app.models.order import MarketplaceAccount, Order, OrderItem, OrderEvent
from app.integrations.marketplaces.registry import get_adapter
from app.services.realtime import OrderEventBroadcaster

logger = structlog.get_logger()


class OrderService:
    """
    High-level order operations: listing, syncing, and webhook handling.
    Adapter implementations for each marketplace will live under app.integrations.marketplaces.
    """

    def __init__(self, db: Session):
        self.db = db

    # CRUD: Accounts
    def list_accounts(self) -> List[MarketplaceAccount]:
        return (
            self.db.query(MarketplaceAccount)
            .filter(MarketplaceAccount.is_active == True)
            .order_by(MarketplaceAccount.created_at.desc())
            .all()
        )

    def create_account(self, data: Dict[str, Any], created_by: Optional[str] = None) -> MarketplaceAccount:
        account = MarketplaceAccount(
            platform=data["platform"],
            name=data["name"],
            credentials=data["credentials"],
            configuration=data.get("configuration"),
            webhook_enabled=bool(data.get("webhook_enabled", False)),
            created_by=created_by,
        )
        self.db.add(account)
        self.db.commit()
        self.db.refresh(account)
        return account

    def update_account(self, account_id: int, updates: Dict[str, Any]) -> Optional[MarketplaceAccount]:
        account = self.db.query(MarketplaceAccount).filter(MarketplaceAccount.id == account_id).first()
        if not account:
            return None
        for key in ["name", "credentials", "configuration", "webhook_enabled"]:
            if key in updates and updates[key] is not None:
                setattr(account, key, updates[key])
        self.db.commit()
        self.db.refresh(account)
        return account

    # Orders
    def list_orders(self, skip: int = 0, limit: int = 100, account_id: Optional[int] = None) -> List[Order]:
        query = self.db.query(Order).filter(Order.is_active == True)
        if account_id:
            query = query.filter(Order.account_id == account_id)
        return query.order_by(Order.placed_at.desc().nullslast()).offset(skip).limit(limit).all()

    def get_order(self, order_id: int) -> Optional[Order]:
        return self.db.query(Order).filter(Order.id == order_id).first()

    # Sync logic
    def upsert_order(self, account: MarketplaceAccount, raw_order: Dict[str, Any]) -> Order:
        """
        Idempotent upsert by (account_id, external_order_id)
        raw_order should be a normalized dict with keys matching OrderBase schema.
        """
        external_id = raw_order["external_order_id"]
        order = (
            self.db.query(Order)
            .filter(Order.account_id == account.id, Order.external_order_id == external_id)
            .first()
        )

        if not order:
            order = Order(account_id=account.id, external_order_id=external_id)
            self.db.add(order)

        # Map scalar fields
        scalar_fields = [
            "buyer_name",
            "buyer_email",
            "buyer_phone",
            "shipping_address",
            "billing_address",
            "total_amount",
            "currency",
            "shipment_cost",
            "discount_total",
            "order_status",
            "payment_status",
            "fulfillment_status",
            "placed_at",
            "paid_at",
            "shipped_at",
        ]
        for field in scalar_fields:
            if field in raw_order:
                setattr(order, field, raw_order[field])

        # Replace items (simple approach)
        if "items" in raw_order and isinstance(raw_order["items"], list):
            order.items.clear()
            for item in raw_order["items"]:
                order.items.append(
                    OrderItem(
                        external_product_id=item.get("external_product_id"),
                        sku=item.get("sku"),
                        product_name=item["product_name"],
                        product_url=item.get("product_url"),
                        quantity=item.get("quantity", 1),
                        unit_price=item.get("unit_price"),
                        line_total=item.get("line_total"),
                        currency=item.get("currency", order.currency or "TRY"),
                    )
                )

        self.db.commit()
        self.db.refresh(order)
        # broadcast update
        OrderEventBroadcaster.publish({
            "type": "order.upserted",
            "order_id": order.id,
            "account_id": account.id,
            "external_order_id": order.external_order_id,
            "status": order.order_status,
        })
        return order

    def record_event(
        self,
        order: Order,
        event_type: str,
        payload: Optional[Dict[str, Any]] = None,
        notification_channels: Optional[List[str]] = None,
    ) -> OrderEvent:
        event = OrderEvent(
            order_id=order.id,
            event_type=event_type,
            payload=payload or {},
            notification_channels=notification_channels or ["email"],
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        logger.info("Order event recorded", order_id=order.id, event_type=event_type)
        OrderEventBroadcaster.publish({
            "type": f"order.event.{event_type}",
            "order_id": order.id,
            "event_id": event.id,
        })
        return event

    # High-level sync using adapters
    async def sync_orders(self, account_id: int, since_iso: Optional[str] = None) -> int:
        account = self.db.query(MarketplaceAccount).filter(MarketplaceAccount.id == account_id).first()
        if not account:
            raise ValueError("Account not found")
        adapter = get_adapter(account.platform)
        rows = await adapter.fetch_orders(account.credentials, since_iso=since_iso)
        count = 0
        for row in rows:
            order = self.upsert_order(account, row)
            self.record_event(order, "synced", payload={"source": "api"})
            count += 1
        account.last_synced_at = datetime.utcnow()
        self.db.commit()
        return count

    async def handle_webhook(self, platform: str, account_id: int, payload: Dict[str, Any], headers: Dict[str, Any]) -> Optional[int]:
        account = (
            self.db.query(MarketplaceAccount)
            .filter(MarketplaceAccount.id == account_id, MarketplaceAccount.platform == platform)
            .first()
        )
        if not account:
            raise ValueError("Account not found")
        adapter = get_adapter(platform)
        normalized = await adapter.parse_webhook(payload, headers)
        if not normalized:
            return None
        order = self.upsert_order(account, normalized)
        event = self.record_event(order, "webhook", payload=payload)
        return order.id


