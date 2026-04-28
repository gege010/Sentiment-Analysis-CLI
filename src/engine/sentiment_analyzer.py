from dataclasses import dataclass
from typing import List
from transformers import pipeline


@dataclass
class SentimentResult:
    label: str  # "positive" | "neutral" | "negative"
    confidence: float  # 0.0 to 1.0
    text: str  # original text


class SentimentAnalyzer:
    """
    Sentiment analyzer using cardiffnlp/twitter-roberta-base-sentiment-latest.
    Loads model lazily on first use.
    """

    MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"
    LABEL_MAP = {
        "negative": "negative",
        "neutral": "neutral",
        "positive": "positive",
    }

    def __init__(self):
        self._pipe = None

    def _init_pipe(self):
        """Lazily initialize the pipeline. Called on first analyze()."""
        if self._pipe is None:
            self._pipe = pipeline(
                "sentiment-analysis",
                model=self.MODEL_NAME,
                tokenizer=self.MODEL_NAME,
                device=-1,  # CPU; use device=0 for GPU
                truncation=True,
                max_length=512,
            )
        return self._pipe

    def analyze(self, text: str) -> SentimentResult:
        if not text or not text.strip():
            return SentimentResult(label="neutral", confidence=0.0, text=text)

        pipe = self._init_pipe()
        raw = pipe(text)[0]
        label = raw["label"].lower()
        # Map model's 3-label output (already matches our labels)
        mapped = self.LABEL_MAP.get(label, label)
        return SentimentResult(
            label=mapped,
            confidence=raw["score"],
            text=text,
        )

    def analyze_batch(self, texts: List[str]) -> List[SentimentResult]:
        return [self.analyze(t) for t in texts]