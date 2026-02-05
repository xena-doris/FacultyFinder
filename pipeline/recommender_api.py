"""
recommender_api.py

FastAPI router exposing semantic faculty recommendations.
"""

from typing import Optional
from fastapi import APIRouter, Query

import numpy as np
from sentence_transformers import SentenceTransformer  # type: ignore

from model.recommender import (
    recommend_faculty,
    load_embeddings,
    load_metadata,
)
from config.base import (
    FACULTY_EMBEDDINGS_PATH,
    FACULTY_META_PATH,
)
from config.settings import EMBEDDING_MODEL_NAME, TOP_K_RESULTS

router = APIRouter(prefix="/recommend", tags=["Recommender"])

# -------------------- LOAD ARTIFACTS ONCE --------------------

embeddings: np.ndarray = load_embeddings(FACULTY_EMBEDDINGS_PATH)
metadata = load_metadata(FACULTY_META_PATH)
model = SentenceTransformer(EMBEDDING_MODEL_NAME)

# -------------------- ENDPOINT --------------------

@router.get("/")
def recommend(
    q: str = Query(..., min_length=2, description="Research interest text"),
    top_k: int = Query(TOP_K_RESULTS, ge=1, le=20),
    faculty_type: Optional[str] = Query(None),
):
    """
    Semantic faculty recommendation endpoint.
    """
    results = recommend_faculty(
        query=q,
        embeddings=embeddings,
        metadata=metadata,
        model=model,
        top_k=top_k,
        faculty_type=faculty_type,
    )

    return {
        "query": q,
        "count": len(results),
        "results": results,
    }
