"""
build_embeddings.py

Generates sentence embeddings for faculty research profiles using a
pretrained SentenceTransformer model.

Artifacts created:
- faculty_embeddings.npy : NumPy array of shape (N, 384)
- faculty_meta.json      : Metadata aligned with embedding indices
"""

import json
import os
from typing import List, Dict

import numpy as np
from sentence_transformers import SentenceTransformer #type: ignore


# -------------------- CONFIG --------------------

DATA_PATH = "model/artifacts/faculty_data.json"
OUTPUT_DIR = "model/artifacts"

EMBEDDING_FILE = "faculty_embeddings.npy"
META_FILE = "faculty_meta.json"

MODEL_NAME = "all-mpnet-base-v2"


# -------------------- UTILS --------------------

def load_faculty_data(path: str) -> List[Dict]:
    """
    Load faculty data from JSON file.

    Args:
        path (str): Path to faculty_data.json

    Returns:
        List[Dict]: Faculty records
    """
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_embeddings(embeddings: np.ndarray, path: str) -> None:
    """
    Save embeddings to disk.

    Args:
        embeddings (np.ndarray): Embedding matrix
        path (str): Output .npy file path
    """
    np.save(path, embeddings)


def save_metadata(metadata: List[Dict], path: str) -> None:
    """
    Save faculty metadata aligned with embeddings.

    Args:
        metadata (List[Dict]): Faculty metadata
        path (str): Output JSON path
    """
    with open(path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)


# -------------------- MAIN LOGIC --------------------

def main() -> None:
    """
    Main pipeline for generating faculty embeddings.
    """
    print("🔍 Loading faculty data...")
    faculty_data = load_faculty_data(DATA_PATH)

    # Keep only records with usable text
    texts = []
    metadata = []

    for record in faculty_data:
        text = record.get("text", "")
        if not text:
            continue

        texts.append(text)
        metadata.append({
            "id": record["id"],
            "name": record["name"],
            "faculty_type": record["faculty_type"],
            "text": record["text"]   # store embedding text for explainability
        })


    print(f"🧠 Generating embeddings for {len(texts)} faculty profiles...")

    model = SentenceTransformer(MODEL_NAME)

    embeddings = model.encode(
        texts,
        batch_size=16,
        show_progress_bar=True,
        normalize_embeddings=True
    )

    embeddings = np.array(embeddings)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    save_embeddings(embeddings, os.path.join(OUTPUT_DIR, EMBEDDING_FILE))
    save_metadata(metadata, os.path.join(OUTPUT_DIR, META_FILE))

    print("✅ Embedding generation complete!")
    print(f"📦 Embeddings shape: {embeddings.shape}")
    print(f"📁 Saved to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
