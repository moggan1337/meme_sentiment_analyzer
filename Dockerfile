# Meme Coin Sentiment Analyzer - Docker Configuration

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TZ=UTC

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data
RUN python -c "import nltk; \
    nltk.download('punkt', download_dir='/usr/local/share/nltk_data'); \
    nltk.download('averaged_perceptron_tagger', download_dir='/usr/local/share/nltk_data'); \
    nltk.download('wordnet', download_dir='/usr/local/share/nltk_data'); \
    nltk.download('stopwords', download_dir='/usr/local/share/nltk_data')"

# Set NLTK data path
ENV NLTK_DATA=/usr/local/share/nltk_data

# Copy project files
COPY . .

# Create necessary directories
RUN mkdir -p data reports logs

# Copy .env.example to .env (will be overridden at runtime)
RUN if [ -f .env.example ]; then cp .env.example .env; fi

# Expose ports
EXPOSE 8000

# Health check
HEALTHCHECK --interval=5m --timeout=3s \
    CMD python -c "import requests; requests.get('http://localhost:8000/health', timeout=2)" || exit 1

# Default command
CMD ["python", "-m", "engine.meme_agent"]
