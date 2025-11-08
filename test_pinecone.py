from pinecone import Pinecone
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize Pinecone
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

# Create index (only run once)
index_name = "recallos-memories"

# Check if index exists
existing_indexes = [index.name for index in pc.list_indexes()]

if index_name not in existing_indexes:
    print(f"Creating index: {index_name}")
    pc.create_index(
        name=index_name,
        dimension=768,  # <<<< CHANGED: Google embedding size
        metric="cosine",
        spec={
            "serverless": {
                "cloud": "aws",
                "region": "us-east-1"
            }
        }
    )
    print("Index created!")
else:
    print(f"Index {index_name} already exists")

# Connect to index
index = pc.Index(index_name)
print(f"Index stats: {index.describe_index_stats()}")