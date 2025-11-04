"""
LLM-Enhanced Entity Extractor using Groq Cloud API
Uses Groq for intelligent entity extraction
"""
import os
import json
import requests
from typing import List, Dict

class LLMEntityExtractor:
    """
    LLM-enhanced entity extractor using Groq Cloud API directly
    Falls back to rule-based extraction if Groq fails
    """

    def __init__(self, use_llm: bool = True):
        self.use_llm = use_llm
        self.api_key = os.getenv("GROQ_API_KEY")
        self.api_endpoint = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama-3.1-8b-instant"
        
        # Import rule-based extractor as fallback
        from src.classification.entity_extractor import entity_extractor as rule_based_extractor
        self.rule_based_extractor = rule_based_extractor

    def extract_entities_with_groq(self, user_query: str) -> List[Dict]:
        """Use Groq Cloud API to extract entities"""
        try:
            prompt = f"""Extract entities from this customer support query:

Query: "{user_query}"

Look for: order numbers (ORD-YYYY-XXX), dates, product names, contact info

Respond ONLY in JSON format (no other text):
[{{"type": "order_number", "value": "ORD-2024-001", "confidence": 0.95}}]

Include only high-confidence entities (>0.7)."""

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": 300
            }
            
            print(f"[Groq] Extracting entities from: '{user_query[:40]}...'")
            
            response = requests.post(
                self.api_endpoint,
                headers=headers,
                json=payload,
                timeout=15
            )
            
            if response.status_code != 200:
                print(f"[Groq] API Error {response.status_code}")
                return self._fallback_extraction(user_query)
            
            response_data = response.json()
            response_text = response_data['choices'][0]['message']['content']
            
            # Extract JSON array
            try:
                json_start = response_text.find('[')
                json_end = response_text.rfind(']') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = response_text[json_start:json_end]
                    entities = json.loads(json_str)
                    
                    # Filter high-confidence entities and validate order numbers
                    import re
                    high_conf = []
                    for e in entities:
                        if e.get('confidence', 0) > 0.7:
                            # Extra validation for order numbers
                            if e.get('type') == 'order_number':
                                value = e.get('value', '')
                                # Must match ORD-YYYY-XXX format
                                if re.match(r'^ORD[\-\s]?\d{4}[\-\s]?\d{3,4}$', value, re.IGNORECASE):
                                    # Verify entity actually exists in query (prevent hallucination)
                                    normalized_value = re.sub(r'[\s\-]', '', value.upper())
                                    normalized_query = re.sub(r'[\s\-]', '', user_query.upper())
                                    if normalized_value in normalized_query:
                                        high_conf.append(e)
                            else:
                                high_conf.append(e)
                    
                    print(f"[Groq] Found {len(high_conf)} validated entities")
                    return high_conf
            except (json.JSONDecodeError, KeyError):
                print(f"[Groq] Parse error, using fallback")
                return self._fallback_extraction(user_query)
                
        except Exception as e:
            print(f"[Groq] Error: {str(e)[:50]}")
            return self._fallback_extraction(user_query)

    def _fallback_extraction(self, user_query: str) -> List[Dict]:
        """Fallback to rule-based entity extraction"""
        entities = self.rule_based_extractor.extract_entities(user_query)
        
        # Validate order numbers - must match ORD-XXXX-XXXX format
        validated_entities = []
        for entity in entities:
            if entity.type == "order_number":
                # Strict validation: must be ORD-YYYY-XXX format
                import re
                if re.match(r'^ORD[\-\s]?\d{4}[\-\s]?\d{3,4}$', entity.value, re.IGNORECASE):
                    validated_entities.append({
                        "type": entity.type,
                        "value": entity.value,
                        "confidence": entity.confidence
                    })
            else:
                validated_entities.append({
                    "type": entity.type,
                    "value": entity.value,
                    "confidence": entity.confidence
                })
        
        return validated_entities

    def extract_entities(self, user_query: str) -> List[Dict]:
        """Extract entities using Groq if enabled, otherwise use rule-based"""
        if self.use_llm and self.api_key:
            return self.extract_entities_with_groq(user_query)
        else:
            return self._fallback_extraction(user_query)


# Global instance
llm_entity_extractor = LLMEntityExtractor(use_llm=True)
