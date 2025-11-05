"""
LangGraph State Machine for Intent Routing
"""
from typing import Dict, List, Any, Optional, TypedDict
from langgraph.graph import StateGraph, END
from src.classification.intent_classifier import intent_classifier, Intent
from src.classification.entity_extractor import entity_extractor
from src.config.settings import config
import sys

class ConversationState(TypedDict):
    """State for the conversation flow"""
    query: str
    intent: Intent
    intent_confidence: float
    entities: List[Dict[str, Any]]
    context: Dict[str, Any]
    response: str
    needs_escalation: bool
    escalation_reason: Optional[str]
    routing_path: List[str]

class IntentRouter:
    """Routes queries based on intent classification using LangGraph"""

    def __init__(self):
        self.classifier = intent_classifier
        self.extractor = entity_extractor

        # Build the state graph
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph state machine"""
        workflow = StateGraph(ConversationState)

        # Add nodes
        workflow.add_node("classify_intent", self._classify_intent)
        workflow.add_node("extract_entities", self._extract_entities)
        workflow.add_node("route_faq", self._route_faq)
        workflow.add_node("route_order", self._route_order)
        workflow.add_node("route_complaint", self._route_complaint)
        workflow.add_node("route_account", self._route_account)
        workflow.add_node("route_technical", self._route_technical)
        workflow.add_node("route_escalation", self._route_escalation)
        workflow.add_node("route_general", self._route_general)
        workflow.add_node("generate_response", self._generate_response)

        # Add edges
        workflow.set_entry_point("classify_intent")

        workflow.add_edge("classify_intent", "extract_entities")

        # Conditional routing based on intent
        workflow.add_conditional_edges(
            "extract_entities",
            self._route_by_intent,
            {
                "faq": "route_faq",
                "order_inquiry": "route_order",
                "order_status": "route_order",
                "order_return": "route_order",
                "order_refund": "route_order",
                "complaint": "route_complaint",
                "account_issue": "route_account",
                "technical_support": "route_technical",
                "billing_payment": "route_faq",  # Route to FAQ for now
                "shipping_delivery": "route_faq",  # Route to FAQ for now
                "product_info": "route_faq",  # Route to FAQ for now
                "escalation_request": "route_escalation",
                "general_chat": "route_general"
            }
        )

        # All routing paths lead to response generation
        workflow.add_edge("route_faq", "generate_response")
        workflow.add_edge("route_order", "generate_response")
        workflow.add_edge("route_complaint", "generate_response")
        workflow.add_edge("route_account", "generate_response")
        workflow.add_edge("route_technical", "generate_response")
        workflow.add_edge("route_escalation", "generate_response")
        workflow.add_edge("route_general", "generate_response")

        workflow.add_edge("generate_response", END)

        return workflow.compile()

    def _classify_intent(self, state: ConversationState) -> ConversationState:
        """Classify the intent of the query"""
        intent, confidence = self.classifier.classify_intent(state["query"])

        state["intent"] = intent
        state["intent_confidence"] = confidence
        state["routing_path"] = ["classify_intent"]

        return state

    def _extract_entities(self, state: ConversationState) -> ConversationState:
        """Extract entities from the query"""
        entities = self.extractor.extract_entities(state["query"])

        # Convert entities to dict format for state
        entity_dicts = [
            {
                "type": entity.type,
                "value": entity.value,
                "confidence": entity.confidence,
                "start_pos": entity.start_pos,
                "end_pos": entity.end_pos
            }
            for entity in entities
        ]

        state["entities"] = entity_dicts
        state["routing_path"].append("extract_entities")

        return state

    def _route_by_intent(self, state: ConversationState) -> str:
        """Determine routing path based on intent"""
        intent = state["intent"]
        intent_name = intent.value

        # Map intent enum to routing node name
        routing_map = {
            Intent.FAQ.value: "faq",
            Intent.ORDER_INQUIRY.value: "order_inquiry",
            Intent.ORDER_STATUS.value: "order_status",
            Intent.ORDER_RETURN.value: "order_return",
            Intent.ORDER_REFUND.value: "order_refund",
            Intent.COMPLAINT.value: "complaint",
            Intent.ACCOUNT_ISSUE.value: "account_issue",
            Intent.TECHNICAL_SUPPORT.value: "technical_support",
            Intent.BILLING_PAYMENT.value: "billing_payment",
            Intent.SHIPPING_DELIVERY.value: "shipping_delivery",
            Intent.PRODUCT_INFO.value: "product_info",
            Intent.ESCALATION_REQUEST.value: "escalation_request",
            Intent.GENERAL_CHAT.value: "general_chat"
        }

        route = routing_map.get(intent_name, "faq")
        state["routing_path"].append(f"route_{route}")

        return route

    def _route_faq(self, state: ConversationState) -> ConversationState:
        """Handle FAQ routing"""
        state["context"] = {
            "handler": "faq",
            "action": "search_knowledge_base",
            "category": self._infer_faq_category(state["intent"])
        }
        return state

    def _route_order(self, state: ConversationState) -> ConversationState:
        """Handle order-related routing"""
        # Check if we have order entities in current query
        order_entities = [e for e in state["entities"] if e["type"] == "order_number"]

        # Also check conversation history for previous order numbers
        conversation_history = state["context"].get("conversation_history", [])
        previous_order_numbers = self._extract_previous_order_numbers(conversation_history)

        if order_entities:
            # We have an order number in current query
            state["context"] = {
                "handler": "order_lookup",
                "action": "get_order_details",
                "order_number": order_entities[0]["value"],
                "intent_type": state["intent"].value
            }
        elif previous_order_numbers:
            # Use the most recent order number from conversation
            state["context"] = {
                "handler": "order_lookup",
                "action": "get_order_details",
                "order_number": previous_order_numbers[0],  # Most recent
                "intent_type": state["intent"].value,
                "from_history": True
            }
        else:
            # No order number found, provide general help
            state["context"] = {
                "handler": "order_general",
                "action": "provide_order_help",
                "intent_type": state["intent"].value
            }
        return state

    def _route_complaint(self, state: ConversationState) -> ConversationState:
        """Handle complaint routing"""
        # Check confidence and keywords to determine if escalation needed
        query_lower = state["query"].lower()
        urgent_keywords = ["urgent", "emergency", "immediately", "asap", "angry", "frustrated"]

        needs_escalation = (
            state["intent_confidence"] > 0.8 or
            any(keyword in query_lower for keyword in urgent_keywords)
        )

        state["needs_escalation"] = needs_escalation
        state["context"] = {
            "handler": "complaint",
            "action": "log_complaint" if not needs_escalation else "escalate_complaint",
            "escalation_needed": needs_escalation
        }

        if needs_escalation:
            state["escalation_reason"] = "Customer complaint requiring immediate attention"

        return state

    def _route_account(self, state: ConversationState) -> ConversationState:
        """Handle account issue routing"""
        state["context"] = {
            "handler": "account",
            "action": "provide_account_help"
        }
        return state

    def _route_technical(self, state: ConversationState) -> ConversationState:
        """Handle technical support routing"""
        state["context"] = {
            "handler": "technical",
            "action": "provide_technical_help"
        }
        return state

    def _route_escalation(self, state: ConversationState) -> ConversationState:
        """Handle escalation requests"""
        state["needs_escalation"] = True
        state["escalation_reason"] = "Customer requested to speak with human representative"
        state["context"] = {
            "handler": "escalation",
            "action": "transfer_to_human"
        }
        return state

    def _route_general(self, state: ConversationState) -> ConversationState:
        """Handle general chat"""
        state["context"] = {
            "handler": "general",
            "action": "provide_general_help"
        }
        return state

    def _generate_response(self, state: ConversationState) -> ConversationState:
        """Generate the final response based on routing context"""
        # Import here to avoid circular import
        from src.agents.base_agent import available_agents
        from src.agents.order_queries_handler_agent import order_return_agent

        context = state["context"]
        agent_selection_details = {
            "agents_checked": [],
            "agent_selected": None,
            "selection_reason": None
        }

        # Check if specialized agents can handle this
        conversation_context = state["context"].get("conversation_history", [])
        
        # **CRITICAL**: Check if escalation agent is already active
        # If so, route directly to it WITHOUT going through other checks
        if conversation_context and len(conversation_context) > 0:
            # Create a temporary conversation context to check
            from src.utils.conversation_context import ConversationContext
            temp_context = ConversationContext(session_id="temp")
            # Populate with recent messages
            for msg_dict in conversation_context[-5:]:  # Last 5 messages
                from src.utils.conversation_context import ConversationMessage
                msg = ConversationMessage(
                    role=msg_dict.get("role", "user"),
                    content=msg_dict.get("content", ""),
                    intent=msg_dict.get("intent"),
                    entities=msg_dict.get("entities", [])
                )
                temp_context.add_message(msg)
            
            # **CRITICAL**: Restore conversation state from metadata if available
            # This preserves current_agent, pending_action, etc. across calls
            if conversation_context:
                last_msg = conversation_context[-1]
                metadata = last_msg.get("metadata", {})
                if metadata:
                    # Check if there was an active agent in the last message
                    if metadata.get("current_agent"):
                        temp_context.current_agent = metadata.get("current_agent")
                    if metadata.get("pending_action"):
                        temp_context.pending_action = metadata.get("pending_action")
                    if metadata.get("collected_details"):
                        temp_context.collected_details = metadata.get("collected_details", {})
                    if metadata.get("agent_state"):
                        temp_context.agent_state = metadata.get("agent_state", {})
            
            # **CRITICAL**: If escalation agent is active, route directly to it
            # Don't check other agents - escalation takes priority until completion
            if temp_context.current_agent == "escalation_agent":
                from src.agents.escalation_agent import escalation_agent
                response = escalation_agent.process_message(
                    conversation_context=temp_context,
                    user_query=state["query"],
                    chat_history=conversation_context
                )
                state["response"] = response
                state["routing_path"].append("escalation_agent (continued)")
                agent_selection_details["agent_selected"] = "escalation_agent"
                agent_selection_details["selection_reason"] = "Escalation agent is active - continuing conversation"
                state["agent_selection_details"] = agent_selection_details
                return state

            # Check specialized agents in priority order
            user_query = state["query"]

            # 1. Check order return agent (highest priority for return conversations)
            can_handle_return = order_return_agent.can_handle(temp_context)
            agent_selection_details["agents_checked"].append({
                "agent": "order_return_agent",
                "can_handle": can_handle_return,
                "reason": f"Return intent detected: {order_return_agent._is_return_intent(temp_context)}"
            })
            
            if can_handle_return:
                response = order_return_agent.process_message(temp_context, user_query)
                state["response"] = response
                state["routing_path"].append("order_return_agent")
                agent_selection_details["agent_selected"] = "order_return_agent"
                agent_selection_details["selection_reason"] = "Order return conversation detected"
                state["agent_selection_details"] = agent_selection_details
                return state

            # 2. Check other specialized agents
            for agent in available_agents:
                can_handle = agent.can_handle(temp_context)
                agent_selection_details["agents_checked"].append({
                    "agent": agent.name,
                    "can_handle": can_handle,
                    "reason": f"Intent match: {temp_context.messages[-1].intent if temp_context.messages else 'none'}"
                })
                
                if can_handle:
                    response = agent.process_message(temp_context, user_query)
                    state["response"] = response
                    state["routing_path"].append(f"{agent.name}")
                    agent_selection_details["agent_selected"] = agent.name
                    agent_selection_details["selection_reason"] = f"Agent {agent.name} can handle this conversation"
                    state["agent_selection_details"] = agent_selection_details
                    return state

        # Fall back to regular routing logic if no specialized agent can handle
        agent_selection_details["agent_selected"] = "general_routing"
        agent_selection_details["selection_reason"] = "No specialized agent available, using general routing"
        state["agent_selection_details"] = agent_selection_details
        
        handler = context.get("handler")

        if handler == "faq":
            # Use existing RAG pipeline
            from src.rag.pipeline import rag_pipeline
            category = context.get("category")
            result = rag_pipeline._search_faqs(
                user_query=state["query"],
                category_filter=category
            )
            response = result["response"]

        elif handler == "order_lookup":
            # Use database service for order lookup
            order_num = context.get("order_number")
            intent_type = context.get("intent_type")
            from_history = context.get("from_history", False)
            response = self._generate_order_response_from_db(order_num, intent_type, from_history)

        elif handler == "order_general":
            # General order help
            intent_type = context.get("intent_type")
            response = self._generate_general_order_response(intent_type)

        elif handler == "complaint":
            # For complaints, use escalation agent to analyze context and create ticket
            from src.agents.escalation_agent import escalation_agent
            
            # Get the actual ConversationContext object if available
            conversation_context_obj = context.get("conversation_context_obj")
            chat_history = state["context"].get("conversation_history", [])
            
            # Pass the actual object so escalation agent can modify state
            response = escalation_agent.process_message(
                conversation_context=conversation_context_obj if conversation_context_obj else chat_history,
                user_query=state["query"],
                chat_history=None  # Agent will extract from conversation_context
            )
            state["routing_path"].append("escalation_agent")
            
            # If we have the object, mark that escalation is active
            if conversation_context_obj:
                print(f"[IntentRouter] Escalation agent activated, current_agent = '{conversation_context_obj.current_agent}'")

        elif handler == "account":
            response = self._generate_account_response()

        elif handler == "technical":
            response = self._generate_technical_response()

        elif handler == "escalation":
            # For escalations, use escalation agent to analyze context and create ticket
            from src.agents.escalation_agent import escalation_agent
            
            # Get the actual ConversationContext object if available
            conversation_context_obj = context.get("conversation_context_obj")
            chat_history = state["context"].get("conversation_history", [])
            
            # Pass the actual object so escalation agent can modify state
            response = escalation_agent.process_message(
                conversation_context=conversation_context_obj if conversation_context_obj else chat_history,
                user_query=state["query"],
                chat_history=None  # Agent will extract from conversation_context
            )
            state["routing_path"].append("escalation_agent")
            
            # If we have the object, mark that escalation is active
            if conversation_context_obj:
                print(f"[IntentRouter] Escalation agent activated, current_agent = '{conversation_context_obj.current_agent}'")

        elif handler == "general":
            response = self._generate_general_response()

        else:
            response = "I'm sorry, I'm not sure how to help with that. Let me connect you with a human representative."

        state["response"] = response
        state["routing_path"].append("generate_response")
        state["agent_selection_details"] = agent_selection_details

        return state

    def _extract_previous_order_numbers(self, conversation_history: List[Dict]) -> List[str]:
        """Extract order numbers from conversation history"""
        order_numbers = []

        for message in reversed(conversation_history):  # Most recent first
            if message.get("role") == "user":
                # Look for order numbers in user messages
                # Simple pattern matching for order numbers (can be enhanced)
                text = message.get("content", "").upper()
                # Look for patterns like ORD-12345, #12345, ORDER 12345
                import re
                patterns = [
                    r'ORD-(\d+)',
                    r'#(\d+)',
                    r'ORDER\s*(\d+)',
                    r'ORDER\s*NUMBER\s*(\d+)'
                ]

                for pattern in patterns:
                    matches = re.findall(pattern, text)
                    order_numbers.extend([f"ORD-{match}" for match in matches])

                # Also check if entities were extracted in previous responses
                if "entities" in message:
                    for entity in message["entities"]:
                        if entity.get("type") == "order_number":
                            order_numbers.append(entity["value"])

        # Remove duplicates while preserving order (most recent first)
        seen = set()
        unique_orders = []
        for order in order_numbers:
            if order not in seen:
                seen.add(order)
                unique_orders.append(order)

        return unique_orders

    def _infer_faq_category(self, intent: Intent) -> Optional[str]:
        """Infer FAQ category from intent"""
        category_map = {
            Intent.BILLING_PAYMENT: "billing",
            Intent.SHIPPING_DELIVERY: "shipping",
            Intent.PRODUCT_INFO: "products"
        }
        return category_map.get(intent)

    def _generate_order_response_from_db(self, order_number: str, intent_type: str, from_history: bool = False) -> str:
        """Generate response for order lookup using database"""
        from src.database import db_service
        
        try:
            # Lookup order in database
            result = db_service.lookup_order(order_number)
            
            if not result.found:
                if from_history:
                    return result.message + ". This was the last order number I found in our conversation. Please provide the correct order number or email address."
                else:
                    return result.message + ". Please double-check your order number or provide the email address used for the purchase."
            
            order = result.order
            customer_info = result.customer_info
            
            # Add context about using previous order if applicable
            context_prefix = ""
            if from_history:
                context_prefix = f"Using your previous order {order_number}: "
            
            # Generate response based on intent type
            if intent_type == "order_inquiry":
                response = f"{context_prefix}I found your order! Here's the summary:\n\n"
                response += db_service.format_order_summary(order)
                
            elif intent_type == "order_status":
                status_desc = db_service.get_order_status_description(order)
                response = f"{context_prefix}Order Status Update:\n\n{status_desc}"
                
                if order.status.value == "shipped" and order.tracking_number:
                    response += f"\n\nYou can track your package using tracking number: {order.tracking_number}"
                    
            elif intent_type == "order_return":
                if order.status.value in ["delivered", "shipped"]:
                    response = f"{context_prefix}I can help you start a return for order {order_number}. "
                    response += f"Your order was {order.status.value} on {order.delivered_date.strftime('%B %d, %Y') if order.delivered_date else 'recently'}. "
                    response += "Since our return window is 30 days from delivery, you should still be eligible. Would you like me to guide you through the return process?"
                else:
                    response = f"{context_prefix}I see your order {order_number} is currently {order.status.value}. "
                    response += "Returns are typically available once the order has been delivered. I'll be happy to help once your order arrives!"
                    
            elif intent_type == "order_refund":
                if order.status.value == "refunded":
                    response = f"{context_prefix}Good news! Order {order_number} has already been refunded. "
                    response += "Refunds are typically processed within 5-7 business days and should appear on your original payment method."
                elif order.status.value in ["returned", "cancelled"]:
                    response = f"{context_prefix}I see order {order_number} is {order.status.value}. "
                    response += "Refunds are processed within 5-7 business days after we receive your return or process the cancellation."
                else:
                    response = f"{context_prefix}Order {order_number} is currently {order.status.value}. "
                    response += "If you need a refund, please let me know what specific issue you're experiencing and I'll help resolve it."
                    
            else:
                # General order information
                response = f"{context_prefix}Here's information about your order:\n\n"
                response += db_service.format_order_summary(order)
            
            # Add customer context if available
            if customer_info and customer_info.get("total_orders", 0) > 1:
                response += f"\n\nI see this is order #{customer_info['total_orders']} for your account. Thank you for being a valued customer!"
                
            return response
            
        except Exception as e:
            # Fallback to general response if database fails
            if from_history:
                return f"I encountered an issue looking up your previous order {order_number}. Please try again or provide the order number directly."
            else:
                return f"I encountered an issue looking up order {order_number}. Please try again or contact support with your order details."

    def _generate_general_order_response(self, intent_type: str) -> str:
        """Generate general order help response"""
        responses = {
            "order_inquiry": "To check your order details, please provide your order number. You can find it in your confirmation email.",
            "order_status": "To check your order status, please provide your order number or the email address used for the purchase.",
            "order_return": "Our return policy allows returns within 30 days. Please provide your order number to start the return process.",
            "order_refund": "Refunds are processed within 5-7 business days after we receive your return. Please provide your order number for specific details."
        }
        return responses.get(intent_type, "I can help with order-related questions. Could you provide your order number?")

    def _generate_complaint_response(self, state: ConversationState) -> str:
        """Generate complaint response"""
        if state.get("needs_escalation"):
            return "I understand you're frustrated, and I apologize for the inconvenience. Let me connect you with a human representative who can better assist you."
        else:
            return "I'm sorry to hear you're experiencing an issue. Let me help resolve this for you. Could you provide more details about what happened?"

    def _generate_account_response(self) -> str:
        """Generate account help response"""
        return "I can help with account-related issues. Common solutions include resetting your password or updating your contact information. What specific account issue are you experiencing?"

    def _generate_technical_response(self) -> str:
        """Generate technical support response"""
        return "For technical issues, please try these steps: 1) Clear your browser cache, 2) Try a different browser, 3) Check your internet connection. If the problem persists, please provide more details about what you're experiencing."

    def _generate_escalation_response(self) -> str:
        """Generate escalation response"""
        return "I understand you'd like to speak with a human representative. Let me transfer you to our customer service team. Please hold while I connect you."

    def _generate_general_response(self) -> str:
        """Generate general chat response"""
        return "Hello! I'm here to help with your customer service needs. You can ask me about orders, shipping, returns, products, or any other questions you have."

    def process_query(self, query: str, conversation_context: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Process a user query through the intent routing system

        Args:
            query: User's query
            conversation_context: Previous conversation messages for context

        Returns:
            Dictionary with response and metadata
        """
        # Normalize conversation context to a list[dict] if a ConversationContext object was provided
        normalized_history: List[Dict] = []
        conversation_context_obj = None  # Store the actual object reference
        
        try:
            if conversation_context is None:
                normalized_history = []
            elif hasattr(conversation_context, 'messages'):
                # It's a ConversationContext object; keep the reference!
                conversation_context_obj = conversation_context
                # Also convert to a simple list of dicts for backward compatibility
                normalized_history = []
                for m in conversation_context.messages:
                    normalized_history.append({
                        "role": getattr(m, 'role', 'user'),
                        "content": getattr(m, 'content', ''),
                        "intent": getattr(m, 'intent', None),
                        "entities": getattr(m, 'entities', []),
                        "metadata": getattr(m, 'metadata', {})
                    })
            elif isinstance(conversation_context, list):
                normalized_history = conversation_context
            else:
                # Unknown type; best-effort: wrap into list if it looks like a message dict
                normalized_history = conversation_context  # type: ignore
        except Exception:
            normalized_history = []

        # Initialize state
        initial_state = ConversationState(
            query=query,
            intent=Intent.FAQ,  # Default
            intent_confidence=0.0,
            entities=[],
            context={
                "conversation_history": normalized_history or [],
                "conversation_context_obj": conversation_context_obj  # Pass the actual object!
            },
            response="",
            needs_escalation=False,
            escalation_reason=None,
            routing_path=[]
        )

        # Run the graph
        final_state = self.graph.invoke(initial_state)

        return {
            "query": final_state["query"],
            "intent": final_state["intent"].value,
            "intent_confidence": final_state["intent_confidence"],
            "entities": final_state["entities"],
            "response": final_state["response"],
            "needs_escalation": final_state["needs_escalation"],
            "escalation_reason": final_state.get("escalation_reason"),
            "routing_path": final_state["routing_path"],
            "context": final_state["context"],
            "agent_selection_details": final_state.get("agent_selection_details", {})
        }

# Export singleton instance
intent_router = IntentRouter()