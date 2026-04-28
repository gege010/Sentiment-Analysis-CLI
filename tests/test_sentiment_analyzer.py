"""Test suite for src/engine/sentiment_analyzer.py"""
import pytest
from unittest.mock import patch, MagicMock
from src.engine.sentiment_analyzer import SentimentAnalyzer, SentimentResult


@pytest.fixture
def mock_pipe():
    with patch("transformers.pipeline") as mock:
        yield mock


def test_analyzer_returns_result(mock_pipe):
    mock_pipe.return_value = [{"label": "positive", "score": 0.92}]
    analyzer = SentimentAnalyzer()
    result = analyzer.analyze("This is great!")
    assert isinstance(result, SentimentResult)
    assert result.label == "positive"


def test_analyzer_has_confidence(mock_pipe):
    mock_pipe.return_value = [{"label": "positive", "score": 0.95}]
    analyzer = SentimentAnalyzer()
    result = analyzer.analyze("I love this")
    assert 0.0 <= result.confidence <= 1.0
    assert result.confidence == 0.95


def test_analyze_batch_returns_all(mock_pipe):
    mock_pipe.return_value = [{"label": "positive", "score": 0.9}]
    analyzer = SentimentAnalyzer()
    results = analyzer.analyze_batch(["Good!", "Nice.", "Bad?"])
    assert len(results) == 3


def test_analyze_batch_empty(mock_pipe):
    analyzer = SentimentAnalyzer()
    results = analyzer.analyze_batch([])
    assert results == []


def test_analyze_empty_text(mock_pipe):
    analyzer = SentimentAnalyzer()
    result = analyzer.analyze("")
    assert result.label == "neutral"
    assert result.confidence == 0.0


def test_analyze_whitespace_text(mock_pipe):
    analyzer = SentimentAnalyzer()
    result = analyzer.analyze("   ")
    assert result.label == "neutral"
    assert result.confidence == 0.0


def test_sentiment_result_dataclass(mock_pipe):
    mock_pipe.return_value = [{"label": "negative", "score": 0.88}]
    analyzer = SentimentAnalyzer()
    result = analyzer.analyze("This is bad")
    assert result.text == "This is bad"
    assert result.label == "negative"


def test_sentiment_label_normalization(mock_pipe):
    mock_pipe.return_value = [{"label": "NEUTRAL", "score": 0.7}]
    analyzer = SentimentAnalyzer()
    result = analyzer.analyze("Okay")
    assert result.label == "neutral"
