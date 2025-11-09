from python_a2a import A2AClient, Message, MessageRole, TextContent
import json

print("=== Testing Transcription Agent ===\n")

client = A2AClient("http://localhost:10001/a2a")

# Test transcription
audio_path = "test_audio.mp3"  # Update with your file name
print(f"Transcribing: {audio_path}")

msg = Message(
    role=MessageRole.USER,
    content=TextContent(text=json.dumps({
        "skill": "transcribe",
        "audio_path": audio_path
    }))
)

response = client.send_message(msg)
result = json.loads(response.content.text)

if "error" in result:
    print(f"❌ Error: {result['error']}")
else:
    print(f"\n✅ Transcription Complete!")
    print(f"Language: {result['language']}")
    print(f"Duration: {result['duration']:.1f}s")
    print(f"Segments: {len(result['segments'])}")
    print(f"\nFull Text:\n{result['text']}")
    
    if result['segments']:
        print(f"\nFirst 3 segments:")
        for seg in result['segments'][:3]:
            print(f"  [{seg['start']:.1f}s - {seg['end']:.1f}s] {seg['text']}")