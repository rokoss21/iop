import sqlite3
import time
from pathlib import Path
from typing import Optional

import utils

_DB_PATH: Path = utils.get_config_dir() / "cache.db"

_CREATE_SQL = """
CREATE TABLE IF NOT EXISTS responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model TEXT NOT NULL,
    query TEXT NOT NULL,
    response TEXT NOT NULL,
    timestamp REAL NOT NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_query_model ON responses(model, query);
"""


def _get_conn() -> sqlite3.Connection:
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(_DB_PATH)
    conn.executescript(_CREATE_SQL)
    return conn


def get_cached_response(model: str, query: str, max_age_hours: int = 24) -> Optional[str]:
    conn = _get_conn()
    cur = conn.execute(
        "SELECT response, timestamp FROM responses WHERE model=? AND query=?",
        (model, query),
    )
    row = cur.fetchone()
    conn.close()
    if row:
        resp, ts = row
        if (time.time() - ts) <= max_age_hours * 3600:
            return resp
    return None


def store_response(model: str, query: str, response: str) -> None:
    conn = _get_conn()
    conn.execute(
        "INSERT OR REPLACE INTO responses(model, query, response, timestamp) VALUES(?,?,?,?)",
        (model, query, response, time.time()),
    )
    conn.commit()
    conn.close()