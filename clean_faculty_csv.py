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
]


def clean_text(text: str) -> str | None:
    """
    Normalize and clean a text string.

    Parameters
    ----------
    text : str
        Input text value.

    Returns
    -------
    str or None
        Cleaned text with normalized whitespace, or None if invalid.
    """
    if not isinstance(text, str):
        return None

    text = re.sub(r"\s+", " ", text)
    return text.strip()


def clean_json_list(value: str) -> List[str]:
    """
    Parse and clean a JSON-encoded list stored as a string.

    Parameters
    ----------
    value : str
        JSON string representing a list.

    Returns
    -------
    list of str
        Cleaned list with short and invalid entries removed.
    """
    if pd.isna(value):
        return []

    try:
        items = json.loads(value)
    except Exception:
        return []

    cleaned = []
    for item in items:
        item = clean_text(item)
        if item and len(item) > 2:
            cleaned.append(item)

    return cleaned


def create_text_for_embedding(df: pd.DataFrame) -> pd.Series:
    """
    Create a combined text field for embeddings/search.

    Parameters
    ----------
    df : pandas.DataFrame
        Faculty dataframe.

    Returns
    -------
    pandas.Series
        Combined and cleaned text column.
    """
    text = (
        df["name"].fillna("") + ". " +
        df["biography"].apply(lambda x: " ".join(x)) + " " +
        df["specialization"].apply(lambda x: " ".join(x)) + " " +
        df["research"].apply(lambda x: " ".join(x))
    )

    return text.apply(clean_text)


def clean_faculty_csv(input_csv: Path, output_csv: Path) -> None:
    """
    Clean and normalize faculty CSV data.

    Parameters
    ----------
    input_csv : Path
        Path to raw faculty CSV file.
    output_csv : Path
        Path to save cleaned CSV file.

    Raises
    ------
    FileNotFoundError
        If the input CSV does not exist.
    """
    if not input_csv.exists():
        raise FileNotFoundError(f"Input CSV not found: {input_csv}")

    df = pd.read_csv(input_csv)

    # Normalize null-like values
    df = df.replace(
        to_replace=["", " ", "null", "None"],
        value=pd.NA
    )

    # Clean text columns
    for col in TEXT_COLUMNS:
        df[col] = df[col].apply(clean_text)

    # Clean list-based columns
    for col in LIST_COLUMNS:
        df[col] = df[col].apply(clean_json_list)

    # Remove duplicate faculty entries by email
    df = df.drop_duplicates(subset=["email"], keep="first")

    # Create embedding text column
    df["text_for_embedding"] = create_text_for_embedding(df)

    # Convert list columns back to JSON strings
    for col in LIST_COLUMNS:
        df[col] = df[col].apply(json.dumps, ensure_ascii=False)

    df.to_csv(output_csv, index=False)

    print(f"✅ Cleaned CSV saved as: {output_csv}")
    print(f"📊 Total faculty records: {len(df)}")


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns
    -------
    argparse.Namespace
        Parsed input and output CSV paths.
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
        help="Path to output cleaned CSV (default: faculty_all_cleaned.csv)",
    )

    return parser.parse_args()


def main() -> None:
    """
    Entry point for CLI execution.
    """
    args = parse_arguments()
    clean_faculty_csv(args.input_csv, args.output_csv)


if __name__ == "__main__":
    main()
