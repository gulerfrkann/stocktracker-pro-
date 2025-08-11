"""
Alert service for managing price and stock alerts
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
import structlog

from app.models.product import Product, ProductSnapshot, Alert

logger = structlog.get_logger()


class AlertService:
    """
    Service for managing alerts and notifications
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    async def check_and_create_alerts(self, product: Product, snapshot: ProductSnapshot):
        """
        Check if new snapshot triggers any alerts and create them
        """
        try:
            # Check stock alerts
            await self._check_stock_alerts(product, snapshot)
            
            # Check price alerts
            await self._check_price_alerts(product, snapshot)
            
        except Exception as e:
            logger.error(
                "Failed to check alerts",
                product_id=product.id,
                error=str(e)
            )
    
    async def _check_stock_alerts(self, product: Product, snapshot: ProductSnapshot):
        """
        Check for stock-related alerts
        """
        if not product.track_stock or snapshot.is_in_stock is None:
            return
        
        # Get previous stock status
        previous_snapshot = self.db.query(ProductSnapshot).filter(
            and_(
                ProductSnapshot.product_id == product.id,
                ProductSnapshot.id < snapshot.id,
                ProductSnapshot.is_in_stock.isnot(None)
            )
        ).order_by(ProductSnapshot.created_at.desc()).first()
        
        # If no previous data, don't create alerts for first check
        if not previous_snapshot:
            return
        
        current_stock = snapshot.is_in_stock
        previous_stock = previous_snapshot.is_in_stock
        
        # Stock went out
        if previous_stock and not current_stock:
            await self._create_alert(
                product=product,
                alert_type="stock_out",
                snapshot=snapshot,
                message=f"Product '{product.name}' is now out of stock"
            )
        
        # Stock came back
        elif not previous_stock and current_stock:
            await self._create_alert(
                product=product,
                alert_type="stock_in",
                snapshot=snapshot,
                message=f"Product '{product.name}' is back in stock"
            )
    
    async def _check_price_alerts(self, product: Product, snapshot: ProductSnapshot):
        """
        Check for price-related alerts
        """
        if not product.track_price or snapshot.price is None:
            return
        
        current_price = snapshot.price
        
        # Check threshold alerts
        if product.min_price_threshold and current_price <= product.min_price_threshold:
            await self._create_alert(
                product=product,
                alert_type="price_drop",
                snapshot=snapshot,
                condition_value=product.min_price_threshold,
                trigger_value=current_price,
                message=f"Product '{product.name}' price dropped to {current_price} {snapshot.currency} (threshold: {product.min_price_threshold})"
            )
        
        if product.max_price_threshold and current_price >= product.max_price_threshold:
            await self._create_alert(
                product=product,
                alert_type="price_rise",
                snapshot=snapshot,
                condition_value=product.max_price_threshold,
                trigger_value=current_price,
                message=f"Product '{product.name}' price rose to {current_price} {snapshot.currency} (threshold: {product.max_price_threshold})"
            )
        
        # Check for significant price changes
        previous_snapshot = self.db.query(ProductSnapshot).filter(
            and_(
                ProductSnapshot.product_id == product.id,
                ProductSnapshot.id < snapshot.id,
                ProductSnapshot.price.isnot(None)
            )
        ).order_by(ProductSnapshot.created_at.desc()).first()
        
        if previous_snapshot and previous_snapshot.price:
            price_change_percent = float((current_price - previous_snapshot.price) / previous_snapshot.price * 100)
            
            # Alert for significant price drops (>10%)
            if price_change_percent <= -10:
                await self._create_alert(
                    product=product,
                    alert_type="price_drop",
                    snapshot=snapshot,
                    trigger_value=current_price,
                    message=f"Product '{product.name}' price dropped {abs(price_change_percent):.1f}% from {previous_snapshot.price} to {current_price} {snapshot.currency}"
                )
            
            # Alert for significant price increases (>20%)
            elif price_change_percent >= 20:
                await self._create_alert(
                    product=product,
                    alert_type="price_rise",
                    snapshot=snapshot,
                    trigger_value=current_price,
                    message=f"Product '{product.name}' price increased {price_change_percent:.1f}% from {previous_snapshot.price} to {current_price} {snapshot.currency}"
                )
    
    async def _create_alert(
        self,
        product: Product,
        alert_type: str,
        snapshot: ProductSnapshot,
        condition_value: Optional[Decimal] = None,
        trigger_value: Optional[Decimal] = None,
        message: str = None
    ):
        """
        Create a new alert
        """
        try:
            # Check if similar alert already exists recently (avoid spam)
            recent_alert = self.db.query(Alert).filter(
                and_(
                    Alert.product_id == product.id,
                    Alert.alert_type == alert_type,
                    Alert.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)  # Today
                )
            ).first()
            
            if recent_alert:
                logger.debug(
                    "Similar alert already exists today, skipping",
                    product_id=product.id,
                    alert_type=alert_type
                )
                return
            
            alert = Alert(
                product_id=product.id,
                alert_type=alert_type,
                condition_value=condition_value,
                triggered_at=datetime.utcnow(),
                trigger_value=trigger_value,
                trigger_snapshot_id=snapshot.id,
                message=message,
                notification_channels=["email"]  # Default to email
            )
            
            self.db.add(alert)
            self.db.commit()
            self.db.refresh(alert)
            
            logger.info(
                "Alert created",
                alert_id=alert.id,
                product_id=product.id,
                alert_type=alert_type,
                trigger_value=trigger_value
            )
            
            # Schedule notification sending
            # This would typically be handled by a background task
            # await self._schedule_notification(alert)
            
        except Exception as e:
            self.db.rollback()
            logger.error(
                "Failed to create alert",
                product_id=product.id,
                alert_type=alert_type,
                error=str(e)
            )
    
    def get_pending_alerts(self, limit: int = 100) -> List[Alert]:
        """
        Get alerts that haven't been sent yet
        """
        return self.db.query(Alert).filter(
            and_(
                Alert.is_sent == False,
                Alert.triggered_at.isnot(None),
                Alert.is_active == True
            )
        ).order_by(Alert.triggered_at.asc()).limit(limit).all()
    
    def mark_alert_sent(self, alert_id: int, success: bool = True):
        """
        Mark an alert as sent
        """
        try:
            alert = self.db.query(Alert).filter(Alert.id == alert_id).first()
            if alert:
                alert.is_sent = success
                alert.sent_at = datetime.utcnow() if success else None
                self.db.commit()
                
                logger.info("Alert marked as sent", alert_id=alert_id, success=success)
                
        except Exception as e:
            self.db.rollback()
            logger.error("Failed to mark alert as sent", alert_id=alert_id, error=str(e))
    
    def get_alert_stats(self, days: int = 7) -> dict:
        """
        Get alert statistics for the last N days
        """
        from datetime import timedelta
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        total_alerts = self.db.query(Alert).filter(
            Alert.created_at >= start_date
        ).count()
        
        sent_alerts = self.db.query(Alert).filter(
            and_(
                Alert.created_at >= start_date,
                Alert.is_sent == True
            )
        ).count()
        
        stock_alerts = self.db.query(Alert).filter(
            and_(
                Alert.created_at >= start_date,
                Alert.alert_type.in_(["stock_out", "stock_in"])
            )
        ).count()
        
        price_alerts = self.db.query(Alert).filter(
            and_(
                Alert.created_at >= start_date,
                Alert.alert_type.in_(["price_drop", "price_rise"])
            )
        ).count()
        
        return {
            'days': days,
            'total_alerts': total_alerts,
            'sent_alerts': sent_alerts,
            'pending_alerts': total_alerts - sent_alerts,
            'stock_alerts': stock_alerts,
            'price_alerts': price_alerts,
            'delivery_rate': (sent_alerts / total_alerts * 100) if total_alerts > 0 else 0
        }


