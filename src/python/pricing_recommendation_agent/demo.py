"""
Demo Script for Pricing Recommendation Agent

This script demonstrates the pricing recommendation agent functionality
with simulated data and shows how to use the system.
"""

import asyncio
import time
import httpx
import json
from datetime import datetime
from typing import Dict, List, Any

# Import our modules
from pricing_recommendation_agent import PricingRecommendationAgent, AnalysisConfig
from data_simulator import DataSimulator


def print_separator(title: str):
    """Print a formatted separator with title."""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)


def print_subsection(title: str):
    """Print a formatted subsection title."""
    print(f"\n--- {title} ---")


def demo_agent_functionality():
    """Demonstrate the core agent functionality."""
    print_separator("DEMO: Pricing Recommendation Agent")

    # Initialize agent and data simulator
    print("Initializing agent and data simulator...")
    agent = PricingRecommendationAgent()
    data_simulator = DataSimulator(seed=42)

    # Generate test data
    print_subsection("Generating Test Data")
    print("Creating simulated data with various scenarios...")
    data = data_simulator.generate_all_data(days=60)

    print(f"Generated data for:")
    for key, df in data.items():
        print(f"  - {key}: {len(df)} records")

    # Generate recommendations
    print_subsection("Generating Recommendations")
    print("Analyzing data for pricing optimization opportunities...")

    start_time = time.time()
    recommendations = agent.generate_recommendations(data)
    end_time = time.time()

    print(
        f"Generated {len(recommendations)} recommendations in {end_time - start_time:.2f} seconds"
    )

    # Display recommendations
    print_subsection("Recommendation Details")
    for i, rec in enumerate(recommendations[:5], 1):  # Show first 5
        print(f"\n{i}. {rec.type.replace('_', ' ').title()}")
        print(f"   Supplier: {rec.supplier_id}")
        if rec.partner_id:
            print(f"   Partner: {rec.partner_id}")
        print(f"   Description: {rec.description}")
        print(f"   Confidence: {rec.confidence_score:.3f}")
        print(f"   Impact: {rec.impact_score:.3f}")
        print(f"   Status: {rec.status}")

    if len(recommendations) > 5:
        print(f"\n... and {len(recommendations) - 5} more recommendations")

    # Demonstrate feedback processing
    print_subsection("Processing User Feedback")
    if recommendations:
        # Simulate user feedback
        test_rec = recommendations[0]
        print(f"Processing feedback for recommendation: {test_rec.id}")

        feedback = {
            "action": "accept",
            "supplier_priority": "high",
            "reason": "This supplier is critical for our business",
            "comments": "Good catch! We should investigate this further.",
        }

        agent.process_user_feedback(test_rec.id, feedback)
        print("Feedback processed successfully!")

        # Show updated recommendation
        updated_rec = next(
            (r for r in agent.recommendations_history if r.id == test_rec.id), None
        )
        if updated_rec:
            print(f"Updated status: {updated_rec.status}")

    # Show summary
    print_subsection("Agent Summary")
    summary = agent.get_recommendation_summary()
    print(f"Total recommendations: {summary['total_recommendations']}")
    print(f"Accepted: {summary['accepted']}")
    print(f"Rejected: {summary['rejected']}")
    print(f"Pending: {summary['pending']}")
    print(f"Acceptance rate: {summary['acceptance_rate']:.1%}")
    print(f"High priority suppliers: {summary['high_priority_suppliers']}")
    print(f"Low priority suppliers: {summary['low_priority_suppliers']}")


def demo_scenario_analysis():
    """Demonstrate analysis of different scenarios."""
    print_separator("DEMO: Scenario Analysis")

    agent = PricingRecommendationAgent()
    data_simulator = DataSimulator(seed=123)

    scenarios = ["profitability", "volume", "availability", "inventory", "mixed"]

    for scenario in scenarios:
        print_subsection(f"Scenario: {scenario.title()}")

        # Generate scenario-specific data
        data = data_simulator.create_scenario_data(scenario)

        # Generate recommendations
        recommendations = agent.generate_recommendations(data)

        # Count by type
        type_counts = {}
        for rec in recommendations:
            type_counts[rec.type] = type_counts.get(rec.type, 0) + 1

        print(f"Generated {len(recommendations)} recommendations:")
        for rec_type, count in type_counts.items():
            print(f"  - {rec_type}: {count}")

        # Show top recommendation
        if recommendations:
            top_rec = recommendations[0]
            print(f"Top recommendation: {top_rec.type} for {top_rec.supplier_id}")
            print(f"  Impact score: {top_rec.impact_score:.3f}")
            print(f"  Confidence: {top_rec.confidence_score:.3f}")


