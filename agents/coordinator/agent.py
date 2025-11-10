import sys
from pathlib import Path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from google.adk import Agent
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
gemini_model = genai.GenerativeModel('gemini-2.0-flash-exp')

def plan_execution(task_description: str) -> dict:
    """
    Agent Planning - Analyzes task and creates execution plan.
    Decides which agents to use and in what order.
    """
    print(f"\n🧠 PLANNING: {task_description}")
    
    planning_prompt = f"""You are an AI Agent Coordinator. Analyze this task and create an execution plan.

TASK: {task_description}

AVAILABLE AGENTS:
1. transcription_agent - Transcribes audio files (Google Speech-to-Text with diarization)
2. memory_agent - Stores and searches memories (Pinecone vector DB)
3. synthesis_agent - Generates intelligent answers (Gemini 2.0)
4. insights_agent - Finds patterns across conversations
5. timeline_agent - Creates temporal visualizations

CREATE EXECUTION PLAN:
{{
    "task_type": "upload|query|insight|analysis",
    "agents_required": ["agent1", "agent2"],
    "execution_strategy": "sequential|parallel|hybrid",
    "estimated_complexity": "low|medium|high",
    "special_requirements": ["requirement1"],
    "optimization_hints": ["hint1"]
}}

Respond ONLY with valid JSON."""

    response = gemini_model.generate_content(planning_prompt)
    plan_text = response.text.strip()
    
    # Extract JSON
    if '```json' in plan_text:
        plan_text = plan_text.split('```json')[1].split('```')[0].strip()
    
    plan = json.loads(plan_text)
    
    print(f"   📋 Task Type: {plan['task_type']}")
    print(f"   🤖 Agents: {', '.join(plan['agents_required'])}")
    print(f"   ⚡ Strategy: {plan['execution_strategy']}")
    print(f"   📊 Complexity: {plan['estimated_complexity']}")
    
    return plan

def negotiate_resources(agents: list, task_complexity: str) -> dict:
    """
    Agent Negotiation - Agents negotiate resources and priorities.
    """
    print(f"\n🤝 NEGOTIATING: {len(agents)} agents for {task_complexity} complexity task")
    
    negotiation_prompt = f"""Agents are negotiating resource allocation.

AGENTS INVOLVED: {', '.join(agents)}
TASK COMPLEXITY: {task_complexity}

NEGOTIATE:
- Processing priority
- Resource allocation
- Fallback strategies

Return JSON:
{{
    "primary_agent": "agent_name",
    "support_agents": ["agent1"],
    "resource_allocation": {{"agent1": "high|medium|low"}},
    "fallback_chain": ["agent1", "agent2"]
}}"""

    response = gemini_model.generate_content(negotiation_prompt)
    result_text = response.text.strip()
    
    if '```json' in result_text:
        result_text = result_text.split('```json')[1].split('```')[0].strip()
    
    negotiation = json.loads(result_text)
    
    print(f"   👑 Primary: {negotiation['primary_agent']}")
    print(f"   🔧 Support: {', '.join(negotiation['support_agents'])}")
    
    return negotiation

# Create coordinator agent
coordinator_agent = Agent(
    model='gemini-2.0-flash-exp',
    name='coordinator_agent',
    description='Intelligent coordinator that plans tasks and coordinates multiple agents',
    tools=[plan_execution, negotiate_resources]
)

print("✅ Coordinator Agent initialized")