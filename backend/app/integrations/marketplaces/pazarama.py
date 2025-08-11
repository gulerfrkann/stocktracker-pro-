from typing import List, Dict, Any, Optional


class PazaramaAdapter:
    platform = "pazarama"

    async def fetch_orders(self, account_credentials: Dict[str, Any], since_iso: Optional[str] = None) -> List[Dict[str, Any]]:
        return []

    async def parse_webhook(self, payload: Dict[str, Any], headers: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return None



