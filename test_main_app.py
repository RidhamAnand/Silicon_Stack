#!/usr/bin/env python
"""
Test the main agentic app with multiple queries (ASCII only)
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.agents.router_agent import router_agent

# Test queries
test_queries = [
    "What is the status of my order ORD-2024-001?",
    "When will it arrive?",
    "My item arrived damaged!",
    "What's your return policy?",
    "How much does shipping cost?",
    "I need to speak to a manager NOW!",
]

print("\n" + "="*80)
print("TESTING AGENTIC ROUTER WITH GROQ LLM INTEGRATION")
print("="*80)

session_id = f"test_session_{id(None)}"
current_agent = None

for i, query in enumerate(test_queries, 1):
    print(f"\n{'='*80}")
    print(f"QUERY {i}/6")
    print(f"{'='*80}")
    print(f"User: {query}\n")
    
    try:
        # Route through agentic system
        routing_result = router_agent.route_query(session_id, query)
        
        # Extract routing information
        routing_decision = routing_result["routing_decision"]
        target_agent = routing_decision["target_agent"]
        reason = routing_decision["reason"]
        
        # Display routing decision
        print(f"[ROUTING] -> {target_agent.upper()}")
        print(f"[REASON]  -> {reason}")
        
        # Check for agent switch
        agent_switched = target_agent != current_agent
        if agent_switched and current_agent is not None:
            print(f"[SWITCH]  -> From {current_agent} to {target_agent}")
        
        current_agent = target_agent
        
        # Display extracted order numbers
        entities = routing_result.get("entities", [])
        order_numbers = [e["value"] for e in entities if e["type"] == "order_number"]
        if order_numbers:
            print(f"[ORDERS]  -> {', '.join(order_numbers)}")
        
        # Display metadata
        intent = routing_result.get("intent", "unknown")
        confidence = routing_result.get("confidence", 0)
        print(f"[INTENT]  -> {intent} (Confidence: {confidence:.1%})")
        
        # Get response
        response = routing_result.get("response", "No response generated")
        print(f"\n[RESPONSE]\n{response}")
        
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()

print("\n" + "="*80)
print("APP TEST COMPLETED")
print("="*80 + "\n")
