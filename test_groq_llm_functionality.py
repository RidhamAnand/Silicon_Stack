"""
Groq Cloud LLM Functionality Tests
Tests all LLM-enhanced components with Groq Cloud API
"""
import sys
from colorama import Fore, Back, Style

def print_header(text):
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80)

def print_test_section(name):
    print(f"\n[{name}]")
    print("-" * 80)

def print_pass(msg):
    print(f"{Fore.GREEN}[PASS]{Style.RESET_ALL} {msg}")

def print_fail(msg):
    print(f"{Fore.RED}[FAIL]{Style.RESET_ALL} {msg}")

def print_info(msg):
    print(f"   {msg}")

# Initialize counters
total_tests = 0
passed_tests = 0
failed_tests = 0

print_header("GROQ CLOUD LLM FUNCTIONALITY TESTS")

# Test 1: Intent Classification with Groq
print_test_section("TEST 1: LLM INTENT CLASSIFICATION")

from src.classification.llm_intent_classifier import llm_intent_classifier

test_cases = [
    ("What is the status of my order ORD-2024-001?", "order_status"),
    ("How much does shipping cost?", "shipping_delivery"),
    ("My item arrived damaged!", "complaint"),
    ("Can I return this product?", "order_return"),
    ("What's your return policy?", "faq"),
]

for query, expected_intent in test_cases:
    total_tests += 1
    intent, confidence = llm_intent_classifier.classify_intent(query)
    
    if intent.value == expected_intent:
        print_pass(f"{query}")
        print_info(f"Intent: {intent.value} (confidence: {confidence:.2f})")
        passed_tests += 1
    else:
        print_fail(f"{query}")
        print_info(f"Expected: {expected_intent}, Got: {intent.value}")
        failed_tests += 1

# Test 2: Entity Extraction with Groq
print_test_section("TEST 2: LLM ENTITY EXTRACTION")

from src.classification.llm_entity_extractor import llm_entity_extractor

entity_test_cases = [
    ("Where is my order ORD-2024-001?", "ORD-2024-001"),
    ("Track package ORD-2024-002", "ORD-2024-002"),
    ("I want to return ORD-2023-999", "ORD-2023-999"),
]

for query, expected_order in entity_test_cases:
    total_tests += 1
    entities = llm_entity_extractor.extract_entities(query)
    
    order_numbers = [e['value'] for e in entities if e['type'] == 'order_number']
    
    if expected_order in order_numbers:
        print_pass(f"{query}")
        print_info(f"Extracted: {order_numbers}")
        passed_tests += 1
    else:
        print_fail(f"{query}")
        print_info(f"Expected: {expected_order}, Got: {order_numbers}")
        failed_tests += 1

# Test 3: Routing with Groq
print_test_section("TEST 3: LLM ROUTING")

from src.agents.llm_router import llm_router

routing_test_cases = [
    ("Where is my order ORD-2024-001?", "order_status", "order_handler"),
    ("What's your return policy?", "faq", "faq_agent"),
    ("This product is broken and I'm very angry!", "complaint", "escalation_agent"),
]

for query, intent_type, expected_agent in routing_test_cases:
    total_tests += 1
    decision = llm_router.route_query(
        user_query=query,
        detected_intent=intent_type
    )
    
    if decision and decision.get('target_agent') == expected_agent:
        print_pass(f"{query}")
        print_info(f"Agent: {decision['target_agent']} (confidence: {decision['confidence']:.2f})")
        passed_tests += 1
    else:
        agent = decision.get('target_agent') if decision else "None"
        print_fail(f"{query}")
        print_info(f"Expected: {expected_agent}, Got: {agent}")
        failed_tests += 1

# Test 4: Hybrid Routing (LLM + Rule-Based)
print_test_section("TEST 4: HYBRID ROUTING")

from src.agents.hybrid_router import hybrid_router

hybrid_test_cases = [
    ("Where is my order?", "order_status"),
    ("How do I return this?", "order_return"),
    ("I need to escalate this NOW!", "complaint"),
]

for query, intent_type in hybrid_test_cases:
    total_tests += 1
    
    decision = hybrid_router.route_query(
        user_query=query,
        detected_intent=intent_type
    )
    
    if decision and decision.get('target_agent'):
        print_pass(f"{query}")
        print_info(f"Agent: {decision['target_agent']}")
        print_info(f"Validation: {decision.get('validation', 'N/A')}")
        print_info(f"Method: {decision.get('method', 'N/A')}")
        passed_tests += 1
    else:
        print_fail(f"{query}")
        print_info(f"No routing decision")
        failed_tests += 1

# Test 5: Context-Aware Routing
print_test_section("TEST 5: CONTEXT-AWARE ROUTING")

conversation_history = [
    {"role": "user", "content": "Where is my order ORD-2024-001?"},
    {"role": "assistant", "content": "Let me check your order status..."},
]

total_tests += 1
decision = llm_router.route_query(
    user_query="When will it arrive?",
    detected_intent="order_status",
    conversation_history=conversation_history
)

if decision and decision.get('target_agent') == "order_handler":
    print_pass("Multi-turn conversation context maintained")
    print_info(f"Agent: {decision['target_agent']}")
    passed_tests += 1
else:
    print_fail("Multi-turn conversation context lost")
    agent = decision.get('target_agent') if decision else "None"
    print_info(f"Got: {agent}, Expected: order_handler")
    failed_tests += 1

# Test 6: Intent Classification with Confidence
print_test_section("TEST 6: CONFIDENCE SCORING")

confidence_test = "I want to return this broken item for a refund"
total_tests += 1

intent, confidence = llm_intent_classifier.classify_intent(confidence_test)

if confidence >= 0.7:
    print_pass(f"High confidence classification")
    print_info(f"Intent: {intent.value}")
    print_info(f"Confidence: {confidence:.2f} (>= 0.7)")
    passed_tests += 1
else:
    print_fail(f"Low confidence classification")
    print_info(f"Intent: {intent.value}")
    print_info(f"Confidence: {confidence:.2f} (< 0.7)")
    failed_tests += 1

# Summary
print_header("TEST RESULTS SUMMARY")

print(f"\nTotal Tests:  {total_tests}")
print(f"Passed:       {Fore.GREEN}{passed_tests}{Style.RESET_ALL}")
print(f"Failed:       {Fore.RED}{failed_tests}{Style.RESET_ALL}")

if total_tests > 0:
    pass_rate = (passed_tests / total_tests) * 100
    if pass_rate >= 80:
        color = Fore.GREEN
    elif pass_rate >= 60:
        color = Fore.YELLOW
    else:
        color = Fore.RED
    
    print(f"Success Rate: {color}{pass_rate:.1f}%{Style.RESET_ALL}")

print("\n" + "="*80)

sys.exit(0 if failed_tests == 0 else 1)
