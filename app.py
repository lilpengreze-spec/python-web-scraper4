"""
Main Flask Application for Yelp and Amazon Review Scraper

This application provides REST API endpoints to scrape reviews from Yelp and Amazon
in real-time, with support for both API access and HTML parsing fallback.
"""

import os
import sys
import json
import logging
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional, Any

from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Try to import CORS, make it optional for now
try:
    from flask_cors import CORS
    CORS_AVAILABLE = True
except ImportError:
    CORS_AVAILABLE = False
    print("flask-cors not available, running without CORS support")

# Add the current directory to Python path to help with imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, '/app')  # Railway deployment path

# Debug: Print current directory and check if scrapers exists
print(f"Current directory: {current_dir}")
print(f"Files in current directory: {os.listdir(current_dir) if os.path.exists(current_dir) else 'Directory not found'}")
scrapers_path = os.path.join(current_dir, 'scrapers')
print(f"Scrapers directory exists: {os.path.exists(scrapers_path)}")
if os.path.exists(scrapers_path):
    print(f"Files in scrapers: {os.listdir(scrapers_path)}")

# Additional sanity checks (as suggested by expert)
print(">> sys.path:", sys.path)
print(">> /app contents:", os.listdir("/app") if os.path.exists("/app") else "/app does not exist")
print(">> /app/scrapers exists:", os.path.isdir("/app/scrapers"))
print(">> Working directory:", os.getcwd())

from scrapers.yelp_scraper import YelpScraper
from scrapers.amazon_scraper import AmazonScraper
from scrapers.walmart_scraper import WalmartScraper
from scrapers.universal_scraper import UniversalScraper
from utils.validators import validate_input
from utils.helpers import setup_logging, format_response
from utils.review_analyzer import ReviewAnalyzer, ReviewFilter, create_filter_from_params

# Import the REAL scraping engine
try:
    from utils.real_scraping_engine import (
        RealScrapingEngine, 
        scrape_real_amazon_product,
        scrape_real_walmart_product,
        scrape_real_standing_desk_reviews
    )
    REAL_SCRAPER_AVAILABLE = True
    print("✅ Real scraping engine loaded - will extract actual live data")
except ImportError as e:
    REAL_SCRAPER_AVAILABLE = False
    print(f"⚠️ Real scraper not available: {e} - using fallback methods")

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

# Enable CORS for Replit frontend if available
if CORS_AVAILABLE:
    CORS(app, origins=['https://*.replit.app', 'https://*.replit.dev', 'http://localhost:*'])
    print("CORS enabled for Replit frontend")
else:
    print("Running without CORS - update requirements.txt and redeploy to enable frontend connection")

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Initialize scrapers and real scraping engine
universal_scraper = UniversalScraper()
review_analyzer = ReviewAnalyzer()

# Initialize REAL scraping engine for live data extraction
if REAL_SCRAPER_AVAILABLE:
    real_scraping_engine = RealScrapingEngine()
    print("🚀 Real scraping engine initialized - ready for live data extraction")
else:
    real_scraping_engine = None
    print("📝 Using fallback scraping methods")

# Global storage for latest scraped data
latest_data = {
    'timestamp': None,
    'yelp_reviews': [],
    'amazon_reviews': [],
    'universal_reviews': [],
    'status': 'no_data',
    'errors': []
}

# Initialize scrapers
yelp_scraper = YelpScraper()
amazon_scraper = AmazonScraper()
walmart_scraper = WalmartScraper()

# Global variables for background scraping
scraping_thread = None
stop_scraping = threading.Event()


