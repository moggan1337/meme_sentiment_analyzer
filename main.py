"""FastAPI web dashboard for Meme Coin Sentiment Analyzer.

Provides:
- REST API for analysis results
- Web UI dashboard
- Real-time data endpoints
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Meme Coin Sentiment Analyzer API",
    description="API for meme coin sentiment analysis and monitoring",
    version="1.0.0"
)

# Project root directory
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
REPORTS_DIR = PROJECT_ROOT / "reports"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)

# ============ Data Models ============

class CoinAnalysis(BaseModel):
    """Coin analysis result model."""
    coin: str
    score: float
    sentiment: str
    confidence: float
    mentions: int
    price_change_24h: float
    volume_change: float

class AnalysisSummary(BaseModel):
    """Analysis summary model."""
    timestamp: str
    coins_analyzed: int
    coins_passing: int
    top_coins: List[CoinAnalysis]

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    timestamp: str

# ============ API Endpoints ============

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the dashboard home page."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Meme Coin Sentiment Analyzer</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                min-height: 100vh; color: #fff;
            }
            .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
            header { 
                text-align: center; padding: 40px 0; 
                border-bottom: 1px solid rgba(255,255,255,0.1);
            }
            h1 { font-size: 2.5rem; margin-bottom: 10px; }
            .subtitle { color: #888; font-size: 1.1rem; }
            .stats-grid {
                display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px; margin: 40px 0;
            }
            .stat-card {
                background: rgba(255,255,255,0.05);
                border-radius: 15px; padding: 25px;
                border: 1px solid rgba(255,255,255,0.1);
            }
            .stat-value { font-size: 2.5rem; font-weight: bold; color: #00d4ff; }
            .stat-label { color: #888; margin-top: 5px; }
            .section { margin: 40px 0; }
            .section h2 { margin-bottom: 20px; font-size: 1.5rem; }
            .coins-grid {
                display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                gap: 15px;
            }
            .coin-card {
                background: rgba(255,255,255,0.05);
                border-radius: 10px; padding: 20px;
                border-left: 4px solid #00d4ff;
            }
            .coin-header { display: flex; justify-content: space-between; align-items: center; }
            .coin-name { font-weight: bold; font-size: 1.2rem; }
            .sentiment { padding: 5px 10px; border-radius: 20px; font-size: 0.8rem; }
            .sentiment.bullish { background: rgba(0,255,0,0.2); color: #00ff00; }
            .sentiment.bearish { background: rgba(255,0,0,0.2); color: #ff4444; }
            .sentiment.neutral { background: rgba(255,255,0,0.2); color: #ffff00; }
            .coin-stats { margin-top: 15px; display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
            .coin-stat { font-size: 0.9rem; }
            .coin-stat span { color: #888; }
            .api-links { background: rgba(255,255,255,0.05); padding: 20px; border-radius: 10px; }
            .api-links a { color: #00d4ff; margin-right: 20px; }
            .btn {
                display: inline-block; padding: 12px 30px;
                background: #00d4ff; color: #1a1a2e;
                border-radius: 25px; text-decoration: none;
                font-weight: bold; margin-top: 20px;
            }
            .btn:hover { background: #00b8e6; }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>🚀 Meme Coin Sentiment Analyzer</h1>
                <p class="subtitle">Real-time meme coin sentiment analysis and ranking</p>
            </header>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value" id="totalCoins">-</div>
                    <div class="stat-label">Total Coins Analyzed</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="passingCoins">-</div>
                    <div class="stat-label">Coins Passing Thresholds</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="topCoin">-</div>
                    <div class="stat-label">Top Performer</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="lastUpdate">-</div>
                    <div class="stat-label">Last Update</div>
                </div>
            </div>
            
            <div class="section">
                <h2>📊 Latest Analysis Results</h2>
                <div class="coins-grid" id="coinsGrid">
                    <p>Loading...</p>
                </div>
            </div>
            
            <div class="section">
                <h2>🔗 API Endpoints</h2>
                <div class="api-links">
                    <a href="/api/latest">/api/latest</a> - Latest analysis results
                    <a href="/api/coins">/api/coins</a> - All tracked coins
                    <a href="/api/history">/api/history</a> - Historical data
                    <a href="/health">/health</a> - Health check
                </div>
            </div>
            
            <div style="text-align: center;">
                <a href="#" class="btn" onclick="runAnalysis()">🔄 Run New Analysis</a>
            </div>
        </div>
        
        <script>
            async function loadData() {
                try {
                    const response = await fetch('/api/latest');
                    const data = await response.json();
                    
                    document.getElementById('totalCoins').textContent = data.coins_analyzed || 0;
                    document.getElementById('passingCoins').textContent = data.coins_passing || 0;
                    document.getElementById('topCoin').textContent = data.top_coins?.[0]?.coin || 'N/A';
                    document.getElementById('lastUpdate').textContent = new Date(data.timestamp).toLocaleTimeString();
                    
                    const grid = document.getElementById('coinsGrid');
                    if (data.top_coins && data.top_coins.length > 0) {
                        grid.innerHTML = data.top_coins.map(coin => `
                            <div class="coin-card">
                                <div class="coin-header">
                                    <span class="coin-name">${coin.coin}</span>
                                    <span class="sentiment ${coin.sentiment}">${coin.sentiment}</span>
                                </div>
                                <div class="coin-stats">
                                    <div class="coin-stat"><span>Score:</span> ${coin.score.toFixed(1)}</div>
                                    <div class="coin-stat"><span>Mentions:</span> ${coin.mentions}</div>
                                    <div class="coin-stat"><span>Price 24h:</span> ${coin.price_change_24h >= 0 ? '+' : ''}${coin.price_change_24h.toFixed(1)}%</div>
                                    <div class="coin-stat"><span>Volume:</span> ${coin.volume_change >= 0 ? '+' : ''}${coin.volume_change.toFixed(1)}%</div>
                                </div>
                            </div>
                        `).join('');
                    } else {
                        grid.innerHTML = '<p>No analysis data available. Run an analysis first.</p>';
                    }
                } catch (e) {
                    console.error(e);
                    document.getElementById('coinsGrid').innerHTML = '<p>Error loading data. Make sure to run analysis first.</p>';
                }
            }
            
            async function runAnalysis() {
                const btn = document.querySelector('.btn');
                btn.textContent = '⏳ Running...';
                btn.disabled = true;
                
                try {
                    const response = await fetch('/api/run', { method: 'POST' });
                    if (response.ok) {
                        await loadData();
                    }
                } catch (e) {
                    console.error(e);
                }
                
                btn.textContent = '🔄 Run New Analysis';
                btn.disabled = false;
            }
            
            loadData();
            setInterval(loadData, 60000); // Refresh every minute
        </script>
    </body>
    </html>
    """


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.utcnow().isoformat()
    )


