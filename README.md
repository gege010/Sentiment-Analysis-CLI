# Sentiment Analyzer CLI

CLI tool for sentiment analysis of X.com (Twitter) tweets using HuggingFace Transformers + Playwright.

## Features

- **Smart Topic Expansion** - Automatically expands topics into related terms for better data coverage
- **Multi-Source Scraping** - Scrapes from multiple related searches simultaneously
- **Sentiment Analysis** - Uses `cardiffnlp/twitter-roberta-base-sentiment-latest` with Indonesian lexicon boost
- **Indonesian Language Support** - Enhanced accuracy for Indonesian slang and emoticons
- **Interactive Rich CLI Dashboard** - Visual sentiment breakdown with highlights
- **Export to CSV/JSON** - Save results for further analysis
- **Debug Mode** - Verify scraped data and sentiment accuracy
- **Cookie-based Authentication** - More reliable than password login

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
```

## Authentication (Cookie Method - Recommended)

### Option 1: Auto-export cookies (Recommended)
1. Log into X.com in Chrome browser
2. Run the export script:
   ```bash
   python scripts/export_cookies.py --save
   ```
   This will extract cookies from Chrome and save them to `.env`

### Option 2: Manual cookies
1. Log into X.com in Chrome browser
2. Open DevTools (F12) → Application → Cookies → x.com
3. Copy these values to your `.env`:
   ```
   X_COOKIE_AUTH_TOKEN=your_auth_token
   X_COOKIE_CT0=your_csrf_token
   X_COOKIE_GUEST_ID=your_guest_id
   ```

### Option 3: Username/Password (May be blocked)
```
X_USERNAME=your_email
X_PASSWORD=your_password
```
Note: X.com may block this method with verification challenges.

## Usage

### Basic Commands
```bash
# Interactive dashboard (default)
python -m src.main analyze --topic "AI Technology"

# Stats only
python -m src.main analyze --topic "AI" --format stats

# Per-tweet breakdown
python -m src.main analyze --topic "Machine Learning" --format breakdown

# Export results
python -m src.main analyze --topic "AI" --export csv,json

# Custom tweet count
python -m src.main analyze --topic "AI" --count 100
```

### Advanced Options
```bash
# Debug mode - show raw tweets and sentiment for verification
python -m src.main analyze --topic "MBG" --debug

# Disable topic expansion (use exact search term)
python -m src.main analyze --topic "MBG" --no-expand

# Show browser window (for debugging scraping)
python -m src.main analyze --topic "AI" --headful

# Combine options
python -m src.main analyze --topic "MBG" --count 100 --debug --export csv
```

### Topic Expansion Examples
The CLI automatically expands topics into related terms:

| Input Topic | Expanded Terms |
|-------------|----------------|
| `MBG` | MBG, Makan Bergizi Gratis, Prabowo, Prabowo Subianto, #Prabowo, susu MBG, dapur MBG, stunting... |
| `AI` | AI, Artificial Intelligence, ChatGPT, GPT, Machine Learning, #AI, #MachineLearning... |
| `pendidikan` | pendidikan, sekolah, kampus, guru, siswa, mahasiswa, beasiswa... |

## Output Formats

### Dashboard
```
Topic: 'MBG'
Expanded to 14 related terms...

Scraping from 14 sources...
  [1/14] Scraping: 'Prabowo Subianto' ... -> Got 50 new tweets (Total: 50)
  [2/14] Scraping: 'dapur MBG' ... -> Got 50 new tweets (Total: 100)

+---------------------- [CHART] Sentiment Analysis: MBG ----------------------+
|   Topic             MBG                                                     |
|   Total Tweets      100                                                     |
|   Avg Confidence    79.7%                                                   |
|   Positive          22 (22.0%)                                              |
|   Neutral           63 (63.0%)                                              |
|   Negative          15 (15.0%)                                              |
+-----------------------------------------------------------------------------+

  + Positive  ####----------------    22 (22.0%)
  = Neutral   ############--------    63 (63.0%)
  - Negative  ###-----------------    15 (15.0%)

+-------------------------------- Highlights ---------------------------------+
| + Top Positive: proyek kereta api whoosh di zaman jokowi...               |
| - Top Negative: train collision leaves 15 dead in indonesia...              |
+-----------------------------------------------------------------------------+
```

### Stats
```
Topic: MBG
Total Tweets: 100
Avg Confidence: 79.7%

Sentiment Distribution:
  Positive: 22 (22.0%)
  Neutral:  63 (63.0%)
  Negative: 15 (15.0%)
```

### Breakdown
```
  1. [+] POSITIVE (conf:92%) proyek kereta api whoosh di zaman jokowi...
  2. [=] NEUTRAL (conf:82%) lebih dari sekadar makan siang gratis...
  3. [-] NEGATIVE (conf:89%) train collision leaves 15 dead in indonesia...
```

### Debug Mode Output
```
=== RAW TWEETS (DEBUG) ===

1. @TasyaFahira18 (2026-04-28):
   Lebih dari sekadar makan siang gratis, MBG adalah investasi jangka panjang...
   Cleaned: lebih dari sekadar makan siang gratis mbg adalah investasi jangka panjang...
   Sentiment: [POSITIVE] conf=82.0%
```

## Project Structure

```
sentiment-cli/
├── src/
│   ├── cli/
│   │   ├── commands.py       # CLI commands (Typer)
│   │   ├── dashboard.py       # Rich dashboard UI
│   │   └── formatters.py      # Output formatters
│   ├── config/
│   │   └── settings.py        # Settings loader (cookie & credentials)
│   ├── crawler/
│   │   ├── rate_limiter.py       # Rate limiting
│   │   ├── topic_expander.py      # Topic expansion logic
│   │   └── x_scraper.py           # X.com scraper
│   ├── engine/
│   │   ├── indonesian_lexicon.py  # Indonesian slang/emoticon lexicon
│   │   ├── preprocessor.py       # Tweet cleaning
│   │   └── sentiment_analyzer.py  # HuggingFace + lexicon analyzer
│   ├── output/
│   │   └── exporter.py      # CSV/JSON exporter
│   └── main.py              # Entry point
├── scripts/
│   └── export_cookies.py    # Cookie export utility
├── tests/                   # Test suite (57 tests)
├── .env.example             # Environment template
├── requirements.txt          # Dependencies
└── README.md
```

## Testing

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_config.py

# Run with verbose output
python -m pytest -v

# Run with coverage
python -m pytest --cov=src
```

## Sentiment Analysis Model

The analyzer uses a hybrid approach:
1. **HuggingFace Model** - `cardiffnlp/twitter-roberta-base-sentiment-latest`
2. **Indonesian Lexicon** - Local dictionary with Indonesian slang and emoticons
   - Positive: "mantap", "keren", "sukses", "bagus", "luar biasa", "❤", "🔥"...
   - Negative: "kecewa", "gagal", "sedih", "marah", "parah", "💔", "😭"...

When the lexicon agrees with the model, confidence is boosted. When they disagree, confidence is adjusted.

## Troubleshooting

### Scraping Issues
- **No tweets collected**: Check if cookies are valid and not expired
- **Few tweets**: X.com has limits on live search results. Try `--count 100`
- **Stuck scraping**: The CLI has auto-recovery and stuck detection

### Sentiment Accuracy
- Use `--debug` to verify each tweet's sentiment
- Indonesian text with slang may need manual verification
- Low confidence (<50%) indicates ambiguous text

### Cookie Export Fails
1. Make sure Chrome is installed
2. Close Chrome completely before exporting
3. Try manual cookie extraction from DevTools