"""
Example of using the Travel Bookings MCP Client with LlamaIndex agents using local Ollama LLM.

This example shows how to create an AI agent that can help with travel bookings
using the MCP tools with a local Ollama model.
"""

import asyncio
from typing import List
from llama_index.core.agent import ReActAgent
from llama_index.llms.ollama import Ollama
from llama_index.core.tools import BaseTool
from travel_bookings_mcp_client import TravelBookingsMCPClient, TravelBookingsMCPContext


class TravelBookingAgent:
    """AI Agent for travel booking assistance using MCP tools with Ollama"""

    def __init__(
        self, model_name: str = "llama3.1", base_url: str = "http://localhost:11434"
    ):
        """
        Initialize the Travel Booking Agent with Ollama

        Args:
            model_name: Name of the Ollama model to use (e.g., 'llama3.1', 'mistral', 'codellama')
            base_url: Base URL for Ollama server
        """
        # Initialize Ollama LLM
        self.llm = Ollama(
            model=model_name,
            base_url=base_url,
            temperature=0.1,
            request_timeout=120.0,  # Increase timeout for local models
        )

        self.agent = None
        self.mcp_client = None
        self.model_name = model_name

    async def initialize(self, server_command: List[str] = None):
        """Initialize the agent with MCP tools"""
        try:
            print(f"Initializing agent with Ollama model: {self.model_name}")

            # Connect to MCP server
            self.mcp_client = TravelBookingsMCPClient(server_command)
            await self.mcp_client.connect()

            # Get tools from MCP server
            tools = await self.mcp_client.get_tools()

            if not tools:
                raise Exception("No tools available from MCP server")

            print(f"Loaded {len(tools)} tools from MCP server")

            # Create ReAct agent with MCP tools
            self.agent = ReActAgent.from_tools(
                tools=tools,
                llm=self.llm,
                verbose=True,
                max_iterations=10,
                system_prompt="""
You are a helpful travel booking assistant powered by Ollama. You can help customers with:

1. Creating customer profiles
2. Searching for hotels and flights  
3. Making bookings
4. Managing existing bookings
5. Providing travel recommendations

IMPORTANT INSTRUCTIONS:
- Always be polite, helpful, and provide clear information about pricing, availability, and booking terms
- When making bookings, confirm all details with the customer before proceeding
- Use the available tools to search for options, create bookings, and retrieve information
- If you need to create a customer first, ask for their details (name, email, phone)
- When searching for hotels or flights, ask for specific criteria like city, dates, budget, etc.
- Always show prices and key details when presenting options
- Be concise but informative in your responses

Available tools allow you to:
- create_customer: Create new customer profiles
- get_customers: Retrieve customer information
- search_hotels: Find hotels by city, rating, price
- search_flights: Find flights by departure/arrival cities, price
- create_hotel_booking: Book hotels for customers
- create_flight_booking: Book flights for customers  
- get_bookings: View existing bookings
- update_booking_status: Modify booking status
- get_booking_statistics: View booking analytics

Think step by step and use the appropriate tools to help the customer.
                """.strip(),
            )

            print("Travel Booking Agent initialized successfully!")
            return True

        except Exception as e:
            print(f"Failed to initialize agent: {e}")
            return False

    async def chat(self, message: str) -> str:
        """Chat with the travel booking agent"""
        if not self.agent:
            return "Agent not initialized. Please call initialize() first."

        try:
            print(f"\nProcessing with {self.model_name}...")
            response = await self.agent.achat(message)
            return str(response)
        except Exception as e:
            return f"Error processing request: {e}"

    async def cleanup(self):
        """Clean up resources"""
        if self.mcp_client:
            await self.mcp_client.disconnect()


async def demo_travel_agent():
    """Demonstrate the travel booking agent with Ollama"""

    # You can change the model here - popular options:
    # - llama3.1 (recommended for general use)
    # - llama3.1:8b (smaller, faster)
    # - mistral
    # - codellama
    # - qwen2.5

    agent = TravelBookingAgent(model_name="qwen2.5:7b-instruct")

    try:
        # Initialize the agent
        print("Initializing Travel Booking Agent with Ollama...")
        success = await agent.initialize()

        if not success:
            print("Failed to initialize agent")
            return

        # Example conversations
        conversations = [
            "Hello! I'm looking for a hotel in Miami for 2 nights. What options do you have?",
            "Can you show me flights from Chicago to Miami under $300?",
            "I'd like to create a customer profile for Alice Cooper with email alice.cooper.demo@email.com and phone +1-555-0199",
            "What are the current booking statistics?",
            "Can you help me find a luxury hotel in Las Vegas with a rating above 4.5?",
        ]

        print("\n" + "=" * 60)
        print("TRAVEL BOOKING AGENT DEMO (Powered by Ollama)")
        print("=" * 60)

        for i, message in enumerate(conversations, 1):
            print(f"\n--- Conversation {i} ---")
            print(f"User: {message}")
            print("Agent: ", end="")

            response = await agent.chat(message)
            print(response)
            print("-" * 40)

            # Add a small delay between conversations
            await asyncio.sleep(2)

    except Exception as e:
        print(f"Error in demo: {e}")

    finally:
        # Clean up
        await agent.cleanup()


