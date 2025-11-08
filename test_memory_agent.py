# test_memory_agent.py

import time
import json
from python_a2a.client.http import A2AClient
from python_a2a.models.message import Message, MessageRole, TextContent
# ^ pull classes directly from the file where they live in 0.5.10

client = A2AClient("http://localhost:10002/a2a")

def send_json(payload: dict):
    """Wrap JSON in TextContent so the SDK sees content.type == 'text'."""
    return Message(
        role=MessageRole.USER,
        content=TextContent(text=json.dumps(payload))
    )

print("=== Testing Memory Agent ===\n")

# Test 1
print("Test 1: Storing memory about product launch...")
try:
    msg = send_json({
        "skill": "store_memory",
        "text": "We decided to launch the product in Q2 2025",
        "metadata": {"speaker": "Sarah", "topic": "product_launch"}
    })
    resp = client.send_message(msg)
    print(f"✅ Response: {resp}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2
print("\nTest 2: Storing memory about pricing...")
try:
    msg = send_json({
        "skill": "store_memory",
        "text": "The pricing will be $149 per month for enterprise",
        "metadata": {"speaker": "John", "topic": "pricing"}
    })
    resp = client.send_message(msg)
    print(f"✅ Response: {resp}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 3
print("\nTest 3: Storing memory about operations...")
try:
    msg = send_json({
        "skill": "store_memory",
        "text": "Sarah raised concerns about support capacity during scale-up",
        "metadata": {"speaker": "Sarah", "topic": "operations"}
    })
    resp = client.send_message(msg)
    print(f"✅ Response: {resp}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n⏳ Waiting for Pinecone to index...")
time.sleep(3)

# Test 4
print("\n📊 Test 4: Searching for pricing...")
try:
    msg = send_json({
        "skill": "search_memory",
        "query": "What is our pricing strategy?",
        "top_k": 3
    })
    resp = client.send_message(msg)
    print("✅ Search completed")
    print(resp)
except Exception as e:
    print(f"❌ Error: {e}")

# Test 5
print("\n📊 Test 5: What did Sarah say?")
try:
    msg = send_json({
        "skill": "search_memory",
        "query": "What concerns did Sarah raise?",
        "top_k": 3
    })
    resp = client.send_message(msg)
    print("✅ Search completed")
    print(resp)
except Exception as e:
    print(f"❌ Error: {e}")
