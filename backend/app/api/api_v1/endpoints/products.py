"""
Product management endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.core.database import get_db
from app.models.product import Product, Site, ProductSnapshot
from app.services.product_service import ProductService
from app.schemas.product import (
    ProductCreate, ProductUpdate, ProductResponse, ProductListResponse,
    ProductSnapshotResponse
)

router = APIRouter()


@router.get("/", response_model=ProductListResponse)
async def get_products(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    site_id: Optional[int] = Query(None, description="Filter by site ID"),
    category: Optional[str] = Query(None, description="Filter by category"),
    in_stock: Optional[bool] = Query(None, description="Filter by stock status"),
    search: Optional[str] = Query(None, description="Search in product name or SKU"),
    db: Session = Depends(get_db)
):
    """
    Get products with filtering and pagination
    """
    query = db.query(Product).filter(Product.is_active == True)
    
    # Apply filters
    if site_id:
        query = query.filter(Product.site_id == site_id)
    
    if category:
        query = query.filter(Product.category.ilike(f"%{category}%"))
    
    if in_stock is not None:
        query = query.filter(Product.is_in_stock == in_stock)
    
    if search:
        search_filter = or_(
            Product.name.ilike(f"%{search}%"),
            Product.sku.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    products = query.offset(skip).limit(limit).all()
    
    return ProductListResponse(
        products=[ProductResponse.from_orm(p) for p in products],
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific product by ID
    """
    product = db.query(Product).filter(
        and_(Product.id == product_id, Product.is_active == True)
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return ProductResponse.from_orm(product)


@router.post("/", response_model=ProductResponse)
async def create_product(
    product_data: ProductCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Create a new product for tracking
    """
    # Check if site exists
    site = db.query(Site).filter(Site.id == product_data.site_id).first()
    if not site:
        raise HTTPException(status_code=400, detail="Site not found")
    
    # Create product
    product_service = ProductService(db)
    product = await product_service.create_product(product_data)
    
    # Schedule initial scrape
    background_tasks.add_task(
        product_service.schedule_initial_scrape, 
        product.id
    )
    
    return ProductResponse.from_orm(product)


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a product
    """
    product = db.query(Product).filter(
        and_(Product.id == product_id, Product.is_active == True)
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product_service = ProductService(db)
    updated_product = await product_service.update_product(product, product_data)
    
    return ProductResponse.from_orm(updated_product)


@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    """
    Soft delete a product (mark as inactive)
    """
    product = db.query(Product).filter(
        and_(Product.id == product_id, Product.is_active == True)
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product.is_active = False
    db.commit()
    
    return {"message": "Product deleted successfully"}


@router.get("/{product_id}/snapshots", response_model=List[ProductSnapshotResponse])
async def get_product_snapshots(
    product_id: int,
    limit: int = Query(100, ge=1, le=1000, description="Number of snapshots to return"),
    db: Session = Depends(get_db)
):
    """
    Get historical price and stock data for a product
    """
    # Check if product exists
    product = db.query(Product).filter(
        and_(Product.id == product_id, Product.is_active == True)
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get snapshots
    snapshots = db.query(ProductSnapshot).filter(
        ProductSnapshot.product_id == product_id
    ).order_by(ProductSnapshot.created_at.desc()).limit(limit).all()
    
    return [ProductSnapshotResponse.from_orm(snapshot) for snapshot in snapshots]


@router.post("/{product_id}/scrape")
async def trigger_product_scrape(
    product_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Manually trigger a scrape for a specific product
    """
    product = db.query(Product).filter(
        and_(Product.id == product_id, Product.is_active == True)
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product_service = ProductService(db)
    
    # Schedule scrape
    background_tasks.add_task(
        product_service.scrape_single_product,
        product_id
    )
    
    return {"message": "Scrape job scheduled", "product_id": product_id}


@router.get("/{product_id}/price-history")
async def get_price_history(
    product_id: int,
    days: int = Query(30, ge=1, le=365, description="Number of days to look back"),
    db: Session = Depends(get_db)
):
    """
    Get price history for charts and analysis
    """
    from datetime import datetime, timedelta
    
    # Check if product exists
    product = db.query(Product).filter(
        and_(Product.id == product_id, Product.is_active == True)
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get price history
    start_date = datetime.utcnow() - timedelta(days=days)
    
    snapshots = db.query(ProductSnapshot).filter(
        and_(
            ProductSnapshot.product_id == product_id,
            ProductSnapshot.created_at >= start_date,
            ProductSnapshot.price.isnot(None)
        )
    ).order_by(ProductSnapshot.created_at.asc()).all()
    
    # Format for charts
    price_data = [
        {
            "timestamp": snapshot.created_at.isoformat(),
            "price": float(snapshot.price) if snapshot.price else None,
            "is_in_stock": snapshot.is_in_stock,
            "currency": snapshot.currency
        }
        for snapshot in snapshots
    ]
    
    return {
        "product_id": product_id,
        "product_name": product.name,
        "currency": product.current_currency,
        "days": days,
        "data_points": len(price_data),
        "price_history": price_data
    }


