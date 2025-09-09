#!/usr/bin/env python3
"""
Test script to verify the A2A prototype setup.
This script tests the basic functionality without requiring AWS credentials.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def test_imports():
    """Test that all modules can be imported successfully."""
    print("Testing imports...")

    try:
        from src.config import settings

        print("✅ Configuration module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import configuration: {e}")
        return False

    try:
        from src.agents import HostAgent, DataAgent

        print("✅ Agent modules imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import agents: {e}")
        return False

    try:
        from src.tools import AthenaQueryTool

        print("✅ Tool modules imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import tools: {e}")
        return False

    try:
        from src.servers import A2AServerManager

        print("✅ Server modules imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import servers: {e}")
        return False

    return True


def test_configuration():
    """Test configuration loading."""
    print("\nTesting configuration...")

    try:
        from src.config import settings

        # Test that settings are loaded
        assert hasattr(settings, "aws")
        assert hasattr(settings, "bedrock")
        assert hasattr(settings, "athena")
        assert hasattr(settings, "a2a")

        print("✅ Configuration loaded successfully")
        print(f"   - AWS Region: {settings.aws.aws_region}")
        print(f"   - Bedrock Model: {settings.bedrock.model_id}")
        print(f"   - Athena Database: {settings.athena.database}")
        print(f"   - A2A Host: {settings.a2a.host}:{settings.a2a.port}")

        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


def test_agent_creation():
    """Test agent creation (without starting services)."""
    print("\nTesting agent creation...")

    try:
        from src.agents import HostAgent, DataAgent
        from unittest.mock import patch

        # Test host agent creation
        with patch("src.agents.host.host_agent.A2AServer"):
            host_agent = HostAgent("test-host")
            assert host_agent.agent_id == "test-host"
            print("✅ Host agent created successfully")

        # Test data agent creation
        with (
            patch("src.agents.data.data_agent.AthenaQueryTool"),
            patch("src.agents.data.data_agent.BedrockLLMProvider"),
            patch("src.agents.data.data_agent.Agent"),
        ):
            data_agent = DataAgent("test-data")
            assert data_agent.agent_id == "test-data"
            print("✅ Data agent created successfully")

        return True
    except Exception as e:
        print(f"❌ Agent creation test failed: {e}")
        return False


def test_server_manager():
    """Test server manager creation."""
    print("\nTesting server manager...")

    try:
        from src.servers import A2AServerManager
        from unittest.mock import patch

        with (
            patch("src.servers.a2a.a2a_server.HostAgent"),
            patch("src.servers.a2a.a2a_server.DataAgent"),
        ):
            server_manager = A2AServerManager()
            assert server_manager.app is not None
            print("✅ Server manager created successfully")

        return True
    except Exception as e:
        print(f"❌ Server manager test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("A2A Prototype Setup Test")
    print("=" * 40)

    tests = [test_imports, test_configuration, test_agent_creation, test_server_manager]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1

    print("\n" + "=" * 40)
    print(f"Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! The A2A prototype is ready to use.")
        print("\nNext steps:")
        print("1. Set up your AWS credentials in .env file")
        print("2. Run: python main.py")
        print("3. Test the API endpoints")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
