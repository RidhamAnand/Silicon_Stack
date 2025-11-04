"""
Test for unified escalation agent
Tests LLM-based detail extraction from last 10 messages
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.agents.escalation_agent import escalation_agent

def test_scenario_1_product_defect():
    """Test: Customer reports broken product - should extract issue and ask for email"""
    print("\n" + "=" * 70)
    print("SCENARIO 1: Product Defect - Extract from conversation history")
    print("=" * 70)
    
    chat_history = [
        {"role": "user", "content": "Hi, I need help with my recent order"},
        {"role": "assistant", "content": "Sure! What's the issue with your order?"},
        {"role": "user", "content": "The device I received is completely broken. The screen doesn't work at all"},
        {"role": "assistant", "content": "I'm sorry to hear that. Let me help you."},
        {"role": "user", "content": "This is urgent! I need a replacement ASAP"},
        {"role": "user", "content": "My email is customer@example.com"},
        {"role": "assistant", "content": "I understand this is urgent. Let me escalate this for you."},
        {"role": "user", "content": "Please escalate this now, I can't wait"},
    ]
    
    result = escalation_agent.handle_escalation(
        chat_history=chat_history,
        user_query="Please escalate this now, I can't wait",
        interactive=False
    )
    
    print(f"Success: {result.get('success')}")
    print(f"Ticket ID: {result.get('ticket_id')}")
    if result.get('success'):
        details = result.get('details', {})
        print(f"Issue: {details.get('reason', 'N/A')[:100]}")
        print(f"Email: {details.get('email', 'NOT_FOUND')}")
        print(f"Priority: {result.get('priority')}")
        print(f"Keywords Found: {details.get('keywords', {})}")
        print("PASSED - Escalation created with extraction")
    else:
        print(f"FAILED: {result.get('message')}")
    
    return result.get('success', False)


def test_scenario_2_order_tracking():
    """Test: Order never arrived - extract reason and order tracking"""
    print("\n" + "=" * 70)
    print("SCENARIO 2: Order Tracking Issue - Extract order number")
    print("=" * 70)
    
    chat_history = [
        {"role": "user", "content": "Where's my order? ORD-5678-9012"},
        {"role": "assistant", "content": "Let me check that for you."},
        {"role": "user", "content": "It was supposed to arrive 5 days ago. This is ridiculous!"},
        {"role": "assistant", "content": "I apologize for the delay. Let me investigate."},
        {"role": "user", "content": "I need this resolved immediately. This is urgent!"},
        {"role": "user", "content": "Contact me at john.smith@email.com"},
        {"role": "assistant", "content": "I'm escalating this for you."},
        {"role": "user", "content": "My order ORD-5678-9012 is still missing! I'm frustrated"},
    ]
    
    result = escalation_agent.handle_escalation(
        chat_history=chat_history,
        user_query="My order is missing, I need immediate help",
        interactive=False
    )
    
    print(f"Success: {result.get('success')}")
    print(f"Ticket ID: {result.get('ticket_id')}")
    if result.get('success'):
        details = result.get('details', {})
        print(f"Issue: {details.get('reason', 'N/A')[:100]}")
        print(f"Order Number: {details.get('order_number', 'NOT_FOUND')}")
        print(f"Priority: {result.get('priority')}")
        print("PASSED - Order number extracted from history")
    else:
        print(f"FAILED: {result.get('message')}")
    
    return result.get('success', False)


def test_scenario_3_context_analysis():
    """Test: Verify last 10 messages are analyzed correctly"""
    print("\n" + "=" * 70)
    print("SCENARIO 3: Context Analysis - Last 10 messages only")
    print("=" * 70)
    
    # Create 15 messages - only last 10 should be analyzed
    chat_history = [
        {"role": "user", "content": "Old message 1"},
        {"role": "assistant", "content": "Old response 1"},
        {"role": "user", "content": "Old message 2"},
        {"role": "assistant", "content": "Old response 2"},
        {"role": "user", "content": "Old message 3"},
        {"role": "assistant", "content": "Old response 3"},
        {"role": "user", "content": "New: Device arrived damaged with scratches"},
        {"role": "assistant", "content": "I'm sorry to hear that."},
        {"role": "user", "content": "This is critical! Need replacement immediately"},
        {"role": "assistant", "content": "Let me escalate this."},
        {"role": "user", "content": "Please help! Contact: john.doe@example.com"},
        {"role": "assistant", "content": "Escalating now..."},
        {"role": "user", "content": "URGENT - Create ticket now!"},
        {"role": "assistant", "content": "Creating ticket..."},
        {"role": "user", "content": "My issue: damaged device, critical priority"},
    ]
    
    result = escalation_agent.handle_escalation(
        chat_history=chat_history,
        user_query="My issue: damaged device, critical priority",
        interactive=False
    )
    
    print(f"Success: {result.get('success')}")
    print(f"Ticket ID: {result.get('ticket_id')}")
    if result.get('success'):
        details = result.get('details', {})
        print(f"Email Found: {details.get('email', 'NOT_FOUND')}")
        print(f"Keywords: {details.get('keywords', {})}")
        print(f"Priority: {result.get('priority')}")
        print("PASSED - Last 10 messages analyzed correctly")
    else:
        print(f"FAILED: {result.get('message')}")
    
    return result.get('success', False)


def test_scenario_4_multiple_keywords():
    """Test: Multiple escalation keywords should be detected"""
    print("\n" + "=" * 70)
    print("SCENARIO 4: Multiple Keywords - Priority Detection")
    print("=" * 70)
    
    chat_history = [
        {"role": "user", "content": "I received a defective product"},
        {"role": "assistant", "content": "I'm sorry to hear that."},
        {"role": "user", "content": "It's broken and damaged! This is CRITICAL! URGENT!"},
        {"role": "user", "content": "Email: test@company.com"},
        {"role": "assistant", "content": "Let me help you."},
        {"role": "user", "content": "I'm angry and frustrated. I need immediate help!"},
    ]
    
    result = escalation_agent.handle_escalation(
        chat_history=chat_history,
        user_query="I need immediate help!",
        interactive=False
    )
    
    print(f"Success: {result.get('success')}")
    if result.get('success'):
        details = result.get('details', {})
        keywords = details.get('keywords', {})
        priority = result.get('priority')
        
        print(f"Keywords found: {keywords}")
        print(f"Priority level: {priority}")
        
        # Should detect multiple keyword categories
        has_critical = 'critical' in keywords
        has_damage = 'defect' in keywords
        has_frustration = 'frustration' in keywords
        
        if has_critical and has_damage and has_frustration and priority == "urgent":
            print("PASSED - All keywords detected and priority set to URGENT")
            return True
        else:
            print(f"FAILED - Missing keywords or wrong priority")
            return False
    else:
        print(f"FAILED: {result.get('message')}")
        return False


def test_scenario_5_email_extraction():
    """Test: Email extraction from conversation"""
    print("\n" + "=" * 70)
    print("SCENARIO 5: Email Extraction - From conversation content")
    print("=" * 70)
    
    chat_history = [
        {"role": "user", "content": "Hello, I have an issue"},
        {"role": "assistant", "content": "Sure, what's the problem?"},
        {"role": "user", "content": "My device is broken. Contact me at support@example.com"},
        {"role": "assistant", "content": "I'll help you."},
        {"role": "user", "content": "This is urgent! Please escalate"},
    ]
    
    result = escalation_agent.handle_escalation(
        chat_history=chat_history,
        user_query="This is urgent! Please escalate",
        interactive=False
    )
    
    print(f"Success: {result.get('success')}")
    if result.get('success'):
        details = result.get('details', {})
        email = details.get('email', 'NOT_FOUND')
        print(f"Email extracted: {email}")
        
        if email and "@" in email:
            print("PASSED - Email correctly extracted")
            return True
        else:
            print("FAILED - Email not extracted")
            return False
    else:
        print(f"FAILED: {result.get('message')}")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("UNIFIED ESCALATION AGENT - TEST SUITE")
    print("Testing LLM-based detail extraction from last 10 messages")
    print("=" * 70)
    
    tests = [
        ("Product Defect", test_scenario_1_product_defect),
        ("Order Tracking", test_scenario_2_order_tracking),
        ("Context Analysis", test_scenario_3_context_analysis),
        ("Multiple Keywords", test_scenario_4_multiple_keywords),
        ("Email Extraction", test_scenario_5_email_extraction),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\nTEST ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    for test_name, passed in results.items():
        status = "PASSED" if passed else "FAILED"
        print(f"{test_name:30} {status}")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\nALL TESTS PASSED!")
        return 0
    else:
        print(f"\n{total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit(main())
