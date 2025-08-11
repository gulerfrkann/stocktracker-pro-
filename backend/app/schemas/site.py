"""
Site-related Pydantic schemas
"""

from decimal import Decimal
from typing import Optional, Dict, Any
from pydantic import BaseModel, HttpUrl


class SiteBase(BaseModel):
    name: str
    domain: str
    base_url: HttpUrl
    request_delay: Decimal = Decimal("1.0")
    use_javascript: bool = False
    requires_proxy: bool = False
    selectors: Optional[Dict[str, Any]] = None


class SiteCreate(SiteBase):
    pass


class SiteUpdate(BaseModel):
    name: Optional[str] = None
    domain: Optional[str] = None
    base_url: Optional[HttpUrl] = None
    request_delay: Optional[Decimal] = None
    use_javascript: Optional[bool] = None
    requires_proxy: Optional[bool] = None
    selectors: Optional[Dict[str, Any]] = None


class SiteResponse(SiteBase):
    id: int
    created_at: str
    updated_at: str
    is_active: bool

    class Config:
        from_attributes = True


