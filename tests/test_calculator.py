"""Tests for pyfarm-nutrients NutrientCalculator."""

import pytest

from pyfarm.nutrients.calculator import NutrientCalculator
from pyfarm.nutrients.models import NutrientSetpoint


class TestComputeNutrientDose:
    """Test NutrientCalculator.compute_nutrient_dose()."""

    def test_basic_dose_calculation(self):
        dose = NutrientCalculator.compute_nutrient_dose(
            current_ec=1.2,
            target_ec=1.4,
            reservoir_volume_l=100.0
        )
        assert dose > 0.0

    def test_no_dose_needed_equal_ec(self):
        dose = NutrientCalculator.compute_nutrient_dose(
            current_ec=1.4,
            target_ec=1.4,
            reservoir_volume_l=100.0
        )
        assert dose == 0.0

    def test_no_dose_needed_above_target(self):
        dose = NutrientCalculator.compute_nutrient_dose(
            current_ec=1.6,
            target_ec=1.4,
            reservoir_volume_l=100.0
        )
        assert dose == 0.0

    def test_larger_ec_change_requires_more_dose(self):
        dose_small = NutrientCalculator.compute_nutrient_dose(
            current_ec=1.2,
            target_ec=1.3,
            reservoir_volume_l=100.0
        )
        dose_large = NutrientCalculator.compute_nutrient_dose(
            current_ec=1.2,
            target_ec=1.5,
            reservoir_volume_l=100.0
        )
        assert dose_large > dose_small

    def test_larger_reservoir_requires_more_dose(self):
        dose_100l = NutrientCalculator.compute_nutrient_dose(
            current_ec=1.2,
            target_ec=1.4,
            reservoir_volume_l=100.0
        )
        dose_200l = NutrientCalculator.compute_nutrient_dose(
            current_ec=1.2,
            target_ec=1.4,
            reservoir_volume_l=200.0
        )
        assert dose_200l == pytest.approx(dose_100l * 2, rel=0.01)

    def test_small_reservoir(self):
        dose = NutrientCalculator.compute_nutrient_dose(
            current_ec=1.2,
            target_ec=1.4,
            reservoir_volume_l=10.0
        )
        assert dose > 0.0
        assert dose < 10.0  # Reasonable for small volume

    def test_large_ec_jump(self):
        dose = NutrientCalculator.compute_nutrient_dose(
            current_ec=0.5,
            target_ec=2.0,
            reservoir_volume_l=100.0
        )
        assert dose > 0.0


class TestComputePhAdjustment:
    """Test NutrientCalculator.compute_ph_adjustment()."""

    def test_acid_adjustment_needed(self):
        dose = NutrientCalculator.compute_ph_adjustment(
            current_ph=6.8,
            target_ph=6.0,
            reservoir_volume_l=100.0,
            is_acid=True
        )
        assert dose > 0.0

    def test_base_adjustment_needed(self):
        dose = NutrientCalculator.compute_ph_adjustment(
            current_ph=5.8,
            target_ph=6.5,
            reservoir_volume_l=100.0,
            is_acid=False
        )
        assert dose > 0.0

    def test_no_adjustment_at_target(self):
        dose = NutrientCalculator.compute_ph_adjustment(
            current_ph=6.0,
            target_ph=6.0,
            reservoir_volume_l=100.0
        )
        assert dose == 0.0

    def test_small_ph_change_below_threshold(self):
        # Less than 0.1 pH change
        dose = NutrientCalculator.compute_ph_adjustment(
            current_ph=6.04,
            target_ph=6.0,
            reservoir_volume_l=100.0
        )
        assert dose == 0.0

    def test_larger_ph_change_requires_more_dose(self):
        dose_01 = NutrientCalculator.compute_ph_adjustment(
            current_ph=6.1,
            target_ph=6.0,
            reservoir_volume_l=100.0
        )
        dose_05 = NutrientCalculator.compute_ph_adjustment(
            current_ph=6.5,
            target_ph=6.0,
            reservoir_volume_l=100.0
        )
        assert dose_05 > dose_01

    def test_larger_reservoir_requires_more_dose(self):
        dose_100l = NutrientCalculator.compute_ph_adjustment(
            current_ph=6.8,
            target_ph=6.0,
            reservoir_volume_l=100.0
        )
        dose_200l = NutrientCalculator.compute_ph_adjustment(
            current_ph=6.8,
            target_ph=6.0,
            reservoir_volume_l=200.0
        )
        assert dose_200l > dose_100l

    def test_max_daily_limit(self):
        # Large pH change should be capped by max_daily
        dose = NutrientCalculator.compute_ph_adjustment(
            current_ph=4.0,
            target_ph=7.0,
            reservoir_volume_l=100.0
        )
        max_daily = 100.0 * 0.02  # 2% of reservoir
        assert dose <= max_daily


