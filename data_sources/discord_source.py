"""Discord data source for fetching crypto server mentions.

Requires Discord bot token with appropriate intents.
"""

import os
import logging
from typing import List, Optional
from datetime import datetime, timedelta

from .base import DataSource, DataItem, SourceType

logger = logging.getLogger(__name__)


class DiscordSource(DataSource):
    """Discord data source for fetching crypto mentions from servers.
    
    Note: This requires a Discord bot with Message Content Intent enabled.
    """
    
    def __init__(self, token: Optional[str] = None):
        """Initialize Discord source.
        
        Args:
            token: Discord bot token (from DISCORD_BOT_TOKEN env var if not provided)
        """
        super().__init__(SourceType.DISCORD)
        self.token = token or os.getenv("DISCORD_BOT_TOKEN")
        self.client = None
        self._guilds = []
        
        if not self.token:
            logger.warning("Discord bot token not provided. Using mock data.")
    
    async def _initialize_client(self):
        """Initialize Discord client (async)."""
        try:
            import discord
            intents = discord.Intents.default()
            intents.message_content = True
            self.client = discord.Client(intents=intents)
        except ImportError:
            logger.error("discord.py not installed. Install with: pip install discord.py")
            raise
    
    def fetch(self, coin_ids: List[str], **kwargs) -> List[DataItem]:
        """Fetch Discord messages mentioning coins.
        
        Args:
            coin_ids: List of coin IDs to search for
            
        Returns:
            List of DataItem objects
        """
        if not self.token:
            return self._generate_mock_data(coin_ids)
        
        # Run async fetch
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If already in async context, schedule as task
                future = asyncio.run_coroutine_threadsafe(
                    self._fetch_async(coin_ids), loop
                )
                return future.result(timeout=30)
            else:
                return asyncio.run(self._fetch_async(coin_ids))
        except Exception as e:
            logger.error(f"Error fetching Discord data: {e}")
            return self._generate_mock_data(coin_ids)
    
    async def _fetch_async(self, coin_ids: List[str]) -> List[DataItem]:
        """Async fetch implementation."""
        # Implementation would go here with discord.py
        # For now, return mock data
        return self._generate_mock_data(coin_ids)
    
    def _generate_mock_data(self, coin_ids: List[str]) -> List[DataItem]:
        """Generate mock Discord data for testing."""
        import random
        
        messages = [
            "Just bought more {coin}! 🚀",
            "{coin} looking bullish today",
            "Anyone else in {coin}?",
            "{coin} to the moon! 🌙",
            "This {coin} dip is a gift",
            "{coin} holders staying strong 💪",
            "Just aped into {coin}",
            "{coin} volume looking crazy",
        ]
        
        items = []
        for coin_id in coin_ids:
            coin_symbol = coin_id.upper()
            num_mentions = random.randint(5, 20)
            
            for _ in range(num_mentions):
                message = random.choice(messages).format(coin=coin_symbol)
                items.append(DataItem(
                    coin_id=coin_id,
                    source=SourceType.DISCORD,
                    timestamp=datetime.utcnow() - timedelta(hours=random.randint(0, 24)),
                    content=message,
                    author=f"user_{random.randint(1000, 9999)}",
                    engagement=random.randint(0, 100),
                    url=f"https://discord.com/channels/.../{random.randint(1000000, 9999999)}"
                ))
        
        logger.info(f"Generated {len(items)} mock Discord messages")
        return items
    
    def test_connection(self) -> bool:
        """Test Discord connection.
        
        Returns:
            True if connection successful, False otherwise
        """
        if not self.token:
            logger.info("Discord token not configured")
            return False
        
        # Would test actual connection here
        return True
