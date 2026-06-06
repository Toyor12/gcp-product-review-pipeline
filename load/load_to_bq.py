import os
import pandas as pd
from google.cloud import storage, bigquery
import tempfile

PROJECT_ID = os.getenv("GCP_PROJECT_ID", "product-review-pipeline")
BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "product-review-pipeline-raw")
DATASET_ID = os.getenv("BQ_DATASET_ID", "product_reviews")
TABLE_ID = os.getenv("BQ_TABLE_ID", "reviews_analyzed")

SCHEMA = [
    bigquery.SchemaField("review_id", "INTEGER"),
    bigquery.SchemaField("product_id", "STRING"),
    bigquery.SchemaField("product_name", "STRING"),
    bigquery.SchemaField("rating", "INTEGER"),
    bigquery.SchemaField("review_text", "STRING"),
    bigquery.SchemaField("review_date", "DATE"),
    bigquery.SchemaField("sentiment", "STRING"),
    bigquery.SchemaField("sentiment_score", "FLOAT"),
    bigquery.SchemaField("keywords", "STRING"),
    bigquery.SchemaField("review_length", "INTEGER"),
    bigquery.SchemaField("processed_at", "STRING"),
]

def create_dataset_if_not_exists(client: bigquery.Client) -> None:
    dataset_ref = f"{PROJECT_ID}.{DATASET_ID}"
    try:
        client.get_dataset(dataset_ref)
        print(f"Dataset {DATASET_ID} already exists.")
    except Exception:
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = "EU"
        client.create_dataset(dataset)
        print(f"Dataset {DATASET_ID} created.")

def download_latest_transformed(bucket_name: str) -> pd.DataFrame:
    client = storage.Client(project=PROJECT_ID)
    bucket = client.bucket(bucket_name)
    blobs = sorted(
        [b for b in bucket.list_blobs(prefix="transformed/")],
        key=lambda b: b.updated,
        reverse=True
    )
    if not blobs:
        raise FileNotFoundError("No transformed files found in GCS.")
    latest = blobs[0]
    print(f"Downloading {latest.name} from GCS...")
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
        latest.download_to_filename(tmp.name)
        df = pd.read_csv(tmp.name)
    return df

def load_to_bigquery(df: pd.DataFrame, client: bigquery.Client) -> None:
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"
    job_config = bigquery.LoadJobConfig(
        schema=SCHEMA,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )
    job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
    job.result()
    print(f"Loaded {len(df)} rows into {table_ref}")

if __name__ == "__main__":
    bq_client = bigquery.Client(project=PROJECT_ID)
    create_dataset_if_not_exists(bq_client)
    df = download_latest_transformed(BUCKET_NAME)
    print(f"Downloaded {len(df)} transformed rows.")
    load_to_bigquery(df, bq_client)
    print("Load complete.")
