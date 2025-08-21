"""
Travel Bookings MCP Client using LlamaIndex BasicMCPClient and McpToolSpec.

This client connects to the Travel Bookings MCP Server and provides
tools for managing travel bookings through LlamaIndex.
"""

import asyncio
from typing import List, Dict, Any, Optional
from llama_index.tools.mcp import BasicMCPClient, McpToolSpec


class TravelBookingsMCPClient:
    """Client for interacting with the Travel Bookings MCP Server"""

    def __init__(self, server_command: List[str] = None):
        """
        Initialize the Travel Bookings MCP Client

        Args:
            server_command: Command to start the MCP server.
                          Defaults to running the travel_bookings_mcp_server.py
        """
        if server_command is None:
            server_command = ["python", "travel_bookings_mcp_server.py"]

        self.server_command = server_command
        self.client = None
        self.tool_spec = None

    async def connect(self):
        """Connect to the MCP server and initialize tools"""
        try:
            # Create BasicMCPClient instance
            self.client = BasicMCPClient("http://localhost:8000/sse")

            # Connect to the server

            # Create McpToolSpec from the client
            self.tool_spec = McpToolSpec(self.client)

            print("Successfully connected to Travel Bookings MCP Server")
            return True

        except Exception as e:
            print(f"Failed to connect to MCP server: {e}")
            return False

    async def disconnect(self):
        """Disconnect from the MCP server"""
        if self.client:
            # await self.client.disconnect()
            print("Disconnected from Travel Bookings MCP Server")

    async def get_tools(self):
        """Get all available tools from the MCP server"""
        if self.tool_spec:
            return await self.tool_spec.to_tool_list_async()
        return []

    async def get_tool_names(self) -> List[str]:
        """Get names of all available tools"""
        tools = await self.get_tools()
        return [tool.metadata.name for tool in tools if tool.metadata.name is not None]

    async def list_available_tools(self):
        """List all available tools with descriptions"""
        if not self.client:
            print("Client not connected. Please call connect() first.")
            return

        try:
            tools_response = await self.client.list_tools()
            print("\nAvailable Tools:")
            print("=" * 50)

            for tool in tools_response.tools:
                print(f"Tool: {tool.name}")
                print(f"Description: {tool.description}")
                if hasattr(tool, "inputSchema") and tool.inputSchema:
                    print(
                        f"Parameters: {tool.inputSchema.get('properties', {}).keys()}"
                    )
                print("-" * 30)

        except Exception as e:
            print(f"Error listing tools: {e}")

    async def list_available_resources(self):
        """List all available resources"""
        if not self.client:
            print("Client not connected. Please call connect() first.")
            return

        try:
            resources_response = await self.client.list_resources()
            print("\nAvailable Resources:")
            print("=" * 50)

            for resource in resources_response.resources:
                print(f"Resource: {resource.uri}")
                print(f"Name: {resource.name}")
                print(f"Description: {resource.description}")
                print("-" * 30)

        except Exception as e:
            print(f"Error listing resources: {e}")

    async def list_available_prompts(self):
        """List all available prompts"""
        if not self.client:
            print("Client not connected. Please call connect() first.")
            return

        try:
            prompts_response = await self.client.list_prompts()
            print("\nAvailable Prompts:")
            print("=" * 50)

            for prompt in prompts_response.prompts:
                print(f"Prompt: {prompt.name}")
                print(f"Description: {prompt.description}")
                if hasattr(prompt, "arguments"):
                    print(f"Arguments: {[arg.name for arg in prompt.arguments]}")
                print("-" * 30)

        except Exception as e:
            print(f"Error listing prompts: {e}")

    # Convenience methods for common operations
    async def create_customer(
        self, first_name: str, last_name: str, email: str, phone: str = None
    ):
        """Create a new customer"""
        if not self.client:
            raise Exception("Client not connected")

        return await self.client.call_tool(
            "create_customer",
            {
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "phone": phone,
            },
        )

    async def search_hotels(
        self, city: str = None, min_rating: float = None, max_price: float = None
    ):
        """Search for hotels"""
        if not self.client:
            raise Exception("Client not connected")

        params = {}
        if city:
            params["city"] = city
        if min_rating:
            params["min_rating"] = min_rating
        if max_price:
            params["max_price"] = max_price

        return await self.client.call_tool("search_hotels", params)

    async def search_flights(
        self,
        departure_city: str = None,
        arrival_city: str = None,
        max_price: float = None,
    ):
        """Search for flights"""
        if not self.client:
            raise Exception("Client not connected")

        params = {}
        if departure_city:
            params["departure_city"] = departure_city
        if arrival_city:
            params["arrival_city"] = arrival_city
        if max_price:
            params["max_price"] = max_price

        return await self.client.call_tool("search_flights", params)

    async def create_hotel_booking(
        self,
        customer_id: int,
        hotel_id: int,
        check_in_date: str,
        check_out_date: str,
        guests: int = 1,
    ):
        """Create a hotel booking"""
        if not self.client:
            raise Exception("Client not connected")

        return await self.client.call_tool(
            "create_hotel_booking",
            {
                "customer_id": customer_id,
                "hotel_id": hotel_id,
                "check_in_date": check_in_date,
                "check_out_date": check_out_date,
                "guests": guests,
            },
        )

    async def create_flight_booking(
        self, customer_id: int, flight_id: int, guests: int = 1
    ):
        """Create a flight booking"""
        if not self.client:
            raise Exception("Client not connected")

        return await self.client.call_tool(
            "create_flight_booking",
            {"customer_id": customer_id, "flight_id": flight_id, "guests": guests},
        )

    async def get_bookings(
        self, customer_id: int = None, status: str = None, limit: int = 10
    ):
        """Get bookings with optional filters"""
        if not self.client:
            raise Exception("Client not connected")

        params = {"limit": limit}
        if customer_id:
            params["customer_id"] = customer_id
        if status:
            params["status"] = status

        return await self.client.call_tool("get_bookings", params)

    async def get_booking_statistics(self):
        """Get booking statistics"""
        if not self.client:
            raise Exception("Client not connected")

        return await self.client.call_tool("get_booking_statistics", {})

    async def get_resource(self, uri: str):
        """Get a specific resource"""
        if not self.client:
            raise Exception("Client not connected")

        return await self.client.read_resource(uri)

    async def get_prompt(self, name: str, arguments: Dict[str, Any] = None):
        """Get a prompt with arguments"""
        if not self.client:
            raise Exception("Client not connected")

        return await self.client.get_prompt(name, arguments or {})


