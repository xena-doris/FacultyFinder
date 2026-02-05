import requests #type: ignore
from typing import Dict

from config import API_BASE_URL, RECOMMEND_ENDPOINT


def get_recommendations(
    query: str,
    top_k: int = 5,
    faculty_type: str | None = None,
) -> Dict:
    """
    Call FastAPI recommender endpoint.
    """
    params = {
        "q": query,
        "top_k": top_k,
    }

    if faculty_type:
        params["faculty_type"] = faculty_type

    response = requests.get(
        f"{API_BASE_URL}{RECOMMEND_ENDPOINT}",
        params=params,
        timeout=30,
    )

    response.raise_for_status()
    return response.json()