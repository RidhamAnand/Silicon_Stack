"""
Comprehensive Test Suite for LLM-Enhanced Customer Support System
Tests LLM-based intent classification, entity extraction, and routing
"""

import sys
from colorama import Fore, Style, init

init(autoreset=True)

# Test counters
total_tests = 0
passed_tests = 0
failed_tests = 0


def print_header(title):
    """Print formatted header"""
    print("\n" + "=" * 80)
    print(Fore.CYAN + f"  {title}".upper())
    print("=" * 80)


def test_case(test_name, condition, expected=None, actual=None):
    """Check test condition and record results"""
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
    print(Fore.MAGENTA + "  FINAL TEST RESULTS")
    print("=" * 80)
    print(f"Total Tests:  {total_tests}")
    print(f"{Fore.GREEN}Passed: {passed_tests}")
    print(f"{Fore.RED}Failed: {failed_tests}")
    if total_tests > 0:
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    print("=" * 80 + "\n")
    
    return failed_tests == 0


# ============================================================================
# TEST 1: LLM INTENT CLASSIFICATION
# ============================================================================

def test_llm_intent_classification():
    """Test LLM-enhanced intent classification"""
    print_header("TEST 1: LLM Intent Classification")
    
    try:
        from src.classification.llm_intent_classifier import llm_intent_classifier
        from src.classification.intent_classifier import Intent
        
        test_cases = [
            ("What is the status of my order ORD-2024-001?", "order_status", "Order Status"),
            ("How much does shipping cost?", "shipping_delivery", "Shipping Question"),
            ("I want to return this item", "order_return", "Order Return"),
            ("My product is broken!", "complaint", "Complaint"),
            ("How do I reset my password?", "account_issue", "Account Issue"),
        ]
        
        print("\n[Testing LLM Intent Classification]")
        print("-" * 80)
        
        for query, expected_intent, description in test_cases:
            print(f"\nQuery: '{query}'")
            intent, confidence = llm_intent_classifier.classify_intent(query)
            actual_intent = intent.value.lower()
            
            # Check if intent matches or is close
            matches = actual_intent == expected_intent.lower()
            
            test_case(
                f"{description}",
                matches,
                expected=expected_intent,
                actual=actual_intent
            )
            print(f"   Confidence: {confidence:.2f}")
            
    except Exception as e:
        print(f"{Fore.RED}[ERROR]{Style.RESET_ALL}: {e}")
        import traceback
        traceback.print_exc()


# ============================================================================
# TEST 2: LLM ENTITY EXTRACTION
# ============================================================================

def test_llm_entity_extraction():
    """Test LLM-enhanced entity extraction"""
    print_header("TEST 2: LLM Entity Extraction")
    
    try:
        from src.classification.llm_entity_extractor import llm_entity_extractor
        
        test_cases = [
            ("What is the status of order ORD-2024-001?", "ORD-2024-001", "Order ID Extraction"),
            ("I want to return my order ORD-2024-002", "ORD-2024-002", "Order ID in Return"),
            ("Track my package ORD-2023-999", "ORD-2023-999", "Previous Year Order"),
        ]
        
        print("\n[Testing LLM Entity Extraction]")
        print("-" * 80)
        
        for query, expected_entity, description in test_cases:
            print(f"\nQuery: '{query}'")
            entities = llm_entity_extractor.extract_entities(query)
            
            found = any(e.get("value") == expected_entity for e in entities if e.get("type") == "order_number")
            
            test_case(
                f"{description}",
                found,
                expected=expected_entity,
                actual=str([e.get("value") for e in entities if e.get("type") == "order_number"])
            )
            print(f"   Extracted: {entities}")
            
    except Exception as e:
        print(f"{Fore.RED}[ERROR]{Style.RESET_ALL}: {e}")
        import traceback
        traceback.print_exc()


# ============================================================================
# TEST 3: LLM ROUTING DECISIONS
# ============================================================================

