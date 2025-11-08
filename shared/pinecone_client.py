from pinecone import Pinecone
from dotenv import load_dotenv
import os

load_dotenv()

class PineconeClient:
    def __init__(self, index_name: str = "recallos-memories"):
        """Initialize Pinecone client"""
        self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        self.index_name = index_name
        self.index = self.pc.Index(index_name)
    
    def store(self, id: str, embedding: list, metadata: dict):
        """Store a single vector"""
        self.index.upsert(vectors=[{
            "id": id,
            "values": embedding,
            "metadata": metadata
        }])
    
    def store_batch(self, vectors: list):
        """
        Store multiple vectors
        vectors: list of dicts with keys: id, embedding, metadata
        """
        formatted = [{
            "id": v["id"],
            "values": v["embedding"],
            "metadata": v["metadata"]
        } for v in vectors]
        self.index.upsert(vectors=formatted)
    
    def search(self, query_embedding: list, top_k: int = 5, filter: dict = None):
        """Search for similar vectors"""
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
            filter=filter
        )
        return results.matches
    
    def delete(self, id: str):
        """Delete a vector by ID"""
        self.index.delete(ids=[id])