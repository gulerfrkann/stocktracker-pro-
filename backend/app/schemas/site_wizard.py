"""
Site wizard related Pydantic schemas
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, HttpUrl, validator


class SiteAnalysisRequest(BaseModel):
    url: HttpUrl


class SiteAnalysisResponse(BaseModel):
    domain: str
    site_name: str
    suggested_config: Dict[str, Any]
    suggested_selectors: Dict[str, List[str]]
    requires_javascript: bool
    analysis_successful: bool


class NewSiteConfig(BaseModel):
    name: str
    domain: str
    use_javascript: bool = True
    requires_proxy: bool = False
    request_delay: float = 2.0
    selectors: Dict[str, str]
    headers: Optional[Dict[str, str]] = None
    custom_logic: Optional[Dict[str, Any]] = None
    
    @validator('request_delay')
    def validate_delay(cls, v):
        if v < 0.5 or v > 10.0:
            raise ValueError('Request delay must be between 0.5 and 10.0 seconds')
        return v


class SiteTestRequest(BaseModel):
    domain: str
    test_url: HttpUrl
    config: NewSiteConfig


class SiteTestResponse(BaseModel):
    test_successful: bool
    extracted_data: Dict[str, Any]
    response_time_ms: Optional[int] = None
    issues: List[str] = []
    suggestions: List[str] = []
    http_status_code: Optional[int] = None


class SelectorSuggestion(BaseModel):
    selector: str
    confidence: float  # 0.0 - 1.0
    description: str


class SupportedSite(BaseModel):
    domain: str
    name: str
    type: str  # 'predefined' or 'dynamic'
    parser_available: bool


