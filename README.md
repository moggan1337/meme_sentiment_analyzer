# Crypto Meme Sentiment Analyzer

AI-powered sentiment analysis system for meme coins.

## Features
- Multi-source data collection (CoinGecko, Reddit)
- Sentiment analysis with TextBlob/NLTK
- Configurable scoring thresholds
- Hourly automated reports

## Setup
```bash
pip install -r requirements.txt
python -m nltk.downloader vader_lexicon
```

## Usage
```bash
python -m engine.meme_agent
```
