"""Integration tests for full sentiment analysis flow."""
import pytest
from unittest.mock import patch, MagicMock
from src.crawler.x_scraper import XScraper, Tweet, ScrapeResult
from src.engine.sentiment_analyzer import SentimentAnalyzer, SentimentResult
from src.engine.preprocessor import clean_tweet
from src.cli.formatters import format_stats


def test_preprocess_then_analyze_mocked():
    """Full flow: preprocess → mock sentiment → format stats."""
    text = "@user Check https://t.co/abc this is great!"
    cleaned = clean_tweet(text)
    assert "http" not in cleaned
    assert "@" not in cleaned

    mock_pipe_instance = MagicMock(return_value=[{"label": "positive", "score": 0.92}])

    analyzer = SentimentAnalyzer()
    analyzer._pipe = mock_pipe_instance
    result = analyzer.analyze(cleaned)
    assert result.label == "positive"
    assert result.confidence > 0.9

    stats = format_stats("AI", [result])
    assert "AI" in stats
    assert "positive" in stats.lower()


def test_full_flow_batch_mocked():
    """Batch full flow with mocked model."""
    texts = [
        "@alice https://x.com this is amazing!",
        "@bob terrible experience",
        "just a normal day",
    ]

    def pipe_side_effect(text):
        if "amazing" in text:
            return [{"label": "positive", "score": 0.93}]
        elif "terrible" in text:
            return [{"label": "negative", "score": 0.87}]
        else:
            return [{"label": "neutral", "score": 0.72}]

    mock_pipe_instance = MagicMock(side_effect=pipe_side_effect)

    analyzer = SentimentAnalyzer()
    analyzer._pipe = mock_pipe_instance
    results = analyzer.analyze_batch([clean_tweet(t) for t in texts])
    assert len(results) == 3
    labels = {r.label for r in results}
    assert "positive" in labels
    assert "negative" in labels
    assert "neutral" in labels


def test_scrape_result_dataclass():
    """Test ScrapeResult structure."""
    tweets = [
        Tweet(id="1", text="Hello", username="@user", timestamp="2026-04-28"),
        Tweet(id="2", text="World", username="@other", timestamp="2026-04-28"),
    ]
    result = ScrapeResult(tweets=tweets, topic="test", total=2)
    assert result.total == 2
    assert len(result.tweets) == 2
    assert result.topic == "test"


def test_full_stats_aggregation():
    """Test that format_stats aggregates all sentiments."""
    results = [
        SentimentResult(label="positive", confidence=0.9, text=f"Tweet {i}")
        for i in range(5)
    ] + [
        SentimentResult(label="negative", confidence=0.8, text="Bad")
        for i in range(3)
    ]
    stats = format_stats("Tech", results)
    assert "Tech" in stats
    assert "5" in stats or "5" in stats.split("Positive")[0]
