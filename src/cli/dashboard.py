from typing import List, Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from src.engine.sentiment_analyzer import SentimentResult
from src.cli.formatters import format_bar


console = Console()


def print_dashboard(
    topic: str,
    results: List[SentimentResult],
    tweets_data: List[Dict[str, Any]],
) -> None:
    """
    Render an interactive-style Rich dashboard to the terminal.
    """
    if not results:
        console.print("[yellow]No results found for this topic.[/yellow]")
        return

    counts = {"positive": 0, "neutral": 0, "negative": 0}
    for r in results:
        counts[r.label] = counts.get(r.label, 0) + 1

    total = len(results)
    avg_conf = sum(r.confidence for r in results) / total

    # Build overview table
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Metric", style="bold cyan")
    table.add_column("Value", style="white")
    table.add_row("Topic", topic)
    table.add_row("Total Tweets", str(total))
    table.add_row("Avg Confidence", f"{avg_conf:.1%}")
    table.add_row("Positive", f"{counts['positive']} ({counts['positive']/total:.1%})")
    table.add_row("Neutral", f"{counts['neutral']} ({counts['neutral']/total:.1%})")
    table.add_row("Negative", f"{counts['negative']} ({counts['negative']/total:.1%})")

    # Sentiment bar chart
    pos_bar = format_bar(counts["positive"], total, 20)
    neu_bar = format_bar(counts["neutral"], total, 20)
    neg_bar = format_bar(counts["negative"], total, 20)

    pos_pct = f"{counts['positive']/total:.1%}"
    neu_pct = f"{counts['neutral']/total:.1%}"
    neg_pct = f"{counts['negative']/total:.1%}"

    # Find top positive and negative tweets
    positive_tweets = [
        (r, td) for r, td in zip(results, tweets_data) if r.label == "positive"
    ]
    negative_tweets = [
        (r, td) for r, td in zip(results, tweets_data) if r.label == "negative"
    ]

    top_pos = positive_tweets[0] if positive_tweets else (None, None)
    top_neg = negative_tweets[0] if negative_tweets else (None, None)

    top_pos_text = top_pos[0].text[:100] if top_pos[0] else "N/A"
    top_neg_text = top_neg[0].text[:100] if top_neg[0] else "N/A"

    highlights = (
        f"[green]+ Top Positive:[/green] {top_pos_text}\n"
        f"[red]- Top Negative:[/red] {top_neg_text}"
    )

    console.print()
    console.print(
        Panel(
            table,
            title=f"[bold][CHART] Sentiment Analysis: {topic}[/bold]",
            border_style="cyan",
        )
    )
    console.print()
    console.print(
        f"  [green]+ Positive[/green]  {pos_bar}  "
        f"{counts['positive']:>4} ({pos_pct})"
    )
    console.print(
        f"  [yellow]= Neutral [/yellow]  {neu_bar}  "
        f"{counts['neutral']:>4} ({neu_pct})"
    )
    console.print(
        f"  [red]- Negative[/red]  {neg_bar}  "
        f"{counts['negative']:>4} ({neg_pct})"
    )
    console.print()
    console.print(
        Panel(
            highlights,
            title="[bold]Highlights[/bold]",
            border_style="blue",
        )
    )
    console.print()