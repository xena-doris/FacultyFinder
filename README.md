# FacultyFinder
Please Visit our Faculty Finder here - https://findtherigthfaculty.streamlit.app/


An end-to-end faculty data ingestion, embedding and recommender project. This repository demonstrates how to collect raw faculty records (JSON or scraped), clean and transform them into CSV/SQLite, compute embeddings for faculty profiles, and serve a simple recommender API and a demo frontend.

This README is written to help a new contributor reproduce the project locally, understand each component, and run the full pipeline.

## High-level plan

- Recreate a reproducible Python environment
- Scrape the Facuty data from the DAIICT website
- Convert raw scarped JSON data into a cleaned CSV
- Load cleaned data into SQLite
- Make FastAPI endpoint to easily get the faculty data fromt eh sqlite db
- Build embeddings for faculty profiles using the FastAPI endpoint created and save artifacts
- Build a user friendly frontend for the recommender results and host them publically

## Project Structure

```
Project1/
├── daiict_faculty/                 # Scrapy project for web scraping
│   ├── daiict_faculty/
│   │   ├── spiders/
│   │   │   └── faculty.py          # Main spider for scraping faculty data
│   │   ├── items.py                # Item definitions for scraped data
│   └── JSON files                  # Scraped faculty data (JSON format)
│       ├── faculty.json
│       ├── adjunct.json
│       ├── distinguished.json
│       ├── international_adjunct.json
│       ├── practice.json
├──pipeline/
│   ├── main.py                         # FastAPI application
│   ├── pipeline.py                     # One Command Runs everything
│   ├── json_to_csv.py                  # Converts JSON data to CSV
│   ├── clean_faculty_csv.py            # Cleans and normalizes CSV data
│   ├── csv_to_sqlite.py                # Imports cleaned CSV to SQLite database
│   ├── faculty_all.csv                 # Raw faculty data (CSV)
│   ├── faculty_all_cleaned.csv         # Cleaned faculty data (CSV)
│   ├── faculty.db                      # SQLite database
├──model/
│   ├── fetch_data.py                         
│   ├── build_embeddings.py                     
│   ├── recommender.py                  
│   └── JSON files/                
│       ├── faculty_data.json
│       ├── faculty_embeddings_all_mpnet.json
│       ├── faculty_meta_all_mpnet.json
├──frontend2/
│   ├── app.py                                             
│   ├── config.py 
├── requirements.txt
├── .gitignore
└── README.md            # This file

```

## 🔄 Data Pipeline Flow

```
DAIICT Website
      ↓
  Web Scraper (Scrapy - Faculty Spider)
      ↓
  JSON Files
      ↓
  json_to_csv.py (JSON → CSV)
      ↓
  faculty_all.csv
      ↓
  clean_faculty_csv.py (Data Cleaning)
      ↓
  faculty_all_cleaned.csv
      ↓
  csv_to_sqlite.py (Import to DB)
      ↓
  faculty.db (SQLite)
      ↓
  FastAPI Server
      ↓
  REST API Endpoints
      ↓
  fetch_data.py (fetch data for embeddings)
      ↓
  faculty_data.json (only required faculty data for embeddings)
      ↓
  build_embeddings.py (build embeddings for eah faculty using sentence transformer model)
        ↓
  faculty_embeddings_all_mpnet.npy, faculty_meta_all_mpnet.json
      ↓
  recommender.py (recommend the best matched faculty)
      ↓
  app.py (streamlit frontend application for recommender)
```

## Requirements

- Python 3.10+ (3.11 or 3.10 recommended — the repo contains a virtual environment for 3.11 but creating a fresh venv is recommended)
- pip
- (Optional) GPU for faster embedding computation if you plan to run large models locally
- Python dependencies: see `requirements.txt`

## Quick setup (copy/paste)

1. Create and activate a virtual environment (recommended) in a new folder:

	python3 -m venv .venv
	on mac/linux - 
        source .venv/bin/activate
    on windows - 
        venv\Scripts\activate

2. Clone the repository and change into the project directory:

	git clone <repo-url>
	cd FacultyFinder

3. Upgrade pip and install dependencies:

	pip install --upgrade pip
	pip install -r requirements.txt

4. (Optional) Inspect the raw data and artifacts shipped with the repo before running heavy jobs:

	- Raw JSON files: `daiict_faculty/*.json`
	- Precomputed embeddings + metadata: `model/artifacts/` and `model/JSON files/` (if present)

## Reproducing the pipeline (recommended order)

alternatively you could run the entire pipeline using the command -
    python -m pipeline.pipeline --all

1. Convert JSON -> CSV

	The repository contains a script to merge JSON records into a tabular CSV used by the rest of the pipeline.

	python -m pipeline.pipeline --json-to-csv

2. Clean CSV

	Normalize fields, remove duplicates, and prepare the dataset for embedding.

	python -m pipeline.pipeline --clean-csv

3. Load CSV into SQLite

	Persist a clean, queryable DB for experiments and for the API to read.

	python -m pipeline.pipeline --to-sqlite

4. Start the Uvicorn FastAPI 

    Start the FastAPI endpoint to host the faculty data on a unvicorn application for the next art of the project.

    uvicorn pipeline.main:app --reload