@app.get("/api/latest")
async def get_latest_analysis():
    """Get the latest analysis results."""
    import json
    
    # Try to read latest report
    report_files = sorted(REPORTS_DIR.glob("analysis_*.json"), reverse=True)
    
    if report_files:
        try:
            with open(report_files[0]) as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading report: {e}")
    
    # Return mock data if no reports exist
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "coins_analyzed": 9,
        "coins_passing": 3,
        "results": []
    }


@app.get("/api/coins")
async def get_coins():
    """Get all tracked coins."""
    import yaml
    
    coins_file = PROJECT_ROOT / "config" / "coins.yaml"
    if coins_file.exists():
        with open(coins_file) as f:
            config = yaml.safe_load(f)
            return config.get("watchlist", [])
    
    return []


@app.get("/api/history")
async def get_history(days: int = Query(7, ge=1, le=30)):
    """Get historical analysis data."""
    import json
    
    history = []
    cutoff = datetime.utcnow() - timedelta(days=days)
    
    for report_file in REPORTS_DIR.glob("analysis_*.json"):
        try:
            mtime = datetime.fromtimestamp(report_file.stat().st_mtime)
            if mtime >= cutoff:
                with open(report_file) as f:
                    data = json.load(f)
                    history.append({
                        "timestamp": data.get("timestamp"),
                        "coins_analyzed": data.get("coins_analyzed"),
                        "coins_passing": data.get("coins_passing")
                    })
        except Exception as e:
            logger.error(f"Error reading {report_file}: {e}")
    
    return sorted(history, key=lambda x: x["timestamp"], reverse=True)


@app.post("/api/run")
async def run_analysis():
    """Trigger a new analysis run."""
    try:
        from engine.meme_agent import MemeAgent
        
        agent = MemeAgent()
        result = agent.run_analysis()
        
        return {"status": "success", "result": result}
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ Main ============

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
