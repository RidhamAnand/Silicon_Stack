from src.classification.intent_classifier import intent_classifier

test_queries = [
    "i have received defected item",
    "my item is broken",
    "the product is damaged",
    "wrong item received",
    "defective product"
]

for query in test_queries:
    intent, conf = intent_classifier.classify_intent(query)
    print(f"Query: '{query}'")
    print(f"  Intent: {intent.value}, Confidence: {conf:.2f}")
    print()
