import json
import csv
import argparse
from pathlib import Path
from typing import List, Dict, Any


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
    "source_file",
]


def load_json_file(json_path: Path) -> List[Dict[str, Any]]:
    """
    Load a JSON file containing faculty records.

    Parameters
    ----------
    json_path : Path
        Path to the JSON file.

    Returns
    -------
    list of dict
        List of faculty records.
    """
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def process_faculty_record(
    faculty: Dict[str, Any], source_file: str
) -> Dict[str, str]:
    """
    Process a single faculty record into a flat CSV-compatible dictionary.

    Parameters
    ----------
    faculty : dict
        Raw faculty data from JSON.
    source_file : str
        Name of the JSON file from which the record was loaded.

    Returns
    -------
    dict
        Cleaned and flattened faculty record.
    """
    row = {}

    for field in FIELDS:
        if field == "source_file":
            row[field] = source_file
            continue

        value = faculty.get(field)

        # Handle list fields (education, publications, etc.)
        if isinstance(value, list):
            cleaned = [
                v.strip() for v in value if isinstance(v, str) and v.strip()
            ]
            row[field] = " | ".join(cleaned)

        # Handle missing values
        elif value is None:
            row[field] = ""

        # Everything else (strings, numbers)
        else:
            row[field] = str(value).strip()

    return row


def convert_json_dir_to_csv(input_dir: Path, output_csv: Path) -> None:
    """
    Convert all JSON files in a directory into a single CSV file.

    Parameters
    ----------
    input_dir : Path
        Directory containing JSON files.
    output_csv : Path
        Path to the output CSV file.

    Raises
    ------
    FileNotFoundError
        If the input directory does not exist.
    """
    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")

    rows = []

    for json_file in input_dir.glob("*.json"):
        data = load_json_file(json_file)

        for faculty in data:
            row = process_faculty_record(
                faculty=faculty,
                source_file=json_file.name
            )
            rows.append(row)

    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=FIELDS, quoting=csv.QUOTE_MINIMAL
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"✅ CSV created successfully: {output_csv}")


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns
    -------
    argparse.Namespace
        Parsed arguments containing input and output paths.
    """
    parser = argparse.ArgumentParser(
        description="Convert faculty JSON files into a single CSV file"
    )

    parser.add_argument(
        "--input-dir",
        type=Path,
        required=True,
        help="Directory containing faculty JSON files",
    )

    parser.add_argument(
        "--output-csv",
        type=Path,
        default=Path("faculty_all.csv"),
        help="Path to output CSV file (default: faculty_all.csv)",
    )

    return parser.parse_args()


def main() -> None:
    """
    Entry point for CLI execution.
    """
    args = parse_arguments()
    convert_json_dir_to_csv(args.input_dir, args.output_csv)


if __name__ == "__main__":
    main()
