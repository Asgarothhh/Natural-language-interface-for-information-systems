import math
import os
from datetime import datetime
from typing import Dict, Optional, Union

import pymupdf
import numpy as np

from src.utils import tokenize_and_lemmatize

DOCUMENTS_DB: Dict[int, "Document"] = {}
VOCABULARY: Dict[str, int] = {}  # lemmStr -> lemmId
REVERSE_VOCABULARY: Dict[int, str] = {}  # lemmId -> lemmStr
TERM_DOC_COUNT: Dict[int, int] = {}  # lemmId -> P_i


class Document:
    def __init__(self, filepath: str, doc_id: int):
        self.document_id = doc_id
        self.filepath = filepath
        self.title = os.path.basename(filepath)
        self.text = ""
        self.vector: Dict[int, float] = {}

        now = datetime.now()
        self.date = now.strftime("%Y-%m-%d")
        self.time = now.strftime("%H:%M:%S")
        self.term_frequencies: Dict[int, int] = {}

    def _extract_text_from_pdf(self) -> str:
        """Извлечение текста из PDF через PyMuPDF."""
        doc = pymupdf.open(self.filepath)
        try:
            return " ".join(page.get_text() for page in doc)
        finally:
            doc.close()

    def _extract_text(self) -> str:
        ext = os.path.splitext(self.filepath)[1].lower()
        if ext == ".pdf":
            return self._extract_text_from_pdf()
        if ext == ".txt":
            with open(self.filepath, encoding="utf-8") as file:
                return file.read()
        raise ValueError(f"Неподдерживаемый формат файла: {self.filepath}")

    def add_document_to_base(self) -> bool:
        global DOCUMENTS_DB, VOCABULARY, REVERSE_VOCABULARY, TERM_DOC_COUNT

        if self.document_id in DOCUMENTS_DB:
            return False

        if not self.text:
            self.text = self._extract_text()

        tokens = tokenize_and_lemmatize(self.text)
        unique_terms_in_doc = set()

        for token in tokens:
            if token not in VOCABULARY:
                lemm_id = len(VOCABULARY) + 1
                VOCABULARY[token] = lemm_id
                REVERSE_VOCABULARY[lemm_id] = token
            else:
                lemm_id = VOCABULARY[token]

            self.term_frequencies[lemm_id] = self.term_frequencies.get(lemm_id, 0) + 1
            unique_terms_in_doc.add(lemm_id)

        for lemm_id in unique_terms_in_doc:
            TERM_DOC_COUNT[lemm_id] = TERM_DOC_COUNT.get(lemm_id, 0) + 1

        DOCUMENTS_DB[self.document_id] = self
        return True

    @staticmethod
    def delete_document_from_base(document_id: Optional[int]) -> bool:
        global DOCUMENTS_DB, TERM_DOC_COUNT
        if document_id is None or document_id not in DOCUMENTS_DB:
            return False

        doc = DOCUMENTS_DB[document_id]
        unique_terms = set(doc.term_frequencies.keys())

        for lemm_id in unique_terms:
            if lemm_id in TERM_DOC_COUNT:
                TERM_DOC_COUNT[lemm_id] -= 1
                if TERM_DOC_COUNT[lemm_id] <= 0:
                    del TERM_DOC_COUNT[lemm_id]

        del DOCUMENTS_DB[document_id]
        return True

    @staticmethod
    def _resolve_lemma_id(lemma: Union[str, int]) -> Optional[int]:
        if isinstance(lemma, int):
            return lemma if lemma in REVERSE_VOCABULARY else None

        tokens = tokenize_and_lemmatize(lemma)
        if not tokens:
            return VOCABULARY.get(lemma.lower())
        return VOCABULARY.get(tokens[0])

    @staticmethod
    def get_lemm_inverse_frequency(lemma: Union[str, int]) -> float:
        """Вычисление B_i = log(N / P_i)."""
        n_docs = len(DOCUMENTS_DB)
        if n_docs == 0:
            return 0.0

        lemm_id = Document._resolve_lemma_id(lemma)
        if not lemm_id or lemm_id not in TERM_DOC_COUNT:
            return 0.0

        p_i = TERM_DOC_COUNT.get(lemm_id, 0)
        return math.log(n_docs / p_i) if p_i > 0 else 0.0

    @staticmethod
    def get_lemm_weight_in_document(lemma: Union[str, int], document_id: int) -> float:
        """Вычисление веса A_i^j = Q_i^j * B_i."""
        if document_id not in DOCUMENTS_DB:
            return 0.0

        lemm_id = Document._resolve_lemma_id(lemma)
        if not lemm_id:
            return 0.0

        doc = DOCUMENTS_DB[document_id]
        q_ij = doc.term_frequencies.get(lemm_id, 0)
        b_i = Document.get_lemm_inverse_frequency(lemm_id)
        return q_ij * b_i

    @staticmethod
    def get_document_vector(document_id: int) -> Dict[int, float]:
        """Нормированный вектор документа (TF-IDF / L2)."""
        if document_id not in DOCUMENTS_DB:
            return {}
        doc = DOCUMENTS_DB[document_id]

        weights = {}
        sum_sq = 0.0
        for lemm_id, n_dk in doc.term_frequencies.items():
            b_i = Document.get_lemm_inverse_frequency(lemm_id)
            weight = n_dk * b_i
            weights[lemm_id] = weight
            sum_sq += weight ** 2

        norm = math.sqrt(sum_sq)
        if norm == 0:
            return {lemm_id: 0.0 for lemm_id in weights}
        return {lemm_id: weight / norm for lemm_id, weight in weights.items()}

    @staticmethod
    def rebuild_all_vectors() -> None:
        """Пересчитывает векторы после изменения коллекции (IDF зависит от N и P_i)."""
        for doc_id, doc in DOCUMENTS_DB.items():
            doc.vector = Document.get_document_vector(doc_id)

    @staticmethod
    def get_matrix_L() -> np.ndarray:
        """Явная бинарная матрица L размерности N x D (формула 1.7)."""
        n_docs = len(DOCUMENTS_DB)
        n_terms = len(VOCABULARY)
        matrix = np.zeros((n_docs, n_terms), dtype=np.float64)

        for row_idx, doc in enumerate(DOCUMENTS_DB.values()):
            for lemm_id in doc.term_frequencies:
                matrix[row_idx, lemm_id - 1] = 1.0
        return matrix
