import json
import csv
from pathlib import Path

INPUT_DIR = Path("/Users/subratotapaswi/Desktop/BDE_Faculty_Finder/FacultyFinder/daiict_faculty")  
OUTPUT_CSV = "faculty_all.csv"

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
    "source_file"
]

rows = []

for json_file in INPUT_DIR.glob("*.json"):
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    for faculty in data:
        row = {}

        for field in FIELDS:
            if field == "source_file":
                row[field] = json_file.name
                continue

            value = faculty.get(field)

            # Handle lists (publications, research, etc.)
            if isinstance(value, list):
                # Clean junk entries and join safely for CSV
                cleaned = [v.strip() for v in value if isinstance(v, str) and v.strip()]
                row[field] = " | ".join(cleaned)

            # Handle missing values
            elif value is None:
                row[field] = ""

            # Everything else (strings, numbers)
            else:
                row[field] = value

        rows.append(row)

with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=FIELDS, quoting=csv.QUOTE_MINIMAL)
    writer.writeheader()
    writer.writerows(rows)

print(f"CSV created successfully: {OUTPUT_CSV}")