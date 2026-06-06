import os
import pandas as pd
from google.cloud import storage
import tempfile
from datetime import datetime

PROJECT_ID = os.getenv("GCP_PROJECT_ID", "product-review-pipeline")
BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "product-review-pipeline-raw")

POSITIVE_WORDS = [
    "brilliant", "excellent", "perfect", "great", "good", "happy",
    "comfortable", "bright", "strong", "easy", "powerful", "lightweight"
]
NEGATIVE_WORDS = [
    "terrible", "poor", "disappointed", "waste", "difficult", "bad",
    "awful", "broken", "flickered", "died", "fell", "stopped"
]

def get_sentiment(text: str) -> str:
    text_lower = text.lower()
    pos_score = sum(1 for word in POSITIVE_WORDS if word in text_lower)
    neg_score = sum(1 for word in NEGATIVE_WORDS if word in text_lower)
    if pos_score > neg_score:
        return "positive"
    elif neg_score > pos_score:
        return "negative"
    return "neutral"

def get_sentiment_score(text: str) -> float:
    text_lower = text.lower()
    pos_score = sum(1 for word in POSITIVE_WORDS if word in text_lower)
    neg_score = sum(1 for word in NEGATIVE_WORDS if word in text_lower)
    total = pos_score + neg_score
    if total == 0:
        return 0.0
    return round((pos_score - neg_score) / total, 2)

def extract_keywords(text: str) -> str:
    all_keywords = POSITIVE_WORDS + NEGATIVE_WORDS
    text_lower = text.lower()
    found = [word for word in all_keywords if word in text_lower]
    return ", ".join(found) if found else "none"

def download_latest_from_gcs(bucket_name: str) -> pd.DataFrame:
    client = storage.Client(project=PROJECT_ID)
    bucket = client.bucket(bucket_name)
    blobs = sorted(
        [b for b in bucket.list_blobs(prefix="raw/")],
        key=lambda b: b.updated,
        reverse=True
    )
    if not blobs:
        raise FileNotFoundError("No files found in GCS raw/ folder.")
    latest = blobs[0]
    print(f"Downloading {latest.name} from GCS...")
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
        latest.download_to_filename(tmp.name)
        df = pd.read_csv(tmp.name)
    return df

def transform(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["review_text"] = df["review_text"].fillna("").str.strip()
    df["product_name"] = df["product_name"].str.strip()
    df["review_date"] = pd.to_datetime(df["review_date"])
    df["sentiment"] = df["review_text"].apply(get_sentiment)
    df["sentiment_score"] = df["review_text"].apply(get_sentiment_score)
    df["keywords"] = df["review_text"].apply(extract_keywords)
    df["review_length"] = df["review_text"].apply(len)
    df["processed_at"] = datetime.utcnow().isoformat()
    return df

def upload_transformed(df: pd.DataFrame, bucket_name: str) -> str:
    client = storage.Client(project=PROJECT_ID)
    bucket = client.bucket(bucket_name)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    blob_name = f"transformed/reviews_{timestamp}.csv"
    blob = bucket.blob(blob_name)
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
        df.to_csv(tmp.name, index=False)
        blob.upload_from_filename(tmp.name)
    print(f"Uploaded transformed data to gs://{bucket_name}/{blob_name}")
    return blob_name

if __name__ == "__main__":
    df_raw = download_latest_from_gcs(BUCKET_NAME)
    print(f"Downloaded {len(df_raw)} rows.")
    df_transformed = transform(df_raw)
    print(df_transformed[["review_id", "sentiment", "sentiment_score", "keywords"]].to_string())
    blob_name = upload_transformed(df_transformed, BUCKET_NAME)
    print(f"Transform complete: {blob_name}")
