"""
Database models for customer support system
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr
from enum import Enum

class OrderStatus(str, Enum):
    """Order status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    RETURNED = "returned"
    REFUNDED = "refunded"

class PaymentStatus(str, Enum):
    """Payment status enumeration"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class OrderItem(BaseModel):
    """Individual order item"""
    product_id: str
    product_name: str
    quantity: int = Field(gt=0)
    unit_price: float = Field(gt=0)
    total_price: float = Field(gt=0)

class ShippingAddress(BaseModel):
    """Shipping address"""
    street: str
    city: str
    state: str
    zip_code: str
    country: str = "US"

class Order(BaseModel):
    """Order model"""
    order_number: str = Field(..., description="Unique order identifier")
    customer_email: EmailStr
    customer_name: str
    items: List[OrderItem]
    subtotal: float = Field(gt=0)
    tax: float = Field(ge=0)
    shipping_cost: float = Field(ge=0)
    total_amount: float = Field(gt=0)
    status: OrderStatus = OrderStatus.PENDING
    payment_status: PaymentStatus = PaymentStatus.PENDING
    shipping_address: ShippingAddress
    order_date: datetime = Field(default_factory=datetime.utcnow)
    shipped_date: Optional[datetime] = None
    delivered_date: Optional[datetime] = None
    tracking_number: Optional[str] = None
    notes: Optional[str] = None
    status_notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class Customer(BaseModel):
    """Customer model"""
    email: EmailStr
    name: str
    phone: Optional[str] = None
    total_orders: int = 0
    total_spent: float = 0.0
    last_order_date: Optional[datetime] = None
    account_status: str = "active"
    preferences: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class OrderLookupResult(BaseModel):
    """Result of an order lookup operation"""
    found: bool
    order: Optional[Order] = None
    message: str
    customer_info: Optional[Dict[str, Any]] = None

class CustomerLookupResult(BaseModel):
    """Result of a customer lookup operation"""
    found: bool
    customer: Optional[Customer] = None
    recent_orders: List[Order] = Field(default_factory=list)
    message: str