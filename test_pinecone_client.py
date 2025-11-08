# test_pinecone_client.py
from shared.pinecone_client import PineconeClient
from shared.embeddings import get_document_embedding

client = PineconeClient()

# Store test
embedding = get_document_embedding("Test memory")
client.store(
    id="test-util",
    embedding=embedding,
    metadata={"text": "Test memory", "type": "test"}
)
print("Stored successfully")

# Search test
query_emb = get_document_embedding("Test memory")
results = client.search(query_emb, top_k=1)
print(f"Found: {results[0].metadata['text']}")