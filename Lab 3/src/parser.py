"""Синтаксическое дерево предложения (вкладка 2)."""

from __future__ import annotations

from src.utils import pos_tag, tokenize

CHUNK_GRAMMAR = r"""
NP: {<DT|PRP\$>?<JJ.*>*<NN.*>+}
PP: {<IN><NP>}
VP: {<MD>?<VB.*><RB>?<NP|PP|JJ.*>*}
CLAUSE: {<NP><VP>}
"""

_parser = None


def _get_parser():
    global _parser
    if _parser is not None:
        return _parser
    try:
        from nltk import RegexpParser
        _parser = RegexpParser(CHUNK_GRAMMAR)
    except (LookupError, ImportError):
        _parser = False
    return _parser


def parse_tree(sentence: str) -> str:
    tokens = tokenize(sentence)
    tagged = [(token, tag) for token, tag in pos_tag(tokens) if token.strip()]
    if not tagged:
        return "(пустое предложение)"
    parser = _get_parser()
    if parser:
        tree = parser.parse(tagged)
        return tree.pformat(margin=80)
    return _fallback_tree(tagged)


def parse_tree_pretty(sentence: str) -> str:
    tokens = tokenize(sentence)
    tagged = [(token, tag) for token, tag in pos_tag(tokens) if token.strip()]
    if not tagged:
        return "(пустое предложение)"
    parser = _get_parser()
    if not parser:
        return _fallback_tree(tagged)
    tree = parser.parse(tagged)
    try:
        from contextlib import redirect_stdout
        from io import StringIO

        buffer = StringIO()
        with redirect_stdout(buffer):
            tree.pretty_print()
        pretty = buffer.getvalue().rstrip()
        return pretty or tree.pformat(margin=80)
    except Exception:
        return tree.pformat(margin=80)


def _fallback_tree(tagged: list[tuple[str, str]]) -> str:
    leaves = " ".join(f"({tag} {token})" for token, tag in tagged)
    return f"(S {leaves})"


def html_tree(sentence: str) -> str:
    from html import escape
    return f"<pre>{escape(parse_tree_pretty(sentence))}</pre>"