# Context manager for easier usage
class TravelBookingsMCPContext:
    """Context manager for Travel Bookings MCP Client"""

    def __init__(self, server_command: List[str] = None):
        self.client = TravelBookingsMCPClient(server_command)

    async def __aenter__(self):
        await self.client.connect()
        return self.client

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.disconnect()


# Example usage functions
async def demo_client_usage():
    """Demonstrate client usage"""
    async with TravelBookingsMCPContext() as client:
        # List available capabilities
        await client.list_available_tools()
        await client.list_available_resources()
        await client.list_available_prompts()

        # Create a customer
        print("\n" + "=" * 50)
        print("Creating a new customer...")
        customer_result = await client.create_customer(
            "Alice", "Johnson", "alice.johnson@email.com", "+1-555-0199"
        )
        print(f"Customer creation result: {customer_result}")

        # Search for hotels
        print("\n" + "=" * 50)
        print("Searching for hotels in New York...")
        hotels = await client.search_hotels(city="New York", min_rating=4.0)
        print(f"Found hotels: {hotels}")

        # Search for flights
        print("\n" + "=" * 50)
        print("Searching for flights from New York to Los Angeles...")
        flights = await client.search_flights(
            departure_city="New York", arrival_city="Los Angeles"
        )
        print(f"Found flights: {flights}")

        # Get booking statistics
        print("\n" + "=" * 50)
        print("Getting booking statistics...")
        stats = await client.get_booking_statistics()
        print(f"Booking statistics: {stats}")

        # Get a resource
        print("\n" + "=" * 50)
        print("Getting booking details for booking ID 1...")
        try:
            booking_details = await client.get_resource("booking://1")
            print(f"Booking details: {booking_details}")
        except Exception as e:
            print(f"Error getting resource: {e}")


if __name__ == "__main__":
    # Run the demo
    asyncio.run(demo_client_usage())
