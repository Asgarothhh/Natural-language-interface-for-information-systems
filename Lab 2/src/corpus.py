"""Тестовая коллекция варианта 7: EN/FR, computer science и литература.

Основные тексты загружаются из Wikipedia (как допускает методичка) и
приводятся к сопоставимому объёму ~10 страниц A4. Если сети нет,
используются встроенные эссе того же состава по языкам и темам.
"""

from __future__ import annotations

import json
import os
import re
import textwrap
import urllib.error
import urllib.parse
import urllib.request
from typing import Sequence

import pymupdf

from src.fallback_texts import FALLBACK_CORPUS

TARGET_CHARS = 42_000
MIN_CHARS = 28_000

FONT_REGULAR = "/usr/share/fonts/TTF/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf"

SOURCES: Sequence[dict] = (
    {
        "filename": "01_en_cs_artificial_intelligence.pdf",
        "language": "english",
        "domain": "computer science",
        "wiki_lang": "en",
        "wiki_title": "Artificial intelligence",
    },
    {
        "filename": "02_en_cs_operating_system.pdf",
        "language": "english",
        "domain": "computer science",
        "wiki_lang": "en",
        "wiki_title": "Operating system",
    },
    {
        "filename": "03_en_lit_hamlet.pdf",
        "language": "english",
        "domain": "literature",
        "wiki_lang": "en",
        "wiki_title": "Hamlet",
    },
    {
        "filename": "04_en_lit_romanticism.pdf",
        "language": "english",
        "domain": "literature",
        "wiki_lang": "en",
        "wiki_title": "Romanticism",
    },
    {
        "filename": "05_fr_cs_intelligence_artificielle.pdf",
        "language": "french",
        "domain": "computer science",
        "wiki_lang": "fr",
        "wiki_title": "Intelligence artificielle",
    },
    {
        "filename": "06_fr_cs_base_de_donnees.pdf",
        "language": "french",
        "domain": "computer science",
        "wiki_lang": "fr",
        "wiki_title": "Base de données",
    },
    {
        "filename": "07_fr_lit_les_miserables.pdf",
        "language": "french",
        "domain": "literature",
        "wiki_lang": "fr",
        "wiki_title": "Les Misérables",
    },
    {
        "filename": "08_fr_lit_letranger.pdf",
        "language": "french",
        "domain": "literature",
        "wiki_lang": "fr",
        "wiki_title": "L'Étranger",
    },
)

RELATED_PAGES = {
    "Base de données": ("Système de gestion de base de données", "fr"),
    "L'Étranger": ("Albert Camus", "fr"),
}

TAIL_MARKERS = (
    "\n== See also ==",
    "\n== References ==",
    "\n== Notes ==",
    "\n== Notes and references ==",
    "\n== External links ==",
    "\n== Further reading ==",
    "\n== Bibliography ==",
    "\n== Sources ==",
    "\n== Voir aussi ==",
    "\n== Notes et références ==",
    "\n== Références ==",
    "\n== Bibliographie ==",
    "\n== Annexes ==",
    "\n== Liens externes ==",
    "\n== Notes et références",
)


def _font_pair() -> tuple[str | None, str | None]:
    regular = FONT_REGULAR if os.path.exists(FONT_REGULAR) else None
    bold = FONT_BOLD if os.path.exists(FONT_BOLD) else None
    return regular, bold


def clean_wikipedia(extract: str) -> tuple[str, str]:
    text = extract.replace("\r\n", "\n")
    text = re.sub(r"\[\d+\]", "", text)
    text = re.sub(r"\[citation needed\]", "", text, flags=re.I)
    cut_at = len(text)
    for marker in TAIL_MARKERS:
        pos = text.find(marker)
        if pos != -1:
            cut_at = min(cut_at, pos)
    text = text[:cut_at]
    lead_match = re.split(r"\n={2,}[^=\n].*={2,}\n", text, maxsplit=1)
    reference = lead_match[0].strip()
    text = re.sub(r"^={2,}\s*(.+?)\s*={2,}\s*$", r"\n\n\1.\n\n", text, flags=re.M)
    text = re.sub(r"^\*\s+", "", text, flags=re.M)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text, reference


def clip_to_size(text: str, target: int = TARGET_CHARS) -> str:
    if len(text) <= target:
        return text
    window = text[:target]
    cut = window.rfind("\n\n")
    if cut < target * 0.72:
        cut = window.rfind(". ")
        cut = cut + 1 if cut != -1 else target
    return text[:cut].strip()


