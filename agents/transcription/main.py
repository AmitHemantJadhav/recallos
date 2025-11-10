import sys
from pathlib import Path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from google.adk import Agent
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def transcribe_audio(audio_path: str) -> dict:
    """
    Transcribe audio file using Groq Whisper.
    
    Args:
        audio_path: Path to the audio file
    
    Returns:
        Dictionary with transcript and segments
    """
    print(f"🎙️ Transcribing: {audio_path}")
    
    try:
        with open(audio_path, "rb") as audio_file:
            transcription = groq_client.audio.transcriptions.create(
                file=(audio_path, audio_file.read()),
                model="whisper-large-v3",
                response_format="verbose_json",
                temperature=0.0
            )
        
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
        return result
        
    except FileNotFoundError:
        return {"error": f"Audio file not found: {audio_path}"}
    except Exception as e:
        return {"error": f"Transcription failed: {str(e)}"}

# Create the agent
transcription_agent = Agent(
    model='gemini-2.0-flash-exp',
    name='transcription_agent',
    description='Transcribes audio files using Groq Whisper',
    tools=[transcribe_audio]
)

print("✅ Transcription Agent initialized")