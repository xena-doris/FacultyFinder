"""
clean_faculty_csv.py

Clean and normalize faculty CSV data produced after scraping.
This step prepares data for database storage, embeddings, and search.

All input/output paths are sourced from the central config module.
"""

import json
import re
from pathlib import Path
from typing import List

import pandas as pd

from config.base import RAW_CSV_PATH, CLEAN_CSV_PATH


# -------------------- CONFIG --------------------

LIST_COLUMNS = [
    "education",
    "biography",
    "specialization",
    "teaching",
    "publications",
    "research",
]

TEXT_COLUMNS = [
    "name",
    "profile_url",
    "email",
    "phone",
    "address",
    "faculty_web",
    "source_file",
    "faculty_type",
]


# -------------------- UTILS --------------------

def clean_text(text: str | None) -> str | None:
    """
    Normalize and clean a text string.

    Args:
        text (str | None): Raw text

    Returns:
        str | None: Cleaned text
    """
    if not isinstance(text, str):
        return None

    text = re.sub(r"\s+", " ", text)
    return text.strip()


def clean_list_items(items: List[str]) -> List[str]:
    """
    Clean individual list items.

    Args:
        items (List[str]): Raw list values

    Returns:
        List[str]: Cleaned list
    """
    cleaned: List[str] = []
    for item in items:
        item = clean_text(item)
        if item and len(item) > 2:
            cleaned.append(item)
    return cleaned


def parse_list_field(value) -> List[str]:
    """
    Parse list-like fields coming from CSV.

    Supports:
    - NaN
    - JSON-encoded lists
    - Pipe-separated strings ("A | B | C")
    """
    if pd.isna(value):
        return []

    if isinstance(value, list):
        return clean_list_items(value)

    if isinstance(value, str):
        value = value.strip()

        # JSON list
        if value.startswith("[") and value.endswith("]"):
            try:
                return clean_list_items(json.loads(value))
            except Exception:
                pass

        # Pipe-separated fallback
        parts = [v.strip() for v in value.split("|")]
        return clean_list_items(parts)

    return []


def create_text_for_embedding(df: pd.DataFrame) -> pd.Series:
    """
    Create a combined text field for embeddings/search.
    """
    text = (
        df["biography"].apply(lambda x: " ".join(x)) + " " +
        df["specialization"].apply(lambda x: " ".join(x)) + " " +
        df["research"].apply(lambda x: " ".join(x)) + " " +
        df["teaching"].apply(lambda x: " ".join(x))
    )

    return text.apply(clean_text)


# -------------------- CORE LOGIC --------------------

def clean_faculty_csv(
    input_csv: Path,
    output_csv: Path,
) -> None:
    """
    Clean and normalize faculty CSV data.

    Args:
        input_csv (Path): Raw CSV path
        output_csv (Path): Cleaned CSV path
    """
    if not input_csv.exists():
        raise FileNotFoundError(f"Input CSV not found: {input_csv}")

    print("🧹 Cleaning faculty CSV...")
    df = pd.read_csv(input_csv)

    # Normalize null-like values
    df = df.replace(
        to_replace=["", " ", "null", "None"],
        value=pd.NA,
    )

    # Clean text columns
    for col in TEXT_COLUMNS:
        if col in df.columns:
            df[col] = df[col].apply(clean_text)

    # Parse and clean list columns
    for col in LIST_COLUMNS:
        if col in df.columns:
            df[col] = df[col].apply(parse_list_field)

    # Remove duplicate faculty entries by email
    if "email" in df.columns:
        before = len(df)
        df = df.drop_duplicates(subset=["email"], keep="first")
        after = len(df)
        print(f"🔁 Removed {before - after} duplicate records")

    # Create embedding/search text
    df["text_for_embedding"] = create_text_for_embedding(df)

    # Convert list columns to JSON strings for storage
    for col in LIST_COLUMNS:
        df[col] = df[col].apply(json.dumps, ensure_ascii=False)

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_csv, index=False)

    print(f"✅ Cleaned CSV saved as: {output_csv}")
    print(f"📊 Total faculty records: {len(df)}")


# -------------------- ENTRY POINT --------------------

def main() -> None:
    """
    Entry point for CSV cleaning.
    """
    clean_faculty_csv(
        input_csv=RAW_CSV_PATH,
        output_csv=CLEAN_CSV_PATH,
    )


if __name__ == "__main__":
    main()
