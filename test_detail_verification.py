"""
Test: Detail Verification During Ticket Creation
Tests extracting and verifying details with user interaction
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

print_header("TEST: DETAIL EXTRACTION AND VERIFICATION")

# Simulate conversation with good details
chat_history = [
    {
        "role": "user",
        "content": "I need to return order ORD-2024-567 because it arrived broken"
    },
    {
        "role": "assistant",
        "content": "I can help with that. Do you have your order number?"
    },
    {
        "role": "user",
        "content": "Yes, my email is john.doe@example.com and I ordered ORD-2024-567"
    },
    {
        "role": "assistant",
        "content": "Thank you. Our return policy is 30 days."
    }
]

print("\n📋 Chat History:")
for i, msg in enumerate(chat_history, 1):
    print(f"  {i}. {msg['role'].upper()}: {msg['content'][:60]}...")

# TEST 1: Extract details
print_header("TEST 1: Extract Details from History")

extracted = ticket_agent.extract_details_from_history(chat_history)

print(f"\n✅ Extracted Details:")
print(f"  📝 Reason: {extracted['reason'][:70] if extracted['reason'] else 'NOT FOUND'}")
print(f"  📧 Email: {extracted['email'] if extracted['email'] else 'NOT FOUND'}")
print(f"  📦 Order Number: {extracted['order_number'] if extracted['order_number'] else 'NOT FOUND'}")
print(f"  ⚠️ Priority: {extracted['priority'].upper()}")
print(f"  ❌ Missing: {extracted['missing_fields']}")

# TEST 2: Show extracted details (non-interactive test)
print_header("TEST 2: Create Ticket with Extracted Details (Non-Interactive)")

ticket_result = ticket_agent.handle_dissatisfaction(
    chat_history=chat_history,
    interactive=False
)

if ticket_result['success']:
    print(f"\n✅ Ticket Created: {ticket_result['ticket_id']}")
    print(f"   Message: {ticket_result['message']}")
    
    # Get ticket details
    details = ticket_agent.get_ticket_details(ticket_result['ticket_id'])
    print(f"\n📋 Full Ticket Details:")
    print(details['message'])
else:
    print(f"\n❌ Failed: {ticket_result.get('message', 'Unknown error')}")

# TEST 3: Test with incomplete details
print_header("TEST 3: Handling Missing Details")

incomplete_history = [
    {
        "role": "user",
        "content": "The product is broken and I'm very urgent about this!"
    },
    {
        "role": "assistant",
        "content": "I understand. Let me help."
    }
]

print("\n📋 Incomplete Chat History:")
for i, msg in enumerate(incomplete_history, 1):
    print(f"  {i}. {msg['role'].upper()}: {msg['content'][:60]}...")

extracted_incomplete = ticket_agent.extract_details_from_history(incomplete_history)

print(f"\n✅ Extracted Details:")
print(f"  📝 Reason: {extracted_incomplete['reason'][:50] if extracted_incomplete['reason'] else 'NOT FOUND'}")
print(f"  📧 Email: {extracted_incomplete['email'] if extracted_incomplete['email'] else 'NOT FOUND ⚠️'}")
print(f"  📦 Order Number: {extracted_incomplete['order_number'] if extracted_incomplete['order_number'] else 'NOT FOUND'}")
print(f"  ⚠️ Priority: {extracted_incomplete['priority'].upper()}")
print(f"  ❌ Missing Fields: {extracted_incomplete['missing_fields']}")

if extracted_incomplete['missing_fields']:
    print(f"\n⚠️ Fields that would be asked from user:")
    for field in extracted_incomplete['missing_fields']:
        print(f"  • {field}")

print("\n" + "=" * 80)
print("✅ DETAIL VERIFICATION TEST COMPLETE")
print("=" * 80)
print("\nFlow Summary:")
print("  1. Extract details from chat history")
print("  2. Show extracted details to user for verification")
print("  3. User can say 'no' to correct any field")
print("  4. Ask for missing fields one by one")
print("  5. Show priority (auto-detected from keywords)")
print("  6. Create ticket with verified details")
print("=" * 80 + "\n")
