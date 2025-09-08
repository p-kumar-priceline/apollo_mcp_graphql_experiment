#!/usr/bin/env python3
"""
Test script for TOML configuration system

This script tests the TOML configuration loading and validation.
"""

import os
import sys
from pathlib import Path

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.config import ConfigManager, get_config


def test_toml_loading():
    """Test TOML configuration loading."""
    print("🧪 Testing TOML Configuration Loading")
    print("=" * 40)

    # Test with TOML file
    config_path = Path("config.toml")
    if config_path.exists():
        print("✅ Found config.toml file")

        config = ConfigManager("config.toml")
        summary = config.get_config_summary()

        print(f"Config Source: {summary.get('config_source', 'Unknown')}")
        print(f"LLM Provider: {summary['llm_provider']}")
        print(f"Server URL: {summary['server_url']}")

        validation = config.validate_llm_config()
        if validation["is_valid"]:
            print("✅ Configuration is valid")
        else:
            print("❌ Configuration has issues:")
            for issue in validation["issues"]:
                print(f"  - {issue}")
    else:
        print("❌ config.toml file not found")
        return False

    return True


def test_environment_fallback():
    """Test environment variable fallback."""
    print("\n🧪 Testing Environment Variable Fallback")
    print("=" * 40)

    # Test with non-existent TOML file
    config = ConfigManager("nonexistent.toml")
    summary = config.get_config_summary()

    print(f"Config Source: {summary.get('config_source', 'Unknown')}")
    print(f"LLM Provider: {summary['llm_provider']}")
    print(f"Server URL: {summary['server_url']}")

    return True


def test_config_saving():
    """Test saving configuration to TOML."""
    print("\n🧪 Testing Configuration Saving")
    print("=" * 40)

    config = get_config()

    # Test saving to a temporary file
    test_file = "test_config.toml"
    if config.save_to_toml(test_file):
        print(f"✅ Successfully saved configuration to {test_file}")

        # Test loading the saved configuration
        test_config = ConfigManager(test_file)
        summary = test_config.get_config_summary()
        print(f"✅ Successfully loaded saved configuration")
        print(f"Config Source: {summary.get('config_source', 'Unknown')}")

        # Clean up
        try:
            os.remove(test_file)
            print(f"✅ Cleaned up {test_file}")
        except:
            pass

        return True
    else:
        print("❌ Failed to save configuration")
        return False


def main():
    """Run all tests."""
    print("🚀 TOML Configuration System Tests")
    print("=" * 50)

    tests = [
        ("TOML Loading", test_toml_loading),
        ("Environment Fallback", test_environment_fallback),
        ("Configuration Saving", test_config_saving),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results.append((test_name, False))

    # Summary
    print("\n📊 Test Results")
    print("=" * 20)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed!")
        return True
    else:
        print("⚠️ Some tests failed. Check the output above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
