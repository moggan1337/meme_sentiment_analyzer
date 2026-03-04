#!/bin/bash

# Meme Sentiment Analyzer - Setup Script
# This script sets up the development environment

set -e

echo "=========================================="
echo "Meme Sentiment Analyzer Setup"
echo "=========================================="

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo "Step 1: Creating virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists. Removing old venv..."
    rm -rf venv
fi

python3 -m venv venv

echo ""
echo "Step 2: Activating virtual environment..."
source venv/bin/activate

echo ""
echo "Step 3: Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "Step 4: Downloading NLTK data..."
python3 -c "
import nltk
nltk.download('punkt', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('stopwords', quiet=True)
print('NLTK data downloaded successfully!')
"

echo ""
echo "Step 5: Creating .env file from template..."
if [ -f ".env" ]; then
    echo ".env file already exists. Skipping..."
else
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo ".env created from .env.example"
        echo "Please edit .env and add your API keys!"
    else
        echo ".env.example not found. Creating default .env..."
        cat > .env << 'ENVEOF'
# Reddit API (optional - for production use)
REDDIT_CLIENT_ID=
REDDIT_CLIENT_SECRET=
REDDIT_USERNAME=
REDDIT_PASSWORD=

# Twitter/X API (optional - for production use)
TWITTER_BEARER_TOKEN=

# CoinGecko (free tier available, no key required for basic use)
COINGECKO_API_KEY=

# CoinMarketCap (optional)
CMC_API_KEY=

# Discord Webhook (optional - for notifications)
DISCORD_WEBHOOK_URL=
ENVEOF
    fi
fi

echo ""
echo "=========================================="
echo "Setup completed successfully!"
echo "=========================================="
echo ""
echo "To activate the virtual environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "To run the analyzer, use:"
echo "  python -m engine.meme_agent"
echo ""
echo "Don't forget to configure your API keys in .env!"
