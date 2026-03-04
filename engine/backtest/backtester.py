"""Backtesting engine for historical analysis of sentiment-based strategies."""

import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import json

logger = logging.getLogger(__name__)

@dataclass
class BacktestResult:
    strategy_name: str
    start_date: str
    end_date: str
    initial_capital: float
    final_capital: float
    total_return: float
    total_return_pct: float
    max_drawdown: float
    sharpe_ratio: float
    win_rate: float
    num_trades: int
    trades: List[Dict] = field(default_factory=list)
    equity_curve: List[Dict] = field(default_factory=list)

class Backtester:
    def __init__(self, initial_capital: float = 10000.0):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.position = None
        self.trades = []
        self.equity_curve = []
    
    def run_backtest(self, historical_data: List[Dict], strategy: Dict[str, Any]) -> BacktestResult:
        self.capital = self.initial_capital
        self.position = None
        self.trades = []
        self.equity_curve = []
        
        entry_threshold = strategy.get("entry_threshold", 60)
        exit_threshold = strategy.get("exit_threshold", 40)
        position_size = strategy.get("position_size", 0.1)
        
        for data_point in historical_data:
            timestamp = data_point.get("timestamp", "")
            coins = data_point.get("results", [])
            
            if not coins:
                continue
            
            top_coin = coins[0]
            score = top_coin.get("score", 0)
            price_change = top_coin.get("price_change_24h", 0)
            
            # Buy signal
            if self.position is None and score >= entry_threshold:
                investment = self.capital * position_size
                simulated_price = 1.0 + (price_change / 100)
                coins_bought = investment / simulated_price
                
                self.position = {"coin": top_coin.get("coin"), "amount": coins_bought,
                                "entry_price": simulated_price, "entry_score": score, "entry_time": timestamp}
                
                self.trades.append({"type": "BUY", "coin": top_coin.get("coin"), "amount": coins_bought,
                                "price": simulated_price, "value": investment, "timestamp": timestamp})
            
            # Sell signal
            elif self.position is not None and score <= exit_threshold:
                simulated_price = 1.0 + (price_change / 100)
                sell_value = self.position["amount"] * simulated_price
                
                self.trades.append({"type": "SELL", "coin": self.position["coin"], "amount": self.position["amount"],
                                "price": simulated_price, "value": sell_value, "timestamp": timestamp,
                                "profit": sell_value - (self.position["amount"] * self.position["entry_price")]})
                
                self.capital = sell_value
                self.position = None
            
            portfolio_value = self.capital
            if self.position:
                portfolio_value = self.position["amount"] * (1.0 + price_change / 100)
            
            self.equity_curve.append({"timestamp": timestamp, "value": portfolio_value})
        
        total_return = self.capital - self.initial_capital
        total_return_pct = (total_return / self.initial_capital) * 100
        
        sell_trades = [t for t in self.trades if t.get("type") == "SELL"]
        winning_trades = [t for t in sell_trades if t.get("profit", 0) > 0]
        win_rate = len(winning_trades) / max(len(sell_trades), 1)
        
        return BacktestResult(
            strategy_name=strategy.get("name", "Sentiment Strategy"),
            start_date=historical_data[0].get("timestamp", "") if historical_data else "",
            end_date=historical_data[-1].get("timestamp", "") if historical_data else "",
            initial_capital=self.initial_capital,
            final_capital=self.capital,
            total_return=total_return,
            total_return_pct=total_return_pct,
            max_drawdown=0,  # Simplified
            sharpe_ratio=0,  # Simplified
            win_rate=win_rate,
            num_trades=len(sell_trades),
            trades=self.trades,
            equity_curve=self.equity_curve
        )
