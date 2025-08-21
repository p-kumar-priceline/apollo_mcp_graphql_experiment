# Pricing Recommendation Agent - Proof of Concept

A comprehensive pricing optimization recommendation system that identifies statistically significant opportunities for improving profitability, volume, availability, and inventory management in travel booking operations.

## 🎯 Overview

This proof of concept implements a recommendation agent that analyzes travel booking data to identify:

- **Profitability Slowdowns**: Statistically significant declines in profit margins from suppliers/partners
- **Volume Slowdowns**: Significant decreases in booking volumes
- **Availability Ratio Issues**: Declining ratios of availability to itinerary creation
- **Leftover Inventory**: High leftover inventory with accompanying margin analysis

## 🏗️ Architecture

The system consists of several components:

### Core Components

1. **PricingRecommendationAgent** (`pricing_recommendation_agent.py`)
   - Main agent class implementing statistical analysis
   - Generates recommendations based on configurable thresholds
   - Processes user feedback to improve future recommendations
   - Maintains recommendation history and supplier priorities

2. **DataSimulator** (`data_simulator.py`)
   - Generates realistic toy data for testing
   - Creates various scenarios that trigger recommendations
   - Simulates supplier/partner relationships and trends

3. **MCP Server** (`mcp_server.py`)
   - FastAPI-based REST API server
   - Exposes agent functionality through HTTP endpoints
   - Integrates with AWS Athena (placeholder implementation)
   - Handles background recommendation generation

4. **Streamlit UI** (`streamlit_ui.py`)
   - User-friendly web interface for revenue management team
   - Dashboard with metrics and visualizations
   - Recommendation review and feedback system
   - Agent configuration interface
   - **AI Chat Assistant** for conversational insights and recommendations

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip or conda for package management

### Installation

1. **Clone and navigate to the project directory:**
   ```bash
   cd src/python/pricing_recommendation_agent
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the demo to test the system:**
   ```bash
   python demo.py
   ```

4. **Set up LLM for chat functionality (optional):**
   ```bash
   python setup_llm.py
   ```

### Running the Full System

1. **Start the MCP server:**
   ```bash
   python mcp_server.py
   ```
   The server will be available at `http://localhost:8000`

2. **Launch the Streamlit UI:**
   ```bash
   streamlit run streamlit_ui.py
   ```
   The UI will be available at `http://localhost:8501`

3. **Set up LLM API keys (for chat functionality):**
   
   **Option A: OpenAI**
   ```bash
   export OPENAI_API_KEY='your-openai-api-key-here'
   export LLM_PROVIDER='openai'
   ```
   
   **Option B: AWS Bedrock**
   ```bash
   export AWS_ACCESS_KEY_ID='your-aws-access-key'
   export AWS_SECRET_ACCESS_KEY='your-aws-secret-key'
   export AWS_DEFAULT_REGION='us-east-1'
   export BEDROCK_MODEL_ID='anthropic.claude-3-sonnet-20240229-v1:0'
   export LLM_PROVIDER='bedrock'
   ```

4. **Access the API documentation:**
   - FastAPI docs: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

## 📊 Features

### Statistical Analysis

The agent performs rigorous statistical analysis using:

- **T-tests** for comparing recent vs. historical performance
- **Effect size calculations** to measure practical significance
- **Configurable significance levels** (default: p < 0.05)
- **Minimum sample size requirements** for reliable analysis

### Recommendation Types

1. **Profitability Slowdown**
   - Identifies suppliers/partners with declining profit margins
   - Compares recent vs. historical profitability data
   - Calculates confidence based on statistical significance

2. **Volume Slowdown**
   - Detects significant decreases in booking volumes
   - Analyzes trends across different time periods
   - Considers seasonal variations and noise

3. **Availability Ratio Issues**
   - Monitors ratio of availability to itinerary creation
   - Identifies suppliers with declining availability
   - Helps optimize inventory management

4. **Leftover Inventory**
   - Analyzes end-of-day inventory levels
   - Considers margin implications of leftover inventory
   - Suggests pricing or inventory adjustments

### User Feedback System

- **Accept/Reject/Adjust** recommendations
- **Supplier priority management** (high/low/normal)
- **Threshold adjustment** based on feedback
- **Learning system** that improves over time

