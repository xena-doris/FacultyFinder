"""
pipeline.py

Orchestrator script for the Faculty Finder data pipeline.

This script coordinates:
- Web scraping (Scrapy)
- JSON → CSV conversion
- CSV cleaning
- CSV → SQLite loading

All paths and constants are sourced from the central config module.
"""

import argparse
import subprocess
from pathlib import Path

from config.base import (
    PROJECT_ROOT,
    PIPELINE_DIR,
    SCRAPY_DIR,
)

# -------------------- PIPELINE CONFIG --------------------

FACULTY_TYPES = [
    "faculty",
    "adjunct",
    "international_adjunct",
    "distinguished",
    "practice",
]


# -------------------- PIPELINE STEPS --------------------

def run_scraper() -> None:
    """
    Run Scrapy spider for all faculty types.
    """
    print("🚀 Starting web scraping")

    for faculty_type in FACULTY_TYPES:
        output_file = SCRAPY_DIR / f"{faculty_type}.json"

        print(f"🕷️  Scraping '{faculty_type}' → {output_file.name}")

        subprocess.run(
            [
                "scrapy",
                "crawl",
                "faculty",
                "-a",
                f"faculty_type={faculty_type}",
                "-o",
                str(output_file),
            ],
            cwd=SCRAPY_DIR,  # MUST be Scrapy project root
            check=True,
        )

    print("✅ Scraping completed")


def run_json_to_csv() -> None:
    print("📄 Converting JSON → CSV")

    subprocess.run(
        [
            "python",
            "-m",
            "pipeline.json_to_csv",
        ],
        check=True,
    )


def run_clean_csv() -> None:
    print("🧹 Cleaning CSV")

    subprocess.run(
        [
            "python",
            "-m",
            "pipeline.clean_faculty_csv",
        ],
        check=True,
    )


def run_csv_to_sqlite() -> None:
    print("🗄️  Loading data into SQLite")

    subprocess.run(
        [
            "python",
            "-m",
            "pipeline.csv_to_sqlite",
        ],
        check=True,
    )


# -------------------- ARGUMENTS --------------------

def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Run Faculty Finder data pipeline"
    )

    parser.add_argument("--all", action="store_true", help="Run full pipeline")
    parser.add_argument("--scrape", action="store_true", help="Run web scraping")
    parser.add_argument("--json-to-csv", action="store_true", help="JSON → CSV step")
    parser.add_argument("--clean-csv", action="store_true", help="Clean CSV step")
    parser.add_argument("--to-sqlite", action="store_true", help="Load data into SQLite")

    return parser.parse_args()


# -------------------- MAIN --------------------

def main() -> None:
    """
    Pipeline entry point.
    """
    args = parse_arguments()

    if args.all:
        run_scraper()
        run_json_to_csv()
        run_clean_csv()
        run_csv_to_sqlite()
        print("🎉 Full pipeline completed successfully")
        return

    if args.scrape:
        run_scraper()

    if args.json_to_csv:
        run_json_to_csv()

    if args.clean_csv:
        run_clean_csv()

    if args.to_sqlite:
        run_csv_to_sqlite()


if __name__ == "__main__":
    main()

"""
Run this from the Main Project Folder

python -m pipeline.pipeline --all

python -m pipeline.pipeline --scrape
python -m pipeline.pipeline --json-to-csv
python -m pipeline.pipeline --clean-csv
python -m pipeline.pipeline --to-sqlite

uvicorn pipeline.main:app --reload


"""