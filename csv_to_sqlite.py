import sqlite3
import pandas as pd

DB_NAME = "faculty.db"
CSV_FILE = "faculty_all_cleaned.csv"

df = pd.read_csv(CSV_FILE)

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS faculty (
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
    source_file TEXT
)
""")

for _, row in df.iterrows():
    cursor.execute("""
    INSERT OR IGNORE INTO faculty (
        name, profile_url, email, phone, address, faculty_web,
        education, biography, specialization, teaching,
        publications, research, text_for_embedding, source_file
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        row["name"],
        row["profile_url"],
        row["email"],
        row["phone"],
        row["address"],
        row["faculty_web"],
        row["education"],
        row["biography"],
        row["specialization"],
        row["teaching"],
        row["publications"],
        row["research"],
        row["text_for_embedding"],
        row["source_file"]
    ))

conn.commit()
conn.close()

print("Cleaned faculty data stored in faculty.db")
print(f" Records inserted: {len(df)}")