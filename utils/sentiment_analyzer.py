"""Sentiment analysis using TextBlob and NLTK."""

from typing import List, Dict
from textblob import TextBlob
import logging

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """Analyze sentiment from text data."""
    
    def __init__(self, min_confidence: float = 0.3):
        self.min_confidence = min_confidence
    
    def analyze(self, texts: List[str]) -> Dict:
        """Analyze sentiment from a list of texts."""
        if not texts:
            return self._empty_result()
        
        sentiments = []
        for text in texts:
            try:
                blob = TextBlob(text)
                polarity = blob.sentiment.polarity
                subjectivity = blob.sentiment.subjectivity
                
                # Convert polarity to 0-100 scale
                sentiment_score = (polarity + 1) * 50  # -1 to 1 -> 0 to 100
                
                # Confidence based on subjectivity (less subjective = more confident)
                confidence = 1 - subjectivity
                
                sentiments.append({
                    'polarity': polarity,
                    'subjectivity': subjectivity,
                    'score': sentiment_score,
                    'confidence': confidence,
                    'text': text[:100]  # Truncate for storage
                })
            except Exception as e:
                logger.debug(f"Error analyzing text: {e}")
        
        if not sentiments:
            return self._empty_result()
        
        # Calculate aggregate metrics
        avg_score = sum(s['score'] for s in sentiments) / len(sentiments)
        avg_confidence = sum(s['confidence'] for s in sentiments) / len(sentiments)
        
        # Determine overall sentiment
        if avg_score >= 50:
            sentiment_label = "bullish"
        elif avg_score <= 30:
            sentiment_label = "bearish"
        else:
            sentiment_label = "neutral"
        
        return {
            'sentiment': sentiment_label,
            'score': avg_score,
            'confidence': avg_confidence,
            'texts_analyzed': len(texts),
            'individual_scores': [s['score'] for s in sentiments],
            'polarity_range': {
                'min': min(s['polarity'] for s in sentiments),
                'max': max(s['polarity'] for s in sentiments)
            }
        }
    
    def analyze_single(self, text: str) -> Dict:
        """Analyze sentiment of a single text."""
        result = self.analyze([text])
        return result
    
    def _empty_result(self) -> Dict:
        """Return empty result structure."""
        return {
            'sentiment': 'neutral',
            'score': 50,
            'confidence': 0,
            'texts_analyzed': 0,
            'individual_scores': [],
            'polarity_range': {'min': 0, 'max': 0}
        }
    
    def get_sentiment_label(self, score: float) -> str:
        """Get sentiment label from score."""
        if score >= 50:
            return "bullish"
        elif score <= 30:
            return "bearish"
        else:
            return "neutral"
