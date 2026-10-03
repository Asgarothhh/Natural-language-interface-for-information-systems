"""Токенизация, стоп-слова и стемминг для английского и французского."""

from __future__ import annotations

import re
import unicodedata

TOKEN_RE = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿŒœÆæ]+", re.UNICODE)
NUMBER_RE = re.compile(r"\d")
INTRO_RE = re.compile(
    r"^\s*(?:"
    r"however|therefore|thus|moreover|furthermore|nevertheless|"
    r"in addition|for example|indeed|meanwhile|consequently|"
    r"in this (?:paper|article|essay|chapter)|"
    r"cependant|ainsi|donc|de plus|en outre|néanmoins|toutefois|"
    r"par exemple|en effet|par conséquent|"
    r"dans cet(?:te)? (?:article|essai|ouvrage|étude)"
    r")\s*[,:]?\s*",
    re.IGNORECASE,
)

_FALLBACK_STOPWORDS = {
    "english": {
        "a", "an", "the", "and", "or", "but", "if", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "as", "is", "are", "was", "were", "be", "been",
        "being", "it", "its", "this", "that", "these", "those", "not", "no", "nor",
        "so", "than", "too", "very", "can", "could", "should", "would", "may",
        "might", "must", "will", "just", "about", "into", "over", "after", "before",
        "between", "through", "during", "without", "within", "also", "only", "more",
        "most", "other", "some", "such", "own", "same", "both", "each", "few",
        "our", "your", "their", "them", "they", "we", "you", "he", "she", "his",
        "her", "him", "who", "which", "what", "when", "where", "how", "why",
        "has", "have", "had", "do", "does", "did", "done", "there", "here",
    },
    "french": {
        "le", "la", "les", "un", "une", "des", "du", "de", "d", "au", "aux",
        "et", "ou", "mais", "donc", "or", "ni", "car", "en", "dans", "sur",
        "sous", "avec", "sans", "pour", "par", "vers", "chez", "entre",
        "ce", "cet", "cette", "ces", "il", "elle", "ils", "elles", "on",
        "nous", "vous", "je", "tu", "me", "te", "se", "lui", "leur", "y",
        "est", "sont", "été", "etre", "être", "avoir", "a", "ont", "avait",
        "pas", "ne", "plus", "moins", "très", "aussi", "ainsi", "dont",
        "qui", "que", "quoi", "où", "quand", "comment", "pourquoi",
        "son", "sa", "ses", "notre", "nos", "votre", "vos", "leur", "leurs",
        "cependant", "alors", "comme", "si", "tout", "tous", "toute", "toutes",
    },
}

_stopwords_cache: dict[str, set[str]] = {}
_stemmers: dict[str, object] = {}
_sent_tokenize = None


def nltk_language(lang: str) -> str:
    if lang.lower().startswith("fr"):
        return "french"
    return "english"


def ensure_nltk() -> None:
    """Подгружает punkt и стоп-слова; без сети, если ресурсы уже есть."""
    try:
        import nltk
    except ImportError:
        return
    for resource in (
        "tokenizers/punkt",
        "tokenizers/punkt_tab",
        "corpora/stopwords",
    ):
        try:
            nltk.data.find(resource)
        except LookupError:
            name = resource.rsplit("/", 1)[-1]
            try:
                nltk.download(name, quiet=True)
            except Exception:
                continue


def stopwords_for(lang: str) -> set[str]:
    key = nltk_language(lang)
    cached = _stopwords_cache.get(key)
    if cached is not None:
        return cached
    words = set(_FALLBACK_STOPWORDS[key])
    try:
        from nltk.corpus import stopwords
        words |= {item.lower() for item in stopwords.words(key)}
    except (LookupError, ImportError, OSError):
        pass
    _stopwords_cache[key] = words
    return words


def _stemmer(lang: str):
    key = nltk_language(lang)
    if key in _stemmers:
        return _stemmers[key]
    try:
        from nltk.stem.snowball import SnowballStemmer
        stemmer = SnowballStemmer(key)
        _stemmers[key] = stemmer
        return stemmer
    except Exception:
        _stemmers[key] = None
        return None


def fold_accents(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text)
    return "".join(char for char in decomposed if unicodedata.category(char) != "Mn")


def is_content_token(token: str, lang: str) -> bool:
    """Числа и стоп-слова отбрасываются. Латиница — рабочий алфавит EN/FR."""
    if len(token) < 3:
        return False
    if NUMBER_RE.search(token):
        return False
    lowered = token.lower()
    stops = stopwords_for(lang)
    if lowered in stops or fold_accents(lowered) in stops:
        return False
    return True


def tokenize(text: str, lang: str, stem: bool = True) -> list[str]:
    stemmer = _stemmer(lang) if stem else None
    tokens: list[str] = []
    for raw in TOKEN_RE.findall(text.lower()):
        if not is_content_token(raw, lang):
            continue
        tokens.append(stemmer.stem(raw) if stemmer else raw)
    return tokens


def tokenize_keep(text: str, lang: str) -> list[tuple[str, str]]:
    """Пары (поверхностная форма, стем) для ключевых словосочетаний."""
    stemmer = _stemmer(lang)
    pairs: list[tuple[str, str]] = []
    for raw in TOKEN_RE.findall(text.lower()):
        if not is_content_token(raw, lang):
            continue
        stem = stemmer.stem(raw) if stemmer else raw
        pairs.append((raw, stem))
    return pairs


def split_sentences(text: str, lang: str) -> list[str]:
    global _sent_tokenize
    language = nltk_language(lang)
    if _sent_tokenize is None:
        try:
            from nltk.tokenize import sent_tokenize
            sent_tokenize("Test sentence.", language="english")
            _sent_tokenize = sent_tokenize
        except (LookupError, ImportError):
            _sent_tokenize = False
    if _sent_tokenize:
        try:
            parts = _sent_tokenize(text, language=language)
        except LookupError:
            parts = None
        if parts:
            return [part.strip() for part in parts if part.strip()]
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+", text) if part.strip()]


def split_paragraphs(text: str) -> list[str]:
    parts = re.split(r"\n\s*\n+", text.strip())
    return [re.sub(r"[ \t]+\n", "\n", part).strip() for part in parts if part.strip()]


def transform_sentence(text: str) -> str:
    """Лёгкая правка: убрать вводную конструкцию в начале предложения."""
    cleaned = INTRO_RE.sub("", text).strip()
    if not cleaned:
        return text.strip()
    if cleaned[0].islower():
        cleaned = cleaned[0].upper() + cleaned[1:]
    return cleaned
