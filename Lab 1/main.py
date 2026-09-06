from __future__ import annotations

import argparse
import os
import sys
import webbrowser

from src.document import DOCUMENTS_DB, VOCABULARY
from src.pipeline import SearchPipeline
from src.search import SearchResult

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DOCUMENTS_DIR = os.path.join(ROOT_DIR, "data", "documents")


def _print_result(index: int, item: SearchResult) -> None:
    matched = ", ".join(item.matched_terms) if item.matched_terms else "—"
    print(f"  {index}. [{item.rank:.4f}] {item.title}  (id={item.document_id}, {item.date})")
    print(f"     слова запроса в документе: {matched}")
    print(f"     ссылка: {item.filepath}")
    print(f"     фрагмент: {item.snippet[:180]}...")
    print()


def show_help() -> None:
    print(
        """
Команды интерактивного режима
  search <запрос>     логический поиск по ИЛИ (хотя бы один термин)
  and <запрос>        логический поиск по И (все термины сразу)
  open <id>           открыть документ по идентификатору
  list                показать проиндексированные документы
  eval                таблица метрик качества на тестовых запросах
  help                эта справка
  quit                выход

Примеры
  search ethernet switch vlan
  and wireless access point
        """.strip()
    )


def print_collection(pipeline: SearchPipeline) -> None:
    print(f"\nКоллекция: {len(DOCUMENTS_DB)} документов, словарь: {len(VOCABULARY)} терминов")
    print(f"Каталог: {pipeline.documents_dir}\n")
    for doc in DOCUMENTS_DB.values():
        print(f"  {doc.document_id}. {doc.title}  [{doc.date}]  {doc.filepath}")
    print()


def print_search(results: list[SearchResult], query: str, mode: str) -> None:
    print(f"\nЗапрос: «{query}»   режим: {mode}   найдено: {len(results)}\n")
    if not results:
        print("  Ничего не найдено.\n")
        return
    for index, item in enumerate(results, start=1):
        _print_result(index, item)


def print_metrics(pipeline: SearchPipeline) -> None:
    scores = pipeline.evaluate()
    print("\nОценка качества (логические запросы, экспертная разметка)\n")
    header = f"{'Запрос':<38} {'P':>6} {'R':>6} {'F1':>6} {'AP':>6}  Выдача"
    print(header)
    print("-" * len(header))
    for item in scores:
        retrieved = ",".join(str(doc_id) for doc_id in item.retrieved) or "—"
        print(
            f"{item.query:<38} {item.precision:6.2f} {item.recall:6.2f} "
            f"{item.f1:6.2f} {item.average_precision:6.2f}  {retrieved}"
        )
    print("-" * len(header))
    print(f"{'MAP':<38} {pipeline.mean_average_precision(scores):6.2f}\n")
    print("P — точность, R — полнота, F1 — среднее гармоническое, AP — average precision, MAP — среднее AP.\n")


def open_document(doc_id: int) -> None:
    doc = DOCUMENTS_DB.get(doc_id)
    if doc is None:
        print(f"Документ {doc_id} не найден.")
        return
    path = os.path.abspath(doc.filepath)
    print(f"Открываю {path}")
    webbrowser.open(path)


def run_demo(pipeline: SearchPipeline) -> None:
    print("\n=== Демонстрация пайплайна ===")
    print_collection(pipeline)

    demos = (
        ("ethernet switch collision", False),
        ("wireless access point", True),
        ("vlan security firewall", False),
    )
    for query, all_words in demos:
        mode = "AND" if all_words else "OR"
        print_search(pipeline.search(query, all_words_together=all_words), query, mode)
    print_metrics(pipeline)


def interactive_loop(pipeline: SearchPipeline) -> None:
    show_help()
    while True:
        try:
            raw = input("irs> ").strip()
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
            if not argument.isdigit():
                print("Укажите идентификатор: open 3")
                continue
            open_document(int(argument))
        elif command in {"search", "and"}:
            if not argument:
                print("Введите запрос после команды.")
                continue
            results = pipeline.search(argument, all_words_together=(command == "and"))
            print_search(results, argument, "AND" if command == "and" else "OR")
        else:
            print("Неизвестная команда. Введите help.")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="ИПС по документам локальной вычислительной сети (вариант 7)."
    )
    parser.add_argument(
        "--documents",
        default=DOCUMENTS_DIR,
        help="каталог PDF/TXT документов",
    )
    parser.add_argument("--query", help="выполнить один запрос и выйти")
    parser.add_argument("--and", dest="all_words", action="store_true", help="режим AND")
    parser.add_argument("--demo", action="store_true", help="показать демонстрационный прогон")
    parser.add_argument("--eval", action="store_true", help="только таблица метрик")
    parser.add_argument("--no-interactive", action="store_true", help="не входить в консоль")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    pipeline = SearchPipeline(os.path.abspath(args.documents))

    print("Подготовка среды и индексация коллекции...")
    pipeline.run()
    print(
        f"Готово: документов={len(DOCUMENTS_DB)}, терминов={len(VOCABULARY)}, "
        f"каталог={pipeline.documents_dir}"
    )

    if args.query:
        print_search(pipeline.search(args.query, all_words_together=args.all_words), args.query, "AND" if args.all_words else "OR")
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
