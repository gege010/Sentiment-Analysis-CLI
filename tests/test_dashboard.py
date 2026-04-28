"""Test suite for src/cli/dashboard.py"""
import pytest
from src.engine.sentiment_analyzer import SentimentResult
from src.cli.dashboard import print_dashboard


def test_print_dashboard_runs_without_error(capsys):
    results = [
        SentimentResult(label="positive", confidence=0.9, text="Great!"),
        SentimentResult(label="negative", confidence=0.8, text="Bad."),
    ]
    tweets_data = [
        {"id": "1", "text": "Great!", "username": "@u", "timestamp": ""},
        {"id": "2", "text": "Bad.", "username": "@v", "timestamp": ""},
    ]
    print_dashboard("AI", results, tweets_data)


def test_print_dashboard_empty_results(capsys):
    print_dashboard("Empty", [], [])
    captured = capsys.readouterr()
    assert "No results" in captured.out or "no results" in captured.out.lower()
