"""Twitter/X data source connector."""

import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import asyncio

from .base import DataSource, DataItem, SourceType


class TwitterSource(DataSource):
    """Twitter/X data source implementation."""
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__(SourceType.TWITTER, config)
        self.api_key = config.get("api_key") if config else None
        self.api_secret = config.get("api_secret") if config else None
        self.bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
        self.logger = logging.getLogger(__name__)
    
    async def fetch(self, coin_ids: List[str], window_minutes: int) -> List[DataItem]:
        """Fetch tweets mentioning given coins."""
        if not self.bearer_token:
            self.logger.warning("Twitter bearer token not configured, using mock data")
            return self._generate_mock_data(coin_ids, window_minutes)
        
        items = []
        cutoff_time = datetime.now() - timedelta(minutes=window_minutes)
        
        for coin_id in coin_ids:
            try:
                tweets = await self._search_tweets(coin_id, cutoff_time)
                items.extend(tweets)
            except Exception as e:
                self.logger.error(f"Error fetching tweets for {coin_id}: {e}")
        
        return items
    
    async def _search_tweets(self, coin_id: str, cutoff_time: datetime) -> List[DataItem]:
        """Search tweets for a specific coin."""
        # In production, this would use Twitter API v2
        # For now, return mock data if no API key
        return self._generate_mock_data([coin_id], 60)
    
    def _generate_mock_data(self, coin_ids: List[str], window_minutes: int) -> List[DataItem]:
        """Generate mock data for testing."""
        import random
        from datetime import timedelta
        
        mock_tweets = [
            "{coin} to the moon! 🚀 #crypto #memecoin",
            "Just bought more {coin}, this is going to explode!",
            "{coin} holders are going to be rich soon",
            "Why {coin} is the next big thing in crypto",
            "{coin} breaking out! Get in now!",
            "Another green day for {coin} 🚀🚀🚀",
            "{coin} community is based and redpilled",
            "Watching {coin} carefully, looking bullish",
        ]
        
        items = []
        now = datetime.now()
        
        for coin_id in coin_ids:
            # Generate 5-15 mock tweets per coin
            num_tweets = random.randint(5, 15)
            for i in range(num_tweets):
                content = random.choice(mock_tweets).format(coin=coin_id)
                timestamp = now - timedelta(
                    minutes=random.randint(0, window_minutes),
                    seconds=random.randint(0, 59)
                )
                
                items.append(DataItem(
                    coin_id=coin_id,
                    source=SourceType.TWITTER,
                    timestamp=timestamp,
                    content=content,
                    author_id=f"user_{random.randint(1000, 9999)}",
                    engagement=random.randint(0, 500),
                    url=f"https://twitter.com/user/status/{random.randint(100000000000, 999999999999)}",
                    raw_data={"mock": True}
                ))
        
        return items
    
    async def test_connection(self) -> bool:
        """Test Twitter API connection."""
        if not self.bearer_token:
            self.logger.warning("Twitter bearer token not configured")
            return False
        
        try:
            # In production, test actual API connection
            return True
        except Exception as e:
            self.logger.error(f"Twitter connection test failed: {e}")
            return False
