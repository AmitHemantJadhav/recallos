import sys
from pathlib import Path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from google.adk import Agent
from google.cloud import speech
from dotenv import load_dotenv
import os
import io

load_dotenv()

# Initialize Google Speech client
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
speech_client = speech.SpeechClient()

def transcribe_audio(audio_path: str) -> dict:
    """
    Transcribe audio using Google Cloud Speech-to-Text.
    
    Args:
        audio_path: Path to the audio file
    
    Returns:
        Dictionary with transcript and segments
    """
    print(f"🎙️ Transcribing with Google Speech-to-Text: {audio_path}")
    
    try:
        # Read audio file
        with open(audio_path, "rb") as audio_file:
            content = audio_file.read()
        
        # Configure recognition
        audio = speech.RecognitionAudio(content=content)
        
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.MP3,
            language_code="en-US",
            enable_word_time_offsets=True,
            enable_automatic_punctuation=True,
            enable_speaker_diarization=True,  # Speaker identification!
            diarization_speaker_count=2,  # Assume 2 speakers
            model="latest_long",  # Best model for long audio
        )
        
        print("   Sending to Google Speech API...")
        
        # Perform transcription
        response = speech_client.recognize(config=config, audio=audio)
        
        # Extract results with speaker info
        full_text = ""
        segments = []
        
        for i, result in enumerate(response.results):
            alternative = result.alternatives[0]
            full_text += alternative.transcript + " "
            
            # Extract word-level timestamps and speaker tags
            if alternative.words:
                segment_text = alternative.transcript
                start_time = alternative.words[0].start_time.total_seconds()
                end_time = alternative.words[-1].end_time.total_seconds()
                
                # Get speaker tag from first word
                speaker_tag = getattr(alternative.words[0], 'speaker_tag', 1)
                
                segments.append({
                    "text": segment_text,
                    "start": start_time,
                    "end": end_time,
                    "speaker": f"Speaker {speaker_tag}"
                })
        
        duration = segments[-1]["end"] if segments else 0
        
        result = {
            "text": full_text.strip(),
            "segments": segments,
            "language": "en",
            "duration": duration
        }
        
        print(f"✅ Transcribed {len(segments)} segments ({duration:.1f}s) with Google Speech-to-Text")
        print(f"   Detected speakers: {len(set(s['speaker'] for s in segments))}")
        return result
        
    except FileNotFoundError:
        error = f"Audio file not found: {audio_path}"
        print(f"❌ {error}")
        return {"error": error}
    except Exception as e:
        error = f"Google Speech transcription failed: {str(e)}"
        print(f"❌ {error}")
        import traceback
        traceback.print_exc()
        return {"error": error}

# Create the agent
transcription_agent = Agent(
    model='gemini-2.0-flash-exp',
    name='transcription_agent',
    description='Transcribes audio files using Google Cloud Speech-to-Text with speaker diarization',
    tools=[transcribe_audio]
)

print("✅ Transcription Agent initialized with Google Speech-to-Text")