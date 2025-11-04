"""
Hybrid Router combining LLM and Rule-Based Approaches
Validates Groq decisions with rule-based logic for reliability
"""
from typing import Optional, Dict, List, Any

class HybridRouter:
    """
    Combines Groq LLM routing with rule-based validation
    Uses LLM for decision making, validates with rule-based logic
    """

    def __init__(self, use_llm: bool = True, llm_confidence_threshold: float = 0.7):
        self.use_llm = use_llm
        self.llm_confidence_threshold = llm_confidence_threshold
        
        # Import both routers
        from src.agents.llm_router import llm_router
        from src.agents.router_agent import router_agent as rule_based_router
        
        self.llm_router = llm_router
        self.rule_based_router = rule_based_router

    def route_query_hybrid(
        self,
        user_query: str,
        detected_intent: Optional[str] = None,
        extracted_entities: Optional[List[Dict]] = None,
        conversation_history: Optional[List[Dict]] = None,
        current_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Route query using hybrid approach (LLM + rule-based)
        Returns guaranteed decision (never None)
        """
        
        # Get LLM decision
        llm_decision = None
        if self.use_llm:
            llm_decision = self.llm_router.route_query(
                user_query,
                detected_intent,
                extracted_entities,
                conversation_history,
                current_agent
            )
        
        # Get rule-based decision
        rule_based_agent = None
        try:
            # Try to get a simple rule-based routing decision
            if detected_intent and detected_intent in ["order_status", "order_inquiry", "order_return", "order_refund"]:
                rule_based_agent = "order_handler"
            elif "escalat" in user_query.lower() or "manager" in user_query.lower() or "angry" in user_query.lower():
                rule_based_agent = "escalation_agent"
            else:
                rule_based_agent = "faq_agent"
        except:
            rule_based_agent = "faq_agent"
        
        # Decision logic
        if llm_decision and llm_decision.get('confidence', 0) >= self.llm_confidence_threshold:
            # Trust LLM if high confidence
            decision = llm_decision
            decision["validation"] = "llm_preferred"
            
            # Cross-validate with rule-based
            if rule_based_agent and rule_based_agent == llm_decision.get('target_agent'):
                decision["validation"] = "both_agree"
        else:
            # Fall back to rule-based if LLM fails or low confidence
            decision = {
                "target_agent": rule_based_agent or "faq_agent",
                "confidence": 0.8,
                "reasoning": "Rule-based routing",
                "method": "rule_based",
                "validation": "rule_based_fallback"
            }
        
        return decision

    def route_query(
        self,
        user_query: str,
        detected_intent: Optional[str] = None,
        extracted_entities: Optional[List[Dict]] = None,
        conversation_history: Optional[List[Dict]] = None,
        current_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """Public method for hybrid routing"""
        return self.route_query_hybrid(
            user_query,
            detected_intent,
            extracted_entities,
            conversation_history,
            current_agent
        )


# Global instance
hybrid_router = HybridRouter(use_llm=True, llm_confidence_threshold=0.7)
