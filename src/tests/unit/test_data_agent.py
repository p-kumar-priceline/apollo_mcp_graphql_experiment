"""
Unit tests for data agent.
Tests the data agent functionality with Google ADK and AWS Bedrock.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from unittest.mock import Mock, patch, MagicMock
from src.agents.data import DataAgent, BedrockLLMProvider


class TestBedrockLLMProvider:
    """Test cases for BedrockLLMProvider."""

    def setup_method(self):
        """Set up test fixtures."""
        with patch("src.agents.data.data_agent.boto3.Session.client"):
            self.provider = BedrockLLMProvider()

    @patch("src.agents.data.data_agent.boto3.Session.client")
    def test_init(self, mock_boto_client):
        """Test BedrockLLMProvider initialization."""
        mock_client = Mock()
        mock_boto_client.return_value = mock_client

        provider = BedrockLLMProvider()

        assert provider.client == mock_client
        assert provider.model_id == "us.anthropic.claude-sonnet-4-20250514-v1:0"

    @patch("src.agents.data.data_agent.boto3.Session.client")
    def test_generate_success(self, mock_boto_client):
        """Test successful response generation."""
        mock_client = Mock()
        mock_boto_client.return_value = mock_client

        # Mock successful response
        mock_response = {"body": Mock()}
        mock_response["body"].read.return_value = (
            b'{"content": [{"text": "Test response"}]}'
        )
        mock_client.invoke_model.return_value = mock_response

        provider = BedrockLLMProvider()
        response = provider.generate("Test prompt")

        assert response == "Test response"
        mock_client.invoke_model.assert_called_once()

    @patch("src.agents.data.data_agent.boto3.Session.client")
    def test_generate_failure(self, mock_boto_client):
        """Test response generation failure."""
        mock_client = Mock()
        mock_boto_client.return_value = mock_client

        # Mock failure
        mock_client.invoke_model.side_effect = Exception("API Error")

        provider = BedrockLLMProvider()
        response = provider.generate("Test prompt")

        assert "Error generating response" in response


class TestDataAgent:
    """Test cases for DataAgent."""

    def setup_method(self):
        """Set up test fixtures."""
        with (
            patch("src.agents.data.data_agent.AthenaQueryTool"),
            patch("src.agents.data.data_agent.BedrockLLMProvider"),
            patch("src.agents.data.data_agent.Agent"),
        ):
            self.data_agent = DataAgent()

    @patch("src.agents.data.data_agent.AthenaQueryTool")
    @patch("src.agents.data.data_agent.BedrockLLMProvider")
    @patch("src.agents.data.data_agent.Agent")
    def test_init(self, mock_agent, mock_llm_provider, mock_athena_tool):
        """Test DataAgent initialization."""
        mock_agent_instance = Mock()
        mock_agent.return_value = mock_agent_instance

        agent = DataAgent("test-agent")

        assert agent.agent_id == "test-agent"
        assert agent.athena_tool == mock_athena_tool.return_value
        assert agent.llm_provider == mock_llm_provider.return_value
        mock_agent.assert_called_once()

    def test_format_results(self):
        """Test result formatting."""
        with (
            patch("src.agents.data.data_agent.AthenaQueryTool"),
            patch("src.agents.data.data_agent.BedrockLLMProvider"),
            patch("src.agents.data.data_agent.Agent"),
        ):

            agent = DataAgent()

            # Test with results
            results = [
                {"id": "1", "name": "John", "age": "25"},
                {"id": "2", "name": "Jane", "age": "30"},
            ]

            formatted = agent._format_results(results)

            assert "| id | name | age |" in formatted
            assert "| 1 | John | 25 |" in formatted
            assert "| 2 | Jane | 30 |" in formatted

    def test_format_results_empty(self):
        """Test formatting of empty results."""
        with (
            patch("src.agents.data.data_agent.AthenaQueryTool"),
            patch("src.agents.data.data_agent.BedrockLLMProvider"),
            patch("src.agents.data.data_agent.Agent"),
        ):

            agent = DataAgent()

            formatted = agent._format_results([])
            assert formatted == "No results found."

    def test_format_results_large_dataset(self):
        """Test formatting of large datasets (truncation)."""
        with (
            patch("src.agents.data.data_agent.AthenaQueryTool"),
            patch("src.agents.data.data_agent.BedrockLLMProvider"),
            patch("src.agents.data.data_agent.Agent"),
        ):

            agent = DataAgent()

            # Create 15 rows of data
            results = [{"id": str(i), "name": f"User{i}"} for i in range(15)]

            formatted = agent._format_results(results)

            assert "... and 5 more rows" in formatted
            assert (
                len([line for line in formatted.split("\n") if "|" in line]) == 12
            )  # 10 data rows + header + separator

    def test_get_agent_info(self):
        """Test agent information retrieval."""
        with (
            patch("src.agents.data.data_agent.AthenaQueryTool"),
            patch("src.agents.data.data_agent.BedrockLLMProvider"),
            patch("src.agents.data.data_agent.Agent"),
        ):

            agent = DataAgent("test-agent")
            info = agent.get_agent_info()

            assert info["agent_id"] == "test-agent"
            assert info["llm_provider"] == "AWS Bedrock"
            assert "athena_query" in info["tools"]
            assert "Execute SQL queries against AWS Athena" in info["capabilities"]

    def test_process_query_success(self):
        """Test successful query processing."""
        with (
            patch("src.agents.data.data_agent.AthenaQueryTool"),
            patch("src.agents.data.data_agent.BedrockLLMProvider"),
            patch("src.agents.data.data_agent.Agent") as mock_agent_class,
        ):

            mock_agent = Mock()
            mock_agent.process.return_value = "Test response"
            mock_agent_class.return_value = mock_agent

            agent = DataAgent()
            response = agent.process_query("Test query")

            assert response == "Test response"
            mock_agent.process.assert_called_once_with("Test query")

    def test_process_query_failure(self):
        """Test query processing failure."""
        with (
            patch("src.agents.data.data_agent.AthenaQueryTool"),
            patch("src.agents.data.data_agent.BedrockLLMProvider"),
            patch("src.agents.data.data_agent.Agent") as mock_agent_class,
        ):

            mock_agent = Mock()
            mock_agent.process.side_effect = Exception("Processing error")
            mock_agent_class.return_value = mock_agent

            agent = DataAgent()
            response = agent.process_query("Test query")

            assert "Error processing query" in response