4. Build embeddings

    First Fetch the data from the FastAPI and get all the required faulty data for embeddings
	Compute vector embeddings for each faculty profile and write numpy arrays + metadata into `model/artifacts/`.

    python -m model.fetch_data
	python -m model.build_embeddings

	Notes: the script may accept parameters for the encoder / batch size — open the file to tune memory or model choices. You may Make the required CHanges in teh Config files

5. Run recommender demo frontend

	You can first the run the recommender.py file locally to test it out in the terminal/cmd

        python -m model.recommender

    You can then run the frontend and check it out too

        streamlit run frontend2/app.py

	Then open the frontend or query the API endpoints as described in the script docstrings.
    you cna view the publically hosted project on https://findtherigthfaculty.streamlit.app/

## Project structure and purpose of each file/folder

Root files
- `requirements.txt` — pip dependencies used by the project. Install these after creating a venv.
- `README.md` — (this file) a guide to the project.

Directories
- `config/`
  - `base.py`, `settings.py` — centralized configuration (paths, constants). If scripts fail due to missing paths, check these files first.

- `daiict_faculty/`
  - Contains example raw JSONs (adjunct.json, distinguished.json, faculty.json, international_adjunct.json, practice.json) and a Scrapy project (`daiict_faculty/daiict_faculty/`) used to scrape DAIICT faculty pages. If you don't plan to run scraping, use the JSON files as the canonical data source.

- `pipeline/`
  - `json_to_csv.py` — converts raw JSONs into a CSV.
  - `clean_faculty_csv.py` — cleans and normalizes CSV fields.
  - `csv_to_sqlite.py` — loads the cleaned CSV into SQLite (`faculty.db`).
  - `pipeline.py` & `main.py` — orchestration scripts for running the full pipeline.
  - `recommender_api.py` — a small API to serve recommendations. Check the code to see the available endpoints and expected inputs.

- `model/`
  - `build_embeddings.py` — script that computes embeddings and stores the resulting artifacts (numpy arrays + metadata JSON).
  - `fetch_data.py` — helper functions to load saved artifacts.
  - `recommender.py` — core recommender implementation (nearest neighbors in embedding space).
  - `artifacts/` — prebuilt embeddings and metadata that the recommender reads if present.
  - `JSON files/` — copies of input JSON data used for modeling.

- `frontend2/`
  - `app.py` — example demo application (could be using Streamlit, Flask, or other minimal UI). Check the top of the file for instructions on how to run.
  - `config.py` — frontend-specific configuration.

- `EDA/` — exploratory notebook(s) used during development (e.g., `EDA.ipynb`). Useful for understanding feature engineering and dataset exploration.


## How the pieces interact (contract)

- Inputs: raw JSON records found in `daiict_faculty/*.json`. Each record should contain faculty fields such as name, designation, department, email, research interests, profile text, etc.
- Processing: `pipeline/*` scripts convert and clean the data, produce a cleaned CSV and a local SQLite database.
- Modeling: `model/build_embeddings.py` reads the cleaned data and outputs embeddings as numpy arrays plus a metadata JSON that maps vectors to faculty records.
- Serving: `pipeline/recommender_api.py` or `frontend2/app.py` loads artifacts via `model/fetch_data.py` and serves similarity search queries using `model/recommender.py`.

Success criteria
- After running the pipeline and building embeddings, the recommender API should return a ranked list of similar faculty for an input query or faculty id.

Error modes
- Missing or malformed JSON fields — check `pipeline/json_to_csv.py` and `pipeline/clean_faculty_csv.py` for how the code handles missing keys.
- Path issues — update `config/settings.py` to reflect local directories.
- Dependency issues — ensure venv active and `requirements.txt` installed.


## Adding new data

1. Add JSON files to `daiict_faculty/` using the same schema as the other JSONs.
2. Re-run `json_to_csv.py` then `clean_faculty_csv.py`.
3. Rebuild embeddings with `model/build_embeddings.py`.
4. Restart the API / frontend so they pick up the new artifacts.

## Troubleshooting tips

- ImportError / ModuleNotFoundError: Activate your virtualenv and run `pip install -r requirements.txt`.
- Scripts fail with file/path errors: open `config/settings.py` and set correct paths.
- Embedding build runs out of memory: reduce batch size in `model/build_embeddings.py` or compute embeddings on a machine with more RAM / GPU.

## Data Statistics
- Dataset contains **112 faculty records** with **15 attributes**
- Academic fields (specialization, research, teaching) are **nearly complete**
- Contact details (phone, address, website) have higher missing values
- **391 unique specializations** identified across faculty
- Dominant research areas include **Machine Learning, Computer Vision, NLP, and Information Retrieval**
- Average publications per faculty: **~8**
- Publication count ranges from **0 to 61**
- Majority of faculty fall under **regular faculty category**
- Text data shows high variability, suitable for **semantic embedding**
- Dataset quality supports **statistical analysis and recommendation systems**

## Next improvements (suggestions)

- Add a Dockerfile and docker-compose to make reproduction a single command.
- Add unit tests that run a small sample through `json_to_csv.py`, `clean_faculty_csv.py`, `build_embeddings.py` to detect regressions.
- Add OpenAPI / Swagger docs if the recommender API uses FastAPI.
