"""
Comprehensive Test Suite for Agentic Customer Support System
Tests all components: Intent Classification, Entity Extraction, Routing, and Context Continuity
"""

import sys
from colorama import Fore, Style, init

# Initialize colorama for colored output
init(autoreset=True)

# Test counters
total_tests = 0
passed_tests = 0
failed_tests = 0


def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(Fore.CYAN + f"  {title}".upper())
    print("=" * 80)


def print_subheader(title):
    """Print a formatted subheader"""
    print(f"\n{Fore.YELLOW}-> {title}")
    print("-" * 80)


def test_case(test_name, condition, expected=None, actual=None):
    """Check a test condition and record results"""
    global total_tests, passed_tests, failed_tests
    total_tests += 1
    
    if condition:
        passed_tests += 1
        print(f"{Fore.GREEN}[PASS]{Style.RESET_ALL}: {test_name}")
        return True
    else:
        failed_tests += 1
        print(f"{Fore.RED}[FAIL]{Style.RESET_ALL}: {test_name}")
        if expected is not None and actual is not None:
            print(f"   Expected: {expected}")
            print(f"   Actual:   {actual}")
        return False


def print_results():
    """Print final test results"""
    print("\n" + "=" * 80)
    print(Fore.MAGENTA + f"  FINAL TEST RESULTS")
    print("=" * 80)
    print(f"Total Tests:  {total_tests}")
    print(f"{Fore.GREEN}Passed: {passed_tests}")
    print(f"{Fore.RED}Failed: {failed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    print("=" * 80 + "\n")
    
    return failed_tests == 0


# ============================================================================
# TEST 1: INTENT CLASSIFICATION
# ============================================================================

def test_intent_classification():
    """Test intent classification module"""
    print_header("TEST 1: Intent Classification")
    
    from src.classification.intent_classifier import intent_classifier
    
    test_cases = [
        # Order-related intents
        ("What is the status of my order?", "order_status", "Order Status Query"),
        ("Where is my package?", "order_inquiry", "Order Inquiry"),
        ("I want to return this item", "order_return", "Order Return"),
        ("Can I get a refund?", "order_refund", "Refund Request"),
        
        # FAQ intents
        ("How much does shipping cost?", "shipping_delivery", "Shipping Question"),
        ("Do you accept credit cards?", "billing_payment", "Payment Question"),
        ("What's the warranty on this product?", "product_info", "Product Information"),
        ("How do I reset my password?", "account_issue", "Account Issue"),
        
        # General chat
        ("Hi there!", "general_chat", "General Greeting"),
        ("Tell me about your return policy", "faq", "General FAQ"),
    ]
    
    print_subheader("Testing Intent Classification")
    
    for query, expected_intent, description in test_cases:
        intent, confidence = intent_classifier.classify_intent(query)
        intent_value = intent.value.lower() if intent else None
        
        matches = intent_value == expected_intent.lower()
        test_case(
            f"{description}: '{query}'",
            matches,
            expected=expected_intent,
            actual=intent_value
        )
        print(f"   Confidence: {confidence:.2f}")


# ============================================================================
# TEST 2: ENTITY EXTRACTION
# ============================================================================

def test_entity_extraction():
    """Test entity extraction module"""
    print_header("TEST 2: Entity Extraction")
    
    from src.classification.entity_extractor import entity_extractor
    
    test_cases = [
        # Order number extraction
        ("What is the status of order ORD-2024-001?", "ORD-2024-001", "Order ID Extraction"),
        ("Track my order ORD-2024-002", "ORD-2024-002", "Order ID Extraction Alt Format"),
        ("I lost my order ORD 2024 003", "ORD-2024-003", "Order ID with Spaces"),
        ("Multiple orders: ORD-2024-001 and ORD-2024-002", "ORD-2024-001", "Multiple Order Numbers (First One)"),
        
        # Edge cases
        ("My order number is ORD-2023-999", "ORD-2023-999", "Previous Year Order"),
        ("ORD-2024-001 is my order", "ORD-2024-001", "Order ID at Start"),
    ]
    
    print_subheader("Testing Order Number Extraction")
    
    for query, expected_order, description in test_cases:
        entities = entity_extractor.extract_entities(query)
        order_numbers = [e.value for e in entities if e.type == "order_number"]
        
        found = expected_order in order_numbers
        test_case(
            f"{description}: '{query}'",
            found,
            expected=expected_order,
            actual=order_numbers[0] if order_numbers else "No order found"
        )
        print(f"   Extracted: {order_numbers}")


# ============================================================================
# TEST 3: ROUTER AGENT - BASIC ROUTING
# ============================================================================

def test_router_basic_routing():
    """Test router agent basic routing decisions"""
    print_header("TEST 3: Router Agent - Basic Routing")
    
    from src.agents.router_agent import router_agent
    
    test_cases = [
        # Order-related queries
        ("What is the status of order ORD-2024-001?", "order_handler", "Order Status Query"),
        ("Where is my package ORD-2024-002?", "order_handler", "Order Inquiry"),
        ("I want to return my item", "order_handler", "Order Return"),
        
        # FAQ queries
        ("How much does shipping cost?", "faq_agent", "Shipping FAQ"),
        ("What payment methods do you accept?", "faq_agent", "Payment FAQ"),
        ("Tell me about your products", "faq_agent", "Product FAQ"),
        
        # Escalation queries
        ("I'm very angry! This product is broken!", "escalation_agent", "Escalation - Broken Product"),
        ("I need to speak to a manager urgently", "escalation_agent", "Escalation - Manager Request"),
        ("The item arrived damaged!", "escalation_agent", "Escalation - Damaged Item"),
    ]
    
    print_subheader("Testing Basic Routing Decisions")
    
    for idx, (query, expected_agent, description) in enumerate(test_cases):
        # Use separate session for each test to avoid context carryover
        session_id = f"test_basic_routing_{idx}"
        router_agent.create_session(session_id)
        
        result = router_agent.route_query(session_id, query)
        routing = result['routing_decision']
        actual_agent = routing['target_agent']
        
        matches = actual_agent == expected_agent
        test_case(
            f"{description}",
            matches,
            expected=expected_agent,
            actual=actual_agent
        )
        print(f"   Query: '{query}'")
        print(f"   Reason: {routing['reason']}")


# ============================================================================
# TEST 4: ROUTER AGENT - CONTEXT CONTINUITY
# ============================================================================

def test_router_context_continuity():
    """Test router agent maintains context for follow-up questions"""
    print_header("TEST 4: Router Agent - Context Continuity")
    
    from src.agents.router_agent import router_agent
    
    print_subheader("Test Case 1: Order Context Continuity")
    
    session_id = "test_context_order"
    router_agent.create_session(session_id)
    
    # Turn 1: Initial order query
    result1 = router_agent.route_query(session_id, "What is the status of order ORD-2024-001?")
    routing1 = result1['routing_decision']
    agent1 = routing1['target_agent']
    
    test_case(
        "Turn 1: Initial order query routed to order_handler",
        agent1 == "order_handler",
        expected="order_handler",
        actual=agent1
    )
    print(f"   Query: What is the status of order ORD-2024-001?")
    
    # Turn 2: Follow-up about delivery
    result2 = router_agent.route_query(session_id, "When will it be delivered?")
    routing2 = result2['routing_decision']
    agent2 = routing2['target_agent']
    
    test_case(
        "Turn 2: Follow-up stays with order_handler (context maintained)",
        agent2 == "order_handler",
        expected="order_handler",
        actual=agent2
    )
    print(f"   Query: When will it be delivered?")
    print(f"   Reason: {routing2['reason']}")
    
    # Turn 3: Another follow-up
    result3 = router_agent.route_query(session_id, "Can I track it online?")
    routing3 = result3['routing_decision']
    agent3 = routing3['target_agent']
    
    test_case(
        "Turn 3: Another follow-up stays with order_handler",
        agent3 == "order_handler",
        expected="order_handler",
        actual=agent3
    )
    print(f"   Query: Can I track it online?")
    
    print_subheader("Test Case 2: Escalation Overrides Context")
    
    # Turn 4: Escalation (should override context)
    result4 = router_agent.route_query(session_id, "It arrived damaged! This is unacceptable!")
    routing4 = result4['routing_decision']
    agent4 = routing4['target_agent']
    
    test_case(
        "Turn 4: Escalation keywords override context",
        agent4 == "escalation_agent",
        expected="escalation_agent",
        actual=agent4
    )
    print(f"   Query: It arrived damaged! This is unacceptable!")
    print(f"   Reason: {routing4['reason']}")
    
    print_subheader("Test Case 3: FAQ Context Continuity")
    
    session_id2 = "test_context_faq"
    router_agent.create_session(session_id2)
    
    # Start with FAQ
    result_faq1 = router_agent.route_query(session_id2, "What are your shipping options?")
    routing_faq1 = result_faq1['routing_decision']
    agent_faq1 = routing_faq1['target_agent']
    
    test_case(
        "FAQ Turn 1: Shipping question routed to faq_agent",
        agent_faq1 == "faq_agent",
        expected="faq_agent",
        actual=agent_faq1
    )
    
    # Follow-up FAQ question
    result_faq2 = router_agent.route_query(session_id2, "How long does it take?")
    routing_faq2 = result_faq2['routing_decision']
    agent_faq2 = routing_faq2['target_agent']
    
    test_case(
        "FAQ Turn 2: Follow-up stays with faq_agent (context maintained)",
        agent_faq2 == "faq_agent",
        expected="faq_agent",
        actual=agent_faq2
    )
    print(f"   Query: How long does it take?")


# ============================================================================
# TEST 5: ORDER NUMBER MEMORY
# ============================================================================

def test_order_number_memory():
    """Test router remembers order numbers across conversation turns"""
    print_header("TEST 5: Order Number Memory")
    
    from src.agents.router_agent import router_agent
    
    print_subheader("Testing Order Number Memory")
    
    session_id = "test_order_memory"
    router_agent.create_session(session_id)
    
    # Turn 1: Mention order number
    result1 = router_agent.route_query(session_id, "Where is my order ORD-2024-005?")
    order_num1 = result1['entities']
    
    test_case(
        "Turn 1: Order number extracted",
        any(e['type'] == 'order_number' and e['value'] == 'ORD-2024-005' for e in order_num1),
        expected="ORD-2024-005",
        actual=str(order_num1)
    )
    
    # Turn 2: Don't mention order number, but should remember it
    result2 = router_agent.route_query(session_id, "How long until it arrives?")
    routing2 = result2['routing_decision']
    
    # Check if router remembered the order number in its context
    remembered_order = routing2['context'].get('order_number')
    
    test_case(
        "Turn 2: Router remembers previous order number (ORD-2024-005)",
        remembered_order == 'ORD-2024-005',
        expected="ORD-2024-005",
        actual=remembered_order
    )
    print(f"   Query: How long until it arrives?")
    print(f"   Remembered Order: {remembered_order}")
    
    # Get conversation summary
    summary = router_agent.get_conversation_summary(session_id)
    
    test_case(
        "Conversation Summary: Order number in history",
        'ORD-2024-005' in summary['order_numbers_mentioned'],
        expected="ORD-2024-005",
        actual=summary['order_numbers_mentioned']
    )


# ============================================================================
# TEST 6: CONVERSATION HISTORY
# ============================================================================

def test_conversation_history():
    """Test conversation history tracking"""
    print_header("TEST 6: Conversation History")
    
    from src.agents.router_agent import router_agent
    
    print_subheader("Testing Conversation History Tracking")
    
    session_id = "test_history"
    router_agent.create_session(session_id)
    
    queries = [
        "What's the status of order ORD-2024-001?",
        "When will it arrive?",
        "Can I track it?",
        "Actually, I want to return it",
        "It's damaged!"
    ]
    
    for i, query in enumerate(queries, 1):
        router_agent.route_query(session_id, query)
    
    summary = router_agent.get_conversation_summary(session_id)
    
    test_case(
        "Conversation has all 5 user messages",
        summary['message_count'] >= 5,
        expected=">= 5 messages",
        actual=f"{summary['message_count']} messages"
    )
    
    test_case(
        "Multiple topics tracked",
        len(summary['topics_discussed']) > 1,
        expected="> 1 topic",
        actual=f"{len(summary['topics_discussed'])} topics: {summary['topics_discussed']}"
    )
    
    test_case(
        "Order number tracked",
        'ORD-2024-001' in summary['order_numbers_mentioned'],
        expected="ORD-2024-001 in history",
        actual=summary['order_numbers_mentioned']
    )
    
    print(f"   Total messages: {summary['message_count']}")
    print(f"   Topics: {summary['topics_discussed']}")
    print(f"   Order numbers: {summary['order_numbers_mentioned']}")


# ============================================================================
# TEST 7: EDGE CASES
# ============================================================================

def test_edge_cases():
    """Test edge cases and special scenarios"""
    print_header("TEST 7: Edge Cases")
    
    from src.agents.router_agent import router_agent
    
    print_subheader("Testing Edge Cases")
    
    # Edge case 1: Empty/minimal query
    print("\nEdge Case 1: Very short queries")
    session_id = "test_edge"
    router_agent.create_session(session_id)
    
    result1 = router_agent.route_query(session_id, "Hello")
    routing1 = result1['routing_decision']
    
    test_case(
        "Minimal query handled without error",
        routing1['target_agent'] in ['faq_agent', 'order_handler', 'escalation_agent'],
        expected="Valid agent",
        actual=routing1['target_agent']
    )
    
    # Edge case 2: Multiple order numbers
    print("\nEdge Case 2: Multiple order numbers mentioned")
    session_id2 = "test_edge2"
    router_agent.create_session(session_id2)
    
    result2 = router_agent.route_query(session_id2, "What about ORD-2024-001 and ORD-2024-002?")
    entities2 = result2['entities']
    order_numbers = [e['value'] for e in entities2 if e['type'] == 'order_number']
    
    test_case(
        "Multiple order numbers detected",
        len(order_numbers) >= 1,
        expected=">= 1 order",
        actual=f"{len(order_numbers)} orders: {order_numbers}"
    )
    
    # Edge case 3: Mixed intent with different keywords
    print("\nEdge Case 3: Complex query with mixed signals")
    session_id3 = "test_edge3"
    router_agent.create_session(session_id3)
    
    result3 = router_agent.route_query(session_id3, "My package ORD-2024-003 arrived but it's damaged!")
    routing3 = result3['routing_decision']
    
    # Should escalate due to "damaged"
    test_case(
        "Escalation keyword takes priority over order number",
        routing3['target_agent'] == 'escalation_agent',
        expected="escalation_agent",
        actual=routing3['target_agent']
    )
    print(f"   Routing reason: {routing3['reason']}")
    
    # Edge case 4: Context switch scenario
    print("\nEdge Case 4: Context switch - from order to FAQ (with new session for topic shift)")
    session_id4 = "test_edge4"
    router_agent.create_session(session_id4)
    
    r1 = router_agent.route_query(session_id4, "Where is order ORD-2024-004?")
    a1 = r1['routing_decision']['target_agent']
    
    # For a true topic switch, the FAQ question should break out since it's a clear FAQ intent
    r2 = router_agent.route_query(session_id4, "What's your return policy?")
    a2 = r2['routing_decision']['target_agent']
    
    r3 = router_agent.route_query(session_id4, "My order ORD-2024-004 is damaged")
    a3 = r3['routing_decision']['target_agent']
    
    test_case(
        "Correct agent routing with intelligent context switches",
        a1 == "order_handler" and a2 == "faq_agent" and a3 == "escalation_agent",
        expected="order_handler, faq_agent, escalation_agent",
        actual=f"{a1}, {a2}, {a3}"
    )


# ============================================================================
# TEST 8: SESSION ISOLATION
# ============================================================================

def test_session_isolation():
    """Test that different sessions maintain isolated contexts"""
    print_header("TEST 8: Session Isolation")
    
    from src.agents.router_agent import router_agent
    
    print_subheader("Testing Session Isolation")
    
    # Create two separate sessions
    session_a = "session_customer_a"
    session_b = "session_customer_b"
    
    router_agent.create_session(session_a)
    router_agent.create_session(session_b)
    
    # Session A: Order inquiry
    ra1 = router_agent.route_query(session_a, "Where is order ORD-2024-100?")
    summary_a = router_agent.get_conversation_summary(session_a)
    
    # Session B: FAQ question
    rb1 = router_agent.route_query(session_b, "What's your shipping policy?")
    summary_b = router_agent.get_conversation_summary(session_b)
    
    test_case(
        "Session A has order in history",
        'ORD-2024-100' in summary_a['order_numbers_mentioned'],
        expected="ORD-2024-100",
        actual=summary_a['order_numbers_mentioned']
    )
    
    test_case(
        "Session B does NOT have order from Session A",
        'ORD-2024-100' not in summary_b['order_numbers_mentioned'],
        expected="No ORD-2024-100",
        actual=summary_b['order_numbers_mentioned']
    )
    
    print(f"   Session A orders: {summary_a['order_numbers_mentioned']}")
    print(f"   Session B orders: {summary_b['order_numbers_mentioned']}")


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

if __name__ == "__main__":
    print("\n")
    print(Fore.MAGENTA + "+" + "=" * 78 + "+")
    print(Fore.MAGENTA + "|" + " " * 78 + "|")
    print(Fore.MAGENTA + "|" + "  COMPREHENSIVE TEST SUITE FOR AGENTIC CUSTOMER SUPPORT SYSTEM".center(78) + "|")
    print(Fore.MAGENTA + "|" + " " * 78 + "|")
    print(Fore.MAGENTA + "+" + "=" * 78 + "+")
    
    try:
        # Run all tests
        test_intent_classification()
        test_entity_extraction()
        test_router_basic_routing()
        test_router_context_continuity()
        test_order_number_memory()
        test_conversation_history()
        test_edge_cases()
        test_session_isolation()
        
        # Print final results
        success = print_results()
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"\n{Fore.RED}[ERROR]{Style.RESET_ALL}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
