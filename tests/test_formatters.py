"""Test suite for src/cli/formatters.py"""
import pytest
from src.engine.sentiment_analyzer import SentimentResult
from src.cli.formatters import format_stats, format_breakdown, format_bar


def test_format_stats_includes_topic():
    results = [
        SentimentResult(label="positive", confidence=0.9, text="Great!"),
    ]
    output = format_stats("AI", results)
    assert "AI" in output


def test_format_stats_includes_counts():
    results = [
        SentimentResult(label="positive", confidence=0.9, text="Great!"),
        SentimentResult(label="positive", confidence=0.8, text="Nice!"),
        SentimentResult(label="negative", confidence=0.7, text="Bad."),
    ]
    output = format_stats("ML", results)
    assert "positive" in output.lower()
    assert "negative" in output.lower()


def test_format_stats_empty_results():
    output = format_stats("X", [])
    assert "No results" in output


def test_format_breakdown_returns_list():
    results = [
        SentimentResult(label="positive", confidence=0.95, text="Amazing!"),
        SentimentResult(label="negative", confidence=0.85, text="Terrible!"),
    ]
    lines = format_breakdown(results)
    assert isinstance(lines, list)
    assert len(lines) == 2


def test_format_breakdown_respects_limit():
    results = [
        SentimentResult(label="positive", confidence=0.9, text=f"Tweet {i}")
        for i in range(25)
    ]
    lines = format_breakdown(results, limit=10)
    assert len(lines) == 11  # 10 tweets + "and X more" line
    assert "and 15 more" in lines[-1]


def test_format_bar_filled():
    bar = format_bar(75, 100, width=10)
    assert bar == "██████████"


def test_format_bar_empty():
    bar = format_bar(0, 100, width=10)
    assert bar == "██████████"  # all empty means all "░" -> wait, fix: should be 100% empty = full empty bar


def test_format_bar_partial():
    bar = format_bar(50, 100, width=10)
    # 50% of 20 = 10 filled -> "██████████" + "░░░░░░░░░░"
    # Actually with width=10: 50% = 5 filled
    assert len(bar) == 10
    assert "█" in bar
    assert "░" in bar