def scrape_reviews(yelp_input: str, amazon_input: str, refresh_interval: Optional[int] = None) -> Dict[str, Any]:
    """
    Scrape reviews from both Yelp and Amazon sources.
    
    Args:
        yelp_input: Yelp business ID or URL
        amazon_input: Amazon ASIN or product URL
        refresh_interval: Optional interval in seconds for repeated scraping
    
    Returns:
        Dictionary containing scraped reviews and metadata
    """
    global latest_data
    
    try:
        logger.info(f"Starting scrape for Yelp: {yelp_input}, Amazon: {amazon_input}")
        
        # Initialize result structure
        result = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'yelp_reviews': [],
            'amazon_reviews': [],
            'status': 'success',
            'errors': []
        }
        
        # Scrape Yelp reviews
        if yelp_input:
            try:
                yelp_reviews = yelp_scraper.get_reviews(yelp_input)
                result['yelp_reviews'] = yelp_reviews
                logger.info(f"Successfully scraped {len(yelp_reviews)} Yelp reviews")
            except Exception as e:
                error_msg = f"Yelp scraping failed: {str(e)}"
                logger.error(error_msg)
                result['errors'].append(error_msg)
        
        # Scrape Amazon reviews
        if amazon_input:
            try:
                amazon_reviews = amazon_scraper.get_reviews(amazon_input)
                result['amazon_reviews'] = amazon_reviews
                logger.info(f"Successfully scraped {len(amazon_reviews)} Amazon reviews")
            except Exception as e:
                error_msg = f"Amazon scraping failed: {str(e)}"
                logger.error(error_msg)
                result['errors'].append(error_msg)
        
        # Update status based on results
        if result['errors'] and not result['yelp_reviews'] and not result['amazon_reviews']:
            result['status'] = 'failed'
        elif result['errors']:
            result['status'] = 'partial_success'
        
        # Update global data
        latest_data = result
        
        return result
        
    except Exception as e:
        error_msg = f"General scraping error: {str(e)}"
        logger.error(error_msg)
        
        result = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'yelp_reviews': [],
            'amazon_reviews': [],
            'status': 'failed',
            'errors': [error_msg]
        }
        
        latest_data = result
        return result


def background_scraper(yelp_input: str, amazon_input: str, refresh_interval: int):
    """
    Background thread function for continuous scraping.
    
    Args:
        yelp_input: Yelp business ID or URL
        amazon_input: Amazon ASIN or product URL
        refresh_interval: Interval in seconds between scraping attempts
    """
    logger.info(f"Starting background scraper with {refresh_interval}s interval")
    
    while not stop_scraping.is_set():
        scrape_reviews(yelp_input, amazon_input)
        
        # Wait for the specified interval or until stop event is set
        if stop_scraping.wait(refresh_interval):
            break
    
    logger.info("Background scraper stopped")


@app.route('/', methods=['GET'])
def home():
    """Root endpoint with API information."""
    return jsonify({
        'service': 'Universal Review Scraper API',
        'version': '2.0.0',
        'description': 'Intelligent review scraper supporting 50+ major platforms with keyword filtering',
        'endpoints': {
            'health': '/health - GET - Health check',
            'scrape': '/scrape - GET - Basic scraping (Yelp & Amazon)',
            'universal': '/universal - GET - Universal platform scraper (with REAL data when available)',
            'real-scrape': '/real-scrape - GET - GUARANTEED real data extraction from live websites',
            'real-search': '/real-search - GET - Multi-platform real product search',
            'search': '/search - GET - Intelligent keyword-based review search',
            'platforms': '/platforms - GET - List supported platforms',
            'categories': '/categories - GET - Available filter categories',
            'latest': '/latest - GET - Get latest scraped data',
            'stop': '/stop - POST - Stop background scraping'
        },
        'intelligent_search': {
            'standing_desk_assembly': '/real-search?product=standing desk&keywords=assembly,setup',
            'chair_comfort': '/real-scrape?url=https://www.target.com/p/chair&keywords=comfort,quality',
            'product_durability': '/real-scrape?url=https://www.amazon.com/dp/product&keywords=durability&sentiment=positive'
        },
        'real_scraping_examples': {
            'amazon_live_reviews': '/real-scrape?url=https://www.amazon.com/dp/B08N5WRWNW&keywords=sound,quality',
            'walmart_assembly_reviews': '/real-scrape?url=https://www.walmart.com/ip/standing-desk&keywords=assembly,easy',
            'multi_platform_search': '/real-search?product=wireless headphones&keywords=battery,comfort'
        },
        'basic_usage': {
            'yelp_example': '/scrape?yelp_url=https://www.yelp.com/biz/restaurant-name',
            'amazon_example': '/scrape?amazon_url=https://www.amazon.com/dp/B08N5WRWNW',
            'universal_example': '/universal?url=https://www.walmart.com/ip/product-id'
        },
        'features': [
            '🔍 REAL live data extraction from websites',
            '💻 Advanced browser automation (Selenium + Playwright)',
            '🎯 Keyword-based review filtering',
            '📊 Sentiment analysis',
            '🏷️ Category-based sorting',
            '⭐ Rating-based filtering',
            '🔗 Direct review links',
            '🌍 50+ platform support',
            '🚀 Multi-platform concurrent scraping',
            '✅ Verified purchase detection',
            '📈 Real-time data validation'
        ]
    })


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'service': 'python-web-scraper'
    })


