import sys
from pathlib import Path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from google.adk import Agent
from shared.pinecone_client import PineconeClient
from shared.embeddings import get_document_embedding, get_query_embedding
from groq import Groq
import google.generativeai as genai
from dotenv import load_dotenv
import os
import uuid
from datetime import datetime

load_dotenv()

# Initialize all clients
db = PineconeClient()
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
gemini_model = genai.GenerativeModel('gemini-2.0-flash-exp')

# ==================== TRANSCRIPTION FUNCTIONS ====================

def transcribe_audio(audio_path: str) -> dict:
    """Transcribe audio file using Groq Whisper."""
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
        
    except Exception as e:
        return {"error": f"Transcription failed: {str(e)}"}

# ==================== MEMORY FUNCTIONS ====================

def store_memory(text: str, metadata: dict = None) -> dict:
    """Store a memory chunk in the vector database."""
    memory_id = f"mem_{uuid.uuid4().hex[:8]}"
    embedding = get_document_embedding(text)
    
    full_metadata = {
        "text": text,
        "created_at": datetime.now().isoformat(),
        **(metadata or {})
    }
    
    db.store(
        id=memory_id,
        embedding=embedding,
        metadata=full_metadata
    )
    
    print(f"✅ Stored memory: {memory_id} - {text[:50]}...")
    return {
        "id": memory_id,
        "status": "stored",
        "text": text[:100]
    }

def search_memory(query: str, top_k: int = 5) -> dict:
    """Search for similar memories using semantic search."""
    query_embedding = get_query_embedding(query)
    matches = db.search(query_embedding, top_k=top_k)
    
    results = [{
        "id": match.id,
        "score": match.score,
        "text": match.metadata.get("text", ""),
        "metadata": {k: v for k, v in match.metadata.items() if k != "text"}
    } for match in matches]
    
    print(f"🔍 Found {len(results)} results for: '{query}'")
    for i, r in enumerate(results[:3], 1):
        print(f"   {i}. Score {r['score']:.3f}: {r['text'][:60]}...")
    
    return {
        "results": results,
        "count": len(results),
        "query": query
    }

# ==================== SYNTHESIS FUNCTIONS ====================

def answer_question(query: str, context: list) -> dict:
    """Generate intelligent answer from query and context memories."""
    # Format context
    context_text = ""
    for i, memory in enumerate(context, 1):
        text = memory.get('text', '')
        metadata = memory.get('metadata', {})
        speaker = metadata.get('speaker', 'Unknown')
        score = memory.get('score', 0)
        
        context_text += f"[Memory #{i}] (Relevance: {score:.2f})\n"
        context_text += f"Speaker: {speaker}\n"
        context_text += f"Content: {text}\n\n"
    
    prompt = f"""You are RecallOS, an AI memory assistant. Answer the user's question based ONLY on the provided conversation memories.

CONVERSATION MEMORIES:
{context_text}

USER QUESTION: {query}

INSTRUCTIONS:
1. Answer the question directly and concisely
2. Cite specific memories using [Memory #N] format
3. If memories mention speakers, include who said what
4. If the memories don't contain the answer, say "I don't have information about that in your memories"
5. Be natural and conversational

ANSWER:"""

    response = gemini_model.generate_content(prompt)
    answer = response.text
    
    sources = [{
        "id": m.get('id'),
        "text": m.get('text', '')[:100],
        "score": m.get('score', 0),
        "metadata": m.get('metadata', {})
    } for m in context]
    
    print(f"💬 Generated answer for: '{query[:50]}...'")
    return {
        "answer": answer,
        "sources": sources,
        "query": query
    }

# ==================== ORCHESTRATOR WORKFLOWS ====================

def upload_and_process_audio(audio_path: str) -> dict:
    """Complete workflow: transcribe audio and store in memory."""
    print(f"\n{'='*60}")
    print(f"🎬 PROCESSING AUDIO: {audio_path}")
    print(f"{'='*60}")
    
    # Step 1: Transcribe
    print("\n[1/2] 🎙️ Transcribing audio...")
    transcript_data = transcribe_audio(audio_path)
    
    if "error" in transcript_data:
        return {"error": f"Transcription failed: {transcript_data['error']}"}
    
    print(f"   ✅ Transcribed {len(transcript_data['segments'])} segments")
    
    # Step 2: Store segments
    print("\n[2/2] 💾 Storing in memory...")
    file_id = f"audio_{uuid.uuid4().hex[:8]}"
    stored_count = 0
    
    for i, segment in enumerate(transcript_data['segments']):
        store_memory(
            text=segment['text'],
            metadata={
                "file_id": file_id,
                "segment_index": i,
                "timestamp_start": segment['start'],
                "timestamp_end": segment['end'],
                "speaker": segment.get('speaker', 'Unknown'),
                "audio_file": audio_path
            }
        )
        stored_count += 1
    
    print(f"   ✅ Stored {stored_count} memory chunks")
    print(f"\n✅ Processing complete!")
    print(f"{'='*60}\n")
    
    return {
        "status": "success",
        "file_id": file_id,
        "audio_path": audio_path,
        "duration": transcript_data['duration'],
        "segments_stored": stored_count,
        "transcript_preview": transcript_data['text'][:200] + "..."
    }

def query_memory_tool(query: str) -> dict:
    """Answer user query by searching memory and generating response."""
    print(f"\n{'='*60}")
    print(f"❓ QUERY: {query}")
    print(f"{'='*60}")
    
    # Step 1: Search
    print("\n[1/2] 🔍 Searching memories...")
    search_data = search_memory(query, top_k=5)
    print(f"   ✅ Found {search_data['count']} relevant memories")
    
    # Step 2: Generate answer
    print("\n[2/2] 💬 Generating answer...")
    synthesis_data = answer_question(query, search_data['results'])
    print(f"   ✅ Answer generated")
    print(f"{'='*60}\n")
    
    return {
        "query": query,
        "answer": synthesis_data['answer'],
        "sources": synthesis_data['sources'],
        "memories_used": search_data['count']
    }

# ==================== CREATE AGENT ====================

orchestrator = Agent(
    model='gemini-2.0-flash-exp',
    name='recallos_orchestrator',
    description='Orchestrates audio processing and memory queries for RecallOS',
    tools=[upload_and_process_audio, query_memory_tool]
)

print("✅ RecallOS Orchestrator initialized")