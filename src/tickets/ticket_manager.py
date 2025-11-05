"""
Ticket Management System
Handles support ticket creation, tracking, and status updates
"""
import uuid
from datetime import datetime
from typing import Any
from src.database.mongodb_client import mongodb_client
from typing import Dict, List, Optional
from enum import Enum

class TicketStatus(Enum):
    """Ticket status types"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"
    REOPENED = "reopened"

class TicketPriority(Enum):
    """Ticket priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class Ticket:
    """Represents a support ticket"""
    
    def __init__(
        self,
        title: str,
        description: str,
        user_email: str,
        order_number: Optional[str] = None,
        priority: TicketPriority = TicketPriority.MEDIUM
    ):
        self.ticket_id = f"TKT-{uuid.uuid4().hex[:8].upper()}"
        self.title = title
        self.description = description
        self.user_email = user_email
        # Clean order number - store None if it's a default message or "no order"
        self.order_number = self._clean_order_number(order_number)
        self.priority = priority
        self.status = TicketStatus.OPEN
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.notes: List[str] = []
    
    def _clean_order_number(self, order_number: Optional[str]) -> Optional[str]:
        """
        Clean order number for storage
        - If None or empty, return None
        - If contains default messages like "no order", "N/A", etc., return None
        - If it's the default example "ORD-1234-5678", return None
        - Otherwise return the order number as-is
        """
        if not order_number:
            return None
        
        order_str = str(order_number).strip()
        
        # Check if it's the default example order number
        if order_str.upper() == 'ORD-1234-5678':
            return None
        
        order_lower = order_str.lower()
        
        # Default messages to treat as "no order"
        no_order_phrases = [
            'no order',
            'n/a',
            'not_found',
            'not found',
            'none',
            'no related order',
            'no order number'
        ]
        
        if order_lower in no_order_phrases:
            return None
        
        return order_number
    
    def get_display_order_number(self) -> str:
        """
        Get order number for display purposes
        Returns "No related order" if order_number is None
        """
        if self.order_number is None:
            return "No related order"
        return self.order_number
    
    def add_note(self, note: str):
        """Add a note to the ticket"""
        # Store timestamp as ISO string so the ticket is JSON-serializable for DB storage
        self.notes.append({
            "timestamp": datetime.now().isoformat(),
            "note": note
        })
        self.updated_at = datetime.now()
    
    def update_status(self, new_status: TicketStatus, note: str = ""):
        """Update ticket status"""
        self.status = new_status
        self.updated_at = datetime.now()
        if note:
            self.add_note(f"Status changed to {new_status.value}: {note}")
    
    def to_dict(self) -> Dict:
        """Convert ticket to dictionary"""
        return {
            "ticket_id": self.ticket_id,
            "title": self.title,
            "description": self.description,
            "user_email": self.user_email,
            "order_number": self.order_number,  # Store as None in DB if no order
            "order_number_display": self.get_display_order_number(),  # For frontend display
            "priority": self.priority.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "notes": self.notes
        }

class TicketManager:
    """Manages support tickets"""
    
    def __init__(self):
        # Store tickets by user email for easy lookup
        self.tickets_by_user: Dict[str, List[Ticket]] = {}
        self.all_tickets: Dict[str, Ticket] = {}
    
    def create_ticket(
        self,
        title: str,
        description: str,
        user_email: str,
        order_number: Optional[str] = None,
        priority: TicketPriority = TicketPriority.MEDIUM
    ) -> Ticket:
        """Create a new support ticket"""
        ticket = Ticket(
            title=title,
            description=description,
            user_email=user_email,
            order_number=order_number,
            priority=priority
        )
        
        # Store ticket in memory
        self.all_tickets[ticket.ticket_id] = ticket

        if user_email not in self.tickets_by_user:
            self.tickets_by_user[user_email] = []
        self.tickets_by_user[user_email].append(ticket)

        # Persist to MongoDB if available
        try:
            if mongodb_client.is_connected():
                tickets_col = mongodb_client.get_collection("tickets")
                doc = ticket.to_dict()
                # Insert document
                result = tickets_col.insert_one(doc)
                # Save DB _id string on ticket for reference
                try:
                    ticket.db_id = str(result.inserted_id)
                except Exception:
                    ticket.db_id = None
        except Exception:
            # Fail silently and keep in-memory store operational
            pass

        return ticket
    
    def get_ticket(self, ticket_id: str) -> Optional[Ticket]:
        """Get a specific ticket by ID"""
        return self.all_tickets.get(ticket_id)
    
    def get_user_tickets(self, user_email: str) -> List[Ticket]:
        """Get all tickets for a user"""
        return self.tickets_by_user.get(user_email, [])
    
    def get_user_tickets_by_status(
        self,
        user_email: str,
        status: TicketStatus
    ) -> List[Ticket]:
        """Get tickets for a user filtered by status"""
        user_tickets = self.get_user_tickets(user_email)
        return [t for t in user_tickets if t.status == status]
    
    def update_ticket_status(
        self,
        ticket_id: str,
        new_status: TicketStatus,
        note: str = ""
    ) -> bool:
        """Update a ticket's status"""
        ticket = self.get_ticket(ticket_id)
        if ticket:
            ticket.update_status(new_status, note)
            # Persist status update to DB if connected
            try:
                if mongodb_client.is_connected():
                    tickets_col = mongodb_client.get_collection("tickets")
                    update_data = {
                        "status": ticket.status.value,
                        "updated_at": ticket.updated_at.isoformat()
                    }
                    if note:
                        # Also push the note into notes array
                        tickets_col.update_one(
                            {"ticket_id": ticket_id},
                            {
                                "$set": update_data,
                                "$push": {"notes": {"timestamp": datetime.now().isoformat(), "note": note}}
                            }
                        )
                    else:
                        tickets_col.update_one({"ticket_id": ticket_id}, {"$set": update_data})
            except Exception:
                pass
            return True
        return False
    
    def add_ticket_note(self, ticket_id: str, note: str) -> bool:
        """Add a note to a ticket"""
        ticket = self.get_ticket(ticket_id)
        if ticket:
            ticket.add_note(note)
            # Persist note to DB if connected
            try:
                if mongodb_client.is_connected():
                    tickets_col = mongodb_client.get_collection("tickets")
                    tickets_col.update_one(
                        {"ticket_id": ticket_id},
                        {"$push": {"notes": {"timestamp": datetime.now().isoformat(), "note": note}},
                         "$set": {"updated_at": ticket.updated_at.isoformat()}}
                    )
            except Exception:
                pass
            return True
        return False
    
    def get_tickets_summary(self, user_email: str) -> Dict:
        """Get a summary of user's tickets"""
        user_tickets = self.get_user_tickets(user_email)
        
        summary = {
            "total_tickets": len(user_tickets),
            "open": len(self.get_user_tickets_by_status(user_email, TicketStatus.OPEN)),
            "in_progress": len(self.get_user_tickets_by_status(user_email, TicketStatus.IN_PROGRESS)),
            "resolved": len(self.get_user_tickets_by_status(user_email, TicketStatus.RESOLVED)),
            "tickets": [
                {
                    "ticket_id": t.ticket_id,
                    "title": t.title,
                    "status": t.status.value,
                    "priority": t.priority.value,
                    "created_at": t.created_at.isoformat(),
                    "order_number": t.get_display_order_number()  # Use display version
                }
                for t in user_tickets
            ]
        }
        
        return summary


# Global ticket manager instance
ticket_manager = TicketManager()
