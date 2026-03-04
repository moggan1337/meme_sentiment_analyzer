"""Tests for CoinGecko data source."""

import pytest
from data_sources.coingecko import CoinGeckoClient


class TestCoinGeckoClient:
    """Test cases for CoinGeckoClient class."""

    @pytest.fixture
    def client(self):
        """Create a CoinGeckoClient instance."""
        return CoinGeckoClient()

    def test_client_initialization(self, client):
        """Test client initializes correctly."""
        assert client is not None
        assert hasattr(client, 'base_url')

    def test_get_coin_data(self, client):
        """Test fetching coin data."""
        data = client.get_coin_data('bitcoin')
        
        assert data is not None
        if data:
            assert 'symbol' in data or data == {}

    def test_get_coin_data_invalid(self, client):
        """Test fetching data for invalid coin."""
        data = client.get_coin_data('invalid_coin_12345')
        
        # Should return empty or error gracefully
        assert data is not None

    def test_get_market_chart(self, client):
        """Test fetching market chart data."""
        data = client.get_market_chart('bitcoin', days=1)
        
        assert data is not None
