"""
Debug test to check context continuity in router agent
"""
from src.agents.router_agent import router_agent

session_id = 'debug_session'

print('='*80)
print('DEBUG: Testing Context Continuity')
print('='*80)
print()

# Test 1: Order query
print('[Turn 1] User: What is the status of order ORD-2024-001?')
result1 = router_agent.route_query(session_id, 'What is the status of order ORD-2024-001?')
routing1 = result1['routing_decision']
context1 = result1['conversation_context']

print(f'  Routing Decision: {routing1["target_agent"]}')
print(f'  Reason: {routing1["reason"]}')
print(f'  Messages in context: {len(context1.messages)}')
for i, msg in enumerate(context1.messages):
    print(f'    Msg {i}: role={msg.role}, content={msg.content[:50]}..., metadata={msg.metadata}')
print()

# Test 2: Follow-up about delivery
print('[Turn 2] User: When will it be delivered?')
result2 = router_agent.route_query(session_id, 'When will it be delivered?')
routing2 = result2['routing_decision']
context2 = result2['conversation_context']

print(f'  Routing Decision: {routing2["target_agent"]}')
print(f'  Reason: {routing2["reason"]}')
print(f'  Messages in context: {len(context2.messages)}')
for i, msg in enumerate(context2.messages):
    print(f'    Msg {i}: role={msg.role}, content={msg.content[:50]}..., metadata={msg.metadata}')
print()

# Check if current agent detection works
print('[DEBUG] Checking current agent detection:')
current_agent = router_agent._get_current_agent_from_history(context2)
print(f'  Current agent detected: {current_agent}')
print()

# Check if we're detecting "in_order_conversation"
print('[DEBUG] Checking order conversation detection:')
recent_messages = context2.get_recent_messages(10)
recent_intents = [msg.intent.value if msg.intent else None for msg in recent_messages if msg.role == "assistant"]
print(f'  Recent intents from assistant messages: {recent_intents}')
print()

if routing1['target_agent'] == routing2['target_agent'] == 'order_handler':
    print('✅ PASS: Context continuity maintained!')
else:
    print(f'❌ FAIL: Context not maintained!')
    print(f'   Turn 1: {routing1["target_agent"]}')
    print(f'   Turn 2: {routing2["target_agent"]}')
