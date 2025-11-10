import sys
from pathlib import Path
import importlib.util

# Add root to path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

# Import coordinator functions using importlib
coordinator_path = Path(__file__).parent.parent / 'coordinator' / 'agent.py'
coordinator_spec = importlib.util.spec_from_file_location("coordinator_module", coordinator_path)
coordinator_module = importlib.util.module_from_spec(coordinator_spec)
coordinator_spec.loader.exec_module(coordinator_module)
plan_execution = coordinator_module.plan_execution
negotiate_resources = coordinator_module.negotiate_resources

# Import insights functions using importlib
insights_path = Path(__file__).parent.parent / 'insights' / 'agent.py'
insights_spec = importlib.util.spec_from_file_location("insights_module", insights_path)
insights_module = importlib.util.module_from_spec(insights_spec)
insights_spec.loader.exec_module(insights_module)
find_cross_conversation_patterns = insights_module.find_cross_conversation_patterns
get_topic_evolution = insights_module.get_topic_evolution

# Now import everything else
from google.adk import Agent
from shared.pinecone_client import PineconeClient
from shared.embeddings import get_document_embedding, get_query_embedding
from shared.google_services import upload_to_storage, save_session, get_session, log_agent_action
from google.cloud import speech
import google.generativeai as genai
from dotenv import load_dotenv
import os
import uuid
from datetime import datetime
import json
import time

load_dotenv()

# Initialize all clients
db = PineconeClient()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "/app/speech-key.json")
speech_client = speech.SpeechClient()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
gemini_model = genai.GenerativeModel('gemini-2.0-flash-exp')



# ==================== TRANSCRIPTION FUNCTIONS ====================

def transcribe_audio(audio_path: str, gcs_uri: str = None) -> dict:
    """
    Transcribe audio using Google Cloud Speech-to-Text.
    If gcs_uri provided, use long-running operation for large files.
    """
    print(f"🎙️ Transcribing: {audio_path}")
    
    try:
        # If GCS URI provided, use long-running operation (no size limit)
        if gcs_uri:
            print(f"   Using GCS URI: {gcs_uri}")
            
            audio = speech.RecognitionAudio(uri=gcs_uri)
            
            diarization_config = speech.SpeakerDiarizationConfig(
                enable_speaker_diarization=True,
                min_speaker_count=1,
                max_speaker_count=4,
            )
            
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.MP3,
                language_code="en-US",
                enable_word_time_offsets=True,
                enable_automatic_punctuation=True,
                diarization_config=diarization_config,
                model="latest_long",
            )
            
            print("   Starting long-running transcription...")
            operation = speech_client.long_running_recognize(config=config, audio=audio)
            print("   Waiting for operation to complete...")
            response = operation.result(timeout=300)
            
        else:
            # For small files, use synchronous recognition
            with open(audio_path, "rb") as audio_file:
                content = audio_file.read()
            
            audio = speech.RecognitionAudio(content=content)
            
            diarization_config = speech.SpeakerDiarizationConfig(
                enable_speaker_diarization=True,
                min_speaker_count=1,
                max_speaker_count=4,
            )
            
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.MP3,
                language_code="en-US",
                enable_word_time_offsets=True,
                enable_automatic_punctuation=True,
                diarization_config=diarization_config,
                model="latest_long",
            )
            
            print("   Sending to Google Speech API...")
            response = speech_client.recognize(config=config, audio=audio)
        
        # Extract results (same for both methods)
        full_text = ""
        segments = []
        
        for i, result in enumerate(response.results):
            alternative = result.alternatives[0]
            full_text += alternative.transcript + " "
            
            if alternative.words:
                segment_text = alternative.transcript
                start_time = alternative.words[0].start_time.total_seconds()
                end_time = alternative.words[-1].end_time.total_seconds()
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
        
        print(f"✅ Transcribed {len(segments)} segments ({duration:.1f}s)")
        return result
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": f"Google Speech transcription failed: {str(e)}"}

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
# ==================== ENHANCED WORKFLOWS WITH RETRY & LOGGING ====================

