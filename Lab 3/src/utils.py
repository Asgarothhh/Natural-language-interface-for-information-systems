"""Токенизация, POS-теги Penn Treebank и их расшифровка."""

from __future__ import annotations

import re

TOKEN_RE = re.compile(r"[A-Za-z]+(?:['-][A-Za-z]+)?|[0-9]+|[^\sA-Za-z0-9]")

PENN_TAGS: dict[str, str] = {
    "CC": "сочинительный союз (and, but, or)",
    "CD": "числительное (one, two, 15)",
    "DT": "детерминатив, артикль (the, a, this)",
    "EX": "экзистенциальное there",
    "FW": "иностранное слово",
    "IN": "предлог или подчинительный союз (in, of, that)",
    "JJ": "прилагательное (clinical, red)",
    "JJR": "прилагательное в сравнительной степени (better)",
    "JJS": "прилагательное в превосходной степени (best)",
    "LS": "маркер списка",
    "MD": "модальный глагол (can, must, will)",
    "NN": "существительное, ед. число (patient, museum)",
    "NNS": "существительное, мн. число (patients, colors)",
    "NNP": "имя собственное, ед. число",
    "NNPS": "имя собственное, мн. число",
    "PDT": "предопределитель (all, both)",
    "POS": "притяжательный маркер ('s)",
    "PRP": "личное местоимение (he, it, they)",
    "PRP$": "притяжательное местоимение (his, its)",
    "RB": "наречие (often, clinically)",
    "RBR": "наречие в сравнительной степени",
    "RBS": "наречие в превосходной степени",
    "RP": "частица (up, off)",
    "SYM": "символ",
    "TO": "частица to",
    "UH": "междометие",
    "VB": "глагол, базовая форма (treat)",
    "VBD": "глагол, прошедшее время (treated)",
    "VBG": "причастие / герундий (treating)",
    "VBN": "причастие прошедшего времени (treated)",
    "VBP": "глагол, настоящее, не 3 л. ед. (treat)",
    "VBZ": "глагол, настоящее, 3 л. ед. (treats)",
    "WDT": "wh-детерминатив (which, that)",
    "WP": "wh-местоимение (who, what)",
    "WP$": "притяжательное wh-местоимение",
    "WRB": "wh-наречие (where, when, how)",
    ".": "точка",
    ",": "запятая",
    ":": "двоеточие / точка с запятой",
    "(": "открывающая скобка",
    ")": "закрывающая скобка",
    "``": "открывающая кавычка",
    "''": "закрывающая кавычка",
}

_pos_tag = None
_sent_tokenize = None


def ensure_nltk() -> None:
    try:
        import nltk
    except ImportError:
        return
    for resource in (
        "tokenizers/punkt",
        "tokenizers/punkt_tab",
        "taggers/averaged_perceptron_tagger",
        "taggers/averaged_perceptron_tagger_eng",
    ):
        try:
            nltk.data.find(resource)
        except LookupError:
            name = resource.rsplit("/", 1)[-1]
            try:
                nltk.download(name, quiet=True)
            except Exception:
                continue


def tag_explanation(tag: str) -> str:
    return PENN_TAGS.get(tag, f"тег {tag}")


def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(text)


def split_sentences(text: str) -> list[str]:
    global _sent_tokenize
    if _sent_tokenize is None:
        try:
            from nltk.tokenize import sent_tokenize
            sent_tokenize("Test sentence.")
            _sent_tokenize = sent_tokenize
        except (LookupError, ImportError):
            _sent_tokenize = False
    if _sent_tokenize:
        return [part.strip() for part in _sent_tokenize(text) if part.strip()]
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+", text) if part.strip()]


def pos_tag(tokens: list[str]) -> list[tuple[str, str]]:
    global _pos_tag
    if not tokens:
        return []
    if _pos_tag is None:
        try:
            from nltk import pos_tag as nltk_pos_tag
            nltk_pos_tag(["test"])
            _pos_tag = nltk_pos_tag
        except (LookupError, ImportError):
            _pos_tag = False
    if _pos_tag:
        return _pos_tag(tokens)
    return [(token, _fallback_tag(token)) for token in tokens]


def _fallback_tag(token: str) -> str:
    if re.fullmatch(r"[0-9]+", token):
        return "CD"
    if token in {".", "!", "?"}:
        return "."
    if token in {",", ";", ":"}:
        return token if token == "," else ":"
    if token.lower() in {"the", "a", "an", "this", "that", "these", "those"}:
        return "DT"
    if token.lower() in {"in", "on", "at", "of", "for", "with", "by", "from", "into", "about"}:
        return "IN"
    if token.lower() in {"and", "or", "but"}:
        return "CC"
    if token.lower() in {"is", "are", "was", "were", "be", "been", "being"}:
        return "VB" if token.lower() == "be" else "VBZ"
    if token[:1].isupper():
        return "NNP"
    if token.endswith("ing"):
        return "VBG"
    if token.endswith("ed"):
        return "VBD"
    if token.endswith("ly"):
        return "RB"
    if token.endswith("s") and len(token) > 3:
        return "NNS"
    return "NN"


def is_word(token: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z]+(?:['-][A-Za-z]+)?", token))
