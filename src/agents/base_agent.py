"""
Base agent class and specialized agents for customer service
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from src.utils.conversation_context import ConversationContext

class BaseAgent(ABC):
    """Base class for all customer service agents"""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def can_handle(self, context: ConversationContext) -> bool:
        """Check if this agent can handle the conversation"""
        pass

    @abstractmethod
    def process_message(self, context: ConversationContext, user_message: str) -> str:
        """Process a user message and return response"""
        pass

class FAQAgent(BaseAgent):
    """Agent for handling FAQ queries using knowledge base"""

    def __init__(self):
        super().__init__("faq_agent")

    def can_handle(self, context: ConversationContext) -> bool:
        """Check if this is a FAQ-type query"""
        if not context.messages:
            return False

        last_message = context.messages[-1]
        faq_intents = ['faq', 'billing_payment', 'shipping_delivery', 'product_info', 'general_chat']

        return last_message.intent in faq_intents

    def process_message(self, context: ConversationContext, user_message: str) -> str:
        """Process FAQ query using RAG pipeline"""
        from src.rag.pipeline import rag_pipeline

        # Determine category from intent
        last_message = context.messages[-1]
        intent = last_message.intent

        category_map = {
            'billing_payment': 'billing',
            'shipping_delivery': 'shipping',
            'product_info': 'products'
        }

        category = category_map.get(intent)

        result = rag_pipeline._search_faqs(
            user_query=user_message,
            category_filter=category
        )

        return result["response"]

class OrderQueryAgent(BaseAgent):
    """Agent for handling order-related queries"""

    def __init__(self):
        super().__init__("order_query_agent")

    def can_handle(self, context: ConversationContext) -> bool:
        """Check if this is an order-related query"""
        if not context.messages:
            return False

        last_message = context.messages[-1]
        order_intents = ['order_inquiry', 'order_status', 'order_tracking']

        return last_message.intent in order_intents

    def process_message(self, context: ConversationContext, user_message: str) -> str:
        """Process order query using database service"""
        from src.database import db_service
        from src.classification.intent_router import intent_router

        # Extract order number from message or context
        order_number = self._extract_order_number(context, user_message)

        if not order_number:
            return "I need your order number to help with your order inquiry. Please provide it in the format ORD-XXXX."

        last_message = context.messages[-1]
        intent_type = last_message.intent

        # Use the intent router's order response generation
        return intent_router._generate_order_response_from_db(order_number, intent_type)

    def _extract_order_number(self, context: ConversationContext, user_message: str) -> Optional[str]:
        """Extract order number from message or conversation context"""
        from src.classification.entity_extractor import entity_extractor

        # First try current message
        entities = entity_extractor.extract_entities(user_message)
        order_entities = [e for e in entities if e.type == "order_number"]

        if order_entities:
            return order_entities[0].value

        # Then check conversation history
        for message in reversed(context.messages):
            if message.entities:
                for entity in message.entities:
                    if entity.get("type") == "order_number":
                        return entity["value"]

        return None

class EscalationAgent(BaseAgent):
    """Agent for handling escalations and ticket generation"""

    def __init__(self):
        super().__init__("escalation_agent")

    def can_handle(self, context: ConversationContext) -> bool:
        """Check if this requires escalation"""
        if not context.messages:
            return False

        last_message = context.messages[-1]
        escalation_intents = ['escalation_request', 'complaint']
        urgent_keywords = ["urgent", "emergency", "immediately", "asap", "angry", "frustrated", "manager", "supervisor"]

        message_text = last_message.content.lower()

        return (last_message.intent in escalation_intents or
                any(keyword in message_text for keyword in urgent_keywords))

    def process_message(self, context: ConversationContext, user_message: str) -> str:
        """Process escalation request and generate ticket"""
        ticket_id = self._generate_ticket_id()

        response = f"I understand you need immediate assistance. I've created a support ticket for you (Ticket ID: {ticket_id}). "
        response += "A human representative will contact you within the next 5-10 minutes. "
        response += "In the meantime, please provide any additional details about your issue."

        # In a real system, this would create an actual ticket in a ticketing system
        self._create_ticket(context, ticket_id, user_message)

        return response

    def _generate_ticket_id(self) -> str:
        """Generate a unique ticket ID"""
        import uuid
        return f"TICKET-{str(uuid.uuid4())[:8].upper()}"

    def _create_ticket(self, context: ConversationContext, ticket_id: str, issue_description: str):
        """Create a ticket in the system (placeholder for actual implementation)"""
        # This would integrate with a ticketing system like Zendesk, Jira, etc.
        ticket_data = {
            "ticket_id": ticket_id,
            "session_id": context.session_id,
            "customer_issue": issue_description,
            "conversation_history": [msg.content for msg in context.messages[-5:]],  # Last 5 messages
            "priority": "high" if self._is_urgent(issue_description) else "normal",
            "created_at": "2025-11-04T12:00:00Z"  # Would use actual timestamp
        }

        # Placeholder - in real implementation, save to database or send to ticketing system
        print(f"Created ticket: {ticket_data}")

    def _is_urgent(self, message: str) -> bool:
        """Check if the issue seems urgent"""
        urgent_keywords = ["urgent", "emergency", "immediately", "asap", "angry", "frustrated"]
        return any(keyword in message.lower() for keyword in urgent_keywords)

# Global agent instances
faq_agent = FAQAgent()
order_query_agent = OrderQueryAgent()
escalation_agent = EscalationAgent()

# List of all available agents for routing
available_agents = [faq_agent, order_query_agent, escalation_agent]