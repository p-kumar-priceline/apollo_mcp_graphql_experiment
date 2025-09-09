"""
AWS Athena MCP tool for executing SQL queries.
Provides data access capabilities for the data agent.
"""

import boto3
from typing import Dict, Any, List
from fastmcp import FastMCP
from ...config import settings


class AthenaQueryTool:
    """
    MCP tool for executing AWS Athena queries.

    This tool provides a standardized interface for the data agent
    to query data from AWS Athena.
    """

    def __init__(self):
        """Initialize the Athena client with AWS credentials."""
        session = boto3.Session(profile_name="dev", region_name=settings.aws.aws_region)

        self.client = session.client("athena")
        self.database = settings.athena.database
        self.s3_output_location = settings.athena.s3_output_location
        self.workgroup = settings.athena.workgroup

    def execute_query(self, query: str) -> Dict[str, Any]:
        """
        Execute a SQL query against AWS Athena.

        Args:
            query: SQL query string to execute

        Returns:
            Dictionary containing query results and metadata

        Raises:
            Exception: If query execution fails
        """
        try:
            # Start query execution
            response = self.client.start_query_execution(
                QueryString=query,
                QueryExecutionContext={"Database": self.database},
                ResultConfiguration={"OutputLocation": self.s3_output_location},
                WorkGroup=self.workgroup,
            )

            query_execution_id = response["QueryExecutionId"]

            # Wait for query completion
            self._wait_for_completion(query_execution_id)

            # Get query results
            results = self._get_query_results(query_execution_id)

            return {
                "query_execution_id": query_execution_id,
                "status": "SUCCEEDED",
                "results": results,
                "query": query,
            }

        except Exception as e:
            return {"status": "FAILED", "error": str(e), "query": query}

    def _wait_for_completion(
        self, query_execution_id: str, max_wait_time: int = 300
    ) -> None:
        """
        Wait for query execution to complete.

        Args:
            query_execution_id: Athena query execution ID
            max_wait_time: Maximum time to wait in seconds
        """
        import time

        start_time = time.time()
        while time.time() - start_time < max_wait_time:
            response = self.client.get_query_execution(
                QueryExecutionId=query_execution_id
            )

            status = response["QueryExecution"]["Status"]["State"]

            if status in ["SUCCEEDED", "FAILED", "CANCELLED"]:
                if status != "SUCCEEDED":
                    raise Exception(f"Query failed with status: {status}")
                return

            time.sleep(2)

        raise Exception("Query execution timed out")

    def _get_query_results(self, query_execution_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve query results from Athena.

        Args:
            query_execution_id: Athena query execution ID

        Returns:
            List of dictionaries representing query results
        """
        response = self.client.get_query_results(QueryExecutionId=query_execution_id)

        # Parse results
        columns = [
            col["Name"]
            for col in response["ResultSet"]["ResultSetMetadata"]["ColumnInfo"]
        ]
        rows = []

        for row in response["ResultSet"]["Rows"][1:]:  # Skip header row
            row_data = {}
            for i, col in enumerate(columns):
                if i < len(row["Data"]):
                    row_data[col] = row["Data"][i].get("VarCharValue", "")
                else:
                    row_data[col] = ""
            rows.append(row_data)

        return rows


def create_athena_mcp_tool() -> FastMCP:
    """
    Create and configure the Athena MCP tool.

    Returns:
        Configured FastMCP instance with Athena query capabilities
    """
    mcp = FastMCP("Athena Query Tool")
    athena_tool = AthenaQueryTool()

    @mcp.tool()
    def query_athena(query: str) -> Dict[str, Any]:
        """
        Execute a SQL query against AWS Athena.

        Args:
            query: SQL query string to execute

        Returns:
            Query results and metadata
        """
        return athena_tool.execute_query(query)

    return mcp
