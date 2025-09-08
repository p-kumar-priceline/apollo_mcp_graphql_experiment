#!/usr/bin/env python3
"""
Setup script for Pricing Recommendation Agent Configuration

This script helps users set up their LLM credentials and test the configuration.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.config import ConfigManager, get_config


def create_config_file() -> bool:
    """Create a config.toml file from the example if it doesn't exist."""
    example_path = Path("config/config.toml.example")
    config_path = Path("config.toml")

    if config_path.exists():
        print("✅ config.toml file already exists")
        return True

    if not example_path.exists():
        print("❌ config.toml.example not found")
        return False

    try:
        with open(example_path, "r") as f:
            content = f.read()

        with open(config_path, "w") as f:
            f.write(content)

        print("✅ Created config.toml file from config.toml.example")
        print("📝 Please edit config.toml file with your credentials")
        return True

    except Exception as e:
        print(f"❌ Error creating config.toml file: {e}")
        return False


def create_env_file() -> bool:
    """Create a .env file from the example if it doesn't exist."""
    example_path = Path("config/config.env.example")
    env_path = Path(".env")

    if env_path.exists():
        print("✅ .env file already exists")
        return True

    if not example_path.exists():
        print("❌ config.env.example not found")
        return False

    try:
        with open(example_path, "r") as f:
            content = f.read()

        with open(env_path, "w") as f:
            f.write(content)

        print("✅ Created .env file from config.env.example")
        print("📝 Please edit .env file with your credentials")
        return True

    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False


def load_config_file() -> bool:
    """Load configuration from TOML file or .env file."""
    config_path = Path("config.toml")
    env_path = Path(".env")

    # Try TOML first
    if config_path.exists():
        print("✅ Found config.toml file")
        return True

    # Fall back to .env file
    if env_path.exists():
        try:
            with open(env_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        os.environ[key] = value

            print("✅ Loaded environment variables from .env file")
            return True

        except Exception as e:
            print(f"❌ Error loading .env file: {e}")
            return False

    print("❌ No configuration file found (config.toml or .env)")
    return False


def load_env_file() -> bool:
    """Load environment variables from .env file."""
    env_path = Path(".env")

    if not env_path.exists():
        print("❌ .env file not found")
        return False

    try:
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key] = value

        print("✅ Loaded environment variables from .env file")
        return True

    except Exception as e:
        print(f"❌ Error loading .env file: {e}")
        return False


def test_llm_configuration() -> Dict[str, Any]:
    """Test the LLM configuration and return results."""
    config = get_config()
    validation = config.validate_llm_config()

    print("\n🔍 Testing LLM Configuration...")
    print(f"Provider: {validation['provider'].upper()}")

    if validation["is_valid"]:
        print("✅ Configuration is valid")

        if validation["provider"] == "openai":
            print(f"Model: {config.llm_config.openai_model}")
            print(f"Max Tokens: {config.llm_config.openai_max_tokens}")
            print(f"Temperature: {config.llm_config.openai_temperature}")

        elif validation["provider"] == "bedrock":
            print(f"Model: {config.llm_config.bedrock_model_id}")
            print(f"Region: {config.llm_config.aws_region}")
            print(f"Max Tokens: {config.llm_config.bedrock_max_tokens}")
            print(f"Temperature: {config.llm_config.bedrock_temperature}")

    else:
        print("❌ Configuration has issues:")
        for issue in validation["issues"]:
            print(f"  - {issue}")

    return validation


def test_bedrock_connection() -> bool:
    """Test AWS Bedrock connection."""
    try:
        import boto3
        from botocore.exceptions import ClientError, NoCredentialsError

        config = get_config()

        if config.llm_config.provider != "bedrock":
            print("⏭️  Skipping Bedrock test (not configured as provider)")
            return True

        print("\n🔍 Testing AWS Bedrock Connection...")

        # Test credentials
        if (
            not config.llm_config.aws_access_key_id
            or not config.llm_config.aws_secret_access_key
        ):
            print("❌ AWS credentials not found")
            return False

        # Test Bedrock client creation
        bedrock_client = boto3.client(
            service_name="bedrock-runtime",
            region_name=config.llm_config.aws_region,
            aws_access_key_id=config.llm_config.aws_access_key_id,
            aws_secret_access_key=config.llm_config.aws_secret_access_key,
        )

        # Test model availability (list models)
        try:
            bedrock_client.list_foundation_models()
            print("✅ Bedrock connection successful")
            return True

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "AccessDeniedException":
                print("❌ Access denied. Check your AWS credentials and permissions.")
            elif error_code == "ValidationException":
                print("❌ Invalid model ID or region.")
            else:
                print(f"❌ Bedrock error: {error_code}")
            return False

    except ImportError:
        print("❌ boto3 not installed. Install with: pip install boto3")
        return False
    except Exception as e:
        print(f"❌ Error testing Bedrock connection: {e}")
        return False


