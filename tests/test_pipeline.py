import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from transform.transform import (
    get_sentiment,
    get_sentiment_score,
    extract_keywords,
    transform,
)

def make_df(rows):
    import csv, io, pandas as pd
    fields = ["review_id","product_id","product_name","rating","review_text","review_date"]
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fields)
    w.writeheader()
    w.writerows(rows)
    buf.seek(0)
    return pd.read_csv(buf)

# --- Sentiment tests ---

def test_positive_sentiment():
    assert get_sentiment("Absolutely brilliant and excellent product") == "positive"

def test_negative_sentiment():
    assert get_sentiment("Terrible quality, completely broken and awful") == "negative"

def test_neutral_sentiment():
    assert get_sentiment("It arrived on time") == "neutral"

def test_sentiment_score_positive():
    assert get_sentiment_score("brilliant excellent perfect") > 0

def test_sentiment_score_negative():
    assert get_sentiment_score("terrible broken awful") < 0

def test_sentiment_score_neutral():
    assert get_sentiment_score("it arrived on time") == 0.0

# --- Keyword extraction tests ---

def test_keywords_found():
    keywords = extract_keywords("Excellent grip and very comfortable")
    assert "excellent" in keywords
    assert "comfortable" in keywords

def test_keywords_none():
    assert extract_keywords("It arrived yesterday") == "none"

# --- Transform function tests ---

ROW = {"review_id":"1","product_id":"P001","product_name":"Drill",
       "rating":"5","review_text":"Brilliant and powerful tool","review_date":"2024-01-15"}

def test_transform_adds_sentiment_column():
    result = transform(make_df([ROW]))
    assert "sentiment" in result.columns

def test_transform_adds_sentiment_score():
    result = transform(make_df([ROW]))
    assert "sentiment_score" in result.columns

def test_transform_adds_keywords():
    result = transform(make_df([ROW]))
    assert "keywords" in result.columns

def test_transform_adds_review_length():
    result = transform(make_df([ROW]))
    assert "review_length" in result.columns

def test_transform_row_count_unchanged():
    rows = [
        {"review_id":"1","product_id":"P001","product_name":"Drill",
         "rating":"5","review_text":"Brilliant product","review_date":"2024-01-15"},
        {"review_id":"2","product_id":"P002","product_name":"Gloves",
         "rating":"1","review_text":"Terrible quality","review_date":"2024-01-16"},
    ]
    result = transform(make_df(rows))
    assert len(result) == 2

def test_transform_handles_empty_review():
    row = {"review_id":"1","product_id":"P001","product_name":"Drill",
           "rating":"3","review_text":"","review_date":"2024-01-15"}
    result = transform(make_df([row]))
    assert result["sentiment"].iloc[0] == "neutral"
