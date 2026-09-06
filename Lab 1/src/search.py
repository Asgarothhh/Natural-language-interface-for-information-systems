from dataclasses import dataclass, field
from typing import Dict, List

import numpy as np

from src.document import DOCUMENTS_DB, REVERSE_VOCABULARY, VOCABULARY, Document
from src.utils import tokenize_and_lemmatize


@dataclass
class SearchResult:
    document_id: int
    title: str
    snippet: str
    rank: float
    date: str
    filepath: str = ""
    matched_terms: List[str] = field(default_factory=list)

    def __repr__(self):
        matched = ", ".join(self.matched_terms) if self.matched_terms else "-"
        return (
            f"<SearchResult docId={self.document_id} rank={self.rank:.4f} "
            f"title='{self.title}' matched='{matched}'>"
        )


class Search:
    def __init__(
        self,
        search_query: str,
        all_words_together: bool = False,
        date_start_string: str = "",
        date_end_string: str = "",
    ):
        self.allWordsTogether: bool = all_words_together
        self.dateStartString: str = date_start_string
        self.dateEndString: str = date_end_string
        self.searchQuery: str = search_query

    def _get_search_query(self, query: str, doc_vector: Dict[int, float]) -> Dict[int, float]:
        """
        Вектор запроса Q = {w_q1, w_q2, ...},
        где w_qj = 1.0, если термин есть в запросе и словаре, иначе термин отсутствует.
        """
        del doc_vector  # одинаковая структура с ПОД, координаты берутся из словаря
        query_tokens = set(tokenize_and_lemmatize(query))
        query_vector = {}
        for token in query_tokens:
            lemm_id = VOCABULARY.get(token)
            if lemm_id is not None:
                query_vector[lemm_id] = 1.0
        return query_vector

    def _scalar_product(self, a: Dict[int, float], b: Dict[int, float]) -> float:
        common_keys = set(a.keys()).intersection(b.keys())
        if not common_keys:
            return 0.0
        vec_a = np.array([a[k] for k in common_keys], dtype=np.float64)
        vec_b = np.array([b[k] for k in common_keys], dtype=np.float64)
        return float(np.dot(vec_a, vec_b))

    def _euclidean_norm(self, a: Dict[int, float]) -> float:
        if not a:
            return 0.0
        vec = np.array(list(a.values()), dtype=np.float64)
        return float(np.linalg.norm(vec))

    def _linear_response(self, query_vector: Dict[int, float]) -> Dict[int, float]:
        """Вектор отклика r = L × q (формула 1.8)."""
        matrix_l = Document.get_matrix_L()
        q = np.zeros(len(VOCABULARY), dtype=np.float64)
        for lemm_id, weight in query_vector.items():
            q[lemm_id - 1] = weight

        response = matrix_l @ q
        return {
            doc_id: float(response[row_idx])
            for row_idx, doc_id in enumerate(DOCUMENTS_DB.keys())
        }

    def _passes_date_filter(self, doc: Document) -> bool:
        if self.dateStartString and doc.date < self.dateStartString:
            return False
        if self.dateEndString and doc.date > self.dateEndString:
            return False
        return True

    def get_search_result(self) -> List[SearchResult]:
        """
        Логический поиск (вариант 7): отбор документов по AND/OR,
        затем ранжирование косинусной мерой.
        """
        query_tokens = set(tokenize_and_lemmatize(self.searchQuery))
        if not query_tokens:
            return []

        dummy_vector = {lemm_id: 0.0 for lemm_id in VOCABULARY.values()}
        query_vec = self._get_search_query(self.searchQuery, dummy_vector)
        if not query_vec:
            return []

        # Неизвестные слова не встречаются ни в одном документе — AND даёт пустую выдачу
        if self.allWordsTogether and len(query_vec) != len(query_tokens):
            return []

        linear_scores = self._linear_response(query_vec)
        required_hits = float(len(query_vec))
        results: List[SearchResult] = []

        for doc_id, doc in DOCUMENTS_DB.items():
            if not self._passes_date_filter(doc):
                continue

            hits = linear_scores.get(doc_id, 0.0)
            if self.allWordsTogether:
                if hits < required_hits:
                    continue
            elif hits <= 0:
                continue

            doc_vec = doc.vector or Document.get_document_vector(doc_id)
            dot_product = self._scalar_product(doc_vec, query_vec)
            norm_d = self._euclidean_norm(doc_vec)
            norm_q = self._euclidean_norm(query_vec)
            denominator = norm_d * norm_q
            rank = dot_product / denominator if denominator > 0 else 0.0

            matched_terms = [
                REVERSE_VOCABULARY[lemm_id]
                for lemm_id in query_vec
                if lemm_id in doc.term_frequencies
            ]
            clean_text = doc.text.replace("\n", " ").strip()
            snippet = clean_text[:300] + "..." if len(clean_text) > 300 else clean_text

            results.append(
                SearchResult(
                    document_id=doc.document_id,
                    title=doc.title,
                    snippet=snippet,
                    rank=rank,
                    date=doc.date,
                    filepath=doc.filepath,
                    matched_terms=sorted(matched_terms),
                )
            )

        results.sort(key=lambda item: item.rank, reverse=True)
        return results
