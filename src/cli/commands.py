import typer
from typing import Optional
from src.config.settings import load_settings
from src.engine.sentiment_analyzer import SentimentAnalyzer
from src.engine.preprocessor import clean_tweet
from src.crawler.x_scraper import XScraper, XScrapeError
from src.cli.dashboard import print_dashboard
from src.cli.formatters import format_stats, format_breakdown
from src.output.exporter import Exporter


analyze_app = typer.Typer(help="Analyze sentiment for a topic on X.com")
export_app = typer.Typer(help="Export previously saved results")


@analyze_app.command("analyze")
def analyze(
    topic: str = typer.Option(..., "--topic", "-t", help="Topic to analyze"),
    count: int = typer.Option(200, "--count", "-c", help="Number of tweets to scrape"),
    format: str = typer.Option("dashboard", "--format", "-f",
        help="Output format: dashboard, stats, breakdown"),
    export: str = typer.Option("", "--export", "-e",
        help="Export types: csv, json (comma-separated)"),
    output_dir: str = typer.Option("./output", "--output-dir", "-o",
        help="Directory for exported files"),
    headful: bool = typer.Option(False, "--headful", help="Show browser window (default: headless)"),
) -> None:
    """
    Analyze sentiment for a given topic from X.com.
    """
    try:
        settings = load_settings()
    except ValueError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)

    typer.secho(f"Scraping X.com for topic: '{topic}' ...", fg=typer.colors.CYAN)

    try:
        scraper = XScraper(
            username=settings.x_username,
            password=settings.x_password,
            headless=not headful,
            tweet_count=count,
        )
        scrape_result = scraper.scrape(topic)
    except XScrapeError as e:
        typer.secho(f"Scraping failed: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)

    typer.secho(f"Collected {len(scrape_result.tweets)} tweets. Running sentiment analysis...", fg=typer.colors.CYAN)

    analyzer = SentimentAnalyzer()

    cleaned_texts = [clean_tweet(t.text) for t in scrape_result.tweets]
    sentiment_results = analyzer.analyze_batch(cleaned_texts)

    typer.secho("Analysis complete!", fg=typer.colors.GREEN)

    tweets_data = [
        {"id": t.id, "text": t.text, "username": t.username, "timestamp": t.timestamp}
        for t in scrape_result.tweets
    ]

    if format == "dashboard":
        print_dashboard(topic, sentiment_results, tweets_data)
    elif format == "stats":
        typer.echo(format_stats(topic, sentiment_results))
    elif format == "breakdown":
        lines = format_breakdown(sentiment_results)
        for line in lines:
            typer.echo(line)

    # Export if requested
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


@export_app.command("export")
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

    exporter = Exporter(output_dir=str(Path(path).parent))

    typer.echo(f"Results from: {data.get('topic', topic)}")