"""Метрики качества рефератов: ROUGE-N, overlap предложений, покрытие терминов."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from src.document import Document
from src.utils import tokenize


def _ngrams(tokens: Sequence[str], n: int) -> list[tuple[str, ...]]:
    if n <= 0 or len(tokens) < n:
        return []
    return [tuple(tokens[i:i + n]) for i in range(len(tokens) - n + 1)]


def rouge_n(hypothesis: str, reference: str, lang: str, n: int = 1) -> float:
    """F1 по n-граммам (ROUGE-N)."""
    hyp = _ngrams(tokenize(hypothesis, lang), n)
    ref = _ngrams(tokenize(reference, lang), n)
    if not hyp or not ref:
        return 0.0
    ref_counts: dict[tuple[str, ...], int] = {}
    for gram in ref:
        ref_counts[gram] = ref_counts.get(gram, 0) + 1
    overlap = 0
    for gram in hyp:
        if ref_counts.get(gram, 0) > 0:
            overlap += 1
            ref_counts[gram] -= 1
    precision = overlap / len(hyp)
    recall = overlap / len(ref)
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def jaccard(left: Iterable[int], right: Iterable[int]) -> float:
    a, b = set(left), set(right)
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def keyword_coverage(summary: str, keywords: Sequence[str], lang: str) -> float:
    if not keywords:
        return 0.0
    tokens = set(tokenize(summary, lang))
    hits = 0
    for word in keywords:
        stems = tokenize(word, lang)
        if stems and set(stems) <= tokens:
            hits += 1
    return hits / len(keywords)


@dataclass
class DocScores:
    document_id: int
    title: str
    language: str
    domain: str
    n_sentences: int
    se_rouge1: float
    se_rouge2: float
    ml_rouge1: float
    ml_rouge2: float
    lead_rouge1: float
    overlap: float
    se_coverage: float
    ml_coverage: float
    se_seconds: float
    ml_seconds: float


def lead_sentences(document: Document, count: int = 10) -> list[str]:
    return [item.text for item in document.sentences[:count]]
