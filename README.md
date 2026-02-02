# Faculty Finder - DAIICT Faculty Data Scraper & API

A comprehensive web scraping and data processing pipeline that extracts faculty information from DAIICT (Dhirubhai Ambani Institute of Information and Communication Technology) and provides a REST API for querying the data.

## 📋 Project Overview

This project consists of three main components:

1. **Web Scraper** (Scrapy) - Extracts faculty data from DAIICT website
2. **Data Pipeline** - Cleans, transforms, and stores data in SQLite
3. **REST API** (FastAPI) - Provides endpoints to query faculty information

## 🏗️ Project Structure

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
│       └── practice.json
├── main.py                         # FastAPI application
├── pipeline.py                     # One Command Runs everything
├── json_to_csv.py                  # Converts JSON data to CSV
├── clean_faculty_csv.py            # Cleans and normalizes CSV data
├── csv_to_sqlite.py                # Imports cleaned CSV to SQLite database
├── faculty_all.csv                 # Raw faculty data (CSV)
├── faculty_all_cleaned.csv         # Cleaned faculty data (CSV)
├── faculty.db                      # SQLite database
└── README.md                       # This file
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
```

### Running the Entire Pipeline
```bash
python pipeline\pipeline.py --all
```


## 📊 Data Fields Collected

The system collects the following information for each faculty member:

- **name** - Faculty member's full name
- **profile_url** - URL to faculty profile page
- **email** - Email address
- **phone** - Phone number
- **address** - Office/residential address
- **faculty_web** - Personal website/homepage URL
- **education** - Educational background (list)
- **biography** - Professional biography
- **specialization** - Research specializations (list)
- **teaching** - Teaching interests/courses (list)
- **publications** - Research publications (list)
- **research** - Research interests/areas (list)
- **source_file** - Source JSON file name
- **faculty_type** - The type of faculty


## 🚀 Setup & Installation

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Install Dependencies

```bash
pip install scrapy fastapi uvicorn pandas sqlite3
```

## 🕷️ Web Scraping

### Running the Scraper

```bash
python pipeline\pipeline.py --scrape
```

### Scraper Features

- **Source**: Scrapes faculty data from `https://www.daiict.ac.in/faculty`
- **Target**: Extracts detailed information from individual faculty profile pages
- **Throttling**: Includes 1-second download delay to respect server resources
- **Robots.txt**: Complies with robots.txt rules
- **Concurrent Requests**: 1 request per domain to avoid overloading the server


## 🔧 Data Processing Pipeline

### Step 1: JSON to CSV Conversion

```bash
python pipeline\pipeline.py --json-to-csv
```

**File**: `json_to_csv.py`

Converts scraped JSON files to CSV format:

**Input**: JSON files from scraper (taken automatically)
**Output**: `faculty_all.csv` 

**Features**:
- Handles nested lists and structures
- Preserves source file information
- Cleans and formats data for CSV compatibility
- Includes `faculty_type` field (categorizes source e.g., `adjunct`, `distinguished`)

### Step 2: Data Cleaning

```bash
python pipeline\pipeline.py --clean-csv
```

**File**: `clean_faculty_csv.py`

Cleans and normalizes the CSV data:

**Input**: `faculty_all.csv`
**Output**: `faculty_all_cleaned.csv`

**Features**:
- Removes duplicate records (by email)
- Handles missing values
- Cleans whitespace and text formatting
- Parses and validates JSON list fields
- Filters out short/invalid entries
- Normalizes text across all fields
- Creates `text_for_embedding` (combined text for search/embeddings)
- Converts list columns to JSON strings for storage
- Retains `faculty_type` as a text field for filtering

**List Columns Processed**:
- education
- biography
- specialization
- teaching
- publications
- research

### Step 3: SQLite Database Creation

```bash
python pipeline\pipeline.py --to-sqlite
```

**File**: `csv_to_sqlite.py`

Imports cleaned CSV data into SQLite database:

**Input**: `faculty_all_cleaned.csv`
**Output**: `faculty.db`

**Features**:
- Creates optimized database schema
- Enforces unique email constraint
- Auto-incrementing primary keys
- Handles data type conversions
- Truncates existing faculty table before refresh
- Ignores duplicate records

## 🌐 REST API

### Running the API Server

```bash
python -m uvicorn pipeline.main:app --reload
```

Server will start at: `http://127.0.0.1:8000`

**Interactive API Documentation**: `http://127.0.0.1:8000/docs`

### API Endpoints

#### 1. Get All Faculty

```
GET /faculty
```

**Query Parameters**:
- `faculty_type` (string, optional) - Filter by faculty type (e.g., `adjunct`, `distinguished`)
- `limit` (int, default: 100, max: 500) - Number of records to return
- `offset` (int, default: 0) - Pagination offset

**Example**:
```bash
curl "http://127.0.0.1:8000/faculty?limit=10&offset=0"
```

**Response**:
```json
{
  "faculty": [
    {
      "id": 1,
      "name": "Dr. Faculty Name",
      "email": "faculty@daiict.ac.in",
      "phone": "+91-XXXXXXXXXX",
      "education": ["PhD in Computer Science", "B.Tech in IT"],
      "specialization": ["AI", "Machine Learning"],
      "publications": ["Publication 1", "Publication 2"],
      ...
    }
  ],
  "total": 150,
  "limit": 10,
  "offset": 0
}
```

#### 2. Get Faculty by ID

```
GET /faculty/{id}
```

**Example**:
```bash
curl "http://127.0.0.1:8000/faculty/1"
```

#### 3. Search Faculty (by query text)

```
GET /faculty/search
```

**Query Parameters**:
- `q` (string, required, min_length=2) - Text to search in `name` and `text_for_embedding`
- `faculty_type` (string, optional) - Filter results by faculty type

**Example**:
```bash
curl "http://127.0.0.1:8000/faculty/search?q=Dr.%20John&faculty_type=adjunct"
```

## 📦 Database Schema

```sql
CREATE TABLE faculty (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    profile_url TEXT,
    email TEXT UNIQUE,
    phone TEXT,
    address TEXT,
    faculty_web TEXT,
    education TEXT,           
    biography TEXT,           
    specialization TEXT,      
    teaching TEXT,            
    publications TEXT,        
    research TEXT,            
    text_for_embedding TEXT,   
    source_file TEXT,
    faculty_type TEXT
)
```

## 🔍 Data Quality

### Cleaning Process

The data cleaning pipeline includes:

1. **Deduplication** - Removes duplicate records by email
2. **Null Handling** - Converts empty strings, "null", "None" to NA
3. **Text Normalization** - Removes extra whitespace and trims text
4. **List Validation** - Cleans list items and filters short entries
5. **Type Consistency** - Ensures consistent data types across fields
6. **JSON Serialization** - Converts lists to JSON strings for storage

### Data Statistics

- **Total Faculty Records**: 113 faculty members (based on current `faculty_all_cleaned.csv`)
- **Data Sources**: 5 JSON files: `faculty.json`, `adjunct.json`, `distinguished.json`, `international_adjunct.json`, `practice.json`
- **Completeness**: Various fields may have partial data based on website availability

## 🛠️ Technologies Used

- **Web Scraping**: Scrapy Framework
- **Data Processing**: Pandas
- **Database**: SQLite3
- **API Framework**: FastAPI
- **Server**: Uvicorn
- **Language**: Python 3.8+


**Last Updated**: January 2026
**Status**: Active Development