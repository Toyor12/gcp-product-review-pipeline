# GCP Product Review Pipeline

A cloud-native ETL pipeline that ingests product review data, performs text analysis and sentiment scoring, and loads enriched data into BigQuery for analytics — built on Google Cloud Platform.

## Architecture

CSV (Cloud Storage) → Transform + Sentiment Analysis → BigQuery

### GCP Services Used
- **Cloud Storage** — raw and transformed data storage
- **BigQuery** — data warehouse and analytics layer
- **Cloud Run** — containerised pipeline execution
- **Pub/Sub** — event-driven trigger capability
- **Cloud Build** — CI/CD pipeline

## Pipeline Steps

1. **Ingestion** — uploads raw product review CSV to GCS (raw/ folder)
2. **Transform** — downloads from GCS, runs text analysis and sentiment scoring, uploads to GCS (transformed/ folder)
3. **Load** — loads transformed data from GCS into BigQuery

## Text Analysis Features

Each review is enriched with:
- sentiment — positive, negative, or neutral
- sentiment_score — float score from -1.0 to 1.0
- keywords — matched signal words extracted from review text
- review_length — character count of review text

## Project Structure

    gcp-product-review-pipeline/
    ├── data/
    │   └── reviews.csv
    ├── ingestion/
    │   └── ingest.py
    ├── transform/
    │   └── transform.py
    ├── load/
    │   └── load_to_bq.py
    ├── tests/
    │   └── test_pipeline.py
    ├── main.py
    ├── Dockerfile
    ├── requirements.txt
    └── .env.example

## Setup

### Installation
    pip install -r requirements.txt

### Authentication
    gcloud auth application-default login
    gcloud config set project product-review-pipeline

### Run the full pipeline
    python main.py

### Run tests
    pytest tests/ -v

## BigQuery Output

Table: product-review-pipeline.product_reviews.reviews_analyzed

Columns: review_id, product_id, product_name, rating, review_text, review_date, sentiment, sentiment_score, keywords, review_length, processed_at

## Author

Oyewole Oluwatoyosi — https://github.com/Toyor12
