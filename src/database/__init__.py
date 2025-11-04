"""
Database package
"""
from .mongodb_client import mongodb_client, MongoDBClient
from .service import db_service, DatabaseService
from .models import (
    Order, Customer, OrderItem, ShippingAddress,
    OrderStatus, PaymentStatus, OrderLookupResult, CustomerLookupResult
)

__all__ = [
    # Clients
    "mongodb_client",
    "MongoDBClient",

    # Services
    "db_service",
    "DatabaseService",

    # Models
    "Order",
    "Customer",
    "OrderItem",
    "ShippingAddress",
    "OrderStatus",
    "PaymentStatus",
    "OrderLookupResult",
    "CustomerLookupResult"
]
