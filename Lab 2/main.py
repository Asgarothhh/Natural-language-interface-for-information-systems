from __future__ import annotations

import argparse
import os
import subprocess
import sys
import webbrowser

from src.document import DOCUMENTS_DB
from src.pipeline import (
    SummarizationPipeline,
    format_text_report,
    save_report,
)

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DOCUMENTS_DIR = os.path.join(ROOT_DIR, "data", "documents")
SUMMARIES_DIR = os.path.join(ROOT_DIR, "data", "summaries")


def show_help() -> None:
    print(
        """
Команды интерактивного режима
  list                 показать коллекцию документов
  show <id>            построить и показать реферат документа
  save <id> [файл]     сохранить реферат в TXT и HTML
  print <id>           сохранить реферат и отправить на печать
  open <id>            открыть исходный PDF (активная ссылка)
  eval                 таблица качества, графики ROUGE и времени
  help                 эта справка
  quit                 выход

Реферат всегда состоит из двух разделов:
  1) sentence extraction — ключевые слова и классический реферат (10 предложений);
  2) машинное обучение — TextRank на графе близости предложений.

Примеры
  show 1
  save 3
  open 5
        """.strip()
    )


def print_collection(pipeline: SummarizationPipeline) -> None:
    print(f"\nКоллекция: {len(DOCUMENTS_DB)} документов")
    print(f"Каталог: {pipeline.documents_dir}\n")
    for doc in DOCUMENTS_DB.values():
        pages_est = max(doc.char_length / 4200, 1)
        print(
            f"  {doc.document_id}. {doc.title}"
            f"  [{doc.language}, {doc.domain}]"
            f"  ~{pages_est:.1f} стр.  {doc.filepath}"
        )
    print()


def print_summary(result) -> None:
    print()
    print(format_text_report(result))
    print()


def open_path(path: str) -> None:
    abs_path = os.path.abspath(path)
    print(f"Открываю {abs_path}")
    webbrowser.open(abs_path)


def print_file(path: str) -> None:
    abs_path = os.path.abspath(path)
    for command in (("lp", abs_path), ("lpr", abs_path)):
        try:
            completed = subprocess.run(command, check=False, capture_output=True, text=True)
            if completed.returncode == 0:
                print(f"Отправлено на печать: {abs_path}")
                return
        except FileNotFoundError:
            continue
    print("Системная печать недоступна, открываю файл — используйте диалог печати браузера.")
    open_path(path)


def print_metrics(pipeline: SummarizationPipeline) -> None:
    scores = pipeline.evaluate()
    print("\nОценка качества рефератов")
    print("Эталон — первые три абзаца лида Wikipedia (или аннотация запасного текста).\n")
    header = (
        f"{'id':>3} {'язык':<8} {'область':<18} {'N':>4} "
        f"{'SE-1':>6} {'ML-1':>6} {'Lead':>6} {'Jac':>5} "
        f"{'SE мс':>7} {'ML мс':>7}"
    )
    print(header)
    print("-" * len(header))
    for item in scores:
        print(
            f"{item.document_id:>3} {item.language:<8} {item.domain:<18} {item.n_sentences:>4} "
            f"{item.se_rouge1:6.2f} {item.ml_rouge1:6.2f} {item.lead_rouge1:6.2f} {item.overlap:5.2f} "
            f"{item.se_seconds*1000:7.1f} {item.ml_seconds*1000:7.1f}"
        )
    print("-" * len(header))
    if scores:
        mean_se = sum(item.se_rouge1 for item in scores) / len(scores)
        mean_ml = sum(item.ml_rouge1 for item in scores) / len(scores)
        print(f"Средний ROUGE-1:  SE={mean_se:.2f}  ML={mean_ml:.2f}\n")
        print("SE — sentence extraction, ML — TextRank, Lead — первые 10 предложений, Jac — Jaccard выбранных предложений.")

    chart = pipeline.visualize_metrics(scores, show=False)
    timing = pipeline.visualize_time(scores, show=False)
    print(f"График качества: {chart}")
    print(f"График времени:  {timing}")
    for doc in DOCUMENTS_DB.values():
        save_report(pipeline.summarize(doc), SUMMARIES_DIR)
    print(f"Рефераты сохранены в {SUMMARIES_DIR}\n")

    by_lang: dict[str, list] = {}
    by_domain: dict[str, list] = {}
    for item in scores:
        by_lang.setdefault(item.language, []).append(item)
        by_domain.setdefault(item.domain, []).append(item)
    print("Средний ROUGE-1 по языкам и областям:")
    for name, group in list(by_lang.items()) + list(by_domain.items()):
        se = sum(item.se_rouge1 for item in group) / len(group)
        ml = sum(item.ml_rouge1 for item in group) / len(group)
        print(f"  {name:<18} SE={se:.2f}  ML={ml:.2f}")
    print()


