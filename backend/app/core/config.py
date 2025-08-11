"""
Configuration settings for StockTracker Pro
"""

import secrets
from typing import List, Optional, Union
from pydantic import validator, AnyHttpUrl
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Project Info
    PROJECT_NAME: str = "StockTracker Pro"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # Database
    DATABASE_URL: Optional[str] = None
    
    @validator("DATABASE_URL", pre=True)
    def assemble_db_connection(cls, v: Optional[str]) -> str:
        if v:
            return v
        return "postgresql://stocktracker_user:stocktracker_pass@localhost:5432/stocktracker"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",  # React dev
        "http://localhost:8000",  # FastAPI docs
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Email Settings
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None
    
    # Scraping Settings
    DEFAULT_REQUEST_DELAY: float = 1.0  # seconds between requests
    MAX_CONCURRENT_SCRAPERS: int = 5
    REQUEST_TIMEOUT: int = 30  # seconds
    MAX_RETRIES: int = 3
    
    # Playwright Settings
    BROWSER_HEADLESS: bool = True
    BROWSER_TIMEOUT: int = 30000  # milliseconds
    
    # Proxy Settings
    USE_PROXY_ROTATION: bool = False
    PROXY_LIST_URL: Optional[str] = None
    
    # Celery Settings
    CELERY_BROKER_URL: str = REDIS_URL
    CELERY_RESULT_BACKEND: str = REDIS_URL
    
    # File Storage
    EXPORT_DIR: str = "exports"
    MAX_EXPORT_AGE_DAYS: int = 7
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    ENVIRONMENT: str = "development"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
