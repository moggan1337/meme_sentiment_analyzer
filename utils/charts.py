"""Charts and visualization module for analysis reports.

Provides matplotlib-based charts for sentiment, price, and volume analysis.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
import json

logger = logging.getLogger(__name__)

# Try to import matplotlib
try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.patches import Patch
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    logger.warning("matplotlib not available. Charts will be disabled.")

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


class ChartGenerator:
    """Generate charts and visualizations for analysis reports."""
    
    def __init__(self, output_dir: str = "reports/charts"):
        """Initialize chart generator.
        
        Args:
            output_dir: Directory to save generated charts
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        if not MATPLOTLIB_AVAILABLE:
            logger.error("matplotlib not available. Cannot generate charts.")
            return
        
        # Set style
        plt.style.use('dark_background')
        self.colors = {
            'bullish': '#00ff88',
            'bearish': '#ff4444',
            'neutral': '#ffaa00',
            'primary': '#00d4ff',
            'secondary': '#888888'
        }
    
    def generate_sentiment_chart(self, analysis_data: Dict[str, Any], 
                                filename: str = "sentiment_chart.png") -> Optional[str]:
        """Generate sentiment distribution chart.
        
        Args:
            analysis_data: Analysis results dictionary
            filename: Output filename
            
        Returns:
            Path to generated chart or None
        """
        if not MATPLOTLIB_AVAILABLE:
            return None
            
        results = analysis_data.get("results", [])
        if not results:
            logger.warning("No data for sentiment chart")
            return None
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Prepare data
        coins = [r.get("coin", "N/A") for r in results[:10]]
        scores = [r.get("score", 0) for r in results[:10]]
        sentiments = [r.get("sentiment", "neutral") for r in results[:10]]
        
        # Color based on sentiment
        colors = [self.colors.get(s, self.colors['neutral']) for s in sentiments]
        
        # Create horizontal bar chart
        bars = ax.barh(coins, scores, color=colors, edgecolor='white', alpha=0.8)
        
        # Add value labels
        for bar, score in zip(bars, scores):
            ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
                   f'{score:.1f}', va='center', fontsize=10)
        
        ax.set_xlabel('Sentiment Score', fontsize=12)
        ax.set_title('📊 Meme Coin Sentiment Analysis', fontsize=14, fontweight='bold')
        ax.set_xlim(0, 110)
        ax.grid(axis='x', alpha=0.3)
        
        # Add legend
        legend_elements = [
            Patch(facecolor=self.colors['bullish'], label='Bullish'),
            Patch(facecolor=self.colors['neutral'], label='Neutral'),
            Patch(facecolor=self.colors['bearish'], label='Bearish')
        ]
        ax.legend(handles=legend_elements, loc='lower right')
        
        plt.tight_layout()
        
        output_path = self.output_dir / filename
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Sentiment chart saved to {output_path}")
        return str(output_path)
    
    def generate_price_volume_chart(self, analysis_data: Dict[str, Any],
                                   filename: str = "price_volume_chart.png") -> Optional[str]:
        """Generate price and volume comparison chart.
        
        Args:
            analysis_data: Analysis results dictionary
            filename: Output filename
            
        Returns:
            Path to generated chart or None
        """
        if not MATPLOTLIB_AVAILABLE:
            return None
            
        results = analysis_data.get("results", [])
        if not results:
            return None
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        coins = [r.get("coin", "N/A") for r in results[:8]]
        price_changes = [r.get("price_change_24h", 0) for r in results[:8]]
        volume_changes = [r.get("volume_change", 0) for r in results[:8]]
        
        # Price change chart
        price_colors = ['#00ff88' if p >= 0 else '#ff4444' for p in price_changes]
        ax1.bar(coins, price_changes, color=price_colors, edgecolor='white')
        ax1.axhline(y=0, color='white', linestyle='-', linewidth=0.5)
        ax1.set_title('24h Price Change (%)', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Price Change (%)')
        ax1.tick_params(axis='x', rotation=45)
        ax1.grid(axis='y', alpha=0.3)
        
        # Volume change chart
        vol_colors = ['#00d4ff' if v >= 0 else '#ff6666' for v in volume_changes]
        ax2.bar(coins, volume_changes, color=vol_colors, edgecolor='white')
        ax2.axhline(y=0, color='white', linestyle='-', linewidth=0.5)
        ax2.set_title('Volume Change (%)', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Volume Change (%)')
        ax2.tick_params(axis='x', rotation=45)
        ax2.grid(axis='y', alpha=0.3)
        
        plt.suptitle('📈 Price & Volume Analysis', fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()
        
        output_path = self.output_dir / filename
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return str(output_path)
    
    def generate_history_chart(self, history_data: List[Dict],
                             filename: str = "history_chart.png") -> Optional[str]:
        """Generate historical trend chart.
        
        Args:
            history_data: List of historical data points
            filename: Output filename
            
        Returns:
            Path to generated chart or None
        """
        if not MATPLOTLIB_AVAILABLE or not history_data:
            return None
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Parse timestamps
        timestamps = []
        counts = []
        for item in history_data:
            try:
                ts = datetime.fromisoformat(item.get("timestamp", "").replace("Z", "+00:00"))
                timestamps.append(ts)
                counts.append(item.get("coins_passing", 0))
            except:
                continue
        
        if not timestamps:
            return None
        
        ax.plot(timestamps, counts, marker='o', color=self.colors['primary'], 
               linewidth=2, markersize=6)
        ax.fill_between(timestamps, counts, alpha=0.3, color=self.colors['primary'])
        
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Coins Passing Thresholds', fontsize=12)
        ax.set_title('📉 Historical Analysis Trends', fontsize=14, fontweight='bold')
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
        plt.xticks(rotation=45)
        ax.grid(alpha=0.3)
        
        plt.tight_layout()
        
        output_path = self.output_dir / filename
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return str(output_path)
    
    def generate_all_charts(self, analysis_data: Dict[str, Any], 
                           history_data: Optional[List[Dict]] = None) -> Dict[str, str]:
        """Generate all charts.
        
        Args:
            analysis_data: Current analysis data
            history_data: Optional historical data
            
        Returns:
            Dictionary of chart name to file path
        """
        charts = {}
        
        # Generate sentiment chart
        chart_path = self.generate_sentiment_chart(analysis_data)
        if chart_path:
            charts["sentiment"] = chart_path
        
        # Generate price/volume chart
        chart_path = self.generate_price_volume_chart(analysis_data)
        if chart_path:
            charts["price_volume"] = chart_path
        
        # Generate history chart
        if history_data:
            chart_path = self.generate_history_chart(history_data)
            if chart_path:
                charts["history"] = chart_path
        
        return charts


# Convenience function
def get_chart_generator(output_dir: str = "reports/charts") -> Optional[ChartGenerator]:
    """Get chart generator instance.
    
    Args:
        output_dir: Output directory for charts
        
    Returns:
        ChartGenerator instance or None
    """
    if not MATPLOTLIB_AVAILABLE:
        logger.warning("matplotlib not available")
        return None
    return ChartGenerator(output_dir=output_dir)