def test_openai_connection() -> bool:
    """Test OpenAI connection."""
    try:
        import openai

        config = get_config()

        if config.llm_config.provider != "openai":
            print("⏭️  Skipping OpenAI test (not configured as provider)")
            return True

        print("\n🔍 Testing OpenAI Connection...")

        if not config.llm_config.openai_api_key:
            print("❌ OpenAI API key not found")
            return False

        # Test OpenAI client
        client = openai.OpenAI(api_key=config.llm_config.openai_api_key)

        # Test with a simple request
        try:
            response = client.chat.completions.create(
                model=config.llm_config.openai_model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10,
                temperature=0,
            )
            print("✅ OpenAI connection successful")
            return True

        except Exception as e:
            print(f"❌ OpenAI API error: {e}")
            return False

    except ImportError:
        print("❌ openai not installed. Install with: pip install openai")
        return False
    except Exception as e:
        print(f"❌ Error testing OpenAI connection: {e}")
        return False


def show_configuration_summary():
    """Show a summary of the current configuration."""
    config = get_config()
    summary = config.get_config_summary()

    print("\n📋 Configuration Summary:")
    print(f"Config Source: {summary.get('config_source', 'Unknown')}")
    print(f"LLM Provider: {summary['llm_provider'].upper()}")
    print(f"Server URL: {summary['server_url']}")

    print("\nAvailable Models:")
    for provider, models in summary["available_models"].items():
        print(f"  {provider.upper()}:")
        for model in models[:3]:  # Show first 3 models
            print(f"    - {model}")
        if len(models) > 3:
            print(f"    ... and {len(models) - 3} more")


def interactive_setup():
    """Interactive setup process."""
    print("🚀 Pricing Recommendation Agent Configuration Setup")
    print("=" * 50)

    # Step 1: Create config file (prefer TOML)
    print("\nStep 1: Configuration File Setup")
    if not create_config_file():
        if not create_env_file():
            return False

    # Step 2: Load configuration
    print("\nStep 2: Loading Configuration")
    if not load_config_file():
        return False

    # Step 3: Test configuration
    print("\nStep 3: Testing Configuration")
    validation = test_llm_configuration()

    if not validation["is_valid"]:
        print("\n❌ Configuration issues found. Please fix them and run again.")
        return False

    # Step 4: Test connections
    print("\nStep 4: Testing Connections")
    bedrock_ok = test_bedrock_connection()
    openai_ok = test_openai_connection()

    # Step 5: Show summary
    show_configuration_summary()

    # Final status
    if validation["is_valid"] and (bedrock_ok or openai_ok):
        print("\n✅ Setup completed successfully!")
        print("\nNext steps:")
        print("1. Start the MCP server: python server/mcp_server.py")
        print("2. Start the Streamlit UI: streamlit run ui/streamlit_ui.py")
        print("3. Open your browser to http://localhost:8501")
        return True
    else:
        print("\n❌ Setup completed with issues. Please check the errors above.")
        return False


def main():
    """Main function."""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "test":
            # Just test the current configuration
            load_env_file()
            test_llm_configuration()
            test_bedrock_connection()
            test_openai_connection()
            show_configuration_summary()

        elif command == "summary":
            # Show configuration summary
            load_env_file()
            show_configuration_summary()

        elif command == "create-env":
            # Just create the .env file
            create_env_file()
        elif command == "create-toml":
            # Just create the config.toml file
            create_config_file()

        else:
            print(f"Unknown command: {command}")
            print("Available commands: test, summary, create-env, create-toml")
            return False
    else:
        # Interactive setup
        return interactive_setup()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
