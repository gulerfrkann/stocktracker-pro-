"""
Custom field data extractor
"""

import re
from typing import Dict, Any, List, Optional, Union
from decimal import Decimal
from datetime import datetime
from dataclasses import dataclass
import structlog

logger = structlog.get_logger()


@dataclass
class CustomFieldResult:
    """
    Result of custom field extraction
    """
    field_name: str
    field_type: str
    raw_value: Optional[str] = None
    processed_value: Optional[Union[str, int, float, bool, Decimal]] = None
    extraction_successful: bool = True
    error_message: Optional[str] = None


class CustomFieldExtractor:
    """
    Extract custom fields from HTML using user-defined selectors
    """
    
    def __init__(self):
        self.logger = logger.bind(component="custom_extractor")
    
    def extract_custom_fields(
        self, 
        parser, 
        soup, 
        custom_field_mappings: List[Dict[str, Any]],
        user_preferences: Dict[str, bool]
    ) -> List[CustomFieldResult]:
        """
        Extract all custom fields based on user mappings and preferences
        
        Args:
            parser: selectolax parser (if available)
            soup: BeautifulSoup parser (fallback)
            custom_field_mappings: List of field mapping configurations
            user_preferences: User's data extraction preferences
            
        Returns:
            List of CustomFieldResult objects
        """
        results = []
        
        for mapping in custom_field_mappings:
            field_name = mapping['field_name']
            
            # Check if user wants this field extracted
            if not user_preferences.get(f'extract_{field_name}', True):
                continue
            
            try:
                result = self._extract_single_field(parser, soup, mapping)
                results.append(result)
                
            except Exception as e:
                error_result = CustomFieldResult(
                    field_name=field_name,
                    field_type=mapping['field_type'],
                    extraction_successful=False,
                    error_message=str(e)
                )
                results.append(error_result)
                
                self.logger.warning(
                    "Custom field extraction failed",
                    field_name=field_name,
                    error=str(e)
                )
        
        return results
    
    def _extract_single_field(
        self, 
        parser, 
        soup, 
        mapping: Dict[str, Any]
    ) -> CustomFieldResult:
        """
        Extract a single custom field
        """
        field_name = mapping['field_name']
        field_type = mapping['field_type']
        css_selector = mapping['css_selector']
        attribute = mapping.get('attribute', 'text')
        regex_pattern = mapping.get('regex_pattern')
        preprocessing_rules = mapping.get('preprocessing_rules', {})
        
        # Extract raw value
        raw_value = self._extract_raw_value(parser, soup, css_selector, attribute)
        
        if raw_value is None:
            return CustomFieldResult(
                field_name=field_name,
                field_type=field_type,
                extraction_successful=False,
                error_message="Element not found or empty"
            )
        
        # Apply regex if provided
        if regex_pattern:
            match = re.search(regex_pattern, raw_value)
            if match:
                raw_value = match.group(1) if match.groups() else match.group(0)
            else:
                return CustomFieldResult(
                    field_name=field_name,
                    field_type=field_type,
                    raw_value=raw_value,
                    extraction_successful=False,
                    error_message=f"Regex pattern '{regex_pattern}' did not match"
                )
        
        # Apply preprocessing
        processed_value = self._preprocess_value(raw_value, preprocessing_rules)
        
        # Type conversion
        final_value = self._convert_to_type(processed_value, field_type)
        
        return CustomFieldResult(
            field_name=field_name,
            field_type=field_type,
            raw_value=raw_value,
            processed_value=final_value,
            extraction_successful=True
        )
    
    def _extract_raw_value(self, parser, soup, css_selector: str, attribute: str) -> Optional[str]:
        """
        Extract raw text value using CSS selector
        """
        try:
            if parser:
                element = parser.css_first(css_selector)
                if element:
                    if attribute == 'text':
                        return element.text()
                    else:
                        return element.attributes.get(attribute)
            else:
                element = soup.select_one(css_selector)
                if element:
                    if attribute == 'text':
                        return element.get_text().strip()
                    else:
                        return element.get(attribute)
            
            return None
            
        except Exception as e:
            self.logger.warning(
                "Raw value extraction failed",
                selector=css_selector,
                attribute=attribute,
                error=str(e)
            )
            return None
    
    def _preprocess_value(self, value: str, rules: Dict[str, Any]) -> str:
        """
        Apply preprocessing rules to extracted value
        """
        if not value:
            return value
        
        processed = value
        
        # Trim whitespace
        if rules.get('trim', True):
            processed = processed.strip()
        
        # Convert case
        if rules.get('lowercase'):
            processed = processed.lower()
        elif rules.get('uppercase'):
            processed = processed.upper()
        elif rules.get('title_case'):
            processed = processed.title()
        
        # Remove extra whitespace
        if rules.get('normalize_whitespace', True):
            processed = re.sub(r'\s+', ' ', processed)
        
        # Remove specific characters
        remove_chars = rules.get('remove_chars')
        if remove_chars:
            for char in remove_chars:
                processed = processed.replace(char, '')
        
        # Replace characters
        replacements = rules.get('replacements', {})
        for old, new in replacements.items():
            processed = processed.replace(old, new)
        
        # Extract numbers only
        if rules.get('numbers_only'):
            processed = re.sub(r'[^\d.,]', '', processed)
        
        # Extract text only (remove numbers and symbols)
        if rules.get('text_only'):
            processed = re.sub(r'[^\w\s]', '', processed)
        
        return processed
    
    def _convert_to_type(self, value: str, field_type: str) -> Union[str, int, float, bool, Decimal, None]:
        """
        Convert string value to appropriate type
        """
        if not value:
            return None
        
        try:
            if field_type == 'text':
                return str(value)
            
            elif field_type == 'number':
                # Try to parse as number
                cleaned = re.sub(r'[^\d.,]', '', value)
                if ',' in cleaned and '.' in cleaned:
                    # Handle Turkish format: 1.234,56
                    if cleaned.rindex(',') > cleaned.rindex('.'):
                        cleaned = cleaned.replace('.', '').replace(',', '.')
                    else:
                        cleaned = cleaned.replace(',', '')
                elif ',' in cleaned:
                    # Could be decimal separator
                    parts = cleaned.split(',')
                    if len(parts) == 2 and len(parts[1]) <= 2:
                        cleaned = cleaned.replace(',', '.')
                    else:
                        cleaned = cleaned.replace(',', '')
                
                if '.' in cleaned:
                    return float(cleaned)
                else:
                    return int(cleaned)
            
            elif field_type == 'price':
                # Similar to number but return as Decimal
                cleaned = re.sub(r'[^\d.,]', '', value)
                if ',' in cleaned and '.' in cleaned:
                    if cleaned.rindex(',') > cleaned.rindex('.'):
                        cleaned = cleaned.replace('.', '').replace(',', '.')
                    else:
                        cleaned = cleaned.replace(',', '')
                elif ',' in cleaned:
                    parts = cleaned.split(',')
                    if len(parts) == 2 and len(parts[1]) <= 2:
                        cleaned = cleaned.replace(',', '.')
                    else:
                        cleaned = cleaned.replace(',', '')
                
                return Decimal(cleaned)
            
            elif field_type == 'boolean':
                # Check for boolean indicators
                true_values = ['true', '1', 'yes', 'var', 'evet', 'mevcut', 'active']
                false_values = ['false', '0', 'no', 'yok', 'hayır', 'inactive']
                
                value_lower = value.lower()
                
                if any(true_val in value_lower for true_val in true_values):
                    return True
                elif any(false_val in value_lower for false_val in false_values):
                    return False
                else:
                    # If unclear, return None
                    return None
            
            elif field_type == 'date':
                # Try to parse date (basic implementation)
                from dateutil import parser as date_parser
                try:
                    parsed_date = date_parser.parse(value)
                    return parsed_date.isoformat()
                except:
                    return value  # Return as string if parsing fails
            
            else:
                return str(value)
                
        except Exception as e:
            self.logger.warning(
                "Type conversion failed",
                value=value,
                field_type=field_type,
                error=str(e)
            )
            return str(value)  # Fallback to string


