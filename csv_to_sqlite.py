import sqlite3
import pandas as pd
import argparse
from pathlib import Path


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


def create_database(db_path: Path) -> sqlite3.Connection:
    """
    Create (or connect to) a SQLite database and ensure schema exists.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(TABLE_SCHEMA)
    conn.commit()
    return conn


def truncate_faculty_table(conn: sqlite3.Connection) -> None:
    """
    Remove all existing records from the faculty table.
    """
    cursor = conn.cursor()
    cursor.execute("DELETE FROM faculty")
    conn.commit()


def insert_faculty_data(conn: sqlite3.Connection, df: pd.DataFrame) -> int:
    """
    Insert faculty records into the database.
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


def csv_to_sqlite(input_csv: Path, db_path: Path) -> None:
    """
    Load cleaned faculty CSV data into a SQLite database
    after truncating existing records.
    """
    if not input_csv.exists():
        raise FileNotFoundError(f"Input CSV not found: {input_csv}")

    df = pd.read_csv(input_csv)

    conn = create_database(db_path)

    # 🔥 IMPORTANT FIX
    truncate_faculty_table(conn)

    record_count = insert_faculty_data(conn, df)
    conn.close()

    print(f"✅ Faculty table refreshed in database: {db_path}")
    print(f"📊 Records inserted: {record_count}")


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Import cleaned faculty CSV data into SQLite database"
    )

    parser.add_argument(
        "--input-csv",
        type=Path,
        required=True,
        help="Path to cleaned faculty CSV file",
    )

    parser.add_argument(
        "--db-name",
        type=Path,
        default=Path("faculty.db"),
        help="SQLite database file (default: faculty.db)",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    csv_to_sqlite(args.input_csv, args.db_name)


if __name__ == "__main__":
    main()
