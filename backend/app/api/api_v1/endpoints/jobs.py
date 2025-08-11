"""
Scraping job management endpoints
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.product import ScrapingJob
from app.schemas.job import JobResponse, JobCreate

router = APIRouter()


@router.get("/", response_model=List[JobResponse])
async def get_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: str = Query(None, description="Filter by job status"),
    db: Session = Depends(get_db)
):
    """
    Get scraping jobs with filtering
    """
    query = db.query(ScrapingJob).filter(ScrapingJob.is_active == True)
    
    if status:
        query = query.filter(ScrapingJob.status == status)
    
    jobs = query.order_by(ScrapingJob.created_at.desc()).offset(skip).limit(limit).all()
    
    return [JobResponse.from_orm(job) for job in jobs]


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific scraping job by ID
    """
    job = db.query(ScrapingJob).filter(ScrapingJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return JobResponse.from_orm(job)


@router.post("/", response_model=JobResponse)
async def create_job(
    job_data: JobCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Create and schedule a new scraping job
    """
    job = ScrapingJob(
        job_type=job_data.job_type,
        product_ids=job_data.product_ids,
        total_products=len(job_data.product_ids),
        scheduled_at=job_data.scheduled_at
    )
    
    db.add(job)
    db.commit()
    db.refresh(job)
    
    # Schedule the job
    from app.services.scraping_service import ScrapingService
    scraping_service = ScrapingService(db)
    
    background_tasks.add_task(
        scraping_service.execute_job,
        job.id
    )
    
    return JobResponse.from_orm(job)


