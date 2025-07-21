# Apollo MCP Server for GraphQL Router

### Apollo MCP server
docker image pull ghcr.io/apollographql/apollo-mcp-server:latest

### References

https://www.apollographql.com/docs/apollo-mcp-server/guides

https://modelcontextprotocol.io/introduction

### Dev API key Rover for GraphOS
user:gh.26e9ae6e-a15d-4445-acaa-e0779b4a5342:8EqERPLfpcJUGSTLoX75Qw

## Run Instructions

Please ensure you have UV installed.

1. cd to src/python
2. uv run run_travel_agent.py


# Travel Bookings MCP Server

A comprehensive MCP (Model Context Protocol) server for managing travel bookings with SQLite backend.

## Features

### Database Tables
- **Customers**: Customer information and contact details
- **Hotels**: Hotel inventory with ratings, prices, and amenities
- **Flights**: Flight information with schedules and pricing
- **Bookings**: Booking records linking customers to hotels/flights

### Available Tools

#### Customer Management
- `create_customer(first_name, last_name, email, phone)` - Create new customer
- `get_customers(limit)` - Retrieve customer list

#### Search & Discovery
- `search_hotels(city, min_rating, max_price)` - Find hotels by criteria
- `search_flights(departure_city, arrival_city, max_price)` - Find flights by criteria

#### Booking Management
- `create_hotel_booking(customer_id, hotel_id, check_in_date, check_out_date, guests)` - Book hotel
- `create_flight_booking(customer_id, flight_id, guests)` - Book flight
- `get_bookings(customer_id, status, limit)` - Retrieve bookings
- `update_booking_status(booking_id, status)` - Update booking status

#### Analytics
- `get_booking_statistics()` - Get comprehensive booking analytics

### Resources
- `booking://{booking_id}` - Detailed booking information
- `customer://{customer_id}` - Customer profile with booking history

### Prompts
- `travel_recommendation(destination, budget, travel_dates, preferences)` - Generate travel recommendations
- `booking_assistance(booking_type, customer_requirements)` - Provide booking assistance

## Usage

### Running the Server
```bash
cd src/python
python travel_bookings_mcp_server.py
```

### Testing
```bash
python test_travel_server.py
```

### Example Usage
```bash
python usage_example.py
```

## Database Schema

The server automatically creates and populates the SQLite database with sample data including:
- 5 sample customers
- 5 sample hotels across different cities
- 5 sample flights with various routes
- 5 sample bookings of different types

## Sample Data

### Hotels
- Grand Plaza Hotel (New York) - $299.99/night
- Ocean View Resort (Miami) - $189.99/night  
- Mountain Lodge (Denver) - $159.99/night
- City Center Inn (Chicago) - $129.99/night
- Luxury Suites (Las Vegas) - $399.99/night

### Flights
- American Airlines AA101: New York → Los Angeles
- Delta Airlines DL205: Chicago → Miami
- United Airlines UA350: Denver → Seattle
- Southwest Airlines SW420: Las Vegas → Phoenix
- JetBlue Airways B6180: Boston → Orlando

## Integration with MCP Clients

This server can be integrated with any MCP-compatible client to provide travel booking capabilities through natural language interactions.
