"""Feature extraction for ML models."""

from typing import List, Dict, Any
from datetime import datetime, timedelta


class FeatureExtractor:
    """Extract features from analysis data for ML models."""
    
    @staticmethod
    def extract_technical_features(analysis_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract technical features from analysis."""
        results = analysis_data.get("results", [])
        
        if not results:
            return {}
        
        top = results[0]
        
        return {
            "avg_score": sum(r.get("score", 0) for r in results) / len(results),
            "top_score": top.get("score", 0),
            "total_mentions": sum(r.get("mentions", 0) for r in results),
            "avg_volume_change": sum(r.get("volume_change", 0) for r in results) / len(results),
            "avg_price_change": sum(r.get("price_change_24h", 0) for r in results) / len(results),
            "bullish_ratio": len([r for r in results if r.get("sentiment") == "bullish"]) / len(results),
            "coins_passing": analysis_data.get("coins_passing", 0)
        }
    
    @staticmethod
    def extract_time_features(data: Dict[str, Any]) -> Dict[str, float]:
        """Extract time-based features."""
        timestamp = data.get("timestamp", "")
        
        try:
            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            return {
                "hour": dt.hour / 24.0,
                "day_of_week": dt.weekday() / 7.0,
                "day_of_month": dt.day / 31.0
            }
        except:
            return {}
    
    @staticmethod
    def extract_all_features(analysis_data: Dict[str, Any]) -> List[float]:
        """Extract all features as a list."""
        tech = FeatureExtractor.extract_technical_features(analysis_data)
        time_feat = FeatureExtractor.extract_time_features(analysis_data)
        
        all_features = list(tech.values()) + list(time_feat.values())
        return all_features