### AI Chat Assistant

- **Conversational interface** for exploring recommendations
- **Natural language queries** about pricing data and insights
- **Context-aware responses** based on current recommendations
- **Sample questions** to help users get started
- **Real-time insights** about supplier performance and trends
- **Multiple LLM Providers** - Support for OpenAI GPT and AWS Bedrock models (Claude, Titan, etc.)

## 🔧 Configuration

### Analysis Parameters

The agent can be configured with various parameters:

```python
from pricing_recommendation_agent import AnalysisConfig

config = AnalysisConfig(
    profitability_significance_level=0.05,  # p-value threshold
    volume_significance_level=0.05,
    availability_ratio_threshold=0.8,       # minimum acceptable ratio
    leftover_inventory_threshold=0.1,       # maximum acceptable ratio
    min_sample_size=30,                     # minimum data points
    lookback_days=30,                       # historical comparison period
    comparison_days=7                       # recent period for comparison
)
```

### API Configuration

The MCP server can be configured via environment variables:

```bash
export DATABASE_NAME="travel_analytics"
export ATHENA_OUTPUT_LOCATION="s3://travel-analytics-output/"
export API_HOST="0.0.0.0"
export API_PORT="8000"
```

### LLM Configuration

The chat assistant supports multiple LLM providers:

**OpenAI Configuration:**
```bash
export LLM_PROVIDER="openai"
export OPENAI_API_KEY="your-openai-api-key"
```

**AWS Bedrock Configuration:**
```bash
export LLM_PROVIDER="bedrock"
export AWS_ACCESS_KEY_ID="your-aws-access-key"
export AWS_SECRET_ACCESS_KEY="your-aws-secret-key"
export AWS_DEFAULT_REGION="us-east-1"
export BEDROCK_MODEL_ID="anthropic.claude-3-sonnet-20240229-v1:0"
```

**Available Bedrock Models:**
- `anthropic.claude-3-sonnet-20240229-v1:0` (Claude 3 Sonnet)
- `anthropic.claude-3-haiku-20240307-v1:0` (Claude 3 Haiku)
- `amazon.titan-text-express-v1` (Titan Text)
- `ai21.j2-ultra-v1` (Jurassic-2 Ultra)

## 📈 Usage Examples

### Basic Usage

```python
from pricing_recommendation_agent import PricingRecommendationAgent
from data_simulator import DataSimulator

# Initialize components
agent = PricingRecommendationAgent()
data_simulator = DataSimulator()

# Generate test data
data = data_simulator.generate_all_data(days=60)

# Generate recommendations
recommendations = agent.generate_recommendations(data)

# Process feedback
agent.process_user_feedback(
    recommendation_id="profit_supplier_123_partner_456_20241201_120000",
    feedback={
        'action': 'accept',
        'supplier_priority': 'high',
        'reason': 'Critical supplier for our business'
    }
)
```

### API Usage

```python
import requests

# Generate recommendations
response = requests.post("http://localhost:8000/generate_recommendations", json={
    "scenario": "mixed",
    "days": 60,
    "use_simulated_data": True
})

recommendations = response.json()

# Submit feedback
requests.post("http://localhost:8000/feedback", json={
    "recommendation_id": "profit_supplier_123_partner_456_20241201_120000",
    "action": "accept",
    "supplier_priority": "high"
})
```

### Chat Assistant Usage

The chat interface provides a conversational way to explore recommendations:

```python
# Example chat interactions (via Streamlit UI)
# User: "What are the most critical pricing issues we should address?"
# AI: "Based on the analysis, the most critical issue is a profitability slowdown 
#      for supplier_hotel_chain_a. This has an impact score of 0.85 and confidence 
#      of 0.92. I recommend investigating this supplier's recent performance trends."

# User: "Which suppliers are showing the biggest profitability declines?"
# AI: "The supplier showing the biggest profitability decline is supplier_airline_x 
#      with partner partner_ota_1. The recent average profitability is 12.3% compared 
#      to historical 18.7%. This represents a significant decline that warrants 
#      immediate attention."
```

