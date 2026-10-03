"""Реферат в виде списка ключевых слов и иерархии именных групп."""

from __future__ import annotations

from collections import Counter, defaultdict

from src.document import Document
from src.extraction import collection_weights
from src.utils import tokenize_keep


def keyword_unigrams(document: Document, weights: dict[str, float] | None = None, limit: int = 12) -> list[tuple[str, str, float]]:
    """Топ стеммов по w(t, D); возвращает (поверхность, стем, вес)."""
    weights = weights or collection_weights(document)
    surface: dict[str, Counter] = defaultdict(Counter)
    for sentence in document.sentences:
        for form, stem in tokenize_keep(sentence.text, document.language):
            surface[stem][form] += 1
    ranked = sorted(weights.items(), key=lambda item: item[1], reverse=True)
    result = []
    for stem, weight in ranked:
        if stem not in surface:
            continue
        if sum(surface[stem].values()) < 3:
            continue
        form = surface[stem].most_common(1)[0][0]
        result.append((form, stem, weight))
        if len(result) >= limit:
            break
    return result


def _phrases(document: Document, max_n: int = 3) -> Counter:
    counts: Counter = Counter()
    for sentence in document.sentences:
        pairs = tokenize_keep(sentence.text, document.language)
        stems = [stem for _, stem in pairs]
        forms = [form for form, _ in pairs]
        for n in range(2, max_n + 1):
            for index in range(len(stems) - n + 1):
                phrase = " ".join(forms[index:index + n])
                counts[phrase] += 1
    return counts


def hierarchical_keywords(document: Document, weights: dict[str, float] | None = None, limit: int = 8) -> list[dict]:
    """
    Дерево: голова (униграмма) → словосочетания, где она встречается.
    Пример из методички: лазер → лазерный луч, синий лазер.
    """
    weights = weights or collection_weights(document)
    heads = keyword_unigrams(document, weights, limit=limit)
    phrases = _phrases(document)
    tree = []
    used = set()
    for form, stem, weight in heads:
        children = []
        for phrase, freq in phrases.most_common():
            phrase_stems = [stem_token for _, stem_token in tokenize_keep(phrase, document.language)]
            if stem not in phrase_stems:
                continue
            if phrase == form or phrase in used:
                continue
            if freq < 2 and len(phrase.split()) > 2:
                continue
            children.append(phrase)
            used.add(phrase)
            if len(children) >= 4:
                break
        tree.append({"term": form, "stem": stem, "weight": weight, "children": children})
    return tree


def format_keyword_tree(tree: list[dict]) -> str:
    lines = []
    for node in tree:
        lines.append(f"{node['term']}")
        for child in node["children"]:
            lines.append(f"    {child}")
    return "\n".join(lines) if lines else "—"
