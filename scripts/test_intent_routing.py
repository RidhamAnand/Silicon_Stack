#!/usr/bin/env python3
"""
Test script for Checkpoint 2: Intent Classification & Routing
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.classification.intent_router import intent_router

def test_intent_routing():
    """Test various queries to demonstrate intent routing"""

    test_queries = [
        # FAQ queries
        "What are your shipping options?",
        "Do you accept PayPal?",
        "What's your return policy?",

        # Order queries
        "Where is my order ABC123?",
        "I want to return order XYZ789",
        "When will my refund for order ORD456 be processed?",

        # Complaints
        "I'm really angry about my broken product",
        "This product is terrible and doesn't work",
        "I'm frustrated with your service",

        # Account issues
        "I can't log into my account",
        "How do I reset my password?",
        "I need to update my email address",

        # Technical support
        "Your website is not working",
        "I can't access the app",
        "The system is giving me an error",

        # Escalation requests
        "I need to speak to a manager",
        "Connect me to a human representative",
        "I want to talk to someone right now",

        # General chat
        "Hello",
        "Thank you",
        "Goodbye"
    ]

    print("🧪 Testing Intent Classification & Routing System")
    print("=" * 60)

    for i, query in enumerate(test_queries, 1):
        print(f"\n{i:2d}. Query: '{query}'")
        print("-" * 40)

        try:
            result = intent_router.process_query(query)

            print(f"   Intent: {result['intent']} (Confidence: {result['intent_confidence']:.1%})")
            print(f"   Entities: {len(result['entities'])} found")
            if result['entities']:
                for entity in result['entities'][:2]:  # Show first 2 entities
                    print(f"     - {entity['type']}: {entity['value']}")

            print(f"   Route: {' → '.join(result['routing_path'])}")
            print(f"   Escalation: {'Yes' if result['needs_escalation'] else 'No'}")

            # Show response (truncated)
            response = result['response']
            if len(response) > 100:
                response = response[:97] + "..."
            print(f"   Response: {response}")

        except Exception as e:
            print(f"   ❌ Error: {e}")

    print("\n" + "=" * 60)
    print("✅ Intent routing test completed!")

if __name__ == "__main__":
    test_intent_routing()