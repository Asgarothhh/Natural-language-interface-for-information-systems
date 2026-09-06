from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Iterable, List, Sequence

import matplotlib.pyplot as plt
import numpy as np

from src.corpus import ensure_corpus
from src.document import DOCUMENTS_DB, VOCABULARY, Document
from src.search import Search, SearchResult

# Экспертные оценки релевантности для демонстрации метрик качества
RELEVANCE_JUDGMENTS: dict[str, set[int]] = {
    "ethernet collision switch": {2, 4},
    "wireless wifi access point": {7},
    "ip subnet dhcp addressing": {5},
    "firewall security access control": {8},
    "star topology cable": {3},
    "vlan trunk segmentation": {6},
    "local area network campus": {1, 3, 4},
}


@dataclass
class QualityScores:
    query: str
    retrieved: List[int]
    relevant: set[int]
    precision: float
    recall: float
    f1: float
    average_precision: float


class SearchPipeline:
    def __init__(self, documents_dir: str):
        self.documents_dir = documents_dir

    def setup_environment(self) -> None:
        """NLTK подключается лениво в utils; сеть при старте не трогаем."""
        return

    def build_collection(self) -> List[str]:
        return ensure_corpus(self.documents_dir)

    def index_documents(self, paths: Iterable[str] | None = None) -> int:
        if paths is None:
            paths = [
                os.path.join(self.documents_dir, name)
                for name in sorted(os.listdir(self.documents_dir))
                if name.lower().endswith((".pdf", ".txt"))
            ]

        added = 0
        next_id = max(DOCUMENTS_DB.keys(), default=0) + 1
        for path in paths:
            document = Document(path, next_id)
            if document.add_document_to_base():
                added += 1
                next_id += 1
        Document.rebuild_all_vectors()
        return added

    def search(
        self,
        query: str,
        all_words_together: bool = False,
        date_start: str = "",
        date_end: str = "",
    ) -> List[SearchResult]:
        engine = Search(
            search_query=query,
            all_words_together=all_words_together,
            date_start_string=date_start,
            date_end_string=date_end,
        )
        return engine.get_search_result()

    def evaluate(self, judgments: dict[str, set[int]] | None = None) -> List[QualityScores]:
        judgments = judgments or RELEVANCE_JUDGMENTS
        scores = []
        for query, relevant in judgments.items():
            results = self.search(query, all_words_together=False)
            retrieved = [item.document_id for item in results]
            scores.append(_score_query(query, retrieved, relevant))
        return scores

    def mean_average_precision(self, scores: Sequence[QualityScores]) -> float:
        if not scores:
            return 0.0
        return sum(item.average_precision for item in scores) / len(scores)

    def visualize_metrics(
        self,
        scores: Sequence[QualityScores] | None = None,
        output_path: str | None = None,
        show: bool = True,
    ) -> str:
        """Столбчатая диаграмма P, R, F1, AP по запросам и линия MAP."""
        scores = list(scores) if scores is not None else self.evaluate()
        if output_path is None:
            output_path = os.path.join(os.path.dirname(self.documents_dir), "quality_metrics.png")

        if not scores:
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.set_title("Метрики качества поиска")
            ax.text(0.5, 0.5, "Нет оценок для визуализации", ha="center", va="center")
            ax.axis("off")
            fig.savefig(output_path, dpi=150, bbox_inches="tight")
            if show:
                plt.show()
            plt.close(fig)
            return output_path

        labels = [item.query for item in scores]
        x = np.arange(len(labels))
        width = 0.18
        series = (
            ("P", [item.precision for item in scores]),
            ("R", [item.recall for item in scores]),
            ("F1", [item.f1 for item in scores]),
            ("AP", [item.average_precision for item in scores]),
        )
        map_value = self.mean_average_precision(scores)

        fig, ax = plt.subplots(figsize=(12, 6))
        for index, (name, values) in enumerate(series):
            ax.bar(x + (index - 1.5) * width, values, width, label=name)

        ax.axhline(map_value, color="black", linestyle="--", linewidth=1.2, label=f"MAP = {map_value:.2f}")
        ax.set_ylim(0, 1.15)
        ax.set_ylabel("Значение")
        ax.set_title("Метрики качества поиска")
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=25, ha="right")
        ax.legend(loc="upper right")
        ax.grid(axis="y", linestyle=":", alpha=0.6)
        fig.tight_layout()
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        fig.savefig(output_path, dpi=150, bbox_inches="tight")
        if show:
            plt.show()
        plt.close(fig)
        return output_path

    def run(self) -> List[str]:
        self.setup_environment()
        paths = self.build_collection()
        self.index_documents(paths)
        return paths


def _safe_div(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator else 0.0


def _score_query(query: str, retrieved: List[int], relevant: set[int]) -> QualityScores:
    retrieved_set = set(retrieved)
    true_positive = len(retrieved_set & relevant)
    precision = _safe_div(true_positive, len(retrieved_set))
    recall = _safe_div(true_positive, len(relevant))
    f1 = _safe_div(2 * precision * recall, precision + recall)

    hits = 0
    precision_sum = 0.0
    for rank, doc_id in enumerate(retrieved, start=1):
        if doc_id in relevant:
            hits += 1
            precision_sum += hits / rank
    average_precision = _safe_div(precision_sum, len(relevant))

    return QualityScores(
        query=query,
        retrieved=retrieved,
        relevant=relevant,
        precision=precision,
        recall=recall,
        f1=f1,
        average_precision=average_precision,
    )
