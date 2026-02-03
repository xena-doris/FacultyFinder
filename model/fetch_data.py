"""
fetch_data.py

Fetch faculty data from the DAIICT Faculty Finder REST API and store
model-ready metadata locally for downstream embedding and recommendation.

This script treats the FastAPI service as a black-box provider and adapts
to the API response schema.
"""

import json
import os
from typing import Dict, List

import requests

# -------------------- CONFIG --------------------

API_BASE_URL = "http://127.0.0.1:8000"
FACULTY_ENDPOINT = "/faculty"

OUTPUT_DIR = "model/artifacts"
OUTPUT_FILE = "faculty_data.json"

LIMIT = 500
TIMEOUT = 10


# -------------------- UTILS --------------------

def ensure_output_dir(path: str) -> None:
    """Ensure output directory exists."""
    os.makedirs(path, exist_ok=True)


def fetch_faculty_page(limit: int, offset: int) -> Dict:
    """
    Fetch one page of faculty data from API.

    Args:
        limit (int): Page size
        offset (int): Offset for pagination

    Returns:
        Dict: API JSON response
    """
    url = f"{API_BASE_URL}{FACULTY_ENDPOINT}"
    params = {"limit": limit, "offset": offset}

    response = requests.get(url, params=params, timeout=TIMEOUT)
    response.raise_for_status()

    return response.json()


def normalize_text(text: str) -> str:
    """Minimal normalization for embedding text."""
    if not isinstance(text, str):
        return ""
    return " ".join(text.strip().split())


def extract_model_fields(record: Dict) -> Dict:
    """
    Extract only model-relevant fields from API response.
    """
    return {
        "id": record.get("id"),
        "name": record.get("name", "").strip(),
        "faculty_type": record.get("faculty_type", "").strip(),
        "text": normalize_text(record.get("text_for_embedding", ""))
    }


# -------------------- CORE LOGIC --------------------

def fetch_all_faculty() -> List[Dict]:
    """
    Fetch all faculty records using pagination.

    Returns:
        List[Dict]: Faculty records
    """
    all_faculty: List[Dict] = []
    offset = 0

    while True:
        response = fetch_faculty_page(limit=LIMIT, offset=offset)

        faculty_list = response.get("data", [])
        total = response.get("count", 0)

        if not faculty_list:
            break

        for record in faculty_list:
            all_faculty.append(extract_model_fields(record))

        offset += LIMIT

        if offset >= total:
            break

    return all_faculty


def save_to_json(data: List[Dict], output_path: str) -> None:
    """Save fetched faculty data to JSON."""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def main() -> None:
    """Main entry point."""
    print("📡 Fetching faculty data from REST API...")

    ensure_output_dir(OUTPUT_DIR)

    faculty_data = fetch_all_faculty()

    output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
    save_to_json(faculty_data, output_path)

    print(f"✅ Saved {len(faculty_data)} faculty records to:")
    print(f"   {output_path}")

    empty_text = sum(1 for f in faculty_data if not f["text"])
    print(f"ℹ️  Records with empty text_for_embedding: {empty_text}")


if __name__ == "__main__":
    main()
