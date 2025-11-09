import sys
from pathlib import Path

# Add root directory to Python path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from python_a2a import A2AServer, run_server, Message, MessageRole
from groq import Groq
from dotenv import load_dotenv
import os
import json

load_dotenv()

class TranscriptionAgent(A2AServer):
    
    def __init__(self):
        super().__init__(
            url="http://localhost:10001",
            name="Transcription Agent",
            description="Transcribes audio files using Groq Whisper (70x realtime)"
        )
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        print("✅ Transcription Agent initialized with Groq Whisper-Large-V3")
    
    def handle_message(self, message: Message) -> Message:
        """Route messages to transcription skills"""
        try:
            content = message.content.text if hasattr(message.content, 'text') else str(message.content)
            data = json.loads(content)
            
            skill = data.get('skill')
            
            if skill == 'transcribe':
                result = self.transcribe(data.get('audio_path'))
            else:
                result = {"error": f"Unknown skill: {skill}"}
            
            return Message(
                role=MessageRole.AGENT,
                content=json.dumps(result)
            )
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return Message(
                role=MessageRole.AGENT,
                content=json.dumps({"error": str(e)})
            )
    
    def transcribe(self, audio_path: str) -> dict:
        """Transcribe audio using Groq Whisper"""
        print(f"🎙️ Transcribing: {audio_path}")
        
        try:
            with open(audio_path, "rb") as audio_file:
                transcription = self.client.audio.transcriptions.create(
                    file=(audio_path, audio_file.read()),
                    model="whisper-large-v3",
                    response_format="verbose_json",
                    temperature=0.0
                )
            
            # Parse response
            segments = []
            if hasattr(transcription, 'segments') and transcription.segments:
                for seg in transcription.segments:
                    segments.append({
                        "text": seg['text'],
                        "start": seg['start'],
                        "end": seg['end'],
                        "speaker": "Speaker 1"
                    })
            
            duration = segments[-1]["end"] if segments else 0
            
            result = {
                "text": transcription.text,
                "segments": segments,
                "language": transcription.language if hasattr(transcription, 'language') else "en",
                "duration": duration
            }
            
            print(f"✅ Transcribed {len(segments)} segments ({duration:.1f}s)")
            print(f"   Text: {transcription.text[:100]}...")
            
            return result
            
        except FileNotFoundError:
            error = f"Audio file not found: {audio_path}"
            print(f"❌ {error}")
            return {"error": error}
        except Exception as e:
            error = f"Transcription failed: {str(e)}"
            print(f"❌ {error}")
            import traceback
            traceback.print_exc()
            return {"error": error}

if __name__ == "__main__":
    agent = TranscriptionAgent()
    run_server(agent, host="0.0.0.0", port=10001)