"""
Test: Direct Escalation to Ticket Agent
When user sends complaint/escalation, it should create ticket immediately
"""
import sys
import os
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
os.chdir(project_root)

from src.classification.intent_classifier import intent_classifier
from src.rag.pipeline import rag_pipeline

def print_header(title):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)

print_header("TEST: DIRECT ESCALATION → AUTOMATIC TICKET CREATION")

test_scenarios = [
    {
        "query": "I received the wrong device!",
        "expected_intent": "complaint",
        "should_create_ticket": True
    },
    {
        "query": "My item arrived broken and damaged!",
        "expected_intent": "complaint",
        "should_create_ticket": True
    },
    {
        "query": "This is URGENT! I need immediate help!",
        "expected_intent": "escalation_request",
        "should_create_ticket": True
    },
    {
        "query": "I want to speak to a manager NOW!",
        "expected_intent": "escalation_request",
        "should_create_ticket": True
    },
    {
        "query": "What is your return policy?",
        "expected_intent": "faq",
        "should_create_ticket": False
    },
]

for i, scenario in enumerate(test_scenarios, 1):
    print_header(f"SCENARIO {i}: {scenario['query'][:50]}...")
    
    query = scenario['query']
    print(f"\nQuery: {query}\n")
    
    # Query through RAG which will classify intent
    # (Simplified - skip direct classification)
    
    # Query through RAG pipeline
    result = rag_pipeline.query(
        user_query=query,
        conversation_context=None
    )
    
    print(f"\nIntent (from RAG): {result.get('intent')}")
    print(f"Needs Escalation: {result.get('needs_escalation', False)}")
    print(f"Should Create Ticket: {result.get('should_create_ticket', False)}")
    
    print(f"\nResponse:")
    print(result["response"][:150] + "..." if len(result["response"]) > 150 else result["response"])
    
    # Check if ticket was created
    if "Ticket ID" in result["response"] or "TKT-" in result["response"]:
        print("\n✅ TICKET CREATED IN RESPONSE")
    elif scenario['should_create_ticket']:
        print("\n⚠️ Expected ticket creation but response doesn't show ticket ID")
    else:
        print("\n✅ Correct: No ticket creation needed")

print_header("TEST COMPLETE")
print("\nExpected Behavior:")
print("  1. Complaint detected → Automatic ticket creation")
print("  2. Escalation detected → Automatic ticket creation")
print("  3. FAQ query → No ticket, return answer")
print("  4. All tickets show TKT-XXXXXXXX ID in response")
print("=" * 80 + "\n")
