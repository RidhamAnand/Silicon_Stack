"""
Integration test for complete escalation flow
Simulates real user journey: complaint -> email collection -> ticket creation
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.agents.escalation_agent import escalation_agent

def test_complete_escalation_flow():
    """Test the complete escalation flow from complaint to ticket creation"""
    print("\n" + "=" * 70)
    print("INTEGRATION TEST: Complete Escalation Flow")
    print("=" * 70)
    
    # Simulate multi-message conversation leading to escalation
    chat_history = [
        {"role": "user", "content": "Hi, I need help with my recent order"},
        {"role": "assistant", "content": "Sure! How can I assist you?"},
        {"role": "user", "content": "I received the wrong item. The package contains item B but I ordered item A"},
        {"role": "assistant", "content": "I apologize for that mistake. Let me help you."},
        {"role": "user", "content": "This is really frustrating! I need this urgently"},
        {"role": "assistant", "content": "I understand your frustration. Let me escalate this."},
        {"role": "user", "content": "The order number is ORD-1234-5678 and I'm very angry about this"},
    ]
    
    print("\n1. User reports wrong item received (complaint detected)")
    print("   Chat history has 7 messages")
    print("   Escalation triggered...")
    
    # First escalation attempt (no email in history)
    result1 = escalation_agent.handle_escalation(
        chat_history=chat_history,
        user_query="The order number is ORD-1234-5678 and I'm very angry about this",
        interactive=False
    )
    
    print(f"\n2. First escalation attempt:")
    print(f"   - Success: {result1.get('success')}")
    print(f"   - Needs Email: {result1.get('needs_email')}")
    print(f"   - Reason Found: {bool(result1.get('reason'))}")
    print(f"   - Order Number Found: {result1.get('order_number')}")
    
    if result1.get('needs_email'):
        print("   → System asks user for email")
        print("\n3. User provides email: support.user@company.com")
        
        # Now simulate the user providing email
        extracted_details = escalation_agent._extract_details_with_llm(
            escalation_agent._analyze_context(chat_history, "")
        )
        extracted_details["email"] = "support.user@company.com"
        
        context_analysis = escalation_agent._analyze_context(chat_history, "")
        result2 = escalation_agent._create_escalation_ticket(extracted_details, context_analysis)
        
        print(f"\n4. Ticket creation with email:")
        print(f"   - Success: {result2.get('success')}")
        if result2.get('success'):
            print(f"   - Ticket ID: {result2.get('ticket_id')}")
            print(f"   - Priority: {result2.get('priority').upper()}")
            print(f"   - Details:")
            details = result2.get('details', {})
            print(f"     • Issue: {details.get('reason', 'N/A')[:80]}")
            print(f"     • Email: {details.get('email')}")
            print(f"     • Order: {details.get('order_number')}")
            print(f"     • Keywords: {details.get('keywords', {})}")
            print("\n✓ INTEGRATION TEST PASSED")
            return True
        else:
            print(f"   - Error: {result2.get('message')}")
            print("\n✗ INTEGRATION TEST FAILED")
            return False
    else:
        print(f"   Error: Expected needs_email but got: {result1.get('message')}")
        print("\n✗ INTEGRATION TEST FAILED")
        return False


def test_escalation_with_email_in_history():
    """Test escalation when email is found in conversation history"""
    print("\n" + "=" * 70)
    print("INTEGRATION TEST: Escalation with Email in History")
    print("=" * 70)
    
    chat_history = [
        {"role": "user", "content": "Hello, I have a problem"},
        {"role": "assistant", "content": "How can I help?"},
        {"role": "user", "content": "My device is broken. Please contact me at john.smith@email.com"},
        {"role": "assistant", "content": "I'm sorry to hear that."},
        {"role": "user", "content": "This is URGENT! I need immediate help!"},
    ]
    
    print("\n1. User reports broken device and provides email in message")
    print("   Escalation triggered...")
    
    result = escalation_agent.handle_escalation(
        chat_history=chat_history,
        user_query="This is URGENT! I need immediate help!",
        interactive=False
    )
    
    print(f"\n2. Escalation result:")
    print(f"   - Success: {result.get('success')}")
    if result.get('success'):
        print(f"   - Ticket ID: {result.get('ticket_id')}")
        print(f"   - Priority: {result.get('priority').upper()}")
        print(f"   - Email Auto-detected: {result['details'].get('email')}")
        print(f"\n✓ INTEGRATION TEST PASSED - Email auto-detected from history")
        return True
    else:
        print(f"   - Error: {result.get('message')}")
        print(f"\n✗ INTEGRATION TEST FAILED")
        return False


def test_priority_detection():
    """Test that priority levels are correctly detected"""
    print("\n" + "=" * 70)
    print("INTEGRATION TEST: Priority Detection")
    print("=" * 70)
    
    test_cases = [
        {
            "name": "URGENT Priority",
            "keywords": "This is CRITICAL! Emergency! ASAP!",
            "email": "user@example.com",
            "expected": "urgent"
        },
        {
            "name": "HIGH Priority",
            "keywords": "The item arrived broken and damaged",
            "email": "user@example.com",
            "expected": "high"
        },
        {
            "name": "MEDIUM Priority",
            "keywords": "I need help with my account",
            "email": "user@example.com",
            "expected": "medium"
        }
    ]
    
    passed = 0
    for test_case in test_cases:
        chat_history = [
            {"role": "user", "content": test_case["keywords"]},
            {"role": "user", "content": f"Email: {test_case['email']}"},
        ]
        
        result = escalation_agent.handle_escalation(
            chat_history=chat_history,
            user_query=test_case["keywords"],
            interactive=False
        )
        
        if result.get('success'):
            priority = result.get('priority', '').lower()
            expected = test_case['expected'].lower()
            if priority == expected:
                print(f"✓ {test_case['name']}: {priority.upper()}")
                passed += 1
            else:
                print(f"✗ {test_case['name']}: Expected {expected}, got {priority}")
        else:
            print(f"✗ {test_case['name']}: Escalation failed")
    
    if passed == len(test_cases):
        print(f"\n✓ INTEGRATION TEST PASSED - All priority levels correct")
        return True
    else:
        print(f"\n✗ INTEGRATION TEST FAILED - {len(test_cases) - passed} priority levels incorrect")
        return False


def main():
    """Run all integration tests"""
    print("\n" + "=" * 70)
    print("ESCALATION AGENT - INTEGRATION TEST SUITE")
    print("=" * 70)
    
    tests = [
        ("Complete Escalation Flow", test_complete_escalation_flow),
        ("Escalation with Email in History", test_escalation_with_email_in_history),
        ("Priority Detection", test_priority_detection),
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
    print("INTEGRATION TEST SUMMARY")
    print("=" * 70)
    
    for test_name, passed in results.items():
        status = "PASSED" if passed else "FAILED"
        print(f"{test_name:40} {status}")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    print(f"\nTotal: {passed}/{total} integration tests passed")
    
    if passed == total:
        print("\nALL INTEGRATION TESTS PASSED!")
        return 0
    else:
        print(f"\n{total - passed} integration test(s) failed")
        return 1


if __name__ == "__main__":
    exit(main())
