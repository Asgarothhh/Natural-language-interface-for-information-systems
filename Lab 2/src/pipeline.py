"""Пайплайн: коллекция → индексация → два реферата → оценка и графики."""

from __future__ import annotations

import os
import time
from dataclasses import dataclass
from html import escape
from typing import Optional

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from src.corpus import ensure_corpus
from src.document import DOCUMENTS_DB, Document, load_documents
from src.extraction import extract_sentences, score_document
from src.keywords import format_keyword_tree, hierarchical_keywords, keyword_unigrams
from src.metrics import DocScores, jaccard, keyword_coverage, lead_sentences, rouge_n
from src.ml_summarizer import ml_extract
from src.utils import ensure_nltk, transform_sentence


@dataclass
class SummaryResult:
    document: Document
    keywords_tree: str
    keywords: list[str]
    classic: list[str]
    classic_ids: list[int]
    machine: list[str]
    machine_ids: list[int]
    se_seconds: float
    ml_seconds: float

    @property
    def classic_text(self) -> str:
        return " ".join(self.classic)

    @property
    def machine_text(self) -> str:
        return " ".join(self.machine)


class SummarizationPipeline:
    def __init__(self, documents_dir: str):
        self.documents_dir = documents_dir
        self.data_dir = os.path.dirname(documents_dir)
        self.records: list[dict] = []

    def run(self) -> None:
        ensure_nltk()
        self.records = ensure_corpus(self.documents_dir)
        Document.reset()
        load_documents(
            (
                record["path"],
                {
                    "language": record["language"],
                    "domain": record["domain"],
                    "title": record["title"],
                    "reference": record["reference"],
                    "body": record.get("body", ""),
                },
            )
            for record in self.records
        )

    def get_document(self, doc_id: int) -> Optional[Document]:
        return DOCUMENTS_DB.get(doc_id)

    def summarize(self, document: Document, count: int = 10) -> SummaryResult:
        started = time.perf_counter()
        weights = score_document(document)
        classic_sents = extract_sentences(document, count)
        se_seconds = time.perf_counter() - started

        started = time.perf_counter()
        ml_sents = ml_extract(document, count)
        ml_seconds = time.perf_counter() - started

        tree = hierarchical_keywords(document, weights)
        unigrams = keyword_unigrams(document, weights)
        return SummaryResult(
            document=document,
            keywords_tree=format_keyword_tree(tree),
            keywords=[item[0] for item in unigrams],
            classic=[transform_sentence(item.text) for item in classic_sents],
            classic_ids=[item.index for item in classic_sents],
            machine=[transform_sentence(item.text) for item in ml_sents],
            machine_ids=[item.index for item in ml_sents],
            se_seconds=se_seconds,
            ml_seconds=ml_seconds,
        )

    def evaluate(self, count: int = 10) -> list[DocScores]:
        scores = []
        for document in DOCUMENTS_DB.values():
            result = self.summarize(document, count)
            reference = document.reference or " ".join(lead_sentences(document, count))
            reference = " ".join(reference.split("\n\n")[:3])
            lang = document.language
            classic = result.classic_text
            machine = result.machine_text
            lead = " ".join(lead_sentences(document, count))
            scores.append(
                DocScores(
                    document_id=document.document_id,
                    title=document.title,
                    language=document.language,
                    domain=document.domain,
                    n_sentences=len(document.sentences),
                    se_rouge1=rouge_n(classic, reference, lang, 1),
                    se_rouge2=rouge_n(classic, reference, lang, 2),
                    ml_rouge1=rouge_n(machine, reference, lang, 1),
                    ml_rouge2=rouge_n(machine, reference, lang, 2),
                    lead_rouge1=rouge_n(lead, reference, lang, 1),
                    overlap=jaccard(result.classic_ids, result.machine_ids),
                    se_coverage=keyword_coverage(classic, result.keywords, lang),
                    ml_coverage=keyword_coverage(machine, result.keywords, lang),
                    se_seconds=result.se_seconds,
                    ml_seconds=result.ml_seconds,
                )
            )
        return scores

    def visualize_metrics(
        self,
        scores: list[DocScores] | None = None,
        output_path: str | None = None,
        show: bool = False,
    ) -> str:
        scores = scores or self.evaluate()
        if output_path is None:
            output_path = os.path.join(self.data_dir, "quality_metrics.png")
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

        labels = [f"{item.document_id}. {item.language[:2]}/{item.domain.split()[0]}" for item in scores]
        x = np.arange(len(labels))
        width = 0.25

        fig, axes = plt.subplots(2, 1, figsize=(12, 8))
        ax = axes[0]
        ax.bar(x - width, [item.se_rouge1 for item in scores], width, label="SE ROUGE-1")
        ax.bar(x, [item.ml_rouge1 for item in scores], width, label="ML ROUGE-1")
        ax.bar(x + width, [item.lead_rouge1 for item in scores], width, label="Lead-10 ROUGE-1")
        ax.set_ylabel("ROUGE-1 F1")
        ax.set_title("Сравнение с эталоном (лид Wikipedia / абзац-аннотация)")
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=20, ha="right")
        ax.set_ylim(0, 1.05)
        ax.legend()
        ax.grid(axis="y", linestyle=":", alpha=0.6)

        ax = axes[1]
        ax.bar(x - width, [item.overlap for item in scores], width, label="Jaccard SE∩ML")
        ax.bar(x, [item.se_coverage for item in scores], width, label="Покрытие KW (SE)")
        ax.bar(x + width, [item.ml_coverage for item in scores], width, label="Покрытие KW (ML)")
        ax.set_ylabel("Доля")
        ax.set_title("Согласие методов и покрытие ключевых слов")
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=20, ha="right")
        ax.set_ylim(0, 1.05)
        ax.legend()
        ax.grid(axis="y", linestyle=":", alpha=0.6)

        fig.tight_layout()
        fig.savefig(output_path, dpi=150, bbox_inches="tight")
        if show:
            plt.show()
        plt.close(fig)
        return output_path

    def visualize_time(
        self,
        scores: list[DocScores] | None = None,
        output_path: str | None = None,
        show: bool = False,
    ) -> str:
        scores = scores or self.evaluate()
        if output_path is None:
            output_path = os.path.join(self.data_dir, "runtime.png")
        labels = [str(item.document_id) for item in scores]
        x = np.arange(len(labels))
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.bar(x - 0.18, [item.se_seconds * 1000 for item in scores], 0.36, label="Sentence extraction")
        ax.bar(x + 0.18, [item.ml_seconds * 1000 for item in scores], 0.36, label="TextRank (ML)")
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.set_xlabel("id документа")
        ax.set_ylabel("мс")
        ax.set_title("Время построения реферата")
        ax.legend()
        ax.grid(axis="y", linestyle=":", alpha=0.6)
        fig.tight_layout()
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        fig.savefig(output_path, dpi=150, bbox_inches="tight")
        if show:
            plt.show()
        plt.close(fig)
        return output_path