async def interactive_chat():
    """Interactive chat with the travel booking agent using Ollama"""

    print("Available Ollama models you can try:")
    print("- llama3.1 (recommended)")
    print("- llama3.1:8b (faster)")
    print("- mistral")
    print("- qwen2.5")
    print("- codellama")

    model_choice = input("\nEnter model name (or press Enter for llama3.1): ").strip()
    if not model_choice:
        model_choice = "llama3.1"

    agent = TravelBookingAgent(model_name=model_choice)

    try:
        print(f"\nInitializing Travel Booking Agent with {model_choice}...")
        success = await agent.initialize()

        if not success:
            print("Failed to initialize agent")
            print("\nTroubleshooting tips:")
            print("1. Make sure Ollama is running: ollama serve")
            print(f"2. Make sure the model is installed: ollama pull {model_choice}")
            print("3. Check if Ollama is accessible at http://localhost:11434")
            return

        print("\n" + "=" * 60)
        print(f"INTERACTIVE TRAVEL BOOKING ASSISTANT (Powered by {model_choice})")
        print("=" * 60)
        print("Type 'quit' or 'exit' to end the conversation")
        print("Type 'help' for example queries")
        print("Type 'stats' for quick booking statistics")
        print("-" * 60)

        while True:
            try:
                user_input = input("\nYou: ").strip()

                if user_input.lower() in ["quit", "exit", "bye"]:
                    print("Thank you for using the Travel Booking Assistant!")
                    break

                if user_input.lower() == "help":
                    print("\nExample queries you can try:")
                    print("- 'Find hotels in New York with rating above 4.0'")
                    print("- 'Show me flights from Boston to Orlando under $250'")
                    print(
                        "- 'Create a customer profile for Jane Doe with email jane@example.com'"
                    )
                    print(
                        "- 'Book the Grand Plaza Hotel for customer ID 1 from 2024-03-15 to 2024-03-18'"
                    )
                    print("- 'What hotels are available in Las Vegas?'")
                    print("- 'Show me all bookings for customer ID 2'")
                    continue

                if user_input.lower() == "stats":
                    print("Getting booking statistics...")
                    stats = await agent.mcp_client.get_booking_statistics()
                    print(f"Total Revenue: ${stats.get('total_revenue', 0)}")
                    print(f"Average Booking: ${stats.get('average_booking_amount', 0)}")
                    print(f"Bookings by Type: {stats.get('bookings_by_type', {})}")
                    print(f"Bookings by Status: {stats.get('bookings_by_status', {})}")
                    continue

                if not user_input:
                    continue

                print(f"Agent ({model_choice}): ", end="")
                response = await agent.chat(user_input)
                print(response)

            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
                print("The model might be taking longer to respond. Please try again.")

    finally:
        await agent.cleanup()


async def quick_test():
    """Quick test to verify Ollama connectivity"""
    print("Testing Ollama connectivity...")

    try:
        llm = Ollama(model="llama3.1", base_url="http://localhost:11434")
        response = await llm.acomplete(
            "Hello! Respond with just 'OK' if you can hear me."
        )
        print(f"✓ Ollama test successful: {response}")
        return True
    except Exception as e:
        print(f"✗ Ollama test failed: {e}")
        print("\nTroubleshooting:")
        print("1. Start Ollama: ollama serve")
        print("2. Install a model: ollama pull llama3.1")
        print("3. Verify Ollama is running on http://localhost:11434")
        return False


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "interactive":
            # Run interactive mode
            asyncio.run(interactive_chat())
        elif sys.argv[1] == "test":
            # Run connectivity test
            asyncio.run(quick_test())
        else:
            print("Usage:")
            print("  python travel_agent_example.py          # Run demo")
            print("  python travel_agent_example.py interactive  # Interactive chat")
            print(
                "  python travel_agent_example.py test     # Test Ollama connectivity"
            )
    else:
        # Run demo mode
        asyncio.run(demo_travel_agent())
