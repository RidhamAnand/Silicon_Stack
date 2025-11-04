"""
MongoDB database client for customer support system
"""
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from typing import Optional, Dict, List, Any
import logging
from datetime import datetime

from src.config.settings import config

logger = logging.getLogger(__name__)

class MongoDBClient:
    """MongoDB client for customer data and orders"""

    def __init__(self):
        self.client: Optional[MongoClient] = None
        self.db = None
        self._connected = False

    def connect(self) -> bool:
        """Connect to MongoDB Atlas"""
        try:
            self.client = MongoClient(
                config.MONGODB_URI,
                serverSelectionTimeoutMS=5000,  # 5 second timeout
                connectTimeoutMS=5000,
                socketTimeoutMS=5000
            )

            # Test the connection
            self.client.admin.command('ping')
            self.db = self.client[config.MONGODB_DB_NAME]
            self._connected = True

            logger.info(f"Connected to MongoDB database: {config.MONGODB_DB_NAME}")
            return True

        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            self._connected = False
            return False
        except Exception as e:
            logger.error(f"Unexpected error connecting to MongoDB: {e}")
            self._connected = False
            return False

    def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            self._connected = False
            logger.info("Disconnected from MongoDB")

    def is_connected(self) -> bool:
        """Check if connected to MongoDB"""
        return self._connected

    def get_collection(self, collection_name: str):
        """Get a collection from the database"""
        if not self._connected or self.db is None:
            raise ConnectionError("Not connected to MongoDB")
        return self.db[collection_name]

    # Order-related methods
    def find_order_by_number(self, order_number: str) -> Optional[Dict[str, Any]]:
        """Find an order by order number"""
        try:
            orders = self.get_collection("orders")
            return orders.find_one({"order_number": order_number})
        except Exception as e:
            logger.error(f"Error finding order {order_number}: {e}")
            return None

    def find_orders_by_email(self, email: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Find orders by customer email"""
        try:
            orders = self.get_collection("orders")
            return list(orders.find({"customer_email": email}).limit(limit))
        except Exception as e:
            logger.error(f"Error finding orders for email {email}: {e}")
            return []

    def find_customer_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Find customer by email"""
        try:
            customers = self.get_collection("customers")
            return customers.find_one({"email": email})
        except Exception as e:
            logger.error(f"Error finding customer {email}: {e}")
            return None

    def update_order_status(self, order_number: str, status: str, notes: str = "") -> bool:
        """Update order status"""
        try:
            orders = self.get_collection("orders")
            update_data = {
                "status": status,
                "updated_at": datetime.utcnow()
            }
            if notes:
                update_data["status_notes"] = notes

            result = orders.update_one(
                {"order_number": order_number},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating order {order_number}: {e}")
            return False

# Global instance
mongodb_client = MongoDBClient()