**Sample Questions for the Chat Assistant:**
- "What are the most critical pricing issues we should address?"
- "Which suppliers are showing the biggest profitability declines?"
- "How can we improve our acceptance rate for recommendations?"
- "What insights can you provide about our volume trends?"
- "Which recommendations have the highest impact scores?"
- "How should we prioritize suppliers based on current data?"
- "What statistical significance should we look for in our analysis?"
- "Can you explain the difference between profitability and volume slowdowns?"

**LLM Provider Features:**
- **OpenAI GPT**: Fast responses, good for general business insights
- **AWS Bedrock Claude**: Advanced reasoning, excellent for complex analysis
- **AWS Bedrock Titan**: Cost-effective, good for straightforward queries
- **Easy Switching**: Change providers by setting the `LLM_PROVIDER` environment variable

## 🔍 Data Requirements

### Input Data Format

The agent expects data in the following formats:

**Profitability Data:**
```python
{
    'supplier_id': str,
    'partner_id': str,
    'date': datetime,
    'profit_margin': float,  # percentage
    'revenue': float
}
```

**Volume Data:**
```python
{
    'supplier_id': str,
    'partner_id': str,
    'date': datetime,
    'booking_count': int,
    'revenue': float
}
```

**Availability Data:**
```python
{
    'supplier_id': str,
    'date': datetime,
    'availability_count': int,
    'itinerary_count': int
}
```

**Inventory Data:**
```python
{
    'supplier_id': str,
    'date': datetime,
    'leftover_inventory': int,
    'margin': float,  # percentage
    'total_inventory': int
}
```

### AWS Athena Integration

For production use, the system can integrate with AWS Athena:

```python
# Example Athena query
query = """
SELECT 
    supplier_id,
    partner_id,
    date,
    profit_margin,
    revenue
FROM travel_analytics.profitability_data
WHERE date >= CURRENT_DATE - INTERVAL '60' DAY
"""
```

## 🧪 Testing

### Running Tests

```bash
# Run the demo
python demo.py

# Run unit tests (when implemented)
pytest tests/

# Test API endpoints
python -m pytest tests/test_api.py

# Test chat functionality
python test_chat.py

# Set up LLM providers
python setup_llm.py
```

### Demo Scenarios

The demo includes several scenarios:

1. **Mixed Scenario**: All types of issues
2. **Profitability Focus**: Only profitability problems
3. **Volume Focus**: Only volume issues
4. **Availability Focus**: Only availability problems
5. **Inventory Focus**: Only inventory issues

## 📊 Metrics and KPIs

The system tracks several key metrics:

- **Total Recommendations**: Number of recommendations generated
- **Acceptance Rate**: Percentage of accepted recommendations
- **Confidence Scores**: Statistical confidence in recommendations
- **Impact Scores**: Estimated business impact
- **Processing Time**: Time to generate recommendations

## 🔮 Future Enhancements

### Planned Features

1. **Machine Learning Integration**
   - Predictive models for trend forecasting
   - Anomaly detection algorithms
   - Automated threshold optimization

2. **Advanced Analytics**
   - Seasonal decomposition
   - Multi-variate analysis
   - Correlation analysis between metrics

3. **Production Features**
   - Real-time data streaming
   - Automated alerting system
   - Integration with existing BI tools

4. **Enhanced UI**
   - Interactive dashboards
   - Real-time updates
   - Mobile-responsive design

### Integration Opportunities

- **Data Warehouses**: Snowflake, BigQuery, Redshift
- **BI Tools**: Tableau, Power BI, Looker
- **Alerting**: Slack, email, SMS
- **Workflow**: Airflow, Prefect, Dagster

## 🤝 Contributing

### Development Setup

1. **Fork the repository**
2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install development dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Run tests and linting:**
   ```bash
   black .
   flake8 .
   pytest
   ```

### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Write docstrings for all functions
- Include unit tests for new features

## 📄 License

This project is a proof of concept and is provided as-is for educational and demonstration purposes.

## 🆘 Support

For questions or issues:

1. Check the demo output for common issues
2. Review the API documentation at `http://localhost:8000/docs`
3. Examine the logs for error messages
4. Ensure all dependencies are properly installed

## 📚 References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Pandas Documentation](https://pandas.pydata.org/)
- [SciPy Statistical Functions](https://docs.scipy.org/doc/scipy/reference/stats.html)
- [AWS Athena Documentation](https://docs.aws.amazon.com/athena/) 