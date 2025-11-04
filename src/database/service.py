"""
Database service layer for customer support operations
"""
import logging
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta

from .mongodb_client import mongodb_client
from .models import Order, Customer, OrderLookupResult, CustomerLookupResult, OrderStatus

logger = logging.getLogger(__name__)

class DatabaseService:
    """Service layer for database operations"""

    def __init__(self):
        self.client = mongodb_client

    def connect(self) -> bool:
        """Connect to database"""
        return self.client.connect()

    def disconnect(self):
        """Disconnect from database"""
        self.client.disconnect()

    def is_connected(self) -> bool:
        """Check database connection"""
        return self.client.is_connected()

    def lookup_order(self, order_number: str) -> OrderLookupResult:
        """Lookup an order by order number"""
        try:
            if not self.is_connected():
                return OrderLookupResult(
                    found=False,
                    message="Database connection unavailable"
                )

            order_data = self.client.find_order_by_number(order_number)

            if not order_data:
                return OrderLookupResult(
                    found=False,
                    message=f"Order {order_number} not found"
                )

            # Convert to Order model
            order = Order(**order_data)

            # Get customer info
            customer_data = self.client.find_customer_by_email(order.customer_email)
            customer_info = None
            if customer_data:
                customer_info = {
                    "name": customer_data.get("name"),
                    "email": customer_data.get("email"),
                    "total_orders": customer_data.get("total_orders", 0),
                    "account_status": customer_data.get("account_status", "active")
                }

            return OrderLookupResult(
                found=True,
                order=order,
                customer_info=customer_info,
                message=f"Order {order_number} found"
            )

        except Exception as e:
            logger.error(f"Error looking up order {order_number}: {e}")
            return OrderLookupResult(
                found=False,
                message=f"Error retrieving order: {str(e)}"
            )

    def lookup_customer_orders(self, email: str, limit: int = 5) -> CustomerLookupResult:
        """Lookup customer and their recent orders"""
        try:
            if not self.is_connected():
                return CustomerLookupResult(
                    found=False,
                    message="Database connection unavailable"
                )

            # Find customer
            customer_data = self.client.find_customer_by_email(email)
            customer = None
            if customer_data:
                customer = Customer(**customer_data)

            # Find recent orders
            orders_data = self.client.find_orders_by_email(email, limit)
            recent_orders = [Order(**order_data) for order_data in orders_data]

            if not customer and not recent_orders:
                return CustomerLookupResult(
                    found=False,
                    message=f"No customer found with email {email}"
                )

            return CustomerLookupResult(
                found=True,
                customer=customer,
                recent_orders=recent_orders,
                message=f"Found customer with {len(recent_orders)} recent orders"
            )

        except Exception as e:
            logger.error(f"Error looking up customer {email}: {e}")
            return CustomerLookupResult(
                found=False,
                message=f"Error retrieving customer data: {str(e)}"
            )

    def get_order_status_description(self, order: Order) -> str:
        """Get human-readable order status description"""
        status_descriptions = {
            OrderStatus.PENDING: "Your order is being prepared",
            OrderStatus.PROCESSING: "Your order is being processed",
            OrderStatus.SHIPPED: f"Your order shipped on {order.shipped_date.strftime('%B %d, %Y') if order.shipped_date else 'recently'}",
            OrderStatus.DELIVERED: f"Your order was delivered on {order.delivered_date.strftime('%B %d, %Y') if order.delivered_date else 'recently'}",
            OrderStatus.CANCELLED: "This order has been cancelled",
            OrderStatus.RETURNED: "This order has been returned",
            OrderStatus.REFUNDED: "This order has been refunded"
        }

        description = status_descriptions.get(order.status, f"Order status: {order.status.value}")

        if order.tracking_number and order.status in [OrderStatus.SHIPPED, OrderStatus.DELIVERED]:
            description += f" (Tracking: {order.tracking_number})"

        if order.status_notes:
            description += f" - {order.status_notes}"

        return description

    def format_order_summary(self, order: Order) -> str:
        """Format order information for display"""
        lines = [
            f"Order #{order.order_number}",
            f"Status: {self.get_order_status_description(order)}",
            f"Order Date: {order.order_date.strftime('%B %d, %Y')}",
            f"Total: ${order.total_amount:.2f}",
            f"Items: {len(order.items)} item(s)"
        ]

        if order.items:
            lines.append("Items:")
            for item in order.items[:3]:  # Show first 3 items
                lines.append(f"  • {item.product_name} (x{item.quantity}) - ${item.total_price:.2f}")
            if len(order.items) > 3:
                lines.append(f"  ... and {len(order.items) - 3} more items")

        return "\n".join(lines)

# Global instance
db_service = DatabaseService()