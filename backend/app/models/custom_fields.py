"""
Custom field models for user-specific data extraction
"""

from datetime import datetime
from sqlalchemy import Column, String, Text, Boolean, ForeignKey, JSON, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.models.base import BaseModel


class CustomFieldDefinition(BaseModel):
    """
    User-defined custom fields for data extraction
    """
    __tablename__ = "custom_field_definitions"
    
    # Field identification
    field_uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False, index=True)
    field_name = Column(String(100), nullable=False)  # e.g., "stok_kodu", "renk", "beden"
    field_label = Column(String(200), nullable=False)  # e.g., "Stok Kodu", "Renk", "Beden"
    field_type = Column(String(50), nullable=False)  # 'text', 'number', 'boolean', 'price', 'date'
    
    # Field configuration
    description = Column(Text, nullable=True)
    is_required = Column(Boolean, default=False, nullable=False)
    default_value = Column(Text, nullable=True)
    
    # Validation rules
    validation_rules = Column(JSON, nullable=True)  # e.g., {"min_length": 3, "max_length": 50, "pattern": "regex"}
    
    # Display configuration
    display_order = Column(Integer, default=0, nullable=False)
    is_searchable = Column(Boolean, default=True, nullable=False)
    is_exportable = Column(Boolean, default=True, nullable=False)
    
    # Access control
    created_by = Column(String, nullable=False, index=True)  # User UUID
    is_global = Column(Boolean, default=False, nullable=False)  # Available to all users
    
    def __repr__(self):
        return f"<CustomFieldDefinition(name='{self.field_name}', label='{self.field_label}')>"


class UserDataPreferences(BaseModel):
    """
    User preferences for data extraction per site
    """
    __tablename__ = "user_data_preferences"
    
    # User and site reference
    user_id = Column(String, nullable=False, index=True)  # User UUID
    site_id = Column(Integer, ForeignKey("sites.id"), nullable=False, index=True)
    
    # Standard field preferences
    extract_price = Column(Boolean, default=True, nullable=False)
    extract_stock_status = Column(Boolean, default=True, nullable=False)
    extract_stock_quantity = Column(Boolean, default=False, nullable=False)
    extract_product_name = Column(Boolean, default=True, nullable=False)
    extract_description = Column(Boolean, default=False, nullable=False)
    extract_images = Column(Boolean, default=False, nullable=False)
    extract_reviews = Column(Boolean, default=False, nullable=False)
    extract_rating = Column(Boolean, default=False, nullable=False)
    extract_brand = Column(Boolean, default=False, nullable=False)
    extract_model = Column(Boolean, default=False, nullable=False)
    extract_category = Column(Boolean, default=False, nullable=False)
    
    # Custom field preferences (JSON array of field UUIDs)
    enabled_custom_fields = Column(JSON, nullable=True)  # ["field_uuid1", "field_uuid2"]
    
    # Site-specific selectors (user can override default selectors)
    custom_selectors = Column(JSON, nullable=True)
    
    # Relationships
    site = relationship("Site")
    
    def __repr__(self):
        return f"<UserDataPreferences(user_id='{self.user_id}', site_id={self.site_id})>"


class CustomFieldMapping(BaseModel):
    """
    Mapping of custom fields to CSS selectors for specific sites
    """
    __tablename__ = "custom_field_mappings"
    
    # References
    field_id = Column(Integer, ForeignKey("custom_field_definitions.id"), nullable=False)
    site_id = Column(Integer, ForeignKey("sites.id"), nullable=False)
    user_id = Column(String, nullable=False, index=True)  # User who created the mapping
    
    # Selector configuration
    css_selector = Column(Text, nullable=False)
    attribute = Column(String(100), nullable=True)  # e.g., 'text', 'data-value', 'href'
    regex_pattern = Column(Text, nullable=True)  # Optional regex for text extraction
    
    # Processing configuration
    preprocessing_rules = Column(JSON, nullable=True)  # e.g., {"trim": true, "lowercase": true}
    
    # Validation
    is_tested = Column(Boolean, default=False, nullable=False)
    test_url = Column(Text, nullable=True)
    test_result = Column(Text, nullable=True)
    last_tested = Column(String, nullable=True)
    
    # Relationships
    field_definition = relationship("CustomFieldDefinition")
    site = relationship("Site")
    
    def __repr__(self):
        return f"<CustomFieldMapping(field_id={self.field_id}, site_id={self.site_id})>"


class ProductCustomData(BaseModel):
    """
    Store custom field data extracted for products
    """
    __tablename__ = "product_custom_data"
    
    # References
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    field_id = Column(Integer, ForeignKey("custom_field_definitions.id"), nullable=False)
    snapshot_id = Column(Integer, ForeignKey("product_snapshots.id"), nullable=False)
    
    # Data
    field_value = Column(Text, nullable=True)
    raw_value = Column(Text, nullable=True)  # Original extracted value before processing
    
    # Extraction metadata
    extraction_successful = Column(Boolean, default=True, nullable=False)
    extraction_error = Column(Text, nullable=True)
    
    # Relationships
    product = relationship("Product")
    field_definition = relationship("CustomFieldDefinition")
    snapshot = relationship("ProductSnapshot")
    
    def __repr__(self):
        return f"<ProductCustomData(product_id={self.product_id}, field_id={self.field_id})>"


