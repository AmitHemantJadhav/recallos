import sys
sys.path.insert(0, 'agents/orchestrator')
from main import intelligent_query, find_cross_conversation_patterns

print("="*70)
print("🧠 TESTING INTELLIGENT QUERY & CROSS-CONVERSATION INSIGHTS")
print("="*70)

# Test 1: Regular intelligent query
print("\n📋 TEST 1: Intelligent Query with Planning")
print("-"*70)
result1 = intelligent_query("What role is Amit applying for?")
print(f"\n✅ Plan: {result1.get('execution_plan', {}).get('task_type')}")
print(f"✅ Strategy: {result1.get('execution_plan', {}).get('execution_strategy')}")
print(f"✅ Answer: {result1.get('answer', '')[:150]}...")

# Test 2: Cross-conversation insights
print("\n\n📋 TEST 2: Cross-Conversation Pattern Analysis (NOVEL)")
print("-"*70)
insights = find_cross_conversation_patterns("Prepify interview Google")
print(f"\n✅ Conversations analyzed: {insights['conversations_analyzed']}")
print(f"✅ Total mentions: {insights['total_mentions']}")
print(f"✅ Speakers: {insights['speakers']}")
print(f"\n📊 INSIGHTS:\n{insights['insights'][:500]}...")

# Test 3: Insights-triggered query
print("\n\n📋 TEST 3: Query Triggering Insights Agent")
print("-"*70)
result3 = intelligent_query("What patterns exist across conversations about interviews?")
if result3.get('type') == 'insights':
    print("✅ Insights agent automatically triggered!")
    print(f"✅ Found patterns in {result3['insights']['conversations_analyzed']} conversations")
else:
    print("✅ Regular query executed")

print("\n" + "="*70)
print("✅ INTELLIGENT QUERY TESTS COMPLETE!")
print("="*70)