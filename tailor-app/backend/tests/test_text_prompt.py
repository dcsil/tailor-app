from unittest.mock import MagicMock, patch, call
import pytest
from bson.objectid import ObjectId

from usecases.text_prompt import search_database, search_class_group


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


def test_search_class_group_with_excluded_ids(mock_files_collection):
    """Test the excluded_ids parameter in search_class_group"""
    query_emb = [0.1, 0.2, 0.3]
    group_name = "test_group"
    classes = ["garment"]
    allocation = 5
    excluded_ids = ["6152f9ae1b55674f32db4a1a", "6152f9ae1b55674f32db4a1b"]
    
    mock_files_collection.aggregate.return_value = [
        {"_id": "file1", "blob_url": "url1", "class": "garment"}
    ]
    
    results = search_class_group(
        mock_files_collection,
        query_emb,
        group_name,
        classes,
        allocation,
        excluded_ids
    )
    
    mock_files_collection.aggregate.assert_called_once()
    
    call_args = mock_files_collection.aggregate.call_args[0][0]
    vs_query = call_args[0]["$vectorSearch"]
    
    assert "_id" in vs_query["filter"]
    assert "$nin" in vs_query["filter"]["_id"]
    assert isinstance(vs_query["filter"]["_id"]["$nin"][0], ObjectId)
    assert str(vs_query["filter"]["_id"]["$nin"][0]) == excluded_ids[0]
    assert str(vs_query["filter"]["_id"]["$nin"][1]) == excluded_ids[1]


@patch("usecases.text_prompt.logger")
def test_search_class_group_exception_handling(mock_logger, mock_files_collection):
    """Test exception handling in search_class_group"""
    query_emb = [0.1, 0.2, 0.3]
    group_name = "test_group"
    classes = ["garment"]
    allocation = 5
    
    mock_files_collection.aggregate.side_effect = Exception("Database error")
    
    results = search_class_group(
        mock_files_collection,
        query_emb,
        group_name,
        classes,
        allocation
    )
    
    assert results == []  # Should return empty list on exception
    mock_logger.warning.assert_called_once()
    assert "Error searching test_group" in mock_logger.warning.call_args[0][0]


@patch("usecases.text_prompt.co.embed")
@patch("usecases.text_prompt.logger")
def test_search_database_embed_exception(mock_logger, mock_embed, mock_files_collection):
    """Test exception handling in search_database when embedding fails"""
    prompt = "test prompt"
    
    mock_embed.side_effect = Exception("Embedding error")
    
    result = search_database(mock_files_collection, prompt)
    
    assert result == []  # Should return empty list on exception
    mock_logger.warning.assert_called_once()
    mock_files_collection.aggregate.assert_not_called()


@patch("usecases.text_prompt.co.embed")
@patch("usecases.text_prompt.concurrent.futures.ThreadPoolExecutor")
@patch("usecases.text_prompt.logger")
def test_search_database_threadpool_exception(mock_logger, mock_executor, mock_embed, mock_files_collection):
    """Test exception handling in search_database when thread execution fails"""
    prompt = "test prompt"
    mock_embed.return_value.embeddings.float = [[0.1, 0.2, 0.3]]
    
    mock_future = MagicMock()
    mock_future.result.side_effect = Exception("Thread execution error")
    
    mock_cm = MagicMock()
    mock_cm.__enter__.return_value = mock_executor
    mock_executor.return_value = mock_cm
    
    mock_executor.submit.return_value = mock_future
    
    with patch("usecases.text_prompt.concurrent.futures.as_completed", 
               return_value=[mock_future]):
        
        result = search_database(mock_files_collection, prompt)
        
        assert result == []
        mock_logger.warning.assert_called()


@patch("usecases.text_prompt.co.embed")
def test_search_database_remaining_results_block(mock_embed, mock_files_collection):
    """Test the remaining_results block in search_database"""
    mock_embed.return_value.embeddings.float = [[0.1, 0.2, 0.3]]
    
    # Create a scenario where some groups have more results than their allocation
    # and some have less, forcing the code to fill remaining slots
    
    # First pass will select 2 from garment, 3 from fashion_representation, etc.
    # Second pass will need to fill remaining slots from the extras
    group1 = [
        {"_id": "g1_1", "blob_url": "url_g1_1", "score": 0.95},
        {"_id": "g1_2", "blob_url": "url_g1_2", "score": 0.94},
        {"_id": "g1_3", "blob_url": "url_g1_3", "score": 0.93}  # Extra that could fill remaining slots
    ]
    
    group2 = [
        {"_id": "g2_1", "blob_url": "url_g2_1", "score": 0.92},
        {"_id": "g2_2", "blob_url": "url_g2_2", "score": 0.91},
        {"_id": "g2_3", "blob_url": "url_g2_3", "score": 0.90},
        {"_id": "g2_4", "blob_url": "url_g2_4", "score": 0.89}  # Extra that could fill remaining slots
    ]
    
    # Group 3 has no results
    group3 = []
    
    # Group 4 has fewer than its allocation
    group4 = [
        {"_id": "g4_1", "blob_url": "url_g4_1", "score": 0.85}
    ]
    
    group5 = [
        {"_id": "g5_1", "blob_url": "url_g5_1", "score": 0.83}
    ]
    
    group6 = [
        {"_id": "g6_1", "blob_url": "url_g6_1", "score": 0.80}
    ]
    
    mock_files_collection.aggregate.side_effect = [
        group1, group2, group3, group4, group5, group6
    ]
    
    # Execute with topK=8 to ensure we need to use the remaining_results block
    # With normal allocations, we'd expect to get roughly:
    # garment: 1.6 (2), fashion_representation: 2.4 (2), real_world_fashion: 1.6 (2), 
    # textures_materials: 0.8 (1), contextual_environmental: 0.8 (1), creative_inspiration: 0.8 (1)
    # But group3 has 0, so we're 1 short and need to fill from remaining
    prompt = "test prompt"
    ids, urls = search_database(mock_files_collection, prompt, topK=8)
    
    # We should have 8 results total (topK=8)
    assert len(ids) == 8
    assert len(urls) == 8
    
    # The results should include both the allocated items and the extras to fill remaining slots
    # We can't assert exact order due to randomization
    all_ids = {
        "g1_1", "g1_2", "g1_3",
        "g2_1", "g2_2", "g2_3", "g2_4",
        "g4_1", "g5_1", "g6_1"
    }
    
    assert set(ids).issubset(all_ids)