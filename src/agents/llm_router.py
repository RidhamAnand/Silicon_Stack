"""
LLM-Enhanced Router using Groq Cloud API
Uses Groq for intelligent routing decisions with conversation context
"""
import os
import json
import requests
from typing import Optional, Dict, List, Any

class LLMRouter:
    """
    LLM-enhanced router using Groq Cloud API directly
    Makes intelligent routing decisions considering conversation context
    """

    def __init__(self, use_llm: bool = True):
        self.use_llm = use_llm
        self.api_key = os.getenv("GROQ_API_KEY")
        self.api_endpoint = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama-3.1-8b-instant"
        
        # Import rule-based router as fallback
        from src.agents.router_agent import router_agent as rule_based_router
        self.rule_based_router = rule_based_router

    def route_query_with_groq(
        self,
        user_query: str,
        detected_intent: Optional[str] = None,
        extracted_entities: Optional[List[Dict]] = None,
        conversation_history: Optional[List[Dict]] = None,
        current_agent: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Use Groq Cloud API to make routing decision"""
        try:
            # Build conversation context
            history_text = ""
            if conversation_history:
                recent = conversation_history[-3:]  # Last 3 messages
                history_text = "\nRecent conversation:\n"
                for msg in recent:
                    role = msg.get("role", "user").upper()
                    content = msg.get("content", "")[:100]
                    history_text += f"- {role}: {content}\n"
            
            # Build entities text
            entities_text = ""
            if extracted_entities:
                entities_text = "Extracted entities: "
                entities_text += ", ".join([f"{e.get('type')}: {e.get('value')}" for e in extracted_entities])
                entities_text += "\n"
            
            agents_info = """Available agents:
- faq_agent: Handles general questions, FAQs, policies
- order_handler: Handles order status, tracking, inquiries
- escalation_agent: Handles urgent issues, complaints, escalations"""
            
            prompt = f"""You are a customer support router. Make an intelligent routing decision.

User Query: "{user_query}"
Detected Intent: {detected_intent or "unknown"}
{entities_text}{history_text}
Current Agent (if any): {current_agent or "none"}

{agents_info}

Respond ONLY in JSON format (no other text):
{{"target_agent": "agent_name", "confidence": 0.95, "reasoning": "brief reason"}}

Choose the MOST appropriate agent."""

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
            
            print(f"[Groq Router] Routing: '{user_query[:40]}...'")
            
            response = requests.post(
                self.api_endpoint,
                headers=headers,
                json=payload,
                timeout=15
            )
            
            if response.status_code != 200:
                print(f"[Groq Router] API Error {response.status_code}")
                return None
            
            response_data = response.json()
            response_text = response_data['choices'][0]['message']['content']
            
            # Extract JSON
            try:
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = response_text[json_start:json_end]
                    result = json.loads(json_str)
                    result["method"] = "groq"
                    print(f"[Groq Router] -> {result['target_agent']} ({result['confidence']:.2f})")
                    return result
            except (json.JSONDecodeError, KeyError):
                print(f"[Groq Router] Parse error")
                return None
                
        except Exception as e:
            print(f"[Groq Router] Error: {str(e)[:50]}")
            return None

    def route_query(
        self,
        user_query: str,
        detected_intent: Optional[str] = None,
        extracted_entities: Optional[List[Dict]] = None,
        conversation_history: Optional[List[Dict]] = None,
        current_agent: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Route query using Groq if enabled"""
        if self.use_llm and self.api_key:
            return self.route_query_with_groq(
                user_query,
                detected_intent,
                extracted_entities,
                conversation_history,
                current_agent
            )
        return None


# Global instance
llm_router = LLMRouter(use_llm=True)
