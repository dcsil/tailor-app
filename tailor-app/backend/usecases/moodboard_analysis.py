"""
Search in the database for images most relevant to the text prompt based on the image descriptions and/or alt_text.
"""

from bson.objectid import ObjectId
import concurrent.futures
import cohere
import logging
import random
import math

co = cohere.ClientV2()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def analyze_image():
    """
    Analyze an image with Cohere.

    Args:

    Returns:

    """


def search_class_group(
    files_collection,
    query_emb,
    group_name,
    classes,
    allocation,
    excluded_ids=[],
    postfilter={},
):
    """
    Search for a specific class group.

    Args:
        files_collection: MongoDB collection
        query_emb: Embedding vector for the query
        group_name: Name of the class group
        classes: List of classes to search for
        allocation: Number of results to fetch
        excluded_ids: List of IDs to exclude
        postfilter: Additional filters to apply

    Returns:
        List of results from the search
    """
    try:
        # Create the search filter
        search_filter = {}

        # Add class filter if needed
        if classes and len(classes) > 0:
            if len(classes) == 1:
                search_filter["class"] = classes[0]
            else:
                search_filter["class"] = {"$in": classes}

        # Add excluded IDs filter if there are any
        if len(excluded_ids) > 0:
            search_filter["_id"] = {"$nin": [ObjectId(i) for i in excluded_ids]}

        # Create the vector search query
        vs_query = {
            "index": "default",
            "path": "embedding",
            "queryVector": query_emb,
            "numCandidates": 30,
            "limit": allocation,
        }

        # Only add filter if we have conditions
        if search_filter:
            vs_query["filter"] = search_filter

        # Execute the vector search query
        new_search_query = {"$vectorSearch": vs_query}
        project = {
            "$project": {
                "score": {"$meta": "vectorSearchScore"},
                "_id": 1,
                "blob_url": 1,
                "class": 1,
            }
        }

        # Apply post-filter if present
        if len(postfilter.keys()) > 0:
            postFilter = {"$match": postfilter}
            results = list(
                files_collection.aggregate([new_search_query, project, postFilter])
            )
        else:
            results = list(files_collection.aggregate([new_search_query, project]))

        return results
    except Exception as e:
        logger.warning(f"Error searching {group_name}: {e}")
        return []


def search_database(
    files_collection,
    prompt,
    postfilter={},
    excluded_ids=[],
    topK=10,
):
    """
    Search the database for the most relevant image descriptions to prompt.
    Return a list of image ids
    """
    # Define class groups and their allocations
    class_groups = {
        "garment": {"classes": ["garment"], "allocation": 0.2},
        "fashion_representation": {
            "classes": ["fashion illustration", "runway"],
            "allocation": 0.3,
        },
        "real_world_fashion": {
            "classes": ["street style photograph"],
            "allocation": 0.2,
        },
        "textures_materials": {"classes": ["fabric", "texture"], "allocation": 0.1},
        "contextual_environmental": {
            "classes": ["nature", "location photograph", "historical photograph"],
            "allocation": 0.1,
        },
        "creative_inspiration": {"classes": ["art and film"], "allocation": 0.1},
    }

    # Normalize allocations to ensure they sum to 1
    total_allocation = sum(
        group_info["allocation"] for group_info in class_groups.values()
    )
    normalized_allocations = {}

    for group_name, group_info in class_groups.items():
        # Normalize the allocation
        normalized_allocations[group_name] = group_info["allocation"] / total_allocation

    # Calculate the number of results to fetch for each group
    group_allocations = {}
    for group_name, normalized_allocation in normalized_allocations.items():
        allocation = math.ceil(topK * normalized_allocation)
        # Add 1 extra result per group to handle potential shortfalls
        group_allocations[group_name] = allocation + 1

    try:
        # Generate embedding for the query once
        query_emb = co.embed(
            texts=[prompt],
            model="embed-english-v3.0",
            input_type="search_query",
            embedding_types=["float"],
        ).embeddings.float[0]

        # # Execute searches for each class group sequentially
        # all_results = {}
        # for group_name, group_info in class_groups.items():
        #     all_results[group_name] = search_class_group(
        #         files_collection,
        #         query_emb,
        #         group_name,
        #         group_info["classes"],
        #         group_allocations[group_name],
        #         excluded_ids,
        #         postfilter
        #     )

        # Execute parallel searches for each class group
        all_results = {}
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_group = {
                executor.submit(
                    search_class_group,
                    files_collection,
                    query_emb,
                    group_name,
                    group_info["classes"],
                    group_allocations[group_name],
                    excluded_ids,
                    postfilter,
                ): group_name
                for group_name, group_info in class_groups.items()
            }

            for future in concurrent.futures.as_completed(future_to_group):
                group_name = future_to_group[future]
                try:
                    all_results[group_name] = future.result()
                except Exception as e:
                    logger.warning(f"Error searching {group_name}: {e}")
                    all_results[group_name] = []

        # Calculate how many results we should take from each group
        total_results = []
        remaining_slots = topK

        # First pass: Fill slots according to normalized allocations as much as possible
        for group_name in class_groups.keys():
            target_count = min(
                math.floor(topK * normalized_allocations[group_name]),
                len(all_results[group_name]),
                remaining_slots,
            )

            if target_count > 0:
                total_results.extend(all_results[group_name][:target_count])
                # Remove used results from the available pool
                all_results[group_name] = all_results[group_name][target_count:]
                remaining_slots -= target_count

        # Second pass: Fill any remaining slots from groups with extras
        if remaining_slots > 0:
            # Flatten remaining results from all groups
            remaining_results = []
            for results in all_results.values():
                remaining_results.extend(results)

            # Take what we need to reach topK
            if remaining_results:
                # Sort by vector search score to get best remaining matches
                remaining_results.sort(key=lambda x: x.get("score", 0), reverse=True)
                total_results.extend(remaining_results[:remaining_slots])

        # Randomize the order of results
        random.shuffle(total_results)

        # Extract IDs and URLs in the same format as the original function
        ids, urls = [], []
        for r in total_results:
            ids.append(str(r["_id"]))
            urls.append(r["blob_url"])

        return ids, urls

    except Exception as e:
        logger.warning(e)
        return []
