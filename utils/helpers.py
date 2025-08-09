"""
Helper Utilities

This module provides various utility functions for logging, formatting,
and other common operations.
"""

import os
import logging
import json
from datetime import datetime
from typing import Dict, Any, List, Optional


def setup_logging() -> None:
    """
    Setup logging configuration for the application.
    """
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Configure logging format
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Set log level based on environment
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format=log_format,
        datefmt=date_format,
        handlers=[
            # Console handler
            logging.StreamHandler(),
            # File handler
            logging.FileHandler(
                'logs/scraper.log',
                mode='a',
                encoding='utf-8'
            )
        ]
    )
    
    # Set third-party library log levels
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('bs4').setLevel(logging.WARNING)


def format_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format API response data for consistent output.
    
    Args:
        data: Raw response data
        
    Returns:
        Formatted response dictionary
    """
    if not isinstance(data, dict):
        return {
            'error': 'Invalid response data format',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
    
    # Ensure required fields exist
    formatted_data = {
        'timestamp': data.get('timestamp', datetime.utcnow().isoformat() + 'Z'),
        'status': data.get('status', 'unknown'),
        'yelp_reviews': data.get('yelp_reviews', []),
        'amazon_reviews': data.get('amazon_reviews', []),
        'walmart_reviews': data.get('walmart_reviews', []),
        'target_reviews': data.get('target_reviews', []),
        'universal_reviews': data.get('universal_reviews', []),
        'errors': data.get('errors', [])
    }
    
    # Calculate total reviews from all platforms
    total_reviews = (
        len(formatted_data['yelp_reviews']) + 
        len(formatted_data['amazon_reviews']) +
        len(formatted_data['walmart_reviews']) +
        len(formatted_data['target_reviews']) +
        len(formatted_data['universal_reviews'])
    )
    
    # Add statistics
    formatted_data['statistics'] = {
        'total_reviews': total_reviews,
        'yelp_review_count': len(formatted_data['yelp_reviews']),
        'amazon_review_count': len(formatted_data['amazon_reviews']),
        'walmart_review_count': len(formatted_data['walmart_reviews']),
        'target_review_count': len(formatted_data['target_reviews']),
        'universal_review_count': len(formatted_data['universal_reviews']),
        'has_errors': len(formatted_data['errors']) > 0
    }
    
    # Add metadata if available
    if 'background_scraping' in data:
        formatted_data['background_scraping'] = data['background_scraping']
    
    if 'refresh_interval' in data:
        formatted_data['refresh_interval'] = data['refresh_interval']
    
    if 'scraping_method' in data:
        formatted_data['scraping_method'] = data['scraping_method']
    
    if 'platforms_scraped' in data:
        formatted_data['platforms_scraped'] = data['platforms_scraped']
    
    return formatted_data


def sanitize_text(text: str) -> str:
    """
    Sanitize text content for safe output.
    
    Args:
        text: Text to sanitize
        
    Returns:
        Sanitized text
    """
    if not isinstance(text, str):
        return ""
    
    # Remove excessive whitespace
    text = ' '.join(text.split())
    
    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '&']
    for char in dangerous_chars:
        text = text.replace(char, '')
    
    # Limit length
    max_length = 5000
    if len(text) > max_length:
        text = text[:max_length] + '...'
    
    return text.strip()


def clean_review_data(reviews: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Clean and normalize review data with prominent links.
    
    Args:
        reviews: List of review dictionaries
        
    Returns:
        Cleaned review list with formatted links
    """
    cleaned_reviews = []
    
    for review in reviews:
        if not isinstance(review, dict):
            continue
        
        # Get review URL and create display link
        review_url = str(review.get('review_url', ''))
        platform = str(review.get('platform', review.get('source', 'unknown'))).lower()
        
        # Create a user-friendly link text
        if 'yelp' in platform:
            link_text = f"🔗 View on Yelp: {review_url}"
        elif 'amazon' in platform:
            link_text = f"🔗 View on Amazon: {review_url}"
        elif 'walmart' in platform:
            link_text = f"🔗 View on Walmart: {review_url}"
        elif 'target' in platform:
            link_text = f"🔗 View on Target: {review_url}"
        else:
            link_text = f"🔗 View Review: {review_url}"
        
        cleaned_review = {
            'reviewer_name': sanitize_text(str(review.get('reviewer_name', 'Anonymous'))),
            'rating': max(0, min(5, float(review.get('rating', 0)))),  # Ensure rating is 0-5
            'review_text': sanitize_text(str(review.get('review_text', ''))),
            'date': sanitize_text(str(review.get('date', ''))),
            'review_url': review_url,
            'review_link': link_text,
            'source': str(review.get('source', 'unknown')),
            'platform': str(review.get('platform', review.get('source', 'unknown')))
        }
        
        # Add star rating display
        star_count = int(cleaned_review['rating'])
        stars = '⭐' * star_count + '☆' * (5 - star_count)
        cleaned_review['star_display'] = f"{stars} ({cleaned_review['rating']}/5)"
        
        # Add additional fields if they exist
        if 'helpful_votes' in review:
            cleaned_review['helpful_votes'] = sanitize_text(str(review['helpful_votes']))
        
        # Only add reviews with meaningful content
        if cleaned_review['review_text'] or cleaned_review['rating'] > 0:
            cleaned_reviews.append(cleaned_review)
    
    return cleaned_reviews


