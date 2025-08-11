"""
Alert-related Pydantic schemas
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel


class AlertResponse(BaseModel):
    id: int
    alert_uuid: str
    product_id: int
    alert_type: str
    condition_value: Optional[Decimal] = None
    triggered_at: Optional[datetime] = None
    trigger_value: Optional[Decimal] = None
    is_sent: bool
    sent_at: Optional[datetime] = None
    notification_channels: Optional[List[str]] = None
    message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


