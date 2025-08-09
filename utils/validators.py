"""
Input Validation Utilities

This module provides validation functions for user inputs to ensure
data integrity and security.
"""

import re
from typing import Dict, Any, Union
from urllib.parse import urlparse


def validate_yelp_input(input_str: str) -> Dict[str, Union[bool, str]]:
    """
    Validate Yelp business ID or URL.
    
    Args:
        input_str: Yelp business ID or URL to validate
        
    Returns:
        Dictionary with validation result and message
    """
    if not input_str or not isinstance(input_str, str):
        return {'valid': False, 'message': 'Yelp input must be a non-empty string'}
    
    input_str = input_str.strip()
    
    # Check if it's a URL
    if input_str.startswith('http'):
        try:
            parsed = urlparse(input_str)
            if 'yelp.com' not in parsed.netloc:
                return {'valid': False, 'message': 'URL must be from yelp.com domain'}
            
            if '/biz/' not in parsed.path:
                return {'valid': False, 'message': 'Yelp URL must contain /biz/ path'}
            
            return {'valid': True, 'message': 'Valid Yelp URL'}
            
        except Exception:
            return {'valid': False, 'message': 'Invalid URL format'}
    
    # Check if it's a business ID (alphanumeric, hyphens, underscores)
    if re.match(r'^[a-zA-Z0-9_-]+$', input_str):
        if len(input_str) < 3 or len(input_str) > 100:
            return {'valid': False, 'message': 'Yelp business ID must be 3-100 characters'}
        return {'valid': True, 'message': 'Valid Yelp business ID'}
    
    return {'valid': False, 'message': 'Invalid Yelp business ID format'}


def validate_walmart_input(input_str: str) -> Dict[str, Union[bool, str]]:
    """
    Validate Walmart product ID or URL.
    
    Args:
        input_str: Walmart product ID or URL to validate
        
    Returns:
        Dictionary with validation result and message
    """
    if not input_str or not isinstance(input_str, str):
        return {'valid': False, 'message': 'Walmart input must be a non-empty string'}
    
    input_str = input_str.strip()
    
    # Check if it's a URL
    if input_str.startswith('http'):
        try:
            parsed = urlparse(input_str)
            if 'walmart.com' not in parsed.netloc:
                return {'valid': False, 'message': 'URL must be from walmart.com domain'}
            
            if '/ip/' not in parsed.path:
                return {'valid': False, 'message': 'Walmart URL must contain /ip/ path'}
            
            return {'valid': True, 'message': 'Valid Walmart URL'}
            
        except Exception:
            return {'valid': False, 'message': 'Invalid URL format'}
    
    # Check if it's a product ID (numeric)
    if re.match(r'^\d+$', input_str):
        if len(input_str) < 3 or len(input_str) > 20:
            return {'valid': False, 'message': 'Walmart product ID must be 3-20 digits'}
        return {'valid': True, 'message': 'Valid Walmart product ID'}
    
    return {'valid': False, 'message': 'Invalid Walmart product ID format'}


def validate_target_input(input_str: str) -> Dict[str, Union[bool, str]]:
    """
    Validate Target product DPCI or URL.
    
    Args:
        input_str: Target product DPCI or URL to validate
        
    Returns:
        Dictionary with validation result and message
    """
    if not input_str or not isinstance(input_str, str):
        return {'valid': False, 'message': 'Target input must be a non-empty string'}
    
    input_str = input_str.strip()
    
    # Check if it's a URL
    if input_str.startswith('http'):
        try:
            parsed = urlparse(input_str)
            if 'target.com' not in parsed.netloc:
                return {'valid': False, 'message': 'URL must be from target.com domain'}
            
            if '/p/' not in parsed.path:
                return {'valid': False, 'message': 'Target URL must contain /p/ path'}
            
            return {'valid': True, 'message': 'Valid Target URL'}
            
        except Exception:
            return {'valid': False, 'message': 'Invalid URL format'}
    
    # Check if it's a DPCI (XXX-XX-XXXX format)
    if re.match(r'^\d{3}-\d{2}-\d{4}$', input_str):
        return {'valid': True, 'message': 'Valid Target DPCI'}
    
    # Check if it's a numeric product ID
    if re.match(r'^\d+$', input_str):
        if len(input_str) < 3 or len(input_str) > 20:
            return {'valid': False, 'message': 'Target product ID must be 3-20 digits'}
        return {'valid': True, 'message': 'Valid Target product ID'}
    
    return {'valid': False, 'message': 'Invalid Target product ID format'}


def validate_platform_input(platform: str, input_str: str) -> Dict[str, Union[bool, str]]:
    """
    Validate input based on platform type.
    
    Args:
        platform: Platform name (amazon, walmart, yelp, target, etc.)
        input_str: Input string to validate
        
    Returns:
        Dictionary with validation result and message
    """
    platform = platform.lower() if platform else ''
    
    if platform == 'amazon':
        return validate_amazon_input(input_str)
    elif platform == 'walmart':
        return validate_walmart_input(input_str)
    elif platform == 'yelp':
        return validate_yelp_input(input_str)
    elif platform == 'target':
        return validate_target_input(input_str)
    elif platform in ['generic', 'universal', 'unknown']:
        return validate_url(input_str)
    else:
        return {'valid': False, 'message': f'Unsupported platform: {platform}'}


