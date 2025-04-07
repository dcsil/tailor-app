import unittest
from unittest.mock import patch, MagicMock
import os
import sys
from bson.objectid import ObjectId

# We need to patch pymongo before importing init_mongo module
# to prevent actual connection attempts


class TestInitMongo(unittest.TestCase):
    def setUp(self):
        # Save original environment variables to restore later
        self.original_env = os.environ.copy()

        # Set testing mode to True for all tests
        os.environ["TESTING"] = "True"

        # Remove module from cache to ensure clean imports
        if "init_mongo" in sys.modules:
            del sys.modules["init_mongo"]

        # Apply patches before importing
        self.mongo_client_patcher = patch("pymongo.MongoClient")
        self.mock_client = self.mongo_client_patcher.start()

        # Configure the mock client
        self.mock_instance = MagicMock()
        self.mock_admin = MagicMock()
        self.mock_db = MagicMock()
        self.mock_instance.admin = self.mock_admin
        self.mock_instance.get_database.return_value = self.mock_db
        self.mock_client.return_value = self.mock_instance

    def tearDown(self):
        # Restore original environment variables
        os.environ.clear()
        os.environ.update(self.original_env)

        # Stop all patches
        self.mongo_client_patcher.stop()

        # Remove module again to prevent state leakage between tests
        if "init_mongo" in sys.modules:
            del sys.modules["init_mongo"]

    # def test_get_config_defaults(self):
    #     # Test that default values are set when env vars are missing
    #     if "MONGO_URI" in os.environ:
    #         del os.environ["MONGO_URI"]
    #     if "DB_NAME" in os.environ:
    #         del os.environ["DB_NAME"]

    #     # Mock sys.exit to prevent actual exits
    #     with patch("sys.exit"):
    #         # Import module after setting up environment
    #         import init_mongo

    #         # Override the module's global variables that were set during import
    #         init_mongo.testing_mode = True
    #         init_mongo.client = None
    #         init_mongo.db = None

    #         # Call the function to get fresh config
    #         config = init_mongo.get_config()

    #         # Check default values
    #         self.assertEqual(config["mongo_uri"], "mongodb://localhost:27017")
    #         self.assertEqual(config["db_name"], "app_mvp")

    # def test_get_config_from_env(self):
    #     # Test that values from environment variables are used
    #     os.environ["MONGO_URI"] = "mongodb://testuser:testpass@testhost:27017"
    #     os.environ["DB_NAME"] = "test_database"

    #     # Mock sys.exit to prevent actual exits
    #     with patch("sys.exit"):
    #         # Import module after setting up environment
    #         import init_mongo

    #         # Override the module's global variables
    #         init_mongo.testing_mode = True
    #         init_mongo.client = None
    #         init_mongo.db = None

    #         # Call the function to get fresh config
    #         config = init_mongo.get_config()

    #         # Check values from environment
    #         self.assertEqual(config["mongo_uri"], "mongodb://testuser:testpass@testhost:27017")
    #         self.assertEqual(config["db_name"], "test_database")

    # def test_get_config_invalid_uri(self):
    #     # Test that invalid MongoDB Atlas URI is detected
    #     os.environ["MONGO_URI"] = "mongodb+srv://testhost:27017"  # Missing credentials

    #     # Mock sys.exit to test it's called
    #     with patch("sys.exit") as mock_exit:
    #         # Import module after setting up environment
    #         import init_mongo

    #         # Override the module's global variables
    #         init_mongo.testing_mode = True
    #         init_mongo.client = None
    #         init_mongo.db = None

    #         # This should call sys.exit(1)
    #         init_mongo.get_config()

    #         # Verify sys.exit was called
    #         mock_exit.assert_called_once_with(1)

    def test_initialize_mongo_test_mode(self):
        # Test that no connection is made in test mode
        os.environ["TESTING"] = "True"

        # Import module after setting up environment
        with patch("sys.exit"):
            import init_mongo

            # Force testing mode and clear existing connections
            init_mongo.testing_mode = True
            init_mongo.client = None
            init_mongo.db = None

            # Reset mock to clear any calls from module import
            self.mock_client.reset_mock()
            self.mock_admin.reset_mock()

            client, db = init_mongo.initialize_mongo()

            # Should not create a client in test mode
            self.assertIsNone(client)
            self.assertIsNone(db)
            self.mock_client.assert_not_called()

    def test_initialize_mongo_force_connect(self):
        # Test forced connection even in test mode
        os.environ["TESTING"] = "True"

        # Import module after setting up environment
        with patch("sys.exit"):
            import init_mongo

            # Force testing mode and clear existing connections
            init_mongo.testing_mode = True
            init_mongo.client = None
            init_mongo.db = None

            # Reset mock to clear any calls from module import
            self.mock_client.reset_mock()
            self.mock_admin.reset_mock()

            client, db = init_mongo.initialize_mongo(force_connect=True)

            # Should create a client when force_connect=True
            self.mock_client.assert_called_once()
            self.mock_admin.command.assert_called_once_with("ping")

    def test_initialize_mongo_connection_error(self):
        # Test handling of connection errors
        # Configure mock to raise an exception
        self.mock_admin.command.side_effect = Exception("Connection failed")

        # Import module after setting up environment
        with patch("sys.exit"):
            import init_mongo

            # Force testing mode off to test connection path
            init_mongo.testing_mode = False
            init_mongo.client = None
            init_mongo.db = None

            # Reset mock to clear any calls from module import
            self.mock_client.reset_mock()
            self.mock_admin.reset_mock()

            # Should return None, None when connection fails
            client, db = init_mongo.initialize_mongo()
            self.assertIsNone(client)
            self.assertIsNone(db)

    def test_initialize_mongo_successful_connection(self):
        # Test successful connection
        os.environ["TESTING"] = "False"

        # Configure successful connection
        self.mock_admin.command.return_value = True

        # Import module after setting up environment
        with patch("sys.exit"):
            import init_mongo

            # Force settings for this test
            init_mongo.testing_mode = False
            init_mongo.client = None
            init_mongo.db = None

            # Reset mock to clear any calls from module import
            self.mock_client.reset_mock()
            self.mock_admin.reset_mock()

            client, db = init_mongo.initialize_mongo()

            # Should establish connection
            self.assertEqual(client, self.mock_instance)
            self.assertEqual(db, self.mock_db)
            self.mock_admin.command.assert_called_once_with("ping")

    def test_user_collection_test_mode(self):
        # Test getting a mock collection in test mode
        os.environ["TESTING"] = "True"

        # Import module after setting up environment
        with patch("sys.exit"):
            import init_mongo

            # Force testing mode and clear existing connections
            init_mongo.testing_mode = True
            init_mongo.client = None
            init_mongo.db = None

            collection = init_mongo.get_user_collection("test_user", "test_collection")

            # Should return a MockCollection in test mode
            self.assertIsInstance(collection, init_mongo.MockCollection)
            self.assertEqual(collection.name, "user_test_user_test_collection")

    def test_initialize_atlas_search(self):
        # Test collection initialization with search index
        os.environ["TESTING"] = "False"

        # Set up mock DB with collection creation
        mock_collection = MagicMock()

        # Simulate a new collection that needs to be created
        self.mock_db.list_collection_names.return_value = []
        self.mock_db.get_collection.return_value = mock_collection
        self.mock_db.create_collection.return_value = mock_collection

        # Import module after setting up environment
        with patch("sys.exit"):
            import init_mongo

            # Override module globals
            init_mongo.testing_mode = False
            init_mongo.client = self.mock_instance
            init_mongo.db = self.mock_db

            # Call the function
            result = init_mongo.initialize_atlas_search("test_user", "files")

            # Should create a new collection with search index
            self.mock_db.create_collection.assert_called_once_with(
                "user_test_user_files"
            )
            mock_collection.create_search_index.assert_called_once()
            self.assertEqual(result, mock_collection)

    def test_mock_collection_operations(self):
        # Test that MockCollection methods work as expected
        with patch("sys.exit"):
            import init_mongo

            mock_collection = init_mongo.MockCollection("test_collection")

            # Test insert_one
            test_doc = {"name": "test"}
            result = mock_collection.insert_one(test_doc)
            self.assertIsInstance(result.inserted_id, ObjectId)
            self.assertEqual(len(mock_collection.data), 1)
            self.assertEqual(mock_collection.data[0]["name"], "test")

            # Test other methods return expected types
            find_result = mock_collection.find()
            self.assertEqual(find_result, [])

            update_result = mock_collection.update_one(
                {"_id": "123"}, {"$set": {"name": "updated"}}
            )
            self.assertEqual(update_result.modified_count, 0)

            delete_result = mock_collection.delete_one({"_id": "123"})
            self.assertEqual(delete_result.deleted_count, 0)

    def test_crud_operations(self):
        # Test CRUD operations with mock collections
        os.environ["TESTING"] = "True"

        # Import module after setting up environment
        with patch("sys.exit"):
            import init_mongo

            # Force testing mode
            init_mongo.testing_mode = True
            init_mongo.client = None
            init_mongo.db = None

            # Insert document
            doc = {"name": "test_document"}
            doc_id = init_mongo.insert_document("test_user", "test_collection", doc)
            self.assertIsInstance(doc_id, str)

            # We can't easily test find, update, and delete because MockCollection
            # has minimal implementations, but we can verify the methods exist
            self.assertTrue(callable(init_mongo.find_documents))
            self.assertTrue(callable(init_mongo.update_document))
            self.assertTrue(callable(init_mongo.delete_document))
            self.assertTrue(callable(init_mongo.delete_documents))


class TestMongoDBCrudOperations(unittest.TestCase):
    def setUp(self):
        # Save original environment variables to restore later
        self.original_env = os.environ.copy()

        # Set testing mode to True for all tests
        os.environ["TESTING"] = "True"

        # Remove module from cache to ensure clean imports
        # if "init_mongo" in sys.modules:
        #     del sys.modules["init_mongo"]

        # Apply patches before importing
        self.mongo_client_patcher = patch("pymongo.MongoClient")
        self.mock_client = self.mongo_client_patcher.start()

        # Configure the mock client
        self.mock_instance = MagicMock()
        self.mock_admin = MagicMock()
        self.mock_db = MagicMock()
        self.mock_collection = MagicMock()

        self.mock_instance.admin = self.mock_admin
        self.mock_instance.get_database.return_value = self.mock_db
        self.mock_client.return_value = self.mock_instance

        # Prevent module's sys.exit from actually exiting during tests
        self.sys_exit_patcher = patch("sys.exit")
        self.mock_exit = self.sys_exit_patcher.start()

        # Import the module after patching
        import init_mongo

        self.init_mongo = init_mongo

        # Force testing mode off to test actual MongoDB calls
        self.init_mongo.testing_mode = False
        self.init_mongo.client = self.mock_instance
        self.init_mongo.db = self.mock_db

        # Setup mock collection return
        self.mock_db.get_collection.return_value = self.mock_collection

    def tearDown(self):
        # Restore original environment variables
        os.environ.clear()
        os.environ.update(self.original_env)

        # Stop all patches
        self.mongo_client_patcher.stop()
        self.sys_exit_patcher.stop()

        # Remove module again to prevent state leakage between tests
        if "init_mongo" in sys.modules:
            del sys.modules["init_mongo"]

    def test_insert_documents(self):
        """Test inserting multiple documents"""
        # Setup mock response for insert_many
        mock_result = MagicMock()
        mock_result.inserted_ids = [
            ObjectId("507f1f77bcf86cd799439011"),
            ObjectId("507f1f77bcf86cd799439012"),
        ]
        self.mock_collection.insert_many.return_value = mock_result

        # Test documents to insert
        documents = [{"name": "doc1"}, {"name": "doc2"}]

        # Call the function
        result = self.init_mongo.insert_documents(
            "test_user", "test_collection", documents
        )

        # Verify the correct collection was retrieved
        self.mock_db.get_collection.assert_called_once_with(
            "user_test_user_test_collection"
        )

        # Verify insert_many was called with the documents
        self.mock_collection.insert_many.assert_called_once_with(documents)

        # Verify the result contains string IDs
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], "507f1f77bcf86cd799439011")
        self.assertEqual(result[1], "507f1f77bcf86cd799439012")

    def test_find_documents_no_query(self):
        """Test finding documents with no query (should find all)"""
        # Setup mock cursor
        mock_cursor = MagicMock()
        self.mock_collection.find.return_value = mock_cursor

        # Call the function with no query
        result = self.init_mongo.find_documents("test_user", "test_collection")

        # Verify the correct collection was retrieved
        self.mock_db.get_collection.assert_called_once_with(
            "user_test_user_test_collection"
        )

        # Verify find was called with empty query
        self.mock_collection.find.assert_called_once_with({})

        # Verify the result is the cursor
        self.assertEqual(result, mock_cursor)

    def test_find_documents_with_query(self):
        """Test finding documents with a specific query"""
        # Setup mock cursor
        mock_cursor = MagicMock()
        self.mock_collection.find.return_value = mock_cursor

        # Test query
        query = {"name": "test"}

        # Call the function with a query
        result = self.init_mongo.find_documents("test_user", "test_collection", query)

        # Verify the correct collection was retrieved
        self.mock_db.get_collection.assert_called_once_with(
            "user_test_user_test_collection"
        )

        # Verify find was called with the specific query
        self.mock_collection.find.assert_called_once_with(query)

        # Verify the result is the cursor
        self.assertEqual(result, mock_cursor)

    def test_update_document(self):
        """Test updating a single document"""
        # Setup mock response for update_one
        mock_result = MagicMock()
        mock_result.modified_count = 1
        self.mock_collection.update_one.return_value = mock_result

        # Test data
        document_id = "507f1f77bcf86cd799439011"
        update_data = {"name": "updated_name", "status": "active"}

        # Call the function
        result = self.init_mongo.update_document(
            "test_user", "test_collection", document_id, update_data
        )

        # Verify the correct collection was retrieved
        self.mock_db.get_collection.assert_called_once_with(
            "user_test_user_test_collection"
        )

        # Verify update_one was called with correct parameters
        self.mock_collection.update_one.assert_called_once_with(
            {"_id": ObjectId(document_id)}, {"$set": update_data}
        )

        # Verify the result is the update result
        self.assertEqual(result, mock_result)
        self.assertEqual(result.modified_count, 1)

    def test_delete_document(self):
        """Test deleting a single document"""
        # Setup mock response for delete_one
        mock_result = MagicMock()
        mock_result.deleted_count = 1
        self.mock_collection.delete_one.return_value = mock_result

        # Test document ID
        document_id = "507f1f77bcf86cd799439011"

        # Call the function
        result = self.init_mongo.delete_document(
            "test_user", "test_collection", document_id
        )

        # Verify the correct collection was retrieved
        self.mock_db.get_collection.assert_called_once_with(
            "user_test_user_test_collection"
        )

        # Verify delete_one was called with correct ID
        self.mock_collection.delete_one.assert_called_once_with(
            {"_id": ObjectId(document_id)}
        )

        # Verify the result is the delete result
        self.assertEqual(result, mock_result)
        self.assertEqual(result.deleted_count, 1)

    def test_delete_documents(self):
        """Test deleting multiple documents"""
        # Setup mock response for delete_many
        mock_result = MagicMock()
        mock_result.deleted_count = 2
        self.mock_collection.delete_many.return_value = mock_result

        # Test document IDs
        document_ids = ["507f1f77bcf86cd799439011", "507f1f77bcf86cd799439012"]

        # Call the function
        result = self.init_mongo.delete_documents(
            "test_user", "test_collection", document_ids
        )

        # Verify the correct collection was retrieved
        self.mock_db.get_collection.assert_called_once_with(
            "user_test_user_test_collection"
        )

        # Verify delete_many was called with correct IDs
        expected_object_ids = [
            ObjectId("507f1f77bcf86cd799439011"),
            ObjectId("507f1f77bcf86cd799439012"),
        ]
        self.mock_collection.delete_many.assert_called_once_with(
            {"_id": {"$in": expected_object_ids}}
        )

        # Verify the result is the delete result
        self.assertEqual(result, mock_result)
        self.assertEqual(result.deleted_count, 2)

    def test_mongodb_error_handling(self):
        """Test error handling when MongoDB operations fail"""
        # Setup mock to raise an exception
        self.mock_collection.insert_many.side_effect = Exception("Database error")

        # Test documents to insert
        documents = [{"name": "doc1"}, {"name": "doc2"}]

        # Call the function and expect an exception
        with self.assertRaises(Exception) as context:
            self.init_mongo.insert_documents("test_user", "test_collection", documents)

        # Verify the exception message
        self.assertIn("Database error", str(context.exception))
