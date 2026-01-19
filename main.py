from fastapi import FastAPI, HTTPException, Query
import sqlite3
import json

app = FastAPI(
    title="Faculty Finder API",
    description="API to serve faculty data for analytics and embeddings",
    version="1.0.0"
)

DB_NAME = "faculty.db"


def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def parse_json_fields(record: dict):
    """Convert JSON string fields back to Python objects"""
    json_fields = [
        "education",
        "biography",
        "specialization",
        "teaching",
        "publications",
        "research"
    ]

    for field in json_fields:
        if record.get(field):
            try:
                record[field] = json.loads(record[field])
            except Exception:
                record[field] = []
        else:
            record[field] = []

    return record


# GET: All Faculty
@app.get("/faculty")
def get_all_faculty(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0)
):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM faculty LIMIT ? OFFSET ?",
        (limit, offset)
    )
    rows = cursor.fetchall()
    conn.close()

    faculty = []
    for row in rows:
        record = dict(row)
        record = parse_json_fields(record)
        faculty.append(record)

    return {
        "count": len(faculty),
        "limit": limit,
        "offset": offset,
        "data": faculty
    }


# GET: Faculty by ID
@app.get("/faculty/{faculty_id}")
def get_faculty_by_id(faculty_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM faculty WHERE id = ?",
        (faculty_id,)
    )
    row = cursor.fetchone()
    conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail="Faculty not found")

    record = parse_json_fields(dict(row))
    return record

# GET: Search Faculty
@app.get("/faculty/search")
def search_faculty(
    q: str = Query(..., min_length=2)
):
    conn = get_db_connection()
    cursor = conn.cursor()

    wildcard = f"%{q.lower()}%"

    cursor.execute("""
        SELECT * FROM faculty
        WHERE
            LOWER(name) LIKE ?
            OR LOWER(specialization) LIKE ?
            OR LOWER(text_for_embedding) LIKE ?
    """, (wildcard, wildcard, wildcard))

    rows = cursor.fetchall()
    conn.close()

    results = []
    for row in rows:
        record = parse_json_fields(dict(row))
        results.append(record)

    return {
        "query": q,
        "count": len(results),
        "data": results
    }