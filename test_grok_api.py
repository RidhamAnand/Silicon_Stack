"""
Test Grok API Integration
Tests direct API calls to Grok for intent classification, entity extraction, and routing
"""
import sys

print("\n" + "="*80)
print("TESTING GROK API INTEGRATION")
print("="*80 + "\n")

# Test 1: Intent Classification with Grok
print("[TEST 1] LLM Intent Classification with Grok")
print("-" * 80)

try:
    from src.classification.llm_intent_classifier import llm_intent_classifier
    
    test_queries = [
        "What is the status of my order ORD-2024-001?",
        "How much does shipping cost?",
        "My item arrived damaged!",
    ]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        intent, confidence = llm_intent_classifier.classify_intent(query)
        print(f"Result: {intent.value} (confidence: {confidence:.2f})")
        
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Entity Extraction with Grok
print("\n" + "="*80)
print("[TEST 2] LLM Entity Extraction with Grok")
print("-" * 80)

try:
    from src.classification.llm_entity_extractor import llm_entity_extractor
    
    test_queries = [
        "Where is my order ORD-2024-001?",
        "Track package ORD-2024-002",
        "I want to return ORD-2023-999",
    ]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        entities = llm_entity_extractor.extract_entities(query)
        print(f"Entities: {entities}")
        
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Routing with Grok
print("\n" + "="*80)
print("[TEST 3] LLM Routing with Grok")
print("-" * 80)

try:
    from src.agents.llm_router import llm_router
    
    test_cases = [
        {
            "query": "Where is my order ORD-2024-001?",
            "intent": "order_status",
            "entities": [{"type": "order_number", "value": "ORD-2024-001"}]
        },
        {
            "query": "What's your return policy?",
            "intent": "faq",
            "entities": []
        },
        {
            "query": "This product is broken and I'm very angry!",
            "intent": "complaint",
            "entities": []
        }
    ]
    
    for test in test_cases:
        print(f"\nQuery: '{test['query']}'")
        
        decision = llm_router.route_query(
            user_query=test['query'],
            detected_intent=test['intent'],
            extracted_entities=test['entities']
        )
        
        if decision:
            print(f"Agent: {decision['target_agent']}")
            print(f"Confidence: {decision['confidence']:.2f}")
            print(f"Reason: {decision.get('reasoning', decision.get('reason', 'N/A'))}")
        else:
            print("No routing decision from Grok")
        
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("GROK API TESTS COMPLETED")
print("="*80 + "\n")
