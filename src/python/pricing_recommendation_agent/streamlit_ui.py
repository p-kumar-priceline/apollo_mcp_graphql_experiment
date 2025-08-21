"""
Streamlit UI for Pricing Recommendation Agent

This module provides a user-friendly web interface for the revenue management team
to review recommendations and provide feedback, including a chat interface with LLM.
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
from typing import Dict, List, Any, Optional
import time
import openai
import os
import boto3
from botocore.exceptions import ClientError, NoCredentialsError


# Configuration
API_BASE_URL = "http://localhost:8000"

# Page configuration
st.set_page_config(
    page_title="Pricing Recommendation Agent",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better styling
st.markdown(
    """
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .recommendation-card {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e0e0e0;
        margin-bottom: 1rem;
    }
    .high-impact {
        border-left: 4px solid #d62728;
    }
    .medium-impact {
        border-left: 4px solid #ff7f0e;
    }
    .low-impact {
        border-left: 4px solid #2ca02c;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        align-items: flex-start;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .assistant-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
    .stTextInput > div > div > input {
        background-color: white;
    }
</style>
""",
    unsafe_allow_html=True,
)


def make_api_request(
    endpoint: str, method: str = "GET", data: Optional[Dict[str, Any]] = None
) -> Optional[Dict[str, Any]]:
    """
    Make API request to the MCP server.

    Args:
        endpoint: API endpoint
        method: HTTP method
        data: Request data for POST requests

    Returns:
        API response
    """
    try:
        url = f"{API_BASE_URL}{endpoint}"

        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        else:
            raise ValueError(f"Unsupported method: {method}")

        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        st.error(f"API request failed: {str(e)}")
        return None


def initialize_chat_session():
    """Initialize chat session state."""
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "current_data" not in st.session_state:
        st.session_state.current_data = None

    if "recommendations" not in st.session_state:
        st.session_state.recommendations = []


def get_bedrock_client():
    """
    Initialize AWS Bedrock client using access keys.

    Returns:
        Bedrock client or None if credentials are not available
    """
    try:
        # Check for AWS credentials
        aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        aws_region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")

        if not aws_access_key_id or not aws_secret_access_key:
            return None

        # Initialize Bedrock client
        bedrock_client = boto3.client(
            service_name="bedrock-runtime",
            region_name=aws_region,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )

        return bedrock_client

    except (NoCredentialsError, ClientError) as e:
        st.error(f"AWS Bedrock client initialization failed: {str(e)}")
        return None


def invoke_bedrock_model(client, model_id: str, messages: List[Dict[str, str]]) -> str:
    """
    Invoke AWS Bedrock model with messages.

    Args:
        client: Bedrock client
        model_id: Model identifier (e.g., 'anthropic.claude-3-sonnet-20240229-v1:0')
        messages: List of message dictionaries

    Returns:
        Model response as string
    """
    try:
        # Convert messages to the format expected by the model
        if "claude" in model_id.lower():
            # Claude format
            prompt = ""
            for message in messages:
                if message["role"] == "system":
                    prompt += f"\n\nHuman: {message['content']}\n\nAssistant: I understand. I am an AI assistant for a pricing recommendation agent in the travel industry."
                elif message["role"] == "user":
                    prompt += f"\n\nHuman: {message['content']}\n\nAssistant:"

            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 500,
                "temperature": 0.7,
                "messages": [{"role": "user", "content": prompt}],
            }

        elif "titan" in model_id.lower():
            # Titan format
            prompt = ""
            for message in messages:
                if message["role"] == "system":
                    prompt += f"{message['content']}\n\n"
                elif message["role"] == "user":
                    prompt += f"User: {message['content']}\n\nAssistant:"

            body = {
                "inputText": prompt,
                "textGenerationConfig": {
                    "maxTokenCount": 500,
                    "temperature": 0.7,
                    "topP": 0.9,
                    "stopSequences": [],
                },
            }

        else:
            # Generic format for other models
            prompt = ""
            for message in messages:
                if message["role"] == "system":
                    prompt += f"{message['content']}\n\n"
                elif message["role"] == "user":
                    prompt += f"User: {message['content']}\n\nAssistant:"

            body = {"prompt": prompt, "max_tokens": 500, "temperature": 0.7}

        # Invoke the model
        response = client.invoke_model(modelId=model_id, body=json.dumps(body))

        response_body = json.loads(response.get("body").read())

        # Extract response based on model type
        if "claude" in model_id.lower():
            return response_body["content"][0]["text"]
        elif "titan" in model_id.lower():
            return response_body["results"][0]["outputText"]
        else:
            return response_body.get(
                "completion", response_body.get("text", "No response")
            )

    except Exception as e:
        return f"❌ Error invoking Bedrock model: {str(e)}"


def get_llm_response(
    user_message: str, context_data: Optional[Dict[str, Any]] = None
) -> str:
    """
    Get response from LLM (OpenAI or AWS Bedrock).

    Args:
        user_message: User's message
        context_data: Context data about recommendations and metrics

    Returns:
        LLM response
    """
    try:
        # Check for LLM provider preference
        llm_provider = os.getenv("LLM_PROVIDER", "openai").lower()

        # Prepare system message with context
        system_message = """You are an AI assistant for a pricing recommendation agent in the travel industry. 
        You help revenue management teams understand pricing optimization opportunities and provide insights.
        
        Your role is to:
        1. Analyze pricing data and recommendations
        2. Explain statistical findings in business terms
        3. Suggest actions based on recommendations
        4. Answer questions about profitability, volume, availability, and inventory
        5. Provide context and insights for decision-making
        
        Be helpful, professional, and focus on actionable insights."""

        # Add context if available
        if context_data:
            context_str = f"""
            Current context:
            - Total recommendations: {context_data.get('total_recommendations', 0)}
            - Acceptance rate: {context_data.get('acceptance_rate', 0):.1%}
            - High priority suppliers: {context_data.get('high_priority_suppliers', [])}
            - Recent recommendations: {len(context_data.get('recent_recommendations', []))}
            """
            system_message += context_str

        # Prepare messages
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ]

        if llm_provider == "bedrock":
            # Use AWS Bedrock
            bedrock_client = get_bedrock_client()
            if not bedrock_client:
                return "⚠️ AWS Bedrock credentials not found. Please set AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and optionally AWS_DEFAULT_REGION environment variables."

            # Get model ID from environment or use default
            model_id = os.getenv(
                "BEDROCK_MODEL_ID", "anthropic.claude-3-sonnet-20240229-v1:0"
            )

            return invoke_bedrock_model(bedrock_client, model_id, messages)

        else:
            # Use OpenAI (default)
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                return "⚠️ OpenAI API key not found. Please set the OPENAI_API_KEY environment variable to use the chat feature."

            # Call OpenAI API
            client = openai.OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=500,
                temperature=0.7,
            )

            content = response.choices[0].message.content
            return content if content else "No response received from AI assistant."

    except Exception as e:
        return f"❌ Error getting LLM response: {str(e)}"


def display_chat_interface():
    """Display the chat interface for LLM interaction."""
    st.subheader("💬 AI Assistant Chat")

    # Initialize chat session
    initialize_chat_session()

    # Get current context data
    summary = make_api_request("/summary")
    recommendations = make_api_request("/recommendations")

    context_data = None
    if summary and recommendations:
        context_data = {
            "total_recommendations": summary["total_recommendations"],
            "acceptance_rate": summary["acceptance_rate"],
            "high_priority_suppliers": summary["high_priority_suppliers"],
            "recent_recommendations": recommendations[:5],  # Last 5 recommendations
        }

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input(
        "Ask me about pricing recommendations, data analysis, or business insights..."
    ):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = get_llm_response(prompt, context_data)
                st.markdown(response)

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

    # Sidebar with chat controls
    with st.sidebar:
        st.subheader("Chat Controls")

        if st.button("Clear Chat History"):
            st.session_state.messages = []
            st.rerun()

        if st.button("Generate Sample Questions"):
            sample_questions = [
                "What are the most critical pricing issues we should address?",
                "Which suppliers are showing the biggest profitability declines?",
                "How can we improve our acceptance rate for recommendations?",
                "What insights can you provide about our volume trends?",
                "Which recommendations have the highest impact scores?",
                "How should we prioritize suppliers based on current data?",
                "What statistical significance should we look for in our analysis?",
                "Can you explain the difference between profitability and volume slowdowns?",
            ]

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": "Here are some sample questions you can ask:\n\n"
                    + "\n".join([f"• {q}" for q in sample_questions]),
                }
            )
            st.rerun()

        # Show context information
        if context_data:
            st.subheader("Current Context")
            st.metric("Total Recommendations", context_data["total_recommendations"])
            st.metric("Acceptance Rate", f"{context_data['acceptance_rate']:.1%}")

            if context_data["high_priority_suppliers"]:
                st.write("**High Priority Suppliers:**")
                for supplier in context_data["high_priority_suppliers"]:
                    st.write(f"• {supplier}")


def display_dashboard():
    """Display the main dashboard with summary metrics."""
    st.markdown(
        '<h1 class="main-header">📊 Pricing Recommendation Agent</h1>',
        unsafe_allow_html=True,
    )

    # Get summary data
    summary = make_api_request("/summary")

    if summary:
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(
                f"""
            <div class="metric-card">
                <h3>Total Recommendations</h3>
                <h2>{summary['total_recommendations']}</h2>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with col2:
            st.markdown(
                f"""
            <div class="metric-card">
                <h3>Accepted</h3>
                <h2 style="color: #2ca02c;">{summary['accepted']}</h2>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with col3:
            st.markdown(
                f"""
            <div class="metric-card">
                <h3>Rejected</h3>
                <h2 style="color: #d62728;">{summary['rejected']}</h2>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with col4:
            acceptance_rate = summary["acceptance_rate"] * 100
            st.markdown(
                f"""
            <div class="metric-card">
                <h3>Acceptance Rate</h3>
                <h2>{acceptance_rate:.1f}%</h2>
            </div>
            """,
                unsafe_allow_html=True,
            )

        # Display thresholds
        st.subheader("Current Analysis Thresholds")
        thresholds = summary["current_thresholds"]

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(
                "Profitability Significance",
                f"{thresholds['profitability_significance_level']:.3f}",
            )
        with col2:
            st.metric(
                "Volume Significance", f"{thresholds['volume_significance_level']:.3f}"
            )
        with col3:
            st.metric(
                "Availability Ratio Threshold",
                f"{thresholds['availability_ratio_threshold']:.2f}",
            )
        with col4:
            st.metric(
                "Leftover Inventory Threshold",
                f"{thresholds['leftover_inventory_threshold']:.2f}",
            )


def display_recommendations():
    """Display recommendations with filtering and feedback options."""
    st.subheader("📋 Recommendations")

    # Filter options
    col1, col2, col3 = st.columns(3)

    with col1:
        status_filter = st.selectbox(
            "Filter by Status", ["All", "pending", "accepted", "rejected"], index=0
        )

    with col2:
        type_filter = st.selectbox(
            "Filter by Type",
            [
                "All",
                "profitability_slowdown",
                "volume_slowdown",
                "availability_ratio",
                "leftover_inventory",
            ],
            index=0,
        )

    with col3:
        if st.button("🔄 Refresh Recommendations"):
            st.rerun()

    # Get recommendations
    params = {}
    if status_filter != "All":
        params["status"] = status_filter
    if type_filter != "All":
        params["recommendation_type"] = type_filter

    recommendations = make_api_request("/recommendations")

    if recommendations:
        # Display recommendations
        for rec in recommendations:
            # Determine impact level for styling
            impact_score = rec["impact_score"]
            if impact_score > 0.7:
                impact_class = "high-impact"
                impact_color = "🔴 High Impact"
            elif impact_score > 0.4:
                impact_class = "medium-impact"
                impact_color = "🟡 Medium Impact"
            else:
                impact_class = "low-impact"
                impact_color = "🟢 Low Impact"

            # Create recommendation card
            st.markdown(
                f"""
            <div class="recommendation-card {impact_class}">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div style="flex: 1;">
                        <h4>{rec['type'].replace('_', ' ').title()}</h4>
                        <p><strong>Supplier:</strong> {rec['supplier_id']}</p>
                        {f"<p><strong>Partner:</strong> {rec['partner_id']}</p>" if rec['partner_id'] else ""}
                        <p>{rec['description']}</p>
                        <p><strong>Created:</strong> {rec['created_at'][:10]}</p>
                    </div>
                    <div style="text-align: right;">
                        <p><strong>Impact:</strong> {impact_color}</p>
                        <p><strong>Confidence:</strong> {rec['confidence_score']:.2f}</p>
                        <p><strong>Status:</strong> {rec['status'].title()}</p>
                    </div>
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

            # Expandable section for details and feedback
            with st.expander("📊 Details & Feedback"):
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.subheader("Supporting Evidence")

                    # Display evidence as a table
                    evidence_df = pd.DataFrame(
                        list(rec["supporting_evidence"].items()),
                        columns=["Metric", "Value"],
                    )
                    st.dataframe(evidence_df, use_container_width=True)

                    # Create visualizations if possible
                    if (
                        "recent_mean" in rec["supporting_evidence"]
                        and "historical_mean" in rec["supporting_evidence"]
                    ):
                        fig = go.Figure()
                        fig.add_trace(
                            go.Bar(
                                x=["Historical", "Recent"],
                                y=[
                                    rec["supporting_evidence"]["historical_mean"],
                                    rec["supporting_evidence"]["recent_mean"],
                                ],
                                name="Average Values",
                            )
                        )
                        fig.update_layout(
                            title=f"Comparison: {rec['type'].replace('_', ' ').title()}",
                            xaxis_title="Period",
                            yaxis_title="Value",
                        )
                        st.plotly_chart(fig, use_container_width=True)

                with col2:
                    st.subheader("Provide Feedback")

                    if rec["status"] == "pending":
                        action = st.selectbox(
                            "Action",
                            ["accept", "reject", "adjust"],
                            key=f"action_{rec['id']}",
                        )

                        supplier_priority = st.selectbox(
                            "Supplier Priority",
                            ["normal", "high", "low"],
                            key=f"priority_{rec['id']}",
                        )

                        reason = st.text_area(
                            "Reason (optional)", key=f"reason_{rec['id']}"
                        )

                        comments = st.text_area(
                            "Comments (optional)", key=f"comments_{rec['id']}"
                        )

                        if st.button("Submit Feedback", key=f"submit_{rec['id']}"):
                            feedback_data = {
                                "recommendation_id": rec["id"],
                                "action": action,
                                "supplier_priority": supplier_priority,
                                "reason": reason if reason else None,
                                "comments": comments if comments else None,
                            }

                            result = make_api_request(
                                "/feedback", method="POST", data=feedback_data
                            )

                            if result:
                                st.success("Feedback submitted successfully!")
                                time.sleep(1)
                                st.rerun()
                    else:
                        st.info(f"Recommendation already {rec['status']}")

            st.divider()


def display_generate_recommendations():
    """Display interface for generating new recommendations."""
    st.subheader("🚀 Generate New Recommendations")

    col1, col2 = st.columns(2)

    with col1:
        scenario = st.selectbox(
            "Scenario",
            ["mixed", "profitability", "volume", "availability", "inventory"],
            help="Choose the type of scenario to generate recommendations for",
        )

        days = st.slider(
            "Days of Data",
            min_value=30,
            max_value=90,
            value=60,
            help="Number of days of historical data to analyze",
        )

    with col2:
        use_simulated_data = st.checkbox(
            "Use Simulated Data",
            value=True,
            help="Use simulated data for testing (uncheck to use real Athena data)",
        )

        if not use_simulated_data:
            athena_query = st.text_area(
                "Athena Query",
                placeholder="SELECT * FROM travel_analytics.profitability_data WHERE date >= '2024-01-01'",
                help="SQL query to execute against AWS Athena",
            )
        else:
            athena_query = None

    if st.button("Generate Recommendations"):
        with st.spinner("Generating recommendations..."):
            request_data = {
                "scenario": scenario,
                "days": days,
                "use_simulated_data": use_simulated_data,
            }

            if athena_query:
                request_data["athena_query"] = athena_query

            result = make_api_request(
                "/generate_recommendations", method="POST", data=request_data
            )

            if result:
                st.success(f"Generated {len(result)} recommendations!")
                time.sleep(1)
                st.rerun()


def display_configuration():
    """Display agent configuration interface."""
    st.subheader("⚙️ Agent Configuration")

    # Get current configuration
    summary = make_api_request("/summary")

    if summary:
        thresholds = summary["current_thresholds"]

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Statistical Thresholds")

            profitability_sig = st.slider(
                "Profitability Significance Level",
                min_value=0.01,
                max_value=0.10,
                value=float(thresholds["profitability_significance_level"]),
                step=0.01,
                help="P-value threshold for profitability analysis",
            )

            volume_sig = st.slider(
                "Volume Significance Level",
                min_value=0.01,
                max_value=0.10,
                value=float(thresholds["volume_significance_level"]),
                step=0.01,
                help="P-value threshold for volume analysis",
            )

        with col2:
            st.subheader("Business Thresholds")

            availability_threshold = st.slider(
                "Availability Ratio Threshold",
                min_value=0.5,
                max_value=0.95,
                value=float(thresholds["availability_ratio_threshold"]),
                step=0.05,
                help="Minimum acceptable availability ratio",
            )

            leftover_threshold = st.slider(
                "Leftover Inventory Threshold",
                min_value=0.05,
                max_value=0.25,
                value=float(thresholds["leftover_inventory_threshold"]),
                step=0.01,
                help="Maximum acceptable leftover inventory ratio",
            )

        # Additional configuration
        st.subheader("Analysis Parameters")

        col1, col2, col3 = st.columns(3)

        with col1:
            min_sample_size = st.number_input(
                "Minimum Sample Size",
                min_value=10,
                max_value=100,
                value=30,
                help="Minimum number of data points required for analysis",
            )

        with col2:
            lookback_days = st.number_input(
                "Lookback Days",
                min_value=7,
                max_value=90,
                value=30,
                help="Number of days to look back for historical comparison",
            )

        with col3:
            comparison_days = st.number_input(
                "Comparison Days",
                min_value=3,
                max_value=14,
                value=7,
                help="Number of recent days to compare against historical data",
            )

        if st.button("Update Configuration"):
            config_data = {
                "profitability_significance_level": profitability_sig,
                "volume_significance_level": volume_sig,
                "availability_ratio_threshold": availability_threshold,
                "leftover_inventory_threshold": leftover_threshold,
                "min_sample_size": min_sample_size,
                "lookback_days": lookback_days,
                "comparison_days": comparison_days,
            }

            result = make_api_request(
                "/configure_agent", method="POST", data=config_data
            )

            if result:
                st.success("Configuration updated successfully!")
                time.sleep(1)
                st.rerun()


def main():
    """Main application function."""
    # Sidebar navigation
    st.sidebar.title("Navigation")

    page = st.sidebar.selectbox(
        "Choose a page",
        [
            "Dashboard",
            "Chat Assistant",
            "Recommendations",
            "Generate Recommendations",
            "Configuration",
        ],
    )

    # Health check
    health = make_api_request("/health")
    if health:
        st.sidebar.success("✅ Server Connected")
    else:
        st.sidebar.error("❌ Server Disconnected")
        st.error(
            "Cannot connect to the MCP server. Please ensure it's running on localhost:8000"
        )
        return

    # Display selected page
    if page == "Dashboard":
        display_dashboard()
    elif page == "Chat Assistant":
        display_chat_interface()
    elif page == "Recommendations":
        display_recommendations()
    elif page == "Generate Recommendations":
        display_generate_recommendations()
    elif page == "Configuration":
        display_configuration()

    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Pricing Recommendation Agent**")
    st.sidebar.markdown("Version 1.0.0")

    # Chat setup instructions
    if page == "Chat Assistant":
        st.sidebar.markdown("---")
        st.sidebar.markdown("**Chat Setup**")

        # Show current LLM provider
        llm_provider = os.getenv("LLM_PROVIDER", "openai").lower()
        st.sidebar.markdown(f"**Current Provider:** {llm_provider.upper()}")

        if llm_provider == "openai":
            st.sidebar.markdown("To use OpenAI, set:")
            st.sidebar.code("export OPENAI_API_KEY='your-api-key-here'")
        else:
            st.sidebar.markdown("To use AWS Bedrock, set:")
            st.sidebar.code("export AWS_ACCESS_KEY_ID='your-access-key'")
            st.sidebar.code("export AWS_SECRET_ACCESS_KEY='your-secret-key'")
            st.sidebar.code("export AWS_DEFAULT_REGION='us-east-1'")
            st.sidebar.code(
                "export BEDROCK_MODEL_ID='anthropic.claude-3-sonnet-20240229-v1:0'"
            )

        st.sidebar.markdown("To switch providers, set:")
        st.sidebar.code("export LLM_PROVIDER='openai'  # or 'bedrock'")


if __name__ == "__main__":
    main()
