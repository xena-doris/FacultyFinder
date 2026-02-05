"""
build_embeddings.py

Generates sentence embeddings for faculty research profiles using a
pretrained SentenceTransformer model.

Artifacts created:
- faculty_embeddings_all_mpnet.npy : NumPy array of shape (N, D)
- faculty_meta_all_mpnet.json      : Metadata aligned with embedding indices

All paths and settings are sourced from the central config module.
"""

import json
from typing import List, Dict

import numpy as np
from sentence_transformers import SentenceTransformer  # type: ignore

from config.base import (
    FACULTY_DATA_JSON,
    MODEL_ARTIFACT_DIR,
    FACULTY_EMBEDDINGS_PATH,
    FACULTY_META_PATH,
)
from config.settings import (
    EMBEDDING_MODEL_NAME,
    EMBEDDING_BATCH_SIZE,
    NORMALIZE_EMBEDDINGS,
)


# -------------------- UTILS --------------------

def load_faculty_data(path) -> List[Dict]:
    """
    Load faculty data from JSON file.

    Args:
        path (Path): Path to faculty_data.json

    Returns:
        List[Dict]: Faculty records
    """
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_embeddings(embeddings: np.ndarray, path) -> None:
    """
    Save embeddings to disk.

    Args:
        embeddings (np.ndarray): Embedding matrix
        path (Path): Output .npy file path
    """
    np.save(path, embeddings)


def save_metadata(metadata: List[Dict], path) -> None:
    """
    Save faculty metadata aligned with embeddings.

    Args:
        metadata (List[Dict]): Faculty metadata
        path (Path): Output JSON path
    """
    with open(path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)


# -------------------- MAIN LOGIC --------------------

def main() -> None:
    """
    Main pipeline for generating faculty embeddings.
    """
    print("🔍 Loading faculty data...")
    faculty_data = load_faculty_data(FACULTY_DATA_JSON)

    texts: List[str] = []
    metadata: List[Dict] = []

    # Keep only records with usable text
    for record in faculty_data:
        text = record.get("text", "")
        if not text:
            continue

        texts.append(text)
        metadata.append({
            "id": record["id"],
            "name": record["name"],
            "email": record["email"],
            "link": record["link"],
            "faculty_type": record["faculty_type"],
            "text": record["text"],  # retained for explainability
        })

    print(f"🧠 Generating embeddings for {len(texts)} faculty profiles...")
    print(f"🤖 Model: {EMBEDDING_MODEL_NAME}")

    model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    embeddings = model.encode(
        texts,
        batch_size=EMBEDDING_BATCH_SIZE,
        show_progress_bar=True,
        normalize_embeddings=NORMALIZE_EMBEDDINGS,
    )

    embeddings = np.asarray(embeddings)

    # Ensure artifact directory exists
    MODEL_ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    save_embeddings(embeddings, FACULTY_EMBEDDINGS_PATH)
    save_metadata(metadata, FACULTY_META_PATH)

    print("✅ Embedding generation complete!")
    print(f"📦 Embeddings shape: {embeddings.shape}")
    print(f"📁 Saved embeddings to: {FACULTY_EMBEDDINGS_PATH}")
    print(f"📁 Saved metadata to:   {FACULTY_META_PATH}")


if __name__ == "__main__":
    main()
