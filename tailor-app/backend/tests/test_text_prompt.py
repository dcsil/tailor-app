from unittest.mock import MagicMock, patch
import pytest
from usecases.text_prompt import search_database  

@pytest.fixture
def mock_files_collection():
    return MagicMock()

@patch('usecases.text_prompt.co.embed')
def test_search_database_success(mock_embed, mock_files_collection):
    mock_embed.return_value.embeddings.float = [0.1, 0.2, 0.3] 

    mock_files_collection.aggregate.return_value = [
        {"_id": "file1", "description": "Test description 1"},
        {"_id": "file2", "description": "Test description 2"}
    ]

    prompt = "test prompt"
    result = search_database(mock_files_collection, prompt)

    mock_files_collection.aggregate.assert_called_once()
    assert result == ["file1", "file2"]

@patch('usecases.text_prompt.co.embed')
def test_search_database_with_postfilter(mock_embed, mock_files_collection):
    mock_embed.return_value.embeddings.float = [0.1, 0.2, 0.3]  

    mock_files_collection.aggregate.return_value = [
        {"_id": "file1", "description": "Test description 1"},
        {"_id": "file2", "description": "Test description 2"}
    ]

    prompt = "test prompt"
    postfilter = {"category": "test_category"}
    result = search_database(mock_files_collection, prompt, postfilter=postfilter)

    mock_files_collection.aggregate.assert_called_once()
    assert result == ["file1", "file2"]