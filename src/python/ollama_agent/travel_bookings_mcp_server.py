"""
Travel Bookings MCP Server with async SQLite backend.

This server provides tools for managing travel bookings data including:
- Creating and reading bookings
- Managing customers
- Handling hotels and flights data
"""

import argparse
import aiosqlite
import asyncio
import json
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from fastmcp import FastMCP
from pathlib import Path

# Create an MCP server
mcp = FastMCP("TravelBookings")

# Database path
DB_PATH = "travel_bookings.db"


async def init_database():
    """Initialize the SQLite database with tables and dummy data"""
    async with aiosqlite.connect(DB_PATH) as conn:
        # Enable foreign keys
        await conn.execute("PRAGMA foreign_keys = ON")

        # Create tables
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS hotels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                city TEXT NOT NULL,
                country TEXT NOT NULL,
                rating REAL,
                price_per_night REAL NOT NULL,
                amenities TEXT
            )
        """
        )

        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS flights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                airline TEXT NOT NULL,
                flight_number TEXT NOT NULL,
                departure_city TEXT NOT NULL,
                arrival_city TEXT NOT NULL,
                departure_time TEXT NOT NULL,
                arrival_time TEXT NOT NULL,
                price REAL NOT NULL,
                aircraft_type TEXT
            )
        """
        )

        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                booking_type TEXT NOT NULL CHECK (booking_type IN ('hotel', 'flight', 'package')),
                hotel_id INTEGER,
                flight_id INTEGER,
                check_in_date TEXT,
                check_out_date TEXT,
                guests INTEGER DEFAULT 1,
                total_amount REAL NOT NULL,
                status TEXT DEFAULT 'confirmed' CHECK (status IN ('pending', 'confirmed', 'cancelled')),
                booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers (id),
                FOREIGN KEY (hotel_id) REFERENCES hotels (id),
                FOREIGN KEY (flight_id) REFERENCES flights (id)
            )
        """
        )

        # Insert dummy data only if tables are empty
        cursor = await conn.execute("SELECT COUNT(*) FROM customers")
        count = await cursor.fetchone()
        if count[0] == 0:
            # Insert dummy customers
            customers_data = [
                ("John", "Doe", "john.doe@email.com", "+1-555-0101"),
                ("Jane", "Smith", "jane.smith@email.com", "+1-555-0102"),
                ("Mike", "Johnson", "mike.johnson@email.com", "+1-555-0103"),
                ("Sarah", "Williams", "sarah.williams@email.com", "+1-555-0104"),
                ("David", "Brown", "david.brown@email.com", "+1-555-0105"),
            ]
            await conn.executemany(
                "INSERT INTO customers (first_name, last_name, email, phone) VALUES (?, ?, ?, ?)",
                customers_data,
            )

            # Insert dummy hotels
            hotels_data = [
                (
                    "Grand Plaza Hotel",
                    "New York",
                    "USA",
                    4.5,
                    299.99,
                    "WiFi,Pool,Gym,Spa",
                ),
                (
                    "Ocean View Resort",
                    "Miami",
                    "USA",
                    4.2,
                    189.99,
                    "WiFi,Pool,Beach Access,Restaurant",
                ),
                (
                    "Mountain Lodge",
                    "Denver",
                    "USA",
                    4.0,
                    159.99,
                    "WiFi,Fireplace,Hiking Trails",
                ),
                (
                    "City Center Inn",
                    "Chicago",
                    "USA",
                    3.8,
                    129.99,
                    "WiFi,Business Center,Restaurant",
                ),
                (
                    "Luxury Suites",
                    "Las Vegas",
                    "USA",
                    4.7,
                    399.99,
                    "WiFi,Casino,Pool,Spa,Fine Dining",
                ),
            ]
            await conn.executemany(
                "INSERT INTO hotels (name, city, country, rating, price_per_night, amenities) VALUES (?, ?, ?, ?, ?, ?)",
                hotels_data,
            )

            # Insert dummy flights
            flights_data = [
                (
                    "American Airlines",
                    "AA101",
                    "New York",
                    "Los Angeles",
                    "2024-02-15 08:00",
                    "2024-02-15 11:30",
                    299.99,
                    "Boeing 737",
                ),
                (
                    "Delta Airlines",
                    "DL205",
                    "Chicago",
                    "Miami",
                    "2024-02-16 14:30",
                    "2024-02-16 18:45",
                    249.99,
                    "Airbus A320",
                ),
                (
                    "United Airlines",
                    "UA350",
                    "Denver",
                    "Seattle",
                    "2024-02-17 10:15",
                    "2024-02-17 12:45",
                    189.99,
                    "Boeing 757",
                ),
                (
                    "Southwest Airlines",
                    "SW420",
                    "Las Vegas",
                    "Phoenix",
                    "2024-02-18 16:20",
                    "2024-02-18 17:35",
                    129.99,
                    "Boeing 737",
                ),
                (
                    "JetBlue Airways",
                    "B6180",
                    "Boston",
                    "Orlando",
                    "2024-02-19 07:45",
                    "2024-02-19 11:15",
                    199.99,
                    "Airbus A321",
                ),
            ]
            await conn.executemany(
                "INSERT INTO flights (airline, flight_number, departure_city, arrival_city, departure_time, arrival_time, price, aircraft_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                flights_data,
            )

            # Insert dummy bookings
            bookings_data = [
                (
                    1,
                    "hotel",
                    1,
                    None,
                    "2024-03-01",
                    "2024-03-05",
                    2,
                    1199.96,
                    "confirmed",
                ),
                (2, "flight", None, 1, None, None, 1, 299.99, "confirmed"),
                (
                    3,
                    "package",
                    2,
                    2,
                    "2024-03-10",
                    "2024-03-15",
                    2,
                    1199.94,
                    "confirmed",
                ),
                (4, "hotel", 3, None, "2024-03-20", "2024-03-22", 1, 319.98, "pending"),
                (5, "flight", None, 4, None, None, 2, 259.98, "confirmed"),
            ]
            await conn.executemany(
                "INSERT INTO bookings (customer_id, booking_type, hotel_id, flight_id, check_in_date, check_out_date, guests, total_amount, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                bookings_data,
            )

        await conn.commit()


# Utility function to run async functions in sync context
def run_async(coro):
    """Run async function in sync context"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(coro)


