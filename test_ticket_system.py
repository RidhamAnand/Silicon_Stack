"""
Test ticket management system
"""
from src.classification.intent_classifier import intent_classifier
from src.agents.ticket_agent import ticket_agent

print("\n" + "="*80)
print("TESTING TICKET MANAGEMENT SYSTEM")
print("="*80 + "\n")

# Test 1: Intent classification for ticket requests
print("TEST 1: Intent Classification for Ticket Requests")
print("-" * 80)

ticket_queries = [
    "create ticket",
    "raise a ticket",
    "open a support ticket",
    "I want to create a new ticket",
    "show my tickets",
    "view all my support tickets",
]

for query in ticket_queries:
    intent, confidence = intent_classifier.classify_intent(query)
    print(f"Query: '{query}'")
    print(f"  Intent: {intent.value} (Confidence: {confidence:.2f})\n")

# Test 2: Create tickets
print("\nTEST 2: Create Support Tickets")
print("-" * 80)

user_email = "bob.wilson@example.com"

result1 = ticket_agent.handle_ticket_request(
    query="My item arrived damaged!",
    user_email=user_email,
    order_number="ORD-2024-001",
    action="create"
)
print(f"Result: {result1}")
if result1.get('success'):
    print(f"Created ticket: {result1.get('ticket_id')}")
print(f"Message: {result1['message']}\n")

result2 = ticket_agent.handle_ticket_request(
    query="URGENT: The product is completely broken and unusable",
    user_email=user_email,
    order_number="ORD-2024-002",
    action="create"
)
if result2.get('success'):
    print(f"Created ticket: {result2.get('ticket_id')}")
print(f"Message: {result2['message']}\n")

result3 = ticket_agent.handle_ticket_request(
    query="Can I get a refund?",
    user_email=user_email,
    action="create"
)
if result3.get('success'):
    print(f"Created ticket: {result3.get('ticket_id')}")
print(f"Message: {result3['message']}\n")

# Test 3: View tickets
print("TEST 3: View User Tickets")
print("-" * 80)

view_result = ticket_agent.handle_ticket_request(
    query="show my tickets",
    user_email=user_email
)
print(view_result['message'])

# Test 4: Get ticket details
print("\nTEST 4: Get Ticket Details")
print("-" * 80)

if result2.get('success'):
    details = ticket_agent.get_ticket_details(result2['ticket_id'])
    print(details['message'])

print("\n" + "="*80)
print("TICKET SYSTEM TEST COMPLETED")
print("="*80 + "\n")
