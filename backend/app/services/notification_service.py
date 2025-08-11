"""
Notification service to deliver order and alert events to channels (Email/Slack/Webhook)
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Dict, Any, Optional

from sqlalchemy.orm import Session
import structlog

from app.models.user import NotificationChannel

logger = structlog.get_logger()


class NotificationService:
    def __init__(self, db: Session):
        self.db = db

    def get_available_channels(self, user_uuid: Optional[str] = None) -> List[NotificationChannel]:
        query = self.db.query(NotificationChannel).filter(NotificationChannel.is_active == True)
        if user_uuid:
            query = query.filter((NotificationChannel.is_global == True) | (NotificationChannel.created_by == user_uuid))
        return query.order_by(NotificationChannel.created_at.desc()).all()

    def send(self, channel: NotificationChannel, subject: str, message: str, payload: Optional[Dict[str, Any]] = None) -> bool:
        """
        Placeholder send implementation. Extend with real email/slack/webhook logic.
        """
        try:
            logger.info(
                "Sending notification",
                channel_type=channel.channel_type,
                subject=subject,
            )
            # TODO: implement channel-specific senders
            return True
        except Exception as exc:
            logger.error("Notification send failed", error=str(exc))
            return False



