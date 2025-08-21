"""
Test script for the chat functionality of the pricing recommendation agent.

This script demonstrates how the LLM integration works for generating
recommendations and providing insights.
"""

import os
import sys
from typing import Dict, Any, Optional

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pricing_recommendation_agent import PricingRecommendationAgent, AnalysisConfig
from data_simulator import DataSimulator


def simulate_chat_interaction():
    """Simulate a chat interaction with the pricing recommendation agent."""

    print("🤖 Pricing Recommendation Agent - Chat Demo")
    print("=" * 50)

    # Initialize agent and data simulator
    print("Initializing agent and generating test data...")
    agent = PricingRecommendationAgent()
    data_simulator = DataSimulator(seed=42)

    # Generate test data
    data = data_simulator.generate_all_data(days=60)
    recommendations = agent.generate_recommendations(data)

    # Simulate context data
    context_data = {
        "total_recommendations": len(recommendations),
        "acceptance_rate": 0.0,  # No feedback yet
        "high_priority_suppliers": [],
        "recent_recommendations": recommendations[:3] if recommendations else [],
    }

    print(f"Generated {len(recommendations)} recommendations")
    print()

    # Sample questions and simulated responses
    sample_questions = [
        "What are the most critical pricing issues we should address?",
        "Which suppliers are showing the biggest profitability declines?",
        "How can we improve our acceptance rate for recommendations?",
        "What insights can you provide about our volume trends?",
        "Which recommendations have the highest impact scores?",
    ]

    print("💬 Simulated Chat Interaction:")
    print("-" * 30)

    for i, question in enumerate(sample_questions, 1):
        print(f"\n👤 User: {question}")

        # Simulate AI response based on the question and context
        response = generate_simulated_response(question, context_data, recommendations)

        print(f"🤖 AI Assistant: {response}")
        print("-" * 50)

    print("\n✅ Chat demo completed!")
    print("\nTo use the real chat interface:")
    print("1. Set your OpenAI API key: export OPENAI_API_KEY='your-key-here'")
    print("2. Start the MCP server: python mcp_server.py")
    print("3. Launch the Streamlit UI: streamlit run streamlit_ui.py")
    print("4. Navigate to the 'Chat Assistant' page")


def generate_simulated_response(
    question: str, context_data: Dict[str, Any], recommendations: list
) -> str:
    """
    Generate a simulated AI response based on the question and context.

    Args:
        question: User's question
        context_data: Context data about recommendations
        recommendations: List of recommendations

    Returns:
        Simulated AI response
    """

    question_lower = question.lower()

    if "critical" in question_lower or "issues" in question_lower:
        if recommendations:
            high_impact = [r for r in recommendations if r.impact_score > 0.7]
            if high_impact:
                top_rec = high_impact[0]
                return f"Based on the analysis, the most critical issue is a {top_rec.type.replace('_', ' ')} for {top_rec.supplier_id}. This has an impact score of {top_rec.impact_score:.2f} and confidence of {top_rec.confidence_score:.2f}. I recommend investigating this supplier's recent performance trends."
            else:
                return "Currently, no critical issues have been identified. All recommendations have moderate to low impact scores. Consider reviewing the analysis thresholds if you're expecting more significant findings."
        else:
            return "No recommendations have been generated yet. Please run the analysis first to identify pricing issues."

    elif "profitability" in question_lower and "declines" in question_lower:
        profit_recs = [r for r in recommendations if r.type == "profitability_slowdown"]
        if profit_recs:
            top_profit = max(profit_recs, key=lambda x: x.impact_score)
            return f"The supplier showing the biggest profitability decline is {top_profit.supplier_id} with partner {top_profit.partner_id}. The recent average profitability is {top_profit.supporting_evidence.get('recent_mean', 'N/A'):.2f}% compared to historical {top_profit.supporting_evidence.get('historical_mean', 'N/A'):.2f}%. This represents a significant decline that warrants immediate attention."
        else:
            return "No significant profitability declines have been detected in the current analysis. This could indicate stable pricing performance or that the analysis thresholds may need adjustment."

    elif "acceptance rate" in question_lower:
        return f"To improve the acceptance rate for recommendations, consider: 1) Reviewing and adjusting statistical significance thresholds, 2) Focusing on high-impact recommendations first, 3) Providing more detailed supporting evidence, 4) Engaging with stakeholders to understand their decision criteria. Currently, {context_data['total_recommendations']} recommendations are available for review."

    elif "volume trends" in question_lower:
        volume_recs = [r for r in recommendations if r.type == "volume_slowdown"]
        if volume_recs:
            return f"Volume trend analysis shows {len(volume_recs)} suppliers experiencing significant booking volume declines. The most affected is {volume_recs[0].supplier_id} with a {volume_recs[0].impact_score:.2f} impact score. Consider investigating market conditions, competitive pricing, and supplier performance for these partners."
        else:
            return "Volume trends appear stable across suppliers. No significant declines have been detected in the current analysis period."

    elif "highest impact" in question_lower:
        if recommendations:
            sorted_recs = sorted(
                recommendations, key=lambda x: x.impact_score, reverse=True
            )
            top_3 = sorted_recs[:3]
            response = "The recommendations with the highest impact scores are:\n"
            for i, rec in enumerate(top_3, 1):
                response += f"{i}. {rec.type.replace('_', ' ').title()} for {rec.supplier_id} (Impact: {rec.impact_score:.2f})\n"
            return response
        else:
            return "No recommendations available to analyze impact scores."

    else:
        return "I can help you analyze pricing recommendations, supplier performance, and business insights. Please ask specific questions about profitability, volume trends, availability issues, or inventory management."


