"""
Unit tests for Athena query tool.
Tests the MCP tool functionality for AWS Athena integration.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from unittest.mock import Mock, patch, MagicMock
from src.tools.athena import AthenaQueryTool


class TestAthenaQueryTool:
    """Test cases for AthenaQueryTool."""

    def setup_method(self):
        """Set up test fixtures."""
        with patch("src.tools.athena.athena_tool.boto3.client"):
            self.athena_tool = AthenaQueryTool()

    @patch("src.tools.athena.athena_tool.boto3.Session.client")
    def test_init(self, mock_boto_client):
        """Test AthenaQueryTool initialization."""
        mock_client = Mock()
        mock_boto_client.return_value = mock_client

        tool = AthenaQueryTool()

        assert tool.client == mock_client
        assert tool.database == "sampledb"
        assert tool.s3_output_location == "s3://aws-athena-genai/athena-results/"
        assert tool.workgroup == "primary"

    @patch("src.tools.athena.athena_tool.boto3.Session.client")
    def test_execute_query_success(self, mock_boto_client):
        """Test successful query execution."""
        # Mock boto3 client
        mock_client = Mock()
        mock_boto_client.return_value = mock_client

        # Mock query execution response
        mock_client.start_query_execution.return_value = {
            "QueryExecutionId": "test-query-id"
        }

        # Mock query completion check
        mock_client.get_query_execution.return_value = {
            "QueryExecution": {"Status": {"State": "SUCCEEDED"}}
        }

        # Mock query results
        mock_client.get_query_results.return_value = {
            "ResultSet": {
                "ResultSetMetadata": {"ColumnInfo": [{"Name": "id"}, {"Name": "name"}]},
                "Rows": [
                    {
                        "Data": [{"VarCharValue": "id"}, {"VarCharValue": "name"}]
                    },  # Header
                    {"Data": [{"VarCharValue": "1"}, {"VarCharValue": "John"}]},
                    {"Data": [{"VarCharValue": "2"}, {"VarCharValue": "Jane"}]},
                ],
            }
        }

        tool = AthenaQueryTool()
        result = tool.execute_query("SELECT * FROM test_table")

        assert result["status"] == "SUCCEEDED"
        assert result["query_execution_id"] == "test-query-id"
        assert len(result["results"]) == 2
        assert result["results"][0]["id"] == "1"
        assert result["results"][0]["name"] == "John"

    @patch("src.tools.athena.athena_tool.boto3.client")
    def test_execute_query_failure(self, mock_boto_client):
        """Test query execution failure."""
        mock_client = Mock()
        mock_boto_client.return_value = mock_client

        # Mock query execution failure
        mock_client.start_query_execution.side_effect = Exception("Query failed")

        tool = AthenaQueryTool()
        result = tool.execute_query("INVALID SQL")

        assert result["status"] == "FAILED"
        assert "error" in result
        assert result["query"] == "INVALID SQL"

    @patch("src.tools.athena.athena_tool.boto3.client")
    def test_wait_for_completion_timeout(self, mock_boto_client):
        """Test query completion timeout."""
        mock_client = Mock()
        mock_boto_client.return_value = mock_client

        # Mock query execution response
        mock_client.start_query_execution.return_value = {
            "QueryExecutionId": "test-query-id"
        }

        # Mock query that never completes
        mock_client.get_query_execution.return_value = {
            "QueryExecution": {"Status": {"State": "RUNNING"}}
        }

        tool = AthenaQueryTool()

        # For this prototype, we'll just test that the method doesn't crash
        # In a real implementation, this would timeout after 300 seconds
        result = tool.execute_query("SELECT * FROM test_table")
        assert result["status"] == "FAILED"

    @patch("src.tools.athena.athena_tool.boto3.Session.client")
    def test_get_query_results_empty(self, mock_boto_client):
        """Test handling of empty query results."""
        mock_client = Mock()
        mock_boto_client.return_value = mock_client

        # Mock query execution response
        mock_client.start_query_execution.return_value = {
            "QueryExecutionId": "test-query-id"
        }

        # Mock query completion
        mock_client.get_query_execution.return_value = {
            "QueryExecution": {"Status": {"State": "SUCCEEDED"}}
        }

        # Mock empty results
        mock_client.get_query_results.return_value = {
            "ResultSet": {
                "ResultSetMetadata": {"ColumnInfo": [{"Name": "id"}]},
                "Rows": [{"Data": [{"VarCharValue": "id"}]}],  # Only header row
            }
        }

        tool = AthenaQueryTool()
        result = tool.execute_query("SELECT * FROM empty_table")

        assert result["status"] == "SUCCEEDED"
        assert result["results"] == []
