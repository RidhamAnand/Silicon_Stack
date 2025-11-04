"""
RAG (Retrieval-Augmented Generation) Pipeline with Intent Routing
"""
from typing import List, Dict, Optional
from src.embeddings.model import embedding_model
from src.database.pinecone_client import pinecone_client
from src.utils.grok_client import grok_client
from src.classification.intent_router import intent_router
from src.config.settings import config

class RAGPipeline:
    """RAG pipeline with intent-based routing"""
    
    def __init__(self):
        self.embedding_model = embedding_model
        self.vector_db = pinecone_client
        self.llm = grok_client
        self.intent_router = intent_router
    
    def retrieve_context(
        self,
        query: str,
        top_k: int = None,
        category_filter: Optional[str] = None
    ) -> List[Dict]:
        """
        Retrieve relevant FAQs from vector database
        
        Args:
            query: User's question
            top_k: Number of results to retrieve
            category_filter: Filter by category
            
        Returns:
            List of retrieved FAQs with scores
        """
        if top_k is None:
            top_k = config.TOP_K_RESULTS
        
        # Generate query embedding
        query_embedding = self.embedding_model.embed_text(query)
        
        # Prepare filter
        filter_dict = None
        if category_filter:
            filter_dict = {"category": category_filter}
        
        # Search vector database
        results = self.vector_db.search(
            query_vector=query_embedding,
            top_k=top_k,
            filter_dict=filter_dict
        )
        
        return results
    
    def format_context(self, retrieved_docs: List[Dict]) -> str:
        """
        Format retrieved documents as context string
        
        Args:
            retrieved_docs: List of retrieved documents
            
        Returns:
            Formatted context string
        """
        if not retrieved_docs:
            return "No relevant information found."
        
        context_parts = []
        for i, doc in enumerate(retrieved_docs, 1):
            metadata = doc["metadata"]
            score = doc["score"]
            
            context_parts.append(
                f"[Source {i}] (Relevance: {score:.2f})\n"
                f"Category: {metadata.get('category', 'N/A')}\n"
                f"Q: {metadata.get('question', 'N/A')}\n"
                f"A: {metadata.get('answer', 'N/A')}\n"
            )
        
        return "\n".join(context_parts)
    
    def generate_response(
        self,
        query: str,
        context: str,
        include_sources: bool = True,
        retrieved_docs: List[Dict] = None
    ) -> Dict:
        """
        Generate response using simple FAQ extraction
        
        Args:
            query: User's question
            context: Retrieved context
            include_sources: Whether to include source information
            retrieved_docs: Original retrieved documents for confidence scoring
            
        Returns:
            Dict with response and confidence info
        """
        # Check confidence threshold (0.5 or higher is considered a good match)
        confidence_threshold = 0.5
        has_low_confidence = True
        top_score = 0.0
        
        if retrieved_docs and len(retrieved_docs) > 0:
            top_score = retrieved_docs[0].get("score", 0.0)
            has_low_confidence = top_score < confidence_threshold
        
        # For simple FAQ mode, just extract and return the answer directly
        if context and context.strip() and context != "No relevant information found.":
            # Try to extract the answer from the context
            lines = context.split('\n')
            answers = []
            scores = []
            
            for line in lines:
                line = line.strip()
                if line.startswith('A: '):
                    answer = line.replace('A: ', '').strip()
                    if answer:
                        answers.append(answer)
                elif line.startswith('Answer:'):
                    answer = line.replace('Answer:', '').strip()
                    if answer:
                        answers.append(answer)
            
            if answers:
                # Check if match confidence is too low
                if has_low_confidence:
                    return {
                        "response": f"I don't have a clear answer to that question in our FAQ database. Would you like to raise a support ticket? I can help you create one and track it for you.",
                        "confidence": top_score,
                        "has_match": False,
                        "should_create_ticket": True
                    }
                
                # Return the first answer found
                response = answers[0]
                if len(answers) > 1:
                    response += f"\n\n(Found {len(answers)} related answers)"
                return {
                    "response": response,
                    "confidence": top_score,
                    "has_match": True,
                    "should_create_ticket": False
                }
        
        # No context found - suggest ticket
        return {
            "response": "I don't have information about that in our FAQ database. Would you like me to create a support ticket so our team can help you?",
            "confidence": 0.0,
            "has_match": False,
            "should_create_ticket": True
        }
    
    def query(
        self,
        user_query: str,
        top_k: int = None,
        category_filter: Optional[str] = None,
        include_sources: bool = False,
        conversation_context: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Complete RAG pipeline with intent routing
        
        Args:
            user_query: User's question
            top_k: Number of documents to retrieve
            category_filter: Filter by category
            include_sources: Include source documents in response
            
        Returns:
            Dict with response and metadata
        """
        # Use intent router for intelligent routing
        routing_result = self.intent_router.process_query(user_query, conversation_context)
        
        # Extract response and metadata
        response = routing_result["response"]
        intent = routing_result["intent"]
        intent_confidence = routing_result["intent_confidence"]
        entities = routing_result["entities"]
        needs_escalation = routing_result["needs_escalation"]
        routing_path = routing_result["routing_path"]
        
        result = {
            "query": user_query,
            "response": response,
            "intent": intent,
            "intent_confidence": intent_confidence,
            "entities": entities,
            "needs_escalation": needs_escalation,
            "routing_path": routing_path,
            "num_sources": 0,  # Will be updated if FAQ search is used
            "top_score": 0.0,
            "should_create_ticket": False  # Will be set if no FAQ match
        }
        
        # If this was routed to FAQ, also include search results
        if intent == "faq":
            faq_result = self._search_faqs(user_query, top_k, category_filter)
            result["num_sources"] = faq_result["num_sources"]
            result["top_score"] = faq_result["top_score"]
            result["response"] = faq_result["response"]
            result["should_create_ticket"] = faq_result.get("should_create_ticket", False)
            if "sources" in faq_result:
                result["sources"] = faq_result["sources"]
        
        return result

    def _search_faqs(
        self,
        user_query: str,
        top_k: int = None,
        category_filter: Optional[str] = None
    ) -> Dict:
        """
        Search FAQs using the original RAG approach
        
        Args:
            user_query: User's question
            top_k: Number of documents to retrieve
            category_filter: Filter by category
            
        Returns:
            Dict with search results
        """
        # Retrieve relevant context
        retrieved_docs = self.retrieve_context(
            query=user_query,
            top_k=top_k,
            category_filter=category_filter
        )
        
        # Format context
        context = self.format_context(retrieved_docs)
        
        # Generate response with confidence check
        response_data = self.generate_response(
            query=user_query,
            context=context,
            include_sources=False,
            retrieved_docs=retrieved_docs
        )
        
        # Extract response based on type
        if isinstance(response_data, dict):
            response = response_data["response"]
            confidence = response_data.get("confidence", 0.0)
            should_create_ticket = response_data.get("should_create_ticket", False)
        else:
            response = response_data
            confidence = retrieved_docs[0]["score"] if retrieved_docs else 0.0
            should_create_ticket = False
        
        return {
            "response": response,
            "num_sources": len(retrieved_docs),
            "top_score": retrieved_docs[0]["score"] if retrieved_docs else 0.0,
            "sources": retrieved_docs,
            "confidence": confidence,
            "should_create_ticket": should_create_ticket
        }

# Export singleton instance
rag_pipeline = RAGPipeline()
