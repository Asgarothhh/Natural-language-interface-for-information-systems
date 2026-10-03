from __future__ import annotations

import argparse
import os
import subprocess
import sys
import webbrowser

from src.pipeline import (
    TranslationPipeline,
    format_text_report,
    save_report,
)

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DOCUMENTS_DIR = os.path.join(ROOT_DIR, "data", "documents")
OUTPUT_DIR = os.path.join(ROOT_DIR, "data", "translations")
DICTIONARY_PATH = os.path.join(ROOT_DIR, "data", "dictionary.sqlite")


def show_help() -> None:
    print(
        """
Команды интерактивного режима
  list                      коллекция документов
  show <id> [n]             перевод, вкладка 1 и дерево предложения n (по умолчанию 1)
  tab1 <id>                 частотный список слов с POS и переводом
  tab2 <id> [n]             дерево синтаксического разбора предложения n
  translate <текст>         перевести произвольную английскую фразу
  save <id>                 сохранить TXT (Unicode) и HTML
  print <id>                сохранить и отправить на печать
  open <id>                 открыть исходный PDF
  dict list [запрос]        показать словарь
  dict add слово = перевод [POS]
  dict del слово            удалить единицу словаря
  dict pending              неизвестные слова для пополнения
  eval                      покрытие словаря и график
  help                      эта справка
  quit                      выход

Вариант 7: английский → русский; медицина и критика изобразительного искусства.
Система — прямой (пословно-оборотный) перевод по словарю SQLite.
        """.strip()
    )


def print_collection(pipeline: TranslationPipeline) -> None:
    print(f"\nКоллекция: {len(pipeline.documents)} документов")
    print(f"Словарь: {pipeline.dictionary.size()} единиц  ({pipeline.dictionary.path})\n")
    for doc in pipeline.documents.values():
        print(f"  {doc.document_id}. {doc.title}  [{doc.domain}]  {doc.filepath}")
    print()


def print_result(result, sentence_index: int = 0) -> None:
    print()
    print(format_text_report(result, sentence_index))
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


def resolve_document(pipeline: TranslationPipeline, argument: str):
    token = argument.split()[0] if argument else ""
    if not token.isdigit():
        print("Укажите идентификатор документа, например: show 2")
        return None
    doc = pipeline.documents.get(int(token))
    if doc is None:
        print(f"Документа {token} нет в коллекции (смотрите list).")
        return None
    return doc


def sentence_index_from(argument: str) -> int:
    parts = argument.split()
    if len(parts) >= 2 and parts[1].isdigit():
        return max(int(parts[1]) - 1, 0)
    return 0


def print_metrics(pipeline: TranslationPipeline) -> None:
    results = pipeline.evaluate()
    print("\nОценка покрытия словаря (прямой перевод EN→RU)\n")
    header = f"{'id':>3} {'область':<12} {'слов':>6} {'пер.':>6} {'покрытие':>9}  заголовок"
    print(header)
    print("-" * 90)
    for item in results:
        print(
            f"{item.document_id:>3} {item.domain:<12} {item.input_words:>6} "
            f"{item.translated_words:>6} {item.coverage:9.0%}  {item.title}"
        )
    print("-" * 90)
    if results:
        mean = sum(item.coverage for item in results) / len(results)
        med = [item.coverage for item in results if item.domain == "medicine"]
        art = [item.coverage for item in results if item.domain == "art"]
        print(f"Среднее покрытие: {mean:.0%}")
        if med:
            print(f"  медицина: {sum(med)/len(med):.0%}")
        if art:
            print(f"  искусство: {sum(art)/len(art):.0%}")
    chart = pipeline.visualize_coverage(results)
    print(f"График покрытия: {chart}")
    for item in results:
        save_report(item, OUTPUT_DIR)
    print(f"Отчёты сохранены в {OUTPUT_DIR}\n")


def handle_dict(pipeline: TranslationPipeline, argument: str) -> None:
    command, _, rest = argument.partition(" ")
    command = command.lower().strip()
    rest = rest.strip()
    if command in {"", "list"}:
        rows = pipeline.dictionary.search(rest)
        print(f"\nСловарь ({pipeline.dictionary.size()} единиц), показ {len(rows)}:\n")
        for entry in rows:
            print(f"  {entry.source:<28} → {entry.target:<28} {entry.pos}")
        print()
        return
    if command == "pending":
        rows = pipeline.dictionary.pending()
        if not rows:
            print("Очередь неизвестных слов пуста.")
            return
        print("\nСлова вне словаря (автоочередь для пополнения):\n")
        for word, count in rows:
            print(f"  {count:>4}  {word}")
        print("\nДобавить: dict add word = перевод NN\n")
        return
    if command == "del":
        if pipeline.dictionary.delete(rest):
            print(f"Удалено: {rest}")
        else:
            print(f"Нет такой единицы: {rest}")
        return
    if command == "add":
        if "=" not in rest:
            print("Формат: dict add english phrase = русский перевод [POS]")
            return
        left, _, right = rest.partition("=")
        parts = right.strip().split()
        pos = ""
        if parts and parts[-1].isupper() and 2 <= len(parts[-1]) <= 5:
            pos = parts[-1]
            target = " ".join(parts[:-1])
        else:
            target = right.strip()
        pipeline.dictionary.add(left.strip(), target, pos)
        print(f"Записано: {left.strip()} → {target} {pos}".rstrip())
        return
    print("Подкоманды dict: list, add, del, pending")


