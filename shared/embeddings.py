import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_embedding(text: str, task_type: str = "retrieval_document") -> list:
    """
    Get embedding from Google GenAI
    
    Args:
        text: Text to embed
        task_type: "retrieval_document" for storing, "retrieval_query" for querying
    
    Returns:
        List of floats (768 dimensions)
    """
    result = genai.embed_content(
        model="models/text-embedding-004",
        content=text,
        task_type=task_type
    )
    return result['embedding']

def get_document_embedding(text: str) -> list:
    """Convenience function for document embeddings"""
    return get_embedding(text, task_type="retrieval_document")

def get_query_embedding(text: str) -> list:
    """Convenience function for query embeddings"""
    return get_embedding(text, task_type="retrieval_query")