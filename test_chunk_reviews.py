# test_chunk_reviews.py
import pytest
from unittest.mock import MagicMock
from chunk_reviews import chunk_reviews

SAMPLE_DATA = {
    "firstName": "Richard",
    "lastName": "Whittaker",
    "legacyId": 1935348,
    "ratings": {
        "edges": [
            {"node": {
                "comment": "Great professor.",
                "helpfulRating": 5,
                "ratingTags": "Participation matters--Inspirational--Respected",
                # extra fields that should be dropped:
                "difficultyRating": 1, "grade": "B-", "wouldTakeAgain": 1,
            }},
            {"node": {
                "comment": "Teach yourself.",
                "helpfulRating": 1,
                "ratingTags": "Tough grader--Test heavy",
            }},
        ]
    }
}

def test_returns_one_doc_per_edge():
    docs = chunk_reviews(SAMPLE_DATA, "1935348")
    assert len(docs) == 2

def test_field_mapping():
    doc = chunk_reviews(SAMPLE_DATA, "1935348")[0]
    assert doc["professor_id"] == "1935348"
    assert doc["professor_name"] == "Richard Whittaker"
    assert doc["rating"] == 5
    assert doc["review_text"] == "Great professor."
    assert doc["tags"] == ["Participation matters", "Inspirational", "Respected"]

def test_professor_id_is_arg_not_node():
    docs = chunk_reviews(SAMPLE_DATA, "custom-id")
    assert all(d["professor_id"] == "custom-id" for d in docs)

def test_drops_empty_comment():
    data = {**SAMPLE_DATA, "ratings": {"edges": [
        {"node": {"comment": "", "helpfulRating": 3, "ratingTags": ""}},
        {"node": {"comment": None, "helpfulRating": 3, "ratingTags": ""}},
    ]}}
    assert chunk_reviews(data, "123") == []

def test_empty_ratings():
    data = {**SAMPLE_DATA, "ratings": {"edges": []}}
    assert chunk_reviews(data, "123") == []

def test_malformed_tags_stripped():
    data = {**SAMPLE_DATA, "ratings": {"edges": [
        {"node": {"comment": "Good.", "helpfulRating": 4, "ratingTags": "--Tough grader--"}},
    ]}}
    assert chunk_reviews(data, "123")[0]["tags"] == ["Tough grader"]