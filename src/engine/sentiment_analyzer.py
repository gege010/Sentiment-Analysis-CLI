from dataclasses import dataclass
from typing import List
from transformers import pipeline
from src.engine.indonesian_lexicon import POSITIVE_WORDS, NEGATIVE_WORDS


@dataclass
class SentimentResult:
    label: str  # "positive" | "neutral" | "negative"
    confidence: float  # 0.0 to 1.0
    text: str  # original text
    lexicon_boost: float = 0.0  # Boost from local lexicon


class SentimentAnalyzer:
    """
    Sentiment analyzer using cardiffnlp/twitter-roberta-base-sentiment-latest.
    Enhanced with Indonesian slang lexicon for better accuracy.
    """

    MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"

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

    def _check_lexicon(self, text: str) -> tuple:
        """
        Check text against Indonesian lexicon.
        Returns: (sentiment_label, boost_strength)
        """
        text_lower = text.lower()

        pos_count = sum(1 for word in POSITIVE_WORDS if word in text_lower)
        neg_count = sum(1 for word in NEGATIVE_WORDS if word in text_lower)

        if pos_count > neg_count:
            return "positive", min(pos_count - neg_count, 3) * 0.1
        elif neg_count > pos_count:
            return "negative", min(neg_count - pos_count, 3) * 0.1

        return "neutral", 0.0

    def _boost_confidence(self, model_result: dict, label: str, boost: float) -> dict:
        """
        Boost confidence based on lexicon match.
        If lexicon agrees with model, increase confidence.
        If lexicon disagrees with model, decrease confidence.
        """
        model_label = model_result["label"].lower()
        base_score = model_result["score"]

        if label == model_label:
            # Agreement - boost confidence
            new_score = min(base_score + boost, 0.99)
        elif label != "neutral" and model_label != "neutral":
            # Disagreement between model and lexicon
            # Model likely more accurate, but reduce confidence slightly
            new_score = base_score * (1 - boost * 0.5)
        else:
            new_score = base_score

        return {
            "label": label,
            "score": new_score,
        }

    def analyze(self, text: str) -> SentimentResult:
        if not text or not text.strip():
            return SentimentResult(label="neutral", confidence=0.0, text=text)

        # 1. Check lexicon first
        lexicon_label, lexicon_boost = self._check_lexicon(text)

        # 2. Get model prediction
        pipe = self._init_pipe()
        model_result = pipe(text)[0]

        # 3. Boost/adjust based on lexicon
        if lexicon_boost > 0:
            adjusted = self._boost_confidence(model_result, lexicon_label, lexicon_boost)
            final_label = adjusted["label"].lower()
            final_score = adjusted["score"]
        else:
            final_label = model_result["label"].lower()
            final_score = model_result["score"]

        return SentimentResult(
            label=final_label,
            confidence=final_score,
            text=text,
            lexicon_boost=lexicon_boost,
        )

    def analyze_batch(self, texts: List[str]) -> List[SentimentResult]:
        return [self.analyze(t) for t in texts]