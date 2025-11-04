"""
Conversation context management for maintaining chat history and state
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

class ConversationState(Enum):
    """Current state of the conversation"""
    STARTING = "starting"
    ORDER_INQUIRY = "order_inquiry"
    ORDER_STATUS = "order_status"
    ORDER_RETURN = "order_return"
    COMPLAINT = "complaint"
    ACCOUNT_ISSUE = "account_issue"
    GENERAL = "general"
    ESCALATION = "escalation"

@dataclass
class ConversationMessage:
    """Represents a single message in the conversation"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    intent: Optional[str] = None
    confidence: Optional[float] = None
    entities: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ConversationContext:
    """Manages conversation state and history"""
    session_id: str
    messages: List[ConversationMessage] = field(default_factory=list)
    current_state: ConversationState = ConversationState.STARTING
    user_info: Dict[str, Any] = field(default_factory=dict)
    context_variables: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    
    # NEW: Agent state management for conversational flow
    current_agent: Optional[str] = None  # Track which agent is actively handling conversation
    agent_state: Dict[str, Any] = field(default_factory=dict)  # Store agent-specific state
    pending_action: Optional[str] = None  # e.g., "waiting_for_email", "waiting_for_order_number"
    collected_details: Dict[str, Any] = field(default_factory=dict)  # Store collected information

    def add_message(self, message: ConversationMessage):
        """Add a message to the conversation history"""
        self.messages.append(message)
        self.last_activity = datetime.utcnow()

        # Update conversation state based on the message
        if message.role == "user":
            self._update_state_from_user_message(message)
        elif message.role == "assistant":
            self._update_state_from_assistant_message(message)

    def _update_state_from_user_message(self, message: ConversationMessage):
        """Update conversation state based on user message"""
        intent = message.intent

        if intent in ["order_inquiry", "order_status", "order_return", "order_refund"]:
            self.current_state = ConversationState.ORDER_INQUIRY
        elif intent == "complaint":
            self.current_state = ConversationState.COMPLAINT
        elif intent == "account_issue":
            self.current_state = ConversationState.ACCOUNT_ISSUE
        elif intent == "escalation_request":
            self.current_state = ConversationState.ESCALATION
        else:
            self.current_state = ConversationState.GENERAL

    def _update_state_from_assistant_message(self, message: ConversationMessage):
        """Update context based on assistant response"""
        # Store any important information from assistant responses
        pass

    def get_recent_messages(self, limit: int = 10) -> List[ConversationMessage]:
        """Get the most recent messages"""
        return self.messages[-limit:] if len(self.messages) > limit else self.messages

    def get_conversation_summary(self) -> str:
        """Generate a summary of the conversation for context"""
        if not self.messages:
            return "New conversation started."

        summary_parts = []
        user_messages = [msg for msg in self.messages if msg.role == "user"]

        if user_messages:
            summary_parts.append(f"Conversation with {len(user_messages)} user messages.")

            # Add key topics discussed
            intents = [msg.intent for msg in user_messages if msg.intent]
            if intents:
                unique_intents = list(set(intents))
                summary_parts.append(f"Topics discussed: {', '.join(unique_intents)}")

        return " ".join(summary_parts)

    def should_ask_followup(self) -> bool:
        """Determine if we should ask a follow-up question"""
        if len(self.messages) < 2:
            return False

        last_user_msg = None
        last_assistant_msg = None

        # Find the last user and assistant messages
        for msg in reversed(self.messages):
            if msg.role == "user" and last_user_msg is None:
                last_user_msg = msg
            elif msg.role == "assistant" and last_assistant_msg is None:
                last_assistant_msg = msg

            if last_user_msg and last_assistant_msg:
                break

        if not last_user_msg or not last_assistant_msg:
            return False

        # Ask follow-up based on conversation state and content
        state = self.current_state

        if state == ConversationState.ORDER_INQUIRY:
            # If user asked about an order but no order number was found, ask for it
            order_entities = [e for e in last_user_msg.entities if e.get('type') == 'order_number']
            if not order_entities:
                return True

        elif state == ConversationState.ORDER_RETURN:
            # If user wants to return but we need more info
            return True

        elif state == ConversationState.COMPLAINT:
            # Complaints often need follow-up
            return True

        # Ask follow-up if the assistant's response was short or unclear
        if len(last_assistant_msg.content.split()) < 20:
            return True

        return False

    def generate_followup_question(self) -> Optional[str]:
        """Generate an appropriate follow-up question based on context"""
        state = self.current_state

        if state == ConversationState.ORDER_INQUIRY:
            # Check what specific order intent this was
            last_order_intent = None
            for msg in reversed(self.messages):
                if msg.role == "user" and msg.intent:
                    if msg.intent in ["order_inquiry", "order_status", "order_return", "order_refund"]:
                        last_order_intent = msg.intent
                        break
            
            # Check if we have order entities anywhere in conversation
            order_entities = []
            for msg in self.messages:
                if msg.role == "user":
                    order_entities.extend([e for e in msg.entities if e.get('type') == 'order_number'])

            if not order_entities:
                if last_order_intent == "order_return":
                    return "Could you please provide your order number so I can help you start the return process?"
                else:
                    return "Could you please provide your order number so I can look up the details for you?"
            elif last_order_intent == "order_status":
                return "Would you like me to check the tracking information for your order?"
            elif last_order_intent == "order_return":
                return "To help you start the return process, could you tell me why you're returning the item?"

        elif state == ConversationState.COMPLAINT:
            return "I'm sorry to hear you're experiencing issues. Could you provide more details about what happened?"

        elif state == ConversationState.ACCOUNT_ISSUE:
            return "To better assist with your account issue, could you tell me what specific problem you're experiencing?"

        return None

    def store_context_variable(self, key: str, value: Any):
        """Store a context variable for the conversation"""
        self.context_variables[key] = value

    def get_context_variable(self, key: str, default: Any = None) -> Any:
        """Retrieve a context variable"""
        return self.context_variables.get(key, default)
    
    # NEW: Agent state management methods
    def set_active_agent(self, agent_name: str):
        """Set the currently active agent handling the conversation"""
        self.current_agent = agent_name
    
    def clear_active_agent(self):
        """Clear the active agent (conversation ended or agent switch)"""
        self.current_agent = None
        self.agent_state = {}
        self.pending_action = None
    
    def update_agent_state(self, key: str, value: Any):
        """Update agent-specific state"""
        self.agent_state[key] = value
    
    def get_agent_state(self, key: str, default: Any = None) -> Any:
        """Get agent-specific state"""
        return self.agent_state.get(key, default)
    
    def set_pending_action(self, action: str):
        """Set a pending action (e.g., waiting for user input)"""
        self.pending_action = action
    
    def clear_pending_action(self):
        """Clear pending action"""
        self.pending_action = None
    
    def collect_detail(self, key: str, value: Any):
        """Store a collected detail (email, order number, etc.)"""
        self.collected_details[key] = value
    
    def get_collected_detail(self, key: str, default: Any = None) -> Any:
        """Get a collected detail"""
        return self.collected_details.get(key, default)
    
    def has_all_details(self, required_keys: List[str]) -> bool:
        """Check if all required details have been collected"""
        return all(key in self.collected_details for key in required_keys)

class ConversationManager:
    """Manages multiple conversations"""

    def __init__(self):
        self.conversations: Dict[str, ConversationContext] = {}
        self.active_session: Optional[str] = None

    def create_conversation(self, session_id: Optional[str] = None) -> ConversationContext:
        """Create a new conversation"""
        if session_id is None:
            session_id = f"session_{datetime.utcnow().timestamp()}"

        conversation = ConversationContext(session_id=session_id)
        self.conversations[session_id] = conversation
        self.active_session = session_id

        return conversation

    def get_conversation(self, session_id: str) -> Optional[ConversationContext]:
        """Get an existing conversation"""
        return self.conversations.get(session_id)

    def get_active_conversation(self) -> Optional[ConversationContext]:
        """Get the currently active conversation"""
        if self.active_session:
            return self.conversations.get(self.active_session)
        return None

    def end_conversation(self, session_id: str):
        """End a conversation"""
        if session_id in self.conversations:
            del self.conversations[session_id]

        if self.active_session == session_id:
            self.active_session = None

# Global conversation manager instance
conversation_manager = ConversationManager()