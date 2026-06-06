import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from ingestion.ingest import create_bucket_if_not_exists, upload_to_gcs
from transform.transform import download_latest_from_gcs, transform, upload_transformed
from load.load_to_bq import create_dataset_if_not_exists, download_latest_transformed, load_to_bigquery
from google.cloud import bigquery

PROJECT_ID = "product-review-pipeline"
BUCKET_NAME = "product-review-pipeline-raw"

def run_pipeline():
    print("=== Step 1: Ingestion ===")
    create_bucket_if_not_exists(BUCKET_NAME)
    upload_to_gcs("data/reviews.csv", BUCKET_NAME)

    print("\n=== Step 2: Transform ===")
    df_raw = download_latest_from_gcs(BUCKET_NAME)
    df_transformed = transform(df_raw)
    upload_transformed(df_transformed, BUCKET_NAME)

    print("\n=== Step 3: Load to BigQuery ===")
    bq_client = bigquery.Client(project=PROJECT_ID)
    create_dataset_if_not_exists(bq_client)
    df_final = download_latest_transformed(BUCKET_NAME)
    load_to_bigquery(df_final, bq_client)

    print("\n=== Pipeline complete ===")

if __name__ == "__main__":
    run_pipeline()
