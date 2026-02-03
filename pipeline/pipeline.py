import argparse
import subprocess
from pathlib import Path

# ---------- PATHS ----------
PIPELINE_DIR = Path(__file__).resolve().parent     # Project1/pipeline
PROJECT_ROOT = PIPELINE_DIR.parent                 # Project1
SCRAPY_DIR = PROJECT_ROOT / "daiict_faculty"       # Scrapy project root

FACULTY_TYPES = [
    "faculty",
    "adjunct",
    "international_adjunct",
    "distinguished",
    "practice",
]


# ---------- PIPELINE STEPS ----------
def run_scraper():
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
            cwd=SCRAPY_DIR,   # MUST be scrapy root
            check=True,
        )

    print("✅ Scraping completed")


def run_json_to_csv(input_dir: Path, output_csv: Path):
    print("📄 Converting JSON → CSV")

    subprocess.run(
        [
            "python",
            str(PIPELINE_DIR / "json_to_csv.py"),
            "--input-dir",
            str(input_dir),
            "--output-csv",
            str(output_csv),
        ],
        check=True,
    )


def run_clean_csv(input_csv: Path, output_csv: Path):
    print("🧹 Cleaning CSV")

    subprocess.run(
        [
            "python",
            str(PIPELINE_DIR / "clean_faculty_csv.py"),
            "--input-csv",
            str(input_csv),
            "--output-csv",
            str(output_csv),
        ],
        check=True,
    )


def run_csv_to_sqlite(input_csv: Path, db_path: Path):
    print("🗄️  Loading data into SQLite")

    subprocess.run(
        [
            "python",
            str(PIPELINE_DIR / "csv_to_sqlite.py"),
            "--input-csv",
            str(input_csv),
            "--db-name",
            str(db_path),
        ],
        check=True,
    )


# ---------- ARGUMENTS ----------
def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Run Faculty Finder data pipeline"
    )

    parser.add_argument("--all", action="store_true")
    parser.add_argument("--scrape", action="store_true")
    parser.add_argument("--json-to-csv", action="store_true")
    parser.add_argument("--clean-csv", action="store_true")
    parser.add_argument("--to-sqlite", action="store_true")

    parser.add_argument(
        "--json-dir",
        type=Path,
        default=SCRAPY_DIR,
        help="Directory containing scraped JSON files",
    )
    parser.add_argument(
        "--raw-csv",
        type=Path,
        default=PIPELINE_DIR / "faculty_all.csv",
    )
    parser.add_argument(
        "--clean-csv-out",
        type=Path,
        default=PIPELINE_DIR / "faculty_all_cleaned.csv",
    )
    parser.add_argument(
        "--db-name",
        type=Path,
        default=PIPELINE_DIR / "faculty.db",
    )

    return parser.parse_args()


# ---------- MAIN ----------
def main():
    args = parse_arguments()

    if args.all:
        run_scraper()
        run_json_to_csv(args.json_dir, args.raw_csv)
        run_clean_csv(args.raw_csv, args.clean_csv_out)
        run_csv_to_sqlite(args.clean_csv_out, args.db_name)
        print("🎉 Full pipeline completed successfully")
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
Run this from the Main Project Folder

python pipeline/pipeline.py --all

python pipeline/pipeline.py --scrape
python pipeline/pipeline.py --json-to-csv
python pipeline/pipeline.py --clean-csv
python pipeline/pipeline.py --to-sqlite

uvicorn pipeline.main:app --reload


"""