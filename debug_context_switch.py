"""
Debug context switch test
"""
from src.agents.router_agent import router_agent
from src.classification.intent_classifier import intent_classifier

# Check intent classification for the problematic query
query = "What's your return policy?"
intent, confidence = intent_classifier.classify_intent(query)

print(f"Query: {query}")
print(f"Detected Intent: {intent.value}")
print(f"Confidence: {confidence}")

# Now test routing
session_id = "debug_context"
router_agent.create_session(session_id)

# Step 1: Order query
r1 = router_agent.route_query(session_id, "Where is order ORD-2024-004?")
print(f"\nStep 1 - Order query: {r1['routing_decision']['target_agent']}")

# Step 2: FAQ query
r2 = router_agent.route_query(session_id, query)
print(f"Step 2 - FAQ query: {r2['routing_decision']['target_agent']}")
print(f"  Reason: {r2['routing_decision']['reason']}")
print(f"  Intent: {r2['intent']}")