def resolve_document(argument: str):
    if not argument.isdigit():
        print("Укажите идентификатор документа, например: show 2")
        return None
    doc = DOCUMENTS_DB.get(int(argument))
    if doc is None:
        print(f"Документа {argument} нет в коллекции (смотрите list).")
        return None
    return doc


def interactive_loop(pipeline: SummarizationPipeline) -> None:
    show_help()
    while True:
        try:
            raw = input("sum> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not raw:
            continue
        command, _, argument = raw.partition(" ")
        command = command.lower()
        argument = argument.strip()

        if command in {"quit", "exit", "q"}:
            break
        if command == "help":
            show_help()
        elif command == "list":
            print_collection(pipeline)
        elif command == "eval":
            print_metrics(pipeline)
        elif command == "open":
            doc = resolve_document(argument)
            if doc:
                open_path(doc.filepath)
        elif command == "show":
            doc = resolve_document(argument)
            if doc:
                print_summary(pipeline.summarize(doc))
        elif command == "save":
            doc_id, _, maybe_path = argument.partition(" ")
            doc = resolve_document(doc_id)
            if not doc:
                continue
            result = pipeline.summarize(doc)
            output_dir = SUMMARIES_DIR
            prefix = None
            maybe_path = maybe_path.strip()
            if maybe_path:
                output_dir = os.path.dirname(os.path.abspath(maybe_path)) or SUMMARIES_DIR
                prefix = os.path.splitext(os.path.basename(maybe_path))[0]
            txt_path, html_path = save_report(result, output_dir, prefix)
            print(f"Сохранено:\n  {txt_path}\n  {html_path}")
        elif command == "print":
            doc = resolve_document(argument)
            if not doc:
                continue
            result = pipeline.summarize(doc)
            _, html_path = save_report(result, SUMMARIES_DIR)
            print_file(html_path)
        else:
            print("Неизвестная команда. Введите help.")


def run_demo(pipeline: SummarizationPipeline) -> None:
    print("\n=== Демонстрация реферирования ===")
    print_collection(pipeline)
    sample_ids = [1, 5]
    for doc_id in sample_ids:
        doc = DOCUMENTS_DB.get(doc_id)
        if doc:
            print_summary(pipeline.summarize(doc))
            save_report(pipeline.summarize(doc), SUMMARIES_DIR)
    print_metrics(pipeline)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Автоматическое реферирование документов (вариант 7: FR+EN, CS и литература)."
    )
    parser.add_argument("--documents", default=DOCUMENTS_DIR, help="каталог PDF документов")
    parser.add_argument("--id", type=int, help="показать реферат одного документа и выйти")
    parser.add_argument("--save", action="store_true", help="сохранить реферат при --id")
    parser.add_argument("--eval", action="store_true", help="только таблица метрик")
    parser.add_argument("--demo", action="store_true", help="демонстрационный прогон")
    parser.add_argument("--no-interactive", action="store_true", help="не входить в консоль")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    pipeline = SummarizationPipeline(os.path.abspath(args.documents))
    print("Подготовка коллекции и индексация...")
    pipeline.run()
    print(f"Готово: документов={len(DOCUMENTS_DB)}, каталог={pipeline.documents_dir}")

    if args.id:
        doc = DOCUMENTS_DB.get(args.id)
        if doc is None:
            print(f"Документа {args.id} нет.")
            return 1
        result = pipeline.summarize(doc)
        print_summary(result)
        if args.save:
            txt_path, html_path = save_report(result, SUMMARIES_DIR)
            print(f"Сохранено:\n  {txt_path}\n  {html_path}")
        return 0
    if args.eval:
        print_metrics(pipeline)
        return 0
    if args.demo or not args.no_interactive:
        run_demo(pipeline)
    if not args.no_interactive and not args.demo:
        interactive_loop(pipeline)
    elif args.demo and not args.no_interactive:
        interactive_loop(pipeline)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