def format_text_report(result: SummaryResult) -> str:
    doc = result.document
    link = os.path.abspath(doc.filepath)
    lines = [
        f"Реферат документа: {doc.title}",
        f"id={doc.document_id}  язык={doc.language}  область={doc.domain}",
        f"Исходный документ: {link}",
        f"Предложений в тексте: {len(doc.sentences)}  символов: {doc.char_length}",
        "",
        "=== 1. Sentence extraction ===",
        "",
        "Ключевые слова (иерархия):",
        result.keywords_tree,
        "",
        "Классический реферат:",
    ]
    for index, sentence in enumerate(result.classic, start=1):
        lines.append(f"{index}. {sentence}")
    lines += ["", "=== 2. Машинное обучение (TextRank) ===", ""]
    for index, sentence in enumerate(result.machine, start=1):
        lines.append(f"{index}. {sentence}")
    lines += [
        "",
        f"Время SE: {result.se_seconds*1000:.1f} мс   время ML: {result.ml_seconds*1000:.1f} мс",
    ]
    return "\n".join(lines)


def format_html_report(result: SummaryResult) -> str:
    doc = result.document
    link = os.path.abspath(doc.filepath)
    href = "file://" + link.replace(" ", "%20")
    classic = "".join(f"<li>{escape(sentence)}</li>" for sentence in result.classic)
    machine = "".join(f"<li>{escape(sentence)}</li>" for sentence in result.machine)
    keywords = escape(result.keywords_tree)
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="utf-8"/>
  <title>Реферат — {escape(doc.title)}</title>
  <style>
    body {{ font-family: Georgia, serif; max-width: 820px; margin: 2rem auto; line-height: 1.45; }}
    a {{ color: #1a5276; }}
    pre {{ background: #f4f1ea; padding: 1rem; white-space: pre-wrap; }}
    h1, h2, h3 {{ font-family: "DejaVu Sans", sans-serif; }}
  </style>
</head>
<body>
  <h1>{escape(doc.title)}</h1>
  <p>Язык: {escape(doc.language)}. Область: {escape(doc.domain)}.
     Предложений: {len(doc.sentences)}.</p>
  <p><strong>Исходный документ:</strong> <a href="{href}">{escape(link)}</a></p>

  <h2>1. Sentence extraction</h2>
  <h3>Ключевые слова</h3>
  <pre>{keywords}</pre>
  <h3>Классический реферат</h3>
  <ol>{classic}</ol>

  <h2>2. Машинное обучение (TextRank)</h2>
  <ol>{machine}</ol>
  <p>Время SE: {result.se_seconds*1000:.1f} мс, время ML: {result.ml_seconds*1000:.1f} мс.</p>
</body>
</html>
"""


def save_report(result: SummaryResult, output_dir: str, prefix: str | None = None) -> tuple[str, str]:
    os.makedirs(output_dir, exist_ok=True)
    slug = prefix or f"{result.document.document_id:02d}"
    txt_path = os.path.join(output_dir, f"summary_{slug}.txt")
    html_path = os.path.join(output_dir, f"summary_{slug}.html")
    with open(txt_path, "w", encoding="utf-8") as file:
        file.write(format_text_report(result))
        file.write("\n")
    with open(html_path, "w", encoding="utf-8") as file:
        file.write(format_html_report(result))
    return txt_path, html_path
