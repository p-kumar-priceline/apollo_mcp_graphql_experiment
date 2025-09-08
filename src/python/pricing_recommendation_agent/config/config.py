"""
Configuration file for Pricing Recommendation Agent

This module centralizes configuration settings for AWS Bedrock, OpenAI, and other
LLM providers used by the Streamlit chat UI. Supports both TOML and environment variables.
"""

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass
from pathlib import Path

try:
    import tomllib
except ImportError:
    import tomli as tomllib


@dataclass
class LLMConfig:
    """Configuration for LLM providers."""

    # Provider selection
    provider: str = "openai"  # "openai" or "bedrock"

    # OpenAI configuration
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-3.5-turbo"
    openai_max_tokens: int = 500
    openai_temperature: float = 0.7

    # AWS Bedrock configuration
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region: str = "us-east-1"
    bedrock_model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0"
    bedrock_max_tokens: int = 500
    bedrock_temperature: float = 0.7
    bedrock_top_p: float = 0.9

    # Chat configuration
    system_message: str = """You are an AI assistant for a pricing recommendation agent in the travel industry. 
    You help revenue management teams understand pricing optimization opportunities and provide insights.
    
    Your role is to:
    1. Analyze pricing data and recommendations
    2. Explain statistical findings in business terms
    3. Suggest actions based on recommendations
    4. Answer questions about profitability, volume, availability, and inventory
    5. Provide context and insights for decision-making
    
    Be helpful, professional, and focus on actionable insights."""


@dataclass
class ServerConfig:
    """Configuration for MCP server connection."""

    api_base_url: str = "http://localhost:8000"
    api_timeout: int = 30
    health_check_interval: int = 5


@dataclass
class StreamlitConfig:
    """Configuration for Streamlit UI."""

    page_title: str = "Pricing Recommendation Agent"
    page_icon: str = "📊"
    layout: str = "wide"
    initial_sidebar_state: str = "expanded"