# Common custom field templates
COMMON_CUSTOM_FIELDS = {
    'stok_kodu': {
        'field_name': 'stok_kodu',
        'field_label': 'Stok Kodu',
        'field_type': 'text',
        'description': 'Ürünün mağaza stok kodu',
        'common_selectors': [
            '.sku, .stock-code, .product-sku',
            '[data-sku], [data-stock-code]',
            '.model-code, .item-code'
        ]
    },
    
    'renk': {
        'field_name': 'renk',
        'field_label': 'Renk',
        'field_type': 'text',
        'description': 'Ürün rengi',
        'common_selectors': [
            '.color, .colour, .renk',
            '.variant-color, .product-color',
            '[data-color], [data-variant]'
        ]
    },
    
    'beden': {
        'field_name': 'beden',
        'field_label': 'Beden/Boyut',
        'field_type': 'text',
        'description': 'Ürün bedeni veya boyutu',
        'common_selectors': [
            '.size, .beden, .boyut',
            '.variant-size, .product-size',
            '[data-size], [data-beden]'
        ]
    },
    
    'marka': {
        'field_name': 'marka',
        'field_label': 'Marka',
        'field_type': 'text',
        'description': 'Ürün markası',
        'common_selectors': [
            '.brand, .marka, .manufacturer',
            '.product-brand, .brand-name',
            '[data-brand], [data-manufacturer]'
        ]
    },
    
    'model': {
        'field_name': 'model',
        'field_label': 'Model',
        'field_type': 'text',
        'description': 'Ürün modeli',
        'common_selectors': [
            '.model, .model-name, .product-model',
            '[data-model], [data-model-name]'
        ]
    },
    
    'indirim_orani': {
        'field_name': 'indirim_orani',
        'field_label': 'İndirim Oranı',
        'field_type': 'number',
        'description': 'İndirim yüzdesi',
        'common_selectors': [
            '.discount, .discount-rate, .sale-percent',
            '.indirim, .indirim-orani',
            '[data-discount], [data-sale-percent]'
        ]
    },
    
    'kargo_ucreti': {
        'field_name': 'kargo_ucreti',
        'field_label': 'Kargo Ücreti',
        'field_type': 'price',
        'description': 'Kargo maliyeti',
        'common_selectors': [
            '.shipping-cost, .cargo-fee, .delivery-fee',
            '.kargo-ucret, .teslimat-ucret',
            '[data-shipping], [data-delivery]'
        ]
    },
    
    'teslimat_suresi': {
        'field_name': 'teslimat_suresi',
        'field_label': 'Teslimat Süresi',
        'field_type': 'text',
        'description': 'Tahmini teslimat süresi',
        'common_selectors': [
            '.delivery-time, .shipping-time, .teslimat-sure',
            '.cargo-info, .delivery-info',
            '[data-delivery-time], [data-shipping-time]'
        ]
    }
}


