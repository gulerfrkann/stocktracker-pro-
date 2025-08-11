"""
Orders and marketplace accounts endpoints
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.order_service import OrderService
from app.schemas.order import (
    MarketplaceAccountCreate,
    MarketplaceAccountUpdate,
    MarketplaceAccountResponse,
    OrderResponse,
)

router = APIRouter()


@router.get("/accounts", response_model=List[MarketplaceAccountResponse])
async def list_marketplace_accounts(db: Session = Depends(get_db)):
    service = OrderService(db)
    accounts = service.list_accounts()
    return [MarketplaceAccountResponse.from_orm(a) for a in accounts]


@router.post("/accounts", response_model=MarketplaceAccountResponse)
async def create_marketplace_account(
    account: MarketplaceAccountCreate,
    db: Session = Depends(get_db),
):
    service = OrderService(db)
    created = service.create_account(account.model_dump())
    return MarketplaceAccountResponse.from_orm(created)


@router.patch("/accounts/{account_id}", response_model=MarketplaceAccountResponse)
async def update_marketplace_account(
    account_id: int,
    updates: MarketplaceAccountUpdate,
    db: Session = Depends(get_db),
):
    service = OrderService(db)
    updated = service.update_account(account_id, updates.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Account not found")
    return MarketplaceAccountResponse.from_orm(updated)


@router.get("/", response_model=List[OrderResponse])
async def list_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    account_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    service = OrderService(db)
    orders = service.list_orders(skip=skip, limit=limit, account_id=account_id)
    return [OrderResponse.from_orm(o) for o in orders]


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int, db: Session = Depends(get_db)):
    service = OrderService(db)
    order = service.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return OrderResponse.from_orm(order)


@router.post("/accounts/{account_id}/sync")
async def sync_account_orders(account_id: int, since: str | None = Query(None), db: Session = Depends(get_db)):
    service = OrderService(db)
    count = await service.sync_orders(account_id, since_iso=since)
    return {"synced": count}


@router.post("/webhooks/{platform}/{account_id}")
async def handle_webhook(platform: str, account_id: int, request: Request, db: Session = Depends(get_db)):
    payload = await request.json()
    headers = dict(request.headers)
    service = OrderService(db)
    order_id = await service.handle_webhook(platform, account_id, payload, headers)
    return {"ok": True, "order_id": order_id}