def test_llm_routing():
    """Test LLM-enhanced routing decisions"""
    print_header("TEST 3: LLM Routing Decisions")
    
    try:
        from src.agents.llm_router import llm_router
        
        test_cases = [
            {
                "query": "What is the status of order ORD-2024-001?",
                "intent": "order_status",
                "entities": [{"type": "order_number", "value": "ORD-2024-001", "confidence": 0.95}],
                "expected_agent": "order_handler",
                "description": "Order Status Query"
            },
            {
                "query": "How much does shipping cost?",
                "intent": "shipping_delivery",
                "entities": [],
                "expected_agent": "faq_agent",
                "description": "Shipping FAQ"
            },
            {
                "query": "My item arrived damaged!",
                "intent": "complaint",
                "entities": [],
                "expected_agent": "escalation_agent",
                "description": "Escalation - Damaged Item"
            },
        ]
        
        print("\n[Testing LLM Routing Decisions]")
        print("-" * 80)
        
        for test in test_cases:
            print(f"\nQuery: '{test['query']}'")
            
            decision = llm_router.route_query(
                session_id="test_session",
                user_query=test['query'],
                detected_intent=test['intent'],
                extracted_entities=test['entities'],
                conversation_history=[],
                current_agent=None
            )
            
            if decision:
                actual_agent = decision.get('target_agent', 'unknown')
                matches = actual_agent == test['expected_agent']
                
                test_case(
                    f"{test['description']}",
                    matches,
                    expected=test['expected_agent'],
                    actual=actual_agent
                )
                print(f"   Reasoning: {decision.get('reasoning', 'N/A')[:70]}")
            else:
                test_case(
                    f"{test['description']}",
                    False,
                    expected=test['expected_agent'],
                    actual="None (LLM failed)"
                )
            
    except Exception as e:
        print(f"{Fore.RED}[ERROR]{Style.RESET_ALL}: {e}")
        import traceback
        traceback.print_exc()


# ============================================================================
# TEST 4: HYBRID ROUTING (LLM + RULE-BASED)
# ============================================================================

def test_hybrid_routing():
    """Test hybrid routing combining LLM and rule-based approaches"""
    print_header("TEST 4: Hybrid Routing (LLM + Rule-Based)")
    
    try:
        from src.agents.hybrid_router import hybrid_router
        
        test_cases = [
            {
                "query": "Track my order ORD-2024-001",
                "intent": "order_status",
                "entities": [{"type": "order_number", "value": "ORD-2024-001"}],
                "expected_agent": "order_handler",
                "description": "Order Tracking"
            },
            {
                "query": "This is unacceptable! My product is broken!",
                "intent": "complaint",
                "entities": [],
                "expected_agent": "escalation_agent",
                "description": "Escalation Case"
            },
            {
                "query": "What is your return policy?",
                "intent": "faq",
                "entities": [],
                "expected_agent": "faq_agent",
                "description": "General FAQ"
            },
        ]
        
        print("\n[Testing Hybrid Routing Decisions]")
        print("-" * 80)
        
        for test in test_cases:
            print(f"\nQuery: '{test['query']}'")
            
            decision = hybrid_router.route_query_hybrid(
                session_id="test_session",
                user_query=test['query'],
                detected_intent=test['intent'],
                extracted_entities=test['entities'],
                conversation_history=[],
                current_agent=None
            )
            
            actual_agent = decision.get('target_agent', 'unknown')
            matches = actual_agent == test['expected_agent']
            method = decision.get('routing_method', 'unknown')
            
            test_case(
                f"{test['description']} (Method: {method})",
                matches,
                expected=test['expected_agent'],
                actual=actual_agent
            )
            print(f"   Routing Method: {method}")
            print(f"   Confidence: {decision.get('confidence', 'N/A')}")
            
    except Exception as e:
        print(f"{Fore.RED}[ERROR]{Style.RESET_ALL}: {e}")
        import traceback
        traceback.print_exc()


# ============================================================================
# TEST 5: LLM vs RULE-BASED COMPARISON
# ============================================================================

