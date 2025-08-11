"""
User data extraction preferences endpoints
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.custom_fields import (
    CustomFieldDefinition, UserDataPreferences, 
    CustomFieldMapping, ProductCustomData
)
from app.models.product import Site
from app.schemas.user_preferences import (
    CustomFieldCreate, CustomFieldResponse, 
    UserPreferencesCreate, UserPreferencesResponse,
    FieldMappingCreate, FieldMappingResponse,
    FieldTemplateResponse
)
from app.scraper.custom_extractor import COMMON_CUSTOM_FIELDS

router = APIRouter()


@router.post("/custom-fields", response_model=CustomFieldResponse)
async def create_custom_field(
    field_data: CustomFieldCreate,
    current_user_id: str = "test_user",  # TODO: Get from auth
    db: Session = Depends(get_db)
):
    """
    Create a new custom field definition
    """
    try:
        # Check if field name already exists for this user
        existing_field = db.query(CustomFieldDefinition).filter(
            CustomFieldDefinition.field_name == field_data.field_name,
            CustomFieldDefinition.created_by == current_user_id
        ).first()
        
        if existing_field:
            raise HTTPException(
                status_code=400,
                detail=f"Custom field '{field_data.field_name}' already exists"
            )
        
        custom_field = CustomFieldDefinition(
            **field_data.dict(),
            created_by=current_user_id
        )
        
        db.add(custom_field)
        db.commit()
        db.refresh(custom_field)
        
        return CustomFieldResponse.from_orm(custom_field)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create custom field: {str(e)}"
        )


@router.get("/custom-fields", response_model=List[CustomFieldResponse])
async def get_custom_fields(
    current_user_id: str = "test_user",  # TODO: Get from auth
    include_global: bool = Query(True, description="Include global fields"),
    db: Session = Depends(get_db)
):
    """
    Get user's custom field definitions
    """
    query = db.query(CustomFieldDefinition).filter(
        CustomFieldDefinition.is_active == True
    )
    
    if include_global:
        query = query.filter(
            (CustomFieldDefinition.created_by == current_user_id) |
            (CustomFieldDefinition.is_global == True)
        )
    else:
        query = query.filter(CustomFieldDefinition.created_by == current_user_id)
    
    fields = query.order_by(CustomFieldDefinition.display_order).all()
    
    return [CustomFieldResponse.from_orm(field) for field in fields]


@router.get("/field-templates", response_model=List[FieldTemplateResponse])
async def get_field_templates():
    """
    Get common field templates that users can quickly add
    """
    templates = []
    
    for field_name, template in COMMON_CUSTOM_FIELDS.items():
        templates.append(FieldTemplateResponse(
            field_name=template['field_name'],
            field_label=template['field_label'],
            field_type=template['field_type'],
            description=template['description'],
            suggested_selectors=template['common_selectors']
        ))
    
    return templates


@router.post("/site-preferences", response_model=UserPreferencesResponse)
async def set_site_preferences(
    preferences_data: UserPreferencesCreate,
    current_user_id: str = "test_user",  # TODO: Get from auth
    db: Session = Depends(get_db)
):
    """
    Set user's data extraction preferences for a site
    """
    try:
        # Check if site exists
        site = db.query(Site).filter(Site.id == preferences_data.site_id).first()
        if not site:
            raise HTTPException(status_code=404, detail="Site not found")
        
        # Check if preferences already exist
        existing_prefs = db.query(UserDataPreferences).filter(
            UserDataPreferences.user_id == current_user_id,
            UserDataPreferences.site_id == preferences_data.site_id
        ).first()
        
        if existing_prefs:
            # Update existing preferences
            for field, value in preferences_data.dict(exclude={'site_id'}).items():
                if value is not None:
                    setattr(existing_prefs, field, value)
            
            db.commit()
            db.refresh(existing_prefs)
            return UserPreferencesResponse.from_orm(existing_prefs)
        
        else:
            # Create new preferences
            preferences = UserDataPreferences(
                **preferences_data.dict(),
                user_id=current_user_id
            )
            
            db.add(preferences)
            db.commit()
            db.refresh(preferences)
            return UserPreferencesResponse.from_orm(preferences)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to set preferences: {str(e)}"
        )


@router.get("/site-preferences/{site_id}", response_model=UserPreferencesResponse)
async def get_site_preferences(
    site_id: int,
    current_user_id: str = "test_user",  # TODO: Get from auth
    db: Session = Depends(get_db)
):
    """
    Get user's data extraction preferences for a site
    """
    preferences = db.query(UserDataPreferences).filter(
        UserDataPreferences.user_id == current_user_id,
        UserDataPreferences.site_id == site_id
    ).first()
    
    if not preferences:
        # Return default preferences
        site = db.query(Site).filter(Site.id == site_id).first()
        if not site:
            raise HTTPException(status_code=404, detail="Site not found")
        
        # Create default preferences
        default_prefs = UserDataPreferences(
            user_id=current_user_id,
            site_id=site_id,
            # All standard fields enabled by default
            extract_price=True,
            extract_stock_status=True,
            extract_product_name=True
        )
        
        return UserPreferencesResponse.from_orm(default_prefs)
    
    return UserPreferencesResponse.from_orm(preferences)


@router.post("/field-mappings", response_model=FieldMappingResponse)
async def create_field_mapping(
    mapping_data: FieldMappingCreate,
    current_user_id: str = "test_user",  # TODO: Get from auth
    db: Session = Depends(get_db)
):
    """
    Create CSS selector mapping for a custom field
    """
    try:
        # Verify field and site exist
        field = db.query(CustomFieldDefinition).filter(
            CustomFieldDefinition.id == mapping_data.field_id
        ).first()
        if not field:
            raise HTTPException(status_code=404, detail="Custom field not found")
        
        site = db.query(Site).filter(Site.id == mapping_data.site_id).first()
        if not site:
            raise HTTPException(status_code=404, detail="Site not found")
        
        # Check if mapping already exists
        existing_mapping = db.query(CustomFieldMapping).filter(
            CustomFieldMapping.field_id == mapping_data.field_id,
            CustomFieldMapping.site_id == mapping_data.site_id,
            CustomFieldMapping.user_id == current_user_id
        ).first()
        
        if existing_mapping:
            # Update existing mapping
            for field_name, value in mapping_data.dict(exclude={'field_id', 'site_id'}).items():
                if value is not None:
                    setattr(existing_mapping, field_name, value)
            
            db.commit()
            db.refresh(existing_mapping)
            return FieldMappingResponse.from_orm(existing_mapping)
        
        else:
            # Create new mapping
            mapping = CustomFieldMapping(
                **mapping_data.dict(),
                user_id=current_user_id
            )
            
            db.add(mapping)
            db.commit()
            db.refresh(mapping)
            return FieldMappingResponse.from_orm(mapping)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create field mapping: {str(e)}"
        )


@router.get("/field-mappings/{site_id}", response_model=List[FieldMappingResponse])
async def get_field_mappings(
    site_id: int,
    current_user_id: str = "test_user",  # TODO: Get from auth
    db: Session = Depends(get_db)
):
    """
    Get all field mappings for a site
    """
    mappings = db.query(CustomFieldMapping).filter(
        CustomFieldMapping.site_id == site_id,
        CustomFieldMapping.user_id == current_user_id
    ).all()
    
    return [FieldMappingResponse.from_orm(mapping) for mapping in mappings]


@router.post("/test-field-mapping")
async def test_field_mapping(
    test_data: Dict[str, Any],
    current_user_id: str = "test_user"  # TODO: Get from auth
):
    """
    Test a field mapping against a URL
    """
    try:
        import httpx
        from app.scraper.custom_extractor import CustomFieldExtractor
        from bs4 import BeautifulSoup
        
        url = test_data['url']
        css_selector = test_data['css_selector']
        attribute = test_data.get('attribute', 'text')
        field_type = test_data.get('field_type', 'text')
        
        # Fetch page content
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )
            response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Test extraction
        extractor = CustomFieldExtractor()
        
        mapping = {
            'field_name': 'test_field',
            'field_type': field_type,
            'css_selector': css_selector,
            'attribute': attribute,
            'regex_pattern': test_data.get('regex_pattern'),
            'preprocessing_rules': test_data.get('preprocessing_rules', {})
        }
        
        result = extractor._extract_single_field(None, soup, mapping)
        
        return {
            'test_successful': result.extraction_successful,
            'raw_value': result.raw_value,
            'processed_value': result.processed_value,
            'error_message': result.error_message
        }
        
    except Exception as e:
        return {
            'test_successful': False,
            'error_message': str(e)
        }


@router.get("/extraction-stats/{site_id}")
async def get_extraction_stats(
    site_id: int,
    days: int = Query(7, ge=1, le=30),
    current_user_id: str = "test_user",  # TODO: Get from auth
    db: Session = Depends(get_db)
):
    """
    Get extraction statistics for custom fields
    """
    from datetime import datetime, timedelta
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Get extraction stats
    stats = db.query(ProductCustomData).join(CustomFieldDefinition).filter(
        ProductCustomData.created_at >= start_date,
        CustomFieldDefinition.created_by == current_user_id
    ).all()
    
    # Calculate statistics
    total_extractions = len(stats)
    successful_extractions = len([s for s in stats if s.extraction_successful])
    
    field_stats = {}
    for stat in stats:
        field_name = stat.field_definition.field_name
        if field_name not in field_stats:
            field_stats[field_name] = {'total': 0, 'successful': 0}
        
        field_stats[field_name]['total'] += 1
        if stat.extraction_successful:
            field_stats[field_name]['successful'] += 1
    
    return {
        'days': days,
        'total_extractions': total_extractions,
        'successful_extractions': successful_extractions,
        'success_rate': (successful_extractions / total_extractions * 100) if total_extractions > 0 else 0,
        'field_statistics': field_stats
    }


