"""
Data Simulator for Pricing Recommendation Agent

This module generates realistic toy data for testing the pricing recommendation agent.
It simulates various scenarios that would trigger recommendations.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List
import random


class DataSimulator:
    """
    Simulates realistic data for testing the pricing recommendation agent.
    """

    def __init__(self, seed: int = 42):
        self.seed = seed
        np.random.seed(seed)
        random.seed(seed)

        # Define sample suppliers and partners
        self.suppliers = [
            "supplier_hotel_chain_a",
            "supplier_hotel_chain_b",
            "supplier_airline_x",
            "supplier_airline_y",
            "supplier_car_rental_z",
            "supplier_activity_provider_w",
        ]

        self.partners = [
            "partner_ota_1",
            "partner_ota_2",
            "partner_corporate_1",
            "partner_affiliate_1",
            "partner_direct",
        ]

    def generate_profitability_data(self, days: int = 60) -> pd.DataFrame:
        """
        Generate profitability data with some suppliers showing significant declines.

        Args:
            days: Number of days of data to generate

        Returns:
            DataFrame with profitability data
        """
        data = []
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        for supplier_id in self.suppliers:
            for partner_id in self.partners:
                # Base profitability varies by supplier and partner
                base_profit = 15 + random.uniform(-5, 10)

                # Create trend - some suppliers show decline
                if (
                    supplier_id == "supplier_hotel_chain_a"
                    and partner_id == "partner_ota_1"
                ):
                    # Significant decline scenario
                    trend = -0.3  # Declining trend
                    noise = 2.0
                elif supplier_id == "supplier_airline_x":
                    # Moderate decline scenario
                    trend = -0.15
                    noise = 1.5
                else:
                    # Stable or slight growth
                    trend = random.uniform(-0.05, 0.1)
                    noise = 1.0

                for i in range(days):
                    date = start_date + timedelta(days=i)

                    # Calculate profit margin with trend and noise
                    days_from_start = i
                    profit_margin = (
                        base_profit
                        + (trend * days_from_start)
                        + np.random.normal(0, noise)
                    )

                    # Ensure reasonable bounds
                    profit_margin = max(0, min(30, profit_margin))

                    revenue = random.uniform(1000, 10000)

                    data.append(
                        {
                            "supplier_id": supplier_id,
                            "partner_id": partner_id,
                            "date": date,
                            "profit_margin": profit_margin,
                            "revenue": revenue,
                        }
                    )

        return pd.DataFrame(data)

    def generate_volume_data(self, days: int = 60) -> pd.DataFrame:
        """
        Generate booking volume data with some suppliers showing significant declines.

        Args:
            days: Number of days of data to generate

        Returns:
            DataFrame with volume data
        """
        data = []
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        for supplier_id in self.suppliers:
            for partner_id in self.partners:
                # Base volume varies by supplier and partner
                base_volume = 50 + random.uniform(-20, 30)

                # Create trend - some suppliers show decline
                if (
                    supplier_id == "supplier_airline_y"
                    and partner_id == "partner_corporate_1"
                ):
                    # Significant volume decline
                    trend = -1.2
                    noise = 8.0
                elif supplier_id == "supplier_car_rental_z":
                    # Moderate decline
                    trend = -0.8
                    noise = 5.0
                else:
                    # Stable or slight growth
                    trend = random.uniform(-0.3, 0.5)
                    noise = 3.0

                for i in range(days):
                    date = start_date + timedelta(days=i)

                    # Calculate booking count with trend and noise
                    days_from_start = i
                    booking_count = (
                        base_volume
                        + (trend * days_from_start)
                        + np.random.normal(0, noise)
                    )

                    # Ensure positive values
                    booking_count = max(1, booking_count)

                    revenue = booking_count * random.uniform(100, 500)

                    data.append(
                        {
                            "supplier_id": supplier_id,
                            "partner_id": partner_id,
                            "date": date,
                            "booking_count": booking_count,
                            "revenue": revenue,
                        }
                    )

        return pd.DataFrame(data)

    def generate_availability_data(self, days: int = 60) -> pd.DataFrame:
        """
        Generate availability vs itinerary creation data.

        Args:
            days: Number of days of data to generate

        Returns:
            DataFrame with availability data
        """
        data = []
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        for supplier_id in self.suppliers:
            # Base availability varies by supplier
            base_availability = 0.85 + random.uniform(-0.1, 0.1)

            # Create trend - some suppliers show decline in availability ratio
            if supplier_id == "supplier_activity_provider_w":
                # Significant decline in availability ratio
                trend = -0.008
                noise = 0.05
            elif supplier_id == "supplier_hotel_chain_b":
                # Moderate decline
                trend = -0.004
                noise = 0.03
            else:
                # Stable
                trend = random.uniform(-0.002, 0.003)
                noise = 0.02

            for i in range(days):
                date = start_date + timedelta(days=i)

                # Calculate availability ratio with trend and noise
                days_from_start = i
                availability_ratio = (
                    base_availability
                    + (trend * days_from_start)
                    + np.random.normal(0, noise)
                )

                # Ensure reasonable bounds
                availability_ratio = max(0.1, min(1.0, availability_ratio))

                # Generate related counts
                itinerary_count = random.randint(100, 1000)
                availability_count = int(itinerary_count * availability_ratio)

                data.append(
                    {
                        "supplier_id": supplier_id,
                        "date": date,
                        "availability_count": availability_count,
                        "itinerary_count": itinerary_count,
                    }
                )

        return pd.DataFrame(data)

    def generate_inventory_data(self, days: int = 60) -> pd.DataFrame:
        """
        Generate leftover inventory data.

        Args:
            days: Number of days of data to generate

        Returns:
            DataFrame with inventory data
        """
        data = []
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        for supplier_id in self.suppliers:
            # Base leftover ratio varies by supplier
            base_leftover_ratio = 0.05 + random.uniform(0, 0.1)

            # Create trend - some suppliers show increase in leftover inventory
            if supplier_id == "supplier_hotel_chain_a":
                # High leftover inventory
                trend = 0.003
                noise = 0.02
                base_margin = 12.0
            elif supplier_id == "supplier_airline_x":
                # Moderate leftover inventory
                trend = 0.002
                noise = 0.015
                base_margin = 8.0
            else:
                # Normal levels
                trend = random.uniform(-0.001, 0.001)
                noise = 0.01
                base_margin = 15.0 + random.uniform(-5, 5)

            for i in range(days):
                date = start_date + timedelta(days=i)

                # Calculate leftover ratio with trend and noise
                days_from_start = i
                leftover_ratio = (
                    base_leftover_ratio
                    + (trend * days_from_start)
                    + np.random.normal(0, noise)
                )

                # Ensure reasonable bounds
                leftover_ratio = max(0.01, min(0.3, leftover_ratio))

                # Generate related data
                total_inventory = random.randint(1000, 5000)
                leftover_inventory = int(total_inventory * leftover_ratio)
                margin = base_margin + np.random.normal(0, 2)
                margin = max(5, min(25, margin))

                data.append(
                    {
                        "supplier_id": supplier_id,
                        "date": date,
                        "leftover_inventory": leftover_inventory,
                        "margin": margin,
                        "total_inventory": total_inventory,
                    }
                )

        return pd.DataFrame(data)

    def generate_all_data(self, days: int = 60) -> Dict[str, pd.DataFrame]:
        """
        Generate all types of data for testing.

        Args:
            days: Number of days of data to generate

        Returns:
            Dictionary containing all dataframes
        """
        return {
            "profitability_data": self.generate_profitability_data(days),
            "volume_data": self.generate_volume_data(days),
            "availability_data": self.generate_availability_data(days),
            "inventory_data": self.generate_inventory_data(days),
        }

    def create_scenario_data(self, scenario: str = "mixed") -> Dict[str, pd.DataFrame]:
        """
        Create specific scenario data for testing different recommendation types.

        Args:
            scenario: Type of scenario ('profitability', 'volume', 'availability', 'inventory', 'mixed')

        Returns:
            Dictionary containing scenario-specific data
        """
        if scenario == "profitability":
            # Focus on profitability issues
            data = self.generate_all_data(60)
            # Modify to emphasize profitability problems
            return {"profitability_data": data["profitability_data"]}

        elif scenario == "volume":
            # Focus on volume issues
            data = self.generate_all_data(60)
            return {"volume_data": data["volume_data"]}

        elif scenario == "availability":
            # Focus on availability issues
            data = self.generate_all_data(60)
            return {"availability_data": data["availability_data"]}

        elif scenario == "inventory":
            # Focus on inventory issues
            data = self.generate_all_data(60)
            return {"inventory_data": data["inventory_data"]}

        else:  # mixed
            # Return all data with various issues
            return self.generate_all_data(60)
