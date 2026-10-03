"""Пайплайн: коллекция → словарь → перевод → вкладки → оценка."""

from __future__ import annotations

import os
from dataclasses import dataclass
from html import escape

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from src.corpus import ensure_corpus
from src.dictionary import Dictionary
from src.parser import html_tree, parse_tree_pretty
from src.translator import TranslationResult, format_frequency_table, translate_text
from src.utils import ensure_nltk, tag_explanation


@dataclass
class Document:
    document_id: int
    title: str
    domain: str
    filepath: str
    pdf_path: str
    text: str


class TranslationPipeline:
    def __init__(self, documents_dir: str, dictionary_path: str):
        self.documents_dir = documents_dir
        self.data_dir = os.path.dirname(documents_dir)
        self.dictionary = Dictionary(dictionary_path)
        self.documents: dict[int, Document] = {}

    def run(self) -> None:
        ensure_nltk()
        records = ensure_corpus(self.documents_dir)
        self.documents = {}
        for index, record in enumerate(records, start=1):
            self.documents[index] = Document(
                document_id=index,
                title=record["title"],
                domain=record["domain"],
                filepath=record["txt_path"],
                pdf_path=record["pdf_path"],
                text=record["body"],
            )

    def translate_document(self, document: Document) -> TranslationResult:
        result = translate_text(document.text, self.dictionary)
        result.title = document.title
        result.domain = document.domain
        result.filepath = document.pdf_path
        result.document_id = document.document_id
        return result

    def translate_free(self, text: str) -> TranslationResult:
        return translate_text(text, self.dictionary)

    def evaluate(self) -> list[TranslationResult]:
        return [self.translate_document(doc) for doc in self.documents.values()]

    def visualize_coverage(
        self,
        results: list[TranslationResult] | None = None,
        output_path: str | None = None,
    ) -> str:
        results = results or self.evaluate()
        if output_path is None:
            output_path = os.path.join(self.data_dir, "coverage.png")
        labels = [f"{item.document_id}. {item.domain[:3]}" for item in results]
        x = np.arange(len(labels))
        fig, ax = plt.subplots(figsize=(10, 4.5))
        ax.bar(x, [item.coverage for item in results], color="#2e6e8a")
        ax.set_ylim(0, 1.05)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=15, ha="right")
        ax.set_ylabel("доля переведённых слов")
        ax.set_title("Покрытие словаря по документам")
        ax.grid(axis="y", linestyle=":", alpha=0.6)
        fig.tight_layout()
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        fig.savefig(output_path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        return output_path


def format_text_report(result: TranslationResult, sentence_index: int = 0) -> str:
    tree_source = _sentence_at(result, sentence_index)
    tree = parse_tree_pretty(tree_source)
    unknown = ", ".join(result.unknown) if result.unknown else "—"
    link = os.path.abspath(result.filepath) if result.filepath else "—"
    return "\n".join(
        [
            f"Перевод: {result.title or 'свободный текст'}",
            f"id={result.document_id or '—'}  область={result.domain or '—'}",
            f"Исходный документ: {link}",
            f"Слов во входе: {result.input_words}   переведено: {result.translated_words}   "
            f"покрытие: {result.coverage:.0%}",
            f"Нет в словаре: {unknown}",
            "",
            "=== Перевод ===",
            "",
            result.translation,
            "",
            "=== Вкладка 1. Частотный список с грамматикой ===",
            "",
            format_frequency_table(result),
            "",
            f"=== Вкладка 2. Дерево разбора предложения {sentence_index + 1} ===",
            "",
            tree_source,
            "",
            tree,
        ]
    )


def format_html_report(result: TranslationResult, sentence_index: int = 0) -> str:
    tree_source = _sentence_at(result, sentence_index)
    rows = []
    for count, item in result.frequency_rows()[:50]:
        target = escape(item.target) if item.target else "—"
        mark = "" if item.found else " class='miss'"
        rows.append(
            "<tr{mark}><td>{count}</td><td>{src}</td><td>{tgt}</td>"
            "<td>{pos}</td><td>{exp}</td></tr>".format(
                mark=mark,
                count=count,
                src=escape(item.source),
                tgt=target,
                pos=escape(item.pos),
                exp=escape(tag_explanation(item.pos)),
            )
        )
    unknown = escape(", ".join(result.unknown)) if result.unknown else "—"
    href = ""
    if result.filepath:
        path = os.path.abspath(result.filepath).replace(" ", "%20")
        href = f'<p><strong>Исходный документ:</strong> <a href="file://{path}">{escape(os.path.abspath(result.filepath))}</a></p>'
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="utf-8"/>
  <title>Перевод — {escape(result.title or "текст")}</title>
  <style>
    body {{ font-family: Georgia, serif; max-width: 960px; margin: 2rem auto; line-height: 1.45; }}
    .tabs button {{ margin-right: .4rem; padding: .4rem .8rem; }}
    .tab {{ display: none; border: 1px solid #ccc; padding: 1rem; }}
    .tab.active {{ display: block; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #ddd; padding: .35rem .5rem; text-align: left; }}
    tr.miss td {{ color: #a33; }}
    pre {{ background: #f6f3ee; padding: 1rem; overflow: auto; }}
  </style>
</head>
<body>
  <h1>{escape(result.title or "Свободный текст")}</h1>
  {href}
  <p>Слов: {result.input_words}, переведено: {result.translated_words},
     покрытие: {result.coverage:.0%}. Нет в словаре: {unknown}.</p>
  <h2>Перевод</h2>
  <p>{escape(result.translation)}</p>
  <div class="tabs">
    <button type="button" onclick="showTab(1)">Вкладка 1. Частоты и грамматика</button>
    <button type="button" onclick="showTab(2)">Вкладка 2. Дерево разбора</button>
  </div>
  <div id="tab1" class="tab active">
    <table>
      <thead><tr><th>частота</th><th>слово</th><th>перевод</th><th>POS</th><th>расшифровка</th></tr></thead>
      <tbody>{''.join(rows)}</tbody>
    </table>
  </div>
  <div id="tab2" class="tab">
    <p>{escape(tree_source)}</p>
    {html_tree(tree_source)}
  </div>
  <script>
    function showTab(n) {{
      document.getElementById('tab1').className = n === 1 ? 'tab active' : 'tab';
      document.getElementById('tab2').className = n === 2 ? 'tab active' : 'tab';
    }}
  </script>
</body>
</html>
"""


def save_report(result: TranslationResult, output_dir: str, prefix: str | None = None, sentence_index: int = 0) -> tuple[str, str]:
    os.makedirs(output_dir, exist_ok=True)
    slug = prefix or f"{result.document_id:02d}"
    txt_path = os.path.join(output_dir, f"translation_{slug}.txt")
    html_path = os.path.join(output_dir, f"translation_{slug}.html")
    with open(txt_path, "w", encoding="utf-8") as file:
        file.write(format_text_report(result, sentence_index))
        file.write("\n")
    with open(html_path, "w", encoding="utf-8") as file:
        file.write(format_html_report(result, sentence_index))
    return txt_path, html_path


def _sentence_at(result: TranslationResult, index: int) -> str:
    if not result.sentences:
        return result.source_text
    index = max(0, min(index, len(result.sentences) - 1))
    return result.sentences[index]
