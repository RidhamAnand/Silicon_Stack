"""
Intent Classification System
"""
import re
from typing import Dict, List, Optional, Tuple
from enum import Enum

class Intent(Enum):
    """Supported user intents"""
    FAQ = "faq"
    ORDER_INQUIRY = "order_inquiry"
    ORDER_STATUS = "order_status"
    ORDER_RETURN = "order_return"
    ORDER_REFUND = "order_refund"
    COMPLAINT = "complaint"
    ACCOUNT_ISSUE = "account_issue"
    PRODUCT_INFO = "product_info"
    TECHNICAL_SUPPORT = "technical_support"
    BILLING_PAYMENT = "billing_payment"
    SHIPPING_DELIVERY = "shipping_delivery"
    GENERAL_CHAT = "general_chat"
    ESCALATION_REQUEST = "escalation_request"
    TICKET_REQUEST = "ticket_request"

class IntentClassifier:
    """Rule-based intent classifier for customer support queries"""

    def __init__(self):
        # Keywords and patterns for each intent
        self.intent_patterns = {
            Intent.FAQ: [
                r'\b(what|how|when|where|why|can|do|does|is|are)\b.*\?',
                r'\b(tell me|explain|help|guide|info|information)\b',
                r'\b(about|regarding|concerning)\b',
                r'\b(return policy|refund policy|shipping policy|warranty)\b',
                r'\b(policy|policies|terms|conditions)\b'
            ],
            Intent.ORDER_INQUIRY: [
                r'\b(order|purchase|buy|transaction)\b.*\b(number|#|id)\b',
                r'\b(my order|order details|order info)\b',
                r'\b(order history|past orders|previous purchases)\b',
                r'\bORD-\d+|\d+-\d+|\d{4}-\d{3}\b'  # Order number patterns
            ],
            Intent.ORDER_STATUS: [
                r'\b(order status|status.*order|where.*order|tracking|track)\b',
                r'\b(shipped|delivered|arrived|received)\b.*\b(order|package)\b',
                r'\b(when.*order|order.*arrive|delivery.*time)\b',
                r'\b(what.*status|how.*order|where.*package)\b'
            ],
            Intent.ORDER_RETURN: [
                r'\b(return|returning|send back|take back)\b.*\b(order|item|product)\b',
                r'\b(i want to|can i|how do i)\b.*\b(return|send back)\b',
                r'\b(return label|return shipping)\b'
            ],
            Intent.ORDER_REFUND: [
                r'\b(refund|money back|reimbursement)\b',
                r'\b(refund status|refund process|when.*refund)\b',
                r'\b(credit|chargeback|reversal)\b'
            ],
            Intent.COMPLAINT: [
                r'\b(angry|frustrated|disappointed|unhappy|terrible|awful|horrible)\b',
                r'\b(complaint|complain|issue|problem|trouble|wrong|mistake|error)\b',
                r'\b(not working|doesn\'t work|won\'t work)\b',
                r'\b(broken|damaged|defective|defected|faulty|bad quality)\b',
                r'\b(received wrong|wrong item|incorrect item|wrong product)\b',
                r'\b(poor|bad|unsatisfied|dissatisfied)\b',
                r'\b(waste|useless|garbage|junk)\b'
            ],
            Intent.ACCOUNT_ISSUE: [
                r'\b(account|login|password|sign in|sign up|register)\b',
                r'\b(profile|settings|preferences|personal info)\b',
                r'\b(email|phone|address|contact.*info)\b'
            ],
            Intent.PRODUCT_INFO: [
                r'\b(product|item|inventory|stock|available|in stock)\b',
                r'\b(details|specs|specifications|features|description)\b',
                r'\b(size|color|model|version|type)\b'
            ],
            Intent.TECHNICAL_SUPPORT: [
                r'\b(technical|tech|support|help|assistance)\b',
                r'\b(error|bug|glitch|crash|freeze|not working)\b',
                r'\b(website|app|application|system|platform)\b'
            ],
            Intent.BILLING_PAYMENT: [
                r'\b(payment|pay|billing|bill|charge|fee|cost|price)\b',
                r'\b(card|credit|debit|paypal|apple pay|google pay)\b',
                r'\b(invoice|receipt|statement|balance)\b'
            ],
            Intent.SHIPPING_DELIVERY: [
                r'\b(shipping|delivery|ship|deliver|courier|carrier)\b',
                r'\b(address|location|destination|international|overseas)\b',
                r'\b(package|parcel|box|mail)\b'
            ],
            Intent.ESCALATION_REQUEST: [
                r'\b(speak|talk|contact|manager|supervisor|human)\b',
                r'\b(escalate|transfer|higher|authority|representative)\b',
                r'\b(not helpful|not working|need help|urgent|emergency)\b'
            ],
            Intent.TICKET_REQUEST: [
                r'\b(create.*ticket|raise.*ticket|open.*ticket|new.*ticket)\b',
                r'\b(support.*ticket|issue.*ticket|help.*ticket)\b',
                r'\b(ticket|tickets|support request)\b.*\b(create|raise|open|new|request)\b',
                r'\b(report.*issue|file.*complaint|lodge.*complaint)\b'
            ],
            Intent.GENERAL_CHAT: [
                r'\b(hello|hi|hey|greetings|good|thanks|thank you)\b',
                r'\b(bye|goodbye|see you|farewell)\b',
                r'\b(how are you|how.*going|what.*up)\b'
            ]
        }

        # Priority order for intent matching (higher priority intents checked first)
        self.intent_priority = [
            Intent.TICKET_REQUEST,
            Intent.ESCALATION_REQUEST,
            Intent.ORDER_RETURN,  # Moved before ORDER_INQUIRY
            Intent.ORDER_REFUND,  # Moved before ORDER_INQUIRY
            Intent.ORDER_STATUS,  # Moved before ORDER_INQUIRY
            Intent.ORDER_INQUIRY, # Moved after more specific order intents
            Intent.COMPLAINT,
            Intent.ACCOUNT_ISSUE,
            Intent.TECHNICAL_SUPPORT,
            Intent.BILLING_PAYMENT,
            Intent.SHIPPING_DELIVERY,
            Intent.PRODUCT_INFO,
            Intent.FAQ,
            Intent.GENERAL_CHAT
        ]

    def classify_intent(self, query: str) -> Tuple[Intent, float]:
        """
        Classify the intent of a user query

        Args:
            query: User's query text

        Returns:
            Tuple of (intent, confidence_score)
        """
        query_lower = query.lower().strip()

        # Check for each intent in priority order
        for intent in self.intent_priority:
            patterns = self.intent_patterns.get(intent, [])
            matches = 0
            total_patterns = len(patterns)

            for pattern in patterns:
                if re.search(pattern, query_lower, re.IGNORECASE):
                    matches += 1

            if matches > 0:
                # Calculate confidence based on pattern matches
                confidence = min(matches / total_patterns, 1.0) if total_patterns > 0 else 0.5
                return intent, confidence

        # Default to FAQ if no specific intent detected
        return Intent.FAQ, 0.3

    def get_intent_description(self, intent: Intent) -> str:
        """Get human-readable description of an intent"""
        descriptions = {
            Intent.FAQ: "General FAQ question",
            Intent.ORDER_INQUIRY: "Order information inquiry",
            Intent.ORDER_STATUS: "Order status check",
            Intent.ORDER_RETURN: "Return request or information",
            Intent.ORDER_REFUND: "Refund request or status",
            Intent.COMPLAINT: "Customer complaint or issue",
            Intent.ACCOUNT_ISSUE: "Account or login problem",
            Intent.PRODUCT_INFO: "Product information request",
            Intent.TECHNICAL_SUPPORT: "Technical support needed",
            Intent.BILLING_PAYMENT: "Billing or payment issue",
            Intent.SHIPPING_DELIVERY: "Shipping or delivery question",
            Intent.GENERAL_CHAT: "General conversation",
            Intent.ESCALATION_REQUEST: "Request to speak to human"
        }
        return descriptions.get(intent, "Unknown intent")

# Export singleton instance
intent_classifier = IntentClassifier()