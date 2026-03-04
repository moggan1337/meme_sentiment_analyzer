"""Tests for sentiment analyzer module."""

import pytest
from utils.sentiment_analyzer import SentimentAnalyzer


class TestSentimentAnalyzer:
    """Test cases for SentimentAnalyzer class."""

    @pytest.fixture
    def analyzer(self):
        """Create a SentimentAnalyzer instance."""
        return SentimentAnalyzer()

    def test_analyze_bullish_text(self, analyzer):
        """Test analysis of bullish text."""
        texts = ["This coin is going to the moon!", "Bullish on this!", "To the moon!"]
        result = analyzer.analyze(texts)
        
        assert result['sentiment'] == 'bullish'
        assert result['score'] >= 50
        assert result['texts_analyzed'] == 3

    def test_analyze_bearish_text(self, analyzer):
        """Test analysis of bearish text."""
        texts = ["This coin is going to zero", "Bearish on this", "Dump incoming"]
        result = analyzer.analyze(texts)
        
        assert result['sentiment'] == 'bearish'
        assert result['score'] <= 30

    def test_analyze_empty_list(self, analyzer):
        """Test analysis with empty input."""
        result = analyzer.analyze([])
        
        assert result['sentiment'] == 'neutral'
        assert result['score'] == 50
        assert result['texts_analyzed'] == 0

    def test_analyze_single_text(self, analyzer):
        """Test single text analysis."""
        result = analyzer.analyze_single("To the moon!")
        
        assert 'sentiment' in result
        assert 'score' in result
        assert 'confidence' in result

    def test_get_sentiment_label(self, analyzer):
        """Test sentiment label mapping."""
        assert analyzer.get_sentiment_label(70) == 'bullish'
        assert analyzer.get_sentiment_label(30) == 'bearish'
        assert analyzer.get_sentiment_label(50) == 'neutral'
