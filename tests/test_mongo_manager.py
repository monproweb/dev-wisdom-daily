import pytest
from mongomock import MongoClient
from unittest.mock import patch
from mongo_manager import insert_quote, get_last_50_quotes


@patch("mongo_manager.MongoClient")
def test_insert_quote(mock_mongo_client):
    mock_mongo_client.return_value = MongoClient()

    for i in range(51):
        insert_quote(f"quote{i}")

    assert (
        mock_mongo_client.return_value.devwisdomdaily.quotes.count_documents({}) == 50
    )
    assert (
        mock_mongo_client.return_value.devwisdomdaily.quotes.find_one(
            sort=[("quote", 1)]
        )["quote"]
        == "quote1"
    )


@patch("mongo_manager.MongoClient")
def test_get_last_50_quotes(mock_mongo_client):
    mock_mongo_client.return_value = MongoClient()

    for i in range(60):
        insert_quote(f"quote{i}")

    last_50_quotes = get_last_50_quotes()

    assert len(last_50_quotes) == 50
    assert last_50_quotes[0] == "quote59"
    assert last_50_quotes[-1] == "quote10"
