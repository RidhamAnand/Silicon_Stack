"""
Quick test of one-way escalation route
"""
import sys
import os

# Fix console encoding
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, errors='replace')

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.conversation_context import ConversationContext, ConversationMessage
from src.agents.escalation_agent import escalation_agent

def test_one_way_escalation():
    print("\n" + "="*80)
    print("TEST: One-Way Escalation Route (No Loop Back)")
    print("="*80)
    
    context = ConversationContext(session_id="test_one_way")
    
    # Step 1: Initial complaint
    print("\n[Step 1] User: I received wrong product")
    msg1 = ConversationMessage(role="user", content="I received wrong product")
    context.add_message(msg1)
    
    response1 = escalation_agent.process_message(context, "I received wrong product")
    print(f"Bot: {response1[:150]}...")
    print(f"Current Agent: {context.current_agent}")
    print(f"Pending Action: {context.pending_action}")
    
    # Store response
    context.add_message(ConversationMessage(role="assistant", content=response1))
    
    # Step 2: Provide email
    print("\n[Step 2] User: john@example.com")
    msg2 = ConversationMessage(role="user", content="john@example.com")
    context.add_message(msg2)
    
    response2 = escalation_agent.process_message(context, "john@example.com")
    print(f"Bot: {response2[:150]}...")
    print(f"Current Agent: {context.current_agent}")
    print(f"Pending Action: {context.pending_action}")
    
    # Store response
    context.add_message(ConversationMessage(role="assistant", content=response2))
    
    # Step 3: Provide order or skip
    print("\n[Step 3] User: no order")
    msg3 = ConversationMessage(role="user", content="no order")
    context.add_message(msg3)
    
    response3 = escalation_agent.process_message(context, "no order")
    print(f"Bot: {response3[:200]}...")
    print(f"Current Agent: {context.current_agent}")
    print(f"Pending Action: {context.pending_action}")
    
    # Verify
    print("\n" + "="*80)
    print("VERIFICATION")
    print("="*80)
    
    has_ticket = "TKT-" in response3 or ("TICKET" in response3.upper() and "CREATED" in response3.upper())
    agent_cleared = context.current_agent is None
    
    print(f"[1] Ticket created: {has_ticket}")
    print(f"[2] Agent cleared after completion: {agent_cleared}")
    
    if has_ticket and agent_cleared:
        print("\n[SUCCESS] One-way escalation working!")
    else:
        print("\n[FAILED] Issues detected")
    
    print("="*80 + "\n")

if __name__ == "__main__":
    test_one_way_escalation()
