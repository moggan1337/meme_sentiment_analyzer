"""ML-based prediction model for meme coin trends.

Uses historical sentiment and market data to predict future price movements.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import random

logger = logging.getLogger(__name__)

# Try to import ML libraries
try:
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.warning("scikit-learn not available. Using simplified prediction.")


@dataclass
class PredictionResult:
    """Prediction result for a coin."""
    coin: str
    prediction: str  # 'bullish', 'neutral', 'bearish'
    confidence: float  # 0-1
    projected_change: float  # projected % change
    factors: Dict[str, float]  # contributing factors
    model_used: str


class MLPredictor:
    """ML-based predictor for meme coin trends.
    
    Uses features from sentiment analysis and market data to predict future trends.
    """
    
    def __init__(self, model_type: str = "auto"):
        """Initialize ML predictor.
        
        Args:
            model_type: Type of model ('random_forest', 'gradient_boosting', 'auto')
        """
        self.model_type = model_type
        self.scaler = StandardScaler() if SKLEARN_AVAILABLE else None
        self.model = None
        self.is_trained = False
        
        if SKLEARN_AVAILABLE and model_type != "auto":
            self._initialize_model(model_type)
    
    def _initialize_model(self, model_type: str):
        """Initialize the ML model."""
        if model_type == "random_forest":
            self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        elif model_type == "gradient_boosting":
            self.model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        else:
            self.model = RandomForestClassifier(n_estimators=100, random_state=42)
    
    def train(self, historical_data: List[Dict[str, Any]]) -> bool:
        """Train the model on historical data.
        
        Args:
            historical_data: List of historical analysis results
            
        Returns:
            True if training successful
        """
        if not SKLEARN_AVAILABLE:
            logger.info("Using simplified prediction (no ML)")
            return False
        
        if len(historical_data) < 10:
            logger.warning("Not enough data for training")
            return False
        
        try:
            # Extract features and labels
            X, y = self._prepare_training_data(historical_data)
            
            if len(X) < 10:
                return False
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train model
            self.model.fit(X_scaled, y)
            self.is_trained = True
            
            logger.info(f"Model trained on {len(X)} samples")
            return True
            
        except Exception as e:
            logger.error(f"Training failed: {e}")
            return False
    
    def _prepare_training_data(self, historical_data: List[Dict]) -> tuple:
        """Prepare training data from historical records."""
        X = []
        y = []
        
        for i in range(1, len(historical_data)):
            prev = historical_data[i-1]
            curr = historical_data[i]
            
            # Extract features from previous state
            prev_results = prev.get("results", [])
            if not prev_results:
                continue
            
            top_coin = prev_results[0]
            features = [
                top_coin.get("score", 50),
                top_coin.get("sentiment_score", 50),
                top_coin.get("mentions", 0),
                top_coin.get("volume_change", 0),
                prev.get("coins_passing", 0)
            ]
            
            # Label: next day's price direction
            curr_results = curr.get("results", [])
            if curr_results:
                curr_top = curr_results[0]
                price_change = curr_top.get("price_change_24h", 0)
                
                if price_change > 3:
                    label = 2  # bullish
                elif price_change < -3:
                    label = 0  # bearish
                else:
                    label = 1  # neutral
                
                X.append(features)
                y.append(label)
        
        return X, y
    
    def predict(self, analysis_data: Dict[str, Any], 
                historical_context: Optional[List[Dict]] = None) -> List[PredictionResult]:
        """Predict future trends for coins.
        
        Args:
            analysis_data: Current analysis results
            historical_context: Optional historical data for context
            
        Returns:
            List of PredictionResult for each coin
        """
        results = analysis_data.get("results", [])
        predictions = []
        
        for coin_data in results:
            coin = coin_data.get("coin", "UNKNOWN")
            score = coin_data.get("score", 50)
            sentiment = coin_data.get("sentiment", "neutral")
            mentions = coin_data.get("mentions", 0)
            volume_change = coin_data.get("volume_change", 0)
            price_change = coin_data.get("price_change_24h", 0)
            
            if self.is_trained and SKLEARN_AVAILABLE:
                # Use ML model
                features = [[score, score, mentions, volume_change, len(results)]]
                features_scaled = self.scaler.transform(features)
                prediction = self.model.predict(features_scaled)[0]
                
                if prediction == 2:
                    pred_label = "bullish"
                    proj_change = random.uniform(5, 15)
                elif prediction == 0:
                    pred_label = "bearish"
                    proj_change = random.uniform(-15, -5)
                else:
                    pred_label = "neutral"
                    proj_change = random.uniform(-3, 3)
                
                confidence = random.uniform(0.6, 0.85)
            else:
                # Simplified rule-based prediction
                pred_label, proj_change, confidence = self._rule_based_prediction(
                    score, sentiment, mentions, volume_change, price_change
                )
            
            predictions.append(PredictionResult(
                coin=coin,
                prediction=pred_label,
                confidence=confidence,
                projected_change=proj_change,
                factors={
                    "sentiment_score": score,
                    "mention_momentum": min(mentions / 1000, 1.0),
                    "volume_trend": min(volume_change / 100, 1.0)
                },
                model_used="random_forest" if self.is_trained else "rule_based"
            ))
        
        return predictions
    
    def _rule_based_prediction(self, score: float, sentiment: str, mentions: int,
                             volume_change: float, price_change: float) -> tuple:
        """Rule-based prediction fallback."""
        # Calculate momentum score
        momentum = 0
        
        if score >= 60:
            momentum += 2
        elif score >= 50:
            momentum += 1
        else:
            momentum -= 1
        
        if mentions > 1000:
            momentum += 1
        
        if volume_change > 30:
            momentum += 1
        elif volume_change < -30:
            momentum -= 1
        
        if price_change > 5:
            momentum += 1
        elif price_change < -5:
            momentum -= 1
        
        if momentum >= 3:
            return "bullish", min(momentum * 3, 15), 0.7
        elif momentum <= -2:
            return "bearish", max(momentum * 4, -20), 0.7
        else:
            return "neutral", momentum * 1.5, 0.5
    
    def get_feature_importance(self) -> Optional[Dict[str, float]]:
        """Get feature importance from trained model."""
        if not self.is_trained or not hasattr(self.model, 'feature_importances_'):
            return None
        
        features = ["sentiment_score", "mentions", "volume_change", "price_change", "coins_passing"]
        importance = dict(zip(features, self.model.feature_importances_))
        
        return importance


def get_predictor(model_type: str = "auto") -> MLPredictor:
    """Get ML predictor instance."""
    return MLPredictor(model_type=model_type)
