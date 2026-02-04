"""
main.py

FastAPI application serving faculty data from SQLite database.

All database paths are sourced from the central config module to ensure
consistency across the data pipeline and model layers.
"""

import sqlite3
import json
from pathlib import Path
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException, Query

from config.base import DB_PATH


# -------------------- APP FACTORY --------------------

def create_app(db_path: Path) -> FastAPI:
    """
    Create and configure the FastAPI application.

    Args:
        db_path (Path): Path to SQLite database

    Returns:
        FastAPI: Configured FastAPI app
    """
    app = FastAPI(
        title="Faculty Finder API",
        description="API to serve faculty data for analytics and embeddings",
        version="1.1.0",
    )

    # -------------------- DB UTILS --------------------

    def get_db_connection() -> sqlite3.Connection:
        """
        Create a SQLite connection with row factory enabled.
        """
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def parse_json_fields(record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse JSON-encoded list fields stored as TEXT in SQLite.
        """
        json_fields = [
            "education",
            "biography",
            "specialization",
            "teaching",
            "publications",
            "research",
        ]

        for field in json_fields:
            try:
                record[field] = json.loads(record[field]) if record[field] else []
            except Exception:
                record[field] = []

        return record

    # -------------------- API ENDPOINTS --------------------

    @app.get("/faculty")
    def get_all_faculty(
        faculty_type: Optional[str] = Query(None),
        limit: int = Query(100, ge=1, le=500),
        offset: int = Query(0, ge=0),
    ):
        """
        Fetch all faculty records with optional filtering and pagination.
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        if faculty_type:
            cursor.execute(
                """
                SELECT * FROM faculty
                WHERE faculty_type = ?
                LIMIT ? OFFSET ?
                """,
                (faculty_type, limit, offset),
            )
        else:
            cursor.execute(
                """
                SELECT * FROM faculty
                LIMIT ? OFFSET ?
                """,
                (limit, offset),
            )

        rows = cursor.fetchall()
        conn.close()

        return {
            "count": len(rows),
            "data": [parse_json_fields(dict(r)) for r in rows],
        }

    @app.get("/faculty/search")
    def search_faculty(
        q: str = Query(..., min_length=2),
        faculty_type: Optional[str] = Query(None),
    ):
        """
        Search faculty by name or embedding text.
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        wildcard = f"%{q.lower()}%"

        if faculty_type:
            cursor.execute(
                """
                SELECT * FROM faculty
                WHERE faculty_type = ?
                  AND (
                    LOWER(name) LIKE ?
                    OR LOWER(text_for_embedding) LIKE ?
                  )
                """,
                (faculty_type, wildcard, wildcard),
            )
        else:
            cursor.execute(
                """
                SELECT * FROM faculty
                WHERE
                    LOWER(name) LIKE ?
                    OR LOWER(text_for_embedding) LIKE ?
                """,
                (wildcard, wildcard),
            )

        rows = cursor.fetchall()
        conn.close()

        return {
            "query": q,
            "count": len(rows),
            "data": [parse_json_fields(dict(r)) for r in rows],
        }

    @app.get("/faculty/{faculty_id}")
    def get_faculty_by_id(faculty_id: int):
        """
        Fetch a single faculty record by ID.
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM faculty WHERE id = ?",
            (faculty_id,),
        )
        row = cursor.fetchone()
        conn.close()

        if not row:
            raise HTTPException(
                status_code=404,
                detail="Faculty not found",
            )

        return parse_json_fields(dict(row))

    return app


# -------------------- APP ENTRYPOINT --------------------

app = create_app(DB_PATH)