def interactive_loop(pipeline: TranslationPipeline) -> None:
    show_help()
    while True:
        try:
            raw = input("mt> ").strip()
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
        elif command == "dict":
            handle_dict(pipeline, argument)
        elif command == "open":
            doc = resolve_document(pipeline, argument)
            if doc:
                open_path(doc.pdf_path)
        elif command == "show":
            doc = resolve_document(pipeline, argument)
            if doc:
                print_result(pipeline.translate_document(doc), sentence_index_from(argument))
        elif command == "tab1":
            doc = resolve_document(pipeline, argument)
            if doc:
                result = pipeline.translate_document(doc)
                print(f"\nВкладка 1. {result.title}\n")
                from src.translator import format_frequency_table
                print(format_frequency_table(result))
                print()
        elif command == "tab2":
            doc = resolve_document(pipeline, argument)
            if doc:
                result = pipeline.translate_document(doc)
                index = sentence_index_from(argument)
                from src.parser import parse_tree_pretty
                sentence = result.sentences[min(index, len(result.sentences) - 1)]
                print(f"\nВкладка 2. Предложение {index + 1}\n{sentence}\n")
                print(parse_tree_pretty(sentence))
                print()
        elif command == "translate":
            if not argument:
                print("Введите английский текст после команды.")
                continue
            if argument.isdigit() and int(argument) in pipeline.documents:
                print_result(pipeline.translate_document(pipeline.documents[int(argument)]))
            else:
                print_result(pipeline.translate_free(argument))
        elif command == "save":
            doc = resolve_document(pipeline, argument)
            if not doc:
                continue
            txt_path, html_path = save_report(
                pipeline.translate_document(doc), OUTPUT_DIR, sentence_index=sentence_index_from(argument)
            )
            print(f"Сохранено (UTF-8):\n  {txt_path}\n  {html_path}")
        elif command == "print":
            doc = resolve_document(pipeline, argument)
            if not doc:
                continue
            _, html_path = save_report(pipeline.translate_document(doc), OUTPUT_DIR)
            print_file(html_path)
        else:
            print("Неизвестная команда. Введите help.")


def run_demo(pipeline: TranslationPipeline) -> None:
    print("\n=== Демонстрация машинного перевода ===")
    print_collection(pipeline)
    for doc_id in (1, 4):
        doc = pipeline.documents.get(doc_id)
        if doc:
            print_result(pipeline.translate_document(doc))
    print_metrics(pipeline)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Машинный перевод EN→RU (вариант 7: медицина и художественная критика)."
    )
    parser.add_argument("--documents", default=DOCUMENTS_DIR, help="каталог документов")
    parser.add_argument("--dictionary", default=DICTIONARY_PATH, help="файл SQLite-словаря")
    parser.add_argument("--id", type=int, help="перевести документ и выйти")
    parser.add_argument("--text", help="перевести произвольный текст и выйти")
    parser.add_argument("--save", action="store_true", help="сохранить результат")
    parser.add_argument("--eval", action="store_true", help="только таблица покрытия")
    parser.add_argument("--demo", action="store_true", help="демонстрационный прогон")
    parser.add_argument("--no-interactive", action="store_true", help="не входить в консоль")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    pipeline = TranslationPipeline(os.path.abspath(args.documents), os.path.abspath(args.dictionary))
    print("Подготовка коллекции и словаря...")
    pipeline.run()
    print(
        f"Готово: документов={len(pipeline.documents)}, "
        f"единиц словаря={pipeline.dictionary.size()}"
    )

    if args.text:
        result = pipeline.translate_free(args.text)
        print_result(result)
        if args.save:
            print("Сохранено:", save_report(result, OUTPUT_DIR, prefix="free")[0])
        return 0
    if args.id:
        doc = pipeline.documents.get(args.id)
        if doc is None:
            print(f"Документа {args.id} нет.")
            return 1
        result = pipeline.translate_document(doc)
        print_result(result)
        if args.save:
            txt_path, html_path = save_report(result, OUTPUT_DIR)
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
