"""SQLite-словарь с посевом, правкой и очередью неизвестных слов."""

from __future__ import annotations

import os
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone

from src.lexicon import SEED


@dataclass
class Entry:
    source: str
    target: str
    pos: str
    updated_at: str


class Dictionary:
    def __init__(self, path: str):
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        self.path = path
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()
        self._seed_if_empty()
        self._phrases: list[str] | None = None

    def _init_schema(self) -> None:
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS words (
                source TEXT PRIMARY KEY COLLATE NOCASE,
                target TEXT NOT NULL,
                pos TEXT NOT NULL DEFAULT '',
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS pending (
                source TEXT PRIMARY KEY COLLATE NOCASE,
                count INTEGER NOT NULL DEFAULT 1
            );
            """
        )
        self.conn.commit()

    def _seed_if_empty(self) -> None:
        count = self.conn.execute("SELECT COUNT(*) FROM words").fetchone()[0]
        if count:
            return
        now = _now()
        self.conn.executemany(
            "INSERT OR IGNORE INTO words(source, target, pos, updated_at) VALUES (?, ?, ?, ?)",
            [(src, tgt, pos, now) for src, tgt, pos in SEED],
        )
        self.conn.commit()
        self._phrases = None

    def lookup(self, phrase: str) -> Entry | None:
        row = self.conn.execute(
            "SELECT source, target, pos, updated_at FROM words WHERE source = ? COLLATE NOCASE",
            (phrase,),
        ).fetchone()
        if row is None:
            return None
        return Entry(row["source"], row["target"], row["pos"], row["updated_at"])

    def longest_match(self, tokens: list[str], index: int, max_n: int = 4) -> tuple[int, Entry] | None:
        limit = min(max_n, len(tokens) - index)
        for length in range(limit, 0, -1):
            phrase = " ".join(tokens[index:index + length])
            entry = self.lookup(phrase)
            if entry is not None:
                return length, entry
        return None

    def add(self, source: str, target: str, pos: str = "") -> None:
        source = source.strip()
        target = target.strip()
        if not source:
            raise ValueError("Пустая исходная единица")
        now = _now()
        self.conn.execute(
            """
            INSERT INTO words(source, target, pos, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(source) DO UPDATE SET
                target = excluded.target,
                pos = CASE WHEN excluded.pos = '' THEN words.pos ELSE excluded.pos END,
                updated_at = excluded.updated_at
            """,
            (source, target, pos, now),
        )
        self.conn.execute("DELETE FROM pending WHERE source = ? COLLATE NOCASE", (source,))
        self.conn.commit()
        self._phrases = None

    def delete(self, source: str) -> bool:
        cursor = self.conn.execute(
            "DELETE FROM words WHERE source = ? COLLATE NOCASE", (source.strip(),)
        )
        self.conn.commit()
        self._phrases = None
        return cursor.rowcount > 0

    def note_unknown(self, source: str) -> None:
        self.conn.execute(
            """
            INSERT INTO pending(source, count) VALUES (?, 1)
            ON CONFLICT(source) DO UPDATE SET count = pending.count + 1
            """,
            (source,),
        )
        self.conn.commit()

    def pending(self, limit: int = 40) -> list[tuple[str, int]]:
        rows = self.conn.execute(
            "SELECT source, count FROM pending ORDER BY count DESC, source LIMIT ?",
            (limit,),
        ).fetchall()
        return [(row["source"], row["count"]) for row in rows]

    def search(self, query: str = "", limit: int = 30) -> list[Entry]:
        if query:
            rows = self.conn.execute(
                """
                SELECT source, target, pos, updated_at FROM words
                WHERE source LIKE ? COLLATE NOCASE OR target LIKE ?
                ORDER BY length(source), source
                LIMIT ?
                """,
                (f"%{query}%", f"%{query}%", limit),
            ).fetchall()
        else:
            rows = self.conn.execute(
                "SELECT source, target, pos, updated_at FROM words ORDER BY source LIMIT ?",
                (limit,),
            ).fetchall()
        return [Entry(row["source"], row["target"], row["pos"], row["updated_at"]) for row in rows]

    def size(self) -> int:
        return int(self.conn.execute("SELECT COUNT(*) FROM words").fetchone()[0])

    def close(self) -> None:
        self.conn.close()


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
