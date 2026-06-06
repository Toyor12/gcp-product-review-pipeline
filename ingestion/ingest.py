import os
from google.cloud import storage
from datetime import datetime

PROJECT_ID = os.getenv("GCP_PROJECT_ID", "product-review-pipeline")
BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "product-review-pipeline-raw")
LOCAL_FILE = "data/reviews.csv"

def create_bucket_if_not_exists(bucket_name: str) -> None:
    client = storage.Client(project=PROJECT_ID)
    try:
        client.get_bucket(bucket_name)
        print(f"Bucket {bucket_name} already exists.")
    except Exception:
        bucket = client.create_bucket(bucket_name, location="EU")
        print(f"Bucket {bucket.name} created.")

def upload_to_gcs(local_file: str, bucket_name: str) -> str:
    client = storage.Client(project=PROJECT_ID)
    bucket = client.bucket(bucket_name)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    blob_name = f"raw/reviews_{timestamp}.csv"
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(local_file)
    print(f"Uploaded {local_file} to gs://{bucket_name}/{blob_name}")
    return blob_name

if __name__ == "__main__":
    create_bucket_if_not_exists(BUCKET_NAME)
    blob_name = upload_to_gcs(LOCAL_FILE, BUCKET_NAME)
    print(f"Ingestion complete: {blob_name}")
