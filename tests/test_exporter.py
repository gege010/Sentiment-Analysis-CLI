"""Test suite for src/output/exporter.py"""
import csv
import json
import os
import tempfile
from src.engine.sentiment_analyzer import SentimentResult
from src.output.exporter import Exporter


def test_export_csv_creates_file():
    with tempfile.TemporaryDirectory() as tmp:
        results = [
            SentimentResult(label="positive", confidence=0.9, text="Great!"),
            SentimentResult(label="negative", confidence=0.8, text="Terrible."),
        ]
        tweets_data = [
            {"id": "1", "text": "Great!", "username": "@u", "timestamp": "2026-04-28", "likes": 0, "retweets": 0},
            {"id": "2", "text": "Terrible.", "username": "@v", "timestamp": "2026-04-28", "likes": 0, "retweets": 0},
        ]
        exporter = Exporter(output_dir=tmp)
        path = exporter.export_csv("AI", results, tweets_data)
        assert os.path.exists(path)
        with open(path) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        assert len(rows) == 2
        assert rows[0]["sentiment"] == "positive"
        assert rows[1]["sentiment"] == "negative"


def test_export_json_creates_file():
    with tempfile.TemporaryDirectory() as tmp:
        results = [
            SentimentResult(label="neutral", confidence=0.7, text="Okay"),
        ]
        tweets_data = [
            {"id": "3", "text": "Okay", "username": "@w", "timestamp": "2026-04-28", "likes": 5, "retweets": 2},
        ]
        exporter = Exporter(output_dir=tmp)
        path = exporter.export_json("ML", results, tweets_data)
        assert os.path.exists(path)
        with open(path) as f:
            data = json.load(f)
        assert data["topic"] == "ML"
        assert data["total_tweets"] == 1
        assert data["summary"]["neutral"]["count"] == 1


def test_export_json_includes_summary():
    with tempfile.TemporaryDirectory() as tmp:
        results = [
            SentimentResult(label="positive", confidence=0.9, text="Good"),
            SentimentResult(label="positive", confidence=0.8, text="Nice"),
        ]
        tweets_data = [{"id": "1", "text": "Good", "username": "@a", "timestamp": "", "likes": 0, "retweets": 0},
                      {"id": "2", "text": "Nice", "username": "@b", "timestamp": "", "likes": 0, "retweets": 0}]
        exporter = Exporter(output_dir=tmp)
        path = exporter.export_json("Test", results, tweets_data)
        with open(path) as f:
            data = json.load(f)
        assert data["summary"]["positive"]["count"] == 2
        assert data["summary"]["negative"]["count"] == 0


def test_exporter_creates_output_dir():
    with tempfile.TemporaryDirectory() as tmp:
        exporter = Exporter(output_dir=os.path.join(tmp, "new_dir"))
        assert os.path.exists(exporter.output_dir)


def test_export_csv_filename_contains_topic():
    with tempfile.TemporaryDirectory() as tmp:
        exporter = Exporter(output_dir=tmp)
        results = [SentimentResult(label="positive", confidence=0.9, text="Hi")]
        tweets_data = [{"id": "1", "text": "Hi", "username": "@u", "timestamp": "", "likes": 0, "retweets": 0}]
        path = exporter.export_csv("AI_Tech", results, tweets_data)
        assert "AI_Tech" in path
