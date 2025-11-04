"""
Router Agent - Orchestrates conversation flow and routes to specialized agents
Maintains full conversation context and makes intelligent routing decisions
"""
from typing import Dict, List, Any, Optional
from enum import Enum
from src.utils.conversation_context import ConversationContext, ConversationMessage
from src.classification.intent_classifier import intent_classifier

class AgentType(Enum):
    """Types of agents available for routing"""
    FAQ_AGENT = "faq_agent"
    ORDER_HANDLER = "order_handler"
    ESCALATION_AGENT = "escalation_agent"
    ROUTER_AGENT = "router_agent"

class RouterAgent:
    """
    Central routing agent that:
    1. Maintains full conversation context
    2. Analyzes queries and decides which agent to route to
    3. Handles follow-up questions intelligently
    4. Escalates when needed
    5. Makes context-aware decisions
    """

    def __init__(self):
        self.name = "router_agent"
        self.intent_classifier = intent_classifier
        self.conversation_memory: Dict[str, ConversationContext] = {}
        
    def create_session(self, session_id: str) -> ConversationContext:
        """Create a new conversation session"""
        if session_id not in self.conversation_memory:
            self.conversation_memory[session_id] = ConversationContext(session_id=session_id)
        return self.conversation_memory[session_id]
    
    def get_session(self, session_id: str) -> Optional[ConversationContext]:
        """Retrieve an existing conversation session"""
        return self.conversation_memory.get(session_id)

    def route_query(self, session_id: str, user_query: str) -> Dict[str, Any]:
        """
        Main routing function that analyzes query and routes to appropriate agent
        
        Args:
            session_id: Unique conversation session ID
            user_query: User's current query
            
        Returns:
            Dictionary with routing decision and context
        """
        # Get or create session
        context = self.create_session(session_id)
        
        # Add user message to conversation memory
        user_msg = ConversationMessage(
            role="user",
            content=user_query
        )
        context.add_message(user_msg)
        
        # Analyze query for intent and entities
        intent, confidence = self.intent_classifier.classify_intent(user_query)
        user_msg.intent = intent
        user_msg.confidence = confidence
        
        # Extract entities
        from src.classification.entity_extractor import entity_extractor
        entities = entity_extractor.extract_entities(user_query)
        user_msg.entities = [
            {
                "type": e.type,
                "value": e.value,
                "confidence": e.confidence
            }
            for e in entities
        ]
        
        # Make routing decision based on:
        # 1. Current intent
        # 2. Conversation history
        # 3. Previous order numbers (context)
        # 4. Escalation flags
        routing_decision = self._make_routing_decision(
            context=context,
            user_query=user_query,
            intent=intent,
            confidence=confidence,
            entities=user_msg.entities
        )
        
        # Create assistant response message and store the agent that will handle it
        assistant_msg = ConversationMessage(
            role="assistant",
            content=f"Routing to {routing_decision['target_agent']}",
            metadata={
                "agent": routing_decision['target_agent'],
                "reason": routing_decision['reason'],
                "escalation_level": routing_decision.get('escalation_level', 'normal')
            }
        )
        context.add_message(assistant_msg)
        
        return {
            "session_id": session_id,
            "user_query": user_query,
            "routing_decision": routing_decision,
            "conversation_context": context,
            "intent": intent.value,
            "confidence": confidence,
            "entities": user_msg.entities,
            "conversation_history": [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "intent": msg.intent.value if msg.intent else None,
                    "timestamp": msg.timestamp.isoformat() if msg.timestamp else None
                }
                for msg in context.get_recent_messages(10)
            ]
        }

    def _make_routing_decision(
        self,
        context: ConversationContext,
        user_query: str,
        intent,
        confidence: float,
        entities: List[Dict]
    ) -> Dict[str, Any]:
        """
        Intelligent routing logic that considers:
        - Query intent
        - Conversation history
        - Extracted entities (order numbers, etc.)
        - Escalation need
        - **CONTEXT CONTINUITY**: Stays with same agent for follow-ups
        - **CURRENT AGENT**: If agent is actively handling conversation, continue with same agent
        
        Returns routing decision with agent selection and reasoning
        """
        intent_value = intent.value.lower()
        query_lower = user_query.lower()
        
        # **CRITICAL: Check if an agent is already actively handling this conversation**
        if context.current_agent and context.pending_action:
            # Agent is waiting for user input (email, order number, etc.)
            return {
                "target_agent": context.current_agent,
                "reason": f"Continuing with {context.current_agent} - {context.pending_action}",
                "escalation_level": "normal",
                "context": {
                    "pending_action": context.pending_action,
                    "collected_details": context.collected_details,
                    "agent_state": context.agent_state,
                    "is_continuation": True
                }
            }
        
        # Check if agent is handling a multi-step process
        if context.current_agent and not self._should_switch_agent(context, intent_value, query_lower):
            return {
                "target_agent": context.current_agent,
                "reason": f"Continuing conversation with {context.current_agent}",
                "escalation_level": "normal",
                "context": {
                    "is_continuation": True,
                    "agent_state": context.agent_state,
                    "collected_details": context.collected_details
                }
            }
        
        # Check conversation history for context
        recent_messages = context.get_recent_messages(10)
        
        # Extract order numbers from current and recent messages
        order_numbers = self._extract_order_numbers(entities)
        previous_order_numbers = self._get_previous_order_numbers(context)
        
        # **KEY: Get the current agent from conversation history**
        current_agent = self._get_current_agent_from_history(context)
        
        # Escalation keywords
        escalation_keywords = [
            "urgent", "emergency", "asap", "immediately",
            "angry", "frustrated", "complaint", "damaged",
            "broken", "defective", "help", "manager"
        ]
        needs_escalation = any(kw in query_lower for kw in escalation_keywords)
        
        # Define intents for each agent
        order_intents = [
            "order_inquiry", "order_status", "order_return",
            "order_refund", "order_tracking"
        ]
        
        faq_intents = [
            "faq", "billing_payment", "shipping_delivery",
            "product_info", "general_chat", "account_issue"
        ]
        
        # **ROUTE TO ESCALATION AGENT if escalation/complaint/negative intent**
        # The escalation agent will analyze last 10 messages and intelligently create tickets
        if intent_value in ["complaint", "escalation_request", "escalation"] or needs_escalation:
            return {
                "target_agent": AgentType.ESCALATION_AGENT.value,
                "reason": f"Escalation/complaint detected (intent: {intent_value})",
                "escalation_level": "high" if any(kw in query_lower for kw in ["damaged", "broken", "urgent", "critical"]) else "normal",
                "context": {
                    "order_number": order_numbers[0] if order_numbers else previous_order_numbers[0] if previous_order_numbers else None,
                    "is_escalation": True,
                    "reason_text": user_query
                }
            }
        
        # Route to ESCALATION AGENT if:
        # 1. High escalation keywords present
        # 2. Explicit request for human/manager
        # 3. Multiple failed attempts
        if needs_escalation or "human" in query_lower or "manager" in query_lower:
            return {
                "target_agent": AgentType.ESCALATION_AGENT.value,
                "reason": "Escalation keywords detected or human assistance requested",
                "escalation_level": "high" if "damaged" in query_lower or "broken" in query_lower else "normal",
                "context": {
                    "has_order_number": len(order_numbers) > 0,
                    "order_number": order_numbers[0] if order_numbers else previous_order_numbers[0] if previous_order_numbers else None,
                    "conversation_length": len(context.messages)
                }
            }
        
        # **CONTEXT CONTINUITY CHECK 1: If currently in ORDER HANDLER, check if follow-up is related**
        if current_agent == "order_handler":
            # First, check if this query has strong order-related keywords
            strong_order_keywords = [
                "deliver", "arrive", "ship", "tracking", "when", "where",
                "refund", "exchange", "status", "track", "order", "package"
            ]
            has_strong_order_signal = any(kw in query_lower for kw in strong_order_keywords)
            
            # Define clear FAQ intents (like product info, account issues)
            # But NOT "faq" or "general_chat" as those could be order-related too
            clear_topic_switch_intents = ["shipping_delivery", "billing_payment", "product_info", "account_issue"]
            
            # If this is a clear topic switch AND no strong order signals, break context
            if intent_value in clear_topic_switch_intents and not has_strong_order_signal:
                # This is a clear topic switch to FAQ - don't stay with order_handler
                pass  # Fall through to FAQ routing
            elif has_strong_order_signal or intent_value in order_intents or len(previous_order_numbers) > 0:
                return {
                    "target_agent": AgentType.ORDER_HANDLER.value,
                    "reason": f"Follow-up question in order conversation. Intent: {intent_value}",
                    "escalation_level": "normal",
                    "context": {
                        "has_order_number": len(order_numbers) > 0 or len(previous_order_numbers) > 0,
                        "order_number": order_numbers[0] if order_numbers else previous_order_numbers[0] if previous_order_numbers else None,
                        "is_followup": True,
                        "previous_agent": current_agent
                    }
                }
        
        # Route to ORDER HANDLER if:
        # 1. Order-related intents (status, return, refund, inquiry)
        # 2. Order number mentioned/extracted
        # 3. Previous conversation was about orders
        if intent_value in order_intents or len(order_numbers) > 0:
            return {
                "target_agent": AgentType.ORDER_HANDLER.value,
                "reason": f"Order-related query detected. Intent: {intent_value}",
                "escalation_level": "normal",
                "context": {
                    "has_order_number": len(order_numbers) > 0,
                    "order_number": order_numbers[0] if order_numbers else previous_order_numbers[0] if previous_order_numbers else None,
                    "order_intents_in_history": self._count_intent_in_history(context, order_intents),
                    "needs_context_from_previous": len(order_numbers) == 0 and len(previous_order_numbers) > 0
                }
            }
        
        # **CONTEXT CONTINUITY CHECK 2: If currently in FAQ AGENT, check if still FAQ-related**
        if current_agent == "faq_agent":
            # Check if question is still FAQ-related
            if intent_value in faq_intents and not (len(order_numbers) > 0 or needs_escalation):
                return {
                    "target_agent": AgentType.FAQ_AGENT.value,
                    "reason": f"Continuing FAQ conversation. Intent: {intent_value}",
                    "escalation_level": "normal",
                    "context": {
                        "question_category": intent_value,
                        "confidence": confidence,
                        "follow_up": True,
                        "previous_agent": current_agent
                    }
                }
        
        # Route to FAQ AGENT if:
        # 1. FAQ-type intents (general questions)
        # 2. Shipping, billing, product info questions
        # 3. No order number context
        if intent_value in faq_intents:
            return {
                "target_agent": AgentType.FAQ_AGENT.value,
                "reason": f"FAQ/General question detected. Intent: {intent_value}",
                "escalation_level": "normal",
                "context": {
                    "question_category": intent_value,
                    "confidence": confidence,
                    "follow_up": self._is_follow_up(context, intent_value)
                }
            }
        
        # Default: Route to FAQ for general handling
        return {
            "target_agent": AgentType.FAQ_AGENT.value,
            "reason": "Default routing to FAQ agent",
            "escalation_level": "normal",
            "context": {
                "intent": intent_value,
                "confidence": confidence
            }
        }

    def _get_current_agent_from_history(self, context: ConversationContext) -> str:
        """Get the current/last agent that was handling the conversation"""
        # Find the last assistant message and extract which agent sent it
        for msg in reversed(context.messages):
            if msg.role == "assistant" and msg.metadata:
                agent = msg.metadata.get("agent")
                if agent:
                    return agent
        return None

    def _extract_order_numbers(self, entities: List[Dict]) -> List[str]:
        """Extract order numbers from entities"""
        return [e["value"] for e in entities if e["type"] == "order_number"]

    def _get_previous_order_numbers(self, context: ConversationContext) -> List[str]:
        """Get order numbers from conversation history"""
        order_numbers = []
        for msg in reversed(context.messages):
            if msg.entities:
                for entity in msg.entities:
                    if entity.get("type") == "order_number":
                        order_numbers.append(entity["value"])
        return list(dict.fromkeys(order_numbers))  # Remove duplicates, preserve order

    def _is_follow_up(self, context: ConversationContext, current_intent: str) -> bool:
        """Check if this is a follow-up question based on conversation history"""
        if len(context.messages) < 2:
            return False
        
        last_assistant_msg = None
        for msg in reversed(context.messages[:-1]):  # Exclude current user message
            if msg.role == "assistant":
                last_assistant_msg = msg
                break
        
        return last_assistant_msg is not None

    def _count_intent_in_history(self, context: ConversationContext, intent_list: List[str]) -> int:
        """Count how many times intents from list appear in history"""
        count = 0
        for msg in context.messages:
            if msg.intent and msg.intent.value in intent_list:
                count += 1
        return count
    
    def _should_switch_agent(self, context: ConversationContext, new_intent: str, query_lower: str) -> bool:
        """
        Determine if we should switch from current agent to a different one
        
        Args:
            context: Conversation context
            new_intent: The newly classified intent
            query_lower: User query in lowercase
            
        Returns:
            True if agent should switch, False if should continue with current agent
        """
        current_agent = context.current_agent
        
        if not current_agent:
            return True  # No current agent, can switch freely
        
        # Explicit switch requests
        switch_keywords = ["different", "another agent", "someone else", "human", "manager", "supervisor"]
        if any(kw in query_lower for kw in switch_keywords):
            return True
        
        # Check if user is explicitly changing topic
        topic_switch_intents = ["account_issue", "billing_payment", "product_info"]
        if new_intent in topic_switch_intents and current_agent == "escalation_agent":
            # User might be switching from complaint to different topic
            # But check if it's a short response that might be answering a question
            if len(query_lower.split()) <= 5:
                return False  # Likely answering escalation agent's question
            return True
        
        # If escalation agent is active, don't switch unless explicit
        if current_agent == "escalation_agent":
            return False  # Let escalation agent handle all follow-ups
        
        # If order handler is active and query is still order-related
        if current_agent == "order_handler" and new_intent.startswith("order_"):
            return False
        
        # If FAQ agent is active and query is still FAQ-related
        if current_agent == "faq_agent" and new_intent in ["faq", "general_chat"]:
            return False
        
        # Default: switch if intent changed significantly
        return True

    def handle_response(self, session_id: str, response: str, agent_type: str) -> None:
        """
        Record agent response in conversation memory
        
        Args:
            session_id: Conversation session ID
            response: Agent's response text
            agent_type: Which agent generated the response
        """
        context = self.get_session(session_id)
        if context:
            assistant_msg = ConversationMessage(
                role="assistant",
                content=response,
                metadata={
                    "agent": agent_type,
                    "responded_at": "now"
                }
            )
            context.add_message(assistant_msg)

    def get_conversation_summary(self, session_id: str) -> Dict[str, Any]:
        """Get summary of conversation so far"""
        context = self.get_session(session_id)
        if not context:
            return {}
        
        messages = context.get_recent_messages(100)
        order_numbers = self._get_previous_order_numbers(context)
        
        return {
            "session_id": session_id,
            "message_count": len(context.messages),
            "recent_messages": [
                {
                    "role": msg.role,
                    "content": msg.content[:100] + "..." if len(msg.content) > 100 else msg.content,
                    "intent": msg.intent.value if msg.intent else None
                }
                for msg in messages[-5:]
            ],
            "order_numbers_mentioned": order_numbers,
            "topics_discussed": list(set([msg.intent.value for msg in messages if msg.intent and msg.role == "user"]))
        }

# Global router agent instance
router_agent = RouterAgent()
