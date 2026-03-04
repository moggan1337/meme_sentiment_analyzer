"""Tests for ranker module."""

import pytest
from engine.ranker import CoinRanker, calculate_weighted_score


class TestCoinRanker:
    """Test cases for CoinRanker class."""

    @pytest.fixture
    def ranker(self):
        """Create a CoinRanker instance."""
        return CoinRanker()

    def test_calculate_score_high_performing(self, ranker):
        """Test scoring for high-performing coin."""
        data = {
            'sentiment': 80,
            'mention_count': 500,
            'mention_growth': 100,
            'volume_change': 50,
            'price_change': 10
        }
        
        score = ranker.calculate_score(data)
        
        assert score >= 70

    def test_calculate_score_low_performing(self, ranker):
        """Test scoring for low-performing coin."""
        data = {
            'sentiment': 20,
            'mention_count': 10,
            'mention_growth': -10,
            'volume_change': -5,
            'price_change': -5
        }
        
        score = ranker.calculate_score(data)
        
        assert score < 30

    def test_rank_returns_sorted_list(self, ranker):
        """Test that rank returns sorted results."""
        coins = [
            {'coin': 'PEPE', 'score': 60},
            {'coin': 'SHIB', 'score': 80},
            {'coin': 'DOGE', 'score': 70},
        ]
        
        ranked = ranker.rank(coins, top_n=3)
        
        assert ranked[0]['coin'] == 'SHIB'
        assert ranked[1]['coin'] == 'DOGE'
        assert ranked[2]['coin'] == 'PEPE'

    def test_rank_limits_results(self, ranker):
        """Test that rank limits results to top_n."""
        coins = [
            {'coin': f'COIN{i}', 'score': 100 - i * 10}
            for i in range(10)
        ]
        
        ranked = ranker.rank(coins, top_n=3)
        
        assert len(ranked) == 3


class TestWeightedScore:
    """Test cases for weighted score calculation."""

    def test_calculate_weighted_score(self):
        """Test weighted score calculation."""
        score = calculate_weighted_score(
            sentiment=80,
            social_score=100,
            volume=50,
            price=10
        )
        
        assert 0 <= score <= 100

    def test_calculate_weighted_score_low_values(self):
        """Test weighted score with low values."""
        score = calculate_weighted_score(
            sentiment=10,
            social_score=10,
            volume=0,
            price=-5
        )
        
        assert score < 30
