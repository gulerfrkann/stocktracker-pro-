"""
User management models
"""

from sqlalchemy import Column, String, Boolean, DateTime, JSON, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.models.base import BaseModel


class User(BaseModel):
    """
    User accounts with role-based access
    """
    __tablename__ = "users"
    
    # User identification
    user_uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=True, index=True)
    
    # Authentication
    hashed_password = Column(String(255), nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Profile
    full_name = Column(String(200), nullable=True)
    department = Column(String(100), nullable=True, index=True)
    role = Column(String(50), default="viewer", nullable=False, index=True)  # 'admin', 'operator', 'viewer'
    
    # Account status
    is_superuser = Column(Boolean, default=False, nullable=False)
    last_login = Column(DateTime, nullable=True)
    
    # Preferences
    notification_preferences = Column(JSON, nullable=True)  # Email, Slack preferences
    timezone = Column(String(50), default="UTC", nullable=False)
    language = Column(String(10), default="tr", nullable=False)
    
    # API access
    api_key = Column(String(255), nullable=True, unique=True, index=True)
    api_key_expires = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<User(email='{self.email}', role='{self.role}')>"


class UserSession(BaseModel):
    """
    User sessions for tracking active logins
    """
    __tablename__ = "user_sessions"
    
    # Session identification
    session_uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)  # Reference to User.user_uuid
    
    # Session data
    access_token = Column(String(500), nullable=False, unique=True, index=True)
    refresh_token = Column(String(500), nullable=True, unique=True, index=True)
    expires_at = Column(DateTime, nullable=False, index=True)
    
    # Client information
    ip_address = Column(String(45), nullable=True)  # IPv6 support
    user_agent = Column(Text, nullable=True)
    device_type = Column(String(50), nullable=True)  # 'web', 'mobile', 'api'
    
    # Status
    is_revoked = Column(Boolean, default=False, nullable=False, index=True)
    revoked_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<UserSession(user_id='{self.user_id}', expires_at={self.expires_at})>"


class NotificationChannel(BaseModel):
    """
    Notification channels (Email, Slack, Webhooks)
    """
    __tablename__ = "notification_channels"
    
    # Channel identification
    channel_uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    
    # Channel type and configuration
    channel_type = Column(String(50), nullable=False, index=True)  # 'email', 'slack', 'webhook', 'teams'
    configuration = Column(JSON, nullable=False)  # Channel-specific config
    
    # Access control
    created_by = Column(String, nullable=False, index=True)  # Reference to User.user_uuid
    is_global = Column(Boolean, default=False, nullable=False)  # Available to all users
    
    # Status
    is_verified = Column(Boolean, default=False, nullable=False)
    last_test_at = Column(DateTime, nullable=True)
    test_status = Column(String(20), nullable=True)  # 'success', 'failed'
    
    def __repr__(self):
        return f"<NotificationChannel(name='{self.name}', type='{self.channel_type}')>"


