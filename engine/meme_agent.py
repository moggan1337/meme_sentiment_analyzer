"""
Meme Coin Sentiment Analyzer - Main Agent

Orchestrates the sentiment analysis workflow:
1. Collects data from CoinGecko and Reddit
2. Analyzes sentiment and computes scores
3. Filters based on rules engine criteria
4. Generates reports when thresholds are met
"""

import yaml
import logging
import os
from datetime import datetime
from pathlib import Path

from data_sources.coingecko import CoinGeckoClient
from data_sources.reddit import RedditClient
from utils.sentiment_analyzer import SentimentAnalyzer
from utils.rules_engine import RulesEngine
from engine.ranker import ScoreRanker
from engine.generator import ReportGenerator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MemeAgent:
    """Main agent for meme coin sentiment analysis."""
    
    def __init__(self, config_path: str = None):
        """Initialize the agent with configuration."""
        self.base_dir = Path(__file__).parent.parent
        self.config_path = config_path or self.base_dir / "config.yaml"
        self.coins_path = self.base_dir / "coins.yaml"
        
        # Load configuration
        with open(self.config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        with open(self.coins_path, 'r') as f:
            self.coins_config = yaml.safe_load(f)
        
        # Initialize components
        self.coingecko = CoinGeckoClient(
            base_url=self.config['api']['coingecko']['base_url'],
            rate_limit=self.config['api']['coingecko']['rate_limit'],
            timeout=self.config['api']['coingecko']['timeout']
        )
        
        self.reddit = RedditClient(
            user_agent=self.config['api']['reddit']['user_agent'],
            rate_limit=self.config['api']['reddit']['rate_limit'],
            timeout=self.config['api']['reddit']['timeout']
        )
        
        self.sentiment_analyzer = SentimentAnalyzer(
            min_confidence=self.config['sentiment']['min_confidence']
        )
        
        self.rules_engine = RulesEngine(
            thresholds=self.config['sentiment'],
            coin_thresholds=self.coins_config['thresholds']
        )
        
        self.ranker = ScoreRanker(
            weights=self.config['sentiment']['weights']
        )
        
        self.generator = ReportGenerator(
            output_dir=self.base_dir / self.config['reporting']['output_dir'],
            format=self.config['reporting']['format']
        )
        
        logger.info("MemeAgent initialized successfully")
    
    def run_analysis(self) -> dict:
        """Run a complete analysis cycle."""
        logger.info("Starting analysis cycle")
        
        watchlist = [c for c in self.coins_config['watchlist'] if c.get('enabled', True)]
        results = []
        
        for coin in watchlist:
            coin_id = coin['id']
            symbol = coin['symbol']
            
            try:
                # Collect market data
                market_data = self.coingecko.get_coin_data(coin_id)
                
                # Collect social data
                social_data = self.reddit.get_coin_mentions(symbol)
                
                # Analyze sentiment
                sentiment_result = self.sentiment_analyzer.analyze(
                    social_data.get('texts', [])
                )
                
                # Combine data for scoring
                coin_data = {
                    'coin_id': coin_id,
                    'symbol': symbol,
                    'name': coin['name'],
                    'market_data': market_data,
                    'social_data': social_data,
                    'sentiment': sentiment_result
                }
                
                # Check if passes rules
                passes, reasons = self.rules_engine.check(coin_data)
                
                if passes:
                    # Calculate score
                    score = self.ranker.calculate(coin_data)
                    coin_data['score'] = score
                    coin_data['reasons'] = reasons
                    results.append(coin_data)
                    logger.info(f"{symbol} passed filters with score {score:.2f}")
                else:
                    logger.debug(f"{symbol} did not pass filters: {reasons}")
                    
            except Exception as e:
                logger.error(f"Error analyzing {coin_id}: {e}")
        
        # Sort by score
        results = sorted(results, key=lambda x: x['score'], reverse=True)
        
        # Generate report if criteria met
        if results:
            report_path = self.generator.generate(results)
            logger.info(f"Report generated: {report_path}")
            return {
                'success': True,
                'coins_analyzed': len(watchlist),
                'coins_passing': len(results),
                'report_path': report_path,
                'top_coins': results[:3]
            }
        else:
            logger.info("No coins met threshold criteria - no report generated")
            return {
                'success': True,
                'coins_analyzed': len(watchlist),
                'coins_passing': 0,
                'report_path': None
            }


def main():
    """Main entry point."""
    agent = MemeAgent()
    result = agent.run_analysis()
    
    print(f"\n{'='*50}")
    print("ANALYSIS COMPLETE")
    print(f"{'='*50}")
    print(f"Coins analyzed: {result['coins_analyzed']}")
    print(f"Coins passing: {result['coins_passing']}")
    
    if result['report_path']:
        print(f"Report: {result['report_path']}")
        print("\nTop coins:")
        for coin in result.get('top_coins', []):
            print(f"  {coin['symbol']}: {coin['score']:.2f}")
    else:
        print("No report generated (no coins met criteria)")


if __name__ == "__main__":
    main()
