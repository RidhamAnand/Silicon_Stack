"""
Simple FAQ-only client (no LLM required)
"""
from typing import List, Dict, Optional

class SimpleFAQClient:
    """Simple client that just returns FAQ answers without LLM"""

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> str:
        """
        Return a simple response based on the last user message
        """
        user_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                break

        # Simple response
        return f"Based on our FAQ database, here's what I found about: {user_message[:50]}..."

    def generate_response(
        self,
        user_query: str,
        context: Optional[str] = None,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Generate response using retrieved context only
        """
        if context and context.strip():
            # Extract the first answer from context
            lines = context.split('\n')
            for line in lines:
                if line.startswith('A: ') or 'Answer:' in line:
                    answer = line.replace('A: ', '').replace('Answer: ', '').strip()
                    return f"Here's what I found: {answer}"

            # Fallback: return first meaningful line
            for line in lines:
                if len(line.strip()) > 20 and not line.startswith('['):
                    return f"From our knowledge base: {line.strip()}"

        return "I found some information but couldn't extract a clear answer. Please try rephrasing your question."

# Export instance
grok_client = SimpleFAQClient()
