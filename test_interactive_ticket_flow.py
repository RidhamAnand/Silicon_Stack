"""
Interactive test: No FAQ Match → Ticket Creation Flow
Tests the full conversation flow from unanswerable question to ticket creation
"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
os.chdir(project_root)

from src.rag.pipeline import rag_pipeline
from src.agents.ticket_agent import ticket_agent

def test_flow():
    """Test the complete flow"""
    print("\n" + "=" * 80)
    print("SCENARIO: User asks an unanswerable FAQ question")
    print("=" * 80)
    
    # Step 1: User asks unanswerable question
    query = "What's the best way to reprogram the quantum motherboard?"
    print(f"\n📝 User Query: {query}\n")
    
    # Step 2: Search FAQ
    print("🔍 Searching FAQ database...")
    faq_result = rag_pipeline._search_faqs(query)
    
    print(f"\nFAQ Result:")
    print(f"  Response: {faq_result['response']}")
    print(f"  Score: {faq_result['top_score']:.2f} (threshold: 0.50)")
    print(f"  Suggest Ticket: {faq_result.get('should_create_ticket', False)}")
    
    # Step 3: Check if ticket should be suggested
    if faq_result.get('should_create_ticket', False):
        print("\n✅ System detected no clear FAQ match")
        print("💡 System prompts user: 'Would you like to create a support ticket?'")
        
        # Simulate user saying "yes"
        print("\n📌 User Response: YES\n")
        
        # Step 4: Create ticket
        user_email = "customer@example.com"
        print(f"Creating ticket for: {user_email}")
        
        ticket_result = ticket_agent.create_ticket_from_faq_no_match(
            user_query=query,
            user_email=user_email,
            order_number="ORD-2024-123"
        )
        
        print(f"\n✅ TICKET CREATED!")
        print(f"  Ticket ID: {ticket_result['ticket_id']}")
        print(f"  Status: {ticket_result['status']}")
        print(f"  Message: {ticket_result['message']}")
        
        # Step 5: Show user their ticket details
        print("\n📋 Ticket Details:")
        details = ticket_agent.get_ticket_details(ticket_result['ticket_id'])
        print(details['message'])
        
        # Step 6: User can check their tickets anytime
        print("\n📊 User Checks All Their Tickets:")
        all_tickets = ticket_agent.view_tickets(user_email)
        print(all_tickets['message'])
        
        print("\n" + "=" * 80)
        print("✅ FLOW COMPLETE - USER HAS TICKET ID FOR TRACKING")
        print("=" * 80)
        return True
    else:
        print("\n❌ ERROR: No ticket suggestion made!")
        return False

if __name__ == "__main__":
    try:
        success = test_flow()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
