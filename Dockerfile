FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV GCP_PROJECT_ID=product-review-pipeline
ENV GCS_BUCKET_NAME=product-review-pipeline-raw
ENV BQ_DATASET_ID=product_reviews
ENV BQ_TABLE_ID=reviews_analyzed

CMD ["python", "-m", "ingestion.ingest"]
