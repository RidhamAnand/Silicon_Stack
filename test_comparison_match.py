"""
Comparison Test: Good Match vs No Match
Shows difference between FAQ answers and no-match scenarios
"""
import sys
import os
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
os.chdir(project_root)

from src.rag.pipeline import rag_pipeline
from src.agents.ticket_agent import ticket_agent

print("\n" + "=" * 80)
print("TEST: FAQ MATCH vs NO-MATCH COMPARISON")
print("=" * 80)

# TEST 1: GOOD FAQ MATCH
print("\n" + "-" * 80)
print("SCENARIO 1: Good FAQ Match (Should NOT suggest ticket)")
print("-" * 80)

good_query = "What is your return policy?"
print(f"\nQuery: {good_query}\n")

faq_result = rag_pipeline._search_faqs(good_query)
print(f"FAQ Response Score: {faq_result['top_score']:.2f}")
print(f"Should Create Ticket: {faq_result.get('should_create_ticket', False)}")
print(f"Response:\n{faq_result['response']}")

if not faq_result.get('should_create_ticket', False):
    print("\n✅ CORRECT: Good FAQ match found - no ticket suggestion")
else:
    print("\n❌ ERROR: Should not suggest ticket for good FAQ match!")

# TEST 2: NO FAQ MATCH
print("\n" + "-" * 80)
print("SCENARIO 2: No FAQ Match (SHOULD suggest ticket)")
print("-" * 80)

bad_query = "How can I turn my phone into a holographic projector?"
print(f"\nQuery: {bad_query}\n")

faq_result2 = rag_pipeline._search_faqs(bad_query)
print(f"FAQ Response Score: {faq_result2['top_score']:.2f}")
print(f"Should Create Ticket: {faq_result2.get('should_create_ticket', False)}")
print(f"Response:\n{faq_result2['response']}")

if faq_result2.get('should_create_ticket', False):
    print("\n✅ CORRECT: No FAQ match - suggests ticket creation")
    
    # Auto-create ticket
    result = ticket_agent.create_ticket_from_faq_no_match(
        user_query=bad_query,
        user_email="user123@test.com"
    )
    print(f"\n✅ Ticket auto-created: {result['ticket_id']}")
else:
    print("\n❌ ERROR: Should suggest ticket for no FAQ match!")

# TEST 3: LOW-SCORE MATCH (Edge case)
print("\n" + "-" * 80)
print("SCENARIO 3: Low-Score Match (SHOULD suggest ticket)")
print("-" * 80)

edge_query = "Something very specific that might not have a clear FAQ"
print(f"\nQuery: {edge_query}\n")

faq_result3 = rag_pipeline._search_faqs(edge_query)
print(f"FAQ Response Score: {faq_result3['top_score']:.2f}")
print(f"Should Create Ticket: {faq_result3.get('should_create_ticket', False)}")
print(f"Response:\n{faq_result3['response'][:150]}...")

print("\n" + "=" * 80)
print("✅ COMPARISON TEST COMPLETE")
print("=" * 80)
print("\nSystem prevents hallucination by:")
print("  • Score >= 0.50 → Return FAQ answer (high confidence)")
print("  • Score <  0.50 → Suggest creating support ticket")
print("  • User accepts  → Create ticket with reason captured")
print("  • Return ticket ID for tracking (TKT-XXXXXXXX format)")
print("=" * 80 + "\n")