def get_user_agent() -> str:
    """
    Get a random user agent string for web requests.
    (Legacy function - use get_enhanced_user_agent for better results)
    
    Returns:
        User agent string
    """
    return get_enhanced_user_agent()


def rate_limit_delay(min_delay: float = 1.0, max_delay: float = 3.0) -> None:
    """
    Add a random delay to avoid rate limiting.
    
    Args:
        min_delay: Minimum delay in seconds
        max_delay: Maximum delay in seconds
    """
    import time
    import random
    
    delay = random.uniform(min_delay, max_delay)
    time.sleep(delay)


def is_valid_json(json_str: str) -> bool:
    """
    Check if a string is valid JSON.
    
    Args:
        json_str: JSON string to validate
        
    Returns:
        True if valid JSON, False otherwise
    """
    try:
        json.loads(json_str)
        return True
    except (json.JSONDecodeError, TypeError):
        return False


def parse_date_string(date_str: str) -> Optional[str]:
    """
    Parse various date string formats and return ISO format.
    
    Args:
        date_str: Date string to parse
        
    Returns:
        ISO formatted date string or None if parsing fails
    """
    if not date_str:
        return None
    
    # Common date formats to try
    date_formats = [
        '%Y-%m-%d',
        '%m/%d/%Y',
        '%d/%m/%Y',
        '%B %d, %Y',
        '%b %d, %Y',
        '%Y-%m-%d %H:%M:%S',
        '%m/%d/%Y %H:%M:%S'
    ]
    
    for date_format in date_formats:
        try:
            parsed_date = datetime.strptime(date_str, date_format)
            return parsed_date.isoformat() + 'Z'
        except ValueError:
            continue
    
    # If no format matches, return the original string cleaned
    return sanitize_text(date_str)


def get_enhanced_user_agent() -> str:
    """
    Get an enhanced random user agent string for enterprise scraping.
    
    Returns:
        User agent string optimized for enterprise scraping
    """
    import random
    
    # Enterprise-grade user agents for better success rates
    user_agents = [
        # Chrome on Windows
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
        
        # Chrome on macOS
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        
        # Firefox on Windows
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:119.0) Gecko/20100101 Firefox/119.0',
        
        # Safari on macOS
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        
        # Edge on Windows
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
        
        # Mobile user agents for mobile-specific content
        'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (Android 14; Mobile; rv:120.0) Gecko/120.0 Firefox/120.0'
    ]
    
    return random.choice(user_agents)


