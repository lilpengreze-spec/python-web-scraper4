"""
Standing Desk Assembly Review Demo

This shows what your scraper would return when searching for
"standing desk easy to assemble" with real-world review examples.
"""

import json
from datetime import datetime


def create_standing_desk_assembly_results():
    """
    Example of what your scraper returns when searching:
    "standing desk easy to assemble"
    """
    
    # Simulated API call result structure
    api_response = {
        "success": True,
        "data": {
            "reviews": [
                {
                    "reviewer_name": "OfficeWorker2024",
                    "rating": 5,
                    "review_text": "This standing desk was surprisingly easy to assemble! The instructions were clear and all parts were labeled. Took me about 45 minutes to set up completely. The height adjustment mechanism works smoothly.",
                    "date": "2025-08-05",
                    "review_url": "https://www.walmart.com/ip/standing-desk/review-123",
                    "source": "walmart",
                    "helpful_votes": "12 people found this helpful",
                    "keywords_matched": ["easy", "assemble", "setup"],
                    "sentiment": "positive"
                },
                {
                    "reviewer_name": "HomeOfficePro",
                    "rating": 4,
                    "review_text": "Assembly was straightforward with good instructions. The desk is sturdy once assembled. Only challenge was the electric motor installation, but even that wasn't too difficult. Worth the price for the quality.",
                    "date": "2025-08-03", 
                    "review_url": "https://www.target.com/p/standing-desk/review-456",
                    "source": "target",
                    "helpful_votes": "8 people found this helpful",
                    "keywords_matched": ["assembly", "easy"],
                    "sentiment": "positive"
                },
                {
                    "reviewer_name": "TechGuru88",
                    "rating": 3,
                    "review_text": "The desk itself is great, but assembly took longer than expected - about 2 hours. Instructions could be clearer for the cable management part. Once set up, it's very stable and the height adjustment is smooth.",
                    "date": "2025-08-01",
                    "review_url": "https://www.bestbuy.com/site/standing-desk/review-789",
                    "source": "bestbuy", 
                    "helpful_votes": "15 people found this helpful",
                    "keywords_matched": ["assembly", "setup"],
                    "sentiment": "neutral"
                },
                {
                    "reviewer_name": "WorkFromHome",
                    "rating": 5,
                    "review_text": "Super easy assembly! Even my non-handy spouse could put this together. The pre-drilled holes lined up perfectly. Clear step-by-step instructions with pictures. Highly recommend for anyone worried about complicated setup.",
                    "date": "2025-07-30",
                    "review_url": "https://www.wayfair.com/furniture/standing-desk/review-321",
                    "source": "wayfair",
                    "helpful_votes": "22 people found this helpful", 
                    "keywords_matched": ["easy", "assembly", "setup"],
                    "sentiment": "positive"
                },
                {
                    "reviewer_name": "SmallOfficeBig",
                    "rating": 4,
                    "review_text": "Assembly was pretty easy, took about an hour. The hardest part was lifting the desktop onto the frame, but that's expected. Instructions were clear and all hardware was included. Great desk for the price.",
                    "date": "2025-07-28",
                    "review_url": "https://www.ikea.com/us/en/p/standing-desk/review-654",
                    "source": "ikea",
                    "helpful_votes": "6 people found this helpful",
                    "keywords_matched": ["easy", "assembly"],
                    "sentiment": "positive"
                },
                {
                    "reviewer_name": "StudentLife",
                    "rating": 2,
                    "review_text": "Assembly was more difficult than advertised. Some holes didn't align properly and I had to force some screws. The instructions weren't very helpful. Took me 3 hours total. Desk works fine now but setup was frustrating.",
                    "date": "2025-07-25",
                    "review_url": "https://www.amazon.com/dp/standing-desk/review-987",
                    "source": "amazon",
                    "helpful_votes": "9 people found this helpful",
                    "keywords_matched": ["assembly"],
                    "sentiment": "negative"
                }
            ],
            "insights": {
                "total_reviews_analyzed": 6,
                "average_rating": 3.8,
                "sentiment_breakdown": {
                    "positive": 4,
                    "neutral": 1, 
                    "negative": 1
                },
                "common_keywords": [
                    {"keyword": "assembly", "frequency": 6, "avg_rating": 3.8},
                    {"keyword": "easy", "frequency": 4, "avg_rating": 4.5},
                    {"keyword": "setup", "frequency": 4, "avg_rating": 4.2},
                    {"keyword": "instructions", "frequency": 5, "avg_rating": 3.6}
                ],
                "assembly_time_mentioned": {
                    "45 minutes": 1,
                    "1 hour": 1, 
                    "2 hours": 1,
                    "3 hours": 1
                }
            },
            "filter_applied": {
                "keywords": ["easy", "assemble", "assembly", "setup"],
                "categories": [],
                "min_rating": 0,
                "max_rating": 5,
                "sentiment": None,
                "sort_by": "relevance"
            },
            "total_found": 6,
            "total_scraped": 47,
            "platforms_searched": ["walmart", "target", "bestbuy", "wayfair", "ikea", "amazon"],
            "scraped_at": "2025-08-09T15:35:00.000Z",
            "search_query": "standing desk easy to assemble"
        },
        "message": "Found 6 relevant reviews out of 47 total reviews matching assembly criteria"
    }
    
    return api_response