def upload_and_process_audio(audio_path: str) -> dict:
    """
    Complete workflow with Cloud Storage, Firestore tracking, and retry logic.
    """
    session_id = f"session_{uuid.uuid4().hex[:8]}"
    file_id = f"audio_{uuid.uuid4().hex[:8]}"
    
    log_agent_action('orchestrator', 'start_processing', {
        'session_id': session_id,
        'file_id': file_id,
        'audio_path': audio_path
    })
    
    print(f"\n{'='*60}")
    print(f"🎬 PROCESSING AUDIO SESSION: {session_id}")
    print(f"{'='*60}")
    
    try:
        # Save initial session to Firestore
        save_session(session_id, {
            'file_id': file_id,
            'status': 'processing',
            'audio_path': audio_path,
            'started_at': datetime.now().isoformat()
        })
        
        # Step 1: Upload to Cloud Storage
        print("\n[1/4] ☁️  Uploading to Cloud Storage...")
        storage_path = f"uploads/{file_id}.mp3"
        
        try:
            gcs_url = upload_to_storage(audio_path, storage_path)
            log_agent_action('storage', 'upload_complete', {'gcs_url': gcs_url})
            print(f"   ✅ Uploaded to {gcs_url}")
        except Exception as e:
            log_agent_action('storage', 'upload_failed', {'error': str(e)})
            raise
        
        # Step 2: Transcribe with retry
        print("\n[2/4] 🎙️ Transcribing audio...")
        max_retries = 3
        transcript_data = None
        
        for attempt in range(max_retries):
            try:
                transcript_data = transcribe_audio(audio_path, gcs_uri=gcs_url)
                
                if "error" not in transcript_data:
                    log_agent_action('transcription', 'success', {
                        'segments': len(transcript_data['segments']),
                        'duration': transcript_data['duration']
                    })
                    break
                else:
                    raise Exception(transcript_data['error'])
                    
            except Exception as e:
                log_agent_action('transcription', 'retry', {
                    'attempt': attempt + 1,
                    'error': str(e)
                })
                
                if attempt == max_retries - 1:
                    save_session(session_id, {'status': 'failed', 'error': str(e)})
                    return {"error": f"Transcription failed after {max_retries} attempts: {str(e)}"}
                
                time.sleep(2 ** attempt)  # Exponential backoff
        
        print(f"   ✅ Transcribed {len(transcript_data['segments'])} segments")
        
        # Step 3: Store in memory with parallel processing simulation
        print("\n[3/4] 💾 Storing in memory...")
        stored_count = 0
        failed_count = 0
        
        for i, segment in enumerate(transcript_data['segments']):
            try:
                store_memory(
                    text=segment['text'],
                    metadata={
                        "session_id": session_id,
                        "file_id": file_id,
                        "segment_index": i,
                        "timestamp_start": segment['start'],
                        "timestamp_end": segment['end'],
                        "speaker": segment.get('speaker', 'Unknown'),
                        "audio_file": audio_path,
                        "gcs_url": gcs_url
                    }
                )
                stored_count += 1
            except Exception as e:
                log_agent_action('memory', 'store_failed', {
                    'segment': i,
                    'error': str(e)
                })
                failed_count += 1
        
        log_agent_action('memory', 'batch_complete', {
            'stored': stored_count,
            'failed': failed_count
        })
        
        print(f"   ✅ Stored {stored_count} chunks ({failed_count} failed)")
        
        # Step 4: Update Firestore
        print("\n[4/4] 📊 Updating session...")
        save_session(session_id, {
            'status': 'completed',
            'file_id': file_id,
            'gcs_url': gcs_url,
            'duration': transcript_data['duration'],
            'segments_stored': stored_count,
            'segments_failed': failed_count,
            'completed_at': datetime.now().isoformat()
        })
        
        print(f"\n✅ Processing complete!")
        print(f"{'='*60}\n")
        
        return {
            "status": "success",
            "session_id": session_id,
            "file_id": file_id,
            "gcs_url": gcs_url,
            "audio_path": audio_path,
            "duration": transcript_data['duration'],
            "segments_stored": stored_count,
            "segments_failed": failed_count,
            "transcript_preview": transcript_data['text'][:200] + "..."
        }
        
    except Exception as e:
        log_agent_action('orchestrator', 'processing_failed', {
            'session_id': session_id,
            'error': str(e)
        })
        
        save_session(session_id, {
            'status': 'failed',
            'error': str(e),
            'failed_at': datetime.now().isoformat()
        })
        
        return {"error": f"Processing failed: {str(e)}"}

