"""Reddit API client for social sentiment data."""

import time
import requests
from typing import Dict, List
from datetime import datetime, timedelta
import logging
import random

logger = logging.getLogger(__name__)


class RedditClient:
    """Client for Reddit API."""
    
    def __init__(self, user_agent: str = "MemeCoinSentimentAnalyzer/1.0",
                 rate_limit: int = 60, timeout: int = 30):
        self.user_agent = user_agent
        self.rate_limit = rate_limit
        self.timeout = timeout
        self.last_request = 0
    
    def _rate_limit_wait(self):
        """Wait to respect rate limits."""
        elapsed = time.time() - self.last_request
        min_interval = 60 / self.rate_limit
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
        self.last_request = time.time()
    
    def get_coin_mentions(self, symbol: str, limit: int = 100) -> Dict:
        """Get Reddit mentions for a coin symbol."""
        self._rate_limit_wait()
        
        # Search subreddits
        subreddits = ['cryptocurrency', 'SolanaMemeCoins', 'dogecoin', 'SHIB', 'PepeCrypto']
        all_posts = []
        
        for subreddit in subreddits[:3]:  # Limit to 3 subreddits
            try:
                posts = self._search_subreddit(subreddit, symbol, limit=25)
                all_posts.extend(posts)
            except Exception as e:
                logger.debug(f"Error searching r/{subreddit}: {e}")
        
        # Extract texts and stats
        texts = [p['title'] + ' ' + p.get('selftext', '') for p in all_posts]
        
        # Calculate mention stats
        mention_count = len(all_posts)
        unique_users = len(set(p['author'] for p in all_posts if p.get('author')))
        
        # Get mention trend (simplified - compare recent to older)
        recent_cutoff = datetime.now() - timedelta(hours=12)
        recent_mentions = sum(
            1 for p in all_posts
            if datetime.fromtimestamp(p['created_utc']) > recent_cutoff
        )
        older_mentions = mention_count - recent_mentions
        
        mention_growth = 0
        if older_mentions > 0:
            mention_growth = ((recent_mentions - older_mentions) / older_mentions) * 100
        
        return {
            'symbol': symbol,
            'posts': all_posts,
            'texts': texts,
            'mention_count': mention_count,
            'unique_users': unique_users,
            'mention_growth': mention_growth,
            'subreddits_ searched': len(subreddits)
        }
    
    def _search_subreddit(self, subreddit: str, query: str, limit: int = 25) -> List[Dict]:
        """Search a subreddit for posts matching query."""
        url = f"https://www.reddit.com/r/{subreddit}/search.json"
        headers = {'User-Agent': self.user_agent}
        params = {
            'q': query,
            'limit': min(limit, 100),
            'sort': 'new',
            't': 'week',
            'include_over_18': 'false'
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            posts = []
            for child in data.get('data', {}).get('children', []):
                post = child.get('data', {})
                posts.append({
                    'id': post.get('id'),
                    'title': post.get('title', ''),
                    'selftext': post.get('selftext', ''),
                    'author': post.get('author'),
                    'created_utc': post.get('created_utc', 0),
                    'score': post.get('score', 0),
                    'num_comments': post.get('num_comments', 0),
                    'subreddit': post.get('subreddit'),
                    'url': post.get('url', ''),
                    'permalink': post.get('permalink', '')
                })
            
            return posts
            
        except requests.exceptions.RequestException as e:
            logger.debug(f"Error searching r/{subreddit}: {e}")
            return []
    
    def get_trending_cryptos(self, limit: int = 10) -> List[Dict]:
        """Get trending cryptocurrencies on Reddit."""
        self._rate_limit_wait()
        
        url = "https://www.reddit.com/r/Cryptocurrency/hot.json"
        headers = {'User-Agent': self.user_agent}
        params = {'limit': min(limit * 2, 100)}
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            posts = []
            for child in data.get('data', {}).get('children', [])[:limit]:
                post = child.get('data', {})
                posts.append({
                    'title': post.get('title', ''),
                    'score': post.get('score', 0),
                    'num_comments': post.get('num_comments', 0)
                })
            
            return posts
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching trending: {e}")
            return []
