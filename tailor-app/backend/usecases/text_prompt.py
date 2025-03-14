"""
Search in the database for images most relevant to the text prompt based on the image descriptions and/or alt_text.
"""

import cohere
import logging
co = cohere.ClientV2()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def search_database(pins, prompt):
    """
    Search the database for the most relevant image descriptions/alt_texts to prompt.
    Return a list of image ids
    """
    descriptions, alt_texts = [], []
    if not pins:
        return []
    
    for pin in pins:
        description = pin["description"]
        alt_text = pin["alt_text"]
        if description and description.strip(): # should not be empty or only-white space
            descriptions.append(description)
        else:
            descriptions.append("None")
        if alt_text and alt_text.strip(): # should not be empty or only-white space
            alt_texts.append(alt_text)
        else:
            alt_texts.append("None")

    response1 = co.rerank(
        model="rerank-v3.5",
        query=prompt,
        documents=descriptions,
        top_n=10,
    )

    response2 = co.rerank(
        model="rerank-v3.5",
        query=prompt,
        documents=alt_texts,
        top_n=10,
    )
    
    matched_indices = set()
    logger.warning(response1)
    logger.warning(response2)

    for result in response1.results:  
        if result.relevance_score >= 0.1:
            matched_indices.add(result.index)

    for result in response2.results: 
        if result.relevance_score >= 0.1:
            matched_indices.add(result.index)
       
    return [pins[idx]["_id"] for idx in matched_indices] 
    