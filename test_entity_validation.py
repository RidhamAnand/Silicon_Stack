"""
Test entity extraction with validation
"""
from src.classification.llm_entity_extractor import llm_entity_extractor

print("\n" + "="*80)
print("TESTING ENTITY EXTRACTION WITH VALIDATION")
print("="*80 + "\n")

test_cases = [
    ("What is the status of my order ORD-2024-001?", ["ORD-2024-001"]),
    ("Track package ORD-2024-002", ["ORD-2024-002"]),
    ("I want to return ORD-2023-999", ["ORD-2023-999"]),
    ("My order is 1234043d", []),  # Invalid order ID - should NOT match
    ("1234043d", []),  # Just a random string - should NOT match
    ("order number is 1234", []),  # No ORD prefix - should NOT match
    ("ORD-2024-001 and ORD-2024-002", ["ORD-2024-001", "ORD-2024-002"]),
]

for query, expected_orders in test_cases:
    print(f"Query: {query}")
    entities = llm_entity_extractor.extract_entities(query)
    
    order_numbers = [e['value'] for e in entities if e['type'] == 'order_number']
    
    if set(order_numbers) == set(expected_orders):
        print(f"  [PASS] Found: {order_numbers}")
    else:
        print(f"  [FAIL] Expected: {expected_orders}, Got: {order_numbers}")
    
    print()

print("="*80 + "\n")
