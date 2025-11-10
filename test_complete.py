from agents.orchestrator.main import (
    transcribe_audio,
    store_memory,
    search_memory,
    answer_question,
    upload_and_process_audio,
    query_memory_tool,
    intelligent_query,
    orchestrator,
)
import time

print("="*70)
print("🧪 COMPREHENSIVE RECALLOS FUNCTION TEST")
print("="*70)

# ==================== TEST 1: Transcription ====================
print("\n" + "="*70)
print("TEST 1: Transcription Function")
print("="*70)

try:
    transcript = transcribe_audio("test_audio.mp3")
    
    if "error" in transcript:
        print(f"❌ FAILED: {transcript['error']}")
    else:
        print(f"✅ PASSED")
        print(f"   Duration: {transcript['duration']:.1f}s")
        print(f"   Segments: {len(transcript['segments'])}")
        print(f"   Language: {transcript['language']}")
        print(f"   Preview: {transcript['text'][:100]}...")
except Exception as e:
    print(f"❌ FAILED: {e}")

# ==================== TEST 2: Memory Storage ====================
print("\n" + "="*70)
print("TEST 2: Memory Storage Function")
print("="*70)

try:
    result = store_memory(
        "Test memory: RecallOS is an AI-powered audio memory system",
        metadata={"test": True, "category": "system"}
    )
    
    if "error" in result:
        print(f"❌ FAILED: {result['error']}")
    else:
        print(f"✅ PASSED")
        print(f"   Memory ID: {result['id']}")
        print(f"   Status: {result['status']}")
except Exception as e:
    print(f"❌ FAILED: {e}")

time.sleep(2)  # Wait for indexing

# ==================== TEST 3: Memory Search ====================
print("\n" + "="*70)
print("TEST 3: Memory Search Function")
print("="*70)

try:
    search_result = search_memory("RecallOS audio memory", top_k=3)
    
    if "error" in search_result:
        print(f"❌ FAILED: {search_result['error']}")
    else:
        print(f"✅ PASSED")
        print(f"   Results found: {search_result['count']}")
        if search_result['count'] > 0:
            print(f"   Top result score: {search_result['results'][0]['score']:.3f}")
            print(f"   Top result: {search_result['results'][0]['text'][:80]}...")
except Exception as e:
    print(f"❌ FAILED: {e}")

# ==================== TEST 4: Answer Generation ====================
print("\n" + "="*70)
print("TEST 4: Answer Generation Function")
print("="*70)

try:
    # Use the search results as context
    if search_result['count'] > 0:
        answer = answer_question(
            "What is RecallOS?",
            search_result['results']
        )
        
        if "error" in answer:
            print(f"❌ FAILED: {answer['error']}")
        else:
            print(f"✅ PASSED")
            print(f"   Answer: {answer['answer'][:150]}...")
            print(f"   Sources: {len(answer['sources'])}")
    else:
        print("⚠️  SKIPPED: No search results to use as context")
except Exception as e:
    print(f"❌ FAILED: {e}")

# ==================== TEST 5: Full Audio Processing ====================
print("\n" + "="*70)
print("TEST 5: Complete Audio Processing Workflow")
print("="*70)

try:
    process_result = upload_and_process_audio("test_audio.mp3")
    
    if "error" in process_result:
        print(f"❌ FAILED: {process_result['error']}")
    else:
        print(f"✅ PASSED")
        print(f"   File ID: {process_result['file_id']}")
        print(f"   Duration: {process_result['duration']:.1f}s")
        print(f"   Segments stored: {process_result['segments_stored']}")
        print(f"   Preview: {process_result['transcript_preview'][:100]}...")
except Exception as e:
    print(f"❌ FAILED: {e}")

time.sleep(3)  # Wait for indexing

# ==================== TEST 6: Query Workflow ====================
print("\n" + "="*70)
print("TEST 6: Complete Query Workflow")
print("="*70)

try:
    query_result = query_memory_tool("What company is conducting the interview?")
    
    if "error" in query_result:
        print(f"❌ FAILED: {query_result['error']}")
    else:
        print(f"✅ PASSED")
        print(f"   Query: {query_result['query']}")
        print(f"   Answer: {query_result['answer'][:150]}...")
        print(f"   Memories used: {query_result['memories_used']}")
        print(f"   Sources: {len(query_result['sources'])}")
except Exception as e:
    print(f"❌ FAILED: {e}")

# ==================== SUMMARY ====================
print("\n" + "="*70)
print("✅ TEST SUITE COMPLETE")
print("="*70)
print("\n📊 Test Summary:")
print("   1. Transcription: Check output above")
print("   2. Memory Storage: Check output above")
print("   3. Memory Search: Check output above")
print("   4. Answer Generation: Check output above")
print("   5. Audio Processing Workflow: Check output above")
print("   6. Query Workflow: Check output above")
print("\n🎯 If all tests show ✅ PASSED, RecallOS is working perfectly!")
print("="*70)