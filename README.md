# Sentiment Analyzer CLI

CLI tool for sentiment analysis of X.com (Twitter) tweets using HuggingFace Transformers + Playwright.

## Features

- **Smart Topic Expansion** - Automatically expands topics into related terms for better data coverage
- **Multi-Source Scraping** - Scrapes from multiple related searches simultaneously
- **Sentiment Analysis** - Uses IndoBERT (`w11wo/indonesian-roberta-base-sentiment-classifier`)
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

## Authentication (Cookie Method - Required)

X.com requires authentication to scrape tweets. The CLI validates your cookies before allowing you to run any analysis.

### Manual Cookies (100% Reliable)
Due to Windows security and browser profile locking, manual cookie extraction is the required and most reliable method.

1. Log into X.com in your web browser.
2. Open Developer Tools (F12) → Application → Cookies → `https://x.com`
3. Copy these three values to your `.env` file:
   ```env
   X_COOKIE_AUTH_TOKEN=your_auth_token
   X_COOKIE_CT0=your_ct0_value
   X_COOKIE_GUEST_ID=your_guest_id_value
   ```

### Username/Password (Fallback - May be blocked)
```env
X_USERNAME=your_email
X_PASSWORD=your_password
```
*Note: X.com often blocks this method with verification challenges, so Cookies are highly recommended.*

## Usage

The CLI is fully interactive. Simply run the `analyze` command and follow the prompts:

```bash
python -m src.main analyze
```

The program will interactively ask for:
- Product/Topic name
- Number of tweets to fetch
- Output format (dashboard/stats/breakdown)
- Export format (csv/json/none)
- Output directory
- Whether to use auto topic expansion

### Advanced / Scripting Options
You can still bypass the interactive prompts by providing the options directly:

```bash
# Debug mode - show raw tweets and sentiment for verification
python -m src.main analyze --topic "MBG" --count 100 --debug

# Combine options for scripting
python -m src.main analyze --topic "MBG" --count 100 --format dashboard --export csv --no-expand
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

+---------------------- [CHART] Product Grades Report: MBG ---------------------+
|   Topic/Product     MBG                                                     |
|   Total Tweets      100                                                     |
|   Product Grade     B (Baik)                                                |
|   Grade Score       72.5/100                                                |
|   Avg Confidence    85.2%                                                   |
|   Positive          45 (45.0%)                                              |
|   Neutral           55 (55.0%)                                              |
|   Negative          0 (0.0%)                                                |
+-----------------------------------------------------------------------------+

  + Positive  #########-----------    45 (45.0%)
  = Neutral   ###########---------    55 (55.0%)
  - Negative  --------------------     0 (0.0%)

+-------------------------------- Highlights ---------------------------------+
| + Top Positive: program MBG ini sangat membantu meringankan beban...        |
| - Top Negative: N/A                                                         |
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
│   │   ├── settings.py        # Settings loader (cookie & credentials)
│   │   └── cookie_manager.py  # Cookie extraction utility
│   ├── crawler/
│   │   ├── rate_limiter.py       # Rate limiting
│   │   ├── topic_expander.py      # Topic expansion logic
│   │   └── x_scraper.py           # X.com scraper
│   ├── engine/
│   │   ├── preprocessor.py       # Tweet cleaning
│   │   └── sentiment_analyzer.py  # IndoBERT analyzer
│   ├── output/
│   │   └── exporter.py      # CSV/JSON exporter
│   └── main.py              # Entry point
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

The analyzer uses the HuggingFace Model IndoBERT (`w11wo/indonesian-roberta-base-sentiment-classifier`), which natively understands Indonesian text, slang, and context.

## Troubleshooting

### Scraping Issues
- **No tweets collected**: Check if cookies are valid and not expired
- **Few tweets**: X.com has limits on live search results. Try `--count 100`
- **Stuck scraping**: The CLI has auto-recovery and stuck detection

### Sentiment Accuracy
- Use `--debug` to verify each tweet's sentiment
- Indonesian text with slang may need manual verification
- Low confidence (<50%) indicates ambiguous text