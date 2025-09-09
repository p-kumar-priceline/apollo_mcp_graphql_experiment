"""
Main entry point for the A2A prototype application.
Demonstrates A2A protocol with Google ADK, FastMCP, and AWS Bedrock.
"""

import asyncio
import uvicorn
from src.servers import A2AServerManager
from src.config import settings


async def main():
    """
    Main function to start the A2A prototype server.

    This function initializes and starts the A2A server with:
    - Host agent for coordination
    - Data agent with AWS Bedrock LLM
    - MCP tools for AWS Athena integration
    """
    print("Starting A2A Prototype Server...")
    print(f"Configuration:")
    print(f"  - AWS Region: {settings.aws.aws_region}")
    print(f"  - Bedrock Model: {settings.bedrock.model_id}")
    print(f"  - Athena Database: {settings.athena.database}")
    print(f"  - Server Host: {settings.a2a.host}:{settings.a2a.port}")

    # Create and start the A2A server manager
    server_manager = A2AServerManager()
    await server_manager.start()

    # Start the FastAPI server
    config = uvicorn.Config(
        app=server_manager.get_app(),
        host=settings.a2a.host,
        port=settings.a2a.port,
        log_level="info",
    )

    server = uvicorn.Server(config)

    try:
        print(f"Server starting on http://{settings.a2a.host}:{settings.a2a.port}")
        print("Available endpoints:")
        print("  - GET  /           - Server information")
        print("  - GET  /health     - Health check")
        print("  - POST /query      - Execute data queries")
        print("  - GET  /agents     - List all agents")
        print("  - GET  /agents/{id} - Get agent information")
        print("\nPress Ctrl+C to stop the server")

        await server.serve()

    except KeyboardInterrupt:
        print("\nShutting down server...")
        await server_manager.stop()


if __name__ == "__main__":
    asyncio.run(main())
