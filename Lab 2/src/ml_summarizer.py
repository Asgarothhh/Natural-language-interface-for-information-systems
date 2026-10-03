"""Реферат методом машинного обучения: TextRank на графе близости предложений."""

from __future__ import annotations

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.document import Document, Sentence
from src.extraction import is_summary_candidate
from src.utils import stopwords_for, transform_sentence


def _sentence_texts(document: Document) -> list[str]:
    return [item.text for item in document.sentences]


def textrank_scores(document: Document, damping: float = 0.85, iterations: int = 40) -> np.ndarray:
    """
    Графовый алгоритм Mihalcea & Tarau (TextRank):
    вершины — предложения, ребро — косинус TF–IDF, ранг — PageRank.
    """
    texts = _sentence_texts(document)
    n_sent = len(texts)
    if n_sent == 0:
        return np.array([])
    if n_sent == 1:
        return np.array([1.0])

    stops = list(stopwords_for(document.language))
    vectorizer = TfidfVectorizer(
        lowercase=True,
        stop_words=stops,
        token_pattern=r"[A-Za-zÀ-ÖØ-öø-ÿŒœÆæ]{3,}",
        min_df=1,
    )
    try:
        matrix = vectorizer.fit_transform(texts)
    except ValueError:
        return np.ones(n_sent) / n_sent

    similarity = cosine_similarity(matrix)
    np.fill_diagonal(similarity, 0.0)
    row_sum = similarity.sum(axis=1, keepdims=True)
    row_sum[row_sum == 0] = 1.0
    transition = similarity / row_sum

    scores = np.full(n_sent, 1.0 / n_sent)
    teleport = (1.0 - damping) / n_sent
    for _ in range(iterations):
        scores = teleport + damping * transition.T.dot(scores)
    return scores


def ml_extract(document: Document, count: int = 10) -> list[Sentence]:
    scores = textrank_scores(document)
    for sentence, score in zip(document.sentences, scores):
        sentence.ml_score = float(score)
    if not document.sentences:
        return []
    ranked = sorted(document.sentences, key=lambda item: item.ml_score, reverse=True)
    chosen: set[int] = set()
    for sentence in ranked:
        if not is_summary_candidate(sentence):
            continue
        chosen.add(sentence.index)
        if len(chosen) >= count:
            break
    if len(chosen) < min(count, len(document.sentences)):
        for sentence in ranked:
            chosen.add(sentence.index)
            if len(chosen) >= count:
                break
    return [item for item in document.sentences if item.index in chosen]


def ml_summary(document: Document, count: int = 10) -> list[str]:
    return [transform_sentence(item.text) for item in ml_extract(document, count)]
