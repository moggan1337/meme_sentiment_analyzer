"""Main orchestration agent for meme coin sentiment analysis."""

import logging
import yaml
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from .ranker import CoinRanker
from .generator import ReportGenerator
from data_sources.coingecko import CoinGeckoConnector
from data_sources.reddit import RedditConnector
from utils.sentiment_analyzer import SentimentAnalyzer
from utils.rules_engine import RulesEngine

logger = logging.getLogger(__name__)


class MemeCoinAgent:
    """Main agent for orchestrating meme coin sentiment analysis."""

    def __init__(self, config_path: str = "config/config.yaml",
                 coins_path: str = "config/coins.yaml"):
        """Initialize the agent with configuration."""
        self.config = self._load_yaml(config_path)
        self.coins = self._load_yaml(coins_path)
        
        self.rankers = CoinRanker(self.config)
        self.generator = ReportGenerator(self.config)
        self.sentiment = SentimentAnalyzer()
        self.rules = RulesEngine(self.config)
        
        # Data connectors
        self.coingecko = CoinGeckoConnector()
        self.reddit = RedditConnector()
        
        # Track last report times for cooldown
        self.last_report: Dict[str, datetime] = {}
        
    def _load_yaml(self, path: str) -> dict:
        """Load YAML configuration file."""
        with open(path, 'r') as f:
            return yaml.safe_load(f)

    async def analyze_coin(self, symbol: str) -> Optional[dict]:
        """Analyze a single coin."""
        try:
            # Fetch market data
            market_data = await self.coingecko.get_coin_data(symbol)
            
            # Fetch social data
            social_data = await self.reddit.get_mentions(symbol)
            
            # Analyze sentiment
            sentiment_score = self.sentiment.analyze(social_data.get('posts', []))
            
            # Combine data
            analysis = {
                'symbol': symbol,
                'timestamp': datetime.now(),
                'market': market_data,
                'social': social_data,
                'sentiment': sentiment_score
            }
            
            # Apply rules
            if not self.rules.passes(analysis):
                return None
                
            # Score the coin
            score = self.rankers.calculate_score(analysis)
            analysis['score'] = score
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}")
            return None

    async def run_analysis(self) -> List[dict]:
        """Run analysis on all watchlist coins."""
        results = []
        
        for coin in self.coins['watchlist']:
            symbol = coin['symbol']
            result = await self.analyze_coin(symbol)
            if result:
                results.append(result)
        
        # Rank results
        ranked = self.rankers.rank(results)
        
        return ranked

    async def generate_report_if_needed(self, results: List[dict]) -> Optional[str]:
        """Generate report only if thresholds are met."""
        # Check cooldown
        now = datetime.now()
        eligible = []
        
        for r in results:
            symbol = r['symbol']
            last = self.last_report.get(symbol)
            cooldown_hours = self.config.get('analysis', {}).get('cooldown_hours', 4)
            
            if not last or (now - last) > timedelta(hours=cooldown_hours):
                eligible.append(r)
        
        if not eligible:
            return None
            
        # Limit to top N
        max_per_report = self.config.get('analysis', {}).get('max_coins_per_report', 3)
        eligible = eligible[:max_per_report]
        
        # Generate report
        report_path = self.generator.generate(eligible)
        
        # Update last report times
        for r in eligible:
            self.last_report[r['symbol']] = now
            
        return report_path

    async def run(self):
        """Main execution loop."""
        logger.info("Starting meme coin analysis...")
        
        results = await self.run_analysis()
        
        if results:
            report = await self.generate_report_if_needed(results)
            if report:
                logger.info(f"Report generated: {report}")
        else:
            logger.info("No coins met threshold criteria - no report generated")


if __name__ == "__main__":
    import asyncio
    agent = MemeCoinAgent()
    asyncio.run(agent.run())
