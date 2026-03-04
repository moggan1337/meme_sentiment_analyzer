"""Sentiment analysis using TextBlob and NLTK."""

import logging
from typing import List, Dict
from textblob import TextBlob

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """Analyzes sentiment from text data."""

    def __init__(self):
        """Initialize analyzer with NLTK data."""
        try:
            import nltk
            nltk.download('punkt', quiet=True)
            nltk.download('averaged_perceptron_tagger', quiet=True)
        except Exception as e:
            logger.warning(f"NLTK download issue: {e}")

    def analyze(self, texts: List[str]) -> Dict:
        """Analyze sentiment from list of texts."""
        if not texts:
            return self._neutral_result()
        
        scores = []
        confidences = []
        
        for text in texts:
            try:
                blob = TextBlob(str(text))
                # polarity: -1 (negative) to 1 (positive)
                polarity = blob.sentiment.polarity
                # subjectivity: 0 (objective) to 1 (subjective)
                subjectivity = blob.sentiment.subjectivity
                
                # Convert to 0-100 scale (100 = very bullish)
                score = ((polarity + 1) / 2) * 100
                confidence = (1 - subjectivity) * 100
                
                scores.append(score)
                confidences.append(confidence)
                
            except Exception as e:
                logger.debug(f"Error analyzing text: {e}")
        
        if not scores:
            return self._neutral_result()
        
        # Weight by confidence
        weighted_sum = sum(s * c for s, c in zip(scores, confidences))
        total_conf = sum(confidences)
        
        avg_score = weighted_sum / total_conf if total_conf > 0 else 50
        avg_confidence = sum(confidences) / len(confidences)
        
        return {
            'score': round(avg_score - 50, 2),  # Convert to -50 to +50 scale
            'confidence': round(avg_confidence, 2),
            'text_count': len(texts),
            'raw_score': round(avg_score, 2)
        }

    def analyze_single(self, text: str) -> Dict:
        """Analyze single text."""
        return self.analyze([text])

    def _neutral_result(self) -> Dict:
        """Return neutral result."""
        return {
            'score': 0,
            'confidence': 0,
            'text_count': 0,
            'raw_score': 50
        }
