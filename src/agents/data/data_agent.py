"""
Data agent implementation using Google ADK with AWS Bedrock.
Handles data queries and analysis using MCP tools.
"""

import json
import boto3
from typing import Dict, Any, List, Optional, Callable
from abc import ABC, abstractmethod
from ...config import settings
from ...tools.athena import AthenaQueryTool
from botocore.config import Config


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate response from LLM."""
        pass


class Tool:
    """Simple tool class for Google ADK compatibility."""

    def __init__(self, name: str, description: str, function: Callable):
        self.name = name
        self.description = description
        self.function = function

    def run(self, *args, **kwargs):
        """Run the tool function."""
        return self.function(*args, **kwargs)


class Agent:
    """Simple agent class for Google ADK compatibility."""

    def __init__(self, name: str, llm_provider: LLMProvider, tools: List[Tool]):
        self.name = name
        self.llm_provider = llm_provider
        self.tools = {tool.name: tool for tool in tools}

    def process(self, query: str) -> str:
        """Process a query using available tools and LLM."""
        # Simple implementation: use tools if query contains SQL, otherwise use LLM
        if "SELECT" in query.upper() or "FROM" in query.upper():
            # Use Athena tool for SQL queries
            if "athena_query" in self.tools:
                result = self.tools["athena_query"].run(query)
                return f"Query executed: {result}"

        # Use LLM for other queries
        return self.llm_provider.generate(query)


class BedrockLLMProvider(LLMProvider):
    """
    AWS Bedrock LLM provider for Google ADK.

    Integrates Claude models from AWS Bedrock with the ADK framework.
    """

    def __init__(self):
        """Initialize Bedrock client."""

        config = Config(
            retries={
                "max_attempts": 10,
                "mode": "standard",
            }
        )

        session = boto3.Session(profile_name="dev", region_name=settings.aws.aws_region)
        self.client = session.client(
            "bedrock-runtime",
            config=config,
            region_name=settings.aws.aws_region,
        )
        self.model_id = settings.bedrock.model_id

    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate response using AWS Bedrock.

        Args:
            prompt: Input prompt for the LLM
            **kwargs: Additional parameters (temperature, max_tokens, etc.)

        Returns:
            Generated response from the LLM
        """
        try:
            # Prepare the request body for Claude
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": kwargs.get("max_tokens", settings.bedrock.max_tokens),
                "temperature": kwargs.get("temperature", settings.bedrock.temperature),
                "messages": [{"role": "user", "content": prompt}],
            }

            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body),
                contentType="application/json",
            )

            response_body = json.loads(response["body"].read())
            return response_body["content"][0]["text"]

        except Exception as e:
            return f"Error generating response: {str(e)}"


class DataAgent:
    """
    Data agent that uses Google ADK with AWS Bedrock for data analysis.

    This agent can execute SQL queries through MCP tools and provide
    intelligent analysis of the results using AWS Bedrock LLMs.
    """

    def __init__(self, agent_id: str = "data-agent"):
        """
        Initialize the data agent.

        Args:
            agent_id: Unique identifier for the agent
        """
        self.agent_id = agent_id
        self.athena_tool = AthenaQueryTool()
        self.llm_provider = BedrockLLMProvider()

        # Initialize Google ADK agent
        self.agent = Agent(
            name=agent_id,
            llm_provider=self.llm_provider,
            tools=[self._create_athena_tool()],
        )

    def _create_athena_tool(self) -> Tool:
        """
        Create ADK tool wrapper for Athena queries.

        Returns:
            Configured ADK Tool for Athena operations
        """

        def execute_athena_query(query: str) -> str:
            """
            Execute Athena query and return formatted results.

            Args:
                query: SQL query to execute

            Returns:
                Formatted query results
            """
            result = self.athena_tool.execute_query(query)

            if result["status"] == "SUCCEEDED":
                results = result["results"]
                if results:
                    # Format results for LLM consumption
                    formatted_results = self._format_results(results)
                    return f"Query executed successfully. Results:\n{formatted_results}"
                else:
                    return "Query executed successfully but returned no results."
            else:
                return f"Query failed: {result.get('error', 'Unknown error')}"

        return Tool(
            name="athena_query",
            description="Execute SQL queries against AWS Athena database",
            function=execute_athena_query,
        )

    def _format_results(self, results: List[Dict[str, Any]]) -> str:
        """
        Format query results for LLM consumption.

        Args:
            results: List of result dictionaries

        Returns:
            Formatted string representation of results
        """
        if not results:
            return "No results found."

        # Get column names
        columns = list(results[0].keys())

        # Create formatted table
        formatted = "| " + " | ".join(columns) + " |\n"
        formatted += "| " + " | ".join(["---"] * len(columns)) + " |\n"

        for row in results[:10]:  # Limit to first 10 rows
            values = [str(row.get(col, "")) for col in columns]
            formatted += "| " + " | ".join(values) + " |\n"

        if len(results) > 10:
            formatted += f"\n... and {len(results) - 10} more rows"

        return formatted

    def process_query(self, user_query: str) -> str:
        """
        Process a user query using the data agent.

        Args:
            user_query: Natural language query from the user

        Returns:
            Agent's response with data analysis
        """
        try:
            # Use the ADK agent to process the query
            response = self.agent.process(user_query)
            return response

        except Exception as e:
            return f"Error processing query: {str(e)}"

    def get_agent_info(self) -> Dict[str, Any]:
        """
        Get information about the data agent.

        Returns:
            Dictionary containing agent metadata
        """
        return {
            "agent_id": self.agent_id,
            "llm_provider": "AWS Bedrock",
            "model_id": settings.bedrock.model_id,
            "tools": ["athena_query"],
            "capabilities": [
                "Execute SQL queries against AWS Athena",
                "Analyze query results using AWS Bedrock LLM",
                "Provide natural language responses about data",
            ],
        }
