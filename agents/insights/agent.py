# REMOVE the sys.path manipulation block entirely

from google.adk import Agent
from shared.pinecone_client import PineconeClient
from shared.embeddings import get_query_embedding
import google.generativeai as genai
from dotenv import load_dotenv
import os
from collections import Counter, defaultdict
import json  # <-- add this


load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
gemini_model = genai.GenerativeModel('gemini-2.0-flash-exp')
db = PineconeClient()

def find_cross_conversation_patterns(topic: str, min_occurrences: int = 3) -> dict:
    """
    NOVEL FEATURE: Find patterns across ALL conversations.
    
    Analyzes multiple audio files to find:
    - Recurring topics
    - Decision evolution over time
    - Speaker patterns
    - Timeline of discussions
    """
    print(f"\n🔍 CROSS-CONVERSATION ANALYSIS: {topic}")
    print(f"   Searching across ALL memories for patterns...")
    
    # Get many results to analyze patterns
    query_embedding = get_query_embedding(topic)
    matches = db.search(query_embedding, top_k=50)  # Get many results
    
    # Group by file_id and speaker
    by_file = defaultdict(list)
    by_speaker = defaultdict(list)
    by_time = []
    
    for match in matches:
        metadata = match.metadata
        file_id = metadata.get('file_id', 'unknown')
        speaker = metadata.get('speaker', 'Unknown')
        timestamp = metadata.get('timestamp_start', 0)
        
        by_file[file_id].append({
            'text': metadata.get('text', ''),
            'score': match.score,
            'timestamp': timestamp,
            'speaker': speaker
        })
        
        by_speaker[speaker].append({
            'text': metadata.get('text', ''),
            'file_id': file_id,
            'timestamp': timestamp
        })
        
        by_time.append({
            'text': metadata.get('text', ''),
            'file_id': file_id,
            'speaker': speaker,
            'timestamp': timestamp,
            'created_at': metadata.get('created_at', '')
        })
    
    # Analyze patterns with Gemini
    analysis_prompt = f"""Analyze these cross-conversation patterns about "{topic}":

FILES ANALYZED: {len(by_file)}
TOTAL MENTIONS: {len(matches)}
SPEAKERS: {list(by_speaker.keys())}

PATTERN DATA:
{json.dumps({
    'by_file': {k: len(v) for k, v in by_file.items()},
    'by_speaker': {k: len(v) for k, v in by_speaker.items()},
    'sample_mentions': [m['text'][:100] for m in by_time[:5]]
}, indent=2)}

PROVIDE INSIGHTS:
1. What patterns emerge across conversations?
2. How has the discussion evolved over time?
3. Which speakers are most engaged with this topic?
4. What decisions or conclusions have been made?
5. Are there any contradictions or changes in position?

Format as structured JSON with actionable insights."""

    response = gemini_model.generate_content(analysis_prompt)
    insights_text = response.text.strip()
    
    print(f"   📊 Analyzed {len(by_file)} conversations")
    print(f"   👥 {len(by_speaker)} speakers found")
    print(f"   💬 {len(matches)} relevant segments")
    
    return {
        'topic': topic,
        'conversations_analyzed': len(by_file),
        'total_mentions': len(matches),
        'speakers': list(by_speaker.keys()),
        'speaker_distribution': {k: len(v) for k, v in by_speaker.items()},
        'file_distribution': {k: len(v) for k, v in by_file.items()},
        'insights': insights_text,
        'timeline': sorted(by_time, key=lambda x: x.get('created_at', ''))[:10]
    }

def get_topic_evolution(topic: str) -> dict:
    """
    Track how discussion about a topic has evolved over time.
    """
    print(f"\n📈 TOPIC EVOLUTION: {topic}")
    
    query_embedding = get_query_embedding(topic)
    matches = db.search(query_embedding, top_k=30)
    
    # Sort by time
    timeline = []
    for match in matches:
        metadata = match.metadata
        timeline.append({
            'text': metadata.get('text', ''),
            'created_at': metadata.get('created_at', ''),
            'speaker': metadata.get('speaker', 'Unknown'),
            'file_id': metadata.get('file_id', 'unknown'),
            'score': match.score
        })
    
    timeline.sort(key=lambda x: x['created_at'])
    
    # Analyze evolution
    evolution_prompt = f"""Analyze how discussion about "{topic}" has evolved:

TIMELINE DATA (chronological):
{json.dumps(timeline, indent=2)}

PROVIDE:
1. Early discussion points
2. Mid-term developments
3. Recent conclusions
4. Overall trajectory
5. Key inflection points

Return structured analysis."""

    response = gemini_model.generate_content(evolution_prompt)
    
    print(f"   ✅ Tracked {len(timeline)} mentions over time")
    
    return {
        'topic': topic,
        'timeline_points': len(timeline),
        'evolution_analysis': response.text,
        'chronological_data': timeline
    }

# Create insights agent
insights_agent = Agent(
    model='gemini-2.0-flash-exp',
    name='insights_agent',
    description='Finds patterns and insights across multiple conversations - NOVEL FEATURE',
    tools=[find_cross_conversation_patterns, get_topic_evolution]
)

print("✅ Insights Agent initialized (Cross-Conversation Analysis)")