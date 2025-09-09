"""
A2A server manager for coordinating agents and handling requests.
"""

import asyncio
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from ...agents import HostAgent, DataAgent
from ...config import settings


class QueryRequest(BaseModel):
    """Request model for data queries."""

    query: str
    agent_id: Optional[str] = "data-agent"


class QueryResponse(BaseModel):
    """Response model for data queries."""

    response: str
    agent_id: str
    status: str


class A2AServerManager:
    """
    A2A server manager that coordinates the host agent and data agents.

    This manager provides a REST API interface for interacting with
    the A2A protocol and manages the lifecycle of agents.
    """

    def __init__(self):
        """Initialize the A2A server manager."""
        self.app = FastAPI(
            title="A2A Prototype Server",
            description="A2A protocol server with AWS Bedrock and Athena integration",
            version="1.0.0",
        )
        self.host_agent: Optional[HostAgent] = None
        self.data_agent: Optional[DataAgent] = None
        self._setup_routes()

    def _setup_routes(self) -> None:
        """Set up FastAPI routes."""

        @self.app.get("/")
        async def root():
            """Root endpoint with server information."""
            return {
                "message": "A2A Prototype Server",
                "version": "1.0.0",
                "status": "running",
            }

        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            return {"status": "healthy", "agents": self._get_agent_status()}

        @self.app.post("/query", response_model=QueryResponse)
        async def query_data(request: QueryRequest):
            """
            Execute a data query using the data agent.

            Args:
                request: Query request with query string and optional agent ID

            Returns:
                Query response with results
            """
            try:
                if not self.data_agent:
                    raise HTTPException(
                        status_code=503, detail="Data agent not available"
                    )

                response = self.data_agent.process_query(request.query)

                return QueryResponse(
                    response=response, agent_id=request.agent_id, status="success"
                )

            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/agents")
        async def list_agents():
            """List all registered agents."""
            return {
                "host_agent": (
                    self.host_agent.get_agent_info() if self.host_agent else None
                ),
                "data_agent": (
                    self.data_agent.get_agent_info() if self.data_agent else None
                ),
            }

        @self.app.get("/agents/{agent_id}")
        async def get_agent_info(agent_id: str):
            """Get information about a specific agent."""
            if agent_id == "host-agent" and self.host_agent:
                return self.host_agent.get_agent_info()
            elif agent_id == "data-agent" and self.data_agent:
                return self.data_agent.get_agent_info()
            else:
                raise HTTPException(status_code=404, detail="Agent not found")

    def _get_agent_status(self) -> Dict[str, bool]:
        """Get status of all agents."""
        return {
            "host_agent": self.host_agent is not None,
            "data_agent": self.data_agent is not None,
        }

    async def start(self) -> None:
        """Start the A2A server and initialize agents."""
        print("Initializing A2A server...")

        # Initialize host agent
        self.host_agent = HostAgent()
        print("Host agent initialized")

        # Initialize data agent
        self.data_agent = DataAgent()
        print("Data agent initialized")

        # Register data agent with host agent
        self.host_agent.register_data_agent(self.data_agent)
        print("Data agent registered with host agent")

        print("A2A server ready")

    async def stop(self) -> None:
        """Stop the A2A server and cleanup agents."""
        if self.host_agent:
            self.host_agent.stop_server()
        print("A2A server stopped")

    def get_app(self) -> FastAPI:
        """Get the FastAPI application instance."""
        return self.app
