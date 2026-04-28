from typing import List
from src.engine.sentiment_analyzer import SentimentResult


def format_stats(topic: str, results: List[SentimentResult]) -> str:
    """
    Return a formatted stats block (plain text, no Rich).
    """
    if not results:
        return f"No results found for topic: {topic}"

    counts = {"positive": 0, "neutral": 0, "negative": 0}
    for r in results:
        counts[r.label] = counts.get(r.label, 0) + 1

    total = len(results)
    avg_conf = sum(r.confidence for r in results) / total

    lines = [
        f"Topic: {topic}",
        f"Total Tweets: {total}",
        f"Avg Confidence: {avg_conf:.1%}",
        "",
        "Sentiment Distribution:",
        f"  Positive: {counts['positive']} ({counts['positive']/total:.1%})",
        f"  Neutral:  {counts['neutral']} ({counts['neutral']/total:.1%})",
        f"  Negative: {counts['negative']} ({counts['negative']/total:.1%})",
    ]
    return "\n".join(lines)


def format_breakdown(results: List[SentimentResult], limit: int = 20) -> List[str]:
    """
    Return per-tweet breakdown as list of formatted strings.
    """
    lines = []
    for i, r in enumerate(results[:limit], 1):
        emoji = {"positive": "✅", "neutral": "😐", "negative": "❌"}.get(r.label, "•")
        label = r.label.upper()
        conf = f"{r.confidence:.0%}"
        preview = r.text[:80] + ("..." if len(r.text) > 80 else "")
        lines.append(f"{i:3}. {emoji} [{label}] (conf:{conf}) {preview}")

    if len(results) > limit:
        lines.append(f"... and {len(results) - limit} more tweets.")

    return lines


def format_bar(count: int, total: int, width: int = 20) -> str:
    """Return a simple ASCII bar."""
    if total == 0:
        return "░" * width
    filled = int(count / total * width)
    return "█" * filled + "░" * (width - filled)