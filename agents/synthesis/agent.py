import sys
from pathlib import Path

# Add root directory to Python path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from python_a2a import A2AServer, run_server, Message, MessageRole
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

class SynthesisAgent(A2AServer):
    
    def __init__(self):
        super().__init__(
            url="http://localhost:10003",
            name="Synthesis Agent",
            description="Generates intelligent answers from retrieved memories"
        )
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        print("Synthesis Agent initialized with Gemini 2.0 Flash")
    
    def handle_message(self, message: Message) -> Message:
        """
        Route messages to synthesis skills
        """
        try:
            # Parse message
            content = message.content.text if hasattr(message.content, 'text') else str(message.content)
            data = json.loads(content)
            
            skill = data.get('skill')
            
            # Route to skill
            if skill == 'answer_question':
                result = self.answer_question(
                    data.get('query'), 
                    data.get('context', [])
                )
            elif skill == 'summarize':
                result = self.summarize(data.get('text'))
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
    
    def answer_question(self, query: str, context: list) -> dict:
        """
        Generate answer from query and context memories
        
        Args:
            query: User's question
            context: List of memory chunks with scores
        
        Returns:
            {"answer": "...", "sources": [...]}
        """
        # Build prompt with context
        context_text = self._format_context(context)
        
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

        # Generate response
        response = self.model.generate_content(prompt)
        answer = response.text
        
        # Extract sources
        sources = self._extract_sources(context)
        
        print(f"💬 Generated answer for: '{query[:50]}...'")
        print(f"   Used {len(context)} memory chunks")
        
        return {
            "answer": answer,
            "sources": sources,
            "query": query
        }
    
    def summarize(self, text: str) -> dict:
        """Summarize a long text"""
        prompt = f"""Summarize this conversation concisely:

{text}

Summary:"""
        
        response = self.model.generate_content(prompt)
        
        return {
            "summary": response.text
        }
    
    def _format_context(self, context: list) -> str:
        """Format memory chunks for prompt"""
        formatted = []
        for i, memory in enumerate(context, 1):
            text = memory.get('text', '')
            metadata = memory.get('metadata', {})
            speaker = metadata.get('speaker', 'Unknown')
            score = memory.get('score', 0)
            
            formatted.append(
                f"[Memory #{i}] (Relevance: {score:.2f})\n"
                f"Speaker: {speaker}\n"
                f"Content: {text}\n"
            )
        
        return "\n".join(formatted)
    
    def _extract_sources(self, context: list) -> list:
        """Extract source information from context"""
        sources = []
        for memory in context:
            sources.append({
                "id": memory.get('id'),
                "text": memory.get('text', '')[:100],
                "score": memory.get('score', 0),
                "metadata": memory.get('metadata', {})
            })
        return sources

if __name__ == "__main__":
    agent = SynthesisAgent()
    run_server(agent, host="0.0.0.0", port=10003)