def analyze_assembly_feedback():
    """Analyze the assembly-related feedback from the reviews."""
    
    results = create_standing_desk_assembly_results()
    reviews = results["data"]["reviews"]
    insights = results["data"]["insights"]
    
    print("🔍 STANDING DESK ASSEMBLY ANALYSIS")
    print("=" * 60)
    
    print(f"\n📊 Search Results Summary:")
    print(f"   • Total Reviews Found: {len(reviews)}")
    print(f"   • Average Rating: {insights['average_rating']}/5.0")
    print(f"   • Platforms Searched: {', '.join(results['data']['platforms_searched'])}")
    
    print(f"\n😊 Sentiment Breakdown:")
    sentiment = insights['sentiment_breakdown']
    print(f"   • Positive: {sentiment['positive']} reviews")
    print(f"   • Neutral: {sentiment['neutral']} reviews") 
    print(f"   • Negative: {sentiment['negative']} reviews")
    
    print(f"\n⏱️ Assembly Time Feedback:")
    for time, count in insights['assembly_time_mentioned'].items():
        print(f"   • {time}: {count} review(s)")
    
    print(f"\n🔑 Key Assembly Comments:")
    for i, review in enumerate(reviews, 1):
        sentiment_emoji = "😊" if review['sentiment'] == 'positive' else "😐" if review['sentiment'] == 'neutral' else "😞"
        print(f"\n   {i}. {sentiment_emoji} {review['reviewer_name']} ({review['rating']}/5 stars)")
        print(f"      Platform: {review['source'].title()}")
        print(f"      Keywords: {', '.join(review['keywords_matched'])}")
        print(f"      Comment: \"{review['review_text'][:120]}...\"")
    
    print(f"\n📈 Assembly Insights:")
    print(f"   • Most reviews mention clear instructions")
    print(f"   • Assembly time ranges from 45 minutes to 3 hours")
    print(f"   • 67% of reviewers found assembly easy")
    print(f"   • Common issues: hole alignment, heavy parts")
    
    return results


def show_api_call_example():
    """Show the exact API call that would generate these results."""
    
    print(f"\n🚀 YOUR RAILWAY API CALL:")
    print("=" * 60)
    
    api_url = "https://web-production-e6ba.up.railway.app/search"
    params = "?url=https://www.walmart.com/ip/standing-desk&keywords=easy,assemble,assembly,setup"
    
    print(f"URL: {api_url}{params}")
    
    print(f"\n📱 JavaScript Code for Your Replit:")
    print("""
const API_BASE_URL = 'https://web-production-e6ba.up.railway.app';

async function searchStandingDeskAssembly() {
    const url = 'https://www.walmart.com/ip/standing-desk';
    const keywords = 'easy,assemble,assembly,setup';
    
    const response = await fetch(
        `${API_BASE_URL}/search?url=${encodeURIComponent(url)}&keywords=${keywords}`
    );
    
    const data = await response.json();
    
    // Access the assembly-related reviews
    const assemblyReviews = data.data.reviews;
    const insights = data.data.insights;
    
    return {
        reviews: assemblyReviews,
        insights: insights,
        totalFound: data.data.total_found
    };
}

// Usage
searchStandingDeskAssembly().then(results => {
    console.log('Assembly Reviews:', results.reviews);
    console.log('Insights:', results.insights);
});
    """)


if __name__ == "__main__":
    print("🎯 DEMO: Standing Desk Assembly Search Results")
    print("This shows what your Railway API returns when searching for assembly reviews.")
    
    results = analyze_assembly_feedback()
    show_api_call_example()
    
    print(f"\n" + "=" * 60)
    print("🎉 This is the type of intelligent analysis your scraper provides!")
    print("Try it live: https://web-production-e6ba.up.railway.app")
