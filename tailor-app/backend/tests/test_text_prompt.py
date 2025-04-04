from unittest.mock import MagicMock, patch

import pytest
from usecases.text_prompt import search_database


@pytest.fixture
def mock_files_collection():
    return MagicMock()


@patch("usecases.text_prompt.co.embed")
def test_search_database_success(mock_embed, mock_files_collection):
    mock_embed.return_value.embeddings.float = [0.1, 0.2, 0.3]

    group1 = [{"_id": "file1", "blob_url": "url1", "score": 0.9}]
    group2 = [{"_id": "file2", "blob_url": "url2", "score": 0.8}]
    group3 = []  # Empty for one group
    group4 = [{"_id": "file3", "blob_url": "url3", "score": 0.7}]
    group5 = [{"_id": "file4", "blob_url": "url4", "score": 0.6}]
    group6 = [{"_id": "file5", "blob_url": "url5", "score": 0.5}]

    mock_files_collection.aggregate.side_effect = [
        group1,
        group2,
        group3,
        group4,
        group5,
        group6,
    ]

    prompt = "test prompt"
    result = search_database(mock_files_collection, prompt)

    assert mock_files_collection.aggregate.call_count == 6
    ids, urls = result
    assert set(ids) == {"file1", "file2", "file3", "file4", "file5"}
    assert set(urls) == {"url1", "url2", "url3", "url4", "url5"}


@patch("usecases.text_prompt.co.embed")
def test_search_database_with_postfilter(mock_embed, mock_files_collection):
    mock_embed.return_value.embeddings.float = [0.1, 0.2, 0.3]

    group1 = [{"_id": "file1", "blob_url": "url1", "score": 0.9}]
    group2 = [{"_id": "file2", "blob_url": "url2", "score": 0.8}]
    group3 = []  # Empty for one group
    group4 = [{"_id": "file3", "blob_url": "url3", "score": 0.7}]
    group5 = [{"_id": "file4", "blob_url": "url4", "score": 0.6}]
    group6 = [{"_id": "file5", "blob_url": "url5", "score": 0.5}]

    mock_files_collection.aggregate.side_effect = [
        group1,
        group2,
        group3,
        group4,
        group5,
        group6,
    ]

    prompt = "test prompt"
    postfilter = {"category": "test_category"}
    result = search_database(mock_files_collection, prompt, postfilter=postfilter)

    assert mock_files_collection.aggregate.call_count == 6

    for call in mock_files_collection.aggregate.call_args_list:
        pipeline = call.args[0]

        assert len(pipeline) >= 3

        if len(pipeline) == 3:
            assert "$match" in pipeline[2]
            assert pipeline[2]["$match"] == postfilter

    ids, urls = result
    assert set(ids) == {"file1", "file2", "file3", "file4", "file5"}
    assert set(urls) == {"url1", "url2", "url3", "url4", "url5"}
