"""
Advanced Review Filtering and Search

This module provides intelligent filtering of scraped reviews based on
keywords, sentiment, and criteria to help users find specific information.
"""

import re
import logging
from typing import List, Dict, Any, Optional, Set
from collections import Counter
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ReviewFilter:
    """Configuration for review filtering"""
    keywords: List[str] = None
    categories: List[str] = None
    min_rating: float = 0
    max_rating: float = 5
    sentiment: str = None  # 'positive', 'negative', 'neutral'
    sort_by: str = 'relevance'  # 'relevance', 'rating', 'date', 'length'
    limit: int = 50


class ReviewAnalyzer:
    """
    Intelligent review analysis and filtering system.
    """
    
    def __init__(self):
        """Initialize the review analyzer."""
        # Common criteria categories for different product types
        self.criteria_keywords = {
            'assembly': [
                'assembly', 'assemble', 'put together', 'setup', 'installation', 
                'install', 'build', 'construction', 'instructions', 'manual',
                'easy to assemble', 'hard to assemble', 'difficult assembly',
                'setup process', 'installation guide', 'assembly time'
            ],
            'quality': [
                'quality', 'build quality', 'material', 'sturdy', 'durable',
                'solid', 'cheap', 'flimsy', 'well made', 'construction',
                'materials', 'finish', 'craftsmanship', 'workmanship',
                'premium', 'high quality', 'poor quality', 'excellent quality'
            ],
            'value': [
                'value', 'price', 'worth', 'expensive', 'cheap', 'affordable',
                'money', 'cost', 'budget', 'overpriced', 'good deal',
                'bang for buck', 'value for money', 'cost effective',
                'reasonable price', 'great value', 'worth the money'
            ],
            'size': [
                'size', 'big', 'small', 'large', 'compact', 'spacious',
                'dimensions', 'fit', 'space', 'room', 'tiny', 'huge',
                'perfect size', 'too big', 'too small', 'fits perfectly',
                'space saving', 'oversized', 'undersized'
            ],
            'comfort': [
                'comfort', 'comfortable', 'ergonomic', 'soft', 'firm',
                'cushion', 'support', 'padding', 'cozy', 'uncomfortable',
                'ergonomics', 'back support', 'lumbar support', 'comfortable seating'
            ],
            'delivery': [
                'delivery', 'shipping', 'arrived', 'package', 'packaging',
                'fast shipping', 'slow delivery', 'damaged', 'box',
                'delivered', 'received', 'shipping time', 'delivery speed',
                'well packaged', 'damaged in shipping', 'quick delivery'
            ],
            'customer_service': [
                'customer service', 'support', 'help', 'response', 'staff',
                'representative', 'helpful', 'rude', 'friendly', 'contact',
                'service quality', 'support team', 'customer care',
                'responsive', 'unhelpful', 'professional service'
            ],
            'durability': [
                'durability', 'durable', 'last', 'lasting', 'wear', 'tear',
                'broke', 'broken', 'sturdy', 'reliable', 'falls apart',
                'long lasting', 'holds up well', 'wearing out', 'breaking down',
                'built to last', 'still working', 'stopped working'
            ],
            'performance': [
                'performance', 'works', 'working', 'function', 'functionality',
                'efficient', 'effective', 'fast', 'slow', 'responsive',
                'smooth operation', 'performs well', 'excellent performance',
                'poor performance', 'works great', 'not working'
            ],
            'design': [
                'design', 'style', 'appearance', 'look', 'looks', 'attractive',
                'beautiful', 'ugly', 'sleek', 'modern', 'stylish',
                'aesthetic', 'good looking', 'nice design', 'elegant',
                'visually appealing', 'design quality'
            ],
            'features': [
                'features', 'feature', 'options', 'functionality', 'capabilities',
                'useful features', 'great features', 'missing features',
                'feature rich', 'basic features', 'advanced features'
            ]
        }
        
        # Sentiment indicators
        self.positive_words = {
            'excellent', 'amazing', 'great', 'love', 'perfect', 'awesome',
            'fantastic', 'wonderful', 'brilliant', 'outstanding', 'superb',
            'recommend', 'happy', 'satisfied', 'pleased', 'impressed'
        }
        
        self.negative_words = {
            'terrible', 'awful', 'hate', 'horrible', 'worst', 'bad',
            'disappointed', 'poor', 'useless', 'waste', 'regret',
            'broken', 'defective', 'faulty', 'cheap', 'flimsy'
        }
    
    def analyze_sentiment(self, text: str) -> str:
        """
        Analyze sentiment of review text.
        
        Args:
            text: Review text to analyze
            
        Returns:
            Sentiment: 'positive', 'negative', or 'neutral'
        """
        if not text:
            return 'neutral'
        
        text_lower = text.lower()
        words = set(re.findall(r'\b\w+\b', text_lower))
        
        positive_count = len(words.intersection(self.positive_words))
        negative_count = len(words.intersection(self.negative_words))
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    def calculate_keyword_relevance(self, text: str, keywords: List[str]) -> float:
        """
        Calculate how relevant a review is to given keywords.
        
        Args:
            text: Review text
            keywords: List of keywords to match
            
        Returns:
            Relevance score (0-1)
        """
        if not text or not keywords:
            return 0.0
        
        text_lower = text.lower()
        total_matches = 0
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            # Count exact matches and partial matches
            exact_matches = len(re.findall(r'\b' + re.escape(keyword_lower) + r'\b', text_lower))
            partial_matches = text_lower.count(keyword_lower) - exact_matches
            
            # Weight exact matches higher
            total_matches += exact_matches * 2 + partial_matches
        
        # Normalize by text length and keyword count
        text_length = len(text.split())
        max_possible_score = len(keywords) * 2
        
        if text_length == 0 or max_possible_score == 0:
            return 0.0
        
        # Calculate relevance score
        relevance = min(total_matches / max_possible_score, 1.0)
        return relevance
    
    def categorize_review(self, text: str) -> List[str]:
        """
        Categorize review based on content.
        
        Args:
            text: Review text to categorize
            
        Returns:
            List of matching categories
        """
        if not text:
            return []
        
        text_lower = text.lower()
        matching_categories = []
        
        for category, keywords in self.criteria_keywords.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    matching_categories.append(category)
                    break  # Found match for this category
        
        return matching_categories
    
    def filter_reviews(self, reviews: List[Dict[str, Any]], filter_config: ReviewFilter) -> List[Dict[str, Any]]:
        """
        Filter and sort reviews based on criteria.
        
        Args:
            reviews: List of review dictionaries
            filter_config: Filtering configuration
            
        Returns:
            Filtered and sorted reviews
        """
        if not reviews:
            return []
        
        filtered_reviews = []
        
        for review in reviews:
            # Skip if review doesn't meet basic criteria
            rating = float(review.get('rating', 0))
            if rating < filter_config.min_rating or rating > filter_config.max_rating:
                continue
            
            review_text = str(review.get('review_text', ''))
            
            # Sentiment filtering
            if filter_config.sentiment:
                review_sentiment = self.analyze_sentiment(review_text)
                if review_sentiment != filter_config.sentiment:
                    continue
            
            # Enhanced review data
            enhanced_review = review.copy()
            enhanced_review['sentiment'] = self.analyze_sentiment(review_text)
            enhanced_review['categories'] = self.categorize_review(review_text)
            
            # Keyword relevance
            if filter_config.keywords:
                relevance = self.calculate_keyword_relevance(review_text, filter_config.keywords)
                enhanced_review['keyword_relevance'] = relevance
                enhanced_review['relevance_percentage'] = f"{relevance * 100:.1f}%"
                
                # Only include reviews with some relevance
                if relevance > 0.1:  # 10% threshold
                    filtered_reviews.append(enhanced_review)
            else:
                enhanced_review['keyword_relevance'] = 1.0
                enhanced_review['relevance_percentage'] = "100%"
                filtered_reviews.append(enhanced_review)
            
            # Category filtering
            if filter_config.categories:
                review_categories = set(enhanced_review['categories'])
                filter_categories = set(filter_config.categories)
                if not review_categories.intersection(filter_categories):
                    continue
        
        # Sort reviews
        filtered_reviews = self._sort_reviews(filtered_reviews, filter_config.sort_by)
        
        # Limit results
        return filtered_reviews[:filter_config.limit]
    
    def _sort_reviews(self, reviews: List[Dict[str, Any]], sort_by: str) -> List[Dict[str, Any]]:
        """Sort reviews by specified criteria."""
        if sort_by == 'relevance':
            return sorted(reviews, key=lambda r: r.get('keyword_relevance', 0), reverse=True)
        elif sort_by == 'rating':
            return sorted(reviews, key=lambda r: float(r.get('rating', 0)), reverse=True)
        elif sort_by == 'date':
            return sorted(reviews, key=lambda r: r.get('date', ''), reverse=True)
        elif sort_by == 'length':
            return sorted(reviews, key=lambda r: len(str(r.get('review_text', ''))), reverse=True)
        else:
            return reviews
    
    def get_review_insights(self, reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate insights from filtered reviews.
        
        Args:
            reviews: List of review dictionaries
            
        Returns:
            Insights dictionary
        """
        if not reviews:
            return {}
        
        # Category distribution
        all_categories = []
        sentiments = []
        ratings = []
        
        for review in reviews:
            all_categories.extend(review.get('categories', []))
            sentiments.append(review.get('sentiment', 'neutral'))
            ratings.append(float(review.get('rating', 0)))
        
        category_counts = Counter(all_categories)
        sentiment_counts = Counter(sentiments)
        
        return {
            'total_reviews': len(reviews),
            'average_rating': sum(ratings) / len(ratings) if ratings else 0,
            'category_breakdown': dict(category_counts.most_common()),
            'sentiment_breakdown': dict(sentiment_counts),
            'top_categories': [cat for cat, _ in category_counts.most_common(5)],
            'rating_distribution': {
                '5_star': len([r for r in ratings if r >= 4.5]),
                '4_star': len([r for r in ratings if 3.5 <= r < 4.5]),
                '3_star': len([r for r in ratings if 2.5 <= r < 3.5]),
                '2_star': len([r for r in ratings if 1.5 <= r < 2.5]),
            }
        }


def create_enterprise_filter(platform: str, keywords: List[str] = None, **kwargs) -> ReviewFilter:
    """
    Create an enterprise-grade filter optimized for specific platforms.
    
    Args:
        platform: Platform name (amazon, walmart, yelp, etc.)
        keywords: Keywords to filter by
        **kwargs: Additional filter parameters
        
    Returns:
        Optimized ReviewFilter for the platform
    """
    # Platform-specific optimizations
    platform_defaults = {
        'amazon': {
            'min_rating': 1.0,
            'max_rating': 5.0,
            'sort_by': 'relevance',
            'limit': 100
        },
        'walmart': {
            'min_rating': 1.0,
            'max_rating': 5.0,
            'sort_by': 'relevance',
            'limit': 75
        },
        'yelp': {
            'min_rating': 1.0,
            'max_rating': 5.0,
            'sort_by': 'relevance',
            'limit': 50
        },
        'target': {
            'min_rating': 1.0,
            'max_rating': 5.0,
            'sort_by': 'relevance',
            'limit': 75
        }
    }
    
    defaults = platform_defaults.get(platform.lower(), platform_defaults['amazon'])
    
    # Merge with custom parameters
    filter_params = {**defaults, **kwargs}
    filter_params['keywords'] = keywords
    
    return ReviewFilter(**filter_params)


def analyze_review_authenticity(review: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze review authenticity using advanced heuristics.
    
    Args:
        review: Review dictionary
        
    Returns:
        Authenticity analysis results
    """
    review_text = str(review.get('review_text', ''))
    reviewer_name = str(review.get('reviewer_name', ''))
    rating = float(review.get('rating', 0))
    
    authenticity_score = 1.0
    flags = []
    
    # Text analysis
    if len(review_text) < 20:
        authenticity_score -= 0.3
        flags.append('very_short_text')
    
    if len(review_text) > 2000:
        authenticity_score -= 0.1
        flags.append('very_long_text')
    
    # Generic patterns
    generic_patterns = [
        r'\b(great|good|nice|awesome|amazing|excellent)\s+product\b',
        r'\bwould\s+recommend\b',
        r'\b(five|5)\s+stars?\b',
        r'\bbuy\s+this\b'
    ]
    
    generic_matches = sum(1 for pattern in generic_patterns 
                         if re.search(pattern, review_text, re.IGNORECASE))
    
    if generic_matches >= 3:
        authenticity_score -= 0.2
        flags.append('generic_language')
    
    # Rating vs text sentiment mismatch
    analyzer = ReviewAnalyzer()
    sentiment = analyzer.analyze_sentiment(review_text)
    
    if rating >= 4 and sentiment == 'negative':
        authenticity_score -= 0.4
        flags.append('rating_sentiment_mismatch')
    elif rating <= 2 and sentiment == 'positive':
        authenticity_score -= 0.4
        flags.append('rating_sentiment_mismatch')
    
    # Reviewer name analysis
    if re.match(r'^[A-Z][a-z]+\s[A-Z]\.$', reviewer_name):
        authenticity_score += 0.1  # Real name pattern
    elif 'Amazon Customer' in reviewer_name or 'Anonymous' in reviewer_name:
        authenticity_score -= 0.1
        flags.append('anonymous_reviewer')
    
    # Clamp score between 0 and 1
    authenticity_score = max(0.0, min(1.0, authenticity_score))
    
    return {
        'authenticity_score': round(authenticity_score, 2),
        'authenticity_percentage': f"{authenticity_score * 100:.1f}%",
        'is_likely_authentic': authenticity_score >= 0.6,
        'flags': flags,
        'confidence': 'high' if len(flags) <= 1 else 'medium' if len(flags) <= 3 else 'low'
    }


def create_filter_from_params(request_args: Dict[str, Any]) -> ReviewFilter:
    """
    Create ReviewFilter from request parameters.
    
    Args:
        request_args: Request arguments dictionary
        
    Returns:
        ReviewFilter configuration
    """
    keywords = []
    if request_args.get('keywords'):
        keywords = [k.strip() for k in str(request_args['keywords']).split(',')]
    
    categories = []
    if request_args.get('categories'):
        categories = [c.strip() for c in str(request_args['categories']).split(',')]
    
    return ReviewFilter(
        keywords=keywords,
        categories=categories,
        min_rating=float(request_args.get('min_rating', 0)),
        max_rating=float(request_args.get('max_rating', 5)),
        sentiment=request_args.get('sentiment'),
        sort_by=request_args.get('sort_by', 'relevance'),
        limit=int(request_args.get('limit', 50))
    )
