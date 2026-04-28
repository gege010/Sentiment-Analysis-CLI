import csv
import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from src.engine.sentiment_analyzer import SentimentResult


class Exporter:
    """Export sentiment analysis results to CSV and JSON."""

    def __init__(self, output_dir: str = "./output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _timestamp(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def _filename(self, topic: str, ext: str) -> str:
        safe = topic.replace(" ", "_")[:50]
        return f"sentiment_report_{safe}_{self._timestamp()}.{ext}"

    def _summarize(self, results: List[SentimentResult]) -> Dict[str, Dict[str, Any]]:
        counts = {"positive": 0, "neutral": 0, "negative": 0}
        for r in results:
            counts[r.label] = counts.get(r.label, 0) + 1
        total = len(results) or 1
        return {
            label: {
                "count": count,
                "percent": round(count / total * 100, 1),
            }
            for label, count in counts.items()
        }

    def export_csv(
        self,
        topic: str,
        results: List[SentimentResult],
        tweets_data: List[Dict[str, Any]],
    ) -> str:
        filepath = self.output_dir / self._filename(topic, "csv")

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "id", "tweet_text", "sentiment", "confidence",
                "timestamp", "username", "likes", "retweets"
            ])
            for i, (r, td) in enumerate(zip(results, tweets_data)):
                writer.writerow([
                    td.get("id", str(i)),
                    r.text,
                    r.label,
                    f"{r.confidence:.3f}",
                    td.get("timestamp", ""),
                    td.get("username", ""),
                    td.get("likes", 0),
                    td.get("retweets", 0),
                ])

        return str(filepath)

    def export_json(
        self,
        topic: str,
        results: List[SentimentResult],
        tweets_data: List[Dict[str, Any]],
    ) -> str:
        filepath = self.output_dir / self._filename(topic, "json")
        total = len(results) or 1
        avg_conf = round(sum(r.confidence for r in results) / total, 3)
        summary = self._summarize(results)

        data = {
            "topic": topic,
            "timestamp": datetime.now().isoformat(),
            "total_tweets": total,
            "avg_confidence": avg_conf,
            "summary": summary,
            "tweets": [
                {
                    "id": td.get("id", ""),
                    "text": r.text,
                    "sentiment": r.label,
                    "confidence": round(r.confidence, 3),
                    "timestamp": td.get("timestamp", ""),
                    "username": td.get("username", ""),
                    "likes": td.get("likes", 0),
                    "retweets": td.get("retweets", 0),
                }
                for r, td in zip(results, tweets_data)
            ],
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return str(filepath)