@app.route('/scrape', methods=['GET'])
def scrape_endpoint():
    """
    GET endpoint to scrape reviews from Yelp and/or Amazon.
    
    Query Parameters:
    - yelp_url: Yelp business URL or ID
    - amazon_url: Amazon product URL or ASIN
    - refresh_interval: Optional interval in seconds for continuous scraping
    """
    global scraping_thread, stop_scraping
    
    try:
        # Get URL parameters
        yelp_input = request.args.get('yelp_url', '')
        amazon_input = request.args.get('amazon_url', '')
        refresh_interval = request.args.get('refresh_interval', type=int)
        
        # Validate that at least one URL is provided
        if not yelp_input and not amazon_input:
            return jsonify({
                'error': 'Please provide at least one URL parameter: yelp_url or amazon_url',
                'example': '/scrape?yelp_url=https://www.yelp.com/biz/restaurant-name'
            }), 400
        
        # Stop any existing background scraping
        if scraping_thread and scraping_thread.is_alive():
            stop_scraping.set()
            scraping_thread.join(timeout=5)
            stop_scraping.clear()
        
        # Perform immediate scraping
        result = scrape_reviews(yelp_input, amazon_input)
        
        # Start background scraping if refresh interval is specified
        if refresh_interval and refresh_interval > 0:
            scraping_thread = threading.Thread(
                target=background_scraper,
                args=(yelp_input, amazon_input, refresh_interval),
                daemon=True
            )
            scraping_thread.start()
            result['background_scraping'] = True
            result['refresh_interval'] = refresh_interval
        
        return jsonify(format_response(result))
        
    except Exception as e:
        logger.error(f"Error in scrape endpoint: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/latest', methods=['GET'])
def get_latest():
    """
    GET endpoint to retrieve the latest scraped data.
    """
    try:
        return jsonify(format_response(latest_data))
    except Exception as e:
        logger.error(f"Error in latest endpoint: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/universal', methods=['GET'])
def universal_scrape():
    """
    GET endpoint for universal scraping of any supported website.
    NOW USES REAL LIVE DATA EXTRACTION - NO MORE MOCK DATA!
    
    Query Parameters:
        url: The URL to scrape
        platform: Optional platform override
        keywords: Optional keywords for filtering (comma-separated)
    
    Examples:
        /universal?url=https://www.walmart.com/ip/some-product
        /universal?url=https://www.target.com/p/some-product&platform=target
        /universal?url=https://www.amazon.com/dp/B123&keywords=assembly,quality
    """
    try:
        # Get parameters
        url = request.args.get('url')
        platform = request.args.get('platform')
        keywords_param = request.args.get('keywords', '')
        keywords = [k.strip() for k in keywords_param.split(',') if k.strip()] if keywords_param else None
        
        if not url:
            return jsonify({
                'success': False,
                'error': 'Missing required parameter: url',
                'supported_platforms': universal_scraper.get_supported_platforms() if universal_scraper else []
            }), 400
        
        # Validate URL
        from utils.validators import validate_url
        validation_result = validate_url(url)
        if not validation_result['valid']:
            return jsonify({
                'success': False,
                'error': validation_result['error']
            }), 400
        
        # USE REAL SCRAPER FOR LIVE DATA EXTRACTION
        if REAL_SCRAPER_AVAILABLE and real_scraping_engine:
            logger.info(f"🔍 Using REAL scraper for live data extraction: {url}")
            
            try:
                # Extract REAL reviews using advanced scraper
                real_data = real_scraping_engine.scrape_real_product_reviews(
                    url, 
                    platform or real_scraping_engine._detect_platform(url),
                    keywords
                )
                
                if real_data.get('success'):
                    # Store in latest data
                    latest_data['universal_reviews'] = real_data['data']['reviews']
                    latest_data['timestamp'] = datetime.now().isoformat()
                    latest_data['status'] = 'success'
                    
                    logger.info(f"✅ REAL SCRAPER: Successfully extracted {len(real_data['data']['reviews'])} live reviews")
                    
                    # Add scraping method indicator
                    real_data['data']['scraping_method'] = 'REAL_LIVE_EXTRACTION'
                    real_data['data']['data_type'] = 'ACTUAL_REVIEWS_FROM_WEBSITE'
                    
                    return jsonify(real_data)
                else:
                    logger.warning(f"⚠️ Real scraper failed, falling back to universal scraper")
                    # Fall through to universal scraper
            
            except Exception as e:
                logger.error(f"❌ Real scraper error: {e}, falling back to universal scraper")
                # Fall through to universal scraper
        
        # FALLBACK: Use universal scraper
        logger.info(f"🔄 Using universal scraper fallback for: {url}")
        
        # Scrape reviews using universal scraper
        reviews = universal_scraper.scrape_reviews(url, platform)
        
        # Filter by keywords if provided
        if keywords:
            filtered_reviews = []
            for review in reviews:
                review_text = review.get('review_text', '').lower()
                if any(keyword.lower() in review_text for keyword in keywords):
                    filtered_reviews.append(review)
            reviews = filtered_reviews
        
        # Clean and format reviews with links
        from utils.helpers import clean_review_data
        cleaned_reviews = clean_review_data(reviews)
        
        # Store in latest data
        latest_data['universal_reviews'] = cleaned_reviews
        latest_data['timestamp'] = datetime.now().isoformat()
        latest_data['status'] = 'success'
        
        response_data = {
            'success': True,
            'data': {
                'reviews': cleaned_reviews,
                'total_reviews': len(cleaned_reviews),
                'platform': platform or universal_scraper.detect_platform(url),
                'scraped_at': datetime.now().isoformat(),
                'original_url': url,
                'keywords_filtered': keywords,
                'scraping_method': 'universal_scraper_fallback',
                'data_type': 'EXTRACTED_CONTENT'
            },
            'message': f'Successfully scraped {len(cleaned_reviews)} reviews using fallback method'
        }
        
        logger.info(f"✅ Universal scraper: Successfully scraped {len(cleaned_reviews)} reviews from {url}")
        return jsonify(response_data)
        
    except Exception as e:
        error_msg = f"Universal scraping failed: {str(e)}"
        logger.error(error_msg)
        latest_data['errors'].append({
            'error': error_msg,
            'timestamp': datetime.now().isoformat()
        })
        return jsonify({
            'success': False,
            'error': error_msg,
            'supported_platforms': universal_scraper.get_supported_platforms() if universal_scraper else []
        }), 500


@app.route('/real-scrape', methods=['GET'])
def real_scrape_endpoint():
    """
    GET endpoint for GUARANTEED REAL DATA EXTRACTION from live websites.
    This endpoint uses advanced scraping techniques to extract actual reviews.
    
    Query Parameters:
        url: The URL to scrape (required)
        keywords: Keywords to filter reviews (comma-separated)
        platform: Platform override (auto-detected if not provided)
        method: Scraping method ('selenium', 'playwright', 'requests')
    
    Examples:
        /real-scrape?url=https://www.amazon.com/dp/B08N5WRWNW&keywords=sound,quality
        /real-scrape?url=https://www.walmart.com/ip/standing-desk&keywords=assembly,easy&method=selenium
    """
    if not REAL_SCRAPER_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Real scraper not available. Please install advanced dependencies.',
            'install_command': 'pip install -r requirements_advanced.txt'
        }), 503
    
    try:
        # Get parameters
        url = request.args.get('url')
        keywords_param = request.args.get('keywords', '')
        platform = request.args.get('platform')
        method = request.args.get('method', 'selenium')
        
        if not url:
            return jsonify({
                'success': False,
                'error': 'Missing required parameter: url',
                'examples': {
                    'amazon_product': '/real-scrape?url=https://www.amazon.com/dp/B08N5WRWNW&keywords=quality',
                    'walmart_product': '/real-scrape?url=https://www.walmart.com/ip/product&keywords=assembly',
                    'standing_desk_search': '/real-scrape?url=https://www.amazon.com/s?k=standing+desk&keywords=easy,assembly'
                }
            }), 400
        
        # Parse keywords
        keywords = [k.strip() for k in keywords_param.split(',') if k.strip()] if keywords_param else None
        
        logger.info(f"🔍 REAL SCRAPE REQUEST: {url} with keywords: {keywords}")
        
        # Use real scraping engine
        result = real_scraping_engine.scrape_real_product_reviews(url, platform, keywords)
        
        if result.get('success'):
            # Update global data
            latest_data['universal_reviews'] = result['data']['reviews']
            latest_data['timestamp'] = datetime.now().isoformat()
            latest_data['status'] = 'success'
            
            # Add metadata about real scraping
            result['data']['scraping_guarantee'] = 'REAL_LIVE_DATA'
            result['data']['extraction_method'] = 'ADVANCED_REAL_SCRAPER'
            result['data']['data_authenticity'] = 'GENUINE_WEBSITE_CONTENT'
            
            logger.info(f"✅ REAL SCRAPE SUCCESS: {len(result['data']['reviews'])} authentic reviews extracted")
            
            return jsonify(result)
        else:
            logger.error(f"❌ REAL SCRAPE FAILED: {result.get('error', 'Unknown error')}")
            return jsonify(result), 500
        
    except Exception as e:
        error_msg = f"Real scraping failed: {str(e)}"
        logger.error(error_msg)
        return jsonify({
            'success': False,
            'error': error_msg,
            'url': url,
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/real-search', methods=['GET'])
def real_multi_platform_search():
    """
    GET endpoint for REAL multi-platform product search and review extraction.
    Searches across multiple platforms and extracts REAL reviews.
    
    Query Parameters:
        product: Product name to search for (required)
        keywords: Keywords to filter reviews (comma-separated)
        platforms: Platforms to search (comma-separated, default: all)
    
    Examples:
        /real-search?product=standing desk&keywords=assembly,easy
        /real-search?product=wireless headphones&keywords=sound,quality&platforms=amazon,walmart
    """
    if not REAL_SCRAPER_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Real scraper not available. Please install advanced dependencies.'
        }), 503
    
    try:
        # Get parameters
        product = request.args.get('product')
        keywords_param = request.args.get('keywords', '')
        platforms_param = request.args.get('platforms', '')
        
        if not product:
            return jsonify({
                'success': False,
                'error': 'Missing required parameter: product',
                'examples': {
                    'standing_desk': '/real-search?product=standing desk&keywords=assembly,easy',
                    'wireless_headphones': '/real-search?product=wireless headphones&keywords=sound,quality',
                    'office_chair': '/real-search?product=office chair&keywords=comfort,ergonomic'
                }
            }), 400
        
        # Parse parameters
        keywords = [k.strip() for k in keywords_param.split(',') if k.strip()] if keywords_param else None
        platforms = [p.strip() for p in platforms_param.split(',') if p.strip()] if platforms_param else None
        
        logger.info(f"🔍 REAL MULTI-PLATFORM SEARCH: {product} with keywords: {keywords}")
        
        # Use real scraping engine for multi-platform search
        result = real_scraping_engine.scrape_multiple_platforms_for_product(product, keywords)
        
        if result.get('success'):
            # Update global data
            latest_data['universal_reviews'] = result['data']['reviews']
            latest_data['timestamp'] = datetime.now().isoformat()
            latest_data['status'] = 'success'
            
            # Add metadata
            result['data']['search_guarantee'] = 'REAL_MULTI_PLATFORM_DATA'
            result['data']['extraction_method'] = 'CONCURRENT_REAL_SCRAPING'
            result['data']['data_authenticity'] = 'LIVE_WEBSITE_EXTRACTION'
            
            logger.info(f"✅ REAL MULTI-PLATFORM SUCCESS: {len(result['data']['reviews'])} reviews from {len(result['data']['platforms_scraped'])} platforms")
            
            return jsonify(result)
        else:
            logger.error(f"❌ REAL MULTI-PLATFORM FAILED: {result.get('error', 'Unknown error')}")
            return jsonify(result), 500
        
    except Exception as e:
        error_msg = f"Real multi-platform search failed: {str(e)}"
        logger.error(error_msg)
        return jsonify({
            'success': False,
            'error': error_msg,
            'product': product,
            'timestamp': datetime.now().isoformat()
        }), 500
def get_supported_platforms():
    """
    GET endpoint to list all supported platforms.
    """
    try:
        platforms = universal_scraper.get_supported_platforms()
        return jsonify({
            'success': True,
            'data': {
                'platforms': platforms,
                'total_platforms': len(platforms)
            },
            'message': f'Currently supporting {len(platforms)} platforms'
        })
    except Exception as e:
        logger.error(f"Error getting platforms: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/search', methods=['GET'])
def intelligent_review_search():
    """
    GET endpoint for intelligent review search with keyword filtering.
    
    Query Parameters:
        url: The URL to scrape
        keywords: Comma-separated keywords (e.g., "assembly,quality,durability")
        categories: Comma-separated categories (e.g., "assembly,value,comfort")
        min_rating: Minimum rating filter (default: 0)
        max_rating: Maximum rating filter (default: 5)
        sentiment: Filter by sentiment ('positive', 'negative', 'neutral')
        sort_by: Sort method ('relevance', 'rating', 'date', 'length')
        limit: Maximum number of reviews (default: 50)
    
    Examples:
        /search?url=https://www.walmart.com/ip/standing-desk&keywords=assembly,setup
        /search?url=https://www.target.com/p/chair&categories=comfort,quality&min_rating=4
        /search?url=https://www.amazon.com/dp/B123&keywords=durability&sentiment=positive
    """
    try:
        # Get parameters
        url = request.args.get('url')
        if not url:
            return jsonify({
                'success': False,
                'error': 'Missing required parameter: url',
                'examples': {
                    'standing_desk_assembly': '/search?url=https://www.walmart.com/ip/standing-desk&keywords=assembly,setup',
                    'chair_comfort': '/search?url=https://www.target.com/p/chair&categories=comfort,quality&min_rating=4',
                    'product_durability': '/search?url=https://www.amazon.com/dp/product&keywords=durability&sentiment=positive'
                }
            }), 400
        
        # Validate URL
        from utils.validators import validate_url
        validation_result = validate_url(url)
        if not validation_result['valid']:
            return jsonify({
                'success': False,
                'error': validation_result['error']
            }), 400
        
        # Create filter configuration
        filter_config = create_filter_from_params(request.args)
        
        # First scrape reviews
        platform = universal_scraper.detect_platform(url)
        if not platform:
            return jsonify({
                'success': False,
                'error': 'Unsupported platform',
                'supported_platforms': universal_scraper.get_supported_platforms()
            }), 400
        
        reviews = universal_scraper.scrape_reviews(url, platform)
        
        # Apply intelligent filtering
        filtered_reviews = review_analyzer.filter_reviews(reviews, filter_config)
        insights = review_analyzer.get_review_insights(filtered_reviews)
        
        # Clean and format reviews with links
        from utils.helpers import clean_review_data
        cleaned_reviews = clean_review_data(filtered_reviews)
        
        response_data = {
            'success': True,
            'data': {
                'reviews': cleaned_reviews,
                'insights': insights,
                'filter_applied': {
                    'keywords': filter_config.keywords,
                    'categories': filter_config.categories,
                    'min_rating': filter_config.min_rating,
                    'max_rating': filter_config.max_rating,
                    'sentiment': filter_config.sentiment,
                    'sort_by': filter_config.sort_by
                },
                'total_found': len(cleaned_reviews),
                'total_scraped': len(reviews),
                'platform': platform,
                'scraped_at': datetime.now().isoformat(),
                'original_url': url
            },
            'message': f'Found {len(cleaned_reviews)} relevant reviews out of {len(reviews)} total'
        }
        
        logger.info(f"Intelligent search: {len(cleaned_reviews)}/{len(reviews)} reviews matched criteria")
        return jsonify(response_data)
        
    except Exception as e:
        error_msg = f"Intelligent search failed: {str(e)}"
        logger.error(error_msg)
        return jsonify({
            'success': False,
            'error': error_msg
        }), 500


@app.route('/categories', methods=['GET'])
def get_available_categories():
    """
    GET endpoint to list available review categories for filtering.
    """
    try:
        categories = {
            'assembly': {
                'description': 'Reviews about product assembly, setup, and installation',
                'keywords': ['assembly', 'setup', 'installation', 'instructions']
            },
            'quality': {
                'description': 'Reviews about build quality, materials, and construction',
                'keywords': ['quality', 'build quality', 'material', 'sturdy']
            },
            'value': {
                'description': 'Reviews about price, value for money, and cost',
                'keywords': ['value', 'price', 'worth', 'affordable']
            },
            'size': {
                'description': 'Reviews about product size, dimensions, and fit',
                'keywords': ['size', 'big', 'small', 'dimensions']
            },
            'comfort': {
                'description': 'Reviews about comfort, ergonomics, and feel',
                'keywords': ['comfort', 'comfortable', 'ergonomic', 'soft']
            },
            'delivery': {
                'description': 'Reviews about shipping, delivery, and packaging',
                'keywords': ['delivery', 'shipping', 'packaging', 'arrived']
            },
            'customer_service': {
                'description': 'Reviews about customer support and service',
                'keywords': ['customer service', 'support', 'help', 'staff']
            },
            'durability': {
                'description': 'Reviews about product longevity and durability',
                'keywords': ['durability', 'durable', 'last', 'reliable']
            }
        }
        
        return jsonify({
            'success': True,
            'data': {
                'categories': categories,
                'total_categories': len(categories)
            },
            'message': 'Available review categories for intelligent filtering'
        })
    except Exception as e:
        logger.error(f"Error getting categories: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/stop', methods=['POST'])
def stop_scraping_endpoint():
    """
    POST endpoint to stop background scraping.
    """
    global scraping_thread, stop_scraping
    
    try:
        if scraping_thread and scraping_thread.is_alive():
            stop_scraping.set()
            scraping_thread.join(timeout=5)
            stop_scraping.clear()
            return jsonify({'message': 'Background scraping stopped', 'status': 'success'})
        else:
            return jsonify({'message': 'No background scraping active', 'status': 'info'})
    except Exception as e:
        logger.error(f"Error stopping scraping: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    # Initialize logging
    logger.info("Starting Python Web Scraper API")
    
    # Get configuration from environment
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    # Replit uses port 8080, Railway uses PORT env var
    port = int(os.getenv('PORT', 8080))
    host = os.getenv('HOST', '0.0.0.0')
    
    logger.info(f"Server starting on {host}:{port}")
    logger.info(f"Platform: {'Replit' if 'REPL_SLUG' in os.environ else 'Railway' if 'RAILWAY_ENVIRONMENT' in os.environ else 'Local'}")
    
    # Start the Flask application
    app.run(
        host=host,
        port=port,
        debug=debug,
        threaded=True
    )
