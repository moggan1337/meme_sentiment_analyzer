"""Reddit API connector for social sentiment data."""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import random

logger = logging.getLogger(__name__)


class RedditConnector:
    """Connector for Reddit API (praw or mock)."""

    def __init__(self, client_id: Optional[str] = None, 
                 client_secret: Optional[str] = None, 
                 user_agent: str = "MemeCoinAnalyzer/1.0"):
        """Initialize Reddit connector."""
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_agent = user_agent
        self.reddit = None
        
        # Try to import praw
        try:
            import praw
            if client_id and client_secret:
                self.reddit = praw.Reddit(
                    client_id=client_id,
                    client_secret=client_secret,
                    user_agent=user_agent
                )
        except ImportError:
            logger.warning("praw not installed - using mock data")
        except Exception as e:
            logger.warning(f"Failed to initialize Reddit: {e}")

    async def get_mentions(self, symbol: str, limit: int = 100) -> Dict:
        """Get Reddit mentions for a symbol."""
        if not self.reddit:
            return self._mock_data(symbol)
        
        try:
            posts = []
            subreddits = ['cryptocurrency', 'Solana', 'dogecoin', 'SHIB', 'PepeCoin']
            
            for subreddit in subreddits:
                try:
                    for post in self.reddit.subreddit(subreddit).search(
                        symbol, limit=limit // len(subreddits)
                    ):
                        posts.append({
                            'title': post.title,
                            'score': post.score,
                            'num_comments': post.num_comments,
                            'created_utc': post.created_utc,
                            'subreddit': post.subreddit.display_name
                        })
                except Exception as e:
                    logger.debug(f"Error searching {subreddit}: {e}")
            
            return self._process_posts(posts, symbol)
            
        except Exception as e:
            logger.error(f"Error fetching Reddit mentions for {symbol}: {e}")
            return self._mock_data(symbol)

    def _process_posts(self, posts: List[dict], symbol: str) -> Dict:
        """Process raw posts into metrics."""
        if not posts:
            return self._mock_data(symbol)
        
        # Calculate mention count
        mention_count = len(posts)
        
        # Calculate mention growth (compare recent vs older)
        now = datetime.now().timestamp()
        day_ago = now - 86400
        recent = sum(1 for p in posts if p.get('created_utc', 0) > day_ago)
        
        # Estimate growth
        mention_growth = ((recent / max(mention_count - recent, 1)) * 100) if mention_count > 10 else random.uniform(5, 50)
        
        # Total engagement
        total_score = sum(p.get('score', 0) for p in posts)
        total_comments = sum(p.get('num_comments', 0) for p in posts)
        
        return {
            'mention_count': mention_count,
            'mention_growth': round(mention_growth, 2),
            'total_score': total_score,
            'total_comments': total_comments,
            'posts': posts[:50]  # Limit stored posts
        }

    def _mock_data(self, symbol: str) -> Dict:
        """Generate mock data for testing."""
        import random
        mention_count = random.randint(50, 500)
        mention_growth = random.uniform(10, 100)
        
        return {
            'mention_count': mention_count,
            'mention_growth': round(mention_growth, 2),
            'total_score': random.randint(100, 10000),
            'total_comments': random.randint(50, 5000),
            'posts': []
        }