class TestCheckDeficiency:
    """Test NutrientCalculator.check_deficiency()."""

    def test_normal_conditions_no_deficiency(self):
        deficiencies = NutrientCalculator.check_deficiency(
            ec=1.5,
            ph=6.2,
            nitrogen_reading=200.0
        )
        assert len(deficiencies) == 0

    def test_high_ec_low_nitrogen_lockout(self):
        deficiencies = NutrientCalculator.check_deficiency(
            ec=2.8,
            ph=6.2,
            nitrogen_reading=50.0
        )
        assert any("lockout" in d.lower() for d in deficiencies)

    def test_ph_too_low(self):
        deficiencies = NutrientCalculator.check_deficiency(
            ec=1.5,
            ph=5.0,
            nitrogen_reading=200.0
        )
        assert any("too low" in d.lower() for d in deficiencies)

    def test_ph_too_high(self):
        deficiencies = NutrientCalculator.check_deficiency(
            ec=1.5,
            ph=7.2,
            nitrogen_reading=200.0
        )
        assert any("too high" in d.lower() for d in deficiencies)

    def test_very_low_ec(self):
        deficiencies = NutrientCalculator.check_deficiency(
            ec=0.3,
            ph=6.2,
            nitrogen_reading=200.0
        )
        assert any("very low" in d.lower() for d in deficiencies)

    def test_multiple_deficiencies(self):
        deficiencies = NutrientCalculator.check_deficiency(
            ec=2.8,
            ph=5.0,
            nitrogen_reading=50.0
        )
        assert len(deficiencies) >= 2

    def test_boundary_ec_high(self):
        # Just at threshold
        deficiencies = NutrientCalculator.check_deficiency(
            ec=2.5,
            ph=6.2,
            nitrogen_reading=50.0
        )
        # High EC boundary - should trigger lockout warning
        assert len(deficiencies) > 0

    def test_boundary_ec_low(self):
        # Just at low threshold
        deficiencies = NutrientCalculator.check_deficiency(
            ec=0.5,
            ph=6.2,
            nitrogen_reading=200.0
        )
        # At exactly 0.5, should not trigger
        assert not any("very low" in d.lower() for d in deficiencies)

    def test_boundary_ph_low(self):
        # Just above boundary
        deficiencies = NutrientCalculator.check_deficiency(
            ec=1.5,
            ph=5.3,
            nitrogen_reading=200.0
        )
        # Above 5.2 should not trigger
        assert not any("too low" in d.lower() for d in deficiencies)

    def test_boundary_ph_high(self):
        # Just at boundary
        deficiencies = NutrientCalculator.check_deficiency(
            ec=1.5,
            ph=7.0,
            nitrogen_reading=200.0
        )
        # At exactly 7.0 should not trigger
        assert not any("too high" in d.lower() for d in deficiencies)

    def test_nitrogen_zero_no_sensor(self):
        # When nitrogen_reading is 0 (no sensor), should not cause lockout warning alone
        deficiencies = NutrientCalculator.check_deficiency(
            ec=1.5,
            ph=6.2,
            nitrogen_reading=0.0
        )
        # Low N alone doesn't trigger if EC is ok
        assert len(deficiencies) == 0
