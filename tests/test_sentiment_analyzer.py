"""Test suite for src/engine/sentiment_analyzer.py"""
import pytest
from unittest.mock import MagicMock
from src.engine.sentiment_analyzer import SentimentAnalyzer, SentimentResult


def _mock_sentiment_pipe(label: str, score: float) -> MagicMock:
    """Return a MagicMock that is callable and returns the expected list."""
    mock = MagicMock()
    mock.return_value = [{"label": label, "score": score}]
    return mock


def test_analyzer_returns_result():
    analyzer = SentimentAnalyzer()
    analyzer._pipe = _mock_sentiment_pipe("positive", 0.92)
    result = analyzer.analyze("This is great!")
    assert isinstance(result, SentimentResult)
    assert result.label == "positive"
    assert result.confidence == 0.92


def test_analyzer_has_confidence():
    analyzer = SentimentAnalyzer()
    analyzer._pipe = _mock_sentiment_pipe("positive", 0.95)
    result = analyzer.analyze("I love this")
    assert 0.0 <= result.confidence <= 1.0
    assert result.confidence == 0.95


def test_analyze_batch_returns_all():
    analyzer = SentimentAnalyzer()
    analyzer._pipe = _mock_sentiment_pipe("positive", 0.9)
    results = analyzer.analyze_batch(["Good!", "Nice.", "Bad?"])
    assert len(results) == 3


def test_analyze_batch_empty():
    analyzer = SentimentAnalyzer()
    results = analyzer.analyze_batch([])
    assert results == []


def test_analyze_empty_text():
    analyzer = SentimentAnalyzer()
    result = analyzer.analyze("")
    assert result.label == "neutral"
    assert result.confidence == 0.0


def test_analyze_whitespace_text():
    analyzer = SentimentAnalyzer()
    result = analyzer.analyze("   ")
    assert result.label == "neutral"
    assert result.confidence == 0.0


def test_sentiment_result_dataclass():
    analyzer = SentimentAnalyzer()
    analyzer._pipe = _mock_sentiment_pipe("negative", 0.88)
    result = analyzer.analyze("This is bad")
    assert result.text == "This is bad"
    assert result.label == "negative"


def test_sentiment_label_normalization():
    analyzer = SentimentAnalyzer()
    analyzer._pipe = _mock_sentiment_pipe("NEUTRAL", 0.7)
    result = analyzer.analyze("Okay")
    assert result.label == "neutral"