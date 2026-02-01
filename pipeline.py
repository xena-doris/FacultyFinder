import argparse
import subprocess
from pathlib import Path


FACULTY_TYPES = [
    "faculty",
    "adjunct",
    "international_adjunct",
    "distinguished",
    "practice",
]


def run_scraper():
    """
    Run Scrapy spider for all faculty types.
    """
    print("Starting web scraping for all faculty types")

    for faculty_type in FACULTY_TYPES:
        output_file = f"{faculty_type}.json"

        print(f"Scraping faculty_type='{faculty_type}' → {output_file}")

        subprocess.run(
            [
                "scrapy",
                "crawl",
                "faculty",
                "-a",
                f"faculty_type={faculty_type}",
                "-o",
                output_file,
            ],
            cwd="daiict_faculty",
            check=True,
        )

    print("Completed scraping for all faculty types")


def run_json_to_csv(input_dir: Path, output_csv: Path):
    """
    Convert scraped JSON files to CSV.
    """
    print("Converting JSON files to CSV")

    subprocess.run(
        [
            "python",
            "json_to_csv.py",
            "--input-dir",
            str(input_dir),
            "--output-csv",
            str(output_csv),
        ],
        check=True,
    )

    print("JSON → CSV conversion completed")


def run_clean_csv(input_csv: Path, output_csv: Path):
    """
    Clean and normalize faculty CSV.
    """
    print("Cleaning raw faculty CSV")

    subprocess.run(
        [
            "python",
            "clean_faculty_csv.py",
            "--input-csv",
            str(input_csv),
            "--output-csv",
            str(output_csv),
        ],
        check=True,
    )

    print("CSV cleaning completed")


def run_csv_to_sqlite(input_csv: Path, db_path: Path):
    """
    Load cleaned CSV into SQLite database.
    """
    print(f"Importing cleaned CSV into SQLite DB: {db_path}")

    subprocess.run(
        [
            "python",
            "csv_to_sqlite.py",
            "--input-csv",
            str(input_csv),
            "--db-name",
            str(db_path),
        ],
        check=True,
    )

    print("CSV → SQLite import completed")


def parse_arguments():
    """
    Parse pipeline arguments.
    """
    parser = argparse.ArgumentParser(
        description="Run Faculty Finder data pipeline"
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="Run full pipeline (scrape → SQLite)",
    )

    parser.add_argument("--scrape", action="store_true", help="Run scraper only")
    parser.add_argument("--json-to-csv", action="store_true", help="Run JSON → CSV")
    parser.add_argument("--clean-csv", action="store_true", help="Run CSV cleaning")
    parser.add_argument("--to-sqlite", action="store_true", help="Run CSV → SQLite")

    parser.add_argument(
        "--json-dir",
        type=Path,
        default=Path("daiict_faculty"),
        help="Directory containing scraped JSON files",
    )
    parser.add_argument(
        "--raw-csv",
        type=Path,
        default=Path("faculty_all.csv"),
        help="Path to raw CSV file",
    )
    parser.add_argument(
        "--clean-csv-out",
        type=Path,
        default=Path("faculty_all_cleaned.csv"),
        help="Path to cleaned CSV file",
    )
    parser.add_argument(
        "--db-name",
        type=Path,
        default=Path("faculty.db"),
        help="SQLite database file",
    )

    return parser.parse_args()


def main():
    args = parse_arguments()

    if args.all:
        run_scraper()
        run_json_to_csv(args.json_dir, args.raw_csv)
        run_clean_csv(args.raw_csv, args.clean_csv_out)
        run_csv_to_sqlite(args.clean_csv_out, args.db_name)
        print("✅ Full pipeline completed successfully")
        return

    if args.scrape:
        run_scraper()

    if args.json_to_csv:
        run_json_to_csv(args.json_dir, args.raw_csv)

    if args.clean_csv:
        run_clean_csv(args.raw_csv, args.clean_csv_out)

    if args.to_sqlite:
        run_csv_to_sqlite(args.clean_csv_out, args.db_name)


if __name__ == "__main__":
    main()


"""
run everything - python pipeline.py --all
run individual steps 
    python pipeline.py --scrape
    python pipeline.py --json-to-csv
    python pipeline.py --clean-csv
    python pipeline.py --to-sqlite
    uvicorn main:app --reload
"""