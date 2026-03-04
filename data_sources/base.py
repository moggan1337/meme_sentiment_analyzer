"""Base classes for data sources."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum


class SourceType(Enum):
    """Types of data sources."""
    TWITTER = "twitter"
    REDDIT = "reddit"
    DISCORD = "discord"
    COINGECKO = "coingecko"
    COINMARKETCAP = "coinmarketcap"
    NEWS = "news"


@dataclass
class DataItem:
    """Normalized data item from any source."""
    coin_id: str
    source: SourceType
    timestamp: datetime
    content: str
    author_id: Optional[str] = None
    engagement: Optional[int] = None
    url: Optional[str] = None
    raw_data: Dict[Any, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "coin_id": self.coin_id,
            "source": self.source.value,
            "timestamp": self.timestamp.isoformat(),
            "content": self.content,
            "author_id": self.author_id,
            "engagement": self.engagement,
            "url": self.url,
        }


@dataclass
class MarketData:
    """Market data for a coin."""
    coin_id: str
    symbol: str
    name: str
    price_usd: float
    price_change_1h_pct: float
    price_change_24h_pct: float
    volume_24h_usd: float
    market_cap_usd: float
    timestamp: datetime
    
    def to_dict(self) -> Dict:
        return {
            "coin_id": self.coin_id,
            "symbol": self.symbol,
            "name": self.name,
            "price_usd": self.price_usd,
            "price_change_1h_pct": self.price_change_1h_pct,
            "price_change_24h_pct": self.price_change_24h_pct,
            "volume_24h_usd": self.volume_24h_usd,
            "market_cap_usd": self.market_cap_usd,
            "timestamp": self.timestamp.isoformat(),
        }


class DataSource(ABC):
    """Abstract base class for data sources."""
    
    def __init__(self, source_type: SourceType, config: Optional[Dict] = None):
        self.source_type = source_type
        self.config = config or {}
        self.enabled = self.config.get("enabled", True)
        self.logger = None
    
    @abstractmethod
    async def fetch(self, coin_ids: List[str], window_minutes: int) -> List[DataItem]:
        pass
    
    @abstractmethod
    async def test_connection(self) -> bool:
        pass
    
    def get_name(self) -> str:
        return self.source_type.value


class MarketDataSource(ABC):
    """Abstract base class for market data sources."""
    
    def __init__(self, source_type: SourceType, config: Optional[Dict] = None):
        self.source_type = source_type
        self.config = config or {}
        self.enabled = self.config.get("enabled", True)
        self.logger = None
    
    @abstractmethod
    async def fetch_market_data(self, coin_ids: List[str]) -> List[MarketData]:
        pass
    
    @abstractmethod
    async def test_connection(self) -> bool:
        pass
