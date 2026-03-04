"""Metrics calculator for backtesting performance analysis."""

from typing import List, Dict
from dataclasses import dataclass

@dataclass
class PerformanceMetrics:
    total_return: float
    annualized_return: float
    volatility: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    calmar_ratio: float
    win_rate: float
    profit_factor: float
    avg_trade: float
    avg_win: float
    avg_loss: float
    num_trades: int
    num_wins: int
    num_losses: int

class MetricsCalculator:
    @staticmethod
    def calculate_all_metrics(trades: List[Dict], equity_curve: List[Dict], initial_capital: float) -> PerformanceMetrics:
        if not trades:
            return PerformanceMetrics(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        
        sell_trades = [t for t in trades if t.get("type") == "SELL"]
        final_value = equity_curve[-1]["value"] if equity_curve else initial_capital
        total_return = (final_value - initial_capital) / initial_capital
        
        returns = []
        for i in range(1, len(equity_curve)):
            ret = (equity_curve[i]["value"] - equity_curve[i-1]["value"]) / equity_curve[i-1]["value"]
            returns.append(ret)
        
        volatility = (sum((r - (sum(returns)/max(len(returns),1)))**2 for r in returns) / max(len(returns),1)) ** 0.5 if returns else 0
        sharpe_ratio = (sum(returns)/max(len(returns),1) / volatility) if volatility > 0 else 0
        
        downside_returns = [r for r in returns if r < 0]
        downside_std = (sum(r**2 for r in downside_returns) / max(len(downside_returns),1)) ** 0.5
        sortino_ratio = (sum(returns)/max(len(returns),1) / downside_std) if downside_std > 0 else 0
        
        peak = equity_curve[0]["value"] if equity_curve else initial_capital
        max_dd = 0
        for point in equity_curve:
            if point["value"] > peak:
                peak = point["value"]
            dd = (peak - point["value"]) / peak
            if dd > max_dd:
                max_dd = dd
        
        wins = [t for t in sell_trades if t.get("profit", 0) > 0]
        losses = [t for t in sell_trades if t.get("profit", 0) <= 0]
        win_rate = len(wins) / max(len(sell_trades), 1)
        
        gross_profit = sum(t.get("profit", 0) for t in wins)
        gross_loss = abs(sum(t.get("profit", 0) for t in losses))
        profit_factor = gross_profit / max(gross_loss, 1)
        
        avg_trade = sum(t.get("profit", 0) for t in sell_trades) / max(len(sell_trades), 1)
        avg_win = gross_profit / max(len(wins), 1)
        avg_loss = gross_loss / max(len(losses), 1)
        
        return PerformanceMetrics(
            total_return=total_return * 100,
            annualized_return=total_return * 100,
            volatility=volatility * 100,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            max_drawdown=max_dd * 100,
            calmar_ratio=abs(total_return / max_dd) if max_dd > 0 else 0,
            win_rate=win_rate * 100,
            profit_factor=profit_factor,
            avg_trade=avg_trade,
            avg_win=avg_win,
            avg_loss=-avg_loss,
            num_trades=len(sell_trades),
            num_wins=len(wins),
            num_losses=len(losses)
        )
