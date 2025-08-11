"""
Marketplace adapters normalize order data from different platforms.
Define a common interface: fetch_orders, parse_webhook.
"""

from typing import List, Dict, Any, Optional, Protocol


class MarketplaceAdapter(Protocol):
    platform: str

    async def fetch_orders(self, account_credentials: Dict[str, Any], since_iso: Optional[str] = None) -> List[Dict[str, Any]]:
        ...

    async def parse_webhook(self, payload: Dict[str, Any], headers: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        ...



