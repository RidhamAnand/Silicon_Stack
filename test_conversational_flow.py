"""
Test conversational flow with real-world scenarios
Tests multi-turn dialogues with state persistence
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.agents.escalation_agent import EscalationAgent
from src.utils.conversation_context import ConversationContext, ConversationMessage
from datetime import datetime


def test_defective_item_flow():
    """
    Test: User reports defective item, provides order, then email
    Expected: Natural conversational flow with agent persistence
    """
    print("\n" + "="*80)
    print("TEST 1: Defective Item - Step-by-Step Collection")
    print("="*80)
    
    # Initialize
    agent = EscalationAgent()
    context = ConversationContext(session_id="test_session_1")
    
    # Step 1: User reports defective item
    print("\n[USER]: I received defective item")
    msg1 = ConversationMessage(
        role="user",
        content="I received defective item",
        timestamp=datetime.utcnow()
    )
    context.add_message(msg1)
    
    response1 = agent.process_message(context, "I received defective item")
    print(f"\n[ASSISTANT]: {response1}")
    
    # Verify: Should ask for order number
    assert "order number" in response1.lower(), "Should ask for order number"
    assert context.current_agent == "escalation_agent", "Should set active agent"
    assert context.pending_action == "waiting_for_order_number", "Should wait for order"
    print("✅ Step 1 passed: Asked for order number, set agent state")
    
    # Step 2: User provides order number
    print("\n[USER]: ORD-1234-5678")
    msg2 = ConversationMessage(
        role="user",
        content="ORD-1234-5678",
        timestamp=datetime.utcnow()
    )
    context.add_message(msg2)
    
    response2 = agent.process_message(context, "ORD-1234-5678")
    print(f"\n[ASSISTANT]: {response2}")
    
    # Verify: Should ask for email
    assert "email" in response2.lower(), "Should ask for email"
    assert context.current_agent == "escalation_agent", "Should stay with escalation agent"
    assert context.pending_action == "waiting_for_email", "Should wait for email"
    assert context.get_collected_detail("order_number") == "ORD-1234-5678", "Should store order"
    print("✅ Step 2 passed: Asked for email, stored order number")
    
    # Step 3: User provides email
    print("\n[USER]: john@example.com")
    msg3 = ConversationMessage(
        role="user",
        content="john@example.com",
        timestamp=datetime.utcnow()
    )
    context.add_message(msg3)
    
    response3 = agent.process_message(context, "john@example.com")
    print(f"\n[ASSISTANT]: {response3}")
    
    # Verify: Should create ticket
    assert "ticket" in response3.lower(), "Should mention ticket"
    assert "TKT-" in response3, "Should have ticket ID"
    assert "john@example.com" in response3, "Should show email"
    assert "ORD-1234-5678" in response3, "Should show order"
    assert context.current_agent is None, "Should clear agent after completion"
    print("✅ Step 3 passed: Created ticket, cleared agent state")
    
    print("\n✅ TEST 1 PASSED: Complete conversational flow works!")


def test_order_in_first_message():
    """
    Test: User provides order number in first message
    Expected: Skip order collection, go straight to email
    """
    print("\n" + "="*80)
    print("TEST 2: Order Number in First Message")
    print("="*80)
    
    agent = EscalationAgent()
    context = ConversationContext(session_id="test_session_2")
    
    # Step 1: User reports issue with order number
    print("\n[USER]: My order ORD-9999-1111 arrived damaged")
    msg1 = ConversationMessage(
        role="user",
        content="My order ORD-9999-1111 arrived damaged",
        timestamp=datetime.utcnow()
    )
    context.add_message(msg1)
    
    response1 = agent.process_message(context, "My order ORD-9999-1111 arrived damaged")
    print(f"\n[ASSISTANT]: {response1}")
    
    # Verify: Should skip to email collection
    assert "email" in response1.lower(), "Should ask for email directly"
    assert "ORD-9999-1111" in response1, "Should acknowledge order number"
    assert context.get_collected_detail("order_number") == "ORD-9999-1111", "Should extract order"
    assert context.pending_action == "waiting_for_email", "Should wait for email"
    print("✅ Step 1 passed: Extracted order from first message, asked for email")
    
    # Step 2: User provides email
    print("\n[USER]: sarah@test.com")
    msg2 = ConversationMessage(
        role="user",
        content="sarah@test.com",
        timestamp=datetime.utcnow()
    )
    context.add_message(msg2)
    
    response2 = agent.process_message(context, "sarah@test.com")
    print(f"\n[ASSISTANT]: {response2}")
    
    # Verify: Should create ticket
    assert "ticket" in response2.lower(), "Should create ticket"
    assert "TKT-" in response2, "Should have ticket ID"
    print("✅ Step 2 passed: Created ticket successfully")
    
    print("\n✅ TEST 2 PASSED: Smart extraction from first message works!")


def test_no_order_number():
    """
    Test: User doesn't have order number
    Expected: Accept "no order number" and continue
    """
    print("\n" + "="*80)
    print("TEST 3: User Doesn't Have Order Number")
    print("="*80)
    
    agent = EscalationAgent()
    context = ConversationContext(session_id="test_session_3")
    
    # Step 1: Report issue
    print("\n[USER]: The product quality is very poor")
    msg1 = ConversationMessage(
        role="user",
        content="The product quality is very poor",
        timestamp=datetime.utcnow()
    )
    context.add_message(msg1)
    
    response1 = agent.process_message(context, "The product quality is very poor")
    print(f"\n[ASSISTANT]: {response1}")
    assert "order number" in response1.lower(), "Should ask for order"
    
    # Step 2: User doesn't have order
    print("\n[USER]: I don't have order number")
    msg2 = ConversationMessage(
        role="user",
        content="I don't have order number",
        timestamp=datetime.utcnow()
    )
    context.add_message(msg2)
    
    response2 = agent.process_message(context, "I don't have order number")
    print(f"\n[ASSISTANT]: {response2}")
    
    # Should handle gracefully - for now, just check it doesn't crash
    assert len(response2) > 0, "Should provide a response"
    print("✅ Handled 'no order number' case")
    
    print("\n✅ TEST 3 PASSED: Handles missing order gracefully!")


def test_conversational_persistence():
    """
    Test: Verify agent state persists across messages
    Expected: current_agent should remain 'escalation_agent' until completion
    """
    print("\n" + "="*80)
    print("TEST 4: Agent Persistence Across Messages")
    print("="*80)
    
    agent = EscalationAgent()
    context = ConversationContext(session_id="test_session_4")
    
    # Step 1: Initial complaint
    print("\n[USER]: broken item received")
    context.add_message(ConversationMessage(
        role="user",
        content="broken item received",
        timestamp=datetime.utcnow()
    ))
    
    response1 = agent.process_message(context, "broken item received")
    print(f"[ASSISTANT]: {response1[:80]}...")
    agent_after_step1 = context.current_agent
    
    # Step 2: Provide order
    print("\n[USER]: ORD-5555-6666")
    context.add_message(ConversationMessage(
        role="user",
        content="ORD-5555-6666",
        timestamp=datetime.utcnow()
    ))
    
    response2 = agent.process_message(context, "ORD-5555-6666")
    print(f"[ASSISTANT]: {response2[:80]}...")
    agent_after_step2 = context.current_agent
    
    # Step 3: Provide email
    print("\n[USER]: test@example.com")
    context.add_message(ConversationMessage(
        role="user",
        content="test@example.com",
        timestamp=datetime.utcnow()
    ))
    
    response3 = agent.process_message(context, "test@example.com")
    agent_after_step3 = context.current_agent
    
    # Verify persistence
    assert agent_after_step1 == "escalation_agent", "Should set escalation_agent at step 1"
    assert agent_after_step2 == "escalation_agent", "Should stay escalation_agent at step 2"
    assert agent_after_step3 is None, "Should clear agent after completion"
    
    print("\n✅ Agent persistence verified:")
    print(f"   - After step 1: {agent_after_step1}")
    print(f"   - After step 2: {agent_after_step2}")
    print(f"   - After step 3: {agent_after_step3}")
    
    print("\n✅ TEST 4 PASSED: Agent state persists correctly!")


def run_all_tests():
    """Run all conversational flow tests"""
    print("\n" + "="*80)
    print("CONVERSATIONAL FLOW TEST SUITE")
    print("Testing real-world multi-turn conversations")
    print("="*80)
    
    tests = [
        ("Defective Item Flow", test_defective_item_flow),
        ("Order in First Message", test_order_in_first_message),
        ("No Order Number", test_no_order_number),
        ("Agent Persistence", test_conversational_persistence),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"\n❌ TEST FAILED: {test_name}")
            print(f"   Error: {e}")
            failed += 1
        except Exception as e:
            print(f"\n❌ TEST ERROR: {test_name}")
            print(f"   Exception: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Total: {passed + failed}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! Conversational flow working perfectly!")
    else:
        print(f"\n⚠️  {failed} test(s) need attention")
    
    print("="*80 + "\n")


if __name__ == "__main__":
    run_all_tests()
