"""
Site management endpoints
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.product import Site
from app.schemas.site import SiteCreate, SiteUpdate, SiteResponse

router = APIRouter()


@router.get("/", response_model=List[SiteResponse])
async def get_sites(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all e-commerce sites (active and inactive)
    """
    sites = db.query(Site).order_by(Site.created_at.desc()).offset(skip).limit(limit).all()
    return [SiteResponse.from_orm(site) for site in sites]


@router.post("/", response_model=SiteResponse)
async def create_site(
    site_data: SiteCreate,
    db: Session = Depends(get_db)
):
    """
    Add a new e-commerce site for scraping
    """
    # Check if domain already exists
    existing_site = db.query(Site).filter(Site.domain == site_data.domain).first()
    if existing_site:
        raise HTTPException(status_code=400, detail="Site with this domain already exists")
    
    site = Site(**site_data.dict())
    db.add(site)
    db.commit()
    db.refresh(site)
    
    return SiteResponse.from_orm(site)


@router.get("/{site_id}", response_model=SiteResponse)
async def get_site(
    site_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific site by ID
    """
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    
    return SiteResponse.from_orm(site)


@router.put("/{site_id}", response_model=SiteResponse)
async def update_site(
    site_id: int,
    site_data: SiteUpdate,
    db: Session = Depends(get_db)
):
    """
    Update site configuration
    """
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    
    for field, value in site_data.dict(exclude_unset=True).items():
        setattr(site, field, value)
    
    db.commit()
    db.refresh(site)
    
    return SiteResponse.from_orm(site)

