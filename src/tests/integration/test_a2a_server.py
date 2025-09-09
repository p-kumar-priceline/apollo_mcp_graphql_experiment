"""
Integration tests for A2A server.
Tests the complete A2A server functionality with real components.
"""

import pytest
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from src.servers.a2a import A2AServerManager


class TestA2AServerManager:
    """Integration test cases for A2AServerManager."""

    def setup_method(self):
        """Set up test fixtures."""
        with (
            patch("src.servers.a2a.a2a_server.HostAgent"),
            patch("src.servers.a2a.a2a_server.DataAgent"),
        ):
            self.server_manager = A2AServerManager()

    def test_start_server(self):
        """Test starting the A2A server manager."""
        with (
            patch("src.servers.a2a.a2a_server.HostAgent") as mock_host_agent_class,
            patch("src.servers.a2a.a2a_server.DataAgent") as mock_data_agent_class,
        ):

            mock_host_agent = Mock()
            mock_data_agent = Mock()
            mock_host_agent_class.return_value = mock_host_agent
            mock_data_agent_class.return_value = mock_data_agent

            # Test synchronous initialization
            self.server_manager.host_agent = mock_host_agent
            self.server_manager.data_agent = mock_data_agent

            assert self.server_manager.host_agent == mock_host_agent
            assert self.server_manager.data_agent == mock_data_agent

    def test_stop_server(self):
        """Test stopping the A2A server manager."""
        with patch("src.servers.a2a.a2a_server.HostAgent") as mock_host_agent_class:
            mock_host_agent = Mock()
            mock_host_agent_class.return_value = mock_host_agent
            self.server_manager.host_agent = mock_host_agent

            # Test synchronous stop
            if self.server_manager.host_agent:
                self.server_manager.host_agent.stop_server()

            mock_host_agent.stop_server.assert_called_once()

    def test_root_endpoint(self):
        """Test the root endpoint."""
        client = TestClient(self.server_manager.get_app())
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "A2A Prototype Server"
        assert data["version"] == "1.0.0"
        assert data["status"] == "running"

    def test_health_endpoint(self):
        """Test the health check endpoint."""
        client = TestClient(self.server_manager.get_app())
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "agents" in data

    def test_query_endpoint_success(self):
        """Test successful query execution."""
        with patch("src.servers.a2a.a2a_server.DataAgent") as mock_data_agent_class:
            mock_data_agent = Mock()
            mock_data_agent.process_query.return_value = "Query response"
            mock_data_agent_class.return_value = mock_data_agent
            self.server_manager.data_agent = mock_data_agent

            client = TestClient(self.server_manager.get_app())
            response = client.post(
                "/query",
                json={"query": "SELECT * FROM test_table", "agent_id": "data-agent"},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["response"] == "Query response"
            assert data["agent_id"] == "data-agent"
            assert data["status"] == "success"

    def test_query_endpoint_no_agent(self):
        """Test query endpoint when data agent is not available."""
        client = TestClient(self.server_manager.get_app())
        response = client.post("/query", json={"query": "SELECT * FROM test_table"})

        assert response.status_code == 500
        data = response.json()
        assert "Data agent not available" in data["detail"]

    def test_query_endpoint_error(self):
        """Test query endpoint error handling."""
        with patch("src.servers.a2a.a2a_server.DataAgent") as mock_data_agent_class:
            mock_data_agent = Mock()
            mock_data_agent.process_query.side_effect = Exception("Query failed")
            mock_data_agent_class.return_value = mock_data_agent
            self.server_manager.data_agent = mock_data_agent

            client = TestClient(self.server_manager.get_app())
            response = client.post("/query", json={"query": "INVALID SQL"})

            assert response.status_code == 500
            data = response.json()
            assert "Query failed" in data["detail"]

    def test_list_agents_endpoint(self):
        """Test listing all agents."""
        with (
            patch("src.servers.a2a.a2a_server.HostAgent") as mock_host_agent_class,
            patch("src.servers.a2a.a2a_server.DataAgent") as mock_data_agent_class,
        ):

            mock_host_agent = Mock()
            mock_data_agent = Mock()
            mock_host_agent.get_agent_info.return_value = {"agent_id": "host-agent"}
            mock_data_agent.get_agent_info.return_value = {"agent_id": "data-agent"}
            mock_host_agent_class.return_value = mock_host_agent
            mock_data_agent_class.return_value = mock_data_agent

            self.server_manager.host_agent = mock_host_agent
            self.server_manager.data_agent = mock_data_agent

            client = TestClient(self.server_manager.get_app())
            response = client.get("/agents")

            assert response.status_code == 200
            data = response.json()
            assert data["host_agent"]["agent_id"] == "host-agent"
            assert data["data_agent"]["agent_id"] == "data-agent"

    def test_get_agent_info_endpoint_host(self):
        """Test getting host agent information."""
        with patch("src.servers.a2a.a2a_server.HostAgent") as mock_host_agent_class:
            mock_host_agent = Mock()
            mock_host_agent.get_agent_info.return_value = {"agent_id": "host-agent"}
            mock_host_agent_class.return_value = mock_host_agent
            self.server_manager.host_agent = mock_host_agent

            client = TestClient(self.server_manager.get_app())
            response = client.get("/agents/host-agent")

            assert response.status_code == 200
            data = response.json()
            assert data["agent_id"] == "host-agent"

    def test_get_agent_info_endpoint_data(self):
        """Test getting data agent information."""
        with patch("src.servers.a2a.a2a_server.DataAgent") as mock_data_agent_class:
            mock_data_agent = Mock()
            mock_data_agent.get_agent_info.return_value = {"agent_id": "data-agent"}
            mock_data_agent_class.return_value = mock_data_agent
            self.server_manager.data_agent = mock_data_agent

            client = TestClient(self.server_manager.get_app())
            response = client.get("/agents/data-agent")

            assert response.status_code == 200
            data = response.json()
            assert data["agent_id"] == "data-agent"

    def test_get_agent_info_endpoint_not_found(self):
        """Test getting information for non-existent agent."""
        client = TestClient(self.server_manager.get_app())
        response = client.get("/agents/non-existent-agent")

        assert response.status_code == 404
        data = response.json()
        assert "Agent not found" in data["detail"]
