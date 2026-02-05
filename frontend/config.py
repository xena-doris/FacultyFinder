import os

API_BASE_URL = os.getenv("API_URL", "http://localhost:8000")
RECOMMEND_ENDPOINT = "/recommend"

DEFAULT_TOP_K = 5
