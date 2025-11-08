import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

# Configure Google AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Test embedding
text = "This is a test sentence about machine learning and AI"

result = genai.embed_content(
    model="models/text-embedding-004",
    content=text,
    task_type="retrieval_document"
)

embedding = result['embedding']
print(f"Embedding length: {len(embedding)}")
print(f"First 10 values: {embedding[:10]}")