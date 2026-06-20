"""Nutrient dosing and EC/pH calculations."""

from __future__ import annotations

from pyfarm.nutrients.models import NutrientFormula, NutrientSetpoint


class NutrientCalculator:
    """Calculates nutrient dosing based on EC and pH targets."""

    # Calibration factors (liters of nutrient per mS/cm EC change per 100L)
    EC_CALIBRATION_FACTOR = 5.0

    # pH adjustment factors (mL of acid/base per 100L per 0.1 pH change)
    PH_CALIBRATION_FACTOR = 2.0

    @staticmethod
    def compute_nutrient_dose(
        current_ec: float,
        target_ec: float,
        reservoir_volume_l: float,
    ) -> float:
        """Calculate nutrient dose needed to reach target EC.

        Args:
            current_ec: Current EC in mS/cm
            target_ec: Target EC in mS/cm
            reservoir_volume_l: Reservoir volume in liters

        Returns:
            Nutrient dose in milliliters
        """
        ec_change = target_ec - current_ec
        if ec_change <= 0:
            return 0.0

        # Scale calibration by reservoir size
        dose_ml = (
            ec_change
            * NutrientCalculator.EC_CALIBRATION_FACTOR
            * (reservoir_volume_l / 100.0)
        )
        return max(0.0, dose_ml)

    @staticmethod
    def compute_ph_adjustment(
        current_ph: float,
        target_ph: float,
        reservoir_volume_l: float,
        is_acid: bool = True,
    ) -> float:
        """Calculate acid/base dose needed to reach target pH.

        Args:
            current_ph: Current pH
            target_ph: Target pH
            reservoir_volume_l: Reservoir volume in liters
            is_acid: True for acid (pH down), False for base (pH up)

        Returns:
            Adjustment dose in milliliters
        """
        ph_change = abs(target_ph - current_ph)
        if ph_change < 0.1:
            return 0.0

        # Scale by reservoir size
        dose_ml = (
            ph_change
            * NutrientCalculator.PH_CALIBRATION_FACTOR
            * (reservoir_volume_l / 100.0)
        )

        # Limit adjustment per day (avoid overshooting)
        max_daily = reservoir_volume_l * 0.02  # Max 2% per day
        dose_ml = min(dose_ml, max_daily)
        return max(0.0, dose_ml)

    @staticmethod
    def check_deficiency(
        ec: float,
        ph: float,
        nitrogen_reading: float = 0.0,
    ) -> list[str]:
        """Check for potential nutrient deficiencies.

        Args:
            ec: Electrical conductivity
            ph: pH value
            nitrogen_reading: Optional N sensor value

        Returns:
            List of suspected deficiencies
        """
        deficiencies = []

        # High EC + low N often indicates lockout
        if ec > 2.5 and nitrogen_reading < 100:
            deficiencies.append("Potential nutrient lockout due to high EC")

        # pH outside optimal range
        if ph < 5.2:
            deficiencies.append("pH too low - may reduce nutrient availability")
        elif ph > 7.0:
            deficiencies.append("pH too high - may reduce micronutrient availability")

        # Very low EC
        if ec < 0.5:
            deficiencies.append("EC very low - check nutrient concentration")

        return deficiencies
