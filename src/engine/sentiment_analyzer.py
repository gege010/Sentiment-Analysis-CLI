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
    Sentiment analyzer using IndoBERT (w11wo/indonesian-roberta-base-sentiment-classifier).
    Natively supports Indonesian text and slang.
    """

    MODEL_NAME = "w11wo/indonesian-roberta-base-sentiment-classifier"

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

        # Get model prediction
        pipe = self._init_pipe()
        model_result = pipe(text)[0]

        final_label = model_result["label"].lower()
        final_score = model_result["score"]

        return SentimentResult(
            label=final_label,
            confidence=final_score,
            text=text,
        )

    def analyze_batch(self, texts: List[str]) -> List[SentimentResult]:
        return [self.analyze(t) for t in texts]