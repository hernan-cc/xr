"""SQLite cache for API responses."""
from __future__ import annotations
import hashlib
import json
import os
import sqlite3
import time
from pathlib import Path
from typing import Any

def _cache_path() -> Path:
    xdg = os.environ.get("XDG_CACHE_HOME", str(Path.home() / ".cache"))
    return Path(xdg) / "xr" / "cache.db"

class Cache:
    def __init__(self, path: Path | None = None, enabled: bool = True):
        self.enabled = enabled
        self.path = path or _cache_path()
        if self.enabled:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.conn = sqlite3.connect(str(self.path))
            self._init_tables()
        else:
            self.conn = None

    def _init_tables(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS tweets (
                tweet_id TEXT PRIMARY KEY,
                data TEXT NOT NULL,
                fetched_at REAL NOT NULL
            );
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT UNIQUE,
                data TEXT NOT NULL,
                fetched_at REAL NOT NULL
            );
            CREATE TABLE IF NOT EXISTS searches (
                query_hash TEXT PRIMARY KEY,
                query TEXT NOT NULL,
                result_ids TEXT NOT NULL,
                fetched_at REAL NOT NULL
            );
            CREATE TABLE IF NOT EXISTS counts (
                query_hash TEXT PRIMARY KEY,
                query TEXT NOT NULL,
                granularity TEXT NOT NULL,
                data TEXT NOT NULL,
                fetched_at REAL NOT NULL
            );
        """)

    def _is_fresh(self, fetched_at: float, ttl: int) -> bool:
        return (time.time() - fetched_at) < ttl

    def _query_hash(self, query: str) -> str:
        return hashlib.sha256(query.strip().lower().encode()).hexdigest()

    # --- Tweets ---
    def get_tweet(self, tweet_id: str, ttl: int) -> dict | None:
        if not self.enabled or not self.conn:
            return None
        row = self.conn.execute(
            "SELECT data, fetched_at FROM tweets WHERE tweet_id = ?", (tweet_id,)
        ).fetchone()
        if row and self._is_fresh(row[1], ttl):
            return json.loads(row[0])
        return None

    def put_tweet(self, tweet_id: str, data: dict):
        if not self.enabled or not self.conn:
            return
        self.conn.execute(
            "INSERT OR REPLACE INTO tweets (tweet_id, data, fetched_at) VALUES (?, ?, ?)",
            (tweet_id, json.dumps(data), time.time()),
        )
        self.conn.commit()

    # --- Users ---
    def get_user(self, username: str, ttl: int) -> dict | None:
        if not self.enabled or not self.conn:
            return None
        row = self.conn.execute(
            "SELECT data, fetched_at FROM users WHERE username = ?", (username,)
        ).fetchone()
        if row and self._is_fresh(row[1], ttl):
            return json.loads(row[0])
        return None

    def put_user(self, user_id: str, username: str, data: dict):
        if not self.enabled or not self.conn:
            return
        self.conn.execute(
            "INSERT OR REPLACE INTO users (user_id, username, data, fetched_at) VALUES (?, ?, ?, ?)",
            (user_id, username, json.dumps(data), time.time()),
        )
        self.conn.commit()

    # --- Searches ---
    def get_search(self, query: str, ttl: int) -> list[str] | None:
        if not self.enabled or not self.conn:
            return None
        qh = self._query_hash(query)
        row = self.conn.execute(
            "SELECT result_ids, fetched_at FROM searches WHERE query_hash = ?", (qh,)
        ).fetchone()
        if row and self._is_fresh(row[1], ttl):
            return json.loads(row[0])
        return None

    def put_search(self, query: str, result_ids: list[str]):
        if not self.enabled or not self.conn:
            return
        qh = self._query_hash(query)
        self.conn.execute(
            "INSERT OR REPLACE INTO searches (query_hash, query, result_ids, fetched_at) VALUES (?, ?, ?, ?)",
            (qh, query, json.dumps(result_ids), time.time()),
        )
        self.conn.commit()

    # --- Counts ---
    def get_counts(self, query: str, granularity: str, ttl: int) -> dict | None:
        if not self.enabled or not self.conn:
            return None
        qh = self._query_hash(f"{query}:{granularity}")
        row = self.conn.execute(
            "SELECT data, fetched_at FROM counts WHERE query_hash = ?", (qh,)
        ).fetchone()
        if row and self._is_fresh(row[1], ttl):
            return json.loads(row[0])
        return None

    def put_counts(self, query: str, granularity: str, data: dict):
        if not self.enabled or not self.conn:
            return
        qh = self._query_hash(f"{query}:{granularity}")
        self.conn.execute(
            "INSERT OR REPLACE INTO counts (query_hash, query, granularity, data, fetched_at) VALUES (?, ?, ?, ?, ?)",
            (qh, query, granularity, json.dumps(data), time.time()),
        )
        self.conn.commit()

    def cleanup(self, max_size_mb: int = 50):
        """Remove old entries if cache exceeds max size."""
        if not self.enabled or not self.conn:
            return
        size = self.path.stat().st_size / (1024 * 1024) if self.path.exists() else 0
        if size > max_size_mb:
            for table in ("tweets", "searches", "users", "counts"):
                self.conn.execute(f"""
                    DELETE FROM {table} WHERE rowid IN (
                        SELECT rowid FROM {table} ORDER BY fetched_at ASC
                        LIMIT (SELECT COUNT(*) / 2 FROM {table})
                    )
                """)
            self.conn.commit()
            self.conn.execute("VACUUM")
