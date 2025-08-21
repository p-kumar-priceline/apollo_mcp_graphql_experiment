"""
Test script for the travel bookings MCP server
"""

import sqlite3
import json
from travel_bookings_mcp_server import DB_PATH


def test_database():
    """Test the database setup and data"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print("=== Database Test ===")

    # Test customers
    cursor.execute("SELECT COUNT(*) as count FROM customers")
    customer_count = cursor.fetchone()[0]
    print(f"Customers: {customer_count}")

    # Test hotels
    cursor.execute("SELECT COUNT(*) as count FROM hotels")
    hotel_count = cursor.fetchone()[0]
    print(f"Hotels: {hotel_count}")

    # Test flights
    cursor.execute("SELECT COUNT(*) as count FROM flights")
    flight_count = cursor.fetchone()[0]
    print(f"Flights: {flight_count}")

    # Test bookings
    cursor.execute("SELECT COUNT(*) as count FROM bookings")
    booking_count = cursor.fetchone()[0]
    print(f"Bookings: {booking_count}")

    # Show sample data
    print("\n=== Sample Customers ===")
    cursor.execute("SELECT * FROM customers LIMIT 3")
    for row in cursor.fetchall():
        print(
            f"ID: {row['id']}, Name: {row['first_name']} {row['last_name']}, Email: {row['email']}"
        )

    print("\n=== Sample Hotels ===")
    cursor.execute("SELECT * FROM hotels LIMIT 3")
    for row in cursor.fetchall():
        print(
            f"ID: {row['id']}, Name: {row['name']}, City: {row['city']}, Price: ${row['price_per_night']}"
        )

    print("\n=== Sample Bookings ===")
    cursor.execute(
        """
        SELECT b.id, b.booking_type, b.total_amount, b.status,
               c.first_name, c.last_name,
               h.name as hotel_name, f.flight_number
        FROM bookings b
        JOIN customers c ON b.customer_id = c.id
        LEFT JOIN hotels h ON b.hotel_id = h.id
        LEFT JOIN flights f ON b.flight_id = f.id
        LIMIT 3
    """
    )
    for row in cursor.fetchall():
        print(
            f"Booking ID: {row['id']}, Type: {row['booking_type']}, Customer: {row['first_name']} {row['last_name']}, Amount: ${row['total_amount']}"
        )

    conn.close()


if __name__ == "__main__":
    test_database()