def query_memory_tool(query: str, session_id: str = None) -> dict:
    """
    Enhanced query with session tracking and agent decision-making.
    """
    query_id = f"query_{uuid.uuid4().hex[:8]}"
    
    log_agent_action('orchestrator', 'query_start', {
        'query_id': query_id,
        'query': query,
        'session_id': session_id
    })
    
    print(f"\n{'='*60}")
    print(f"❓ QUERY: {query}")
    print(f"{'='*60}")
    
    try:
        # Step 1: Determine optimal search parameters using Gemini
        print("\n[1/3] 🤔 Analyzing query...")
        
        analysis_prompt = f"""Analyze this query and suggest optimal search parameters:
Query: "{query}"

Provide JSON response:
{{
    "search_depth": <number 3-10>,
    "query_type": "factual|temporal|analytical",
    "requires_synthesis": true|false
}}
"""
        
        analysis_response = gemini_model.generate_content(analysis_prompt)
        analysis_text = analysis_response.text.strip()
        
        # Extract JSON from response
        if '```json' in analysis_text:
            analysis_text = analysis_text.split('```json')[1].split('```')[0].strip()
        
        params = json.loads(analysis_text)
        
        log_agent_action('query_analyzer', 'analysis_complete', params)
        print(f"   📊 Query type: {params['query_type']}, Depth: {params['search_depth']}")
        
        # Step 2: Search with optimized parameters
        print(f"\n[2/3] 🔍 Searching {params['search_depth']} memories...")
        search_data = search_memory(query, top_k=params['search_depth'])
        
        log_agent_action('memory', 'search_complete', {
            'results': search_data['count'],
            'top_score': search_data['results'][0]['score'] if search_data['results'] else 0
        })
        
        print(f"   ✅ Found {search_data['count']} relevant memories")
        
        # Step 3: Generate answer
        print("\n[3/3] 💬 Generating answer...")
        synthesis_data = answer_question(query, search_data['results'])
        
        log_agent_action('synthesis', 'answer_generated', {
            'query_id': query_id,
            'sources_used': len(synthesis_data['sources'])
        })
        
        print(f"   ✅ Answer generated with {len(synthesis_data['sources'])} sources")
        print(f"{'='*60}\n")
        
        result = {
            "query_id": query_id,
            "query": query,
            "answer": synthesis_data['answer'],
            "sources": synthesis_data['sources'],
            "memories_used": search_data['count'],
            "query_analysis": params
        }
        
        # Save query to Firestore if session provided
        if session_id:
            session = get_session(session_id)
            if session:
                queries = session.get('queries', [])
                queries.append({
                    'query_id': query_id,
                    'query': query,
                    'timestamp': datetime.now().isoformat()
                })
                save_session(session_id, {'queries': queries})
        
        return result
        
    except Exception as e:
        log_agent_action('orchestrator', 'query_failed', {
            'query_id': query_id,
            'error': str(e)
        })
        
        return {"error": f"Query failed: {str(e)}"}
    
def intelligent_query(query: str) -> dict:
    """
    Use coordinator to plan and execute intelligent multi-agent query.
    """
    # Step 1: Plan
    plan = plan_execution(f"Answer this query: {query}")
    
    # Step 2: Check if insights needed
    if 'insights' in plan['agents_required'] or 'pattern' in query.lower() or 'across' in query.lower():
        insights = find_cross_conversation_patterns(query)
        return {
            'type': 'insights',
            'plan': plan,
            'insights': insights
        }
    
    # Step 3: Regular query with negotiation
    negotiation = negotiate_resources(plan['agents_required'], plan['estimated_complexity'])
    
    # Step 4: Execute
    result = query_memory_tool(query)
    result['execution_plan'] = plan
    result['resource_negotiation'] = negotiation
    
    return result

# Create the orchestrator agent
orchestrator = Agent(
    model='gemini-2.0-flash-exp',
    name='recallos_orchestrator',
    description='Advanced multi-agent orchestrator with Cloud Storage, Firestore, and intelligent agent coordination',
    tools=[upload_and_process_audio, query_memory_tool]
)

print("✅ Enhanced RecallOS Orchestrator initialized")
print("   📦 Google Services: Speech-to-Text, Storage, Firestore, Logging")
print("   🤖 Agents: Transcription, Memory, Synthesis, Query Analyzer")