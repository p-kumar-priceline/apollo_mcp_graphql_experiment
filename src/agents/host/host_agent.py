"""
Host agent implementation for A2A protocol.
Manages the A2A server and coordinates with data agents.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from ...config import settings


@dataclass
class Message:
    """Simple message class for A2A communication."""

    sender_id: str
    recipient_id: str
    content: str
    message_type: str = "message"


class A2AServer:
    """Simplified A2A server implementation."""

    def __init__(self, host: str, port: int, agent_id: str):
        self.host = host
        self.port = port
        self.agent_id = agent_id
        self.message_handlers = []
        self.agent_register_handlers = []
        self.agent_unregister_handlers = []
        self._running = False

    def on_message(self, handler):
        """Register message handler."""
        self.message_handlers.append(handler)

    def on_agent_register(self, handler):
        """Register agent registration handler."""
        self.agent_register_handlers.append(handler)

    def on_agent_unregister(self, handler):
        """Register agent unregistration handler."""
        self.agent_unregister_handlers.append(handler)

    def start(self):
        """Start the A2A server."""
        self._running = True
        print(f"A2A server started on {self.host}:{self.port}")

    def stop(self):
        """Stop the A2A server."""
        self._running = False
        print("A2A server stopped")

    def send_message(self, message: Message):
        """Send a message to another agent."""
        print(
            f"Sending message from {message.sender_id} to {message.recipient_id}: {message.content}"
        )
        # In a real implementation, this would send over network
        for handler in self.message_handlers:
            handler(message)


class HostAgent:
    """
    Host agent that manages the A2A server and coordinates with data agents.

    This agent serves as the central coordinator in the A2A protocol,
    managing communication between different agents and handling
    user requests.
    """

    def __init__(self, agent_id: Optional[str] = None):
        """
        Initialize the host agent.

        Args:
            agent_id: Unique identifier for the agent
        """
        self.agent_id = agent_id or settings.a2a.agent_id
        self.server = None
        self.registered_agents: Dict[str, Agent] = {}

    def start_server(
        self, host: Optional[str] = None, port: Optional[int] = None
    ) -> None:
        """
        Start the A2A server.

        Args:
            host: Server host address
            port: Server port number
        """
        host = host or settings.a2a.host
        port = port or settings.a2a.port

        # Create A2A server
        self.server = A2AServer(host=host, port=port, agent_id=self.agent_id)

        # Register message handlers
        self.server.on_message(self._handle_message)
        self.server.on_agent_register(self._handle_agent_register)
        self.server.on_agent_unregister(self._handle_agent_unregister)

        print(f"Starting A2A server on {host}:{port}")
        self.server.start()

    def stop_server(self) -> None:
        """Stop the A2A server."""
        if self.server:
            self.server.stop()
            print("A2A server stopped")

    def register_data_agent(self, data_agent) -> None:
        """
        Register a data agent with the host.

        Args:
            data_agent: Data agent instance to register
        """
        agent_id = data_agent.agent_id
        self.registered_agents[agent_id] = data_agent
        print(f"Registered data agent: {agent_id}")

    def _handle_message(self, message: Message) -> None:
        """
        Handle incoming messages from agents.

        Args:
            message: Incoming message from an agent
        """
        print(f"Received message from {message.sender_id}: {message.content}")

        # Route message to appropriate agent
        if message.recipient_id in self.registered_agents:
            agent = self.registered_agents[message.recipient_id]
            response = agent.process_query(message.content)

            # Send response back to sender
            response_message = Message(
                sender_id=self.agent_id,
                recipient_id=message.sender_id,
                content=response,
                message_type="response",
            )
            self.server.send_message(response_message)

    def _handle_agent_register(self, agent_id: str) -> None:
        """
        Handle agent registration events.

        Args:
            agent_id: ID of the registering agent
        """
        print(f"Agent registered: {agent_id}")

    def _handle_agent_unregister(self, agent_id: str) -> None:
        """
        Handle agent unregistration events.

        Args:
            agent_id: ID of the unregistering agent
        """
        print(f"Agent unregistered: {agent_id}")
        if agent_id in self.registered_agents:
            del self.registered_agents[agent_id]

    def send_query_to_data_agent(self, query: str, agent_id: str = "data-agent") -> str:
        """
        Send a query to a specific data agent.

        Args:
            query: Query to send to the data agent
            agent_id: ID of the target data agent

        Returns:
            Response from the data agent
        """
        if agent_id not in self.registered_agents:
            return f"Data agent {agent_id} not found"

        agent = self.registered_agents[agent_id]
        return agent.process_query(query)

    def get_registered_agents(self) -> List[str]:
        """
        Get list of registered agent IDs.

        Returns:
            List of registered agent IDs
        """
        return list(self.registered_agents.keys())

    def get_agent_info(self) -> Dict[str, Any]:
        """
        Get information about the host agent.

        Returns:
            Dictionary containing agent metadata
        """
        return {
            "agent_id": self.agent_id,
            "server_running": self.server is not None,
            "registered_agents": self.get_registered_agents(),
            "capabilities": [
                "Manage A2A server",
                "Coordinate with data agents",
                "Route messages between agents",
                "Handle agent registration",
            ],
        }
