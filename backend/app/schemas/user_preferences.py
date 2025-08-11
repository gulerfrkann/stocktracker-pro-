"""
User preferences related Pydantic schemas
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, validator


class CustomFieldCreate(BaseModel):
    field_name: str
    field_label: str
    field_type: str  # 'text', 'number', 'boolean', 'price', 'date'
    description: Optional[str] = None
    is_required: bool = False
    default_value: Optional[str] = None
    validation_rules: Optional[Dict[str, Any]] = None
    display_order: int = 0
    is_searchable: bool = True
    is_exportable: bool = True
    is_global: bool = False
    
    @validator('field_type')
    def validate_field_type(cls, v):
        allowed_types = ['text', 'number', 'boolean', 'price', 'date']
        if v not in allowed_types:
            raise ValueError(f'field_type must be one of: {allowed_types}')
        return v
    
    @validator('field_name')
    def validate_field_name(cls, v):
        # Only allow alphanumeric and underscore
        import re
        if not re.match(r'^[a-z0-9_]+$', v):
            raise ValueError('field_name can only contain lowercase letters, numbers, and underscores')
        return v


class CustomFieldResponse(BaseModel):
    id: int
    field_uuid: str
    field_name: str
    field_label: str
    field_type: str
    description: Optional[str] = None
    is_required: bool
    default_value: Optional[str] = None
    validation_rules: Optional[Dict[str, Any]] = None
    display_order: int
    is_searchable: bool
    is_exportable: bool
    is_global: bool
    created_by: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserPreferencesCreate(BaseModel):
    site_id: int
    
    # Standard field preferences
    extract_price: bool = True
    extract_stock_status: bool = True
    extract_stock_quantity: bool = False
    extract_product_name: bool = True
    extract_description: bool = False
    extract_images: bool = False
    extract_reviews: bool = False
    extract_rating: bool = False
    extract_brand: bool = False
    extract_model: bool = False
    extract_category: bool = False
    
    # Custom field preferences
    enabled_custom_fields: Optional[List[str]] = None  # List of field UUIDs
    
    # Site-specific selectors override
    custom_selectors: Optional[Dict[str, str]] = None


class UserPreferencesResponse(BaseModel):
    id: int
    user_id: str
    site_id: int
    
    # Standard field preferences
    extract_price: bool
    extract_stock_status: bool
    extract_stock_quantity: bool
    extract_product_name: bool
    extract_description: bool
    extract_images: bool
    extract_reviews: bool
    extract_rating: bool
    extract_brand: bool
    extract_model: bool
    extract_category: bool
    
    # Custom field preferences
    enabled_custom_fields: Optional[List[str]] = None
    custom_selectors: Optional[Dict[str, str]] = None
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class FieldMappingCreate(BaseModel):
    field_id: int
    site_id: int
    css_selector: str
    attribute: str = 'text'  # 'text', 'data-value', 'href', etc.
    regex_pattern: Optional[str] = None
    preprocessing_rules: Optional[Dict[str, Any]] = None
    test_url: Optional[str] = None


class FieldMappingResponse(BaseModel):
    id: int
    field_id: int
    site_id: int
    user_id: str
    css_selector: str
    attribute: str
    regex_pattern: Optional[str] = None
    preprocessing_rules: Optional[Dict[str, Any]] = None
    is_tested: bool
    test_url: Optional[str] = None
    test_result: Optional[str] = None
    last_tested: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class FieldTemplateResponse(BaseModel):
    field_name: str
    field_label: str
    field_type: str
    description: str
    suggested_selectors: List[str]


class CustomFieldValueResponse(BaseModel):
    field_name: str
    field_label: str
    field_type: str
    raw_value: Optional[str] = None
    processed_value: Optional[str] = None
    extraction_successful: bool
    error_message: Optional[str] = None


class ProductWithCustomData(BaseModel):
    """
    Product response with custom field data
    """
    id: int
    name: str
    url: str
    current_price: Optional[float] = None
    is_in_stock: Optional[bool] = None
    
    # Standard fields based on user preferences
    stock_quantity: Optional[int] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    category: Optional[str] = None
    rating: Optional[float] = None
    
    # Custom fields data
    custom_fields: List[CustomFieldValueResponse] = []
    
    last_checked: Optional[datetime] = None
    
    class Config:
        from_attributes = True


