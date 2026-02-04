from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# -------------------- DATA PATHS --------------------

SCRAPED_JSON_DIR = PROJECT_ROOT / "daiict_faculty" 

PIPELINE_DIR = PROJECT_ROOT / "pipeline"
SCRAPY_DIR = PROJECT_ROOT / "daiict_faculty"
MODEL_DIR = PROJECT_ROOT / "model"

# CSVs
RAW_CSV_PATH = PIPELINE_DIR / "faculty_all.csv"
CLEAN_CSV_PATH = PIPELINE_DIR / "faculty_all_cleaned.csv"

# Database
DB_PATH = PIPELINE_DIR / "faculty.db"

# -------------------- MODEL ARTIFACTS --------------------

MODEL_ARTIFACT_DIR = MODEL_DIR / "JSON files"

FACULTY_DATA_JSON = MODEL_ARTIFACT_DIR / "faculty_data.json"

FACULTY_EMBEDDINGS_PATH = MODEL_ARTIFACT_DIR / "faculty_embeddings_all_mpnet.npy"
FACULTY_META_PATH = MODEL_ARTIFACT_DIR / "faculty_meta_all_mpnet.json"
