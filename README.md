# Meme Coin Sentiment Analyzer

AI-powered cryptocurrency sentiment analysis agent for meme coins.

## Overview

Automated AI agent that scans social channels (Twitter/X, Reddit, Discord, Telegram), market data feeds (CoinGecko), and crypto news to analyze and score meme coins. Generates reports only when threshold criteria are met.

## Features

- **Multi-source data collection**: CoinGecko API, Reddit API
- **Sentiment analysis**: TextBlob-based NLP for social sentiment
- **Composite scoring**: Weighted formula combining sentiment, mentions, volume, price
- **Rules engine**: Configurable filtering thresholds
- **Smart reporting**: Generates reports only when coins meet criteria
- **Historical tracking**: Persistent storage for trend analysis

## Architecture

```
meme_sentiment_analyzer/
├── config/          # Configuration files
│   ├── config.yaml
│   └── coins.yaml
├── engine/          # Core analysis engine
│   ├── meme_agent.py    # Main orchestration
│   ├── ranker.py        # Scoring logic
│   └── generator.py     # Report generation
├── data_sources/    # API connectors
│   ├── coingecko.py
│   └── reddit.py
├── utils/          # Utilities
│   ├── sentiment_analyzer.py
│   └── rules_engine.py
└── tests/          # Test suite
```

## Installation

```bash
pip install -r requirements.txt
python -c "import nltk; nltk.download('punkt')"
```

## Configuration

Edit `config/config.yaml`:

```yaml
sentiment:
  min_confidence: 0.3
  bullish_threshold: 50
  bearish_threshold: -50
  weights:
    social: 0.4
    news: 0.3
    technical: 0.2
    fundamentals: 0.1

analysis:
  min_mentions: 10
  cooldown_hours: 4
  max_coins_per_report: 3
```

Edit `config/coins.yaml` to modify the watchlist.

## Usage

```python
import asyncio
from engine import MemeCoinAgent

agent = MemeCoinAgent()
asyncio.run(agent.run())
```

## Supported Coins

- SHIB (Shiba Inu)
- DOGE (Dogecoin)
- PEPE (Pepe)
- FLOKI
- BONK
- WIF (dogwifhat)
- BRETT
- MOG (Mog Coin)
- GUY

## Report Output

Reports are generated in `reports/` directory as:
- Markdown (.md) - Human readable
- JSON (.json) - Machine parseable

## Scoring Formula

```
Composite Score = (Sentiment × 0.4) + (Social Score × 0.3) + (Volume × 0.2) + (Price × 0.1)
```

Where:
- Sentiment: -50 to +50 (bullish/bearish)
- Social Score: Mention count + growth rate
- Volume: 24h volume change
- Price: 24h price change

## License

MIT
