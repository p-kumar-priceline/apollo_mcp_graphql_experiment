"""
Unit tests for host agent.
Tests the host agent functionality for A2A protocol coordination.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from unittest.mock import Mock, patch, MagicMock
from src.agents.host import HostAgent


class TestHostAgent:
    """Test cases for HostAgent."""

    def setup_method(self):
        """Set up test fixtures."""
        with patch("src.agents.host.host_agent.A2AServer"):
            self.host_agent = HostAgent("test-host")

    @patch("src.agents.host.host_agent.A2AServer")
    def test_init(self, mock_a2a_server):
        """Test HostAgent initialization."""
        agent = HostAgent("test-agent")

        assert agent.agent_id == "test-agent"
        assert agent.server is None
        assert agent.registered_agents == {}

    @patch("src.agents.host.host_agent.A2AServer")
    def test_start_server(self, mock_a2a_server_class):
        """Test starting the A2A server."""
        mock_server = Mock()
        mock_a2a_server_class.return_value = mock_server

        agent = HostAgent()
        agent.start_server("localhost", 8080)

        assert agent.server == mock_server
        mock_a2a_server_class.assert_called_once_with(
            host="localhost", port=8080, agent_id="host-agent"
        )
        mock_server.start.assert_called_once()

    @patch("src.agents.host.host_agent.A2AServer")
    def test_stop_server(self, mock_a2a_server_class):
        """Test stopping the A2A server."""
        mock_server = Mock()
        mock_a2a_server_class.return_value = mock_server

        agent = HostAgent()
        agent.server = mock_server
        agent.stop_server()

        mock_server.stop.assert_called_once()

    def test_register_data_agent(self):
        """Test registering a data agent."""
        with patch("src.agents.host.host_agent.A2AServer"):
            agent = HostAgent()
            mock_data_agent = Mock()
            mock_data_agent.agent_id = "data-agent-1"

            agent.register_data_agent(mock_data_agent)

            assert "data-agent-1" in agent.registered_agents
            assert agent.registered_agents["data-agent-1"] == mock_data_agent

    def test_handle_message(self):
        """Test handling incoming messages."""
        with patch("src.agents.host.host_agent.A2AServer"):
            agent = HostAgent()
            mock_server = Mock()
            agent.server = mock_server

            # Mock data agent
            mock_data_agent = Mock()
            mock_data_agent.process_query.return_value = "Test response"
            agent.registered_agents["data-agent"] = mock_data_agent

            # Mock message
            mock_message = Mock()
            mock_message.sender_id = "user-1"
            mock_message.recipient_id = "data-agent"
            mock_message.content = "Test query"

            agent._handle_message(mock_message)

            mock_data_agent.process_query.assert_called_once_with("Test query")
            mock_server.send_message.assert_called_once()

    def test_handle_agent_register(self):
        """Test handling agent registration."""
        with patch("src.agents.host.host_agent.A2AServer"):
            agent = HostAgent()

            # This should not raise an exception
            agent._handle_agent_register("new-agent")

    def test_handle_agent_unregister(self):
        """Test handling agent unregistration."""
        with patch("src.agents.host.host_agent.A2AServer"):
            agent = HostAgent()

            # Register an agent first
            mock_agent = Mock()
            agent.registered_agents["test-agent"] = mock_agent

            # Unregister the agent
            agent._handle_agent_unregister("test-agent")

            assert "test-agent" not in agent.registered_agents

    def test_send_query_to_data_agent_success(self):
        """Test sending query to registered data agent."""
        with patch("src.agents.host.host_agent.A2AServer"):
            agent = HostAgent()

            # Register a data agent
            mock_data_agent = Mock()
            mock_data_agent.process_query.return_value = "Query response"
            agent.registered_agents["data-agent"] = mock_data_agent

            response = agent.send_query_to_data_agent("Test query", "data-agent")

            assert response == "Query response"
            mock_data_agent.process_query.assert_called_once_with("Test query")

    def test_send_query_to_data_agent_not_found(self):
        """Test sending query to non-existent data agent."""
        with patch("src.agents.host.host_agent.A2AServer"):
            agent = HostAgent()

            response = agent.send_query_to_data_agent(
                "Test query", "non-existent-agent"
            )

            assert response == "Data agent non-existent-agent not found"

    def test_get_registered_agents(self):
        """Test getting list of registered agents."""
        with patch("src.agents.host.host_agent.A2AServer"):
            agent = HostAgent()

            # Register some agents
            agent.registered_agents["agent-1"] = Mock()
            agent.registered_agents["agent-2"] = Mock()

            agents = agent.get_registered_agents()

            assert set(agents) == {"agent-1", "agent-2"}

    def test_get_agent_info(self):
        """Test getting agent information."""
        with patch("src.agents.host.host_agent.A2AServer"):
            agent = HostAgent("test-host")
            agent.registered_agents["data-agent"] = Mock()

            info = agent.get_agent_info()

            assert info["agent_id"] == "test-host"
            assert info["registered_agents"] == ["data-agent"]
            assert "Manage A2A server" in info["capabilities"]
