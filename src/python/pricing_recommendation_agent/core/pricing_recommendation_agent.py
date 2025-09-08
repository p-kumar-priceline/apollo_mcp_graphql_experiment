"""
Pricing Recommendation Agent - Proof of Concept

This module implements a recommendation agent for identifying pricing optimization opportunities
based on statistical analysis of profitability, volume, and availability data.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
from scipy import stats
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Recommendation:
    """Data class for storing recommendation details"""

    id: str
    type: str  # 'profitability_slowdown', 'volume_slowdown', 'availability_ratio', 'leftover_inventory'
    supplier_id: str
    partner_id: Optional[str]
    description: str
    confidence_score: float
    impact_score: float
    supporting_evidence: Dict[str, Any]
    created_at: datetime
    status: str = "pending"  # 'pending', 'accepted', 'rejected', 'adjusted'


@dataclass
class AnalysisConfig:
    """Configuration for statistical analysis thresholds"""

    profitability_significance_level: float = 0.05
    volume_significance_level: float = 0.05
    availability_ratio_threshold: float = 0.8
    leftover_inventory_threshold: float = 0.1
    min_sample_size: int = 30
    lookback_days: int = 30
    comparison_days: int = 7


class PricingRecommendationAgent:
    """
    Main agent class for generating pricing recommendations based on statistical analysis.
    """

    def __init__(self, config: AnalysisConfig = None):
        self.config = config or AnalysisConfig()
        self.recommendations_history: List[Recommendation] = []
        self.user_feedback: Dict[str, Dict[str, Any]] = {}
        self.high_priority_suppliers: set = set()
        self.low_priority_suppliers: set = set()

    def analyze_profitability_slowdown(
        self, data: pd.DataFrame
    ) -> List[Recommendation]:
        """
        Identify statistically significant slowdown in profitability from suppliers/partners.

        Args:
            data: DataFrame with columns ['supplier_id', 'partner_id', 'date', 'profit_margin', 'revenue']

        Returns:
            List of recommendations for profitability slowdowns
        """
        recommendations = []

        # Group by supplier and partner
        for (supplier_id, partner_id), group in data.groupby(
            ["supplier_id", "partner_id"]
        ):
            if len(group) < self.config.min_sample_size:
                continue

            # Split data into recent and historical periods
            recent_cutoff = datetime.now() - timedelta(days=self.config.comparison_days)
            recent_data = group[group["date"] >= recent_cutoff]["profit_margin"]
            historical_data = group[group["date"] < recent_cutoff]["profit_margin"]

            if len(recent_data) < 10 or len(historical_data) < 10:
                continue

            # Perform t-test to check for significant difference
            t_stat, p_value = stats.ttest_ind(recent_data, historical_data)

            if p_value < self.config.profitability_significance_level:
                # Calculate effect size and confidence
                mean_diff = recent_data.mean() - historical_data.mean()
                effect_size = abs(mean_diff) / historical_data.std()

                if mean_diff < 0:  # Profitability decreased
                    confidence_score = min(0.95, 1 - p_value)
                    impact_score = min(1.0, effect_size / 2)

                    recommendation = Recommendation(
                        id=f"profit_{supplier_id}_{partner_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        type="profitability_slowdown",
                        supplier_id=supplier_id,
                        partner_id=partner_id,
                        description=f"Significant profitability decline detected for supplier {supplier_id} "
                        f"with partner {partner_id}. Recent avg: {recent_data.mean():.2f}%, "
                        f"Historical avg: {historical_data.mean():.2f}%",
                        confidence_score=confidence_score,
                        impact_score=impact_score,
                        supporting_evidence={
                            "p_value": p_value,
                            "t_statistic": t_stat,
                            "recent_mean": recent_data.mean(),
                            "historical_mean": historical_data.mean(),
                            "effect_size": effect_size,
                            "recent_std": recent_data.std(),
                            "historical_std": historical_data.std(),
                        },
                        created_at=datetime.now(),
                    )
                    recommendations.append(recommendation)

        return recommendations

    def analyze_volume_slowdown(self, data: pd.DataFrame) -> List[Recommendation]:
        """
        Identify statistically significant slowdown in volume from suppliers/partners.

        Args:
            data: DataFrame with columns ['supplier_id', 'partner_id', 'date', 'booking_count', 'revenue']

        Returns:
            List of recommendations for volume slowdowns
        """
        recommendations = []

        for (supplier_id, partner_id), group in data.groupby(
            ["supplier_id", "partner_id"]
        ):
            if len(group) < self.config.min_sample_size:
                continue

            recent_cutoff = datetime.now() - timedelta(days=self.config.comparison_days)
            recent_data = group[group["date"] >= recent_cutoff]["booking_count"]
            historical_data = group[group["date"] < recent_cutoff]["booking_count"]

            if len(recent_data) < 10 or len(historical_data) < 10:
                continue

            t_stat, p_value = stats.ttest_ind(recent_data, historical_data)

            if p_value < self.config.volume_significance_level:
                mean_diff = recent_data.mean() - historical_data.mean()
                effect_size = abs(mean_diff) / historical_data.std()

                if mean_diff < 0:  # Volume decreased
                    confidence_score = min(0.95, 1 - p_value)
                    impact_score = min(1.0, effect_size / 2)

                    recommendation = Recommendation(
                        id=f"volume_{supplier_id}_{partner_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        type="volume_slowdown",
                        supplier_id=supplier_id,
                        partner_id=partner_id,
                        description=f"Significant volume decline detected for supplier {supplier_id} "
                        f"with partner {partner_id}. Recent avg: {recent_data.mean():.1f} bookings, "
                        f"Historical avg: {historical_data.mean():.1f} bookings",
                        confidence_score=confidence_score,
                        impact_score=impact_score,
                        supporting_evidence={
                            "p_value": p_value,
                            "t_statistic": t_stat,
                            "recent_mean": recent_data.mean(),
                            "historical_mean": historical_data.mean(),
                            "effect_size": effect_size,
                            "recent_std": recent_data.std(),
                            "historical_std": historical_data.std(),
                        },
                        created_at=datetime.now(),
                    )
                    recommendations.append(recommendation)

        return recommendations

    def analyze_availability_ratio(self, data: pd.DataFrame) -> List[Recommendation]:
        """
        Identify statistically significant lowering in ratio of availability to itinerary creation.

        Args:
            data: DataFrame with columns ['supplier_id', 'date', 'availability_count', 'itinerary_count']

        Returns:
            List of recommendations for availability ratio issues
        """
        recommendations = []

        for supplier_id, group in data.groupby("supplier_id"):
            if len(group) < self.config.min_sample_size:
                continue

            # Calculate availability ratio
            group["availability_ratio"] = (
                group["availability_count"] / group["itinerary_count"]
            )

            recent_cutoff = datetime.now() - timedelta(days=self.config.comparison_days)
            recent_ratio = group[group["date"] >= recent_cutoff][
                "availability_ratio"
            ].mean()
            historical_ratio = group[group["date"] < recent_cutoff][
                "availability_ratio"
            ].mean()

            if recent_ratio < self.config.availability_ratio_threshold:
                # Calculate significance
                recent_data = group[group["date"] >= recent_cutoff][
                    "availability_ratio"
                ]
                historical_data = group[group["date"] < recent_cutoff][
                    "availability_ratio"
                ]

                if len(recent_data) >= 10 and len(historical_data) >= 10:
                    t_stat, p_value = stats.ttest_ind(recent_data, historical_data)

                    if p_value < 0.05:
                        effect_size = (
                            abs(recent_ratio - historical_ratio) / historical_data.std()
                        )

                        recommendation = Recommendation(
                            id=f"availability_{supplier_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                            type="availability_ratio",
                            supplier_id=supplier_id,
                            partner_id=None,
                            description=f"Low availability ratio detected for supplier {supplier_id}. "
                            f"Recent ratio: {recent_ratio:.3f}, Threshold: {self.config.availability_ratio_threshold}",
                            confidence_score=min(0.95, 1 - p_value),
                            impact_score=min(1.0, effect_size / 2),
                            supporting_evidence={
                                "p_value": p_value,
                                "t_statistic": t_stat,
                                "recent_ratio": recent_ratio,
                                "historical_ratio": historical_ratio,
                                "threshold": self.config.availability_ratio_threshold,
                                "effect_size": effect_size,
                            },
                            created_at=datetime.now(),
                        )
                        recommendations.append(recommendation)

        return recommendations

    def analyze_leftover_inventory(self, data: pd.DataFrame) -> List[Recommendation]:
        """
        Identify leftover inventory at the end of the day and accompanying margins.

        Args:
            data: DataFrame with columns ['supplier_id', 'date', 'leftover_inventory', 'margin', 'total_inventory']

        Returns:
            List of recommendations for leftover inventory issues
        """
        recommendations = []

        for supplier_id, group in data.groupby("supplier_id"):
            if len(group) < self.config.min_sample_size:
                continue

            # Calculate leftover ratio
            group["leftover_ratio"] = (
                group["leftover_inventory"] / group["total_inventory"]
            )

            # Focus on recent data
            recent_cutoff = datetime.now() - timedelta(days=self.config.comparison_days)
            recent_data = group[group["date"] >= recent_cutoff]

            if len(recent_data) < 10:
                continue

            avg_leftover_ratio = recent_data["leftover_ratio"].mean()
            avg_margin = recent_data["margin"].mean()

            if avg_leftover_ratio > self.config.leftover_inventory_threshold:
                # Calculate impact based on margin and leftover volume
                impact_score = min(1.0, avg_leftover_ratio * avg_margin / 100)

                recommendation = Recommendation(
                    id=f"leftover_{supplier_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    type="leftover_inventory",
                    supplier_id=supplier_id,
                    partner_id=None,
                    description=f"High leftover inventory detected for supplier {supplier_id}. "
                    f"Avg leftover ratio: {avg_leftover_ratio:.3f}, Avg margin: {avg_margin:.2f}%",
                    confidence_score=0.8,  # Based on threshold breach
                    impact_score=impact_score,
                    supporting_evidence={
                        "avg_leftover_ratio": avg_leftover_ratio,
                        "avg_margin": avg_margin,
                        "threshold": self.config.leftover_inventory_threshold,
                        "total_leftover_value": (
                            recent_data["leftover_inventory"] * recent_data["margin"]
                        ).sum(),
                    },
                    created_at=datetime.now(),
                )
                recommendations.append(recommendation)

        return recommendations

    def generate_recommendations(
        self, data: Dict[str, pd.DataFrame]
    ) -> List[Recommendation]:
        """
        Generate all types of recommendations based on available data.

        Args:
            data: Dictionary containing different dataframes for analysis

        Returns:
            List of all recommendations
        """
        all_recommendations = []

        # Analyze profitability slowdown
        if "profitability_data" in data:
            logger.info("Analyzing profitability slowdown...")
            profitability_recs = self.analyze_profitability_slowdown(
                data["profitability_data"]
            )
            all_recommendations.extend(profitability_recs)
            logger.info(
                f"Found {len(profitability_recs)} profitability recommendations"
            )

        # Analyze volume slowdown
        if "volume_data" in data:
            logger.info("Analyzing volume slowdown...")
            volume_recs = self.analyze_volume_slowdown(data["volume_data"])
            all_recommendations.extend(volume_recs)
            logger.info(f"Found {len(volume_recs)} volume recommendations")

        # Analyze availability ratio
        if "availability_data" in data:
            logger.info("Analyzing availability ratio...")
            availability_recs = self.analyze_availability_ratio(
                data["availability_data"]
            )
            all_recommendations.extend(availability_recs)
            logger.info(f"Found {len(availability_recs)} availability recommendations")

        # Analyze leftover inventory
        if "inventory_data" in data:
            logger.info("Analyzing leftover inventory...")
            inventory_recs = self.analyze_leftover_inventory(data["inventory_data"])
            all_recommendations.extend(inventory_recs)
            logger.info(f"Found {len(inventory_recs)} inventory recommendations")

        # Prioritize recommendations
        prioritized_recs = self.prioritize_recommendations(all_recommendations)

        # Store in history
        self.recommendations_history.extend(prioritized_recs)

        return prioritized_recs

    def prioritize_recommendations(
        self, recommendations: List[Recommendation]
    ) -> List[Recommendation]:
        """
        Prioritize recommendations based on impact, confidence, and supplier priority.

        Args:
            recommendations: List of recommendations to prioritize

        Returns:
            Prioritized list of recommendations
        """
        for rec in recommendations:
            # Boost priority for high-priority suppliers
            if rec.supplier_id in self.high_priority_suppliers:
                rec.impact_score *= 1.5

            # Reduce priority for low-priority suppliers
            if rec.supplier_id in self.low_priority_suppliers:
                rec.impact_score *= 0.7

        # Sort by combined score (impact * confidence)
        sorted_recs = sorted(
            recommendations,
            key=lambda x: x.impact_score * x.confidence_score,
            reverse=True,
        )

        return sorted_recs

    def process_user_feedback(
        self, recommendation_id: str, feedback: Dict[str, Any]
    ) -> None:
        """
        Process user feedback on recommendations to improve future analysis.

        Args:
            recommendation_id: ID of the recommendation
            feedback: Dictionary containing feedback data
        """
        self.user_feedback[recommendation_id] = feedback

        # Update recommendation status
        for rec in self.recommendations_history:
            if rec.id == recommendation_id:
                rec.status = feedback.get("action", "pending")
                break

        # Adjust thresholds based on feedback
        if feedback.get("action") == "reject":
            self._adjust_thresholds_based_on_feedback(recommendation_id, feedback)

        # Update supplier priorities
        if "supplier_priority" in feedback:
            supplier_id = feedback.get("supplier_id")
            if supplier_id:
                if feedback["supplier_priority"] == "high":
                    self.high_priority_suppliers.add(supplier_id)
                    self.low_priority_suppliers.discard(supplier_id)
                elif feedback["supplier_priority"] == "low":
                    self.low_priority_suppliers.add(supplier_id)
                    self.high_priority_suppliers.discard(supplier_id)

    def _adjust_thresholds_based_on_feedback(
        self, recommendation_id: str, feedback: Dict[str, Any]
    ) -> None:
        """
        Adjust analysis thresholds based on user feedback.

        Args:
            recommendation_id: ID of the rejected recommendation
            feedback: Feedback data
        """
        # Find the recommendation
        rec = next(
            (r for r in self.recommendations_history if r.id == recommendation_id), None
        )
        if not rec:
            return

        # Adjust thresholds based on recommendation type and feedback
        if rec.type == "profitability_slowdown":
            if feedback.get("reason") == "threshold_too_low":
                self.config.profitability_significance_level *= 0.9  # Make more strict
        elif rec.type == "volume_slowdown":
            if feedback.get("reason") == "threshold_too_low":
                self.config.volume_significance_level *= 0.9
        elif rec.type == "availability_ratio":
            if feedback.get("reason") == "threshold_too_low":
                self.config.availability_ratio_threshold *= 0.95
        elif rec.type == "leftover_inventory":
            if feedback.get("reason") == "threshold_too_low":
                self.config.leftover_inventory_threshold *= 0.95

    def get_recommendation_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all recommendations and performance metrics.

        Returns:
            Dictionary containing summary statistics
        """
        total_recommendations = len(self.recommendations_history)
        accepted = len(
            [r for r in self.recommendations_history if r.status == "accepted"]
        )
        rejected = len(
            [r for r in self.recommendations_history if r.status == "rejected"]
        )
        pending = len(
            [r for r in self.recommendations_history if r.status == "pending"]
        )

        return {
            "total_recommendations": total_recommendations,
            "accepted": accepted,
            "rejected": rejected,
            "pending": pending,
            "acceptance_rate": (
                accepted / total_recommendations if total_recommendations > 0 else 0
            ),
            "high_priority_suppliers": list(self.high_priority_suppliers),
            "low_priority_suppliers": list(self.low_priority_suppliers),
            "current_thresholds": {
                "profitability_significance_level": self.config.profitability_significance_level,
                "volume_significance_level": self.config.volume_significance_level,
                "availability_ratio_threshold": self.config.availability_ratio_threshold,
                "leftover_inventory_threshold": self.config.leftover_inventory_threshold,
            },
        }
