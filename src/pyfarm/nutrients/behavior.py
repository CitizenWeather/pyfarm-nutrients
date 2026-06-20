"""Nutrient behavior for control loop integration."""

from __future__ import annotations

from typing import Optional

from pyfarm.crops.registry import CultivarRegistry
from pyfarm.nutrients.calculator import NutrientCalculator
from pyfarm.nutrients.models import NutrientSetpoint


class NutrientBehavior:
    """Compute nutrient setpoints based on cultivar and environment."""

    # Pre-defined nutrient formulas for Phase 1
    FORMULAS = {
        "hydro-veg": {
            "name": "Hydro A+B Vegetative",
            "macros": {"N": 150, "P": 30, "K": 150},
            "micros": {"Fe": 5, "Mn": 1, "Zn": 1, "B": 0.5, "Mo": 0.05},
        },
        "hydro-fruit": {
            "name": "Hydro A+B Fruiting",
            "macros": {"N": 100, "P": 50, "K": 200},
            "micros": {"Fe": 5, "Mn": 1, "Zn": 1, "B": 0.5, "Mo": 0.05},
        },
        "general": {
            "name": "General Purpose",
            "macros": {"N": 120, "P": 40, "K": 160},
            "micros": {"Fe": 5, "Mn": 1, "Zn": 1, "B": 0.5, "Mo": 0.05},
        },
    }

    def __init__(self, registry: CultivarRegistry):
        """Initialize nutrient behavior.

        Args:
            registry: Cultivar registry for defaults
        """
        self.registry = registry
        self.calculator = NutrientCalculator()

    async def compute_setpoint(
        self,
        cultivar_id: str,
        current_stage_index: int,
        override_ec: Optional[float] = None,
        override_ph: Optional[float] = None,
        formula_name: str = "general",
    ) -> NutrientSetpoint:
        """Compute nutrient setpoint for current stage.

        Args:
            cultivar_id: Cultivar ID
            current_stage_index: Index in phenophase list
            override_ec: Override EC (use if provided)
            override_ph: Override pH (use if provided)
            formula_name: Nutrient formula to use

        Returns:
            Nutrient setpoint with EC/pH targets
        """
        cultivar = await self.registry.get_cultivar(cultivar_id)
        if not cultivar:
            raise ValueError(f"Cultivar {cultivar_id} not found")

        # Get current stage for defaults
        if current_stage_index < len(cultivar.phenophases):
            # Could extract EC/pH from phenophase if defined
            pass

        # Determine EC
        if override_ec is not None:
            ec = override_ec
        elif cultivar.optimal_ec is not None:
            ec = cultivar.optimal_ec.max  # Use max as target
        else:
            ec = 1.4  # Default for most hydro

        # Determine pH
        if override_ph is not None:
            ph = override_ph
        elif cultivar.optimal_ph is not None:
            ph = cultivar.optimal_ph.max  # Use max as target
        else:
            ph = 6.0  # Default for most hydro

        # Get formula
        if formula_name not in self.FORMULAS:
            formula_name = "general"

        return NutrientSetpoint(
            target_ec=ec,
            target_ph=ph,
            reservoir_volume_l=100.0,
            nutrient_formula=formula_name,
        )

    async def validate_setpoint(self, setpoint: NutrientSetpoint) -> bool:
        """Validate a nutrient setpoint.

        Args:
            setpoint: Setpoint to validate

        Returns:
            True if valid
        """
        # EC must be 0.5-3.0
        if not 0.5 <= setpoint.target_ec <= 3.0:
            return False

        # pH must be 4.5-8.0
        if not 4.5 <= setpoint.target_ph <= 8.0:
            return False

        # Volume must be positive
        if setpoint.reservoir_volume_l <= 0:
            return False

        return True

    async def check_deficiency(
        self,
        current_ec: float,
        current_ph: float,
    ) -> list[str]:
        """Check for potential deficiencies.

        Args:
            current_ec: Current EC
            current_ph: Current pH

        Returns:
            List of suspected deficiencies
        """
        return self.calculator.check_deficiency(current_ec, current_ph)

    async def compute_dose(
        self,
        current_ec: float,
        target_ec: float,
        reservoir_volume_l: float,
    ) -> float:
        """Compute nutrient dose.

        Args:
            current_ec: Current EC
            target_ec: Target EC
            reservoir_volume_l: Reservoir volume

        Returns:
            Dose in milliliters
        """
        return self.calculator.compute_nutrient_dose(current_ec, target_ec, reservoir_volume_l)

    async def compute_ph_adjustment(
        self,
        current_ph: float,
        target_ph: float,
        reservoir_volume_l: float,
    ) -> tuple[str, float]:
        """Compute pH adjustment.

        Args:
            current_ph: Current pH
            target_ph: Target pH
            reservoir_volume_l: Reservoir volume

        Returns:
            Tuple of (adjustment_type, dose_ml) where type is "acid" or "base"
        """
        is_acid = current_ph > target_ph
        dose = self.calculator.compute_ph_adjustment(
            current_ph,
            target_ph,
            reservoir_volume_l,
            is_acid=is_acid,
        )
        adjustment_type = "acid" if is_acid else "base"
        return adjustment_type, dose
