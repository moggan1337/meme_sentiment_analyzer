"""Threshold configuration for filtering rules and scoring."""

import os
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from pathlib import Path
from enum import Enum


class SourceWeight(Enum):
    """Data source weight categories."""
    HIGH = 1.5
    MEDIUM = 1.0
    LOW = 0.5


@dataclass
class ThresholdConfig:
    """Configuration for filtering thresholds and scoring weights."""
    
    # Sentiment thresholds
    min_positive_sentiment_pct: float = 50.0  # X% positive sentiment required
    min_sentiment_confidence: float = 0.5
    
    # Mention thresholds
    min_mention_count: int = 10  # Minimum mentions to consider
    min_mention_growth_pct: float = 50.0  # Z% growth vs baseline
    
    # Market thresholds
    min_price_change_1h_pct: float = 2.0  # P% price change (1h)
    min_price_change_24h_pct: float = 5.0  # Price change (24h)
    min_volume_24h_usd: float = 10000.0  # Minimum volume to filter micro-liquidity
    min_market_cap_usd: float = 10000.0
    min_volume_growth_pct: float = 20.0  # Y% volume increase
    
    # Scoring weights
    sentiment_weight: float = 1.0
    mention_weight: float = 1.0
    price_weight: float = 1.0
    volume_weight: float = 0.8
    
    # Source weights
    twitter_weight: float = 1.0
    reddit_weight: float = 1.2
    discord_weight: float = 0.8
    news_weight: float = 1.0
    
    # Derived thresholds (computed)
    derived_min_positive: float = field(init=False)
    derived_min_mentions: float = field(init=False)
    derived_min_momentum: float = field(init=False)
    
    def __post_init__(self):
        # Compute derived thresholds
        self.derived_min_positive = self.min_positive_sentiment_pct / 100.0
        self.derived_min_mentions = self.min_mention_count
        self.derived_min_momentum = self.min_price_change_1h_pct / 100.0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "sentiment": {
                "min_positive_pct": self.min_positive_sentiment_pct,
                "min_confidence": self.min_sentiment_confidence,
            },
            "mentions": {
                "min_count": self.min_mention_count,
                "min_growth_pct": self.min_mention_growth_pct,
            },
            "market": {
                "min_price_change_1h_pct": self.min_price_change_1h_pct,
                "min_price_change_24h_pct": self.min_price_change_24h_pct,
                "min_volume_24h_usd": self.min_volume_24h_usd,
                "min_market_cap_usd": self.min_market_cap_usd,
                "min_volume_growth_pct": self.min_volume_growth_pct,
            },
            "weights": {
                "sentiment": self.sentiment_weight,
                "mentions": self.mention_weight,
                "price": self.price_weight,
                "volume": self.volume_weight,
                "twitter": self.twitter_weight,
                "reddit": self.reddit_weight,
                "discord": self.discord_weight,
                "news": self.news_weight,
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ThresholdConfig':
        """Create from dictionary."""
        if "sentiment" in data:
            s = data["sentiment"]
            data["min_positive_sentiment_pct"] = s.get("min_positive_pct", 50.0)
            data["min_sentiment_confidence"] = s.get("min_confidence", 0.5)
        if "mentions" in data:
            m = data["mentions"]
            data["min_mention_count"] = m.get("min_count", 10)
            data["min_mention_growth_pct"] = m.get("min_growth_pct", 50.0)
        if "market" in data:
            mk = data["market"]
            data["min_price_change_1h_pct"] = mk.get("min_price_change_1h_pct", 2.0)
            data["min_price_change_24h_pct"] = mk.get("min_price_change_24h_pct", 5.0)
            data["min_volume_24h_usd"] = mk.get("min_volume_24h_usd", 10000.0)
            data["min_market_cap_usd"] = mk.get("min_market_cap_usd", 10000.0)
            data["min_volume_growth_pct"] = mk.get("min_volume_growth_pct", 20.0)
        if "weights" in data:
            w = data["weights"]
            data["sentiment_weight"] = w.get("sentiment", 1.0)
            data["mention_weight"] = w.get("mentions", 1.0)
            data["price_weight"] = w.get("price", 1.0)
            data["volume_weight"] = w.get("volume", 0.8)
            data["twitter_weight"] = w.get("twitter", 1.0)
            data["reddit_weight"] = w.get("reddit", 1.2)
            data["discord_weight"] = w.get("discord", 0.8)
            data["news_weight"] = w.get("news", 1.0)
        return cls(**{k: v for k, v in data.items() if k in {
            "min_positive_sentiment_pct", "min_sentiment_confidence",
            "min_mention_count", "min_mention_growth_pct",
            "min_price_change_1h_pct", "min_price_change_24h_pct",
            "min_volume_24h_usd", "min_market_cap_usd", "min_volume_growth_pct",
            "sentiment_weight", "mention_weight", "price_weight", "volume_weight",
            "twitter_weight", "reddit_weight", "discord_weight", "news_weight",
        }})
    
    @classmethod
    def from_file(cls, path: Path) -> 'ThresholdConfig':
        """Load from JSON file."""
        if path.exists():
            with open(path) as f:
                data = json.load(f)
            return cls.from_dict(data)
        return cls()
    
    def save(self, path: Path):
        """Save to JSON file."""
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)


# Global threshold config
_threshold_config: Optional[ThresholdConfig] = None


def get_threshold_config() -> ThresholdConfig:
    """Get or create global threshold config."""
    global _threshold_config
    if _threshold_config is None:
        config_path = Path("/root/meme_sentiment_analyzer/thresholds.json")
        _threshold_config = ThresholdConfig.from_file(config_path)
    return _threshold_config


def reload_threshold_config() -> ThresholdConfig:
    """Reload threshold config from file."""
    global _threshold_config
    config_path = Path("/root/meme_sentiment_analyzer/thresholds.json")
    _threshold_config = ThresholdConfig.from_file(config_path)
    return _threshold_config
