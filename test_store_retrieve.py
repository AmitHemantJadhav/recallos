from pinecone import Pinecone
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("recallos-memories")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Test data
test_memories = [
    "We decided to price the product at $149 per month",
    "Sarah suggested focusing on enterprise customers",
    "John raised concerns about support capacity"
]

# Store memories
print("Storing memories...")
for i, text in enumerate(test_memories):
    # Generate embedding with Google
    result = genai.embed_content(
        model="models/text-embedding-004",
        content=text,
        task_type="retrieval_document"
    )
    embedding = result['embedding']
    
    # Store in Pinecone
    index.upsert(vectors=[{
        "id": f"test-{i}",
        "values": embedding,
        "metadata": {"text": text, "speaker": "Test", "timestamp": i}
    }])
    print(f"Stored: {text}")

print("\nWaiting for index to update...")
import time
time.sleep(2)

# Test retrieval
query = "What price did we discuss?"
print(f"\nQuerying: {query}")

# Generate query embedding
query_result = genai.embed_content(
    model="models/text-embedding-004",
    content=query,
    task_type="retrieval_query"  # <<<< Note: different task_type for queries
)
query_embedding = query_result['embedding']

# Search
results = index.query(
    vector=query_embedding,
    top_k=3,
    include_metadata=True
)

print("\nResults:")
for match in results.matches:
    print(f"Score: {match.score:.3f} - {match.metadata['text']}")