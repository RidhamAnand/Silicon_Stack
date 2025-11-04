"""
LLM-Enhanced Intent Classifier using Groq Cloud API
Combines rule-based NLP with Groq reasoning for better accuracy
"""
import os
from typing import Tuple
import json
import requests

from src.classification.intent_classifier import Intent

class LLMIntentClassifier:
    """
    LLM-enhanced intent classifier using Groq Cloud API directly
    Falls back to rule-based classification if Groq fails
    """

    def __init__(self, use_llm: bool = True):
        self.use_llm = use_llm
        self.api_key = os.getenv("GROQ_API_KEY")
        self.api_endpoint = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama-3.1-8b-instant"
        
        # Import rule-based classifier as fallback
        from src.classification.intent_classifier import intent_classifier as rule_based_classifier
        self.rule_based_classifier = rule_based_classifier

    def classify_intent_with_groq(self, user_query: str) -> Tuple[Intent, float]:
        """Use Groq Cloud API directly to classify intent"""
        try:
            intent_descriptions = {
                "faq": "General questions about policies, how-to, information",
                "order_inquiry": "Questions about order details, order history",
                "order_status": "Checking status, tracking, delivery time",
                "order_return": "Requests to return or send back items",
                "order_refund": "Requests for refunds",
                "complaint": "Complaints about product or service",
                "account_issue": "Account management, password reset",
                "product_info": "Product features, specifications, warranty",
                "billing_payment": "Payment methods, billing issues",
                "shipping_delivery": "Shipping options, delivery rates",
                "general_chat": "General conversation, greetings",
                "escalation_request": "Manager request, urgent matters"
            }
            
            intent_list = ", ".join([f"'{k}': {v}" for k, v in intent_descriptions.items()])
            
            prompt = f"""Analyze this customer support query and determine the primary intent.

Query: "{user_query}"

Available intents: {intent_list}

Respond ONLY in JSON format (no other text):
{{"intent": "intent_name", "confidence": 0.95, "reasoning": "why"}}

Choose the MOST specific intent that matches the query."""

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": 200
            }
            
            print(f"[Groq] Classifying: '{user_query[:40]}...'")
            
            response = requests.post(
                self.api_endpoint,
                headers=headers,
                json=payload,
                timeout=15
            )
            
            if response.status_code != 200:
                print(f"[Groq] API Error {response.status_code}")
                return self.rule_based_classifier.classify_intent(user_query)
            
            response_data = response.json()
            response_text = response_data['choices'][0]['message']['content']
            
            # Extract JSON
            try:
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = response_text[json_start:json_end]
                    result = json.loads(json_str)
                    
                    intent_name = result.get("intent", "faq").lower()
                    confidence = float(result.get("confidence", 0.5))
                    
                    # Convert to Intent enum
                    try:
                        intent = Intent[intent_name.upper().replace("-", "_")]
                        print(f"[Groq] {intent_name} ({confidence:.2f})")
                        return intent, confidence
                    except KeyError:
                        print(f"[Groq] Unknown intent: {intent_name}, using fallback")
                        return self.rule_based_classifier.classify_intent(user_query)
            except (json.JSONDecodeError, KeyError):
                print(f"[Groq] Parse error, using fallback")
                return self.rule_based_classifier.classify_intent(user_query)
                
        except Exception as e:
            print(f"[Groq] Error: {str(e)[:50]}")
            return self.rule_based_classifier.classify_intent(user_query)

    def classify_intent(self, user_query: str) -> Tuple[Intent, float]:
        """Classify intent using Groq if enabled, otherwise use rule-based"""
        if self.use_llm and self.api_key:
            return self.classify_intent_with_groq(user_query)
        else:
            return self.rule_based_classifier.classify_intent(user_query)


# Global instance
llm_intent_classifier = LLMIntentClassifier(use_llm=True)
