"""Классический реферат методом sentence extraction по формулам методички."""

from __future__ import annotations

import math
from collections import Counter

from src.document import TERM_DOC_COUNT, Document, Sentence
from src.utils import transform_sentence


def word_weight(tf_in_doc: int, tf_max: int, df: int, n_docs: int) -> float:
    """
    Модифицированная схема Salton:

        w(t, D) = 0.5 * (1 + tf(t, D) / tf_max(D)) * log(|DB| / df(t))
    """
    if tf_max <= 0 or df <= 0 or n_docs <= 0:
        return 0.0
    return 0.5 * (1.0 + tf_in_doc / tf_max) * math.log(n_docs / df)


def collection_weights(document: Document) -> dict[str, float]:
    n_docs = Document.collection_size()
    tf_max = document.max_tf
    return {
        term: word_weight(tf, tf_max, TERM_DOC_COUNT.get(term, 1), n_docs)
        for term, tf in document.term_frequencies.items()
    }


def position_scores(sentence: Sentence, doc_length: int) -> tuple[float, float]:
    """
    Posd(Si) = 1 - BD(Si) / |D|
    Posp(Si) = 1 - BP(Si) / |P|
    """
    posd = 1.0 - (sentence.start_char / doc_length) if doc_length else 1.0
    bp = max(sentence.start_char - sentence.paragraph_start, 0)
    posp = 1.0 - (bp / sentence.paragraph_length) if sentence.paragraph_length else 1.0
    return max(posd, 0.0), max(posp, 0.0)


def tfidf_sentence_score(sentence: Sentence, weights: dict[str, float]) -> float:
    """Score(Si) = Σ_t tf(t, Si) · w(t, D)."""
    tf = Counter(sentence.tokens)
    return sum(count * weights.get(term, 0.0) for term, count in tf.items())


def score_document(document: Document) -> dict[str, float]:
    weights = collection_weights(document)
    for sentence in document.sentences:
        sentence.posd, sentence.posp = position_scores(sentence, document.char_length)
        sentence.tfidf_score = tfidf_sentence_score(sentence, weights)
        sentence.weight = sentence.posd * sentence.posp * sentence.tfidf_score
    return weights


def is_summary_candidate(sentence: Sentence) -> bool:
    text = sentence.text.strip()
    if len(text) < 50 or len(text) > 650:
        return False
    if len(sentence.tokens) < 6:
        return False
    if text.count("\n") > 2:
        return False
    return True


def extract_sentences(document: Document, count: int = 10) -> list[Sentence]:
    """Выбрать `count` предложений с наибольшим весом в порядке текста."""
    if not document.sentences:
        return []
    ranked = sorted(document.sentences, key=lambda item: item.weight, reverse=True)
    chosen = set()
    for sentence in ranked:
        if len(chosen) >= count:
            break
        if not is_summary_candidate(sentence):
            continue
        chosen.add(sentence.index)
    if len(chosen) < min(count, len(document.sentences)):
        for sentence in ranked:
            if is_summary_candidate(sentence) or len(sentence.tokens) >= 4:
                chosen.add(sentence.index)
            if len(chosen) >= count:
                break
    selected = [item for item in document.sentences if item.index in chosen]
    return selected[:count]


def classic_summary(document: Document, count: int = 10) -> list[str]:
    score_document(document)
    return [transform_sentence(item.text) for item in extract_sentences(document, count)]
