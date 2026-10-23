"""Persistence. SQLite, one file per environment."""
import sqlite3
from datetime import datetime, timezone

from .models import AuditRun, Finding

SCHEMA = """
CREATE TABLE IF NOT EXISTS audit_run (
    run_id      TEXT PRIMARY KEY,
    item_id     TEXT NOT NULL,
    brand_id    TEXT NOT NULL,
    status      TEXT NOT NULL,
    started_at  TEXT,
    finished_at TEXT
);

CREATE TABLE IF NOT EXISTS finding (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id      TEXT NOT NULL,
    rule_id     TEXT NOT NULL,
    verdict     TEXT NOT NULL,
    evidence    TEXT NOT NULL,
    confidence  REAL NOT NULL,
    written_at  TEXT NOT NULL
);
"""


def connect(path: str = "audit.db") -> sqlite3.Connection:
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.executescript(SCHEMA)
    return conn


def start_run(conn: sqlite3.Connection, run: AuditRun) -> None:
    conn.execute(
        "INSERT OR IGNORE INTO audit_run (run_id, item_id, brand_id, status, started_at) "
        "VALUES (?, ?, ?, 'running', ?)",
        (run.run_id, run.item.item_id, run.item.brand_id,
         datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()


def write_findings(conn: sqlite3.Connection, run_id: str, findings: list[Finding]) -> None:
    """Persist the findings for one audit run.

    TODO — this is the part we're adding together.

    Requirements:
      * Safe to call twice. The pipeline retries, and a step can re-execute
        after a crash. Running it twice must leave one set of findings.
      * Handles partial failure. Some findings written, then the store errors.
      * Observable. Someone debugging at 3am can tell what happened.
      * Tested.
    """
    raise NotImplementedError


def read_findings(conn: sqlite3.Connection, run_id: str) -> list[Finding]:
    rows = conn.execute(
        "SELECT rule_id, verdict, evidence, confidence FROM finding WHERE run_id = ?",
        (run_id,),
    ).fetchall()
    return [Finding(rule_id=r[0], verdict=r[1], evidence=r[2], confidence=r[3]) for r in rows]
