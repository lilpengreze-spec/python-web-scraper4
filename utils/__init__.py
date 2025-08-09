"""
🛠️ ENTERPRISE UTILS PACKAGE
============================

Professional utility modules supporting the enterprise scraper ecosystem.
Provides validation, analysis, helpers, and real scraping engine integration.

🔧 CORE MODULES:
   - helpers: Logging, formatting, user agents, enterprise headers
   - validators: Input validation for all supported platforms
   - review_analyzer: AI-powered review analysis and filtering
   - real_scraping_engine: Production scraping integration

Usage:
    from utils import ReviewAnalyzer, validate_amazon_input
    from utils import get_enhanced_user_agent, format_enterprise_response
    from utils import RealScrapingEngine
    
    # Validate inputs
    result = validate_amazon_input("B08N5WRWNW")
    
    # Analyze reviews
    analyzer = ReviewAnalyzer()
    insights = analyzer.get_review_insights(reviews)
    
    # Real scraping
    engine = RealScrapingEngine()
    data = engine.scrape_real_product_reviews(url)
"""

__version__ = "3.0.0"
__author__ = "Enterprise Scraping Solutions"
__license__ = "MIT"

# Helper functions
try:
    from .helpers import (
        setup_logging,
        format_response,
        format_enterprise_response,
        sanitize_text,
        clean_review_data,
        get_user_agent,
        get_enhanced_user_agent,
        create_enterprise_headers,
        rate_limit_delay,
        smart_rate_limit,
        detect_platform_from_url,
        is_valid_json,
        parse_date_string
    )
    HELPERS_AVAILABLE = True
except ImportError:
    HELPERS_AVAILABLE = False

# Validation functions
try:
    from .validators import (
        validate_yelp_input,
        validate_amazon_input,
        validate_walmart_input,
        validate_target_input,
        validate_platform_input,
        validate_refresh_interval,
        validate_url,
        validate_input
    )
    VALIDATORS_AVAILABLE = True
except ImportError:
    VALIDATORS_AVAILABLE = False

# Review analysis system
try:
    from .review_analyzer import (
        ReviewAnalyzer,
        ReviewFilter,
        create_filter_from_params,
        create_enterprise_filter,
        analyze_review_authenticity
    )
    REVIEW_ANALYZER_AVAILABLE = True
except ImportError:
    REVIEW_ANALYZER_AVAILABLE = False

# Real scraping engine
try:
    from .real_scraping_engine import (
        RealScrapingEngine,
        scrape_real_standing_desk_reviews,
        scrape_real_amazon_product,
        scrape_real_walmart_product
    )
    REAL_SCRAPING_AVAILABLE = True
except ImportError:
    REAL_SCRAPING_AVAILABLE = False

# Public API exports
__all__ = [
    # Helper functions
    'setup_logging',
    'format_response',
    'format_enterprise_response',
    'sanitize_text',
    'clean_review_data',
    'get_user_agent',
    'get_enhanced_user_agent',
    'create_enterprise_headers',
    'rate_limit_delay',
    'smart_rate_limit',
    'detect_platform_from_url',
    'is_valid_json',
    'parse_date_string',
    
    # Validation functions
    'validate_yelp_input',
    'validate_amazon_input',
    'validate_walmart_input',
    'validate_target_input',
    'validate_platform_input',
    'validate_refresh_interval',
    'validate_url',
    'validate_input',
    
    # Review analysis
    'ReviewAnalyzer',
    'ReviewFilter',
    'create_filter_from_params',
    'create_enterprise_filter',
    'analyze_review_authenticity',
    
    # Real scraping engine
    'RealScrapingEngine',
    'scrape_real_standing_desk_reviews',
    'scrape_real_amazon_product',
    'scrape_real_walmart_product',
    
    # Package info
    '__version__',
    '__author__',
    '__license__'
]

# Feature availability status
FEATURES = {
    'helpers': HELPERS_AVAILABLE,
    'validators': VALIDATORS_AVAILABLE,
    'review_analyzer': REVIEW_ANALYZER_AVAILABLE,
    'real_scraping_engine': REAL_SCRAPING_AVAILABLE
}

def get_available_utils():
    """
    Get list of available utility modules.
    
    Returns:
        Dict with utility module availability status
    """
    return FEATURES.copy()

def validate_platform_data(platform: str, data: str):
    """
    Convenience function to validate data for any platform.
    
    Args:
        platform: Platform name (amazon, walmart, yelp, target)
        data: Data to validate (ASIN, URL, business ID, etc.)
        
    Returns:
        Validation result dictionary
    """
    if not VALIDATORS_AVAILABLE:
        return {'valid': False, 'message': 'Validators module not available'}
    
    return validate_platform_input(platform, data)

def create_analyzer_for_platform(platform: str, keywords: list = None):
    """
    Create a pre-configured ReviewAnalyzer for a specific platform.
    
    Args:
        platform: Platform name
        keywords: Keywords to filter by
        
    Returns:
        Configured ReviewAnalyzer or None if not available
    """
    if not REVIEW_ANALYZER_AVAILABLE:
        return None
    
    analyzer = ReviewAnalyzer()
    if keywords:
        filter_config = create_enterprise_filter(platform, keywords)
        return analyzer, filter_config
    
    return analyzer

# Package initialization
def _show_utils_info():
    """Display utils package information on import"""
    available_count = sum(1 for available in FEATURES.values() if available)
    total_count = len(FEATURES)
    
    print(f"🛠️ Enterprise Utils v{__version__}")
    print(f"📦 {available_count}/{total_count} utility modules available")
    
    if REVIEW_ANALYZER_AVAILABLE:
        print("🧠 AI-powered review analysis system loaded")
    
    if REAL_SCRAPING_AVAILABLE:
        print("🚀 Real scraping engine integration ready")
    
    available_modules = [name for name, available in FEATURES.items() if available]
    if available_modules:
        print(f"⚡ Available: {', '.join(available_modules)}")

# Show info on import (can be disabled by setting UTILS_QUIET=1)
import os
if not os.getenv('UTILS_QUIET'):
    _show_utils_info()
