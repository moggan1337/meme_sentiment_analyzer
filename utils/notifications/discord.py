"""Discord webhook notifications."""

import os
import logging
from typing import Optional, Dict, Any
import requests

logger = logging.getLogger(__name__)


class DiscordNotifier:
    """Discord webhook notifier."""
    
    def __init__(self, webhook_url: Optional[str] = None):
        """Initialize Discord notifier.
        
        Args:
            webhook_url: Discord webhook URL
        """
        self.webhook_url = webhook_url or os.getenv("DISCORD_WEBHOOK_URL")
        
        if not self.webhook_url:
            logger.warning("Discord webhook URL not configured.")
    
    def send_message(self, content: str, embed: Optional[Dict] = None) -> bool:
        """Send message to Discord.
        
        Args:
            content: Message content
            embed: Optional embed dictionary
            
        Returns:
            True if successful
        """
        if not self.webhook_url:
            return False
        
        data = {"content": content}
        if embed:
            data["embeds"] = [embed]
        
        try:
            response = requests.post(self.webhook_url, json=data, timeout=10)
            return response.status_code in (200, 204)
        except requests.RequestException as e:
            logger.error(f"Discord notification failed: {e}")
            return False
