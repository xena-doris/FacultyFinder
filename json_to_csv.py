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
            else:
                value = faculty.get(field)
                # Convert lists to JSON strings
                if isinstance(value, list):
                    row[field] = json.dumps(value, ensure_ascii=False)
                else:
                    row[field] = value
        rows.append(row)

with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=FIELDS)
    writer.writeheader()
    writer.writerows(rows)

print(f"CSV created: {OUTPUT_CSV}")