def test_llm_vs_rule_based():
    """Compare LLM and rule-based approaches"""
    print_header("TEST 5: LLM vs Rule-Based Comparison")
    
    try:
        from src.classification.llm_intent_classifier import llm_intent_classifier
        from src.classification.intent_classifier import intent_classifier as rule_based_classifier
        
        queries = [
            "Where can I track my package?",
            "What's your shipping policy?",
            "I want a refund for my order",
            "How do I change my account password?",
            "This product doesn't work!",
        ]
        
        print("\n[Comparing LLM vs Rule-Based Classification]")
        print("-" * 80)
        
        agreement_count = 0
        
        for query in queries:
            print(f"\nQuery: '{query}'")
            
            # Get LLM classification
            llm_intent, llm_conf = llm_intent_classifier.classify_intent(query)
            
            # Get rule-based classification
            rule_intent, rule_conf = rule_based_classifier.classify_intent(query)
            
            agree = llm_intent == rule_intent
            if agree:
                agreement_count += 1
            
            print(f"   LLM:        {llm_intent.value} (conf: {llm_conf:.2f})")
            print(f"   Rule-based: {rule_intent.value} (conf: {rule_conf:.2f})")
            print(f"   Agreement:  {'YES' if agree else 'NO'}")
        
        agreement_rate = (agreement_count / len(queries)) * 100
        test_case(
            f"LLM and Rule-Based Agreement",
            agreement_rate >= 60,  # At least 60% agreement
            expected=">= 60% agreement",
            actual=f"{agreement_rate:.1f}% agreement ({agreement_count}/{len(queries)})"
        )
        
    except Exception as e:
        print(f"{Fore.RED}[ERROR]{Style.RESET_ALL}: {e}")
        import traceback
        traceback.print_exc()


# ============================================================================
# TEST 6: MULTI-TURN CONVERSATION WITH LLM
# ============================================================================

def test_llm_multi_turn_conversation():
    """Test LLM routing across multi-turn conversations"""
    print_header("TEST 6: Multi-Turn Conversation with LLM")
    
    try:
        from src.agents.hybrid_router import hybrid_router
        
        conversation = [
            {
                "query": "Where is my order ORD-2024-001?",
                "expected_agent": "order_handler",
                "description": "Initial Order Query"
            },
            {
                "query": "When will it arrive?",
                "expected_agent": "order_handler",
                "description": "Follow-up - Delivery Time"
            },
            {
                "query": "Actually, I want to return it",
                "expected_agent": "order_handler",  # Still related to order
                "description": "Follow-up - Return Request"
            },
            {
                "query": "It arrived damaged!",
                "expected_agent": "escalation_agent",
                "description": "Escalation - Damaged Item"
            },
        ]
        
        print("\n[Testing Multi-Turn Conversation with LLM]")
        print("-" * 80)
        
        conversation_history = []
        current_agent = None
        
        for i, turn in enumerate(conversation, 1):
            print(f"\nTurn {i}: '{turn['query']}'")
            
            # Extract intent and entities (simplified)
            from src.classification.intent_classifier import intent_classifier
            intent, _ = intent_classifier.classify_intent(turn['query'])
            
            decision = hybrid_router.route_query_hybrid(
                session_id="multi_turn_test",
                user_query=turn['query'],
                detected_intent=intent.value,
                extracted_entities=[],
                conversation_history=conversation_history,
                current_agent=current_agent
            )
            
            actual_agent = decision.get('target_agent', 'unknown')
            matches = actual_agent == turn['expected_agent']
            
            test_case(
                f"Turn {i}: {turn['description']}",
                matches,
                expected=turn['expected_agent'],
                actual=actual_agent
            )
            
            # Update conversation history
            conversation_history.append({
                "role": "user",
                "content": turn['query']
            })
            conversation_history.append({
                "role": "assistant",
                "content": f"Routed to {actual_agent}"
            })
            current_agent = actual_agent
            
    except Exception as e:
        print(f"{Fore.RED}[ERROR]{Style.RESET_ALL}: {e}")
        import traceback
        traceback.print_exc()


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

if __name__ == "__main__":
    print("\n")
    print(Fore.MAGENTA + "+" + "=" * 78 + "+")
    print(Fore.MAGENTA + "|" + " " * 78 + "|")
    print(Fore.MAGENTA + "|" + "  LLM-ENHANCED CUSTOMER SUPPORT SYSTEM - TEST SUITE".center(78) + "|")
    print(Fore.MAGENTA + "|" + " " * 78 + "|")
    print(Fore.MAGENTA + "+" + "=" * 78 + "+")
    
    try:
        # Run all LLM tests
        test_llm_intent_classification()
        test_llm_entity_extraction()
        test_llm_routing()
        test_hybrid_routing()
        test_llm_vs_rule_based()
        test_llm_multi_turn_conversation()
        
        # Print final results
        success = print_results()
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"\n{Fore.RED}[ERROR]{Style.RESET_ALL}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
