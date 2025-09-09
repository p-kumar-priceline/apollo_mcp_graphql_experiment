# A2A Prototype with Google ADK, FastMCP, and AWS Bedrock

A minimal prototype demonstrating the A2A (Agent-to-Agent) protocol using Google ADK, FastMCP, and AWS Bedrock. This project showcases how to create a distributed agent system with data querying capabilities through AWS Athena.

## Architecture

The prototype consists of three main components:

1. **A2A Server with Host Agent**: Coordinates communication between agents using the A2A protocol
2. **Data Agent**: Uses Google ADK with AWS Bedrock LLM for intelligent data analysis
3. **MCP Tool for AWS Athena**: Provides data access capabilities through FastMCP

## Features

- ✅ A2A protocol implementation with host agent coordination
- ✅ Google ADK integration with AWS Bedrock LLM
- ✅ FastMCP tool for AWS Athena data queries
- ✅ RESTful API for agent interaction
- ✅ Comprehensive test suite with TDD approach
- ✅ Enterprise-standard code organization
- ✅ Self-documenting code with detailed docstrings

## Project Structure

```
src/
├── agents/                 # Agent implementations
│   ├── host/              # Host agent for A2A coordination
│   └── data/              # Data agent with Google ADK + Bedrock
├── config/                # Configuration management
├── servers/               # Server implementations
│   └── a2a/              # A2A server manager
├── tools/                 # MCP tools
│   └── athena/           # AWS Athena query tool
└── tests/                 # Test suite
    ├── unit/             # Unit tests
    └── integration/      # Integration tests
```

## Prerequisites

- Python 3.10+
- AWS Account with Bedrock and Athena access
- AWS credentials configured

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd apollo_mcp_graphql_experiment
```

2. Install dependencies using uv:
```bash
uv sync
```

3. Set up environment variables:
```bash
cp env.example .env
# Edit .env with your AWS credentials and configuration
```

## Configuration

Edit the `.env` file with your AWS credentials and settings:

```bash
# AWS Configuration
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
AWS_DEFAULT_REGION=us-east-1

# AWS Bedrock Configuration
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
BEDROCK_MAX_TOKENS=1000
BEDROCK_TEMPERATURE=0.7

# AWS Athena Configuration
ATHENA_DATABASE=default
ATHENA_S3_OUTPUT=s3://your-bucket/athena-results/
ATHENA_WORKGROUP=primary

# A2A Server Configuration
A2A_HOST=localhost
A2A_PORT=8000
A2A_AGENT_ID=host-agent
```

## Usage

### Starting the Server

```bash
python main.py
```

The server will start on `http://localhost:8000` with the following endpoints:

- `GET /` - Server information
- `GET /health` - Health check
- `POST /query` - Execute data queries
- `GET /agents` - List all agents
- `GET /agents/{id}` - Get agent information

### Example API Usage

1. **Health Check**:
```bash
curl http://localhost:8000/health
```

2. **Execute Data Query**:
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT * FROM your_table LIMIT 10"}'
```

3. **List Agents**:
```bash
curl http://localhost:8000/agents
```

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run only unit tests
pytest src/tests/unit/

# Run only integration tests
pytest src/tests/integration/

# Run with coverage
pytest --cov=src
```

## Development

### Code Organization

The project follows enterprise standards with:

- **Separation of Concerns**: Each component has a specific responsibility
- **Dependency Injection**: Configuration and dependencies are injected
- **Interface Segregation**: Clear interfaces between components
- **Test-Driven Development**: Comprehensive test coverage

### Adding New Features

1. Write tests first (TDD approach)
2. Implement the feature
3. Ensure all tests pass
4. Update documentation

### Code Style

- Follow PEP 8 guidelines
- Use type hints throughout
- Write comprehensive docstrings
- Keep functions small and focused

## API Reference

### Query Endpoint

**POST** `/query`

Execute a data query using the data agent.

**Request Body**:
```json
{
  "query": "SELECT * FROM table_name LIMIT 10",
  "agent_id": "data-agent"  // optional
}
```

**Response**:
```json
{
  "response": "Query executed successfully. Results:\n| id | name |\n| 1  | John |",
  "agent_id": "data-agent",
  "status": "success"
}
```

## Troubleshooting

### Common Issues

1. **AWS Credentials**: Ensure your AWS credentials are properly configured
2. **Bedrock Access**: Verify that Bedrock is available in your AWS region
3. **Athena Permissions**: Check that your AWS user has Athena query permissions
4. **S3 Bucket**: Ensure the Athena output S3 bucket exists and is accessible

### Logs

The server provides detailed logging. Check the console output for error messages and debugging information.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests for your changes
4. Implement the feature
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.