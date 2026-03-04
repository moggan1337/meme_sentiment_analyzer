# 🐕 Meme Coin Sentiment Analyzer

A powerful sentiment analysis pipeline for identifying emerging and trending meme coins by analyzing social media discussions and market data.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Version](https://img.shields.io/badge/Version-1.0.0-orange.svg)

---

## 📌 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [API Keys Required](#api-keys-required)
- [Output](#output)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

**Meme Coin Sentiment Analyzer** is an automated pipeline that monitors cryptocurrency discussions across multiple social platforms, analyzes sentiment, and ranks meme coins by their bullish potential. It combines social sentiment analysis with market data to identify coins with growing interest and positive momentum.

### Use Cases

- 🛰️ **Discover emerging gems** before they go viral
- 📊 **Track sentiment trends** for existing meme coins
- 🔍 **Monitor competitor activity** across social platforms
- 📈 **Generate actionable reports** for trading decisions

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **Multi-Source Data Collection** | Fetches data from Reddit, Twitter/X, and CoinGecko |
| **Sentiment Analysis** | NLP-powered analysis using TextBlob and Twitter RoBERTa models |
| **Real-time Market Data** | Live price, volume, and market cap from CoinGecko |
| **Rule-Based Filtering** | Configurable thresholds for filtering low-quality signals |
| **Weighted Scoring** | Composite scoring algorithm with customizable weights |
| **Automated Reports** | Generates both Markdown and JSON reports |
| **Scheduled Execution** | Built-in scheduler for periodic analysis |
| **Extensible Design** | Easy to add new data sources or analysis methods |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        MemeAgent                             │
│                   (Main Orchestrator)                        │
│         Coordinates: fetch → analyze → rank → report        │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
   ┌──────────┐  ┌──────────┐  ┌──────────┐
   │CoinGecko │  │  Reddit  │  │ Twitter  │
   │(market)  │  │ (social) │  │ (social) │
   │  price   │  │  posts   │  │  tweets  │
   │  volume  │  │comments  │  │  likes   │
   └────┬─────┘  └────┬─────┘  └────┬─────┘
        │              │              │
        └──────────────┼──────────────┘
                       ▼
            ┌─────────────────────┐
            │  SentimentAnalyzer   │
            │   (TextBlob NLP)    │
            │  Polarity: -1 to +1 │
            │  Subjectivity: 0-1  │
            └──────────┬───────────┘
                       ▼
            ┌─────────────────────┐
            │    RulesEngine       │
            │  (Filter/Validate)  │
            │  - Min confidence   │
            │  - Min mentions     │
            │  - Sentiment bounds │
            └──────────┬───────────┘
                       ▼
            ┌─────────────────────┐
            │      Ranker          │
            │  (Weighted Scoring)  │
            │  sentiment: 40%     │
            │  social: 30%        │
            │  volume: 20%        │
            │  price: 10%         │
            └──────────┬───────────┘
                       ▼
            ┌─────────────────────┐
            │   ReportGenerator    │
            │  (Markdown + JSON)   │
            └─────────────────────┘
```

---

## 📥 Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Clone the Repository

```bash
git clone https://github.com/moggan1337/meme_sentiment_analyzer.git
cd meme_sentiment_analyzer
```

### Create Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Download NLTK Data

```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger')"
```

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Reddit API (optional - for production use)
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USERNAME=your_username
REDDIT_PASSWORD=your_password

# Twitter/X API (optional - for production use)
TWITTER_BEARER_TOKEN=your_bearer_token

# CoinGecko (free tier available, no key required for basic use)
COINGECKO_API_KEY=your_api_key  # optional

# CoinMarketCap (optional)
CMC_API_KEY=your_api_key

# Discord Webhook (optional - for notifications)
DISCORD_WEBHOOK_URL=your_webhook_url
```

### config.yaml

Main configuration file located at `config/config.yaml`:

```yaml
app:
  name: "Meme Coin Sentiment Analyzer"
  version: "1.0.0"
  log_level: "INFO"

api:
  coingecko:
    base_url: "https://api.coingecko.com/api/v3"
    rate_limit: 10
    timeout: 30
  reddit:
    user_agent: "MemeCoinSentimentAnalyzer/1.0"
    rate_limit: 60
    timeout: 30

sentiment:
  min_confidence: 0.3
  bullish_threshold: 50
  bearish_threshold: -50
  weights:
    sentiment: 0.35
    mentions: 0.25
    volume: 0.20
    price_change: 0.20

analysis:
  check_interval_minutes: 15
  min_data_points: 3
  lookback_hours: 24

reporting:
  output_dir: "reports"
  format: "markdown"
  include_charts: true
  auto_generate: false

storage:
  type: "json"
  data_dir: "data"
  retention_days: 30

scheduler:
  enabled: true
  timezone: "UTC"
```

### coins.yaml

Configure the meme coins to track in `config/coins.yaml`:

```yaml
watchlist:
  - id: "shiba-inu"
    symbol: "SHIB"
    name: "Shiba Inu"
    enabled: true
  - id: "dogecoin"
    symbol: "DOGE"
    name: "Dogecoin"
    enabled: true
  - id: "pepe"
    symbol: "PEPE"
    name: "Pepe"
    enabled: true
  # Add more coins as needed

thresholds:
  sentiment_min: 50
  mention_growth_min: 50
  volume_change_min: 20
  price_change_min: 5
  cooldown_hours: 4
  max_per_report: 3
```

---

## 🚀 Usage

### Run Single Analysis

```bash
python -m engine.meme_agent
```

Or from project root:

```bash
python engine/meme_agent.py
```

### Run with Custom Config

```bash
python -m engine.meme_agent --config custom_config.yaml
```

### Scheduled Execution

The scheduler runs analysis at configured intervals (default: every 15 minutes):

```bash
# Enable scheduler in config.yaml
scheduler:
  enabled: true
  
# Run the scheduler
python -m engine.meme_agent --schedule
```

### Programmatic Usage

```python
from engine.meme_agent import MemeAgent

# Initialize the agent
agent = MemeAgent()

# Run analysis
results = agent.run_analysis()

# Access results
print(f"Coins analyzed: {results['coins_analyzed']}")
print(f"Coins passing: {results['coins_passing']}")
print(f"Report saved to: {results['report_path']}")
```

---

## 📁 Project Structure

```
meme_sentiment_analyzer/
├── config/                      # Configuration modules
│   ├── __init__.py
│   ├── config.yaml              # Main configuration
│   ├── coins.yaml               # Coin watchlist
│   ├── settings.py              # Settings management
│   └── thresholds.py            # Threshold config
├── data_sources/                # Data collection
│   ├── __init__.py
│   ├── base.py                  # Abstract base classes
│   ├── coingecko.py             # CoinGecko API client
│   ├── reddit.py                # Reddit API client
│   └── twitter_source.py       # Twitter/X data source
├── engine/                      # Core analysis engine
│   ├── __init__.py
│   ├── meme_agent.py            # Main orchestrator
│   ├── ranker.py                # Scoring & ranking
│   └── generator.py             # Report generation
├── utils/                       # Utilities
│   ├── __init__.py
│   ├── sentiment_analyzer.py    # NLP sentiment analysis
│   └── rules_engine.py          # Rule-based filtering
├── tests/                       # Unit tests
│   └── __init__.py
├── data/                        # Data storage (generated)
├── reports/                     # Reports output (generated)
├── logs/                        # Log files (generated)
├── requirements.txt             # Python dependencies
├── config.yaml                  # Legacy config
├── coins.yaml                   # Legacy coin config
└── .gitignore                   # Git ignore rules
```

---

## 🔑 API Keys Required

| Service | Required | Free Tier | Notes |
|---------|----------|-----------|-------|
| **CoinGecko** | No | Yes | Basic rate limits apply |
| **Reddit** | No* | Yes | *Mock data without credentials |
| **Twitter/X** | No* | Limited | *Mock data without credentials |
| **CoinMarketCap** | No | No | Optional - for extended data |
| **Discord** | No | N/A | Optional - for notifications |

*Note: The application works with mock data when API keys are not provided.

---

## 📊 Output

### Generated Reports

Reports are saved to the `reports/` directory (configurable):

#### Markdown Report

```markdown
# Meme Coin Sentiment Analysis Report

**Generated:** 2024-01-15 14:30 UTC
**Coins Analyzed:** 9
**Coins Passing:** 3

---

## Summary

| Coin | Score | Sentiment | Confidence | Mentions | Price Change |
|------|-------|-----------|------------|----------|--------------|
| PEPE | 78.5 | Bullish | 0.82 | 1,234 | +5.2% |
| SHIB | 72.1 | Bullish | 0.75 | 2,891 | +3.1% |
| DOGE | 68.9 | Bullish | 0.71 | 5,432 | +1.8% |

---

## Detailed Analysis

### 🐸 PEPE
- **Score:** 78.5
- **Sentiment:** Bullish (62/100)
- **Confidence:** 0.82
- **Mentions:** 1,234 (+45% growth)
- **Price Change:** +5.2% (24h)
- **Volume Change:** +32%
```

#### JSON Report

```json
{
  "timestamp": "2024-01-15T14:30:00Z",
  "coins_analyzed": 9,
  "coins_passing": 3,
  "results": [
    {
      "coin": "PEPE",
      "score": 78.5,
      "sentiment": "bullish",
      "sentiment_score": 62,
      "confidence": 0.82,
      "mentions": 1234,
      "mention_growth": 45,
      "price_change_24h": 5.2,
      "volume_change": 32.0
    }
  ]
}
```

---

## 🧪 Testing

Run the test suite:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=. --cov-report=html
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Guidelines

- Use type hints where possible
- Follow PEP 8 style guide
- Add docstrings to new functions
- Write tests for new features
- Update documentation accordingly

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [CoinGecko](https://www.coingecko.com/) for free crypto market data
- [Reddit](https://www.reddit.com/) for community discussions
- [TextBlob](https://textblob.readthedocs.io/) for sentiment analysis
- [Hugging Face](https://huggingface.co/) for transformer models

---

## 🔮 Roadmap

- [ ] Add Discord data source
- [ ] Implement Twitter API v2
- [ ] Add chart generation with matplotlib
- [ ] Create web dashboard
- [ ] Add Telegram notifications
- [ ] Implement ML-based prediction model
- [ ] Add backtesting capabilities
- [ ] Create Docker container

---

## 📧 Contact

For issues and feature requests, please open an issue on GitHub.

---

**Made with 💙 for the meme coin community**

