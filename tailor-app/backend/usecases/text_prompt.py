"""
Search in the database for images most relevant to the text prompt based on the image descriptions and/or alt_text.
"""
import cohere
import logging
co = cohere.ClientV2()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def search_database(pin_collection, pins, prompt, prefilter = {}, postfilter = {},path="embedding",topK=5):
    """
    Search the database for the most relevant image descriptions/alt_texts to prompt.
    Return a list of image ids
    """
    if not pins:
        return []
    try:
        query_emb = co.embed(
            texts=[prompt],
            model="embed-english-v3.0",
            input_type="search_query",
            embedding_types=["float"],
        ).embeddings.float

        vs_query = {
            "index": "default",
            "path": path,
            "queryVector": query_emb[0],
            "numCandidates": 30,
            "limit": topK,
        }

        if len(prefilter)>0:
            vs_query["filter"] = prefilter
        
        new_search_query = {"$vectorSearch": vs_query}
        project = {"$project": {"score": {"$meta": "vectorSearchScore"},"_id": 1,"description": 1}}
        
        if len(postfilter.keys())>0:
            postFilter = {"$match":postfilter}
            res = list(pin_collection.aggregate([new_search_query, project, postFilter]))
        else:
            res = list(pin_collection.aggregate([new_search_query, project]))
        return [r["description"] for r in res]
    
    except Exception as e:
        logger.warning(e)
        return []
               