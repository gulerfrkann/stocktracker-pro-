"""
Job-related Pydantic schemas
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class JobCreate(BaseModel):
    job_type: str
    product_ids: List[int]
    scheduled_at: Optional[datetime] = None


class JobResponse(BaseModel):
    id: int
    job_uuid: str
    job_type: str
    product_ids: List[int]
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: str
    progress: int
    total_products: int
    successful_scrapes: int
    failed_scrapes: int
    error_message: Optional[str] = None
    retry_count: int
    max_retries: int
    avg_scrape_time_ms: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


