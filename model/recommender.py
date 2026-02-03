"""
recommender.py

Semantic faculty recommender system using sentence embeddings and
cosine similarity with acronym-aware query expansion.

Given a free-text research query, this module returns the most relevant
faculty members based on semantic alignment.
"""

import json
from typing import List, Dict, Optional

import numpy as np
from sentence_transformers import SentenceTransformer # type: ignore
from sklearn.metrics.pairwise import cosine_similarity


# -------------------- CONFIG --------------------

ARTIFACT_DIR = "model/artifacts"

EMBEDDINGS_PATH = f"{ARTIFACT_DIR}/faculty_embeddings.npy"
META_PATH = f"{ARTIFACT_DIR}/faculty_meta.json"

MODEL_NAME = "all-mpnet-base-v2"



# -------------------- ACRONYM EXPANSION --------------------

ACRONYM_MAP = {
    "ml": "machine learning",
    "dl": "deep learning",
    "ai": "artificial intelligence",
    "nlp": "natural language processing",
    "cv": "computer vision",
    "ir": "information retrieval",
    "hci": "human computer interaction",
    "iot": "internet of things",
    "dbms": "database management systems",
    "os": "operating systems",
    "ds": "data science",
    "nn": "neural networks",
    "rl": "reinforcement learning",
    "vlsi": "very large scale integration",
    "llm" : 'large language model'
}


def expand_acronyms(query: str) -> str:
    """
    Expand common research acronyms into full phrases
    to improve embedding quality.

    Args:
        query (str): User input query

    Returns:
        str: Expanded query text
    """
    words = query.lower().split()
    expanded = [ACRONYM_MAP.get(word, word) for word in words]
    return " ".join(expanded)


# -------------------- UTILS --------------------

def load_embeddings(path: str) -> np.ndarray:
    """
    Load faculty embeddings from disk.

    Args:
        path (str): Path to .npy embeddings file

    Returns:
        np.ndarray: Embedding matrix (N, D)
    """
    return np.load(path)


def load_metadata(path: str) -> List[Dict]:
    """
    Load faculty metadata aligned with embeddings.

    Args:
        path (str): Path to metadata JSON file

    Returns:
        List[Dict]: Faculty metadata
    """
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def embed_query(query: str, model: SentenceTransformer) -> np.ndarray:
    """
    Convert a user query into a normalized embedding.

    Args:
        query (str): Input research interest text
        model (SentenceTransformer): Loaded embedding model

    Returns:
        np.ndarray: Query embedding (1, D)
    """
    embedding = model.encode(
        query,
        normalize_embeddings=True
    )
    return embedding.reshape(1, -1)


# -------------------- RECOMMENDER CORE --------------------

def recommend_faculty(
    query: str,
    embeddings: np.ndarray,
    metadata: List[Dict],
    model: SentenceTransformer,
    top_k: int = 5,
    faculty_type: Optional[str] = None
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
    expanded_query = expand_acronyms(query)
    query_embedding = embed_query(expanded_query, model)

    similarity_scores = cosine_similarity(
        query_embedding,
        embeddings
    )[0]

    ranked_indices = np.argsort(similarity_scores)[::-1]

    results = []

    for idx in ranked_indices:
        faculty = metadata[idx]

        if faculty_type and faculty["faculty_type"] != faculty_type:
            continue

        results.append({
            "id": faculty["id"],
            "name": faculty["name"],
            "faculty_type": faculty["faculty_type"],
            "similarity_score": round(float(similarity_scores[idx]), 4),
            "matched_text": faculty.get("text", "")
        })

        if len(results) >= top_k:
            break

    return results


# -------------------- DEMO / CLI --------------------

def main() -> None:
    """
    Simple CLI demo for the faculty recommender.
    """
    print("🔍 Loading recommender artifacts...")

    embeddings = load_embeddings(EMBEDDINGS_PATH)
    metadata = load_metadata(META_PATH)
    model = SentenceTransformer(MODEL_NAME)

    print("✅ Recommender ready!")
    print("-" * 50)

    while True:
        query = input("\nEnter your research interest (or 'exit'): ").strip()

        if query.lower() == "exit":
            print("👋 Goodbye!")
            break

        expanded = expand_acronyms(query)
        print(f"🔎 Interpreted query: {expanded}")

        results = recommend_faculty(
            query=query,
            embeddings=embeddings,
            metadata=metadata,
            model=model,
            top_k=5
        )

        print("\n🎓 Best matching faculty:")
        for i, res in enumerate(results, 1):
            print(f"\n{i}. {res['name']} ({res['faculty_type']})")
            print(f"   🔗 Similarity score: {res['similarity_score']}")
            print("   📄 Matched profile text:")
            print(f"   {res['matched_text'][:500]}...")


if __name__ == "__main__":
    main()
