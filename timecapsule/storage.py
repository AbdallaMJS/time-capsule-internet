from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class StoredSnapshot:
    id: int
    site_key: str
    title: str
    requested_url: str
    final_url: str
    captured_at: str
    png: bytes
    phash: str
    html_hash: str
    html_length: int


class SnapshotStore:
    def __init__(self, db_path: str | Path = "data/time_capsule.db") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    site_key TEXT NOT NULL,
                    title TEXT NOT NULL,
                    requested_url TEXT NOT NULL,
                    final_url TEXT NOT NULL,
                    captured_at TEXT NOT NULL,
                    png BLOB NOT NULL,
                    phash TEXT NOT NULL,
                    html_hash TEXT NOT NULL,
                    html_length INTEGER NOT NULL
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_snapshots_site_time ON snapshots(site_key, captured_at)"
            )

    def add(self, snapshot: dict) -> int:
        captured_at = snapshot.get("timestamp") or datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO snapshots (
                    site_key, title, requested_url, final_url, captured_at,
                    png, phash, html_hash, html_length
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    snapshot["site_key"],
                    snapshot["title"],
                    snapshot["requested_url"],
                    snapshot["final_url"],
                    captured_at,
                    snapshot["png"],
                    snapshot["phash"],
                    snapshot["html_hash"],
                    snapshot["html_length"],
                ),
            )
            return int(cur.lastrowid)

    def list_sites(self) -> list[str]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT DISTINCT site_key FROM snapshots ORDER BY site_key"
            ).fetchall()
        return [row["site_key"] for row in rows]

    def list_snapshots(self, site_key: str) -> list[StoredSnapshot]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM snapshots WHERE site_key=? ORDER BY captured_at, id",
                (site_key,),
            ).fetchall()
        return [StoredSnapshot(**dict(row)) for row in rows]

    def delete_site(self, site_key: str) -> int:
        with self._connect() as conn:
            cur = conn.execute("DELETE FROM snapshots WHERE site_key=?", (site_key,))
            return int(cur.rowcount)
