"""
Test context continuity with email follow-up
"""
from src.agents.router_agent import router_agent

print("\n" + "="*80)
print("TESTING CONTEXT CONTINUITY WITH EMAIL FOLLOW-UP")
print("="*80 + "\n")

session_id = "test_email_followup"

# Query 1: Order lookup with invalid order
print("TURN 1: Order lookup with invalid ID")
print("-" * 80)
query1 = "What's the status of order ORD-2024-102?"
result1 = router_agent.route_query(session_id, query1)
print(f"Query: {query1}")
print(f"Agent: {result1['routing_decision']['target_agent']}")
print(f"Reason: {result1['routing_decision']['reason']}\n")

# Simulate assistant response asking for email
router_agent.handle_response(
    session_id, 
    "Order ORD-2024-102 not found. Please provide your email address.",
    "order_handler"
)

# Query 2: User provides email
print("TURN 2: User provides email (follow-up)")
print("-" * 80)
query2 = "bob.wilson@example.com"
result2 = router_agent.route_query(session_id, query2)
print(f"Query: {query2}")
print(f"Agent: {result2['routing_decision']['target_agent']}")
print(f"Reason: {result2['routing_decision']['reason']}")

# Check if email was captured
context = result2.get("routing_context", {})
print(f"Contact Info Detected: {result2['routing_decision']['context'].get('provided_email')}\n")

# Query 3: Order lookup with valid order
print("TURN 3: Valid order lookup")
print("-" * 80)
query3 = "Check order ORD-2024-001"
result3 = router_agent.route_query(session_id, query3)
print(f"Query: {query3}")
print(f"Agent: {result3['routing_decision']['target_agent']}")
print(f"Reason: {result3['routing_decision']['reason']}\n")

# Query 4: Switch to FAQ
print("TURN 4: Switch to FAQ")
print("-" * 80)
query4 = "What's your return policy?"
result4 = router_agent.route_query(session_id, query4)
print(f"Query: {query4}")
print(f"Agent: {result4['routing_decision']['target_agent']}")
print(f"Reason: {result4['routing_decision']['reason']}\n")

# Query 5: Back to order after FAQ
print("TURN 5: Back to order context")
print("-" * 80)
query5 = "When will my order arrive?"
result5 = router_agent.route_query(session_id, query5)
print(f"Query: {query5}")
print(f"Agent: {result5['routing_decision']['target_agent']}")
print(f"Reason: {result5['routing_decision']['reason']}\n")

print("="*80)
print("TEST COMPLETED")
print("="*80 + "\n")
