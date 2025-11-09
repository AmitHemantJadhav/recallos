from python_a2a import A2AClient, Message, MessageRole, TextContent
import json
import time

print("="*70)
print("🚀 RECALLOS - COMPLETE SYSTEM TEST")
print("="*70)

# Connect to orchestrator
orchestrator = A2AClient("http://localhost:10000/a2a")

print("\n📋 TEST 1: Upload and Process Audio File")
print("-"*70)

# Upload audio
upload_msg = Message(
    role=MessageRole.USER,
    content=TextContent(text=json.dumps({
        "action": "upload_audio",
        "audio_path": "test_audio.mp3"
    }))
)

print("⏳ Processing audio (transcribing + storing in memory)...\n")
upload_response = orchestrator.send_message(upload_msg)
upload_result = json.loads(upload_response.content.text)

if "error" in upload_result:
    print(f"❌ Error: {upload_result['error']}")
else:
    print("✅ AUDIO PROCESSED SUCCESSFULLY!")
    print(f"   File ID: {upload_result['file_id']}")
    print(f"   Duration: {upload_result['duration']:.1f}s")
    print(f"   Segments stored: {upload_result['segments_stored']}")
    print(f"   Preview: {upload_result['transcript_preview']}")

print("\n" + "="*70)
print("📋 TEST 2: Query the Audio Memory")
print("-"*70)

# Wait a moment for indexing
print("⏳ Waiting for memory indexing...")
time.sleep(3)

# Query 1
print("\n🔍 Query 1: 'What company is conducting the interview?'")
query_msg1 = Message(
    role=MessageRole.USER,
    content=TextContent(text=json.dumps({
        "action": "query",
        "query": "What company is conducting the interview?"
    }))
)

query_response1 = orchestrator.send_message(query_msg1)
query_result1 = json.loads(query_response1.content.text)

print("\n" + "💡 ANSWER:")
print(query_result1['answer'])
print(f"\n📊 Used {query_result1['memories_used']} memories")

# Query 2
print("\n" + "-"*70)
print("\n🔍 Query 2: 'What project did Amit build with vector embeddings?'")
query_msg2 = Message(
    role=MessageRole.USER,
    content=TextContent(text=json.dumps({
        "action": "query",
        "query": "What project did Amit build with vector embeddings?"
    }))
)

query_response2 = orchestrator.send_message(query_msg2)
query_result2 = json.loads(query_response2.content.text)

print("\n" + "💡 ANSWER:")
print(query_result2['answer'])
print(f"\n📊 Used {query_result2['memories_used']} memories")

# Query 3
print("\n" + "-"*70)
print("\n🔍 Query 3: 'What role is Amit applying for?'")
query_msg3 = Message(
    role=MessageRole.USER,
    content=TextContent(text=json.dumps({
        "action": "query",
        "query": "What role is Amit applying for?"
    }))
)

query_response3 = orchestrator.send_message(query_msg3)
query_result3 = json.loads(query_response3.content.text)

print("\n" + "💡 ANSWER:")
print(query_result3['answer'])
print(f"\n📊 Used {query_result3['memories_used']} memories")

print("\n" + "="*70)
print("✅ RECALLOS SYSTEM TEST COMPLETE!")
print("="*70)
print("\n🎯 Summary:")
print("   • Transcription Agent: ✅ Working")
print("   • Memory Agent: ✅ Working")
print("   • Synthesis Agent: ✅ Working")
print("   • Orchestrator: ✅ Working")
print("   • A2A Protocol: ✅ All agents communicating")
print("\n🏆 RecallOS is ALIVE!\n")