def validate_amazon_input(input_str: str) -> Dict[str, Union[bool, str]]:
    """
    Validate Amazon ASIN or URL.
    
    Args:
        input_str: Amazon ASIN or URL to validate
        
    Returns:
        Dictionary with validation result and message
    """
    if not input_str or not isinstance(input_str, str):
        return {'valid': False, 'message': 'Amazon input must be a non-empty string'}
    
    input_str = input_str.strip()
    
    # Check if it's a URL
    if input_str.startswith('http'):
        try:
            parsed = urlparse(input_str)
            if 'amazon.' not in parsed.netloc:
                return {'valid': False, 'message': 'URL must be from Amazon domain'}
            
            # Look for ASIN in URL
            asin_patterns = [
                r'/dp/([A-Z0-9]{10})',
                r'/product/([A-Z0-9]{10})',
                r'/ASIN/([A-Z0-9]{10})',
                r'asin=([A-Z0-9]{10})'
            ]
            
            found_asin = False
            for pattern in asin_patterns:
                if re.search(pattern, input_str, re.IGNORECASE):
                    found_asin = True
                    break
            
            if not found_asin:
                return {'valid': False, 'message': 'Amazon URL must contain a valid ASIN'}
            
            return {'valid': True, 'message': 'Valid Amazon URL'}
            
        except Exception:
            return {'valid': False, 'message': 'Invalid URL format'}
    
    # Check if it's an ASIN (10 alphanumeric characters)
    if re.match(r'^[A-Z0-9]{10}$', input_str.upper()):
        return {'valid': True, 'message': 'Valid Amazon ASIN'}
    
    return {'valid': False, 'message': 'Invalid Amazon ASIN format (must be 10 alphanumeric characters)'}


def validate_refresh_interval(interval: Any) -> Dict[str, Union[bool, str]]:
    """
    Validate refresh interval.
    
    Args:
        interval: Refresh interval in seconds
        
    Returns:
        Dictionary with validation result and message
    """
    if interval is None:
        return {'valid': True, 'message': 'No refresh interval specified'}
    
    if not isinstance(interval, (int, float)):
        try:
            interval = float(interval)
        except (ValueError, TypeError):
            return {'valid': False, 'message': 'Refresh interval must be a number'}
    
    if interval <= 0:
        return {'valid': False, 'message': 'Refresh interval must be positive'}
    
    if interval < 60:
        return {'valid': False, 'message': 'Refresh interval must be at least 60 seconds to avoid rate limiting'}
    
    if interval > 86400:  # 24 hours
        return {'valid': False, 'message': 'Refresh interval cannot exceed 24 hours'}
    
    return {'valid': True, 'message': 'Valid refresh interval'}


def validate_url(url: str) -> Dict[str, Union[bool, str]]:
    """
    Validate a general URL.
    
    Args:
        url: URL to validate
        
    Returns:
        Dictionary with validation result and message
    """
    if not url or not isinstance(url, str):
        return {'valid': False, 'error': 'URL must be a non-empty string'}
    
    url = url.strip()
    
    if not url.startswith(('http://', 'https://')):
        return {'valid': False, 'error': 'URL must start with http:// or https://'}
    
    try:
        parsed = urlparse(url)
        if not parsed.netloc:
            return {'valid': False, 'error': 'Invalid URL format - missing domain'}
        return {'valid': True, 'message': 'Valid URL'}
    except Exception:
        return {'valid': False, 'error': 'Invalid URL format'}


def validate_input(data: Dict[str, Any]) -> Dict[str, Union[bool, str]]:
    """
    Validate complete input data for scraping request.
    
    Args:
        data: Dictionary containing request data
        
    Returns:
        Dictionary with validation result and message
    """
    if not isinstance(data, dict):
        return {'valid': False, 'message': 'Request data must be a JSON object'}
    
    # Get all possible inputs
    yelp_input = data.get('yelp_business_id', '')
    amazon_input = data.get('amazon_asin', '')
    walmart_input = data.get('walmart_product_id', '')
    target_input = data.get('target_product_id', '')
    url_input = data.get('url', '')
    refresh_interval = data.get('refresh_interval')
    
    # Count valid inputs
    valid_inputs = 0
    if yelp_input:
        valid_inputs += 1
    if amazon_input:
        valid_inputs += 1
    if walmart_input:
        valid_inputs += 1
    if target_input:
        valid_inputs += 1
    if url_input:
        valid_inputs += 1
    
    # At least one input must be provided
    if valid_inputs == 0:
        return {
            'valid': False, 
            'message': 'At least one of yelp_business_id, amazon_asin, walmart_product_id, target_product_id, or url must be provided'
        }
    
    # Validate each input if provided
    if yelp_input:
        yelp_validation = validate_yelp_input(yelp_input)
        if not yelp_validation['valid']:
            return {'valid': False, 'message': f"Yelp validation error: {yelp_validation['message']}"}
    
    if amazon_input:
        amazon_validation = validate_amazon_input(amazon_input)
        if not amazon_validation['valid']:
            return {'valid': False, 'message': f"Amazon validation error: {amazon_validation['message']}"}
    
    if walmart_input:
        walmart_validation = validate_walmart_input(walmart_input)
        if not walmart_validation['valid']:
            return {'valid': False, 'message': f"Walmart validation error: {walmart_validation['message']}"}
    
    if target_input:
        target_validation = validate_target_input(target_input)
        if not target_validation['valid']:
            return {'valid': False, 'message': f"Target validation error: {target_validation['message']}"}
    
    if url_input:
        url_validation = validate_url(url_input)
        if not url_validation['valid']:
            return {'valid': False, 'message': f"URL validation error: {url_validation.get('error', 'Invalid URL')}"}
    
    # Validate refresh interval if provided
    if refresh_interval is not None:
        interval_validation = validate_refresh_interval(refresh_interval)
        if not interval_validation['valid']:
            return {'valid': False, 'message': f"Refresh interval error: {interval_validation['message']}"}
    
    return {'valid': True, 'message': 'All inputs are valid'}
