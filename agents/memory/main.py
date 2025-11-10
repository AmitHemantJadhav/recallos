import sys
from pathlib import Path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from google.adk import Agent
from shared.pinecone_client import PineconeClient
from shared.embeddings import get_document_embedding, get_query_embedding
import uuid
from datetime import datetime

# Initialize database
db = PineconeClient()

def store_memory(text: str, metadata: dict = None) -> dict:
    """
    Store a memory chunk in the vector database.
    
    Args:
        text: The text content to store
        metadata: Additional metadata (speaker, timestamp, file_id, etc.)
    
    Returns:
        Dictionary with storage confirmation
    """
    memory_id = f"mem_{uuid.uuid4().hex[:8]}"
    embedding = get_document_embedding(text)
    
    full_metadata = {
        "text": text,
        "created_at": datetime.now().isoformat(),
        **(metadata or {})
    }
    
    db.store(
        id=memory_id,
        embedding=embedding,
        metadata=full_metadata
    )
    
    print(f"✅ Stored memory: {memory_id} - {text[:50]}...")
    return {
        "id": memory_id,
        "status": "stored",
        "text": text[:100]
    }

def search_memory(query: str, top_k: int = 5) -> dict:
    """
    Search for similar memories using semantic search.
    
    Args:
        query: Search query text
        top_k: Number of results to return
    
    Returns:
        Dictionary with search results
    """
    query_embedding = get_query_embedding(query)
    matches = db.search(query_embedding, top_k=top_k)
    
    results = [{
        "id": match.id,
        "score": match.score,
        "text": match.metadata.get("text", ""),
        "metadata": {k: v for k, v in match.metadata.items() if k != "text"}
    } for match in matches]
    
    print(f"🔍 Found {len(results)} results for: '{query}'")
    for i, r in enumerate(results[:3], 1):
        print(f"   {i}. Score {r['score']:.3f}: {r['text'][:60]}...")
    
    return {
        "results": results,
        "count": len(results),
        "query": query
    }

# Create the agent
memory_agent = Agent(
    model='gemini-2.0-flash-exp',
    name='memory_agent',
    description='Stores and retrieves memories using semantic search',
    tools=[store_memory, search_memory]
)

print("✅ Memory Agent initialized")