"""
Ticket Agent - Handles support ticket creation and management
"""
from typing import Dict, Any, Optional, List
from src.tickets.ticket_manager import ticket_manager, TicketPriority, TicketStatus

class TicketAgent:
    """Handles ticket creation, viewing, and management"""
    
    def __init__(self):
        self.name = "ticket_agent"
        self.ticket_manager = ticket_manager
    
    def extract_details_from_history(self, chat_history: List[Dict]) -> Dict[str, Any]:
        """
        Extract relevant details from conversation history
        
        Args:
            chat_history: List of conversation messages with role and content
            
        Returns:
            Dict with extracted: reason, email, order_number, priority
        """
        extracted = {
            "reason": None,
            "email": None,
            "order_number": None,
            "priority": "medium",
            "missing_fields": []
        }
        
        if not chat_history:
            extracted["missing_fields"] = ["reason", "email", "order_number"]
            return extracted
        
        # Combine all user messages to find reason
        user_messages = [
            msg.get("content", "") for msg in chat_history 
            if msg.get("role") == "user"
        ]
        
        if user_messages:
            # The first user message is likely the reason
            extracted["reason"] = user_messages[0]
        else:
            extracted["missing_fields"].append("reason")
        
        # Extract email - look for email pattern
        import re
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        for msg in chat_history:
            content = msg.get("content", "")
            email_match = re.search(email_pattern, content)
            if email_match:
                extracted["email"] = email_match.group(0)
                break
        
        if not extracted["email"]:
            extracted["missing_fields"].append("email")
        
        # Extract order number - look for ORD- pattern
        order_pattern = r'ORD[-\s]?\d{4}[-\s]?\d{3,4}'
        for msg in chat_history:
            content = msg.get("content", "")
            order_match = re.search(order_pattern, content, re.IGNORECASE)
            if order_match:
                extracted["order_number"] = order_match.group(0)
                break
        
        # Detect priority from chat history
        full_text = " ".join(user_messages).lower()
        if any(word in full_text for word in ["urgent", "critical", "emergency", "asap"]):
            extracted["priority"] = "urgent"
        elif any(word in full_text for word in ["broken", "damaged", "defective"]):
            extracted["priority"] = "high"
        
        return extracted
    
    def verify_and_collect_details(self, extracted: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ask user to verify and correct extracted details
        
        Args:
            extracted: Dict with reason, email, order_number, priority
            
        Returns:
            Dict with verified/corrected details
        """
        verified = extracted.copy()
        
        print("\n" + "=" * 70)
        print("📋 PLEASE VERIFY YOUR DETAILS")
        print("=" * 70)
        
        # Show reason
        if verified["reason"]:
            print(f"\n📝 Your Issue/Reason:")
            print(f"   {verified['reason'][:100]}")
            print(f"\n   Is this correct? (yes/no/change): ", end='')
            response = input().strip().lower()
            if response in ['no', 'n', 'change', 'c']:
                print(f"   Enter the correct reason: ", end='')
                verified["reason"] = input().strip()
        else:
            print(f"\n📝 What is your issue/reason for creating this ticket?")
            verified["reason"] = input().strip()
        
        # Show email
        if verified["email"]:
            print(f"\n📧 Your Email:")
            print(f"   {verified['email']}")
            print(f"\n   Is this correct? (yes/no/change): ", end='')
            response = input().strip().lower()
            if response in ['no', 'n', 'change', 'c']:
                print(f"   Enter the correct email: ", end='')
                verified["email"] = input().strip()
        else:
            print(f"\n📧 What is your email address?")
            verified["email"] = input().strip()
        
        # Show order number (optional)
        if verified["order_number"]:
            print(f"\n📦 Your Order Number:")
            print(f"   {verified['order_number']}")
            print(f"\n   Is this correct? (yes/no/change): ", end='')
            response = input().strip().lower()
            if response in ['no', 'n', 'change', 'c']:
                print(f"   Enter the correct order number (or leave blank): ", end='')
                order_input = input().strip()
                if order_input:
                    verified["order_number"] = order_input
                else:
                    verified["order_number"] = None
        else:
            print(f"\n📦 Do you have an order number? (optional, press Enter to skip): ", end='')
            order_input = input().strip()
            if order_input:
                verified["order_number"] = order_input
        
        # Show priority
        print(f"\n⚠️  Priority Level: {verified['priority'].upper()}")
        print(f"   (detected from keywords in your message)")
        
        print("\n" + "=" * 70)
        
        return verified
    
    def create_ticket_from_faq_no_match(
        self,
        user_query: str,
        user_email: str,
        order_number: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a ticket when FAQ doesn't have an answer"""
        
        title = "FAQ No Match - User Question"
        description = f"User Question: {user_query}\n\nThe FAQ database didn't have a clear answer to this question."
        priority = "medium"
        
        # Check for keywords indicating higher priority
        query_lower = user_query.lower()
        if any(word in query_lower for word in ["urgent", "critical", "emergency", "asap"]):
            priority = "urgent"
        elif any(word in query_lower for word in ["broken", "damaged", "defective", "issue", "problem"]):
            priority = "high"
        
        return self.create_ticket(
            title=title,
            description=description,
            user_email=user_email,
            order_number=order_number,
            priority=priority
        )
    
    def handle_dissatisfaction(
        self,
        chat_history: List[Dict],
        interactive: bool = True
    ) -> Dict[str, Any]:
        """
        Handle user dissatisfaction by creating a support ticket
        
        Args:
            chat_history: List of previous messages
            interactive: Whether to ask for missing details
            
        Returns:
            Dict with ticket creation result
        """
        # Extract available details from history
        extracted = self.extract_details_from_history(chat_history)
        
        # If interactive, verify and correct extracted details
        if interactive:
            verified = self.verify_and_collect_details(extracted)
            reason = verified["reason"]
            email = verified["email"]
            order_number = verified["order_number"]
            priority = verified["priority"]
        else:
            # If non-interactive, use extracted directly
            reason = extracted["reason"]
            email = extracted["email"]
            order_number = extracted["order_number"]
            priority = extracted["priority"]
            missing_fields = extracted["missing_fields"]
            
            # If non-interactive and missing critical fields, return error
            if missing_fields:
                return {
                    "success": False,
                    "message": f"Missing details: {', '.join(missing_fields)}",
                    "missing_fields": missing_fields
                }
        
        # Validate we have minimum required fields
        if not reason:
            return {
                "success": False,
                "message": "Reason/issue is required to create a ticket"
            }
        
        if not email:
            return {
                "success": False,
                "message": "Email address is required to create a ticket"
            }
        
        # Create ticket with all details
        return self.create_ticket(
            title="Customer Dissatisfaction - Support Request",
            description=f"User Issue: {reason}\n\nUser was not satisfied with the previous response and needs further assistance.",
            user_email=email,
            order_number=order_number,
            priority=priority
        )
    
    def create_ticket(
        self,
        title: str,
        description: str,
        user_email: str,
        order_number: Optional[str] = None,
        priority: str = "medium"
    ) -> Dict[str, Any]:
        """Create a new support ticket"""
        
        try:
            priority_enum = TicketPriority[priority.upper()]
        except KeyError:
            priority_enum = TicketPriority.MEDIUM
        
        ticket = self.ticket_manager.create_ticket(
            title=title,
            description=description,
            user_email=user_email,
            order_number=order_number,
            priority=priority_enum
        )
        
        return {
            "success": True,
            "ticket_id": ticket.ticket_id,
            "title": ticket.title,
            "status": ticket.status.value,
            "message": f"Support ticket {ticket.ticket_id} has been created successfully!"
        }
    
    def view_tickets(self, user_email: str) -> Dict[str, Any]:
        """View all tickets for a user"""
        summary = self.ticket_manager.get_tickets_summary(user_email)
        
        if summary["total_tickets"] == 0:
            return {
                "success": True,
                "message": "You have no support tickets.",
                "tickets": []
            }
        
        # Format tickets for display
        formatted_tickets = []
        for ticket_dict in summary["tickets"]:
            formatted_tickets.append(
                f"- {ticket_dict['ticket_id']}: {ticket_dict['title']} "
                f"[Status: {ticket_dict['status'].upper()}] "
                f"[Priority: {ticket_dict['priority'].upper()}]"
            )
        
        message = f"You have {summary['total_tickets']} total tickets:\n"
        message += f"  - Open: {summary['open']}\n"
        message += f"  - In Progress: {summary['in_progress']}\n"
        message += f"  - Resolved: {summary['resolved']}\n\n"
        message += "Your tickets:\n" + "\n".join(formatted_tickets)
        
        return {
            "success": True,
            "message": message,
            "summary": summary
        }
    
    def get_ticket_details(self, ticket_id: str) -> Dict[str, Any]:
        """Get details of a specific ticket"""
        ticket = self.ticket_manager.get_ticket(ticket_id)
        
        if not ticket:
            return {
                "success": False,
                "message": f"Ticket {ticket_id} not found."
            }
        
        message = f"Ticket Details - {ticket.ticket_id}\n"
        message += f"Title: {ticket.title}\n"
        message += f"Status: {ticket.status.value.upper()}\n"
        message += f"Priority: {ticket.priority.value.upper()}\n"
        message += f"Created: {ticket.created_at}\n"
        message += f"Last Updated: {ticket.updated_at}\n"
        message += f"Description: {ticket.description}\n"
        
        if ticket.notes:
            message += f"\nNotes:\n"
            for note_entry in ticket.notes:
                message += f"  [{note_entry['timestamp']}] {note_entry['note']}\n"
        
        return {
            "success": True,
            "message": message,
            "ticket": ticket.to_dict()
        }
    
    def handle_ticket_request(
        self,
        query: str,
        user_email: str,
        order_number: Optional[str] = None,
        action: str = "create"
    ) -> Dict[str, Any]:
        """Handle ticket-related requests"""
        
        query_lower = query.lower()
        
        # Check what type of ticket action is requested
        # Priority: explicit action parameter > keywords in query
        if action == "view" or any(word in query_lower for word in ["view", "show", "list", "my", "check"]):
            # View tickets
            return self.view_tickets(user_email)
        
        elif action == "create" or any(word in query_lower for word in ["create", "raise", "open", "new"]):
            # Create new ticket
            title = "Customer Support Request"
            description = query
            priority = "medium"
            
            # Determine priority based on keywords
            if any(word in query_lower for word in ["urgent", "critical", "emergency", "asap"]):
                priority = "urgent"
            elif any(word in query_lower for word in ["broken", "damaged", "defective"]):
                priority = "high"
            
            return self.create_ticket(
                title=title,
                description=description,
                user_email=user_email,
                order_number=order_number,
                priority=priority
            )
        
        else:
            # Default: create ticket
            return self.create_ticket(
                title="Customer Support Request",
                description=query,
                user_email=user_email,
                order_number=order_number,
                priority="medium"
            )
    
    def handle_escalation_routing(
        self,
        chat_history: List[Dict],
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Handle escalation/complaint from router - create ticket immediately
        
        Args:
            chat_history: Conversation history
            context: Router context with order_number, reason_text, etc.
            
        Returns:
            Dict with ticket creation result
        """
        if context is None:
            context = {}
        
        # Extract details from history
        extracted = self.extract_details_from_history(chat_history)
        
        reason = extracted["reason"]
        email = extracted["email"]
        order_number = context.get("order_number") or extracted["order_number"]
        priority = extracted["priority"]
        
        # If critical escalation keywords, set high priority
        if reason:
            reason_lower = reason.lower()
            if any(kw in reason_lower for kw in ["urgent", "critical", "emergency", "damaged", "broken"]):
                priority = "urgent" if any(kw in reason_lower for kw in ["urgent", "critical", "emergency"]) else "high"
        
        # If we have required fields, create ticket immediately
        if not email:
            # Return error with default email
            email = "escalation@support.local"
        
        if not reason:
            reason = context.get("reason_text", "Support escalation from user")
        
        return self.create_ticket(
            title="🚨 ESCALATION - Immediate Support Needed",
            description=f"Escalation Type: {context.get('is_escalation', False)} and {context.get('is_ticket_request', False)}\n\nUser Issue: {reason}\n\nOrder Number: {order_number or 'N/A'}\n\nThis ticket requires immediate attention from the support team.",
            user_email=email,
            order_number=order_number,
            priority=priority
        )


# Global ticket agent instance
ticket_agent = TicketAgent()
