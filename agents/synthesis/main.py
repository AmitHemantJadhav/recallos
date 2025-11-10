import sys
from pathlib import Path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from google.adk import Agent
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
gemini_model = genai.GenerativeModel('gemini-2.0-flash-exp')

def answer_question(query: str, context: list) -> dict:
    """
    Generate intelligent answer from query and context memories.
    
    Args:
        query: User's question
        context: List of memory chunks with scores
    
    Returns:
        Dictionary with answer and sources
    """
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

# Create the agent
synthesis_agent = Agent(
    model='gemini-2.0-flash-exp',
    name='synthesis_agent',
    description='Generates intelligent answers from retrieved memories',
    tools=[answer_question]
)

print("✅ Synthesis Agent initialized")