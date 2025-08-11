"""
Alert management endpoints
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.product import Alert
from app.schemas.alert import AlertResponse

router = APIRouter()


@router.get("/", response_model=List[AlertResponse])
async def get_alerts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    alert_type: str = Query(None, description="Filter by alert type"),
    is_sent: bool = Query(None, description="Filter by sent status"),
    db: Session = Depends(get_db)
):
    """
    Get alerts with filtering
    """
    query = db.query(Alert).filter(Alert.is_active == True)
    
    if alert_type:
        query = query.filter(Alert.alert_type == alert_type)
    
    if is_sent is not None:
        query = query.filter(Alert.is_sent == is_sent)
    
    alerts = query.order_by(Alert.created_at.desc()).offset(skip).limit(limit).all()
    
    return [AlertResponse.from_orm(alert) for alert in alerts]


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific alert by ID
    """
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return AlertResponse.from_orm(alert)