def test_llm_integration():
    """Test the actual LLM integration if API keys are available."""

    # Test OpenAI
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        try:
            import openai

            print("\n🧪 Testing OpenAI Integration...")

            # Initialize OpenAI client
            client = openai.OpenAI(api_key=api_key)

            # Test simple query
            test_question = "What are the key factors to consider when analyzing pricing recommendations?"

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a pricing analyst assistant. Provide concise, professional advice.",
                    },
                    {"role": "user", "content": test_question},
                ],
                max_tokens=200,
                temperature=0.7,
            )

            print(f"✅ OpenAI Integration Test Successful!")
            print(f"Question: {test_question}")
            print(f"Response: {response.choices[0].message.content}")

        except Exception as e:
            print(f"❌ OpenAI Integration Test Failed: {str(e)}")
    else:
        print("⚠️ OpenAI API key not found. Skipping OpenAI test.")

    # Test AWS Bedrock
    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")

    if aws_access_key and aws_secret_key:
        try:
            import boto3
            import json

            print("\n🧪 Testing AWS Bedrock Integration...")

            # Initialize Bedrock client
            bedrock_client = boto3.client(
                service_name="bedrock-runtime",
                region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
            )

            # Test simple query with Claude
            model_id = os.getenv(
                "BEDROCK_MODEL_ID", "anthropic.claude-3-sonnet-20240229-v1:0"
            )
            test_question = "What are the key factors to consider when analyzing pricing recommendations?"

            # Prepare request body for Claude
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 200,
                "temperature": 0.7,
                "messages": [
                    {
                        "role": "user",
                        "content": f"You are a pricing analyst assistant. Provide concise, professional advice.\n\nUser: {test_question}\n\nAssistant:",
                    }
                ],
            }

            response = bedrock_client.invoke_model(
                modelId=model_id, body=json.dumps(body)
            )

            response_body = json.loads(response.get("body").read())
            response_text = response_body["content"][0]["text"]

            print(f"✅ AWS Bedrock Integration Test Successful!")
            print(f"Model: {model_id}")
            print(f"Question: {test_question}")
            print(f"Response: {response_text}")

        except Exception as e:
            print(f"❌ AWS Bedrock Integration Test Failed: {str(e)}")
    else:
        print("⚠️ AWS Bedrock credentials not found. Skipping Bedrock test.")
        print(
            "Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables to test Bedrock."
        )


if __name__ == "__main__":
    # Run the chat simulation
    simulate_chat_interaction()

    # Test LLM integration if available
    test_llm_integration()
