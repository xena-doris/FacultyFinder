# -------------------- API SETTINGS --------------------

API_HOST = "127.0.0.1"
API_PORT = 8000
API_BASE_URL = f"http://{API_HOST}:{API_PORT}"

FACULTY_ENDPOINT = "/faculty"

API_LIMIT = 500
API_TIMEOUT = 10


# -------------------- EMBEDDING SETTINGS --------------------

EMBEDDING_MODEL_NAME = "all-mpnet-base-v2"

EMBEDDING_BATCH_SIZE = 16
NORMALIZE_EMBEDDINGS = False   # important for dot-product models


# -------------------- RECOMMENDER SETTINGS --------------------

TOP_K_RESULTS = 5

ENABLE_FACULTY_TYPE_FILTER = True
