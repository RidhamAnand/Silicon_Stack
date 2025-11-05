"""
Specialized conversation agents for handling specific customer service scenarios
"""
from typing import Dict, List, Any, Optional
from enum import Enum
from src.utils.conversation_context import ConversationContext, ConversationState
from src.database import db_service

class ReturnState(Enum):
    """States in the return process"""
    INITIATED = "initiated"
    ORDER_PROVIDED = "order_provided"
    REASON_PROVIDED = "reason_provided"
    PROCESSING = "processing"
    COMPLETED = "completed"

class OrderReturnAgent:
    """Specialized agent for handling order return conversations"""

    def __init__(self):
        self.return_states = {}  # session_id -> ReturnState

    def can_handle(self, context: ConversationContext) -> bool:
        """Check if this agent should handle the conversation"""
        return context.current_state == ConversationState.ORDER_INQUIRY and \
               self._is_return_intent(context)

    def _is_return_intent(self, context: ConversationContext) -> bool:
        """Check if the conversation is about returns"""
        for message in context.messages:
            if message.intent in ['order_return', 'return'] or \
               ('return' in message.content.lower() and 'order' in message.content.lower()):
                return True
        return False

    def process_message(self, context: ConversationContext, user_message: str) -> str:
        """Process a user message in the return conversation"""

        session_id = context.session_id
        current_state = self.return_states.get(session_id, ReturnState.INITIATED)

        # Extract order numbers from the message
        order_numbers = self._extract_order_numbers(user_message)

        if current_state == ReturnState.INITIATED:
            # User just initiated return - ask for order number
            if order_numbers:
                # User provided order number immediately
                self.return_states[session_id] = ReturnState.ORDER_PROVIDED
                return self._handle_order_provided(order_numbers[0])
            else:
                # Ask for order number
                return "I'd be happy to help you with your return. Could you please provide your order number?"

        elif current_state == ReturnState.ORDER_PROVIDED:
            # We have order number, now ask for reason
            if self._is_reason_provided(user_message):
                self.return_states[session_id] = ReturnState.REASON_PROVIDED
                return self._handle_reason_provided(user_message, self.return_states[session_id + "_order"])
            else:
                # Ask for reason
                return "Thank you for providing your order number. To process your return, could you please tell me why you're returning the item?"

        elif current_state == ReturnState.REASON_PROVIDED:
            # Process the return
            order_num = self.return_states.get(session_id + "_order")
            return self._process_return(order_num, user_message)

        # Default response
        return "I'm here to help with your return. Could you provide more details?"

    def _extract_order_numbers(self, message: str) -> List[str]:
        """Extract order numbers from message"""
        import re
        # Patterns for ORD- prefixed order numbers
        patterns = [
            r'\bORD[\-\s]?(\d{4,8})\b',  # ORD-1234 or ORD1234
            r'\bORD[\-\s]?(\d{4})[\-\s]?(\d{3,4})\b',  # ORD-2024-001
            r'#\s*ORD[\-\s]?(\d{4,8})\b',  # #ORD-1234
            r'order\s+#?\s*ORD[\-\s]?(\d{4,8})\b',  # order ORD-1234
            r'(\d{8,12})'  # Fallback for numeric orders
        ]

        order_numbers = []
        for pattern in patterns:
            matches = re.findall(pattern, message.upper())
            for match in matches:
                if isinstance(match, tuple):
                    # Handle patterns with multiple groups
                    order_num = ''.join(match)
                else:
                    order_num = match
                
                # Ensure ORD- prefix
                if not order_num.startswith('ORD'):
                    order_num = f"ORD-{order_num}"
                
                order_numbers.append(order_num)

        return list(set(order_numbers))  # Remove duplicates

    def _is_reason_provided(self, message: str) -> bool:
        """Check if user provided a return reason"""
        reason_keywords = [
            'damaged', 'broken', 'wrong', 'defective', 'not working',
            'size', 'color', 'fit', 'changed mind', 'received wrong',
            'quality', 'issue', 'problem'
        ]
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in reason_keywords)

    def _handle_order_provided(self, order_number: str) -> str:
        """Handle when user provides order number"""
        # Store the order number
        session_id = f"session_{hash(order_number)}"  # Simple session tracking
        self.return_states[session_id + "_order"] = order_number

        # Try to look up the order
        try:
            result = db_service.lookup_order(order_number)
            if result.found:
                order = result.order
                if order.status.value in ['delivered', 'shipped']:
                    return f"I found your order {order_number} that was {order.status.value}. To process your return, could you please tell me why you're returning the item?"
                else:
                    return f"I see your order {order_number} is currently {order.status.value}. Returns are typically available once the order has been delivered. Would you like me to help with something else regarding this order?"
            else:
                return f"I couldn't find an order with number {order_number}. Please double-check your order number or provide the email address used for the purchase."
        except:
            return f"I found your order number {order_number}. To process your return, could you please tell me why you're returning the item?"

    def _handle_reason_provided(self, reason: str, order_number: str) -> str:
        """Handle when user provides return reason"""
        return f"Thank you for providing the reason. Based on what you've told me, I'll help process your return for order {order_number}. Here's what happens next: we'll send you a prepaid return label via email within 24 hours. Once you ship the item back, we'll process your refund within 5-7 business days. Would you like me to send the return label now?"

    def _process_return(self, order_number: str, additional_info: str) -> str:
        """Process the return request"""
        return f"Your return request for order {order_number} has been initiated. You should receive a confirmation email with the return label shortly. If you have any other questions about the return process, feel free to ask!"

# Global agent instance
order_return_agent = OrderReturnAgent()