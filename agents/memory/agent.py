import sys
from pathlib import Path

# Add root directory to Python path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from python_a2a import A2AServer, skill, agent, run_server
from shared.pinecone_client import PineconeClient
from shared.embeddings import get_document_embedding, get_query_embedding
import uuid
from datetime import datetime

@agent(
    name="Memory Agent",
    description="Stores and retrieves memories using semantic search"
)
class MemoryAgent(A2AServer):
    
    def __init__(self):
        # Pass URL to parent - for local dev, use localhost
        super().__init__(url="http://localhost:10002")  # <<<< ADDED THIS
        self.db = PineconeClient()
        print("Memory Agent initialized")
    
    @skill(name="store_memory")
    def store_memory(self, text: str, metadata: dict = None) -> dict:
        """
        Store a memory chunk
        
        Args:
            text: The text to store
            metadata: Additional metadata (speaker, timestamp, file_id, etc.)
        
        Returns:
            {"id": "memory_id", "status": "stored"}
        """
        # Generate unique ID
        memory_id = f"mem_{uuid.uuid4().hex[:8]}"
        
        # Get embedding
        embedding = get_document_embedding(text)
        
        # Prepare metadata
        full_metadata = {
            "text": text,
            "created_at": datetime.now().isoformat(),
            **(metadata or {})
        }
        
        # Store in Pinecone
        self.db.store(
            id=memory_id,
            embedding=embedding,
            metadata=full_metadata
        )
        
        print(f"Stored memory: {memory_id}")
        return {
            "id": memory_id,
            "status": "stored",
            "text": text[:100]  # Return preview
        }
    
    @skill(name="search_memory")
    def search_memory(self, query: str, top_k: int = 5) -> dict:
        """
        Search for similar memories
        
        Args:
            query: Search query
            top_k: Number of results to return
        
        Returns:
            {"results": [...], "count": N}
        """
        # Get query embedding
        query_embedding = get_query_embedding(query)
        
        # Search
        matches = self.db.search(query_embedding, top_k=top_k)
        
        # Format results
        results = [{
            "id": match.id,
            "score": match.score,
            "text": match.metadata.get("text", ""),
            "metadata": {k: v for k, v in match.metadata.items() if k != "text"}
        } for match in matches]
        
        print(f"Found {len(results)} results for: {query}")
        return {
            "results": results,
            "count": len(results),
            "query": query
        }

if __name__ == "__main__":
    agent = MemoryAgent()
    run_server(agent, host="0.0.0.0", port=10002)