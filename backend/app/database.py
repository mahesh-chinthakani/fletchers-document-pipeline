import sqlite3
from pathlib import Path


DATABASE_PATH = Path(__file__).resolve().parent.parent / "documents.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db():
    with get_connection() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                file_type TEXT NOT NULL,
                status TEXT NOT NULL,
                extraction_method TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                error_message TEXT
            );

            CREATE TABLE IF NOT EXISTS document_chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id TEXT NOT NULL,
                sequence_number INTEGER NOT NULL,
                page_number INTEGER,
                content TEXT NOT NULL,
                FOREIGN KEY (document_id)
                    REFERENCES documents(id)
                    ON DELETE CASCADE
            );
            """
        )


def create_document(document_id: str, filename: str, file_type: str):
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO documents (id, filename, file_type, status)
            VALUES (?, ?, ?, ?)
            """,
            (document_id, filename, file_type, "processing"),
        )


def update_document_status(
    document_id: str,
    status: str,
    extraction_method: str | None = None,
    error_message: str | None = None,
):
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE documents
            SET status = ?,
                extraction_method = ?,
                error_message = ?
            WHERE id = ?
            """,
            (
                status,
                extraction_method,
                error_message,
                document_id,
            ),
        )


def add_document_chunk(
    document_id: str,
    sequence_number: int,
    content: str,
    page_number: int | None = None,
):
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO document_chunks (
                document_id,
                sequence_number,
                page_number,
                content
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                document_id,
                sequence_number,
                page_number,
                content,
            ),
        )


def get_document(document_id: str):
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT *
            FROM documents
            WHERE id = ?
            """,
            (document_id,),
        ).fetchone()

    return dict(row) if row else None


def get_document_chunks(document_id: str):
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT sequence_number, page_number, content
            FROM document_chunks
            WHERE document_id = ?
            ORDER BY sequence_number
            """,
            (document_id,),
        ).fetchall()

    return [dict(row) for row in rows]