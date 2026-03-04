"""Tests for rules engine module."""

import pytest
from utils.rules_engine import RulesEngine


class TestRulesEngine:
    """Test cases for RulesEngine class."""

    @pytest.fixture
    def engine(self):
        """Create a RulesEngine instance."""
        return RulesEngine()

    def test_passes_valid_analysis(self, engine):
        """Test that valid analysis passes."""
        analysis = {
            'confidence': 0.8,
            'mention_count': 100,
            'sentiment_score': 60
        }
        
        assert engine.passes(analysis) is True

    def test_passes_low_confidence(self, engine):
        """Test filtering by confidence threshold."""
        analysis = {
            'confidence': 0.1,
            'mention_count': 100,
            'sentiment_score': 60
        }
        
        assert engine.passes(analysis) is False

    def test_passes_low_mentions(self, engine):
        """Test filtering by mention count."""
        analysis = {
            'confidence': 0.8,
            'mention_count': 5,
            'sentiment_score': 60
        }
        
        assert engine.passes(analysis) is False

    def test_passes_bearish_sentiment(self, engine):
        """Test filtering by bearish sentiment."""
        analysis = {
            'confidence': 0.8,
            'mention_count': 100,
            'sentiment_score': 20
        }
        
        assert engine.passes(analysis) is False

    def test_get_violations(self, engine):
        """Test getting violation details."""
        analysis = {
            'confidence': 0.1,
            'mention_count': 5,
            'sentiment_score': 20
        }
        
        violations = engine.get_violations(analysis)
        
        assert len(violations) > 0
        assert any('confidence' in v.lower() for v in violations)

    def test_apply_batch_filter(self, engine):
        """Test batch filtering."""
        results = [
            {'coin': 'PEPE', 'confidence': 0.8, 'mention_count': 100, 'sentiment_score': 60},
            {'coin': 'SHIB', 'confidence': 0.1, 'mention_count': 100, 'sentiment_score': 60},
            {'coin': 'DOGE', 'confidence': 0.8, 'mention_count': 5, 'sentiment_score': 60},
        ]
        
        filtered = engine.apply(results)
        
        assert len(filtered) == 1
        assert filtered[0]['coin'] == 'PEPE'
