"""CoinGecko API client for market data."""

import time
import requests
from typing import Optional, Dict, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class CoinGeckoClient:
    """Client for CoinGecko API."""
    
    def __init__(self, base_url: str = "https://api.coingecko.com/api/v3",
                 rate_limit: int = 10, timeout: int = 30):
        self.base_url = base_url
        self.rate_limit = rate_limit
        self.timeout = timeout
        self.last_request = 0
        self._history = {}  # coin_id -> list of historical data points
    
    def _rate_limit_wait(self):
        """Wait to respect rate limits."""
        elapsed = time.time() - self.last_request
        min_interval = 60 / self.rate_limit
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
        self.last_request = time.time()
    
    def get_coin_data(self, coin_id: str) -> Dict:
        """Get current and historical data for a coin."""
        self._rate_limit_wait()
        
        url = f"{self.base_url}/coins/{coin_id}"
        params = {
            'localization': 'false',
            'tickers': 'false',
            'market_data': 'true',
            'community_data': 'false',
            'developer_data': 'false',
            'sparkline': 'false'
        }
        
        try:
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            market_data = data.get('market_data', {})
            result = {
                'coin_id': coin_id,
                'symbol': data.get('symbol', '').upper(),
                'name': data.get('name', ''),
                'current_price': market_data.get('current_price', {}).get('usd', 0),
                'price_change_24h': market_data.get('price_change_percentage_24h', 0),
                'price_change_7d': market_data.get('price_change_percentage_7d', 0),
                'market_cap': market_data.get('market_cap', {}).get('usd', 0),
                'volume_24h': market_data.get('total_volume', {}).get('usd', 0),
                'market_cap_rank': market_data.get('market_cap_rank', 0),
                'ath': market_data.get('ath', {}).get('usd', 0),
                'atl': market_data.get('atl', {}).get('usd', 0),
                'last_updated': market_data.get('last_updated', '')
            }
            
            # Store for historical comparison
            self._update_history(coin_id, result)
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching {coin_id}: {e}")
            return self._get_empty_data(coin_id)
    
    def _update_history(self, coin_id: str, data: Dict):
        """Update historical data for a coin."""
        if coin_id not in self._history:
            self._history[coin_id] = []
        
        self._history[coin_id].append({
            'timestamp': datetime.now(),
            'price': data['current_price'],
            'volume': data['volume_24h']
        })
        
        # Keep only last 24 hours
        cutoff = datetime.now() - timedelta(hours=24)
        self._history[coin_id] = [
            h for h in self._history[coin_id]
            if h['timestamp'] > cutoff
        ]
    
    def get_historical_stats(self, coin_id: str) -> Dict:
        """Get historical statistics for a coin."""
        if coin_id not in self._history or len(self._history[coin_id]) < 2:
            return {
                'volume_change_24h': 0,
                'price_change_24h': 0,
                'data_points': 0
            }
        
        history = self._history[coin_id]
        oldest = history[0]
        newest = history[-1]
        
        volume_change = 0
        if oldest['volume'] > 0:
            volume_change = ((newest['volume'] - oldest['volume']) / oldest['volume']) * 100
        
        price_change = 0
        if oldest['price'] > 0:
            price_change = ((newest['price'] - oldest['price']) / oldest['price']) * 100
        
        return {
            'volume_change_24h': volume_change,
            'price_change_24h': price_change,
            'data_points': len(history)
        }
    
    def _get_empty_data(self, coin_id: str) -> Dict:
        """Return empty data structure."""
        return {
            'coin_id': coin_id,
            'symbol': '',
            'name': '',
            'current_price': 0,
            'price_change_24h': 0,
            'price_change_7d': 0,
            'market_cap': 0,
            'volume_24h': 0,
            'market_cap_rank': 0,
            'ath': 0,
            'atl': 0,
            'last_updated': ''
        }
    
    def get_market_chart(self, coin_id: str, days: int = 7) -> Dict:
        """Get market chart data."""
        self._rate_limit_wait()
        
        url = f"{self.base_url}/coins/{coin_id}/market_chart"
        params = {'vs_currency': 'usd', 'days': days}
        
        try:
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching chart for {coin_id}: {e}")
            return {'prices': [], 'volumes': []}
