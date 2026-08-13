# ============================================================
# Destiny Memory Layer – thin SQLite-backed store for the stick
# ============================================================
from __future__ import annotations

import sqlite3
import time
from pathlib import Path
from typing import Any, Iterable


class DestinyLayer:
    """Minimal destiny memory API used by demo/system start scripts."""

    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        con = sqlite3.connect(str(self.db_path))
        con.row_factory = sqlite3.Row
        return con

    def _init_db(self) -> None:
        with self._connect() as con:
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts REAL NOT NULL,
                    kind TEXT NOT NULL,
                    key TEXT NOT NULL,
                    value TEXT NOT NULL
                )
                """
            )
            con.execute(
                "CREATE INDEX IF NOT EXISTS idx_memories_key ON memories(key)"
            )
            con.commit()

    def put(self, key: str, value: str, kind: str = "note") -> None:
        with self._connect() as con:
            con.execute(
                "INSERT INTO memories(ts, kind, key, value) VALUES (?,?,?,?)",
                (time.time(), kind, key, value),
            )
            con.commit()

    def get(self, key: str, limit: int = 20) -> list[dict[str, Any]]:
        with self._connect() as con:
            rows = con.execute(
                "SELECT ts, kind, key, value FROM memories WHERE key=? ORDER BY id DESC LIMIT ?",
                (key, limit),
            ).fetchall()
        return [dict(r) for r in rows]

    def stats(self) -> dict[str, Any]:
        with self._connect() as con:
            n = con.execute("SELECT COUNT(*) AS c FROM memories").fetchone()["c"]
        return {"db": str(self.db_path), "entries": n}


def bootstrap_demo_db(db_path: str | Path) -> DestinyLayer:
    layer = DestinyLayer(db_path)
    if layer.stats()["entries"] == 0:
        layer.put("system", "GoldGabel stick initialized", kind="boot")
        layer.put("ownership", "Owner NOVA system package – demo memory", kind="meta")
    return layer


if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    db = root / "destiny_memory.sqlite"
    layer = bootstrap_demo_db(db)
    print(layer.stats())
