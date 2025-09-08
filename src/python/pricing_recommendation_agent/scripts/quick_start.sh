#!/bin/bash

# Pricing Recommendation Agent - Quick Start Script
# This script automates the setup and launch process

set -e  # Exit on any error

echo "🚀 Pricing Recommendation Agent - Quick Start"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is installed
check_python() {
    print_status "Checking Python installation..."
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        print_error "Python is not installed. Please install Python 3.8+ and try again."
        exit 1
    fi
    
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
    print_success "Found Python: $PYTHON_VERSION"
}

# Check if pip is installed
check_pip() {
    print_status "Checking pip installation..."
    if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
        print_error "pip is not installed. Please install pip and try again."
        exit 1
    fi
    print_success "pip is available"
}

# Install dependencies
install_dependencies() {
    print_status "Installing dependencies..."
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        print_success "Dependencies installed successfully"
    else
        print_warning "requirements.txt not found, installing core dependencies..."
        pip install fastapi uvicorn streamlit pandas numpy plotly requests boto3 openai python-dotenv
        print_success "Core dependencies installed"
    fi
}

# Setup configuration
setup_config() {
    print_status "Setting up configuration..."
    
    # Prefer TOML configuration
    if [ ! -f "config.toml" ]; then
        if [ -f "config/config.toml.example" ]; then
            cp config/config.toml.example config.toml
            print_success "Created config.toml file from template"
            print_warning "Please edit config.toml file with your credentials before continuing"
        elif [ -f "config/config.env.example" ]; then
            cp config/config.env.example .env
            print_success "Created .env file from template"
            print_warning "Please edit .env file with your credentials before continuing"
        else
            print_error "No configuration template found (config/config.toml.example or config/config.env.example)"
            exit 1
        fi
    else
        print_success "config.toml file already exists"
    fi
    
    # Test configuration if setup script exists
    if [ -f "scripts/setup_config.py" ]; then
        print_status "Testing configuration..."
        $PYTHON_CMD scripts/setup_config.py test
    fi
}

# Start MCP server
start_mcp_server() {
    print_status "Starting MCP server..."
    
    # Check if server is already running
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        print_success "MCP server is already running"
        return 0
    fi
    
    # Start server in background
    nohup $PYTHON_CMD server/mcp_server.py > mcp_server.log 2>&1 &
    MCP_PID=$!
    
    # Wait for server to start
    print_status "Waiting for MCP server to start..."
    for i in {1..30}; do
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            print_success "MCP server started successfully (PID: $MCP_PID)"
            return 0
        fi
        sleep 1
    done
    
    print_error "MCP server failed to start. Check mcp_server.log for details."
    exit 1
}

# Start Streamlit UI
start_streamlit() {
    print_status "Starting Streamlit UI..."
    
    # Check if Streamlit is already running
    if curl -s http://localhost:8501 > /dev/null 2>&1; then
        print_success "Streamlit UI is already running"
        return 0
    fi
    
    # Start Streamlit in background
    nohup streamlit run ui/streamlit_ui.py --server.port 8501 > streamlit.log 2>&1 &
    STREAMLIT_PID=$!
    
    # Wait for Streamlit to start
    print_status "Waiting for Streamlit UI to start..."
    for i in {1..30}; do
        if curl -s http://localhost:8501 > /dev/null 2>&1; then
            print_success "Streamlit UI started successfully (PID: $STREAMLIT_PID)"
            return 0
        fi
        sleep 1
    done
    
    print_error "Streamlit UI failed to start. Check streamlit.log for details."
    exit 1
}

# Show status
show_status() {
    echo ""
    echo "🎉 Setup Complete!"
    echo "=================="
    echo ""
    echo "Services Status:"
    echo "• MCP Server: http://localhost:8000"
    echo "• Streamlit UI: http://localhost:8501"
    echo "• API Docs: http://localhost:8000/docs"
    echo ""
    echo "Next Steps:"
    echo "1. Open http://localhost:8501 in your browser"
    echo "2. Navigate to 'Chat Assistant' to test LLM connectivity"
    echo "3. Configure your LLM credentials in .env file if needed"
    echo ""
    echo "Logs:"
    echo "• MCP Server: mcp_server.log"
    echo "• Streamlit: streamlit.log"
    echo ""
    echo "To stop services:"
    echo "• MCP Server: kill $MCP_PID"
    echo "• Streamlit: kill $STREAMLIT_PID"
    echo ""
}

# Main execution
main() {
    check_python
    check_pip
    install_dependencies
    setup_config
    
    # Ask user if they want to start services
    echo ""
    read -p "Do you want to start the MCP server and Streamlit UI now? (y/n): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        start_mcp_server
        start_streamlit
        show_status
    else
        echo ""
        print_status "Setup complete. To start services manually:"
        echo "1. Start MCP server: $PYTHON_CMD server/mcp_server.py"
        echo "2. Start Streamlit UI: streamlit run ui/streamlit_ui.py"
    fi
}

# Handle script arguments
case "${1:-}" in
    "install")
        check_python
        check_pip
        install_dependencies
        print_success "Installation complete"
        ;;
    "config")
        setup_config
        ;;
    "server")
        start_mcp_server
        ;;
    "ui")
        start_streamlit
        ;;
    "status")
        echo "Checking service status..."
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            print_success "MCP Server: Running"
        else
            print_error "MCP Server: Not running"
        fi
        
        if curl -s http://localhost:8501 > /dev/null 2>&1; then
            print_success "Streamlit UI: Running"
        else
            print_error "Streamlit UI: Not running"
        fi
        ;;
    "stop")
        echo "Stopping services..."
        pkill -f "mcp_server.py" || true
        pkill -f "streamlit" || true
        print_success "Services stopped"
        ;;
    "help"|"-h"|"--help")
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  install    - Install dependencies only"
        echo "  config     - Setup configuration only"
        echo "  server     - Start MCP server only"
        echo "  ui         - Start Streamlit UI only"
        echo "  status     - Check service status"
        echo "  stop       - Stop all services"
        echo "  help       - Show this help message"
        echo ""
        echo "If no command is provided, runs the full setup and startup process."
        ;;
    "")
        main
        ;;
    *)
        print_error "Unknown command: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac 