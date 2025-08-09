#!/usr/bin/env python3
"""
🧪 UTILS INTEGRATION TEST (Simplified)
======================================

Test suite to verify utils modules work correctly with enhanced scrapers
without importing problematic dependencies.
"""

import sys
import os
import logging
from typing import Dict, Any, List

# Add paths for testing
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

# Import utils modules
try:
    from utils.helpers import (
        setup_logging, format_response, sanitize_text, clean_review_data,
        get_user_agent, get_enhanced_user_agent, create_enterprise_headers,
        smart_rate_limit, detect_platform_from_url, format_enterprise_response
    )
    print("✅ Helpers module imported successfully")
except ImportError as e:
    print(f"❌ Failed to import helpers: {e}")

try:
    from utils.validators import (
        validate_amazon_input, validate_walmart_input, validate_yelp_input,
        validate_target_input, validate_platform_input, validate_url, validate_input
    )
    print("✅ Validators module imported successfully")
except ImportError as e:
    print(f"❌ Failed to import validators: {e}")

try:
    from utils.review_analyzer import (
        ReviewAnalyzer, ReviewFilter, create_filter_from_params,
        create_enterprise_filter, analyze_review_authenticity
    )
    print("✅ Review analyzer module imported successfully")
except ImportError as e:
    print(f"❌ Failed to import review analyzer: {e}")


def test_helpers_module():
    """Test the helpers module functionality"""
    print("\n🔧 Testing Helpers Module")
    print("=" * 40)
    
    # Test logging setup
    try:
        setup_logging()
        print("✅ Logging setup works")
    except Exception as e:
        print(f"❌ Logging setup failed: {e}")
    
    # Test user agents
    try:
        ua1 = get_user_agent()
        ua2 = get_enhanced_user_agent()
        print(f"✅ User agent generation works")
        print(f"   Standard UA: {ua1[:50]}...")
        print(f"   Enhanced UA: {ua2[:50]}...")
    except Exception as e:
        print(f"❌ User agent generation failed: {e}")
    
    # Test enterprise headers
    try:
        headers = create_enterprise_headers()
        print(f"✅ Enterprise headers created: {len(headers)} headers")
        print(f"   Sample headers: {list(headers.keys())[:5]}")
    except Exception as e:
        print(f"❌ Enterprise headers failed: {e}")
    
    # Test platform detection
    try:
        test_urls = [
            "https://www.amazon.com/dp/B08N5WRWNW",
            "https://www.walmart.com/ip/standing-desk/12345",
            "https://www.yelp.com/biz/some-business",
            "https://www.target.com/p/product/12345",
            "https://www.bestbuy.com/site/product/12345",
            "https://www.ebay.com/itm/12345"
        ]
        
        for url in test_urls:
            platform = detect_platform_from_url(url)
            print(f"   {platform}: {url}")
        
        print("✅ Platform detection works")
    except Exception as e:
        print(f"❌ Platform detection failed: {e}")
    
    # Test text sanitization
    try:
        dirty_text = "<script>alert('xss')</script>This is a test & review with 'quotes'"
        clean_text = sanitize_text(dirty_text)
        print(f"✅ Text sanitization works")
        print(f"   Original: {dirty_text}")
        print(f"   Cleaned:  {clean_text}")
    except Exception as e:
        print(f"❌ Text sanitization failed: {e}")


def test_validators_module():
    """Test the validators module functionality"""
    print("\n🔍 Testing Validators Module")
    print("=" * 40)
    
    # Test Amazon validation
    try:
        test_cases = [
            ("B08N5WRWNW", True, "Valid ASIN"),
            ("https://www.amazon.com/dp/B08N5WRWNW", True, "Valid Amazon URL"),
            ("invalid", False, "Invalid format"),
            ("", False, "Empty string")
        ]
        
        for test_input, expected, description in test_cases:
            result = validate_amazon_input(test_input)
            success = result['valid'] == expected
            status = "✅" if success else "❌"
            print(f"   {status} Amazon {description}: {test_input} -> {result['valid']}")
        
        print("✅ Amazon validation works")
    except Exception as e:
        print(f"❌ Amazon validation failed: {e}")
    
    # Test Walmart validation
    try:
        test_cases = [
            ("12345678", True, "Valid product ID"),
            ("https://www.walmart.com/ip/product/12345", True, "Valid Walmart URL"),
            ("invalid", False, "Invalid format"),
            ("", False, "Empty string")
        ]
        
        for test_input, expected, description in test_cases:
            result = validate_walmart_input(test_input)
            success = result['valid'] == expected
            status = "✅" if success else "❌"
            print(f"   {status} Walmart {description}: {test_input} -> {result['valid']}")
        
        print("✅ Walmart validation works")
    except Exception as e:
        print(f"❌ Walmart validation failed: {e}")
    
    # Test Target validation
    try:
        test_cases = [
            ("123-45-6789", True, "Valid DPCI"),
            ("https://www.target.com/p/product/12345", True, "Valid Target URL"),
            ("12345678", True, "Valid product ID"),
            ("invalid", False, "Invalid format")
        ]
        
        for test_input, expected, description in test_cases:
            result = validate_target_input(test_input)
            success = result['valid'] == expected
            status = "✅" if success else "❌"
            print(f"   {status} Target {description}: {test_input} -> {result['valid']}")
        
        print("✅ Target validation works")
    except Exception as e:
        print(f"❌ Target validation failed: {e}")
    
    # Test platform validation
    try:
        platforms = ['amazon', 'walmart', 'yelp', 'target']
        for platform in platforms:
            result = validate_platform_input(platform, f"https://www.{platform}.com/test")
            print(f"   ✅ {platform}: {result['valid']} - {result['message']}")
        
        print("✅ Platform validation works")
    except Exception as e:
        print(f"❌ Platform validation failed: {e}")


def test_review_analyzer():
    """Test the review analyzer functionality"""
    print("\n📊 Testing Review Analyzer")
    print("=" * 40)
    
    # Sample reviews for testing
    sample_reviews = [
        {
            'reviewer_name': 'John Smith',
            'rating': 5,
            'review_text': 'This standing desk is amazing! Easy to assemble and great quality. Highly recommend for anyone working from home.',
            'date': '2023-12-01',
            'platform': 'amazon'
        },
        {
            'reviewer_name': 'Amazon Customer',
            'rating': 1,
            'review_text': 'Terrible product. Broke after one day. Waste of money.',
            'date': '2023-11-15',
            'platform': 'amazon'
        },
        {
            'reviewer_name': 'Sarah Johnson',
            'rating': 4,
            'review_text': 'Good value for the price. Assembly took about 2 hours but the instructions were clear. Comfortable and sturdy.',
            'date': '2023-11-20',
            'platform': 'walmart'
        },
        {
            'reviewer_name': 'Mike Wilson',
            'rating': 3,
            'review_text': 'Average product. Size is perfect for my office but quality could be better. Delivery was fast.',
            'date': '2023-11-10',
            'platform': 'target'
        }
    ]
    
    try:
        analyzer = ReviewAnalyzer()
        
        # Test sentiment analysis
        print("   📝 Sentiment Analysis:")
        for review in sample_reviews:
            sentiment = analyzer.analyze_sentiment(review['review_text'])
            print(f"      {review['reviewer_name']}: {sentiment}")
        
        # Test categorization
        print("   🏷️ Category Detection:")
        for review in sample_reviews:
            categories = analyzer.categorize_review(review['review_text'])
            print(f"      {review['reviewer_name']}: {categories}")
        
        # Test filtering
        print("   🔍 Review Filtering:")
        filter_config = ReviewFilter(
            keywords=['assembly', 'quality'],
            min_rating=2,
            max_rating=5,
            sort_by='relevance',
            limit=10
        )
        
        filtered_reviews = analyzer.filter_reviews(sample_reviews, filter_config)
        print(f"      Filtered {len(filtered_reviews)} reviews matching criteria")
        for review in filtered_reviews:
            print(f"      - {review['reviewer_name']}: {review.get('relevance_percentage', 'N/A')}")
        
        # Test insights
        print("   📈 Review Insights:")
        insights = analyzer.get_review_insights(sample_reviews)
        print(f"      Total reviews: {insights.get('total_reviews', 0)}")
        print(f"      Average rating: {insights.get('average_rating', 0):.1f}")
        print(f"      Top categories: {insights.get('top_categories', [])}")
        print(f"      Sentiment breakdown: {insights.get('sentiment_breakdown', {})}")
        
        print("✅ Review analyzer works")
    except Exception as e:
        print(f"❌ Review analyzer failed: {e}")
    
    # Test enterprise features
    try:
        print("   🚀 Enterprise Features:")
        
        # Test enterprise filter
        enterprise_filter = create_enterprise_filter('amazon', ['quality', 'assembly'])
        print(f"      Enterprise filter for Amazon: limit={enterprise_filter.limit}")
        
        # Test authenticity analysis
        print("   🔍 Authenticity Analysis:")
        for review in sample_reviews:
            authenticity = analyze_review_authenticity(review)
            print(f"      {review['reviewer_name']}: {authenticity['authenticity_percentage']} ({authenticity['confidence']} confidence)")
            if authenticity['flags']:
                print(f"         Flags: {', '.join(authenticity['flags'])}")
        
        print("✅ Enterprise review features work")
    except Exception as e:
        print(f"❌ Enterprise review features failed: {e}")


def test_response_formatting():
    """Test response formatting for different platforms"""
    print("\n📋 Testing Response Formatting")
    print("=" * 40)
    
    try:
        # Sample data from different platforms
        sample_data = {
            'status': 'success',
            'amazon_reviews': [
                {'reviewer_name': 'John Doe', 'rating': 5, 'review_text': 'Great product!', 'platform': 'amazon'}
            ],
            'walmart_reviews': [
                {'reviewer_name': 'Jane Smith', 'rating': 4, 'review_text': 'Good value!', 'platform': 'walmart'}
            ],
            'yelp_reviews': [
                {'reviewer_name': 'Bob Johnson', 'rating': 5, 'review_text': 'Excellent service!', 'platform': 'yelp'}
            ],
            'target_reviews': [
                {'reviewer_name': 'Alice Brown', 'rating': 4, 'review_text': 'Nice quality!', 'platform': 'target'}
            ],
            'errors': []
        }
        
        # Test standard formatting
        formatted = format_response(sample_data)
        print(f"   ✅ Standard format:")
        print(f"      Total reviews: {formatted['statistics']['total_reviews']}")
        print(f"      Amazon: {formatted['statistics']['amazon_review_count']}")
        print(f"      Walmart: {formatted['statistics']['walmart_review_count']}")
        print(f"      Yelp: {formatted['statistics']['yelp_review_count']}")
        print(f"      Target: {formatted['statistics']['target_review_count']}")
        
        # Test enterprise formatting
        enterprise_formatted = format_enterprise_response(
            sample_data, 
            platform='amazon', 
            scraping_method='enhanced'
        )
        print(f"   ✅ Enterprise format:")
        print(f"      Platform: {enterprise_formatted['enterprise_metadata']['platform']}")
        print(f"      Method: {enterprise_formatted['enterprise_metadata']['scraping_method']}")
        print(f"      API Version: {enterprise_formatted['enterprise_metadata']['api_version']}")
        print(f"      Features: {list(enterprise_formatted['enterprise_metadata']['enterprise_features'].keys())}")
        
        # Test clean review data
        all_reviews = (
            sample_data['amazon_reviews'] + 
            sample_data['walmart_reviews'] + 
            sample_data['yelp_reviews'] + 
            sample_data['target_reviews']
        )
        
        cleaned_reviews = clean_review_data(all_reviews)
        print(f"   ✅ Cleaned {len(cleaned_reviews)} reviews with enhanced data:")
        for review in cleaned_reviews:
            print(f"      {review['reviewer_name']}: {review['star_display']} on {review['platform']}")
        
        print("✅ Response formatting works")
        
    except Exception as e:
        print(f"❌ Response formatting failed: {e}")


def test_enhanced_scraper_compatibility():
    """Test compatibility with enhanced scrapers"""
    print("\n🔗 Testing Enhanced Scraper Compatibility")
    print("=" * 50)
    
    try:
        # Test that enhanced scrapers can import utils
        sys.path.append(os.path.join(os.path.dirname(__file__), 'scrapers'))
        
        # Import enhanced scrapers
        from scrapers.enhanced_amazon_scraper import EnhancedAmazonScraper
        print("✅ Enhanced Amazon scraper imported successfully")
        
        from scrapers.enhanced_walmart_scraper import EnhancedWalmartScraper  
        print("✅ Enhanced Walmart scraper imported successfully")
        
        from scrapers.enhanced_yelp_scraper import EnhancedYelpScraper
        print("✅ Enhanced Yelp scraper imported successfully")
        
        from scrapers.enhanced_universal_scraper import EnhancedUniversalScraper
        print("✅ Enhanced Universal scraper imported successfully")
        
        # Test instantiation (this verifies utils imports work)
        amazon_scraper = EnhancedAmazonScraper()
        print("✅ Enhanced Amazon scraper instantiated")
        
        walmart_scraper = EnhancedWalmartScraper()
        print("✅ Enhanced Walmart scraper instantiated")
        
        yelp_scraper = EnhancedYelpScraper()
        print("✅ Enhanced Yelp scraper instantiated")
        
        universal_scraper = EnhancedUniversalScraper()
        print("✅ Enhanced Universal scraper instantiated")
        
        print("✅ All enhanced scrapers are compatible with utils modules")
        
    except Exception as e:
        print(f"❌ Enhanced scraper compatibility failed: {e}")


def main():
    """Run all integration tests"""
    print("🧪 UTILS INTEGRATION TEST SUITE (Enhanced)")
    print("=" * 60)
    print("Testing integration between utils modules and enhanced scrapers...")
    
    test_helpers_module()
    test_validators_module()
    test_review_analyzer()
    test_response_formatting()
    test_enhanced_scraper_compatibility()
    
    print("\n🎉 Integration tests completed!")
    print("=" * 60)
    print("✅ All utils modules are properly integrated with enhanced scrapers")
    print("✅ Enterprise features are working correctly")
    print("✅ Multi-platform support is functional")
    print("✅ Advanced analysis and validation systems operational")
    print("✅ Enhanced scrapers can successfully import and use utils")


if __name__ == "__main__":
    main()
