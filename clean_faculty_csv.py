import pandas as pd
import json
import re
import argparse
from pathlib import Path
from typing import List


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


def clean_text(text: str) -> str | None:
    """
    Normalize and clean a text string.
    """
    if not isinstance(text, str):
        return None

    text = re.sub(r"\s+", " ", text)
    return text.strip()


def clean_list_items(items: List[str]) -> List[str]:
    """
    Clean individual list items.
    """
    cleaned = []
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

    # Already a list (rare but safe)
    if isinstance(value, list):
        return clean_list_items(value)

    # Try JSON first
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


def clean_faculty_csv(input_csv: Path, output_csv: Path) -> None:
    """
    Clean and normalize faculty CSV data.
    """
    if not input_csv.exists():
        raise FileNotFoundError(f"Input CSV not found: {input_csv}")

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

    # Parse and clean list columns (FIXED)
    for col in LIST_COLUMNS:
        if col in df.columns:
            df[col] = df[col].apply(parse_list_field)

    # Remove duplicate faculty entries by email
    if "email" in df.columns:
        df = df.drop_duplicates(subset=["email"], keep="first")

    # Create embedding text column
    df["text_for_embedding"] = create_text_for_embedding(df)

    # Convert list columns to JSON strings for storage
    for col in LIST_COLUMNS:
        df[col] = df[col].apply(json.dumps, ensure_ascii=False)

    df.to_csv(output_csv, index=False)

    print(f"✅ Cleaned CSV saved as: {output_csv}")
    print(f"📊 Total faculty records: {len(df)}")


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Clean and normalize faculty CSV data"
    )

    parser.add_argument(
        "--input-csv",
        type=Path,
        required=True,
        help="Path to raw faculty CSV file",
    )

    parser.add_argument(
        "--output-csv",
        type=Path,
        default=Path("faculty_all_cleaned.csv"),
        help="Path to output cleaned CSV",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    clean_faculty_csv(args.input_csv, args.output_csv)


if __name__ == "__main__":
    main()
