"""
Core package for Pricing Recommendation Agent.

This package contains the main business logic including:
- Pricing recommendation agent implementation
- Data simulation and generation
- Statistical analysis and algorithms
"""

from .pricing_recommendation_agent import PricingRecommendationAgent
from .data_simulator import DataSimulator

__all__ = [
    'PricingRecommendationAgent',
    'DataSimulator'
] 