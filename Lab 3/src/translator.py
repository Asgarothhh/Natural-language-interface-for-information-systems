"""Прямой (пословно-оборотный) перевод с лёгким трансфером."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from src.dictionary import Dictionary
from src.utils import is_word, pos_tag, split_sentences, tag_explanation, tokenize


ARTICLES = {"a", "an", "the"}


@dataclass
class Alignment:
    source: str
    target: str
    pos: str
    found: bool


@dataclass
class TranslationResult:
    source_text: str
    translation: str
    sentences: list[str]
    translated_sentences: list[str]
    alignments: list[Alignment]
    input_words: int
    translated_words: int
    unknown: list[str]
    title: str = ""
    domain: str = ""
    filepath: str = ""
    document_id: int = 0

    @property
    def coverage(self) -> float:
        if self.input_words == 0:
            return 0.0
        return self.translated_words / self.input_words

    def frequency_rows(self) -> list[tuple[int, Alignment]]:
        counts: Counter[str] = Counter()
        first: dict[str, Alignment] = {}
        for item in self.alignments:
            key = item.source.lower()
            if not is_word(item.source):
                continue
            counts[key] += 1
            first.setdefault(key, item)
        rows = [(counts[key], first[key]) for key in counts]
        rows.sort(key=lambda pair: (-pair[0], pair[1].source.lower()))
        return rows


def _apply_transfer(chunks: list[tuple[str, str, str]]) -> list[str]:
    """
    Мини-трансфер англо-русской пары:
    артикли уже отброшены; JJ+NN переставляются как «сущ. прил.».
    """
    words = [target for target, _src, _pos in chunks if target]
    swapped: list[str] = []
    index = 0
    tags = [pos for _t, _s, pos in chunks if _t]
    values = [target for target, _s, _pos in chunks if target]
    while index < len(values):
        if index + 1 < len(tags) and tags[index].startswith("JJ") and tags[index + 1].startswith("NN"):
            swapped.append(values[index + 1])
            swapped.append(values[index])
            index += 2
            continue
        swapped.append(values[index])
        index += 1
    return swapped or words


def translate_text(text: str, dictionary: Dictionary) -> TranslationResult:
    sentences = split_sentences(text)
    translated_sentences: list[str] = []
    alignments: list[Alignment] = []
    unknown: list[str] = []
    input_words = 0
    translated_words = 0

    for sentence in sentences:
        tokens = tokenize(sentence)
        tagged = pos_tag(tokens)
        pieces: list[tuple[str, str, str]] = []
        index = 0
        lower_tokens = [token.lower() for token in tokens]
        while index < len(tagged):
            token, pos = tagged[index]
            if not is_word(token):
                if token in {".", ",", ";", ":", "!", "?"}:
                    pieces.append((token, token, pos))
                    alignments.append(Alignment(token, token, pos, True))
                index += 1
                continue

            input_words += 1
            if token.lower() in ARTICLES and pos == "DT":
                alignments.append(Alignment(token, "", pos, True))
                translated_words += 1
                index += 1
                continue

            matched = dictionary.longest_match(lower_tokens, index)
            if matched:
                length, entry = matched
                source_span = " ".join(tokens[index:index + length])
                target = entry.target
                pieces.append((target, source_span, pos))
                alignments.append(Alignment(source_span, target, pos, True))
                translated_words += 1
                index += length
                continue

            dictionary.note_unknown(token.lower())
            unknown.append(token)
            pieces.append((token, token, pos))
            alignments.append(Alignment(token, token, pos, False))
            index += 1

        words = _apply_transfer(pieces)
        line = _join_russian(words)
        translated_sentences.append(line)

    return TranslationResult(
        source_text=text,
        translation=" ".join(translated_sentences),
        sentences=sentences,
        translated_sentences=translated_sentences,
        alignments=alignments,
        input_words=input_words,
        translated_words=translated_words,
        unknown=sorted(set(unknown), key=str.lower),
    )


def _join_russian(parts: list[str]) -> str:
    out: list[str] = []
    for part in parts:
        if not part:
            continue
        if out and part in {".", ",", ";", ":", "!", "?"}:
            out[-1] = out[-1] + part
        else:
            out.append(part)
    text = " ".join(out).strip()
    if text and text[0].islower():
        text = text[0].upper() + text[1:]
    return text


def format_frequency_table(result: TranslationResult, limit: int = 40) -> str:
    lines = [
        f"{'частота':>8}  {'слово':<28} {'перевод':<28} {'POS':<6} расшифровка",
        "-" * 110,
    ]
    for count, item in result.frequency_rows()[:limit]:
        target = item.target if item.target else "—"
        flag = "" if item.found else " [нет в словаре]"
        lines.append(
            f"{count:>8}  {item.source:<28} {target:<28} {item.pos:<6} "
            f"{tag_explanation(item.pos)}{flag}"
        )
    return "\n".join(lines)
