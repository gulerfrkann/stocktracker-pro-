from typing import List, Dict, Any, Optional
import base64
from datetime import datetime, timedelta, timezone

import httpx


class TrendyolAdapter:
    platform = "trendyol"

    BASE_URL = "https://api.trendyol.com/sapigw"

    def _build_headers(self, api_key: str, api_secret: str, user_agent: str) -> Dict[str, str]:
        token = base64.b64encode(f"{api_key}:{api_secret}".encode("utf-8")).decode("ascii")
        return {
            "Authorization": f"Basic {token}",
            "User-Agent": user_agent or "StockTrackerPro/Orders",
            "Accept": "application/json",
        }

    def _epoch_ms(self, dt: datetime) -> int:
        return int(dt.timestamp() * 1000)

    def _to_datetime(self, epoch_ms: Optional[int]) -> Optional[datetime]:
        if not epoch_ms:
            return None
        return datetime.fromtimestamp(epoch_ms / 1000, tz=timezone.utc)

    def _normalize_order(self, order: Dict[str, Any]) -> Dict[str, Any]:
        # Buyer info
        first_name = order.get("customerFirstName") or order.get("customerFirstName", "")
        last_name = order.get("customerLastName") or order.get("customerLastName", "")
        buyer_name = (f"{first_name} {last_name}").strip() or None

        # Amounts
        total_amount = (
            order.get("totalPrice")
            or order.get("totalAmount")
            or order.get("grossAmount")
        )
        currency = order.get("currencyCode") or order.get("currency") or "TRY"

        # Dates
        placed_at = self._to_datetime(order.get("orderDate") or order.get("createDate"))
        paid_at = self._to_datetime(order.get("paymentDate"))
        shipped_at = self._to_datetime(order.get("shipmentDate"))

        # Items
        items_raw = order.get("lines") or order.get("items") or []
        items: List[Dict[str, Any]] = []
        for it in items_raw:
            quantity = it.get("quantity") or it.get("amount") or 1
            unit_price = it.get("price") or it.get("salePrice")
            line_total = it.get("totalPrice") or (
                (unit_price or 0) * (quantity or 1)
            )
            items.append(
                {
                    "external_product_id": str(it.get("productId") or it.get("barcode") or it.get("sku") or ""),
                    "sku": it.get("sku") or it.get("barcode"),
                    "product_name": it.get("productName") or it.get("name") or "",
                    "product_url": None,
                    "quantity": int(quantity or 1),
                    "unit_price": unit_price,
                    "line_total": line_total,
                    "currency": currency,
                }
            )

        # Addresses
        shipping_address = order.get("shipmentAddress") or order.get("shippingAddress")
        billing_address = order.get("billingAddress")

        normalized = {
            "external_order_id": str(order.get("orderNumber") or order.get("id") or order.get("number")),
            "buyer_name": buyer_name,
            "buyer_email": order.get("customerEmail"),
            "buyer_phone": order.get("customerPhone") or order.get("customerPhoneNumber"),
            "shipping_address": shipping_address,
            "billing_address": billing_address,
            "total_amount": total_amount,
            "currency": currency,
            "shipment_cost": order.get("shipmentPrice") or order.get("cargoPrice"),
            "discount_total": order.get("discount") or order.get("totalDiscount"),
            "order_status": order.get("status") or order.get("orderStatus"),
            "payment_status": order.get("paymentStatus"),
            "fulfillment_status": order.get("fulfillmentStatus"),
            "placed_at": placed_at,
            "paid_at": paid_at,
            "shipped_at": shipped_at,
            "items": items,
        }
        return normalized

    async def fetch_orders(self, account_credentials: Dict[str, Any], since_iso: Optional[str] = None) -> List[Dict[str, Any]]:
        supplier_id = account_credentials.get("supplierId") or account_credentials.get("supplier_id")
        api_key = account_credentials.get("apiKey")
        api_secret = account_credentials.get("apiSecret")
        user_agent = account_credentials.get("userAgent") or "StockTrackerPro/Orders"

        if not (supplier_id and api_key and api_secret):
            return []

        headers = self._build_headers(api_key, api_secret, user_agent)

        # Time window
        if since_iso:
            try:
                since_dt = datetime.fromisoformat(since_iso.replace("Z", "+00:00"))
            except Exception:
                since_dt = datetime.now(timezone.utc) - timedelta(days=1)
        else:
            since_dt = datetime.now(timezone.utc) - timedelta(days=1)

        params = {
            "size": 200,
            "startDate": self._epoch_ms(since_dt),
            "orderByField": "PackageLastModifiedDate",
            "orderByDirection": "DESC",
        }

        url = f"{self.BASE_URL}/suppliers/{supplier_id}/orders"
        results: List[Dict[str, Any]] = []

        async with httpx.AsyncClient(timeout=30) as client:
            page = 0
            while True:
                page_params = {**params, "page": page}
                resp = await client.get(url, headers=headers, params=page_params)
                if resp.status_code == 401:
                    # Invalid credentials
                    break
                resp.raise_for_status()
                data = resp.json()
                content = data.get("content")
                if content is None:
                    # Fallback keys
                    content = data.get("orders") or data.get("items") or []
                if not content:
                    break
                for raw in content:
                    try:
                        normalized = self._normalize_order(raw)
                        results.append(normalized)
                    except Exception:
                        continue
                # Stop if last page
                if data.get("last") is True:
                    break
                page += 1

        return results

    async def parse_webhook(self, payload: Dict[str, Any], headers: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        # Trendyol webhook doğrulaması projeye göre eklenecek
        if not isinstance(payload, dict):
            return None
        # If payload resembles an order
        candidate = payload.get("order") or payload
        if candidate.get("orderNumber") or candidate.get("id"):
            try:
                return self._normalize_order(candidate)
            except Exception:
                return None
        return None


