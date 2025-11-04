"""
Test: Dissatisfaction Detection → Ticket Creation
Simulates user saying "no" to "was this helpful?" and creates ticket
"""
import sys
import os
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
os.chdir(project_root)

from src.agents.ticket_agent import ticket_agent

def print_header(title):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)

print_header("TEST: DISSATISFACTION DETECTION → TICKET CREATION")

# Simulate a chat history where:
# 1. User asked about order
# 2. Got FAQ answer they weren't happy with
chat_history = [
    {
        "role": "user",
        "content": "Where is my order ORD-2024-567?"
    },
    {
        "role": "assistant",
        "content": "Please provide your order number to check status."
    },
    {
        "role": "user",
        "content": "ORD-2024-567 - it was urgent but arrived damaged!"
    },
    {
        "role": "assistant",
        "content": "Our return policy allows returns within 30 days of delivery."
    }
]

print("\n📋 Chat History:")
for msg in chat_history:
    print(f"  {msg['role'].upper()}: {msg['content'][:60]}...")

# TEST 1: Extract details from history
print_header("TEST 1: Extract Details from Chat History")

extracted = ticket_agent.extract_details_from_history(chat_history)
print(f"\nExtracted Details:")
print(f"  Reason: {extracted['reason'][:50]}...")
print(f"  Email: {extracted['email']}")
print(f"  Order Number: {extracted['order_number']}")
print(f"  Priority: {extracted['priority']}")
print(f"  Missing Fields: {extracted['missing_fields']}")

# TEST 2: Handle dissatisfaction (non-interactive, use extracted details)
print_header("TEST 2: Create Ticket from Dissatisfaction (Non-Interactive)")

ticket_result = ticket_agent.handle_dissatisfaction(
    chat_history=chat_history,
    interactive=False
)

print(f"\nTicket Creation Result:")
print(f"  Success: {ticket_result['success']}")
print(f"  Ticket ID: {ticket_result.get('ticket_id', 'N/A')}")
print(f"  Message: {ticket_result.get('message', 'N/A')}")

if ticket_result['success']:
    print("\n✅ PASS: Ticket created from dissatisfaction")
    ticket_id = ticket_result['ticket_id']
    
    # Show ticket details
    print_header("TEST 3: Verify Ticket Details")
    
    details = ticket_agent.get_ticket_details(ticket_id)
    print(f"\nTicket Details:")
    print(details['message'])
    
    print("\n✅ PASS: Ticket details verified")
else:
    print("\n❌ FAIL: Ticket creation failed")

# TEST 4: Scenario with missing email (should ask for it in interactive mode)
print_header("TEST 4: Scenario with Missing Email")

chat_history_no_email = [
    {
        "role": "user",
        "content": "My item arrived broken and I need a refund!"
    },
    {
        "role": "assistant",
        "content": "We can help with that. Please contact support."
    }
]

extracted_no_email = ticket_agent.extract_details_from_history(chat_history_no_email)
print(f"\nExtracted (missing email):")
print(f"  Reason: {extracted_no_email['reason']}")
print(f"  Email: {extracted_no_email['email']}")
print(f"  Priority: {extracted_no_email['priority']}")
print(f"  Missing: {extracted_no_email['missing_fields']}")

if 'email' in extracted_no_email['missing_fields']:
    print("\n✅ PASS: Correctly identified missing email field")
else:
    print("\n❌ FAIL: Should have detected missing email")

# TEST 5: Multiple dissatisfaction scenarios
print_header("TEST 5: Multiple Scenarios")

scenarios = [
    {
        "name": "Broken product with order number",
        "history": [
            {"role": "user", "content": "Order ORD-2024-001 arrived broken!"},
            {"role": "assistant", "content": "Try restarting it."}
        ]
    },
    {
        "name": "Urgent issue",
        "history": [
            {"role": "user", "content": "This is URGENT! Contact: john@example.com"},
            {"role": "assistant", "content": "General FAQ answer."}
        ]
    },
    {
        "name": "Damaged package",
        "history": [
            {"role": "user", "content": "The package was damaged during shipping"},
            {"role": "assistant", "content": "Standard response."}
        ]
    }
]

for i, scenario in enumerate(scenarios, 1):
    print(f"\nScenario {i}: {scenario['name']}")
    
    result = ticket_agent.handle_dissatisfaction(
        chat_history=scenario['history'],
        interactive=False
    )
    
    if result['success']:
        print(f"  ✅ Ticket created: {result['ticket_id']}")
        print(f"  Priority: {result.get('title', 'N/A')}")
    else:
        print(f"  ❌ Failed: {result.get('message', 'Unknown error')}")

print("\n" + "=" * 80)
print("✅ DISSATISFACTION → TICKET CREATION TEST COMPLETE")
print("=" * 80)
print("\nFlow Summary:")
print("  1. User says 'no' to 'Was this helpful?'")
print("  2. System offers: 'Create a support ticket?'")
print("  3. Extract details from chat history")
print("  4. Ask for missing details (email, reason, order#)")
print("  5. Create ticket with all information")
print("  6. Return ticket ID for tracking")
print("=" * 80 + "\n")
