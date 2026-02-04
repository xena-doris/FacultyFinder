"""
fetch_data.py

Fetch faculty data from the DAIICT Faculty Finder REST API and store
model-ready metadata locally for downstream embedding and recommendation.

This script treats the FastAPI service as a black-box provider and
derives all paths and settings from the central config module.
"""

import json
from typing import Dict, List

import requests

from config.base import MODEL_ARTIFACT_DIR, FACULTY_DATA_JSON
from config.settings import (
    API_BASE_URL,
    FACULTY_ENDPOINT,
    API_LIMIT,
    API_TIMEOUT,
)


# -------------------- UTILS --------------------

def ensure_output_dir(path) -> None:
    """
    Ensure output directory exists.

    Args:
        path (Path): Directory path
    """
    path.mkdir(parents=True, exist_ok=True)


def fetch_faculty_page(limit: int, offset: int) -> Dict:
    """
    Fetch one page of faculty data from the REST API.

    Args:
        limit (int): Page size
        offset (int): Pagination offset

    Returns:
        Dict: Parsed API JSON response
    """
    url = f"{API_BASE_URL}{FACULTY_ENDPOINT}"
    params = {"limit": limit, "offset": offset}

    response = requests.get(url, params=params, timeout=API_TIMEOUT)
    response.raise_for_status()

    return response.json()


def normalize_text(text: str) -> str:
    """
    Minimal normalization for embedding text.

    Args:
        text (str): Raw text

    Returns:
        str: Cleaned text
    """
    if not isinstance(text, str):
        return ""
    return " ".join(text.strip().split())


def extract_model_fields(record: Dict) -> Dict:
    """
    Extract only model-relevant fields from API response.

    Args:
        record (Dict): Raw faculty record

    Returns:
        Dict: Model-ready faculty record
    """
    return {
        "id": record.get("id"),
        "name": record.get("name", "").strip(),
        "faculty_type": record.get("faculty_type", "").strip(),
        "text": normalize_text(record.get("text_for_embedding", "")),
    }


# -------------------- CORE LOGIC --------------------

def fetch_all_faculty() -> List[Dict]:
    """
    Fetch all faculty records using pagination.

    Returns:
        List[Dict]: List of faculty records
    """
    all_faculty: List[Dict] = []
    offset = 0

    while True:
        response = fetch_faculty_page(limit=API_LIMIT, offset=offset)

        faculty_list = response.get("data", [])
        total = response.get("count", 0)

        if not faculty_list:
            break

        for record in faculty_list:
            all_faculty.append(extract_model_fields(record))

        offset += API_LIMIT

        if offset >= total:
            break

    return all_faculty


def save_to_json(data: List[Dict], output_path) -> None:
    """
    Save faculty data to JSON file.

    Args:
        data (List[Dict]): Faculty records
        output_path (Path): Output file path
    """
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def main() -> None:
    """
    Entry point for faculty data fetching.
    """
    print("📡 Fetching faculty data from REST API...")

    ensure_output_dir(MODEL_ARTIFACT_DIR)

    faculty_data = fetch_all_faculty()

    save_to_json(faculty_data, FACULTY_DATA_JSON)

    print(f"✅ Saved {len(faculty_data)} faculty records to:")
    print(f"   {FACULTY_DATA_JSON}")

    empty_text = sum(1 for f in faculty_data if not f["text"])
    print(f"ℹ️  Records with empty text_for_embedding: {empty_text}")


if __name__ == "__main__":
    main()
