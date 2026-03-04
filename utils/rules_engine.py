"""Rules engine for filtering and validation."""

import logging
from typing import Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)


class RulesEngine:
    """Applies rules to filter and validate analysis results."""

    def __init__(self, config: dict):
        """Initialize with configuration."""
        self.config = config
        self.sentiment_config = config.get('sentiment', {})
        self.analysis_config = config.get('analysis', {})
        
        # Thresholds
        self.min_confidence = self.sentiment_config.get('min_confidence', 0.3)
        self.bullish_threshold = self.sentiment_config.get('bullish_threshold', 50)
        self.bearish_threshold = self.sentiment_config.get('bearish_threshold', -50)
        self.min_mentions = self.analysis_config.get('min_mentions', 10)

    def passes(self, analysis: dict) -> bool:
        """Check if analysis passes all rules."""
        # Check confidence
        sentiment = analysis.get('sentiment', {})
        confidence = sentiment.get('confidence', 0) / 100  # Convert from 0-100 to 0-1
        if confidence < self.min_confidence:
            logger.debug(f"Low confidence: {confidence} < {self.min_confidence}")
            return False
        
        # Check mention count
        social = analysis.get('social', {})
        mentions = social.get('mention_count', 0)
        if mentions < self.min_mentions:
            logger.debug(f"Low mentions: {mentions} < {self.min_mentions}")
            return False
        
        # Check sentiment is not bearish
        score = sentiment.get('score', 0)
        if score < self.bearish_threshold:
            logger.debug(f"Bearish sentiment: {score} < {self.bearish_threshold}")
            return False
        
        return True

    def get_violations(self, analysis: dict) -> List[str]:
        """Get list of rule violations."""
        violations = []
        
        sentiment = analysis.get('sentiment', {})
        confidence = sentiment.get('confidence', 0) / 100
        if confidence < self.min_confidence:
            violations.append(f"low_confidence ({confidence:.2f} < {self.min_confidence})")
        
        social = analysis.get('social', {})
        mentions = social.get('mention_count', 0)
        if mentions < self.min_mentions:
            violations.append(f"low_mentions ({mentions} < {self.min_mentions})")
        
        score = sentiment.get('score', 0)
        if score < self.bearish_threshold:
            violations.append(f"bearish ({score} < {self.bearish_threshold})")
        
        return violations

    def apply(self, results: List[dict]) -> List[dict]:
        """Filter results through rules."""
        filtered = []
        for r in results:
            if self.passes(r):
                filtered.append(r)
            else:
                r['violations'] = self.get_violations(r)
        return filtered
