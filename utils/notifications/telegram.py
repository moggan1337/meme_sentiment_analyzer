"""Telegram bot notifications for sending alerts.

Requires TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables.
"""

import os
import logging
from typing import Optional, List, Dict, Any
import requests
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class AlertMessage:
    """Telegram alert message structure."""
    title: str
    message: str
    parse_mode: str = "Markdown"
    disable_web_preview: bool = False


class TelegramNotifier:
    """Telegram bot notifier for sending alerts and reports.
    
    Requires:
    - TELEGRAM_BOT_TOKEN: Bot API token from @BotFather
    - TELEGRAM_CHAT_ID: Target chat ID to send messages to
    """
    
    def __init__(self, token: Optional[str] = None, chat_id: Optional[str] = None):
        """Initialize Telegram notifier.
        
        Args:
            token: Telegram bot token (from TELEGRAM_BOT_TOKEN env var if not provided)
            chat_id: Target chat ID (from TELEGRAM_CHAT_ID env var if not provided)
        """
        self.token = token or os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")
        self.api_url = f"https://api.telegram.org/bot{self.token}" if self.token else None
        
        if not self.token or not self.chat_id:
            logger.warning("Telegram credentials not configured. Notifications disabled.")
    
    def send_message(self, text: str, parse_mode: str = "Markdown", 
                    disable_web_preview: bool = False) -> bool:
        """Send a message to the configured chat.
        
        Args:
            text: Message text to send
            parse_mode: Parse mode (Markdown or HTML)
            disable_web_preview: Disable link previews
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.api_url or not self.chat_id:
            logger.warning("Telegram not configured. Message not sent.")
            return False
        
        url = f"{self.api_url}/sendMessage"
        data = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": disable_web_preview
        }
        
        try:
            response = requests.post(url, json=data, timeout=10)
            response.raise_for_status()
            logger.info(f"Telegram message sent successfully")
            return True
        except requests.RequestException as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False
    
    def send_analysis_report(self, analysis_result: Dict[str, Any]) -> bool:
        """Send analysis report as formatted message.
        
        Args:
            analysis_result: Analysis result dictionary
            
        Returns:
            True if sent successfully
        """
        coins_analyzed = analysis_result.get("coins_analyzed", 0)
        coins_passing = analysis_result.get("coins_passing", 0)
        results = analysis_result.get("results", [])[:3]  # Top 3
        
        message = "📊 *Meme Coin Analysis Report*\n\n"
        message += f"• Coins Analyzed: *{coins_analyzed}*\n"
        message += f"• Coins Passing: *{coins_passing}*\n\n"
        
        if results:
            message += "*Top Performers:*\n"
            for i, coin in enumerate(results, 1):
                emoji = "🟢" if coin.get("sentiment") == "bullish" else "🟡"
                message += f"{i}. {emoji} *{coin.get('coin', 'N/A')}* - Score: {coin.get('score', 0):.1f}\n"
        else:
            message += "No coins passing thresholds.\n"
        
        return self.send_message(message)
    
    def send_alert(self, coin: str, alert_type: str, details: str) -> bool:
        """Send an alert for a specific coin.
        
        Args:
            coin: Coin symbol
            alert_type: Type of alert (bullish, bearish, volume_spike, etc.)
            details: Additional details
            
        Returns:
            True if sent successfully
        """
        emoji_map = {
            "bullish": "🚀",
            "bearish": "📉",
            "volume_spike": "📊",
            "price_spike": "💹",
            "mention_spike": "💬"
        }
        
        emoji = emoji_map.get(alert_type, "⚠️")
        message = f"{emoji} *{alert_type.upper()} Alert: {coin}*\n\n{details}"
        
        return self.send_message(message)
    
    def test_connection(self) -> bool:
        """Test the Telegram bot connection.
        
        Returns:
            True if connection successful
        """
        if not self.api_url:
            return False
        
        try:
            response = requests.get(f"{self.api_url}/getMe", timeout=10)
            return response.status_code == 200
        except requests.RequestException:
            return False


# Convenience function
def get_telegram_notifier() -> TelegramNotifier:
    """Get Telegram notifier instance.
    
    Returns:
        TelegramNotifier instance
    """
    return TelegramNotifier()
