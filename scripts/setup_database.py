#!/usr/bin/env python3
"""
Setup script for MongoDB database with sample data
"""
import sys
import os
from datetime import datetime, timedelta
import random

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database import mongodb_client, db_service
from database.models import Order, Customer, OrderItem, ShippingAddress, OrderStatus, PaymentStatus

def create_sample_customers():
    """Create sample customer data"""
    customers = [
        {
            "email": "john.doe@example.com",
            "name": "John Doe",
            "phone": "+1-555-0123",
            "total_orders": 3,
            "total_spent": 245.67,
            "last_order_date": datetime.utcnow() - timedelta(days=5),
            "account_status": "active",
            "preferences": {"newsletter": True, "sms_updates": False}
        },
        {
            "email": "jane.smith@example.com",
            "name": "Jane Smith",
            "phone": "+1-555-0456",
            "total_orders": 1,
            "total_spent": 89.99,
            "last_order_date": datetime.utcnow() - timedelta(days=15),
            "account_status": "active",
            "preferences": {"newsletter": True, "sms_updates": True}
        },
        {
            "email": "bob.wilson@example.com",
            "name": "Bob Wilson",
            "phone": "+1-555-0789",
            "total_orders": 5,
            "total_spent": 456.78,
            "last_order_date": datetime.utcnow() - timedelta(days=2),
            "account_status": "active",
            "preferences": {"newsletter": False, "sms_updates": True}
        }
    ]

    customers_collection = mongodb_client.get_collection("customers")
    customers_collection.insert_many(customers)
    print(f"✓ Created {len(customers)} sample customers")

def create_sample_orders():
    """Create sample order data"""
    orders = [
        {
            "order_number": "ORD-2024-001",
            "customer_email": "john.doe@example.com",
            "customer_name": "John Doe",
            "items": [
                {
                    "product_id": "PROD-001",
                    "product_name": "Wireless Headphones",
                    "quantity": 1,
                    "unit_price": 99.99,
                    "total_price": 99.99
                },
                {
                    "product_id": "PROD-002",
                    "product_name": "Phone Case",
                    "quantity": 2,
                    "unit_price": 19.99,
                    "total_price": 39.98
                }
            ],
            "subtotal": 139.97,
            "tax": 11.20,
            "shipping_cost": 9.50,
            "total_amount": 160.67,
            "status": "shipped",
            "payment_status": "completed",
            "shipping_address": {
                "street": "123 Main St",
                "city": "Anytown",
                "state": "CA",
                "zip_code": "12345",
                "country": "US"
            },
            "order_date": datetime.utcnow() - timedelta(days=5),
            "shipped_date": datetime.utcnow() - timedelta(days=3),
            "tracking_number": "TRK123456789",
            "notes": "Fragile items - handle with care"
        },
        {
            "order_number": "ORD-2024-002",
            "customer_email": "jane.smith@example.com",
            "customer_name": "Jane Smith",
            "items": [
                {
                    "product_id": "PROD-003",
                    "product_name": "Laptop Stand",
                    "quantity": 1,
                    "unit_price": 49.99,
                    "total_price": 49.99
                },
                {
                    "product_id": "PROD-004",
                    "product_name": "USB Cable",
                    "quantity": 1,
                    "unit_price": 9.99,
                    "total_price": 9.99
                },
                {
                    "product_id": "PROD-005",
                    "product_name": "Mouse Pad",
                    "quantity": 1,
                    "unit_price": 12.99,
                    "total_price": 12.99
                }
            ],
            "subtotal": 72.97,
            "tax": 5.84,
            "shipping_cost": 11.18,
            "total_amount": 89.99,
            "status": "delivered",
            "payment_status": "completed",
            "shipping_address": {
                "street": "456 Oak Ave",
                "city": "Somewhere",
                "state": "NY",
                "zip_code": "67890",
                "country": "US"
            },
            "order_date": datetime.utcnow() - timedelta(days=15),
            "shipped_date": datetime.utcnow() - timedelta(days=12),
            "delivered_date": datetime.utcnow() - timedelta(days=10),
            "tracking_number": "TRK987654321",
            "notes": "Leave at front door if not home"
        },
        {
            "order_number": "ORD-2024-003",
            "customer_email": "bob.wilson@example.com",
            "customer_name": "Bob Wilson",
            "items": [
                {
                    "product_id": "PROD-006",
                    "product_name": "Bluetooth Speaker",
                    "quantity": 1,
                    "unit_price": 79.99,
                    "total_price": 79.99
                }
            ],
            "subtotal": 79.99,
            "tax": 6.40,
            "shipping_cost": 7.50,
            "total_amount": 93.89,
            "status": "processing",
            "payment_status": "completed",
            "shipping_address": {
                "street": "789 Pine Rd",
                "city": "Elsewhere",
                "state": "TX",
                "zip_code": "54321",
                "country": "US"
            },
            "order_date": datetime.utcnow() - timedelta(days=2),
            "notes": "Gift wrapping requested"
        },
        {
            "order_number": "ORD-2024-004",
            "customer_email": "john.doe@example.com",
            "customer_name": "John Doe",
            "items": [
                {
                    "product_id": "PROD-007",
                    "product_name": "Webcam",
                    "quantity": 1,
                    "unit_price": 59.99,
                    "total_price": 59.99
                }
            ],
            "subtotal": 59.99,
            "tax": 4.80,
            "shipping_cost": 6.50,
            "total_amount": 71.29,
            "status": "pending",
            "payment_status": "pending",
            "shipping_address": {
                "street": "123 Main St",
                "city": "Anytown",
                "state": "CA",
                "zip_code": "12345",
                "country": "US"
            },
            "order_date": datetime.utcnow() - timedelta(hours=6),
            "notes": "Rush order - needed for meeting tomorrow"
        }
    ]

    orders_collection = mongodb_client.get_collection("orders")
    orders_collection.insert_many(orders)
    print(f"✓ Created {len(orders)} sample orders")

def main():
    """Main setup function"""
    print("Setting up MongoDB database...")

    # Connect to database
    if not mongodb_client.connect():
        print("❌ Failed to connect to MongoDB")
        print("Please check your MONGODB_URI in .env file")
        sys.exit(1)

    try:
        # Clear existing data
        print("Clearing existing data...")
        mongodb_client.get_collection("customers").delete_many({})
        mongodb_client.get_collection("orders").delete_many({})

        # Create sample data
        create_sample_customers()
        create_sample_orders()

        print("\n✅ Database setup complete!")
        print("\nSample data created:")
        print("- 3 customers with order history")
        print("- 4 orders in various states (pending, processing, shipped, delivered)")
        print("\nTest order numbers: ORD-2024-001, ORD-2024-002, ORD-2024-003, ORD-2024-004")

    except Exception as e:
        print(f"❌ Error during setup: {e}")
        sys.exit(1)
    finally:
        mongodb_client.disconnect()

if __name__ == "__main__":
    main()