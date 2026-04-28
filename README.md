# Sentiment Analyzer CLI

CLI tool for sentiment analysis of X.com (Twitter) tweets using HuggingFace Transformers + Playwright.

## Features

- Scrape tweets from X.com based on any topic
- Sentiment analysis using `cardiffnlp/twitter-roberta-base-sentiment-latest`
- Interactive Rich CLI dashboard
- Export to CSV and JSON

## Setup

```bash
# Create venv
python -m venv venv
source venv/Scripts/activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browser
playwright install chromium

# Setup environment
cp .env.example .env
# Edit .env with X credentials

# Run
python src/main.py analyze "AI Technology"
```

## Usage

```bash
# Analyze a topic (interactive dashboard)
python src/main.py analyze --topic "AI Technology"

# Show stats only
python src/main.py analyze --topic "AI Technology" --format stats

# Show per-tweet breakdown
python src/main.py analyze --topic "AI Technology" --format breakdown

# Export results
python src/main.py analyze --topic "AI Technology" --export csv,json

# Custom tweet count
python src/main.py analyze --topic "AI Technology" --count 100
```