import typer
from typing import List, Tuple
from src.engine.sentiment_analyzer import SentimentAnalyzer
from src.engine.preprocessor import clean_tweet
from src.crawler.x_scraper import XScraper, XScrapeError, Tweet
from src.crawler.topic_expander import expand_topic
from src.cli.dashboard import print_dashboard
from src.cli.formatters import format_stats, format_breakdown
from src.output.exporter import Exporter

__version__ = "0.2.0"

app = typer.Typer(
    name="sentiment-cli",
    help="Sentiment analysis CLI for X.com (Twitter) tweets",
)
export_app = typer.Typer(help="Export previously saved results")
app.add_typer(export_app, name="export")


@app.command("version")
def version() -> None:
    """Print version."""
    typer.echo(f"sentiment-cli v{__version__}")


def scrape_with_topics(
    topics: List[str],
    scraper: XScraper,
    total_count: int,
    seen_ids: set
) -> Tuple[List[Tweet], dict]:
    """
    Scrape tweets from multiple topics and deduplicate.

    Returns:
        Tuple of (tweets list, topic_stats dict)
    """
    all_tweets: List[Tweet] = []
    topic_stats = {}

    for topic in topics:
        if len(all_tweets) >= total_count:
            break

        # Calculate how many more tweets we need
        remaining = total_count - len(all_tweets)

        try:
            result = scraper.scrape(topic)

            # Filter out duplicates
            new_tweets = [t for t in result.tweets if t.id not in seen_ids]
            all_tweets.extend(new_tweets)
            seen_ids.update(t.id for t in new_tweets)

            topic_stats[topic] = {
                "total": len(result.tweets),
                "new": len(new_tweets),
            }

        except Exception as e:
            topic_stats[topic] = {"error": str(e)}

    return all_tweets, topic_stats


