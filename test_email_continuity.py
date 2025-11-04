"""
Test that email response stays with escalation agent
Tests the bug: "ridhamanand31@gmail.com" should create ticket, not switch to FAQ
"""

import sys
import os

# Fix console encoding for Windows
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, errors='replace')

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.rag.pipeline import rag_pipeline

def test_email_continuity():
    """Test that providing email continues with escalation agent"""
    
    print("\n" + "="*80)
    print("TEST: Email Response Continuity")
    print("="*80)
    
    # Step 1: User reports complaint
    print("\n[Step 1] User: I received defective item")
    result1 = rag_pipeline.query(
        user_query="I received defective item",
        conversation_context=None
    )
    
    print(f"Intent: {result1['intent']}")
    print(f"Response: {result1['response'][:150]}...")
    
    # Build conversation context
    conversation_context = [
        {
            "role": "user",
            "content": "I received defective item",
            "intent": result1['intent'],
            "confidence": result1['intent_confidence'],
            "entities": result1['entities'],
            "metadata": {}
        },
        {
            "role": "assistant",
            "content": result1['response'],
            "intent": result1['intent'],
            "confidence": result1['intent_confidence'],
            "entities": result1['entities'],
            "metadata": {
                "routing_path": result1['routing_path'],
                # Simulate state being saved (main.py does this)
                "current_agent": "escalation_agent",
                "pending_action": "waiting_for_order_number",
                "collected_details": {"issue": "I received defective item"},
                "agent_state": {"step": "waiting_for_order"}
            }
        }
    ]
    
    # Step 2: User provides order
    print("\n[Step 2] User: ORD-1234-5678")
    result2 = rag_pipeline.query(
        user_query="ORD-1234-5678",
        conversation_context=conversation_context
    )
    
    print(f"Intent: {result2['intent']}")
    print(f"Routing Path: {' -> '.join(result2['routing_path'])}")
    print(f"Response: {result2['response'][:150]}...")
    
    # Update context
    conversation_context.append({
        "role": "user",
        "content": "ORD-1234-5678",
        "intent": result2['intent'],
        "confidence": result2['intent_confidence'],
        "entities": result2['entities'],
        "metadata": {}
    })
    conversation_context.append({
        "role": "assistant",
        "content": result2['response'],
        "intent": result2['intent'],
        "confidence": result2['intent_confidence'],
        "entities": result2['entities'],
        "metadata": {
            "routing_path": result2['routing_path'],
            "current_agent": "escalation_agent",
            "pending_action": "waiting_for_email",
            "collected_details": {
                "issue": "I received defective item",
                "order_number": "ORD-1234-5678"
            },
            "agent_state": {"step": "waiting_for_email"}
        }
    })
    
    # Step 3: User provides email - THE CRITICAL TEST
    print("\n[Step 3] User: ridhamanand31@gmail.com")
    print("THIS IS THE BUG - Should create ticket, NOT switch to FAQ")
    
    result3 = rag_pipeline.query(
        user_query="ridhamanand31@gmail.com",
        conversation_context=conversation_context
    )
    
    print(f"\nIntent: {result3['intent']}")
    print(f"Routing Path: {' -> '.join(result3['routing_path'])}")
    print(f"Response: {result3['response'][:200]}...")
    
    # Verification
    print("\n" + "="*80)
    print("VERIFICATION")
    print("="*80)
    
    # Check routing path contains escalation_agent
    has_escalation = any("escalation" in str(path).lower() for path in result3['routing_path'])
    print(f"[1] Routing path includes escalation_agent: {has_escalation}")
    
    # Check response contains ticket creation
    has_ticket = "TKT-" in result3['response'] or "ticket" in result3['response'].lower()
    print(f"[2] Response mentions ticket: {has_ticket}")
    
    # Check response is NOT from FAQ agent
    is_faq_response = "FAQ database" in result3['response'] or "raise a support ticket" in result3['response']
    print(f"[3] Response is NOT generic FAQ: {not is_faq_response}")
    
    # Final verdict
    success = has_escalation and has_ticket and not is_faq_response
    
    if success:
        print("\n[SUCCESS] Email continuity working correctly!")
        print("Escalation agent maintained control and created ticket.")
    else:
        print("\n[FAILED] Bug still exists!")
        print("System switched away from escalation agent.")
        if is_faq_response:
            print("ERROR: Routed to FAQ agent instead of escalation!")
    
    print("="*80 + "\n")
    
    return success


if __name__ == "__main__":
    success = test_email_continuity()
    sys.exit(0 if success else 1)
