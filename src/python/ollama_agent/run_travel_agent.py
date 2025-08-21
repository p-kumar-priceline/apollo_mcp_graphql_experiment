"""
Simple launcher for the Travel Booking Agent with Ollama.
"""

import asyncio
import sys
import os


async def check_prerequisites():
    """Check if everything is ready to run"""
    print("Checking prerequisites...")

    # Check if MCP server exists
    if not os.path.exists("travel_bookings_mcp_server.py"):
        print("✗ MCP server file not found")
        print("  Make sure travel_bookings_mcp_server.py is in the current directory")
        return False

    # Check if client exists
    if not os.path.exists("travel_bookings_mcp_client.py"):
        print("✗ MCP client file not found")
        print("  Make sure travel_bookings_mcp_client.py is in the current directory")
        return False

    # Check Ollama connectivity
    try:
        import aiohttp

        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:11434/api/tags") as response:
                if response.status == 200:
                    print("✓ Ollama is running")
                    return True
                else:
                    print("✗ Ollama is not responding")
                    return False
    except Exception as e:
        print(f"✗ Cannot connect to Ollama: {e}")
        print("  Make sure Ollama is running: ollama serve")
        return False


async def main():
    """Main launcher function"""
    print("Travel Booking Agent Launcher")
    print("=" * 40)

    # Check prerequisites
    if not await check_prerequisites():
        print("\nSetup issues detected. Please resolve them first.")
        print("\nQuick setup:")
        print("1. Install Ollama: https://ollama.ai")
        print("2. Start Ollama: ollama serve")
        print("3. Install a model: ollama pull llama3.1:8b")
        return

    print("\n✓ All prerequisites met!")

    # Choose mode
    print("\nChoose mode:")
    print("1. Interactive chat")
    print("2. Demo mode")
    print("3. Test Ollama connectivity")

    choice = input("\nEnter choice (1-3): ").strip()

    if choice == "1":
        print("\nStarting interactive mode...")
        from travel_booking_agent import interactive_chat

        await interactive_chat()
    elif choice == "2":
        print("\nStarting demo mode...")
        from travel_booking_agent import demo_travel_agent

        await demo_travel_agent()
    elif choice == "3":
        print("\nTesting Ollama...")
        from travel_booking_agent import quick_test

        await quick_test()
    else:
        print("Invalid choice. Exiting.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error: {e}")
