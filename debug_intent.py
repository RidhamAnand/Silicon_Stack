#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.classification.intent_classifier import intent_classifier

# Test the problematic queries
test_queries = [
    'I want to return my order',
    'ORD-2024-001'
]

print("Intent Classification Test:")
print("=" * 40)

for query in test_queries:
    intent, confidence = intent_classifier.classify_intent(query)
    print(f'Query: "{query}"')
    print(f'Intent: {intent.value} (Confidence: {confidence:.1%})')
    print()