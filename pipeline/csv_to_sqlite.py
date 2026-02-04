"""
csv_to_sqlite.py

Load cleaned faculty CSV data into a SQLite database.
This step refreshes the faculty table on every run.

All input/output paths are sourced from the central config module.
"""

import sqlite3
from pathlib import Path

import pandas as pd

from config.base import CLEAN_CSV_PATH, DB_PATH


# -------------------- DATABASE SCHEMA --------------------

TABLE_SCHEMA = """
CREATE TABLE IF NOT EXISTS faculty (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    profile_url TEXT,
    email TEXT UNIQUE,
    phone TEXT,
    address TEXT,
    faculty_web TEXT,
    education TEXT,
    biography TEXT,
    specialization TEXT,
    teaching TEXT,
    publications TEXT,
    research TEXT,
    text_for_embedding TEXT,
    source_file TEXT,
    faculty_type TEXT
)
"""


# -------------------- DB UTILS --------------------

def create_database(db_path: Path) -> sqlite3.Connection:
    """
    Create (or connect to) a SQLite database and ensure schema exists.

    Args:
        db_path (Path): Path to SQLite DB

    Returns:
        sqlite3.Connection: Active DB connection
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(TABLE_SCHEMA)
    conn.commit()
    return conn


def truncate_faculty_table(conn: sqlite3.Connection) -> None:
    """
    Remove all existing records from the faculty table.

    Args:
        conn (sqlite3.Connection): DB connection
    """
    cursor = conn.cursor()
    cursor.execute("DELETE FROM faculty")
    conn.commit()


def insert_faculty_data(
    conn: sqlite3.Connection,
    df: pd.DataFrame
) -> int:
    """
    Insert faculty records into the database.

    Args:
        conn (sqlite3.Connection): DB connection
        df (pd.DataFrame): Cleaned faculty data

    Returns:
        int: Number of records inserted
    """
    cursor = conn.cursor()

    insert_query = """
    INSERT INTO faculty (
        name, profile_url, email, phone, address, faculty_web,
        education, biography, specialization, teaching,
        publications, research, text_for_embedding,
        source_file, faculty_type
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    for _, row in df.iterrows():
        cursor.execute(
            insert_query,
            (
                row.get("name"),
                row.get("profile_url"),
                row.get("email"),
                row.get("phone"),
                row.get("address"),
                row.get("faculty_web"),
                row.get("education"),
                row.get("biography"),
                row.get("specialization"),
                row.get("teaching"),
                row.get("publications"),
                row.get("research"),
                row.get("text_for_embedding"),
                row.get("source_file"),
                row.get("faculty_type"),
            )
        )

    conn.commit()
    return len(df)


# -------------------- CORE LOGIC --------------------

def csv_to_sqlite(
    input_csv: Path,
    db_path: Path
) -> None:
    """
    Load cleaned faculty CSV data into SQLite database.

    Args:
        input_csv (Path): Cleaned CSV path
        db_path (Path): SQLite DB path
    """
    if not input_csv.exists():
        raise FileNotFoundError(f"Input CSV not found: {input_csv}")

    print("🗄️ Loading cleaned CSV into SQLite database...")

    df = pd.read_csv(input_csv)

    conn = create_database(db_path)

    # Always refresh table
    truncate_faculty_table(conn)

    record_count = insert_faculty_data(conn, df)
    conn.close()

    print(f"✅ Faculty table refreshed in database: {db_path}")
    print(f"📊 Records inserted: {record_count}")


# -------------------- ENTRY POINT --------------------

def main() -> None:
    """
    Entry point for CSV → SQLite import.
    """
    csv_to_sqlite(
        input_csv=CLEAN_CSV_PATH,
        db_path=DB_PATH,
    )


if __name__ == "__main__":
    main()