def demo_configuration_changes():
    """Demonstrate how configuration changes affect recommendations."""
    print_separator("DEMO: Configuration Impact")

    data_simulator = DataSimulator(seed=456)
    data = data_simulator.generate_all_data(days=60)

    # Test different configurations
    configs = [
        (
            "Strict",
            AnalysisConfig(
                profitability_significance_level=0.01,
                volume_significance_level=0.01,
                availability_ratio_threshold=0.9,
                leftover_inventory_threshold=0.05,
            ),
        ),
        (
            "Lenient",
            AnalysisConfig(
                profitability_significance_level=0.1,
                volume_significance_level=0.1,
                availability_ratio_threshold=0.7,
                leftover_inventory_threshold=0.15,
            ),
        ),
        ("Default", AnalysisConfig()),
    ]

    for config_name, config in configs:
        print_subsection(f"Configuration: {config_name}")

        agent = PricingRecommendationAgent(config)
        recommendations = agent.generate_recommendations(data)

        print(f"Generated {len(recommendations)} recommendations")

        # Show threshold values
        print(
            f"  Profitability significance: {config.profitability_significance_level}"
        )
        print(f"  Volume significance: {config.volume_significance_level}")
        print(f"  Availability threshold: {config.availability_ratio_threshold}")
        print(f"  Inventory threshold: {config.leftover_inventory_threshold}")


def demo_api_endpoints():
    """Demonstrate API endpoints (requires server to be running)."""
    print_separator("DEMO: API Endpoints")

    base_url = "http://localhost:8000"

    # Test health endpoint
    try:
        print_subsection("Health Check")
        with httpx.Client() as client:
            response = client.get(f"{base_url}/health")
        if response.status_code == 200:
            health_data = response.json()
            print("✅ Server is healthy")
            print(f"Status: {health_data['status']}")
            print(f"Timestamp: {health_data['timestamp']}")
        else:
            print("❌ Server health check failed")
            return
    except httpx.RequestError:
        print("❌ Cannot connect to server. Make sure it's running on localhost:8000")
        print("To start the server, run: python mcp_server.py")
        return

    # Test generating recommendations
    print_subsection("Generate Recommendations via API")
    try:
        request_data = {"scenario": "mixed", "days": 60, "use_simulated_data": True}
        with httpx.Client() as client:
            response = client.post(
                f"{base_url}/generate_recommendations", json=request_data
            )
        if response.status_code == 200:
            recommendations = response.json()
            print(f"✅ Generated {len(recommendations)} recommendations via API")

            # Show first recommendation
            if recommendations:
                rec = recommendations[0]
                print(f"First recommendation: {rec['type']} for {rec['supplier_id']}")
        else:
            print(f"❌ Failed to generate recommendations: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing API: {str(e)}")

    # Test getting summary
    print_subsection("Get Summary via API")
    try:
        with httpx.Client() as client:
            response = client.get(f"{base_url}/summary")
        if response.status_code == 200:
            summary = response.json()
            print("✅ Retrieved summary via API")
            print(f"Total recommendations: {summary['total_recommendations']}")
            print(f"Acceptance rate: {summary['acceptance_rate']:.1%}")
        else:
            print(f"❌ Failed to get summary: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing API: {str(e)}")


def main():
    """Run all demos."""
    print("🚀 Pricing Recommendation Agent - Proof of Concept Demo")
    print("This demo showcases the pricing recommendation agent functionality.")

    # Run demos
    demo_agent_functionality()
    demo_scenario_analysis()
    demo_configuration_changes()
    demo_api_endpoints()

    print_separator("Demo Complete")
    print("🎉 Demo completed successfully!")
    print("\nNext steps:")
    print("1. Start the MCP server: python mcp_server.py")
    print("2. Launch the Streamlit UI: streamlit run streamlit_ui.py")
    print("3. Open http://localhost:8501 in your browser")
    print("4. Explore the interactive interface")


if __name__ == "__main__":
    main()
