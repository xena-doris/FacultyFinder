"""
json_to_csv.py

Convert scraped faculty JSON files into a single consolidated CSV file.

All paths are sourced from the central config module to ensure
consistency across the pipeline.
"""

import json
import csv
from pathlib import Path
from typing import List, Dict, Any

from config.base import SCRAPED_JSON_DIR, RAW_CSV_PATH


# -------------------- CONFIG --------------------

FIELDS = [
    "name",
    "profile_url",
    "email",
    "phone",
    "address",
    "faculty_web",
    "education",
    "biography",
    "specialization",
    "teaching",
    "publications",
    "research",
    "faculty_type",
    "source_file",
]


# -------------------- UTILS --------------------

def load_json_file(json_path: Path) -> List[Dict[str, Any]]:
    """
    Load a JSON file containing faculty records.

    Args:
        json_path (Path): Path to JSON file

    Returns:
        List[Dict[str, Any]]: Faculty records
    """
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def clean_list(values: Any) -> str:
    """
    Convert list values to a pipe-separated string.

    Examples:
        ["AI", "ML"] -> "AI | ML"
    """
    if not isinstance(values, list):
        return ""

    cleaned = [
        v.strip()
        for v in values
        if isinstance(v, str) and v.strip()
    ]
    return " | ".join(cleaned)


def process_faculty_record(
    faculty: Dict[str, Any],
    source_file: str
) -> Dict[str, str]:
    """
    Process a single faculty record into a CSV-compatible dictionary.

    Args:
        faculty (Dict[str, Any]): Raw faculty record
        source_file (str): JSON file name

    Returns:
        Dict[str, str]: CSV-ready row
    """
    row: Dict[str, str] = {}

    for field in FIELDS:
        if field == "source_file":
            row[field] = source_file
            continue

        value = faculty.get(field)

        if isinstance(value, list):
            row[field] = clean_list(value)
        elif value is None:
            row[field] = ""
        else:
            row[field] = str(value).strip()

    return row


# -------------------- CORE LOGIC --------------------

def convert_json_dir_to_csv(
    input_dir: Path,
    output_csv: Path
) -> None:
    """
    Convert all JSON files in a directory into a single CSV file.

    Args:
        input_dir (Path): Directory containing JSON files
        output_csv (Path): Output CSV path
    """
    if not input_dir.exists():
        raise FileNotFoundError(
            f"Input directory not found: {input_dir}"
        )

    rows: List[Dict[str, str]] = []

    for json_file in sorted(input_dir.glob("*.json")):
        data = load_json_file(json_file)

        for faculty in data:
            rows.append(
                process_faculty_record(
                    faculty=faculty,
                    source_file=json_file.name,
                )
            )

    output_csv.parent.mkdir(parents=True, exist_ok=True)

    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=FIELDS,
            quoting=csv.QUOTE_MINIMAL,
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"✅ CSV created successfully: {output_csv}")
    print(f"📊 Total rows written: {len(rows)}")


# -------------------- ENTRY POINT --------------------

def main() -> None:
    """
    Entry point for JSON → CSV conversion.
    """
    print("🔄 Converting scraped JSON files to CSV...")
    convert_json_dir_to_csv(
        input_dir=SCRAPED_JSON_DIR,
        output_csv=RAW_CSV_PATH,
    )


if __name__ == "__main__":
    main()
