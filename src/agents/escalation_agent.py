"""
Unified Escalation Agent - Handles all escalation and ticket creation flows
- Analyzes last 10 messages to understand the issue
- Uses LLM to extract details (reason, email, order number)
- Intelligently collects missing critical fields from user
- Creates high-priority support tickets
"""
from typing import Dict, List, Any, Optional, Tuple
from src.tickets.ticket_manager import ticket_manager, TicketPriority, TicketStatus
import re
import os
import json
import requests
from datetime import datetime

class EscalationAgent:
    """
    Unified agent for handling all escalation scenarios:
    1. Analyzes conversation context (last 10 messages)
    2. Uses LLM to intelligently extract details via Groq API
    3. Collects missing fields interactively
    4. Creates support tickets with full context
    """
    
    def __init__(self):
        self.name = "escalation_agent"
        self.ticket_manager = ticket_manager
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.groq_endpoint = "https://api.groq.com/openai/v1/chat/completions"
        self.groq_model = "llama-3.1-8b-instant"
        self.max_context_messages = 10
        self.email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        self.order_pattern = r'ORD[-\s]?\d{4}[-\s]?\d{3,4}'
        
        # Store pending escalation context for interactive email collection
        self.pending_escalation = None
    
    def handle_escalation(
        self,
        chat_history: List[Dict],
        user_query: Optional[str] = None,
        interactive: bool = True
    ) -> Dict[str, Any]:
        """
        Main escalation handler - processes escalation request and creates ticket
        
        Args:
            chat_history: Full conversation history
            user_query: Current query that triggered escalation
            interactive: Whether to ask user for missing details
            
        Returns:
            Dict with ticket creation result including ticket ID and status
        """
        # Step 1: Analyze last 10 messages to understand the issue
        context_analysis = self._analyze_context(chat_history, user_query)
        
        # Step 2: Use LLM to intelligently extract details from context
        extracted_details = self._extract_details_with_llm(context_analysis)
        
        # Step 3: Validate extracted details - collect missing critical fields
        verified_details = self._collect_missing_details(
            extracted_details,
            interactive=interactive
        )
        
        # Step 4: If still missing critical fields after collection attempt, return special response
        if not verified_details.get("email"):
            # Return a response asking for email - the router will show this to user
            return {
                "success": False,
                "message": "I need your email address to create a support ticket. Please provide it so I can help you further.",
                "ticket_id": None,
                "needs_email": True,
                "reason": verified_details.get("reason"),
                "order_number": verified_details.get("order_number")
            }
        
        # Step 4: Create ticket with all collected information
        return self._create_escalation_ticket(verified_details, context_analysis)
    
    def _analyze_context(
        self,
        chat_history: List[Dict],
        user_query: Optional[str]
    ) -> Dict[str, Any]:
        """
        Analyze the last 10 messages to understand issue context
        
        Args:
            chat_history: Full conversation history
            user_query: Current query
            
        Returns:
            Dict with analyzed context including messages, keywords, intent
        """
        # Get last 10 messages
        recent_messages = chat_history[-self.max_context_messages:] if chat_history else []
        
        # Reconstruct conversation flow
        full_conversation = "\n".join([
            f"{msg.get('role', 'user').upper()}: {msg.get('content', '')}"
            for msg in recent_messages
        ])
        
        # Extract key information
        escalation_keywords = self._extract_escalation_keywords(full_conversation)
        priority_level = self._determine_priority(full_conversation)
        
        # Look for patterns in the conversation
        user_messages = [msg for msg in recent_messages if msg.get('role') == 'user']
        assistant_messages = [msg for msg in recent_messages if msg.get('role') == 'assistant']
        
        return {
            "recent_messages": recent_messages,
            "full_conversation": full_conversation,
            "user_messages": user_messages,
            "assistant_messages": assistant_messages,
            "total_messages": len(recent_messages),
            "escalation_keywords": escalation_keywords,
            "priority_level": priority_level,
            "current_query": user_query,
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
    
    def _extract_escalation_keywords(self, text: str) -> List[str]:
        """Extract escalation-related keywords from text"""
        keywords = {
            "urgent": ["urgent", "asap", "immediately", "now"],
            "critical": ["critical", "emergency", "severe"],
            "frustration": ["angry", "frustrated", "upset", "disappointed"],
            "defect": ["broken", "damaged", "defective", "faulty"],
            "quality": ["poor quality", "not working", "issue", "problem"],
            "refund": ["refund", "money back", "reimbursement"],
            "replacement": ["replace", "replacement", "exchange"]
        }
        
        found_keywords = {}
        text_lower = text.lower()
        
        for category, terms in keywords.items():
            found = [term for term in terms if term in text_lower]
            if found:
                found_keywords[category] = found
        
        return found_keywords
    
    def _determine_priority(self, text: str) -> str:
        """Determine ticket priority based on content"""
        text_lower = text.lower()
        
        # URGENT priority
        urgent_terms = ["critical", "emergency", "asap", "immediately", "urgent"]
        if any(term in text_lower for term in urgent_terms):
            return "urgent"
        
        # HIGH priority
        high_terms = ["broken", "damaged", "defective", "angry", "frustrated"]
        if any(term in text_lower for term in high_terms):
            return "high"
        
        # MEDIUM priority (default)
        return "medium"
    
    def _extract_details_with_llm(
        self,
        context_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Use LLM to intelligently extract ticket details from conversation
        
        Args:
            context_analysis: Analyzed conversation context
            
        Returns:
            Dict with extracted: reason, email, order_number, priority
        """
        full_conversation = context_analysis["full_conversation"]
        
        # Create LLM prompt for detail extraction
        extraction_prompt = f"""
Analyze this customer support conversation and extract the following details:

CONVERSATION:
{full_conversation}

Please extract:
1. REASON: What is the customer's main issue/complaint? (brief summary)
2. EMAIL: Customer's email address (if mentioned)
3. ORDER_NUMBER: Order/transaction number (if mentioned)
4. ISSUE_CATEGORY: What type of issue? (product_defect, order_problem, billing_issue, etc.)

IMPORTANT:
- For email, look for patterns like: name@domain.com
- For order, look for patterns like: ORD-xxxx, order number, tracking number
- If not found, respond with "NOT_FOUND"
- For REASON, be specific about what went wrong, not just generic frustration

Format your response as:
REASON: [extracted reason]
EMAIL: [email or NOT_FOUND]
ORDER_NUMBER: [order number or NOT_FOUND]
ISSUE_CATEGORY: [category]
"""
        
        try:
            # Call Groq API for extraction
            if not self.groq_api_key:
                print("[Escalation] Groq API key not configured, using regex fallback")
                return self._extract_details_with_regex(context_analysis)
            
            headers = {
                "Authorization": f"Bearer {self.groq_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.groq_model,
                "messages": [{"role": "user", "content": extraction_prompt}],
                "temperature": 0.3,
                "max_tokens": 500
            }
            
            print("[Escalation] Extracting details using Groq LLM...")
            response = requests.post(
                self.groq_endpoint,
                headers=headers,
                json=payload,
                timeout=15
            )
            
            if response.status_code != 200:
                print(f"[Escalation] Groq API error {response.status_code}, using regex fallback")
                return self._extract_details_with_regex(context_analysis)
            
            response_data = response.json()
            llm_text = response_data['choices'][0]['message']['content']
            
            # Parse LLM response
            extracted = {
                "reason": None,
                "email": None,
                "order_number": None,
                "issue_category": None,
                "missing_fields": [],
                "llm_extraction": llm_text
            }
            
            # Parse each line
            for line in llm_text.split('\n'):
                if line.startswith('REASON:'):
                    reason = line.replace('REASON:', '').strip()
                    if reason and reason != "NOT_FOUND":
                        extracted["reason"] = reason
                elif line.startswith('EMAIL:'):
                    email = line.replace('EMAIL:', '').strip()
                    if email and email != "NOT_FOUND":
                        extracted["email"] = email
                elif line.startswith('ORDER_NUMBER:'):
                    order = line.replace('ORDER_NUMBER:', '').strip()
                    if order and order != "NOT_FOUND":
                        extracted["order_number"] = order
                elif line.startswith('ISSUE_CATEGORY:'):
                    category = line.replace('ISSUE_CATEGORY:', '').strip()
                    if category:
                        extracted["issue_category"] = category
            
            # Fallback to regex extraction if LLM didn't find these
            if not extracted["email"]:
                email_matches = re.findall(self.email_pattern, full_conversation)
                if email_matches:
                    extracted["email"] = email_matches[0]
            
            if not extracted["order_number"]:
                order_matches = re.findall(self.order_pattern, full_conversation, re.IGNORECASE)
                if order_matches:
                    extracted["order_number"] = order_matches[0]
            
            # If reason not extracted, use last user message or conversation summary
            if not extracted["reason"]:
                user_messages = context_analysis.get("user_messages", [])
                if user_messages:
                    # Use the last user message as reason
                    extracted["reason"] = user_messages[-1].get("content", "Support escalation request")
                else:
                    extracted["reason"] = "Support escalation requested"
            
            # Identify missing critical fields
            if not extracted["email"]:
                extracted["missing_fields"].append("email")
            if not extracted["reason"]:
                extracted["missing_fields"].append("reason")
            
            # Priority from context analysis
            extracted["priority"] = context_analysis.get("priority_level", "medium")
            
            return extracted
            
        except Exception as e:
            # Fallback to regex extraction if LLM fails
            print(f"[Escalation] LLM extraction failed: {e}. Using regex fallback.")
            return self._extract_details_with_regex(context_analysis)
    
    def _extract_details_with_regex(
        self,
        context_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Fallback regex-based extraction if LLM fails
        
        Args:
            context_analysis: Analyzed conversation context
            
        Returns:
            Dict with extracted details using regex patterns
        """
        full_conversation = context_analysis["full_conversation"]
        user_messages = context_analysis.get("user_messages", [])
        
        extracted = {
            "reason": None,
            "email": None,
            "order_number": None,
            "issue_category": None,
            "missing_fields": [],
            "llm_extraction": None
        }
        
        # Extract email
        email_matches = re.findall(self.email_pattern, full_conversation)
        if email_matches:
            extracted["email"] = email_matches[0]
        
        # Extract order number
        order_matches = re.findall(self.order_pattern, full_conversation, re.IGNORECASE)
        if order_matches:
            extracted["order_number"] = order_matches[0]
        
        # Extract reason from last user message
        if user_messages:
            extracted["reason"] = user_messages[-1].get("content", "Support escalation request")
        else:
            extracted["reason"] = "Support escalation requested"
        
        # Identify missing fields
        if not extracted["email"]:
            extracted["missing_fields"].append("email")
        
        extracted["priority"] = context_analysis.get("priority_level", "medium")
        
        return extracted
    
    def _collect_missing_details(
        self,
        extracted: Dict[str, Any],
        interactive: bool = True
    ) -> Dict[str, Any]:
        """
        Collect missing critical fields from user
        
        Args:
            extracted: Already extracted details
            interactive: Whether to ask user interactively
            
        Returns:
            Dict with complete verified details
        """
        verified = extracted.copy()
        missing = verified.get("missing_fields", [])
        
        if not interactive or not missing:
            return verified
        
        print("\n" + "=" * 70)
        print("📋 ESCALATION TICKET - PLEASE PROVIDE REQUIRED INFORMATION")
        print("=" * 70)
        
        # Show what we found
        if verified.get("reason"):
            print(f"\n✓ Issue Description (auto-detected):")
            print(f"  {verified['reason'][:150]}")
        
        if verified.get("order_number"):
            print(f"\n✓ Order Number (auto-detected):")
            print(f"  {verified['order_number']}")
        
        print()
        
        # Collect email if missing
        if "email" in missing:
            print("📧 Email Address (required for contact):")
            email_input = input("  Enter your email: ").strip()
            if email_input:
                # Validate email format
                if re.match(self.email_pattern, email_input):
                    verified["email"] = email_input
                    missing.remove("email")
                else:
                    print(f"  ⚠️  Invalid email format. Using: {email_input}")
                    verified["email"] = email_input
                    missing.remove("email")
            else:
                print("  ⚠️  Email is required to create a ticket!")
        
        # Collect reason if missing
        if "reason" in missing:
            print("\n📝 Issue Description (required):")
            reason_input = input("  Describe your issue: ").strip()
            if reason_input:
                verified["reason"] = reason_input
                missing.remove("reason")
        
        # Optional: order number if not found
        if verified.get("order_number") is None:
            print("\n📦 Order Number (optional):")
            order_input = input("  Enter your order number (or press Enter to skip): ").strip()
            if order_input:
                verified["order_number"] = order_input
        
        print("\n" + "=" * 70)
        
        return verified
    
    def _create_escalation_ticket(
        self,
        details: Dict[str, Any],
        context_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create support ticket with complete escalation context
        
        Args:
            details: Verified ticket details (reason, email, order_number)
            context_analysis: Analyzed conversation context
            
        Returns:
            Dict with ticket creation result
        """
        # Validate minimum required fields
        if not details.get("reason"):
            return {
                "success": False,
                "message": "Cannot create ticket without issue description",
                "ticket_id": None
            }
        
        if not details.get("email"):
            return {
                "success": False,
                "message": "Cannot create ticket without email address",
                "ticket_id": None
            }
        
        # Build comprehensive ticket description
        description = self._build_ticket_description(details, context_analysis)
        
        # Map priority to enum
        priority_map = {
            "urgent": TicketPriority.URGENT,
            "high": TicketPriority.HIGH,
            "medium": TicketPriority.MEDIUM,
            "low": TicketPriority.LOW
        }
        priority = priority_map.get(details.get("priority", "medium"), TicketPriority.MEDIUM)
        
        # Create ticket
        try:
            ticket = self.ticket_manager.create_ticket(
                title=f"🚨 ESCALATION: {details.get('reason', 'Support Needed')[:50]}",
                description=description,
                user_email=details.get("email"),
                order_number=details.get("order_number"),
                priority=priority
            )
            
            return {
                "success": True,
                "ticket_id": ticket.ticket_id,
                "title": ticket.title,
                "priority": ticket.priority.value,
                "status": ticket.status.value,
                "message": f"✅ Escalation ticket {ticket.ticket_id} created successfully!",
                "details": {
                    "reason": details.get("reason"),
                    "email": details.get("email"),
                    "order_number": details.get("order_number"),
                    "keywords": context_analysis.get("escalation_keywords", {})
                }
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to create ticket: {str(e)}",
                "ticket_id": None
            }
    
    def _build_ticket_description(
        self,
        details: Dict[str, Any],
        context_analysis: Dict[str, Any]
    ) -> str:
        """
        Build comprehensive ticket description from details and context
        
        Args:
            details: Extracted ticket details
            context_analysis: Conversation context analysis
            
        Returns:
            Formatted ticket description
        """
        description = f"""
ESCALATION TICKET - CREATED {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}

=== CUSTOMER ISSUE ===
{details.get('reason', 'N/A')}

=== CONTACT INFORMATION ===
Email: {details.get('email', 'N/A')}
Order Number: {details.get('order_number', 'N/A')}
Issue Category: {details.get('issue_category', 'N/A')}

=== PRIORITY INDICATORS ===
"""
        
        # Add escalation keywords found
        keywords = context_analysis.get("escalation_keywords", {})
        if keywords:
            for category, terms in keywords.items():
                description += f"• {category.upper()}: {', '.join(terms)}\n"
        else:
            description += "• No specific escalation keywords detected\n"
        
        # Add conversation context
        description += f"""
=== CONVERSATION CONTEXT ===
Total Messages Analyzed: {context_analysis.get('total_messages', 'N/A')}
Conversation Summary:
{context_analysis.get('full_conversation', 'N/A')}

=== SYSTEM NOTES ===
This ticket was automatically escalated from the AI support system.
The above conversation has been analyzed and priority indicators identified.
Please review the conversation context above for full details.
"""
        
        return description
    
    def process_message(
        self,
        conversation_context,
        user_query: str,
        chat_history: Optional[List[Dict]] = None
    ) -> str:
        """
        Process message and create escalation ticket - ALWAYS checks for missing details first
        
        Flow:
        1. Analyze conversation and current query
        2. Extract any available details (reason, email, order)
        3. Check what's missing
        4. If missing details: Ask for them one by one
        5. If all details present: Create ticket
        
        Args:
            conversation_context: ConversationContext object (from router_agent)
            user_query: Current user query
            chat_history: Optional chat history (will use conversation_context if not provided)
            
        Returns:
            Formatted response string - next question or ticket confirmation
        """
        # Convert conversation_context to chat_history format if needed
        if chat_history is None:
            # Extract messages from conversation_context
            chat_history = []
            if hasattr(conversation_context, 'messages'):
                # It's a ConversationContext object
                for msg in conversation_context.messages:
                    chat_history.append({
                        "role": msg.role,
                        "content": msg.content
                    })
            else:
                # It's already a dict/list
                chat_history = conversation_context if isinstance(conversation_context, list) else []
        
        # Check if we have ConversationContext with state management
        if hasattr(conversation_context, 'current_agent'):
            return self._handle_with_smart_detail_collection(conversation_context, user_query, chat_history)
        else:
            # Fallback to old behavior
            return self._handle_non_conversational(chat_history, user_query)
    
    def _handle_with_smart_detail_collection(
        self,
        context,
        user_query: str,
        chat_history: List[Dict]
    ) -> str:
        """
        Smart detail collection - ALWAYS checks what's missing and asks for it
        
        Strategy:
        1. Extract all details from conversation history + current query
        2. Check what's still missing
        3. Ask for missing details in order: reason → order → email
        4. Create ticket when all details are present
        """
        # Set this agent as active
        context.set_active_agent("escalation_agent")
        
        # Try to extract details from current query and history
        extracted_details = self._smart_extract_all_details(user_query, chat_history, context)
        
        reason = extracted_details.get("reason")
        email = extracted_details.get("email")
        order_number = extracted_details.get("order_number")
        
        # Determine what's missing and ask for it
        if not reason:
            # Need to understand the issue first
            context.set_pending_action("waiting_for_reason")
            return """I'm here to help! Could you please describe the issue you're experiencing?"""
        
        if not email:
            # Have reason, need email
            context.set_pending_action("waiting_for_email")
            
            # Acknowledge the issue
            issue_summary = reason[:100] if len(reason) > 100 else reason
            response = f"""I understand you're experiencing: "{issue_summary}"
"""
            if order_number:
                response += f"\nOrder Number: {order_number}\n"
            
            response += """\nTo create a support ticket, I'll need your email address so our team can contact you.

What's your email address?"""
            return response
        
        if not order_number:
            # Have reason and email, but no order - ask if they have one
            context.set_pending_action("waiting_for_order_optional")
            
            issue_summary = reason[:100] if len(reason) > 100 else reason
            return f"""I understand you're experiencing: "{issue_summary}"

Email: {email}

Do you have an order number related to this issue? (Format: ORD-1234-5678)

If you don't have one, just type "no order" and I'll proceed without it."""
        
        # ALL DETAILS PRESENT - Create the ticket!
        return self._create_ticket_with_details(
            context=context,
            reason=reason,
            email=email,
            order_number=order_number,
            chat_history=chat_history
        )
    
    def _smart_extract_all_details(
        self,
        user_query: str,
        chat_history: List[Dict],
        context
    ) -> Dict[str, str]:
        """
        Extract ALL available details from current query + conversation history
        
        Checks:
        1. Current query
        2. Conversation history (last 10 messages)
        3. Context collected_details (from previous extractions)
        
        Returns dict with: reason, email, order_number (or None if not found)
        """
        details = {
            "reason": None,
            "email": None,
            "order_number": None
        }
        
        # First, check if we already have details stored in context
        if hasattr(context, 'collected_details'):
            details["reason"] = context.get_collected_detail("issue") or context.get_collected_detail("reason")
            details["email"] = context.get_collected_detail("email")
            details["order_number"] = context.get_collected_detail("order_number")
        
        # Extract from current query
        # Email pattern
        email_matches = re.findall(self.email_pattern, user_query)
        if email_matches and not details["email"]:
            details["email"] = email_matches[0]
            context.collect_detail("email", email_matches[0])
        
        # Order pattern
        order_matches = re.findall(self.order_pattern, user_query, re.IGNORECASE)
        if order_matches and not details["order_number"]:
            details["order_number"] = order_matches[0]
            context.collect_detail("order_number", order_matches[0])
        
        # Reason - check if current query looks like a complaint/issue description
        complaint_keywords = ["defective", "broken", "damaged", "wrong", "issue", "problem", 
                             "complaint", "not working", "doesn't work", "poor", "bad"]
        if any(kw in user_query.lower() for kw in complaint_keywords) and not details["reason"]:
            details["reason"] = user_query
            context.collect_detail("issue", user_query)
            context.collect_detail("reason", user_query)
        
        # Extract from conversation history if still missing details
        if chat_history:
            recent_history = chat_history[-10:]  # Last 10 messages
            
            for msg in recent_history:
                msg_content = msg.get("content", "")
                
                # Look for email
                if not details["email"]:
                    email_in_history = re.findall(self.email_pattern, msg_content)
                    if email_in_history:
                        details["email"] = email_in_history[0]
                        context.collect_detail("email", email_in_history[0])
                
                # Look for order
                if not details["order_number"]:
                    order_in_history = re.findall(self.order_pattern, msg_content, re.IGNORECASE)
                    if order_in_history:
                        details["order_number"] = order_in_history[0]
                        context.collect_detail("order_number", order_in_history[0])
                
                # Look for complaint/reason
                if not details["reason"] and msg.get("role") == "user":
                    if any(kw in msg_content.lower() for kw in complaint_keywords):
                        details["reason"] = msg_content
                        context.collect_detail("issue", msg_content)
                        context.collect_detail("reason", msg_content)
        
        return details
    
    def _create_ticket_with_details(
        self,
        context,
        reason: str,
        email: str,
        order_number: Optional[str],
        chat_history: List[Dict]
    ) -> str:
        """Create ticket with all collected details"""
        # Analyze context for priority
        context_analysis = self._analyze_context(chat_history, reason)
        priority = context_analysis.get("priority_level", "medium")
        
        # Build details dict for ticket creation
        details = {
            "reason": reason,
            "email": email,
            "order_number": order_number,
            "priority": priority,
            "keywords": context_analysis.get("escalation_keywords", {}),
            "missing_fields": []
        }
        
        # Create the ticket
        result = self._create_escalation_ticket(details, context_analysis)
        
        # Clear agent state - conversation done
        context.clear_active_agent()
        context.clear_pending_action()
        
        if result["success"]:
            ticket_id = result["ticket_id"]
            priority_level = result.get("priority", "MEDIUM").upper()
            
            response = f"""✅ SUPPORT TICKET CREATED SUCCESSFULLY!

Ticket ID: {ticket_id}
Priority: {priority_level}
Email: {email}"""
            
            if order_number:
                response += f"\nOrder: {order_number}"
            
            response += f"""

Your ticket has been submitted to our support team. A representative will contact you at {email} within 24 hours.

**Please save your Ticket ID: {ticket_id}** for future reference.

Is there anything else I can help you with?"""
            
            return response
        else:
            return f"I apologize, but there was an error creating your ticket: {result.get('message')}. Let me connect you with a human representative."
    
    def _handle_conversational_flow(
        self,
        context,
        user_query: str,
        chat_history: List[Dict]
    ) -> str:
        """
        Handle escalation with conversational step-by-step flow
        
        State machine:
        1. initial_complaint -> Ask for details about issue
        2. waiting_for_issue_details -> Acknowledge, ask for order number
        3. waiting_for_order -> Acknowledge, ask for email
        4. waiting_for_email -> Create ticket with all details
        """
        # Set this agent as active
        context.set_active_agent("escalation_agent")
        
        # Get current step
        step = context.get_agent_state("step", "initial_complaint")
        
        if step == "initial_complaint":
            # First interaction - acknowledge issue and analyze
            print("[Escalation] Analyzing initial complaint...")
            context_analysis = self._analyze_context(chat_history, user_query)
            
            # Store the issue
            context.collect_detail("issue", user_query)
            context.collect_detail("priority", context_analysis.get("priority_level", "medium"))
            context.collect_detail("keywords", context_analysis.get("escalation_keywords", {}))
            
            # Try to extract order number from query
            order_matches = re.findall(self.order_pattern, user_query, re.IGNORECASE)
            if order_matches:
                context.collect_detail("order_number", order_matches[0])
                # Move to email collection
                context.update_agent_state("step", "waiting_for_email")
                context.set_pending_action("waiting_for_email")
                
                return f"""I'm sorry to hear about this issue. I've noted your concern about: "{user_query[:100]}"

Order Number: {order_matches[0]}

To create a support ticket, I'll need your email address so our team can contact you.

What's your email address?"""
            else:
                # Ask for order number
                context.update_agent_state("step", "waiting_for_order")
                context.set_pending_action("waiting_for_order_number")
                
                return f"""I'm sorry to hear about this issue. I understand you're experiencing: "{user_query[:100]}"

To help you better, could you please provide your order number? (It usually looks like ORD-1234-5678)"""
        
        elif step == "waiting_for_order":
            # User provided order number
            order_matches = re.findall(self.order_pattern, user_query, re.IGNORECASE)
            if order_matches:
                context.collect_detail("order_number", order_matches[0])
                context.update_agent_state("step", "waiting_for_email")
                context.set_pending_action("waiting_for_email")
                
                return f"""Thank you! I've noted your order number: {order_matches[0]}

Now, what's your email address so our support team can reach you?"""
            else:
                # Check if user is providing other info - maybe email?
                email_matches = re.findall(self.email_pattern, user_query)
                if email_matches:
                    # User provided email instead of order - that's ok
                    context.collect_detail("email", email_matches[0])
                    context.update_agent_state("step", "waiting_for_order")
                    return f"""Thank you for providing your email: {email_matches[0]}

Could you also provide your order number? (It usually looks like ORD-1234-5678, or leave blank if you don't have one)"""
                else:
                    # Didn't understand - ask again
                    return """I didn't catch an order number in that message. Could you please provide your order number? (Format: ORD-1234-5678)

If you don't have an order number, you can type "no order number" and we'll proceed without it."""
        
        elif step == "waiting_for_email":
            # User provided email
            email_matches = re.findall(self.email_pattern, user_query)
            if email_matches:
                context.collect_detail("email", email_matches[0])
                # We have everything - create ticket!
                return self._create_ticket_from_context(context, chat_history)
            else:
                # Didn't find email - ask again
                return """I need a valid email address to create your support ticket. Could you please provide your email? (e.g., your.name@example.com)"""
        
        else:
            # Unknown state - restart
            context.update_agent_state("step", "initial_complaint")
            return "Let me help you with that. Could you please describe your issue?"
    
    def _create_ticket_from_context(
        self,
        context,
        chat_history: List[Dict]
    ) -> str:
        """Create ticket from collected context details"""
        issue = context.get_collected_detail("issue", "Support request")
        email = context.get_collected_detail("email")
        order_number = context.get_collected_detail("order_number")
        priority = context.get_collected_detail("priority", "medium")
        keywords = context.get_collected_detail("keywords", {})
        
        # Analyze full context
        context_analysis = self._analyze_context(chat_history, issue)
        
        # Build details dict
        details = {
            "reason": issue,
            "email": email,
            "order_number": order_number,
            "priority": priority,
            "keywords": keywords,
            "missing_fields": []
        }
        
        # Create the ticket
        result = self._create_escalation_ticket(details, context_analysis)
        
        # Clear agent state - conversation done
        context.clear_active_agent()
        context.clear_pending_action()
        
        if result["success"]:
            ticket_id = result["ticket_id"]
            priority_level = result.get("priority", "MEDIUM").upper()
            
            response = f"""✅ **SUPPORT TICKET CREATED SUCCESSFULLY!**

Ticket ID: {ticket_id}
Priority: {priority_level}
Email: {email}"""
            
            if order_number:
                response += f"\nOrder: {order_number}"
            
            response += f"""

Your ticket has been submitted to our support team. A representative will contact you at {email} within 24 hours.

**Please save your Ticket ID: {ticket_id}** for future reference.

Is there anything else I can help you with?"""
            
            return response
        else:
            return f"I apologize, but there was an error creating your ticket: {result.get('message')}. Let me connect you with a human representative."
    
    def _handle_non_conversational(
        self,
        chat_history: List[Dict],
        user_query: str
    ) -> str:
        """Fallback for non-conversational context (backwards compatibility)"""
        result = self.handle_escalation(
            chat_history=chat_history,
            user_query=user_query,
            interactive=False
        )
        
        if result["success"]:
            ticket_id = result["ticket_id"]
            priority = result.get("priority", "HIGH").upper()
            
            return f"""ESCALATION - SUPPORT TICKET CREATED

Thank you for reaching out. I've escalated your issue and created a high-priority support ticket for immediate attention.

Ticket ID: {ticket_id}
Priority: {priority}
Contact: {result['details'].get('email', 'on file')}

Your ticket has been submitted to our support team. A representative will contact you shortly using the email address on file.

**You can reference your Ticket ID for future inquiries.**
"""
        elif result.get("needs_email"):
            msg = f"""I found the issue you reported:
  {result.get('reason', 'N/A')[:100]}
"""
            if result.get('order_number'):
                msg += f"  Order: {result.get('order_number')}\n"
            
            msg += "\n📧 To create a support ticket, please reply with your email address."
            return msg
        else:
            return f"Error creating escalation ticket: {result['message']}"
    
    def create_ticket_with_email(self, email: str) -> str:
        """
        Complete escalation ticket creation with provided email
        Called from main.py when user provides email after initial escalation request
        
        Args:
            email: User's email address
            
        Returns:
            Formatted response with ticket details
        """
        if not self.pending_escalation:
            return "No pending escalation found. Please describe your issue again."
        
        if not email or "@" not in email:
            return "Invalid email format. Please provide a valid email address."
        
        # Get stored context
        chat_history = self.pending_escalation.get("chat_history", [])
        user_query = self.pending_escalation.get("user_query", "")
        
        # Analyze and extract details
        context_analysis = self._analyze_context(chat_history, user_query)
        extracted_details = self._extract_details_with_llm(context_analysis)
        
        # Use the provided email
        extracted_details["email"] = email
        if "email" in extracted_details.get("missing_fields", []):
            extracted_details["missing_fields"].remove("email")
        
        # Create ticket
        result = self._create_escalation_ticket(extracted_details, context_analysis)
        
        # Clear pending escalation
        self.pending_escalation = None
        
        if result["success"]:
            ticket_id = result["ticket_id"]
            priority = result.get("priority", "HIGH").upper()
            
            return f"""ESCALATION - SUPPORT TICKET CREATED

Thank you! I've created a support ticket for your issue.

Ticket ID: {ticket_id}
Priority: {priority}
Email: {email}

Your ticket has been submitted to our support team. A representative will contact you at {email}.

**Reference your Ticket ID: {ticket_id}**
"""
        else:
            return f"Error creating ticket: {result['message']}"
    
    def can_handle(self, conversation_context) -> bool:
        """
        Check if this agent can handle the conversation
        
        Args:
            conversation_context: ConversationContext object from router
            
        Returns:
            True if this is an escalation request
        """
        if not hasattr(conversation_context, 'messages') or not conversation_context.messages:
            return False
        
        last_message = conversation_context.messages[-1]
        if last_message.role != "user":
            return False
        
        # Check for escalation indicators
        content = last_message.content.lower()
        escalation_terms = [
            "escalat", "urgent", "emergency", "asap", "manager",
            "complaint", "angry", "frustrated", "broken", "damaged",
            "critical", "help", "immediately"
        ]
        
        return any(term in content for term in escalation_terms)


# Global escalation agent instance
escalation_agent = EscalationAgent()
