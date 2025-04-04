from unittest.mock import patch


@patch("routes.search_routes.get_user_id")
@patch("routes.search_routes.get_user_collection")
@patch("routes.search_routes.search_database")
def test_search_prompt_valid_request(
    mock_search, mock_get_collection, mock_get_user_id, client
):
    mock_get_user_id.return_value = "user123"
    mock_get_collection.return_value = "mocked_files_collection"
    mock_search.return_value = (
        ["image_1", "image_2", "image_3"],
        [
            "url_1",
            "url_2",
            "url_3",
        ],
    )

    response = client.post("/api/search-prompt", json={"prompt": "fashion"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["blob_urls"] == ["url_1", "url_2", "url_3"]
    assert data["image_ids"] == ["image_1", "image_2", "image_3"]
    assert data["user_id"] == "user123"


@patch("routes.search_routes.get_user_id")
@patch("routes.search_routes.get_user_collection")
@patch("routes.search_routes.find_documents")
@patch("routes.search_routes.update_document")
@patch("routes.search_routes.search_database")
def test_regenerate_search_success(
    mock_search,
    mock_update_document,
    mock_find_documents,
    mock_get_collection,
    mock_get_user_id,
    client,
):
    mock_get_user_id.return_value = "user123"
    mock_get_collection.return_value = "mocked_files_collection"
    mock_find_documents.return_value = [
        {
            "_id": "1",
            "queue_images": [],
            "curr_images": [["image_1", "url_1"], ["image_2", "url_2"]],
        }
    ]
    mock_search.return_value = (
        ["image_3", "image_4", "image_5"],
        [
            "url_3",
            "url_4",
            "url_5",
        ],
    )
    expected_board_doc = {
        "_id": "1",
        "queue_images": [["image_4", "url_4"], ["image_5", "url_5"]],
        "curr_images": [
            ["image_1", "url_1"],
            ["image_2", "url_2"],
            ["image_3", "url_3"],
        ],
    }

    response = client.post("/api/regenerate-search", json={"prompt": "fashion"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["next_image"] == ["image_3", "url_3"]
    assert data["remaining_queue_size"] == 2
    assert data["user_id"] == "user123"
    mock_update_document.assert_called_once_with(
        "user123", "temp_boards", "1", expected_board_doc
    )


@patch("routes.search_routes.get_user_id")
@patch("routes.search_routes.get_user_collection")
@patch("routes.search_routes.find_documents")
@patch("routes.search_routes.update_document")
@patch("routes.search_routes.search_database")
def test_regenerate_search_success2(
    mock_search,
    mock_update_document,
    mock_find_documents,
    mock_get_collection,
    mock_get_user_id,
    client,
):
    mock_get_user_id.return_value = "user123"
    mock_get_collection.return_value = "mocked_files_collection"
    mock_find_documents.return_value = [
        {
            "_id": "1",
            "queue_images": [["image_3", "url_3"]],
            "curr_images": [["image_1", "url_1"], ["image_2", "url_2"]],
        }
    ]
    expected_board_doc = {
        "_id": "1",
        "queue_images": [],
        "curr_images": [
            ["image_1", "url_1"],
            ["image_2", "url_2"],
            ["image_3", "url_3"],
        ],
    }

    response = client.post("/api/regenerate-search", json={"prompt": "fashion"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["next_image"] == ["image_3", "url_3"]
    assert not data["remaining_queue_size"]
    assert data["user_id"] == "user123"
    mock_search.assert_not_called()
    mock_update_document.assert_called_once_with(
        "user123", "temp_boards", "1", expected_board_doc
    )