@app.command()
def analyze(
    topic: str = typer.Option(..., "--topic", "-t", help="Topic to analyze"),
    count: int = typer.Option(200, "--count", "-c", help="Number of tweets to scrape"),
    format: str = typer.Option("dashboard", "--format", "-f",
        help="Output format: dashboard, stats, breakdown"),
    export: str = typer.Option("", "--export", "-e",
        help="Export types: csv, json (comma-separated)"),
    output_dir: str = typer.Option("./output", "--output-dir", "-o",
        help="Directory for exported files"),
    headful: bool = typer.Option(False, "--headful",
        help="Show browser window (default: headless)"),
    debug: bool = typer.Option(False, "--debug",
        help="Show raw tweets before analysis (for debugging)"),
    expand: bool = typer.Option(True, "--expand/--no-expand",
        help="Expand topic to related terms (default: enabled)"),
) -> None:
    """
    Analyze sentiment for a given topic from X.com.
    Uses topic expansion and multi-source scraping for better data coverage.
    """
    try:
        from src.config.settings import load_settings
        settings = load_settings()
    except ValueError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)

    # Topic expansion
    if expand:
        expanded_topics = expand_topic(topic)
        typer.secho(f"Topic: '{topic}'", fg=typer.colors.CYAN)
        typer.secho(f"Expanded to {len(expanded_topics)} related terms:", fg=typer.colors.CYAN)
        typer.echo(f"  {', '.join(expanded_topics[:5])}{'...' if len(expanded_topics) > 5 else ''}")
        typer.echo()
    else:
        expanded_topics = [topic]

    # Setup scraper
    scraper = XScraper(
        username=settings.x_username,
        password=settings.x_password,
        headless=not headful,
        tweet_count=max(50, count // len(expanded_topics)),  # Distribute across topics
        cookies=settings.cookies,
    )

    # Scrape from all topics
    typer.secho(f"Scraping from {len(expanded_topics)} sources...", fg=typer.colors.CYAN)

    seen_ids = set()
    all_tweets = []
    topic_stats = {}

    for i, search_topic in enumerate(expanded_topics, 1):
        remaining = count - len(all_tweets)
        if remaining <= 0:
            break

        scraper.tweet_count = min(50, remaining)

        typer.secho(f"  [{i}/{len(expanded_topics)}] Scraping: '{search_topic}' ...", fg=typer.colors.YELLOW)

        try:
            result = scraper.scrape(search_topic)
            new_tweets = [t for t in result.tweets if t.id not in seen_ids]
            all_tweets.extend(new_tweets)
            seen_ids.update(t.id for t in new_tweets)
            topic_stats[search_topic] = {"new": len(new_tweets), "total": len(result.tweets)}
            typer.secho(f"    -> Got {len(new_tweets)} new tweets (Total: {len(all_tweets)})", fg=typer.colors.GREEN)
        except Exception as e:
            typer.secho(f"    -> Error: {e}", fg=typer.colors.RED)
            topic_stats[search_topic] = {"error": str(e)}

    if not all_tweets:
        typer.secho("No tweets collected!", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)

    typer.secho(f"\nTotal collected: {len(all_tweets)} unique tweets", fg=typer.colors.CYAN)

    # Sentiment analysis
    typer.secho("Running sentiment analysis...", fg=typer.colors.CYAN)

    analyzer = SentimentAnalyzer()
    cleaned_texts = [clean_tweet(t.text) for t in all_tweets]
    sentiment_results = analyzer.analyze_batch(cleaned_texts)

    typer.secho("Analysis complete!", fg=typer.colors.GREEN)

    tweets_data = [
        {"id": t.id, "text": t.text, "username": t.username, "timestamp": t.timestamp}
        for t in all_tweets
    ]

    if debug:
        typer.secho("\n=== RAW TWEETS (DEBUG) ===", fg=typer.colors.YELLOW)
        for i, tweet in enumerate(all_tweets[:20], 1):  # Show first 20 in debug
            result = sentiment_results[i-1]
            # Truncate text safely for Windows console
            try:
                text_preview = tweet.text[:150].encode('utf-8', errors='replace').decode('utf-8', errors='replace')
                cleaned_preview = cleaned_texts[i-1][:100].encode('utf-8', errors='replace').decode('utf-8', errors='replace')
                typer.echo(f"\n{i}. @{tweet.username} ({tweet.timestamp[:10] if tweet.timestamp else 'N/A'}):")
                typer.echo(f"   {text_preview}...")
                typer.echo(f"   Cleaned: {cleaned_preview}...")
                typer.echo(f"   Sentiment: [{result.label.upper()}] conf={result.confidence:.1%}")
            except Exception:
                typer.echo(f"\n{i}. @{tweet.username}: [encoding error - see JSON export]")
        if len(all_tweets) > 20:
            typer.echo(f"\n... and {len(all_tweets) - 20} more tweets")
        typer.echo()

    if format == "dashboard":
        print_dashboard(topic, sentiment_results, tweets_data)
    elif format == "stats":
        typer.echo(format_stats(topic, sentiment_results))
    elif format == "breakdown":
        for line in format_breakdown(sentiment_results):
            typer.echo(line)

    if export:
        exporter = Exporter(output_dir=output_dir)
        for fmt in export.split(","):
            fmt = fmt.strip()
            if fmt == "csv":
                path = exporter.export_csv(topic, sentiment_results, tweets_data)
                typer.secho(f"CSV exported to: {path}", fg=typer.colors.GREEN)
            elif fmt == "json":
                path = exporter.export_json(topic, sentiment_results, tweets_data)
                typer.secho(f"JSON exported to: {path}", fg=typer.colors.GREEN)


@export_app.command()
def export_cmd(
    topic: str = typer.Option(..., "--topic", "-t", help="Topic name"),
    path: str = typer.Option(..., "--path", "-p", help="Path to results JSON"),
    fmt: str = typer.Option("csv", "--format", "-f", help="csv or json"),
) -> None:
    """Re-export results in a different format."""
    import json
    from pathlib import Path

    try:
        with open(path) as f:
            data = json.load(f)
    except Exception as e:
        typer.secho(f"Failed to read file: {e}", fg=typer.colors.RED)
        raise typer.Exit(1)

    typer.echo(f"Results from: {data.get('topic', topic)}")