"""Application settings and configuration management."""

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from pathlib import Path
import json


@dataclass
class DataSourceConfig:
    """Configuration for a data source."""
    enabled: bool = True
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    rate_limit: int = 100
    timeout: int = 30
    
    
@dataclass
class Settings:
    """Main application settings."""
    
    # Application
    app_name: str = "Crypto Meme Sentiment Analyzer"
    version: str = "1.0.0"
    environment: str = "development"
    
    # Paths
    base_dir: Path = field(default_factory=lambda: Path("/root/meme_sentiment_analyzer"))
    data_dir: Path = field(init=False)
    raw_data_dir: Path = field(init=False)
    processed_data_dir: Path = field(init=False)
    reports_dir: Path = field(init=False)
    logs_dir: Path = field(init=False)
    
    # Data sources
    twitter: DataSourceConfig = field(default_factory=DataSourceConfig)
    reddit: DataSourceConfig = field(default_factory=DataSourceConfig)
    discord: DataSourceConfig = field(default_factory=DataSourceConfig)
    coingecko: DataSourceConfig = field(default_factory=DataSourceConfig)
    coinmarketcap: DataSourceConfig = field(default_factory=DataSourceConfig)
    news: DataSourceConfig = field(default_factory=DataSourceConfig)
    
    # Sentiment analysis
    sentiment_model: str = "cardiffnlp/twitter-roberta-base-sentiment-latest"
    sentiment_batch_size: int = 32
    sentiment_confidence_threshold: float = 0.5
    
    # Tracking
    tracked_coins: List[str] = field(default_factory=lambda: [
        "DOGE", "SHIB", "PEPE", "WIF", "BONK", "FLOKI", "ELON", "MAGA", "TRUMP", "BODEN"
    ])
    watchlist: List[str] = field(default_factory=list)
    top_n_by_market_cap: int = 50
    
    # Run windows
    run_window_minutes: int = 60
    baseline_24h: bool = True
    baseline_7d: bool = True
    
    # Scheduler
    schedule_interval_minutes: int = 60
    enable_scheduled_runs: bool = True
    
    # Report settings
    max_report_coins: int = 5
    report_cooldown_hours: int = 4
    score_increase_threshold: float = 0.1
    
    # Storage
    raw_data_retention_days: int = 7
    reports_retention_days: int = 90
    
    # Notifications
    notification_enabled: bool = False
    discord_webhook_url: Optional[str] = None
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    email_enabled: bool = False
    email_recipients: List[str] = field(default_factory=list)
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # API keys (loaded from environment)
    def __post_init__(self):
        self.data_dir = self.base_dir / "data"
        self.raw_data_dir = self.data_dir / "raw"
        self.processed_data_dir = self.data_dir / "processed"
        self.reports_dir = self.data_dir / "reports"
        self.logs_dir = self.base_dir / "logs"
        
        # Create directories
        for d in [self.data_dir, self.raw_data_dir, self.processed_data_dir, 
                  self.reports_dir, self.logs_dir]:
            d.mkdir(parents=True, exist_ok=True)
        
        # Load API keys from environment
        self.twitter.api_key = os.getenv("TWITTER_API_KEY")
        self.twitter.api_secret = os.getenv("TWITTER_API_SECRET")
        self.reddit.api_key = os.getenv("REDDIT_API_KEY")
        self.discord.api_key = os.getenv("DISCORD_BOT_TOKEN")
        self.coingecko.api_key = os.getenv("COINGECKO_API_KEY")
        self.coinmarketcap.api_key = os.getenv("COINMARKETCAP_API_KEY")
        self.news.api_key = os.getenv("NEWS_API_KEY")
        
        # Notification settings
        self.discord_webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
        self.telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    def to_dict(self) -> Dict:
        """Convert settings to dictionary (excluding secrets)."""
        return {
            "app_name": self.app_name,
            "version": self.version,
            "environment": self.environment,
            "tracked_coins": self.tracked_coins,
            "watchlist": self.watchlist,
            "top_n_by_market_cap": self.top_n_by_market_cap,
            "run_window_minutes": self.run_window_minutes,
            "schedule_interval_minutes": self.schedule_interval_minutes,
            "max_report_coins": self.max_report_coins,
            "report_cooldown_hours": self.report_cooldown_hours,
            "sentiment_model": self.sentiment_model,
            "sources": {
                "twitter": self.twitter.enabled,
                "reddit": self.reddit.enabled,
                "discord": self.discord.enabled,
                "coingecko": self.coingecko.enabled,
                "coinmarketcap": self.coinmarketcap.enabled,
                "news": self.news.enabled,
            }
        }
    
    @classmethod
    def from_file(cls, path: Path) -> 'Settings':
        """Load settings from JSON file."""
        if path.exists():
            with open(path) as f:
                data = json.load(f)
            return cls(**data)
        return cls()
    
    def save(self, path: Path):
        """Save settings to JSON file."""
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reload_settings() -> Settings:
    """Reload settings from file."""
    global _settings
    config_path = Path("/root/meme_sentiment_analyzer/config.json")
    if config_path.exists():
        _settings = Settings.from_file(config_path)
    else:
        _settings = Settings()
    return _settings
