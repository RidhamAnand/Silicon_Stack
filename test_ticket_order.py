#!/usr/bin/env python
"""Test ticket manager order number handling"""
from src.tickets.ticket_manager import ticket_manager, TicketPriority

# Test 1: "no order" should become None
print("=" * 60)
print("TEST 1: Creating ticket with 'no order'")
print("=" * 60)
ticket1 = ticket_manager.create_ticket(
    title='Test Ticket 1',
    description='Test with no order',
    user_email='test@test.com',
    order_number='no order',
    priority=TicketPriority.MEDIUM
)
print(f"Internal order_number: {repr(ticket1.order_number)}")
print(f"Display order_number: {ticket1.get_display_order_number()}")
print(f"Dict order_number: {ticket1.to_dict()['order_number']}")
print(f"Dict order_number_display: {ticket1.to_dict()['order_number_display']}")

# Test 2: Valid order number should be preserved
print("\n" + "=" * 60)
print("TEST 2: Creating ticket with valid order 'ORD-1234-5678'")
print("=" * 60)
ticket2 = ticket_manager.create_ticket(
    title='Test Ticket 2',
    description='Test with valid order',
    user_email='test@test.com',
    order_number='ORD-1234-5678',
    priority=TicketPriority.HIGH
)
print(f"Internal order_number: {repr(ticket2.order_number)}")
print(f"Display order_number: {ticket2.get_display_order_number()}")
print(f"Dict order_number: {ticket2.to_dict()['order_number']}")
print(f"Dict order_number_display: {ticket2.to_dict()['order_number_display']}")

# Test 3: None should become "No related order" for display
print("\n" + "=" * 60)
print("TEST 3: Creating ticket with None order_number")
print("=" * 60)
ticket3 = ticket_manager.create_ticket(
    title='Test Ticket 3',
    description='Test with None order',
    user_email='test@test.com',
    order_number=None,
    priority=TicketPriority.LOW
)
print(f"Internal order_number: {repr(ticket3.order_number)}")
print(f"Display order_number: {ticket3.get_display_order_number()}")
print(f"Dict order_number: {ticket3.to_dict()['order_number']}")
print(f"Dict order_number_display: {ticket3.to_dict()['order_number_display']}")

# Test 4: "N/A" should become None
print("\n" + "=" * 60)
print("TEST 4: Creating ticket with 'N/A'")
print("=" * 60)
ticket4 = ticket_manager.create_ticket(
    title='Test Ticket 4',
    description='Test with N/A',
    user_email='test@test.com',
    order_number='N/A',
    priority=TicketPriority.MEDIUM
)
print(f"Internal order_number: {repr(ticket4.order_number)}")
print(f"Display order_number: {ticket4.get_display_order_number()}")
print(f"Dict order_number: {ticket4.to_dict()['order_number']}")
print(f"Dict order_number_display: {ticket4.to_dict()['order_number_display']}")

print("\n" + "=" * 60)
print("✅ All tests completed!")
print("=" * 60)
