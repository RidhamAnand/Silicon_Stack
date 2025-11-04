"""
Debug context switch - detailed
"""

query = "What's your return policy?"
query_lower = query.lower()

related_keywords = [
    "deliver", "arrive", "ship", "tracking", "when", "time",
    "refund", "return", "exchange", "issue", "problem",
    "price", "cost", "quantity", "item", "status", "track"
]

is_related_followup = any(kw in query_lower for kw in related_keywords)
print(f"Query: {query_lower}")
print(f"Related keywords found: {[kw for kw in related_keywords if kw in query_lower]}")
print(f"is_related_followup: {is_related_followup}")

# The problem is "return" is in the related_keywords but "return policy" is FAQ, not order-related
