#!/usr/bin/env python3
"""
Main entry point for Pricing Recommendation Agent

This script provides a unified interface to run different components of the system:
- MCP Server
- Streamlit UI
- Demo
- Tests
- Configuration setup
"""

import sys
import os
import subprocess
from pathlib import Path

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def run_server():
    """Run the MCP server."""
    print("🚀 Starting MCP Server...")
    server_path = Path(__file__).parent / "server" / "mcp_server.py"
    subprocess.run([sys.executable, str(server_path)])


def run_ui():
    """Run the Streamlit UI."""
    print("🚀 Starting Streamlit UI...")
    ui_path = Path(__file__).parent / "ui" / "streamlit_ui.py"
    subprocess.run(["streamlit", "run", str(ui_path)])


def run_demo():
    """Run the demo script."""
    print("🚀 Running Demo...")
    demo_path = Path(__file__).parent / "scripts" / "demo.py"
    subprocess.run([sys.executable, str(demo_path)])


def run_tests():
    """Run the test suite."""
    print("🧪 Running Tests...")
    test_path = Path(__file__).parent / "tests" / "test_toml_config.py"
    subprocess.run([sys.executable, str(test_path)])


def run_setup():
    """Run the setup script."""
    print("🔧 Running Setup...")
    setup_path = Path(__file__).parent / "scripts" / "setup_config.py"
    subprocess.run([sys.executable, str(setup_path)])


def show_help():
    """Show help information."""
    print("""
🚀 Pricing Recommendation Agent - Main Entry Point

Usage: python main.py [command]

Commands:
  server     - Start the MCP server
  ui         - Start the Streamlit UI
  demo       - Run the demo script
  tests      - Run the test suite
  setup      - Run the setup script
  help       - Show this help message

Examples:
  python main.py server    # Start MCP server
  python main.py ui        # Start Streamlit UI
  python main.py demo      # Run demo
  python main.py tests     # Run tests
  python main.py setup     # Run setup

For more information, see docs/README.md
""")


def main():
    """Main function."""
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == "server":
        run_server()
    elif command == "ui":
        run_ui()
    elif command == "demo":
        run_demo()
    elif command == "tests":
        run_tests()
    elif command == "setup":
        run_setup()
    elif command in ["help", "-h", "--help"]:
        show_help()
    else:
        print(f"❌ Unknown command: {command}")
        print("Use 'python main.py help' for usage information")
        sys.exit(1)


if __name__ == "__main__":
    main() 