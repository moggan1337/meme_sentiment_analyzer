"""Coin ranking and scoring logic."""

import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class CoinRanker:
    """Handles composite scoring and ranking of meme coins."""

    def __init__(self, config: dict):
        """Initialize ranker with configuration."""
        self.config = config
        self.sentiment_config = config.get('sentiment', {})
        self.analysis_config = config.get('analysis', {})
        
        # Thresholds
        self.min_confidence = self.sentiment_config.get('min_confidence', 0.3)
        self.bullish_threshold = self.sentiment_config.get('bullish_threshold', 50)
        self.bearish_threshold = self.sentiment_config.get('bearish_threshold', -50)
        
        # Weights
        self.weights = self.sentiment_config.get('weights', {
            'social': 0.4,
            'news': 0.3,
            'technical': 0.2,
            'fundamentals': 0.1
        })

    def calculate_score(self, analysis: dict) -> dict:
        """Calculate composite score for a coin."""
        sentiment = analysis.get('sentiment', {})
        market = analysis.get('market', {})
        social = analysis.get('social', {})
        
        # Extract components
        sentiment_score = sentiment.get('score', 0)
        confidence = sentiment.get('confidence', 0)
        mention_count = social.get('mention_count', 0)
        mention_growth = social.get('mention_growth', 0)
        volume_change = market.get('volume_change_24h', 0)
        price_change = market.get('price_change_24h', 0)
        
        # Skip if below minimum confidence
        if confidence < self.min_confidence:
            return {'valid': False, 'reason': 'low_confidence'}
        
        # Skip if sentiment is bearish
        if sentiment_score < self.bearish_threshold:
            return {'valid': False, 'reason': 'bearish'}
        
        # Calculate weighted components
        social_score = self._score_social(mention_count, mention_growth)
        volume_score = self._score_volume(volume_change)
        price_score = self._score_price(price_change)
        
        # Weighted composite
        composite = (
            (sentiment_score * self.weights.get('social', 0.4)) +
            (social_score * 0.3) +
            (volume_score * self.weights.get('technical', 0.2)) +
            (price_score * self.weights.get('fundamentals', 0.1))
        )
        
        return {
            'valid': True,
            'composite': composite,
            'sentiment': sentiment_score,
            'confidence': confidence,
            'social_score': social_score,
            'volume_score': volume_score,
            'price_score': price_score,
            'mention_count': mention_count,
            'mention_growth': mention_growth,
            'price_change': price_change,
            'volume_change': volume_change
        }

    def _score_social(self, mentions: int, growth: float) -> float:
        """Score social metrics."""
        min_mentions = self.analysis_config.get('min_mentions', 10)
        
        mention_score = min(mentions / min_mentions, 1.0) * 50 if mentions >= min_mentions else 0
        growth_score = min(max(growth, 0) / 100, 1.0) * 50
        
        return mention_score + growth_score

    def _score_volume(self, volume_change: float) -> float:
        """Score volume change (0-100)."""
        return min(max(volume_change, 0) / 20, 1.0) * 100

    def _score_price(self, price_change: float) -> float:
        """Score price change (0-100)."""
        return min(max(price_change, 0) / 5, 1.0) * 100

    def rank(self, results: List[dict]) -> List[dict]:
        """Rank coins by composite score."""
        ranked = []
        
        for r in results:
            score = r.get('score', {})
            if score.get('valid', False):
                r['rank_score'] = score['composite']
                ranked.append(r)
        
        # Sort by composite score descending
        ranked.sort(key=lambda x: x['rank_score'], reverse=True)
        
        # Limit to top N
        top_n = self.analysis_config.get('top_n', 10)
        return ranked[:top_n]


def calculate_weighted_score(sentiment: float, mentions: int, volume: float, 
                             price: float, weights: dict) -> float:
    """
    Calculate weighted composite score.
    
    Formula:
    score = (sentiment * W_social) + (mention_score * 0.3) + (volume_score * 0.2) + (price_score * 0.1)
    
    Args:
        sentiment: Sentiment score (-100 to 100)
        mentions: Number of social mentions
        volume: Volume change percentage
        price: Price change percentage
        weights: Dictionary of component weights
    
    Returns:
        Composite score (0-100)
    """
    # Normalize sentiment to 0-100 range
    sentiment_normalized = (sentiment + 100) / 2
    
    # Normalize other metrics
    mention_score = min(mentions / 1000, 1.0) * 100
    volume_score = min(max(volume, 0) / 50, 1.0) * 100
    price_score = min(max(price, 0) / 20, 1.0) * 100
    
    # Apply weights
    w = weights
    composite = (
        sentiment_normalized * w.get('social', 0.4) +
        mention_score * 0.3 +
        volume_score * w.get('technical', 0.2) +
        price_score * w.get('fundamentals', 0.1)
    )
    
    return round(composite, 2)
