from python_a2a import A2AClient, Message, MessageRole, TextContent
import json
import time

print("=== Testing Memory + Synthesis Agents ===\n")

# Connect to both agents
memory_client = A2AClient("http://localhost:10002/a2a")
synthesis_client = A2AClient("http://localhost:10003/a2a")

# Step 1: Search for memories
print("Step 1: Searching for pricing memories...")
query = "pricing strategy"
search_msg = Message(
    role=MessageRole.USER,
    content=TextContent(text=json.dumps({
        "skill": "search_memory",
        "query": query,
        "top_k": 3
    }))
)
memory_response = memory_client.send_message(search_msg)
memory_data = json.loads(memory_response.content.text)
print(f"✅ Found {memory_data['count']} memories\n")

# Step 2: Ask Synthesis Agent to answer using those memories
print("Step 2: Asking Synthesis Agent to generate answer...")
synthesis_msg = Message(
    role=MessageRole.USER,
    content=TextContent(text=json.dumps({
        "skill": "answer_question",
        "query": "What is our pricing strategy?",
        "context": memory_data['results']
    }))
)
synthesis_response = synthesis_client.send_message(synthesis_msg)
synthesis_data = json.loads(synthesis_response.content.text)

print("\n" + "="*60)
print("QUESTION: What is our pricing strategy?")
print("="*60)
print(f"\nANSWER:\n{synthesis_data['answer']}")
print("\n" + "="*60)
print(f"SOURCES: {len(synthesis_data['sources'])} memories used")
for i, source in enumerate(synthesis_data['sources'], 1):
    print(f"\n[{i}] Score: {source['score']:.3f}")
    print(f"    {source['text']}")
print("="*60)

# Step 3: Try another query
print("\n\nStep 3: Testing with another question...")
search_msg2 = Message(
    role=MessageRole.USER,
    content=TextContent(text=json.dumps({
        "skill": "search_memory",
        "query": "What concerns did Sarah raise?",
        "top_k": 3
    }))
)
memory_response2 = memory_client.send_message(search_msg2)
memory_data2 = json.loads(memory_response2.content.text)

synthesis_msg2 = Message(
    role=MessageRole.USER,
    content=TextContent(text=json.dumps({
        "skill": "answer_question",
        "query": "What concerns did Sarah raise?",
        "context": memory_data2['results']
    }))
)
synthesis_response2 = synthesis_client.send_message(synthesis_msg2)
synthesis_data2 = json.loads(synthesis_response2.content.text)

print("\n" + "="*60)
print("QUESTION: What concerns did Sarah raise?")
print("="*60)
print(f"\nANSWER:\n{synthesis_data2['answer']}")
print("="*60)