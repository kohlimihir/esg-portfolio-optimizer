from __future__ import annotations
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from functools import lru_cache
from .text import chunk
from ..utils.logging import logger

FINBERT = "ProsusAI/finbert"
ESG_BERT = "nbroad/ESG-BERT"


@lru_cache(maxsize=2)
def _load_pipeline(model_name: str):
    logger.info(f"Loading model {model_name}")
    tok = AutoTokenizer.from_pretrained(model_name)
    mdl = AutoModelForSequenceClassification.from_pretrained(model_name)
    device = 0 if torch.cuda.is_available() else -1
    return pipeline("text-classification", model=mdl, tokenizer=tok, device=device, top_k=None)


def finbert_sentiment(texts: list[str]) -> list[dict]:
    """Returns per-text dict of sentiment scores."""
    pipe = _load_pipeline(FINBERT)
    outputs = pipe(texts, truncation=True, max_length=512)
    result = []
    for scores in outputs:
        d = {s["label"].lower(): s["score"] for s in scores}
        result.append(d)
    return result


def esg_classify(text: str, max_chunks: int = 10) -> dict[str, float]:
    """Classify text chunks across ESG categories and return mean scores."""
    pipe = _load_pipeline(ESG_BERT)
    chunks = chunk(text, size=300, overlap=30)[:max_chunks]
    if not chunks:
        return {}
    outputs = pipe(chunks, truncation=True, max_length=512)
    agg: dict[str, list[float]] = {}
    for scores in outputs:
        for s in scores:
            agg.setdefault(s["label"], []).append(s["score"])
    return {k: float(sum(v) / len(v)) for k, v in agg.items()}
