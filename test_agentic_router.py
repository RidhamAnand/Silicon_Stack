"""
Test script for agentic router architecture with context continuity
"""
from src.agents.router_agent import router_agent

session_id = 'test_session_123'

print('='*80)
print('TEST: Agentic Router with Context Continuity')
print('='*80)
print()

# Test 1: Order query
print('Test 1: User - What is the status of order ORD-2024-001?')
result1 = router_agent.route_query(session_id, 'What is the status of order ORD-2024-001?')
routing1 = result1['routing_decision']
print(f'  Router Decision: {routing1["target_agent"]}')
print(f'  Reason: {routing1["reason"]}')
print(f'  Order number detected: {routing1["context"].get("order_number")}')
print(f'  ✓ Agent Selected: {routing1["target_agent"]}')
print()

# Test 2: Follow-up about delivery (SHOULD STAY WITH ORDER_HANDLER)
print('Test 2: User - When will it be delivered? [FOLLOW-UP]')
result2 = router_agent.route_query(session_id, 'When will it be delivered?')
routing2 = result2['routing_decision']
print(f'  Router Decision: {routing2["target_agent"]}')
print(f'  Reason: {routing2["reason"]}')
print(f'  Is Follow-up: {routing2["context"].get("is_followup", routing2["context"].get("follow_up"))}')
print(f'  Previous Agent: {routing2["context"].get("previous_agent")}')
print(f'  ✓ Agent Selected: {routing2["target_agent"]}')
print()

# Verify context continuity
if routing1['target_agent'] == routing2['target_agent'] == 'order_handler':
    print('✅ PASS: Context continuity maintained! Both routed to order_handler')
else:
    print(f'❌ FAIL: Context not maintained!')
    print(f'   Turn 1: {routing1["target_agent"]}')
    print(f'   Turn 2: {routing2["target_agent"]}')
print()

# Test 3: Another follow-up (SHOULD STILL BE ORDER_HANDLER)
print('Test 3: User - Can I track it online? [FOLLOW-UP]')
result3 = router_agent.route_query(session_id, 'Can I track it online?')
routing3 = result3['routing_decision']
print(f'  Router Decision: {routing3["target_agent"]}')
print(f'  Reason: {routing3["reason"]}')
print(f'  ✓ Agent Selected: {routing3["target_agent"]}')
print()

if routing3['target_agent'] == 'order_handler':
    print('✅ PASS: Follow-up question routed to order_handler (context maintained)')
else:
    print(f'❌ FAIL: Lost context on second follow-up!')
print()

# Test 4: Return request (escalation - should override context)
print('Test 4: User - I want to return it, it arrived damaged [ESCALATION]')
result4 = router_agent.route_query(session_id, 'I want to return it, it arrived damaged')
routing4 = result4['routing_decision']
print(f'  Router Decision: {routing4["target_agent"]}')
print(f'  Reason: {routing4["reason"]}')
print(f'  Escalation Level: {routing4["context"].get("escalation_level")}')
print(f'  ✓ Agent Selected: {routing4["target_agent"]}')
print()

if routing4['target_agent'] == 'escalation_agent':
    print('✅ PASS: Escalation keywords triggered escalation_agent (overrides context)')
else:
    print(f'❌ FAIL: Escalation not detected!')
print()

# Test 5: Conversation summary
print('='*80)
print('Conversation Summary:')
print('='*80)
summary = router_agent.get_conversation_summary(session_id)
print(f'Total messages: {summary["message_count"]}')
print(f'Order numbers mentioned: {summary["order_numbers_mentioned"]}')
print(f'Topics discussed: {summary["topics_discussed"]}')
print(f'Agent sequence: {" → ".join([routing1["target_agent"], routing2["target_agent"], routing3["target_agent"], routing4["target_agent"]])}')
print('='*80)

