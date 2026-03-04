"""Data sources package.

Provides connectors for various data sources:
- CoinGecko: Market data (prices, volume, market cap)
- Reddit: Social media mentions
- Twitter/X: Social media mentions
- Discord: Server mentions
"""

from .base import DataSource, DataItem, MarketData, SourceType
from .coingecko import CoinGeckoClient
from .reddit import RedditClient
from .twitter_source import TwitterSource
from .discord_source import DiscordSource

__all__ = [
    "DataSource",
    "DataItem", 
    "MarketData",
    "SourceType",
    "CoinGeckoClient",
    "RedditClient",
    "TwitterSource",
    "DiscordSource",
]
