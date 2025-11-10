import sys
from pathlib import Path

# Add agents/orchestrator to path
sys.path.insert(0, str(Path(__file__).parent / 'agents' / 'orchestrator'))

from main import orchestrator

print("="*70)
print("🚀 TESTING RECALLOS WITH GOOGLE ADK")
print("="*70)

# Test 1: Upload audio
print("\n📋 TEST 1: Upload and Process Audio")
print("-"*70)

result1 = orchestrator.run(
    "Upload and process the audio file at test_audio.mp3"
)
print("\n" + str(result1))

# Wait for indexing
import time
print("\n⏳ Waiting for memory indexing...")
time.sleep(3)

# Test 2: Query
print("\n📋 TEST 2: Query Memory")
print("-"*70)

result2 = orchestrator.run(
    "What company is conducting the interview?"
)
print("\n" + str(result2))

result3 = orchestrator.run(
    "What role is Amit applying for?"
)
print("\n" + str(result3))

print("\n" + "="*70)
print("✅ ADK TEST COMPLETE!")
print("="*70)