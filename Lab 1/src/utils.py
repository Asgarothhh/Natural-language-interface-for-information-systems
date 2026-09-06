import re
import string

_FALLBACK_STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "if", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "as", "is", "are", "was", "were", "be", "been",
    "being", "it", "its", "this", "that", "these", "those", "not", "no", "nor",
    "so", "than", "too", "very", "can", "could", "should", "would", "may",
    "might", "must", "will", "just", "about", "into", "over", "after", "before",
    "between", "through", "during", "without", "within", "also", "only", "more",
    "most", "other", "some", "such", "own", "same", "both", "each", "few",
    "our", "your", "their", "them", "they", "we", "you", "he", "she", "his",
    "her", "him",
}

_lemmatizer = None
_stop_words = None
_use_word_tokenize = None


def _english_stopwords() -> set[str]:
    global _stop_words
    if _stop_words is not None:
        return _stop_words
    try:
        from nltk.corpus import stopwords
        _stop_words = set(stopwords.words("english"))
    except LookupError:
        _stop_words = set(_FALLBACK_STOPWORDS)
    return _stop_words


def _get_lemmatizer():
    global _lemmatizer
    if _lemmatizer is False:
        return None
    if _lemmatizer is not None:
        return _lemmatizer
    try:
        from nltk.stem import WordNetLemmatizer
        candidate = WordNetLemmatizer()
        candidate.lemmatize("switches")
        _lemmatizer = candidate
    except LookupError:
        _lemmatizer = False
        return None
    return _lemmatizer


def _tokenize(text: str) -> list[str]:
    global _use_word_tokenize
    if _use_word_tokenize is None:
        try:
            from nltk.tokenize import word_tokenize
            word_tokenize("test sentence")
            _use_word_tokenize = word_tokenize
        except LookupError:
            _use_word_tokenize = False
    if _use_word_tokenize:
        return _use_word_tokenize(text)
    return re.findall(r"[a-z]+", text)


def tokenize_and_lemmatize(text: str) -> list[str]:
    """Приведение к нижнему регистру, очистка пунктуации и лемматизация."""
    cleaned_text = "".join(char for char in text.lower() if char not in string.punctuation)
    cleaned_text = re.sub(r"\s+", " ", cleaned_text).strip()
    if not cleaned_text:
        return []

    words = _tokenize(cleaned_text)
    stop_words = _english_stopwords()
    filtered_words = [
        word for word in words
        if word.isalpha() and len(word) > 1 and word not in stop_words
    ]
    lemmatizer = _get_lemmatizer()
    if lemmatizer is None:
        return filtered_words
    return [lemmatizer.lemmatize(word) for word in filtered_words]
