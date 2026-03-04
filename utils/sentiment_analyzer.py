"""Sentiment analysis module with support for multiple models.

Supports:
- TextBlob: Lightweight, no GPU required
- RoBERTa: High accuracy transformer model from Hugging Face
"""

import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import logging

# Try to import optional dependencies
try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False

try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class SentimentResult:
    """Container for sentiment analysis results."""
    sentiment: str  # 'bullish', 'neutral', 'bearish'
    score: float  # 0-100 scale
    confidence: float  # 0-1
    texts_analyzed: int
    polarity_range: tuple  # (min, max)
    model_used: str


class SentimentAnalyzer:
    """Sentiment analyzer with support for multiple backends.
    
    Supports TextBlob (default, lightweight) and RoBERTa (accurate).
    """
    
    def __init__(self, model: str = "textblob"):
        """Initialize sentiment analyzer.
        
        Args:
            model: Model to use - 'textblob' or 'roberta'
        """
        self.model_name = model
        self._textblob_analyzer = None
        self._roberta_pipeline = None
        
        if model == "roberta" and not TRANSFORMERS_AVAILABLE:
            logger.warning("Transformers not available, falling back to TextBlob")
            self.model_name = "textblob"
        
        self._initialize_analyzer()
    
    def _initialize_analyzer(self):
        """Initialize the selected model."""
        if self.model_name == "textblob":
            self._initialize_textblob()
        elif self.model_name == "roberta":
            self._initialize_roberta()
    
    def _initialize_textblob(self):
        """Initialize TextBlob analyzer."""
        if TEXTBLOB_AVAILABLE:
            logger.info("Initialized TextBlob sentiment analyzer")
        else:
            logger.error("TextBlob not available. Install with: pip install textblob")
            raise ImportError("TextBlob not available")
    
    def _initialize_roberta(self):
        """Initialize RoBERTa model."""
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError("Transformers not available. Install with: pip install transformers torch")
        
        try:
            # Use the Twitter-specific RoBERTa model for crypto/social media text
            self._roberta_pipeline = pipeline(
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                device=-1,  # CPU (use 0 for GPU)
                truncation=True,
                max_length=512
            )
            logger.info("Initialized RoBERTa sentiment analyzer")
        except Exception as e:
            logger.error(f"Failed to load RoBERTa model: {e}")
            logger.info("Falling back to TextBlob")
            self.model_name = "textblob"
            self._initialize_textblob()
    
    def analyze(self, texts: List[str]) -> SentimentResult:
        """Analyze sentiment of multiple texts.
        
        Args:
            texts: List of text strings to analyze
            
        Returns:
            SentimentResult with aggregated sentiment
        """
        if not texts:
            return SentimentResult(
                sentiment="neutral",
                score=50,
                confidence=0.0,
                texts_analyzed=0,
                polarity_range=(0, 0),
                model_used=self.model_name
            )
        
        if self.model_name == "roberta":
            return self._analyze_roberta(texts)
        else:
            return self._analyze_textblob(texts)
    
    def _analyze_textblob(self, texts: List[str]) -> SentimentResult:
        """Analyze using TextBlob."""
        polarities = []
        subjectivities = []
        
        for text in texts:
            try:
                blob = TextBlob(text)
                polarities.append(blob.sentiment.polarity)
                subjectivities.append(blob.sentiment.subjectivity)
            except Exception as e:
                logger.debug(f"Error analyzing text: {e}")
                continue
        
        if not polarities:
            return SentimentResult(
                sentiment="neutral",
                score=50,
                confidence=0.0,
                texts_analyzed=0,
                polarity_range=(0, 0),
                model_used="textblob"
            )
        
        avg_polarity = sum(polarities) / len(polarities)
        avg_subjectivity = sum(subjectivities) / len(subjectivities)
        
        # Convert polarity (-1 to 1) to score (0 to 100)
        score = ((avg_polarity + 1) / 2) * 100
        confidence = 1 - avg_subjectivity
        
        return SentimentResult(
            sentiment=self.get_sentiment_label(score),
            score=score,
            confidence=confidence,
            texts_analyzed=len(texts),
            polarity_range=(min(polarities), max(polarities)),
            model_used="textblob"
        )
    
    def _analyze_roberta(self, texts: List[str]) -> SentimentResult:
        """Analyze using RoBERTa model."""
        if not self._roberta_pipeline:
            return self._analyze_textblob(texts)
        
        try:
            # Batch process texts for efficiency
            results = self._roberta_pipeline(texts)
            
            # Aggregate results
            label_scores = {"bearish": 0, "neutral": 0, "bullish": 0}
            total_score = 0
            total_confidence = 0
            valid_count = 0
            
            for result in results:
                label = result["label"].lower()
                score = result["score"]
                
                # Map to 0-100 scale
                if label == "bullish":
                    label_scores["bullish"] += score
                    total_score += (50 + 50 * score)
                elif label == "bearish":
                    label_scores["bearish"] += score
                    total_score += (50 - 50 * score)
                else:
                    label_scores["neutral"] += score
                    total_score += 50
                
                total_confidence += score
                valid_count += 1
            
            if valid_count == 0:
                return self._analyze_textblob(texts)
            
            avg_score = total_score / valid_count
            avg_confidence = total_confidence / valid_count
            
            # Determine dominant sentiment
            dominant = max(label_scores, key=label_scores.get)
            
            return SentimentResult(
                sentiment=dominant,
                score=avg_score,
                confidence=avg_confidence,
                texts_analyzed=len(texts),
                polarity_range=(0, 0),  # Not applicable for RoBERTa
                model_used="roberta"
            )
            
        except Exception as e:
            logger.error(f"RoBERTa analysis failed: {e}")
            return self._analyze_textblob(texts)
    
    def analyze_single(self, text: str) -> Dict[str, Any]:
        """Analyze a single text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with sentiment results
        """
        result = self.analyze([text])
        return {
            "sentiment": result.sentiment,
            "score": result.score,
            "confidence": result.confidence,
            "model": result.model_used
        }
    
    @staticmethod
    def get_sentiment_label(score: float) -> str:
        """Map score to sentiment label.
        
        Args:
            score: Score on 0-100 scale
            
        Returns:
            'bullish', 'neutral', or 'bearish'
        """
        if score >= 50:
            return "bullish"
        elif score <= 30:
            return "bearish"
        else:
            return "neutral"
    
    @classmethod
    def create_roberta(cls) -> "SentimentAnalyzer":
        """Factory method to create RoBERTa-based analyzer.
        
        Returns:
            SentimentAnalyzer configured with RoBERTa
        """
        return cls(model="roberta")
    
    @classmethod
    def create_auto(cls) -> "SentimentAnalyzer":
        """Factory method to auto-select best available model.
        
        Returns:
            SentimentAnalyzer with best available model
        """
        if TRANSFORMERS_AVAILABLE:
            return cls(model="roberta")
        return cls(model="textblob")


# Backwards compatibility
def get_analyzer(model: str = "textblob") -> SentimentAnalyzer:
    """Get sentiment analyzer instance.
    
    Args:
        model: Model to use
        
    Returns:
        SentimentAnalyzer instance
    """
    return SentimentAnalyzer(model=model)
