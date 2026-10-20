"""SQLite metadata store (stand-in for the Documentum repository / xECM business workspace)."""

import json
import sqlite3
import uuid
from datetime import datetime, timezone

from app.config import settings


def _conn() -> sqlite3.Connection:
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(settings.data_dir / "meta.db")
    conn.row_factory = sqlite3.Row
    conn.execute(
        """CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY, filename TEXT, access_level TEXT,
            doc_type TEXT, summary TEXT, fields TEXT, chunks INTEGER, created_at TEXT)"""
    )
    return conn


def insert_document(filename, access_level, doc_type, summary, fields, chunks) -> dict:
    doc = {
        "id": uuid.uuid4().hex,
        "filename": filename,
        "access_level": access_level,
        "doc_type": doc_type,
        "summary": summary,
        "fields": fields,
        "chunks": chunks,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    with _conn() as c:
        c.execute(
            "INSERT INTO documents VALUES (?,?,?,?,?,?,?,?)",
            (doc["id"], filename, access_level, doc_type, summary,
             json.dumps(fields), chunks, doc["created_at"]),
        )
    return doc


def list_documents(levels: list[str] | None = None) -> list[dict]:
    with _conn() as c:
        rows = c.execute("SELECT * FROM documents ORDER BY created_at DESC").fetchall()
    docs = [{**dict(r), "fields": json.loads(r["fields"])} for r in rows]
    if levels is not None:
        docs = [d for d in docs if d["access_level"] in levels]
    return docs
