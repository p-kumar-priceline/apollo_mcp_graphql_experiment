"""
Configuration management for A2A prototype.
Handles AWS credentials, Bedrock settings, and Athena configuration.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class AWSSettings(BaseSettings):
    """AWS configuration settings."""

    aws_region: str = Field(
        "us-east-1", json_schema_extra={"env": "AWS_DEFAULT_REGION"}
    )

    model_config = {"env_file": ".env"}


class BedrockSettings(BaseSettings):
    """AWS Bedrock LLM configuration."""

    model_id: str = Field(
        "us.anthropic.claude-sonnet-4-20250514-v1:0",
        json_schema_extra={"env": "BEDROCK_MODEL_ID"},
    )
    max_tokens: int = Field(2000, json_schema_extra={"env": "BEDROCK_MAX_TOKENS"})
    temperature: float = Field(0.7, json_schema_extra={"env": "BEDROCK_TEMPERATURE"})

    model_config = {"env_file": ".env"}


class AthenaSettings(BaseSettings):
    """AWS Athena configuration."""

    database: str = Field("default", json_schema_extra={"env": "ATHENA_DATABASE"})
    s3_output_location: str = Field(
        "s3://aws-athena-genai/athena-results/",
        json_schema_extra={"env": "ATHENA_S3_OUTPUT"},
    )
    workgroup: str = Field("primary", json_schema_extra={"env": "ATHENA_WORKGROUP"})

    model_config = {"env_file": ".env"}


class A2ASettings(BaseSettings):
    """A2A server configuration."""

    host: str = Field("localhost", json_schema_extra={"env": "A2A_HOST"})
    port: int = Field(8000, json_schema_extra={"env": "A2A_PORT"})
    agent_id: str = Field("host-agent", json_schema_extra={"env": "A2A_AGENT_ID"})

    model_config = {"env_file": ".env"}


class Settings:
    """Main settings container."""

    def __init__(self):
        self.aws = AWSSettings(aws_region="us-east-1")
        self.bedrock = BedrockSettings(
            model_id="us.anthropic.claude-sonnet-4-20250514-v1:0",
            max_tokens=2000,
            temperature=0.7,
        )
        self.athena = AthenaSettings(
            database="sampledb",
            s3_output_location="s3://aws-athena-genai/athena-results/",
            workgroup="primary",
        )
        self.a2a = A2ASettings(host="localhost", port=8000, agent_id="host-agent")


# Global settings instance
settings = Settings()
