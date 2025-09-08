# Pricing Recommendation Agent - Project Structure

This document describes the logical organization of the Pricing Recommendation Agent project.

## 📁 Directory Structure

```
pricing_recommendation_agent/
├── main.py                    # Main entry point
├── requirements.txt           # Python dependencies
├── PROJECT_STRUCTURE.md       # This file
│
├── config/                    # Configuration management
│   ├── __init__.py
│   ├── config.py             # Configuration classes and management
│   ├── config.toml.example   # TOML configuration template
│   └── config.env.example    # Environment variables template
│
├── core/                      # Core business logic
│   ├── __init__.py
│   ├── pricing_recommendation_agent.py  # Main agent implementation
│   └── data_simulator.py     # Data generation and simulation
│
├── server/                    # MCP server implementation
│   ├── __init__.py
│   └── mcp_server.py         # FastAPI REST server
│
├── ui/                        # User interface components
│   ├── __init__.py
│   └── streamlit_ui.py       # Streamlit web interface
│
├── tests/                     # Test modules
│   ├── __init__.py
│   ├── test_toml_config.py   # Configuration tests
│   └── test_chat.py          # Chat functionality tests
│
├── scripts/                   # Utility scripts
│   ├── __init__.py
│   ├── setup_config.py       # Configuration setup
│   ├── setup_llm.py          # LLM setup utilities
│   ├── demo.py               # Demo and examples
│   └── quick_start.sh        # Quick start automation
│
└── docs/                      # Documentation
    ├── __init__.py
    ├── README.md             # Main documentation
    ├── recommendation_agent.md  # Technical details
    └── notes.md              # Development notes
```

## 🎯 Package Purposes

### `config/` - Configuration Management
- **Purpose**: Centralized configuration system
- **Key Features**:
  - TOML and environment variable support
  - Configuration validation and management
  - LLM provider configuration (OpenAI, AWS Bedrock)
  - Server and UI settings

### `core/` - Core Business Logic
- **Purpose**: Main application logic and algorithms
- **Key Features**:
  - Pricing recommendation algorithms
  - Statistical analysis
  - Data processing and analysis
  - Recommendation generation

### `server/` - MCP Server
- **Purpose**: REST API server for agent functionality
- **Key Features**:
  - FastAPI-based HTTP server
  - Recommendation endpoints
  - Data processing endpoints
  - Health checks and monitoring

### `ui/` - User Interface
- **Purpose**: Web-based user interface
- **Key Features**:
  - Streamlit dashboard
  - Chat assistant interface
  - Data visualization
  - Configuration management UI

### `tests/` - Testing
- **Purpose**: Test suite and validation
- **Key Features**:
  - Unit tests
  - Integration tests
  - Configuration tests
  - Chat functionality tests

### `scripts/` - Utilities
- **Purpose**: Setup, automation, and utility scripts
- **Key Features**:
  - Configuration setup
  - LLM provider setup
  - Demo and examples
  - Quick start automation

### `docs/` - Documentation
- **Purpose**: Project documentation and guides
- **Key Features**:
  - Setup instructions
  - API documentation
  - Technical specifications
  - Development notes

## 🚀 Usage

### Main Entry Point
```bash
# Start MCP server
python main.py server

# Start Streamlit UI
python main.py ui

# Run demo
python main.py demo

# Run tests
python main.py tests

# Run setup
python main.py setup

# Show help
python main.py help
```

### Direct Component Access
```bash
# Run server directly
python server/mcp_server.py

# Run UI directly
streamlit run ui/streamlit_ui.py

# Run demo directly
python scripts/demo.py

# Run tests directly
python tests/test_toml_config.py

# Run setup directly
python scripts/setup_config.py
```

### Quick Start
```bash
# Use the quick start script
./scripts/quick_start.sh

# Or run individual components
python main.py setup
python main.py server  # In one terminal
python main.py ui      # In another terminal
```

## 🔧 Development

### Adding New Components
1. **Core Logic**: Add to `core/` package
2. **Configuration**: Add to `config/` package
3. **API Endpoints**: Add to `server/` package
4. **UI Components**: Add to `ui/` package
5. **Tests**: Add to `tests/` package
6. **Scripts**: Add to `scripts/` package
7. **Documentation**: Add to `docs/` package

### Import Guidelines
- Use relative imports within packages
- Use absolute imports for cross-package dependencies
- Update `__init__.py` files to expose public APIs
- Follow the established import patterns

### Testing
- Add unit tests in `tests/` package
- Test configuration in `tests/test_toml_config.py`
- Test chat functionality in `tests/test_chat.py`
- Run all tests with `python main.py tests`

## 📋 Benefits of This Structure

1. **Logical Organization**: Related functionality is grouped together
2. **Maintainability**: Easy to find and modify specific components
3. **Scalability**: Easy to add new features and components
4. **Testing**: Clear separation of concerns for testing
5. **Documentation**: Organized documentation structure
6. **Configuration**: Centralized configuration management
7. **Entry Points**: Multiple ways to run and interact with the system 