"""
Search in the database for images most relevant to the text prompt based on the image descriptions and/or alt_text.
"""
from bson.objectid import ObjectId
import cohere
import logging
co = cohere.ClientV2()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def search_database(files_collection, prompt, postfilter = {},excluded_ids=[],topK=10,):
    """
    Search the database for the most relevant image descriptions to prompt.
    Return a list of image ids
    """
    try:
        query_emb = co.embed(
            texts=[prompt],
            model="embed-english-v3.0",
            input_type="search_query",
            embedding_types=["float"],
        ).embeddings.float

        vs_query = {
            "index": "default",
            "path": "embedding",
            "queryVector": query_emb[0],
            "numCandidates": 30,
            "limit": topK,
        }
        
        if len(excluded_ids)>0:
            vs_query["filter"] = {}
            vs_query["filter"]["_id"] = {"$nin": [ObjectId(i) for i in excluded_ids]}  # Convert IDs to ObjectId

        new_search_query = {"$vectorSearch": vs_query}
        project = {"$project": {"score": {"$meta": "vectorSearchScore"},"_id": 1, "blob_url": 1}}

        if len(postfilter.keys())>0:
            postFilter = {"$match":postfilter}
            res = list(files_collection.aggregate([new_search_query, project, postFilter]))
        else:
            res = list(files_collection.aggregate([new_search_query, project]))

        ids, urls = [], []
        for r in res:
            ids.append(str(r["_id"]))
            urls.append(r["blob_url"])
        
        return ids, urls

    except Exception as e:
        logger.warning(e)
        return []

