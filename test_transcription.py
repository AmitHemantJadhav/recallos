import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from agents.transcription.main import transcribe_audio

print("="*70)
print("🧪 TESTING GOOGLE SPEECH-TO-TEXT TRANSCRIPTION")
print("="*70)

# Test with your audio file
audio_file = "test_audio.mp3"  # Change this to your actual audio file

print(f"\n📁 Testing with: {audio_file}")
print("-"*70)

result = transcribe_audio(audio_file)

if "error" in result:
    print(f"\n❌ TRANSCRIPTION FAILED")
    print(f"Error: {result['error']}")
    print("\nPossible issues:")
    print("1. GOOGLE_CLOUD_PROJECT_ID not set in .env")
    print("2. Speech-to-Text API not enabled")
    print("3. Authentication not configured")
    print("4. Audio file not found")
else:
    print(f"\n✅ TRANSCRIPTION SUCCESSFUL!")
    print("-"*70)
    print(f"Provider: {result.get('provider', 'N/A')}")
    print(f"Duration: {result['duration']:.1f} seconds")
    print(f"Language: {result['language']}")
    print(f"Total segments: {len(result['segments'])}")
    
    # Count speakers
    speakers = set(s['speaker'] for s in result['segments'])
    print(f"Unique speakers: {len(speakers)}")
    print(f"Speakers detected: {', '.join(sorted(speakers))}")
    
    print("\n📝 Full Transcript:")
    print("-"*70)
    print(result['text'])
    
    print("\n🎯 Segments with Speakers:")
    print("-"*70)
    for i, seg in enumerate(result['segments'][:5], 1):  # Show first 5 segments
        print(f"\n[{i}] {seg['speaker']} ({seg['start']:.1f}s - {seg['end']:.1f}s)")
        print(f"    {seg['text']}")
    
    if len(result['segments']) > 5:
        print(f"\n... and {len(result['segments']) - 5} more segments")

print("\n" + "="*70)
print("✅ TEST COMPLETE")
print("="*70)