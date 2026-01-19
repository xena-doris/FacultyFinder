import pandas as pd
import json
import re

INPUT_CSV = "faculty_all.csv"
OUTPUT_CSV = "faculty_all_cleaned.csv"

LIST_COLUMNS = [
    "education",
    "biography",
    "specialization",
    "teaching",
    "publications",
    "research"
]

def clean_text(text):
    if not isinstance(text, str):
        return None
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def clean_json_list(value):
    if pd.isna(value):
        return []

    try:
        items = json.loads(value)
    except Exception:
        return []

    cleaned = []
    for item in items:
        item = clean_text(item)
        if item and len(item) > 2:
            cleaned.append(item)

    return cleaned


df = pd.read_csv(INPUT_CSV)

df = df.replace(
    to_replace=["", " ", "null", "None"],
    value=pd.NA
)

TEXT_COLUMNS = [
    "name",
    "profile_url",
    "email",
    "phone",
    "address",
    "faculty_web",
    "source_file"
]

for col in TEXT_COLUMNS:
    df[col] = df[col].apply(clean_text)

for col in LIST_COLUMNS:
    df[col] = df[col].apply(clean_json_list)

df = df.drop_duplicates(subset=["email"], keep="first")

df["text_for_embedding"] = (
    df["name"].fillna("") + ". " +
    df["biography"].apply(lambda x: " ".join(x)) + " " +
    df["specialization"].apply(lambda x: " ".join(x)) + " " +
    df["research"].apply(lambda x: " ".join(x))
)

df["text_for_embedding"] = df["text_for_embedding"].apply(clean_text)

for col in LIST_COLUMNS:
    df[col] = df[col].apply(json.dumps, ensure_ascii=False)

df.to_csv(OUTPUT_CSV, index=False)

print(f"Cleaned CSV saved as: {OUTPUT_CSV}")
print(f"Total faculty records: {len(df)}")