def fetch_wikipedia(title: str, lang: str) -> tuple[str, str, str]:
    query = urllib.parse.urlencode(
        {
            "action": "query",
            "prop": "extracts",
            "explaintext": 1,
            "exsectionformat": "plain",
            "redirects": 1,
            "format": "json",
            "titles": title,
        }
    )
    url = f"https://{lang}.wikipedia.org/w/api.php?{query}"
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Lab2Summarizer/1.0 (university coursework)"},
    )
    with urllib.request.urlopen(request, timeout=40) as response:
        payload = json.loads(response.read().decode("utf-8"))
    pages = payload["query"]["pages"]
    page = next(iter(pages.values()))
    extract = page.get("extract") or ""
    page_title = page.get("title") or title
    if len(extract) < 800:
        raise RuntimeError(f"Слишком короткий extract: {title}")
    body, reference = clean_wikipedia(extract)
    extra = RELATED_PAGES.get(page_title) or RELATED_PAGES.get(title)
    if extra and len(body) < TARGET_CHARS:
        extra_title, extra_lang = extra
        try:
            extra_query = urllib.parse.urlencode(
                {
                    "action": "query",
                    "prop": "extracts",
                    "explaintext": 1,
                    "exsectionformat": "plain",
                    "redirects": 1,
                    "format": "json",
                    "titles": extra_title,
                }
            )
            extra_url = f"https://{extra_lang}.wikipedia.org/w/api.php?{extra_query}"
            extra_req = urllib.request.Request(
                extra_url,
                headers={"User-Agent": "Lab2Summarizer/1.0 (university coursework)"},
            )
            with urllib.request.urlopen(extra_req, timeout=40) as extra_resp:
                extra_payload = json.loads(extra_resp.read().decode("utf-8"))
            extra_page = next(iter(extra_payload["query"]["pages"].values()))
            extra_body, _ = clean_wikipedia(extra_page.get("extract") or "")
            body = body + "\n\n" + extra_body
        except (urllib.error.URLError, TimeoutError, RuntimeError, KeyError, json.JSONDecodeError, OSError):
            pass
    return page_title, clip_to_size(body), reference


def _new_page(doc: pymupdf.Document, regular: str | None, bold: str | None) -> pymupdf.Page:
    page = doc.new_page(width=595, height=842)
    if regular:
        page.insert_font(fontname="body", fontfile=regular)
    if bold:
        page.insert_font(fontname="bold", fontfile=bold)
    return page


def write_pdf(path: str, title: str, body: str) -> None:
    regular, bold = _font_pair()
    body_font = "body" if regular else "helv"
    title_font = "bold" if bold else "hebo"
    doc = pymupdf.open()
    page = _new_page(doc, regular, bold)
    y = 56
    for line in textwrap.wrap(title, width=70) or [title]:
        page.insert_text((50, y), line, fontsize=14, fontname=title_font)
        y += 20
    y += 10
    for paragraph in body.split("\n\n"):
        wrapped = textwrap.wrap(paragraph, width=92) or [""]
        for line in wrapped:
            if y > 800:
                page = _new_page(doc, regular, bold)
                y = 56
            page.insert_text((50, y), line, fontsize=11, fontname=body_font)
            y += 14
        y += 8
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    doc.save(path)
    doc.close()


def _raw_path(raw_dir: str, filename: str) -> str:
    return os.path.join(raw_dir, filename.replace(".pdf", ".txt"))


def _load_cached(raw_dir: str, filename: str) -> tuple[str, str, str] | None:
    path = _raw_path(raw_dir, filename)
    meta_path = path + ".meta.json"
    if not os.path.exists(path) or not os.path.exists(meta_path):
        return None
    with open(path, encoding="utf-8") as file:
        body = file.read()
    with open(meta_path, encoding="utf-8") as file:
        meta = json.load(file)
    if len(body) < 800:
        return None
    return meta.get("title", filename), body, meta.get("reference", "")


def _store_cached(raw_dir: str, filename: str, title: str, body: str, reference: str) -> None:
    os.makedirs(raw_dir, exist_ok=True)
    path = _raw_path(raw_dir, filename)
    with open(path, "w", encoding="utf-8") as file:
        file.write(body)
    with open(path + ".meta.json", "w", encoding="utf-8") as file:
        json.dump({"title": title, "reference": reference}, file, ensure_ascii=False, indent=2)


def _fallback_for(filename: str) -> dict:
    for item in FALLBACK_CORPUS:
        if item["filename"] == filename:
            return item
    raise KeyError(filename)


def prepare_document(source: dict, documents_dir: str, raw_dir: str) -> dict:
    cached = _load_cached(raw_dir, source["filename"])
    if cached:
        title, body, reference = cached
    else:
        title, body, reference = source["wiki_title"], "", ""
        try:
            title, body, reference = fetch_wikipedia(source["wiki_title"], source["wiki_lang"])
        except (urllib.error.URLError, TimeoutError, RuntimeError, KeyError, json.JSONDecodeError, OSError):
            fallback = _fallback_for(source["filename"])
            title = fallback["title"]
            body = fallback["body"]
            reference = fallback["reference"]
        _store_cached(raw_dir, source["filename"], title, body, reference)

    pdf_path = os.path.join(documents_dir, source["filename"])
    if not os.path.exists(pdf_path):
        write_pdf(pdf_path, title, body)
    return {
        "path": pdf_path,
        "title": title,
        "language": source["language"],
        "domain": source["domain"],
        "reference": reference or body.split("\n\n")[0],
        "chars": len(body),
        "body": body,
    }


def ensure_corpus(documents_dir: str) -> list[dict]:
    os.makedirs(documents_dir, exist_ok=True)
    raw_dir = os.path.join(os.path.dirname(documents_dir), "raw")
    records = []
    for source in SOURCES:
        records.append(prepare_document(source, documents_dir, raw_dir))
    return records