# Initialize database on startup
run_async(init_database())


@mcp.tool()
def create_customer(
    first_name: str, last_name: str, email: str, phone: str = None
) -> Dict[str, Any]:
    """Create a new customer"""

    async def _create_customer():
        try:
            async with aiosqlite.connect(DB_PATH) as conn:
                cursor = await conn.execute(
                    "INSERT INTO customers (first_name, last_name, email, phone) VALUES (?, ?, ?, ?)",
                    (first_name, last_name, email, phone),
                )
                customer_id = cursor.lastrowid
                await conn.commit()

                return {
                    "success": True,
                    "customer_id": customer_id,
                    "message": f"Customer {first_name} {last_name} created successfully",
                }
        except aiosqlite.IntegrityError as e:
            return {"success": False, "error": f"Email already exists: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    return run_async(_create_customer())


@mcp.tool()
def get_customers(limit: int = 10) -> List[Dict[str, Any]]:
    """Get all customers with optional limit"""

    async def _get_customers():
        try:
            async with aiosqlite.connect(DB_PATH) as conn:
                conn.row_factory = aiosqlite.Row
                cursor = await conn.execute(
                    "SELECT * FROM customers ORDER BY created_at DESC LIMIT ?", (limit,)
                )
                rows = await cursor.fetchall()
                customers = [dict(row) for row in rows]
                return customers
        except Exception as e:
            return [{"error": str(e)}]

    return run_async(_get_customers())


@mcp.tool()
def search_hotels(
    city: str = None, min_rating: float = None, max_price: float = None
) -> List[Dict[str, Any]]:
    """Search hotels by city, minimum rating, and maximum price"""

    async def _search_hotels():
        try:
            async with aiosqlite.connect(DB_PATH) as conn:
                conn.row_factory = aiosqlite.Row

                query = "SELECT * FROM hotels WHERE 1=1"
                params = []

                if city:
                    query += " AND LOWER(city) LIKE LOWER(?)"
                    params.append(f"%{city}%")

                if min_rating:
                    query += " AND rating >= ?"
                    params.append(min_rating)

                if max_price:
                    query += " AND price_per_night <= ?"
                    params.append(max_price)

                query += " ORDER BY rating DESC"

                cursor = await conn.execute(query, params)
                rows = await cursor.fetchall()
                hotels = [dict(row) for row in rows]
                return hotels
        except Exception as e:
            return [{"error": str(e)}]

    return run_async(_search_hotels())


@mcp.tool()
def search_flights(
    departure_city: str = None, arrival_city: str = None, max_price: float = None
) -> List[Dict[str, Any]]:
    """Search flights by departure city, arrival city, and maximum price"""

    async def _search_flights():
        try:
            async with aiosqlite.connect(DB_PATH) as conn:
                conn.row_factory = aiosqlite.Row

                query = "SELECT * FROM flights WHERE 1=1"
                params = []

                if departure_city:
                    query += " AND LOWER(departure_city) LIKE LOWER(?)"
                    params.append(f"%{departure_city}%")

                if arrival_city:
                    query += " AND LOWER(arrival_city) LIKE LOWER(?)"
                    params.append(f"%{arrival_city}%")

                if max_price:
                    query += " AND price <= ?"
                    params.append(max_price)

                query += " ORDER BY price ASC"

                cursor = await conn.execute(query, params)
                rows = await cursor.fetchall()
                flights = [dict(row) for row in rows]
                return flights
        except Exception as e:
            return [{"error": str(e)}]

    return run_async(_search_flights())


@mcp.tool()
def create_hotel_booking(
    customer_id: int,
    hotel_id: int,
    check_in_date: str,
    check_out_date: str,
    guests: int = 1,
) -> Dict[str, Any]:
    """Create a new hotel booking"""

    async def _create_hotel_booking():
        try:
            async with aiosqlite.connect(DB_PATH) as conn:
                # Get hotel price
                cursor = await conn.execute(
                    "SELECT price_per_night FROM hotels WHERE id = ?", (hotel_id,)
                )
                hotel = await cursor.fetchone()
                if not hotel:
                    return {"success": False, "error": "Hotel not found"}

                # Calculate total amount (simplified - just multiply by number of nights)
                check_in = datetime.strptime(check_in_date, "%Y-%m-%d")
                check_out = datetime.strptime(check_out_date, "%Y-%m-%d")
                nights = (check_out - check_in).days
                total_amount = hotel[0] * nights * guests

                cursor = await conn.execute(
                    """INSERT INTO bookings (customer_id, booking_type, hotel_id, check_in_date, check_out_date, guests, total_amount, status) 
                       VALUES (?, 'hotel', ?, ?, ?, ?, ?, 'confirmed')""",
                    (
                        customer_id,
                        hotel_id,
                        check_in_date,
                        check_out_date,
                        guests,
                        total_amount,
                    ),
                )

                booking_id = cursor.lastrowid
                await conn.commit()

                return {
                    "success": True,
                    "booking_id": booking_id,
                    "total_amount": total_amount,
                    "message": "Hotel booking created successfully",
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

    return run_async(_create_hotel_booking())


@mcp.tool()
def create_flight_booking(
    customer_id: int, flight_id: int, guests: int = 1
) -> Dict[str, Any]:
    """Create a new flight booking"""

    async def _create_flight_booking():
        try:
            async with aiosqlite.connect(DB_PATH) as conn:
                # Get flight price
                cursor = await conn.execute(
                    "SELECT price FROM flights WHERE id = ?", (flight_id,)
                )
                flight = await cursor.fetchone()
                if not flight:
                    return {"success": False, "error": "Flight not found"}

                total_amount = flight[0] * guests

                cursor = await conn.execute(
                    """INSERT INTO bookings (customer_id, booking_type, flight_id, guests, total_amount, status) 
                       VALUES (?, 'flight', ?, ?, ?, 'confirmed')""",
                    (customer_id, flight_id, guests, total_amount),
                )

                booking_id = cursor.lastrowid
                await conn.commit()

                return {
                    "success": True,
                    "booking_id": booking_id,
                    "total_amount": total_amount,
                    "message": "Flight booking created successfully",
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

    return run_async(_create_flight_booking())


@mcp.tool()
def get_bookings(
    customer_id: int = None, status: str = None, limit: int = 10
) -> List[Dict[str, Any]]:
    """Get bookings with optional filters for customer_id and status"""

    async def _get_bookings():
        try:
            async with aiosqlite.connect(DB_PATH) as conn:
                conn.row_factory = aiosqlite.Row

                query = """
                    SELECT b.*, c.first_name, c.last_name, c.email,
                           h.name as hotel_name, h.city as hotel_city,
                           f.airline, f.flight_number, f.departure_city, f.arrival_city
                    FROM bookings b
                    JOIN customers c ON b.customer_id = c.id
                    LEFT JOIN hotels h ON b.hotel_id = h.id
                    LEFT JOIN flights f ON b.flight_id = f.id
                    WHERE 1=1
                """
                params = []

                if customer_id:
                    query += " AND b.customer_id = ?"
                    params.append(customer_id)

                if status:
                    query += " AND b.status = ?"
                    params.append(status)

                query += " ORDER BY b.booking_date DESC LIMIT ?"
                params.append(limit)

                cursor = await conn.execute(query, params)
                rows = await cursor.fetchall()
                bookings = [dict(row) for row in rows]
                return bookings
        except Exception as e:
            return [{"error": str(e)}]

    return run_async(_get_bookings())


@mcp.tool()
def update_booking_status(booking_id: int, status: str) -> Dict[str, Any]:
    """Update booking status (pending, confirmed, cancelled)"""

    async def _update_booking_status():
        try:
            if status not in ["pending", "confirmed", "cancelled"]:
                return {
                    "success": False,
                    "error": "Invalid status. Must be: pending, confirmed, or cancelled",
                }

            async with aiosqlite.connect(DB_PATH) as conn:
                cursor = await conn.execute(
                    "UPDATE bookings SET status = ? WHERE id = ?", (status, booking_id)
                )

                if cursor.rowcount == 0:
                    return {"success": False, "error": "Booking not found"}

                await conn.commit()

                return {
                    "success": True,
                    "message": f"Booking {booking_id} status updated to {status}",
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

    return run_async(_update_booking_status())


@mcp.tool()
def get_booking_statistics() -> Dict[str, Any]:
    """Get booking statistics and analytics"""

    async def _get_booking_statistics():
        try:
            async with aiosqlite.connect(DB_PATH) as conn:
                conn.row_factory = aiosqlite.Row

                # Total bookings by type
                cursor = await conn.execute(
                    "SELECT booking_type, COUNT(*) as count FROM bookings GROUP BY booking_type"
                )
                rows = await cursor.fetchall()
                bookings_by_type = {row[0]: row[1] for row in rows}

                # Total bookings by status
                cursor = await conn.execute(
                    "SELECT status, COUNT(*) as count FROM bookings GROUP BY status"
                )
                rows = await cursor.fetchall()
                bookings_by_status = {row[0]: row[1] for row in rows}

                # Total revenue
                cursor = await conn.execute(
                    "SELECT SUM(total_amount) as total_revenue FROM bookings WHERE status = 'confirmed'"
                )
                result = await cursor.fetchone()
                total_revenue = result[0] or 0

                # Average booking amount
                cursor = await conn.execute(
                    "SELECT AVG(total_amount) as avg_amount FROM bookings WHERE status = 'confirmed'"
                )
                result = await cursor.fetchone()
                avg_booking_amount = result[0] or 0

                # Top customers by booking count
                cursor = await conn.execute(
                    """
                    SELECT c.first_name, c.last_name, c.email, COUNT(b.id) as booking_count
                    FROM customers c
                    JOIN bookings b ON c.id = b.customer_id
                    GROUP BY c.id
                    ORDER BY booking_count DESC
                    LIMIT 5
                """
                )
                rows = await cursor.fetchall()
                top_customers = [dict(row) for row in rows]

                return {
                    "bookings_by_type": bookings_by_type,
                    "bookings_by_status": bookings_by_status,
                    "total_revenue": round(total_revenue, 2),
                    "average_booking_amount": round(avg_booking_amount, 2),
                    "top_customers": top_customers,
                }
        except Exception as e:
            return {"error": str(e)}

    return run_async(_get_booking_statistics())


# Add resources for data access
@mcp.resource("booking://{booking_id}")
def get_booking_details(booking_id: str) -> str:
    """Get detailed information about a specific booking"""

    async def _get_booking_details():
        try:
            async with aiosqlite.connect(DB_PATH) as conn:
                conn.row_factory = aiosqlite.Row

                cursor = await conn.execute(
                    """
                    SELECT b.*, c.first_name, c.last_name, c.email, c.phone,
                           h.name as hotel_name, h.city as hotel_city, h.rating as hotel_rating,
                           f.airline, f.flight_number, f.departure_city, f.arrival_city, f.departure_time, f.arrival_time
                    FROM bookings b
                    JOIN customers c ON b.customer_id = c.id
                    LEFT JOIN hotels h ON b.hotel_id = h.id
                    LEFT JOIN flights f ON b.flight_id = f.id
                    WHERE b.id = ?
                """,
                    (booking_id,),
                )

                booking = await cursor.fetchone()

                if booking:
                    return json.dumps(dict(booking), indent=2)
                else:
                    return f"Booking {booking_id} not found"
        except Exception as e:
            return f"Error retrieving booking: {str(e)}"

    return run_async(_get_booking_details())


@mcp.resource("customer://{customer_id}")
def get_customer_profile(customer_id: str) -> str:
    """Get customer profile with booking history"""

    async def _get_customer_profile():
        try:
            async with aiosqlite.connect(DB_PATH) as conn:
                conn.row_factory = aiosqlite.Row

                # Get customer info
                cursor = await conn.execute(
                    "SELECT * FROM customers WHERE id = ?", (customer_id,)
                )
                customer = await cursor.fetchone()

                if not customer:
                    return f"Customer {customer_id} not found"

                # Get customer's bookings
                cursor = await conn.execute(
                    """
                    SELECT b.*, h.name as hotel_name, f.airline, f.flight_number
                    FROM bookings b
                    LEFT JOIN hotels h ON b.hotel_id = h.id
                    LEFT JOIN flights f ON b.flight_id = f.id
                    WHERE b.customer_id = ?
                    ORDER BY b.booking_date DESC
                """,
                    (customer_id,),
                )

                rows = await cursor.fetchall()
                bookings = [dict(row) for row in rows]

                profile = {
                    "customer": dict(customer),
                    "bookings": bookings,
                    "total_bookings": len(bookings),
                    "total_spent": sum(
                        b["total_amount"]
                        for b in bookings
                        if b["status"] == "confirmed"
                    ),
                }

                return json.dumps(profile, indent=2)
        except Exception as e:
            return f"Error retrieving customer profile: {str(e)}"

    return run_async(_get_customer_profile())


# Add prompts for travel assistance
@mcp.prompt()
def travel_recommendation(
    destination: str, budget: float, travel_dates: str, preferences: str = "standard"
) -> str:
    """Generate travel recommendations based on destination, budget, and preferences"""
    return f"""
    Please provide travel recommendations for:
    
    Destination: {destination}
    Budget: ${budget}
    Travel Dates: {travel_dates}
    Preferences: {preferences}
    
    Include suggestions for:
    1. Best hotels within budget
    2. Flight options
    3. Local attractions and activities
    4. Dining recommendations
    5. Transportation tips
    6. Packing suggestions based on season/weather
    
    Format the response as a comprehensive travel guide.
    """


@mcp.prompt()
def booking_assistance(booking_type: str, customer_requirements: str) -> str:
    """Generate booking assistance prompts"""
    return f"""
    Help the customer with their {booking_type} booking request:
    
    Customer Requirements: {customer_requirements}
    
    Please provide:
    1. Available options that match their requirements
    2. Pricing information
    3. Recommendations based on value and quality
    4. Any special offers or packages
    5. Booking terms and conditions
    6. Cancellation policies
    
    Be helpful, informative, and focus on finding the best solution for the customer's needs.
    """


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Start the MCP server")
    parser.add_argument("--server_type", type=str, default="sse")

    args = parser.parse_args()

    mcp.run(args.server_type)
