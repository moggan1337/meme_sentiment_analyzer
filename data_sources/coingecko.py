"""CoinGecko API connector for market data."""

import logging
from typing import Optional, Dict, List
import requests

logger = logging.getLogger(__name__)


class CoinGeckoConnector:
    """Connector for CoinGecko API."""

    BASE_URL = "https://api.coingecko.com/api/v3"
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize connector with optional API key."""
        self.api_key = api_key
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({
                'x-cg-demo-api-key': api_key
            })
    
    def _map_symbol(self, symbol: str) -> str:
        """Map common meme coin symbols to CoinGecko IDs."""
        mapping = {
            'SHIB': 'shiba-inu',
            'DOGE': 'dogecoin',
            'PEPE': 'pepe',
            'FLOKI': 'floki',
            'BONK': 'bonk',
            'WIF': 'dogwifhat',
            'BRETT': 'brett',
            'MOG': 'mog-coin',
            'GUY': 'guy',
        }
        return mapping.get(symbol.upper(), symbol.lower())
    
    async def get_coin_data(self, symbol: str) -> Dict:
        """Fetch market data for a coin."""
        coin_id = self._map_symbol(symbol)
        
        try:
            url = f"{self.BASE_URL}/coins/{coin_id}"
            params = {
                'localization': 'false',
                'tickers': 'false',
                'community_data': 'false',
                'developer_data': 'false',
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            market_data = data.get('market_data', {})
            
            return {
                'price': market_data.get('current_price', {}).get('usd', 0),
                'price_change_24h': market_data.get('price_change_percentage_24h', 0),
                'price_change_7d': market_data.get('price_change_percentage_7d', 0),
                'volume_24h': market_data.get('total_volume', {}).get('usd', 0),
                'volume_change_24h': market_data.get('volume_change_percentage_24h', 0),
                'market_cap': market_data.get('market_cap', {}).get('usd', 0),
                'market_cap_rank': data.get('market_cap_rank'),
                'circulating_supply': market_data.get('circulating_supply'),
                'ath': market_data.get('ath', {}).get('usd'),
                'atl': market_data.get('atl', {}).get('usd'),
            }
            
        except requests.RequestException as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return self._empty_data()
    
    async def get_multiple_coins(self, symbols: List[str]) -> Dict[str, Dict]:
        """Fetch data for multiple coins."""
        results = {}
        for symbol in symbols:
            results[symbol] = await self.get_coin_data(symbol)
        return results
    
    def _empty_data(self) -> Dict:
        """Return empty data structure."""
        return {
            'price': 0,
            'price_change_24h': 0,
            'price_change_7d': 0,
            'volume_24h': 0,
            'volume_change_24h': 0,
            'market_cap': 0,
            'market_cap_rank': None,
            'circulating_supply': 0,
            'ath': None,
            'atl': None,
        }
