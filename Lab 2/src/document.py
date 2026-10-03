"""Документ, предложения и коллекционные частоты для TF–IDF."""

from __future__ import annotations

import os
from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, Iterable, Optional

from src.utils import split_paragraphs, split_sentences, tokenize

DOCUMENTS_DB: Dict[int, "Document"] = {}
TERM_DOC_COUNT: Dict[str, int] = {}


@dataclass
class Sentence:
    index: int
    paragraph_index: int
    text: str
    start_char: int
    paragraph_start: int
    paragraph_length: int
    tokens: list[str]
    posd: float = 0.0
    posp: float = 0.0
    tfidf_score: float = 0.0
    weight: float = 0.0
    ml_score: float = 0.0

    @property
    def term_tf(self) -> Counter:
        return Counter(self.tokens)


class Document:
    def __init__(
        self,
        filepath: str,
        doc_id: int,
        language: str,
        domain: str,
        title: str = "",
        reference: str = "",
    ):
        self.document_id = doc_id
        self.filepath = filepath
        self.language = language
        self.domain = domain
        self.title = title or os.path.splitext(os.path.basename(filepath))[0]
        self.reference = reference
        self.text = ""
        self.paragraphs: list[str] = []
        self.sentences: list[Sentence] = []
        self.term_frequencies: Counter = Counter()
        self.char_length = 0

    def _extract_text(self) -> str:
        ext = os.path.splitext(self.filepath)[1].lower()
        if ext == ".pdf":
            import pymupdf

            doc = pymupdf.open(self.filepath)
            try:
                pages = []
                for page in doc:
                    pages.append(page.get_text("text"))
                return "\n".join(pages)
            finally:
                doc.close()
        if ext == ".txt":
            with open(self.filepath, encoding="utf-8") as file:
                return file.read()
        raise ValueError(f"Неподдерживаемый формат: {self.filepath}")

    def _build_sentences(self) -> None:
        self.paragraphs = split_paragraphs(self.text)
        self.sentences = []
        cursor = 0
        index = 0
        for para_index, paragraph in enumerate(self.paragraphs):
            found = self.text.find(paragraph, cursor)
            para_start = found if found >= 0 else cursor
            para_length = max(len(paragraph), 1)
            local_cursor = 0
            for raw in split_sentences(paragraph, self.language):
                local = paragraph.find(raw, local_cursor)
                if local < 0:
                    local = local_cursor
                start_char = para_start + local
                tokens = tokenize(raw, self.language)
                self.sentences.append(
                    Sentence(
                        index=index,
                        paragraph_index=para_index,
                        text=raw,
                        start_char=start_char,
                        paragraph_start=para_start,
                        paragraph_length=para_length,
                        tokens=tokens,
                    )
                )
                index += 1
                local_cursor = local + len(raw)
            cursor = para_start + len(paragraph)

        self.char_length = max(len(self.text), 1)
        self.term_frequencies = Counter(
            token for sentence in self.sentences for token in sentence.tokens
        )

    def add_document_to_base(self) -> bool:
        if self.document_id in DOCUMENTS_DB:
            return False
        if not self.text:
            self.text = self._extract_text()
        self._build_sentences()
        for term in set(self.term_frequencies):
            TERM_DOC_COUNT[term] = TERM_DOC_COUNT.get(term, 0) + 1
        DOCUMENTS_DB[self.document_id] = self
        return True

    @property
    def max_tf(self) -> int:
        return max(self.term_frequencies.values(), default=0)

    @staticmethod
    def reset() -> None:
        DOCUMENTS_DB.clear()
        TERM_DOC_COUNT.clear()

    @staticmethod
    def collection_size() -> int:
        return len(DOCUMENTS_DB)


def load_documents(paths: Iterable[tuple[str, dict]]) -> int:
    added = 0
    next_id = max(DOCUMENTS_DB.keys(), default=0) + 1
    for path, meta in paths:
        document = Document(
            filepath=path,
            doc_id=next_id,
            language=meta.get("language", "english"),
            domain=meta.get("domain", "unknown"),
            title=meta.get("title", ""),
            reference=meta.get("reference", ""),
        )
        if meta.get("body"):
            document.text = meta["body"]
        if document.add_document_to_base():
            added += 1
            next_id += 1
    return added
