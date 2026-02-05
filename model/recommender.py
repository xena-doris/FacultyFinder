"""
recommender.py

Semantic faculty recommender system using sentence embeddings and
cosine similarity with robust query embeddings (no explicit acronym maps).

All paths and model settings are sourced from the central config module.
"""

import json
from typing import List, Dict, Optional

import numpy as np
from sentence_transformers import SentenceTransformer  # type: ignore
from sklearn.metrics.pairwise import cosine_similarity # type: ignore

from config.base import (
    FACULTY_EMBEDDINGS_PATH,
    FACULTY_META_PATH,
)
from config.settings import (
    EMBEDDING_MODEL_NAME,
    TOP_K_RESULTS,
)


# -------------------- LOADERS --------------------

def load_embeddings(path) -> np.ndarray:
    """
    Load faculty embeddings from disk.

    Args:
        path (Path): Path to embeddings file

    Returns:
        np.ndarray: Embedding matrix (N, D)
    """
    return np.load(path)


def load_metadata(path) -> List[Dict]:
    """
    Load faculty metadata aligned with embeddings.

    Args:
        path (Path): Path to metadata JSON file

    Returns:
        List[Dict]: Faculty metadata
    """
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# -------------------- QUERY EMBEDDING --------------------

def embed_query_robust(query: str, model: SentenceTransformer) -> np.ndarray:
    """
    Generate a robust query embedding by augmenting short queries
    with generic academic context and averaging embeddings.

    This avoids explicit acronym expansion and relies on the model
    to resolve semantics.

    Args:
        query (str): User input query
        model (SentenceTransformer): Sentence embedding model

    Returns:
        np.ndarray: Query embedding (1, D)
    """
    query = query.strip()

    augmented_queries = [query]

    if len(query.split()) <= 2:
        augmented_queries.extend([
            f"{query} research",
            f"{query} in computer science",
            f"{query} academic research",
            f"{query} field of study",
        ])

    embeddings = model.encode(
        augmented_queries,
        normalize_embeddings=True,
    )

    query_embedding = np.mean(embeddings, axis=0)

    return query_embedding.reshape(1, -1)


# -------------------- RECOMMENDER CORE --------------------

def recommend_faculty(
    query: str,
    embeddings: np.ndarray,
    metadata: List[Dict],
    model: SentenceTransformer,
    top_k: int = TOP_K_RESULTS,
    faculty_type: Optional[str] = None,
) -> List[Dict]:
    """
    Recommend faculty members based on semantic similarity.

    Args:
        query (str): User research interest text
        embeddings (np.ndarray): Faculty embeddings (N, D)
        metadata (List[Dict]): Faculty metadata aligned with embeddings
        model (SentenceTransformer): Sentence embedding model
        top_k (int): Number of results to return
        faculty_type (Optional[str]): Optional faculty type filter

    Returns:
        List[Dict]: Ranked faculty recommendations
    """
    query_embedding = embed_query_robust(query, model)

    similarity_scores = cosine_similarity(
        query_embedding,
        embeddings
    )[0]

    ranked_indices = np.argsort(similarity_scores)[::-1]

    results: List[Dict] = []

    for idx in ranked_indices:
        faculty = metadata[idx]

        if faculty_type and faculty["faculty_type"] != faculty_type:
            continue

        results.append({
            "id": faculty["id"],
            "name": faculty["name"],
            "faculty_type": faculty["faculty_type"],
            "email": faculty.get("email"),
            "profile_link": faculty.get("link"),
            "similarity_score": round(float(similarity_scores[idx]), 4),
            "matched_text": faculty.get("text", ""),
        })


        if len(results) >= top_k:
            break

    return results


# -------------------- CLI DEMO --------------------

def main() -> None:
    """
    Interactive CLI demo for the faculty recommender.
    """
    print("🔍 Loading recommender artifacts...")

    embeddings = load_embeddings(FACULTY_EMBEDDINGS_PATH)
    metadata = load_metadata(FACULTY_META_PATH)
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    print("✅ Recommender ready!")
    print(f"🤖 Model: {EMBEDDING_MODEL_NAME}")
    print("-" * 60)

    while True:
        query = input("\nEnter your research interest (or 'exit'): ").strip()

        if query.lower() == "exit":
            print("👋 Goodbye!")
            break

        results = recommend_faculty(
            query=query,
            embeddings=embeddings,
            metadata=metadata,
            model=model,
        )

        print("\n🎓 Best matching faculty:")
        for i, res in enumerate(results, 1):
            print(f"\n{i}. {res['name']} ({res['faculty_type']})")
            print(f"   🔗 Similarity score: {res['similarity_score']}")
            print("   📄 Matched profile text:")
            print(f"   {res['matched_text'][:500]}...")


if __name__ == "__main__":
    main()
