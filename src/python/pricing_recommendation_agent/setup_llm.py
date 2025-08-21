#!/usr/bin/env python3
"""
LLM Setup Script for Pricing Recommendation Agent

This script helps users configure their preferred LLM provider for the chat functionality.
"""

import os
import sys
from typing import Optional


def check_openai_setup() -> bool:
    """Check if OpenAI is properly configured."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OpenAI API key not found")
        return False

    print("✅ OpenAI API key found")
    return True


def check_bedrock_setup() -> bool:
    """Check if AWS Bedrock is properly configured."""
    access_key = os.getenv("AWS_ACCESS_KEY_ID")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
    model_id = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-sonnet-20240229-v1:0")

    if not access_key or not secret_key:
        print("❌ AWS Bedrock credentials not found")
        return False

    print("✅ AWS Bedrock credentials found")
    print(f"   Region: {region}")
    print(f"   Model: {model_id}")
    return True


def get_current_provider() -> str:
    """Get the currently configured LLM provider."""
    return os.getenv("LLM_PROVIDER", "openai").lower()


def setup_openai():
    """Set up OpenAI configuration."""
    print("\n🔧 Setting up OpenAI...")

    api_key = input("Enter your OpenAI API key: ").strip()
    if not api_key:
        print("❌ API key cannot be empty")
        return False

    # Set environment variables
    os.environ["OPENAI_API_KEY"] = api_key
    os.environ["LLM_PROVIDER"] = "openai"

    print("✅ OpenAI configuration set")
    print("   To make this permanent, add to your shell profile:")
    print(f"   export OPENAI_API_KEY='{api_key}'")
    print("   export LLM_PROVIDER='openai'")

    return True


def setup_bedrock():
    """Set up AWS Bedrock configuration."""
    print("\n🔧 Setting up AWS Bedrock...")

    access_key = input("Enter your AWS Access Key ID: ").strip()
    secret_key = input("Enter your AWS Secret Access Key: ").strip()
    region = input("Enter AWS region (default: us-east-1): ").strip() or "us-east-1"

    # Model selection
    print("\nAvailable Bedrock models:")
    models = [
        (
            "1",
            "anthropic.claude-3-sonnet-20240229-v1:0",
            "Claude 3 Sonnet (Recommended)",
        ),
        (
            "2",
            "anthropic.claude-3-haiku-20240307-v1:0",
            "Claude 3 Haiku (Fast & Cost-effective)",
        ),
        ("3", "amazon.titan-text-express-v1", "Titan Text (Amazon's model)"),
        ("4", "ai21.j2-ultra-v1", "Jurassic-2 Ultra (AI21's model)"),
    ]

    for num, model_id, description in models:
        print(f"   {num}. {model_id} - {description}")

    choice = input("\nSelect model (1-4, default: 1): ").strip() or "1"

    try:
        model_id = models[int(choice) - 1][1]
    except (ValueError, IndexError):
        model_id = models[0][1]
        print(f"Invalid choice, using default: {model_id}")

    if not access_key or not secret_key:
        print("❌ Access key and secret key cannot be empty")
        return False

    # Set environment variables
    os.environ["AWS_ACCESS_KEY_ID"] = access_key
    os.environ["AWS_SECRET_ACCESS_KEY"] = secret_key
    os.environ["AWS_DEFAULT_REGION"] = region
    os.environ["BEDROCK_MODEL_ID"] = model_id
    os.environ["LLM_PROVIDER"] = "bedrock"

    print("✅ AWS Bedrock configuration set")
    print("   To make this permanent, add to your shell profile:")
    print(f"   export AWS_ACCESS_KEY_ID='{access_key}'")
    print(f"   export AWS_SECRET_ACCESS_KEY='{secret_key}'")
    print(f"   export AWS_DEFAULT_REGION='{region}'")
    print(f"   export BEDROCK_MODEL_ID='{model_id}'")
    print("   export LLM_PROVIDER='bedrock'")

    return True


def test_configuration():
    """Test the current LLM configuration."""
    provider = get_current_provider()
    print(f"\n🧪 Testing {provider.upper()} configuration...")

    if provider == "openai":
        if not check_openai_setup():
            print("❌ OpenAI configuration test failed")
            return False

        try:
            import openai

            client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

            # Simple test
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello, this is a test."}],
                max_tokens=10,
            )

            print("✅ OpenAI connection test successful")
            return True

        except Exception as e:
            print(f"❌ OpenAI connection test failed: {str(e)}")
            return False

    elif provider == "bedrock":
        if not check_bedrock_setup():
            print("❌ AWS Bedrock configuration test failed")
            return False

        try:
            import boto3
            import json

            bedrock_client = boto3.client(
                service_name="bedrock-runtime",
                region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            )

            model_id = os.getenv(
                "BEDROCK_MODEL_ID", "anthropic.claude-3-sonnet-20240229-v1:0"
            )

            # Simple test
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 10,
                "messages": [{"role": "user", "content": "Hello, this is a test."}],
            }

            response = bedrock_client.invoke_model(
                modelId=model_id, body=json.dumps(body)
            )

            print("✅ AWS Bedrock connection test successful")
            return True

        except Exception as e:
            print(f"❌ AWS Bedrock connection test failed: {str(e)}")
            return False

    else:
        print(f"❌ Unknown provider: {provider}")
        return False


def main():
    """Main setup function."""
    print("🤖 LLM Setup for Pricing Recommendation Agent")
    print("=" * 50)

    # Check current status
    print("\n📋 Current Configuration:")
    current_provider = get_current_provider()
    print(f"   Provider: {current_provider.upper()}")

    if current_provider == "openai":
        check_openai_setup()
    elif current_provider == "bedrock":
        check_bedrock_setup()

    # Setup options
    print("\n🔧 Setup Options:")
    print("   1. Configure OpenAI")
    print("   2. Configure AWS Bedrock")
    print("   3. Test current configuration")
    print("   4. Exit")

    choice = input("\nSelect option (1-4): ").strip()

    if choice == "1":
        if setup_openai():
            test_configuration()

    elif choice == "2":
        if setup_bedrock():
            test_configuration()

    elif choice == "3":
        test_configuration()

    elif choice == "4":
        print("👋 Setup complete!")
        return

    else:
        print("❌ Invalid choice")
        return

    print("\n🎉 Setup complete!")
    print("\nNext steps:")
    print("1. Start the MCP server: python mcp_server.py")
    print("2. Launch the Streamlit UI: streamlit run streamlit_ui.py")
    print("3. Navigate to the 'Chat Assistant' page")
    print("4. Start chatting with your configured LLM!")


if __name__ == "__main__":
    main()
