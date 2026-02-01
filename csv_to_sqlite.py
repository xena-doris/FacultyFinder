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
    source_file TEXT
)
"""


def create_database(db_path: Path) -> sqlite3.Connection:
    """
    Create (or connect to) a SQLite database and ensure schema exists.

    Parameters
    ----------
    db_path : Path
        Path to SQLite database file.

    Returns
    -------
    sqlite3.Connection
        Active SQLite database connection.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(TABLE_SCHEMA)
    conn.commit()
    return conn


def insert_faculty_data(conn: sqlite3.Connection, df: pd.DataFrame) -> int:
    """
    Insert faculty records into the database.

    Parameters
    ----------
    conn : sqlite3.Connection
        Active SQLite connection.
    df : pandas.DataFrame
        Cleaned faculty dataframe.

    Returns
    -------
    int
        Number of records processed.
    """
    cursor = conn.cursor()

    insert_query = """
    INSERT OR IGNORE INTO faculty (
        name, profile_url, email, phone, address, faculty_web,
        education, biography, specialization, teaching,
        publications, research, text_for_embedding, source_file
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    for _, row in df.iterrows():
        cursor.execute(
            insert_query,
            (
                row["name"],
                row["profile_url"],
                row["email"],
                row["phone"],
                row["address"],
                row["faculty_web"],
                row["education"],
                row["biography"],
                row["specialization"],
                row["teaching"],
                row["publications"],
                row["research"],
                row["text_for_embedding"],
                row["source_file"],
            ),
        )

    conn.commit()
    return len(df)


def csv_to_sqlite(input_csv: Path, db_path: Path) -> None:
    """
    Load cleaned faculty CSV data into a SQLite database.

    Parameters
    ----------
    input_csv : Path
        Path to cleaned faculty CSV file.
    db_path : Path
        Path to SQLite database file.

    Raises
    ------
    FileNotFoundError
        If the input CSV file does not exist.
    """
    if not input_csv.exists():
        raise FileNotFoundError(f"Input CSV not found: {input_csv}")

    df = pd.read_csv(input_csv)

    conn = create_database(db_path)
    record_count = insert_faculty_data(conn, df)
    conn.close()

    print(f"✅ Cleaned faculty data stored in: {db_path}")
    print(f"📊 Records processed: {record_count}")


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns
    -------
    argparse.Namespace
        Parsed CSV and database paths.
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
    """
    Entry point for CLI execution.
    """
    args = parse_arguments()
    csv_to_sqlite(args.input_csv, args.db_name)


if __name__ == "__main__":
    main()