class ConfigManager:
    """Manages configuration loading and validation."""
    
    def __init__(self, config_file: Optional[str] = None):
        self.llm_config = LLMConfig()
        self.server_config = ServerConfig()
        self.streamlit_config = StreamlitConfig()
        self.config_file = config_file or "config.toml"
        self._load_configuration()
    
    def _load_configuration(self):
        """Load configuration from TOML file or environment variables."""
        # Try to load from TOML file first
        if self._load_from_toml():
            return
        
        # Fall back to environment variables
        self._load_from_environment()
    
    def _load_from_toml(self) -> bool:
        """Load configuration from TOML file."""
        config_path = Path(self.config_file)
        
        if not config_path.exists():
            return False
        
        try:
            with open(config_path, "rb") as f:
                config_data = tomllib.load(f)
            
            # Load LLM configuration
            if "llm" in config_data:
                llm_data = config_data["llm"]
                self.llm_config.provider = llm_data.get("provider", "openai").lower()
                
                # Load OpenAI configuration
                if "openai" in llm_data:
                    openai_data = llm_data["openai"]
                    self.llm_config.openai_api_key = openai_data.get("api_key")
                    self.llm_config.openai_model = openai_data.get("model", "gpt-3.5-turbo")
                    self.llm_config.openai_max_tokens = openai_data.get("max_tokens", 500)
                    self.llm_config.openai_temperature = openai_data.get("temperature", 0.7)
                
                # Load Bedrock configuration
                if "bedrock" in llm_data:
                    bedrock_data = llm_data["bedrock"]
                    self.llm_config.aws_access_key_id = bedrock_data.get("aws_access_key_id")
                    self.llm_config.aws_secret_access_key = bedrock_data.get("aws_secret_access_key")
                    self.llm_config.aws_region = bedrock_data.get("aws_region", "us-east-1")
                    self.llm_config.bedrock_model_id = bedrock_data.get(
                        "model_id", "anthropic.claude-3-sonnet-20240229-v1:0"
                    )
                    self.llm_config.bedrock_max_tokens = bedrock_data.get("max_tokens", 500)
                    self.llm_config.bedrock_temperature = bedrock_data.get("temperature", 0.7)
                    self.llm_config.bedrock_top_p = bedrock_data.get("top_p", 0.9)
            
            # Load server configuration
            if "server" in config_data:
                server_data = config_data["server"]
                self.server_config.api_base_url = server_data.get("api_base_url", "http://localhost:8000")
                self.server_config.api_timeout = server_data.get("api_timeout", 30)
                self.server_config.health_check_interval = server_data.get("health_check_interval", 5)
            
            # Load Streamlit configuration
            if "streamlit" in config_data:
                streamlit_data = config_data["streamlit"]
                self.streamlit_config.page_title = streamlit_data.get("page_title", "Pricing Recommendation Agent")
                self.streamlit_config.page_icon = streamlit_data.get("page_icon", "📊")
                self.streamlit_config.layout = streamlit_data.get("layout", "wide")
                self.streamlit_config.initial_sidebar_state = streamlit_data.get("initial_sidebar_state", "expanded")
            
            # Load chat configuration
            if "chat" in config_data:
                chat_data = config_data["chat"]
                self.llm_config.system_message = chat_data.get("system_message", self.llm_config.system_message)
            
            return True
            
        except Exception as e:
            print(f"Warning: Failed to load TOML configuration: {e}")
            return False
    
    def _load_from_environment(self):
        """Load configuration from environment variables."""
        
        # LLM Provider selection
        self.llm_config.provider = os.getenv("LLM_PROVIDER", "openai").lower()
        
        # OpenAI configuration
        self.llm_config.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.llm_config.openai_model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        self.llm_config.openai_max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "500"))
        self.llm_config.openai_temperature = float(
            os.getenv("OPENAI_TEMPERATURE", "0.7")
        )
        
        # AWS Bedrock configuration
        self.llm_config.aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
        self.llm_config.aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.llm_config.aws_region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        self.llm_config.bedrock_model_id = os.getenv(
            "BEDROCK_MODEL_ID", "anthropic.claude-3-sonnet-20240229-v1:0"
        )
        self.llm_config.bedrock_max_tokens = int(os.getenv("BEDROCK_MAX_TOKENS", "500"))
        self.llm_config.bedrock_temperature = float(
            os.getenv("BEDROCK_TEMPERATURE", "0.7")
        )
        self.llm_config.bedrock_top_p = float(os.getenv("BEDROCK_TOP_P", "0.9"))
        
        # Server configuration
        self.server_config.api_base_url = os.getenv(
            "API_BASE_URL", "http://localhost:8000"
        )
        self.server_config.api_timeout = int(os.getenv("API_TIMEOUT", "30"))
        self.server_config.health_check_interval = int(
            os.getenv("HEALTH_CHECK_INTERVAL", "5")
        )

    def validate_llm_config(self) -> Dict[str, Any]:
        """
        Validate LLM configuration and return status.

        Returns:
            Dictionary with validation status and any issues
        """
        issues = []
        is_valid = True

        if self.llm_config.provider == "openai":
            if not self.llm_config.openai_api_key:
                issues.append(
                    "OpenAI API key not found. Set OPENAI_API_KEY environment variable."
                )
                is_valid = False

        elif self.llm_config.provider == "bedrock":
            if not self.llm_config.aws_access_key_id:
                issues.append(
                    "AWS Access Key ID not found. Set AWS_ACCESS_KEY_ID environment variable."
                )
                is_valid = False

            if not self.llm_config.aws_secret_access_key:
                issues.append(
                    "AWS Secret Access Key not found. Set AWS_SECRET_ACCESS_KEY environment variable."
                )
                is_valid = False

        else:
            issues.append(
                f"Unsupported LLM provider: {self.llm_config.provider}. Use 'openai' or 'bedrock'."
            )
            is_valid = False

        return {
            "is_valid": is_valid,
            "provider": self.llm_config.provider,
            "issues": issues,
        }

    def get_available_models(self) -> Dict[str, list]:
        """Get available models for each provider."""
        return {
            "openai": [
                "gpt-3.5-turbo",
                "gpt-3.5-turbo-16k",
                "gpt-4",
                "gpt-4-turbo",
                "gpt-4-turbo-preview",
            ],
            "bedrock": [
                "anthropic.claude-3-sonnet-20240229-v1:0",
                "anthropic.claude-3-haiku-20240307-v1:0",
                "anthropic.claude-3-opus-20240229-v1:0",
                "amazon.titan-text-express-v1",
                "amazon.titan-text-lite-v1",
                "ai21.j2-ultra-v1",
                "ai21.j2-mid-v1",
                "cohere.command-text-v14",
                "cohere.command-light-text-v14",
            ],
        }

        def get_config_summary(self) -> Dict[str, Any]:
        """Get a summary of current configuration."""
        validation = self.validate_llm_config()
        
        return {
            "llm_provider": self.llm_config.provider,
            "llm_validation": validation,
            "server_url": self.server_config.api_base_url,
            "available_models": self.get_available_models(),
            "config_source": "TOML" if Path(self.config_file).exists() else "Environment",
        }
    
    def save_to_toml(self, file_path: Optional[str] = None) -> bool:
        """Save current configuration to TOML file."""
        try:
            import tomli_w
            
            config_data = {
                "llm": {
                    "provider": self.llm_config.provider,
                    "openai": {
                        "api_key": self.llm_config.openai_api_key or "",
                        "model": self.llm_config.openai_model,
                        "max_tokens": self.llm_config.openai_max_tokens,
                        "temperature": self.llm_config.openai_temperature,
                    },
                    "bedrock": {
                        "aws_access_key_id": self.llm_config.aws_access_key_id or "",
                        "aws_secret_access_key": self.llm_config.aws_secret_access_key or "",
                        "aws_region": self.llm_config.aws_region,
                        "model_id": self.llm_config.bedrock_model_id,
                        "max_tokens": self.llm_config.bedrock_max_tokens,
                        "temperature": self.llm_config.bedrock_temperature,
                        "top_p": self.llm_config.bedrock_top_p,
                    },
                },
                "server": {
                    "api_base_url": self.server_config.api_base_url,
                    "api_timeout": self.server_config.api_timeout,
                    "health_check_interval": self.server_config.health_check_interval,
                },
                "streamlit": {
                    "page_title": self.streamlit_config.page_title,
                    "page_icon": self.streamlit_config.page_icon,
                    "layout": self.streamlit_config.layout,
                    "initial_sidebar_state": self.streamlit_config.initial_sidebar_state,
                },
                "chat": {
                    "system_message": self.llm_config.system_message,
                },
            }
            
            output_path = file_path or self.config_file
            with open(output_path, "w") as f:
                tomli_w.dump(config_data, f)
            
            return True
            
        except ImportError:
            print("Warning: tomli-w not installed. Cannot save TOML configuration.")
            return False
        except Exception as e:
            print(f"Error saving TOML configuration: {e}")
            return False


# Global configuration instance
config = ConfigManager()


def get_config() -> ConfigManager:
    """Get the global configuration instance."""
    return config


def reload_config(config_file: Optional[str] = None):
    """Reload configuration from TOML file or environment variables."""
    global config
    config = ConfigManager(config_file)
    return config
