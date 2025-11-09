import sys
from pathlib import Path

# Add root directory to Python path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from python_a2a import A2AServer, A2AClient, run_server, Message, MessageRole, TextContent
from dotenv import load_dotenv
import json
import uuid

load_dotenv()

class OrchestratorAgent(A2AServer):
    
    def __init__(self):
        super().__init__(
            url="http://localhost:10000",
            name="RecallOS Orchestrator",
            description="Orchestrates transcription, memory storage, and intelligent query answering"
        )
        
        # Connect to other agents
        self.transcription_client = A2AClient("http://localhost:10001/a2a")
        self.memory_client = A2AClient("http://localhost:10002/a2a")
        self.synthesis_client = A2AClient("http://localhost:10003/a2a")
        
        print("✅ Orchestrator initialized")
        print("   Connected to: Transcription, Memory, Synthesis agents")
    
    def handle_message(self, message: Message) -> Message:
        """Route user requests to appropriate workflow"""
        try:
            content = message.content.text if hasattr(message.content, 'text') else str(message.content)
            data = json.loads(content)
            
            action = data.get('action')
            
            if action == 'upload_audio':
                result = self.process_audio(data.get('audio_path'))
            elif action == 'query':
                result = self.answer_query(data.get('query'))
            else:
                result = {"error": f"Unknown action: {action}"}
            
            return Message(
                role=MessageRole.AGENT,
                content=json.dumps(result)
            )
            
        except Exception as e:
            print(f"❌ Orchestrator error: {e}")
            import traceback
            traceback.print_exc()
            return Message(
                role=MessageRole.AGENT,
                content=json.dumps({"error": str(e)})
            )
    
    def process_audio(self, audio_path: str) -> dict:
        """
        Complete audio processing workflow:
        1. Transcribe audio
        2. Chunk transcript
        3. Store in memory
        """
        print(f"\n{'='*60}")
        print(f"🎬 PROCESSING AUDIO: {audio_path}")
        print(f"{'='*60}")
        
        # Step 1: Transcribe
        print("\n[1/3] 🎙️ Transcribing audio...")
        transcribe_msg = Message(
            role=MessageRole.USER,
            content=TextContent(text=json.dumps({
                "skill": "transcribe",
                "audio_path": audio_path
            }))
        )
        
        transcribe_response = self.transcription_client.send_message(transcribe_msg)
        transcript_data = json.loads(transcribe_response.content.text)
        
        if "error" in transcript_data:
            return {"error": f"Transcription failed: {transcript_data['error']}"}
        
        print(f"   ✅ Transcribed {len(transcript_data['segments'])} segments")
        
        # Step 2: Chunk and store
        print("\n[2/3] 💾 Storing in memory...")
        file_id = f"audio_{uuid.uuid4().hex[:8]}"
        stored_count = 0
        
        for i, segment in enumerate(transcript_data['segments']):
            # Store each segment as a memory
            store_msg = Message(
                role=MessageRole.USER,
                content=TextContent(text=json.dumps({
                    "skill": "store_memory",
                    "text": segment['text'],
                    "metadata": {
                        "file_id": file_id,
                        "segment_index": i,
                        "timestamp_start": segment['start'],
                        "timestamp_end": segment['end'],
                        "speaker": segment.get('speaker', 'Unknown'),
                        "audio_file": audio_path
                    }
                }))
            )
            
            store_response = self.memory_client.send_message(store_msg)
            stored_count += 1
        
        print(f"   ✅ Stored {stored_count} memory chunks")
        
        # Step 3: Return summary
        print("\n[3/3] ✅ Processing complete!")
        print(f"{'='*60}\n")
        
        return {
            "status": "success",
            "file_id": file_id,
            "audio_path": audio_path,
            "duration": transcript_data['duration'],
            "segments_stored": stored_count,
            "transcript_preview": transcript_data['text'][:200] + "..."
        }
    
    def answer_query(self, query: str) -> dict:
        """
        Answer user query workflow:
        1. Search memory
        2. Generate answer with synthesis
        """
        print(f"\n{'='*60}")
        print(f"❓ QUERY: {query}")
        print(f"{'='*60}")
        
        # Step 1: Search memory
        print("\n[1/2] 🔍 Searching memories...")
        search_msg = Message(
            role=MessageRole.USER,
            content=TextContent(text=json.dumps({
                "skill": "search_memory",
                "query": query,
                "top_k": 5
            }))
        )
        
        search_response = self.memory_client.send_message(search_msg)
        search_data = json.loads(search_response.content.text)
        
        print(f"   ✅ Found {search_data['count']} relevant memories")
        
        # Step 2: Generate answer
        print("\n[2/2] 💬 Generating answer...")
        synthesis_msg = Message(
            role=MessageRole.USER,
            content=TextContent(text=json.dumps({
                "skill": "answer_question",
                "query": query,
                "context": search_data['results']
            }))
        )
        
        synthesis_response = self.synthesis_client.send_message(synthesis_msg)
        synthesis_data = json.loads(synthesis_response.content.text)
        
        print(f"   ✅ Answer generated")
        print(f"{'='*60}\n")
        
        return {
            "query": query,
            "answer": synthesis_data['answer'],
            "sources": synthesis_data['sources'],
            "memories_used": search_data['count']
        }

if __name__ == "__main__":
    agent = OrchestratorAgent()
    run_server(agent, host="0.0.0.0", port=10000)