def create_enterprise_headers(user_agent: str = None, referer: str = None) -> Dict[str, str]:
    """
    Create enterprise-grade HTTP headers for scraping.
    
    Args:
        user_agent: Custom user agent (optional)
        referer: Referer URL (optional)
        
    Returns:
        Dictionary of HTTP headers
    """
    import random
    
    headers = {
        'User-Agent': user_agent or get_enhanced_user_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': random.choice([
            'en-US,en;q=0.9',
            'en-US,en;q=0.9,es;q=0.8',
            'en-GB,en;q=0.9',
            'en-US,en;q=0.8,fr;q=0.6'
        ]),
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': random.choice(['none', 'same-origin', 'cross-site']),
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0'
    }
    
    if referer:
        headers['Referer'] = referer
    
    # Add random sec-ch headers for better fingerprinting
    headers['sec-ch-ua'] = random.choice([
        '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        '"Not_A Brand";v="8", "Chromium";v="119", "Google Chrome";v="119"',
        '"Chromium";v="120", "Not(A:Brand";v="24", "Google Chrome";v="120"'
    ])
    headers['sec-ch-ua-mobile'] = '?0'
    headers['sec-ch-ua-platform'] = random.choice(['"Windows"', '"macOS"', '"Linux"'])
    
    return headers


def smart_rate_limit(base_delay: float = 2.0, variance: float = 1.0, platform: str = None) -> None:
    """
    Intelligent rate limiting based on platform and current load.
    
    Args:
        base_delay: Base delay in seconds
        variance: Random variance to add
        platform: Platform name for specialized timing
    """
    import time
    import random
    
    # Platform-specific delays
    platform_delays = {
        'amazon': (2.0, 4.0),
        'walmart': (1.5, 3.0),
        'yelp': (1.0, 2.5),
        'target': (1.5, 3.0),
        'generic': (1.0, 2.0)
    }
    
    if platform and platform.lower() in platform_delays:
        min_delay, max_delay = platform_delays[platform.lower()]
    else:
        min_delay = base_delay
        max_delay = base_delay + variance
    
    # Add some randomization
    delay = random.uniform(min_delay, max_delay)
    time.sleep(delay)


def detect_platform_from_url(url: str) -> str:
    """
    Detect the platform/website from a URL.
    
    Args:
        url: URL to analyze
        
    Returns:
        Platform name
    """
    if not url:
        return 'unknown'
    
    url_lower = url.lower()
    
    # E-commerce platforms
    if 'amazon.' in url_lower:
        return 'amazon'
    elif 'walmart.com' in url_lower:
        return 'walmart'
    elif 'target.com' in url_lower:
        return 'target'
    elif 'bestbuy.com' in url_lower:
        return 'bestbuy'
    elif 'ebay.com' in url_lower:
        return 'ebay'
    elif 'costco.com' in url_lower:
        return 'costco'
    elif 'homedepot.com' in url_lower:
        return 'homedepot'
    elif 'lowes.com' in url_lower:
        return 'lowes'
    
    # Review platforms
    elif 'yelp.com' in url_lower:
        return 'yelp'
    elif 'tripadvisor.com' in url_lower:
        return 'tripadvisor'
    elif 'trustpilot.com' in url_lower:
        return 'trustpilot'
    elif 'glassdoor.com' in url_lower:
        return 'glassdoor'
    
    # Social commerce
    elif 'etsy.com' in url_lower:
        return 'etsy'
    elif 'facebook.com' in url_lower or 'fb.com' in url_lower:
        return 'facebook'
    
    else:
        return 'generic'


def format_enterprise_response(data: Dict[str, Any], platform: str = None, scraping_method: str = None) -> Dict[str, Any]:
    """
    Format enterprise response with enhanced metadata.
    
    Args:
        data: Raw response data
        platform: Platform name
        scraping_method: Method used for scraping
        
    Returns:
        Enhanced formatted response
    """
    response = format_response(data)
    
    # Add enterprise metadata
    response['enterprise_metadata'] = {
        'platform': platform or detect_platform_from_url(data.get('url', '')),
        'scraping_method': scraping_method or 'enhanced',
        'extraction_timestamp': datetime.utcnow().isoformat() + 'Z',
        'api_version': '3.0',
        'enterprise_features': {
            'anti_bot_bypass': True,
            'ai_analysis': True,
            'real_time_extraction': True,
            'enterprise_logging': True
        }
    }
    
    return response
