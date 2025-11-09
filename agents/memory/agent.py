import sys
from pathlib import Path

# Add root directory to Python path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from python_a2a import A2AServer, run_server, Message, MessageRole
from shared.pinecone_client import PineconeClient
from shared.embeddings import get_document_embedding, get_query_embedding
import uuid
from datetime import datetime
import json

class MemoryAgent(A2AServer):
    
    def __init__(self):
        super().__init__(
            url="http://localhost:10002",
            name="Memory Agent",
            description="Stores and retrieves memories using semantic search"
        )
        self.db = PineconeClient()
        print("Memory Agent initialized")
    
    def handle_message(self, message: Message) -> Message:
        """
        Override to route messages to skills
        """
        try:
            # Parse the message content
            content = message.content.text if hasattr(message.content, 'text') else str(message.content)
            data = json.loads(content)
            
            skill = data.get('skill')
            
            # Route to appropriate skill
            if skill == 'store_memory':
                result = self.store_memory(data.get('text'), data.get('metadata'))
            elif skill == 'search_memory':
                result = self.search_memory(data.get('query'), data.get('top_k', 5))
            else:
                result = {"error": f"Unknown skill: {skill}"}
            
            # Return response
            return Message(
                role=MessageRole.AGENT,
                content=json.dumps(result)
            )
            
        except Exception as e:
            print(f"❌ Error handling message: {e}")
            import traceback
            traceback.print_exc()
            return Message(
                role=MessageRole.AGENT,
                content=json.dumps({"error": str(e)})
            )
    
    def store_memory(self, text: str, metadata: dict = None) -> dict:
        """Store a memory chunk"""
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
        
        print(f"✅ Stored memory: {memory_id} - {text[:50]}...")
        return {
            "id": memory_id,
            "status": "stored",
            "text": text[:100]
        }
    
    def search_memory(self, query: str, top_k: int = 5) -> dict:
        """Search for similar memories"""
        query_embedding = get_query_embedding(query)
        matches = self.db.search(query_embedding, top_k=top_k)
        
        # Format results
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

if __name__ == "__main__":
    agent = MemoryAgent()
    run_server(agent, host="0.0.0.0", port=10002)