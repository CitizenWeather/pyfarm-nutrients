"""Tests for nutrient behavior."""

import pytest

from pyfarm.crops import MemoryRegistry
from pyfarm.nutrients import NutrientBehavior


@pytest.mark.asyncio
async def test_nutrient_setpoint():
    registry = MemoryRegistry()
    behavior = NutrientBehavior(registry)

    setpoint = await behavior.compute_setpoint("oyster-grey-strain-a", current_stage_index=0)
    assert 0.5 <= setpoint.target_ec <= 3.0
    assert 4.5 <= setpoint.target_ph <= 8.0


@pytest.mark.asyncio
async def test_override_ec_ph():
    registry = MemoryRegistry()
    behavior = NutrientBehavior(registry)

    setpoint = await behavior.compute_setpoint(
        "oyster-grey-strain-a",
        current_stage_index=0,
        override_ec=2.0,
        override_ph=6.5,
    )
    assert setpoint.target_ec == 2.0
    assert setpoint.target_ph == 6.5


@pytest.mark.asyncio
async def test_validate_setpoint():
    registry = MemoryRegistry()
    behavior = NutrientBehavior(registry)

    setpoint = await behavior.compute_setpoint("oyster-grey-strain-a", current_stage_index=0)
    assert await behavior.validate_setpoint(setpoint)

    # Invalid EC
    setpoint.target_ec = 5.0
    assert not await behavior.validate_setpoint(setpoint)

    # Invalid pH
    setpoint.target_ec = 1.4
    setpoint.target_ph = 9.0
    assert not await behavior.validate_setpoint(setpoint)


@pytest.mark.asyncio
async def test_ec_dosing():
    registry = MemoryRegistry()
    behavior = NutrientBehavior(registry)

    # Calculate dose to raise EC
    dose = await behavior.compute_dose(
        current_ec=1.2,
        target_ec=1.4,
        reservoir_volume_l=100.0,
    )
    assert dose > 0

    # No dose needed if at target
    dose = await behavior.compute_dose(
        current_ec=1.4,
        target_ec=1.4,
        reservoir_volume_l=100.0,
    )
    assert dose == 0


@pytest.mark.asyncio
async def test_ph_adjustment():
    registry = MemoryRegistry()
    behavior = NutrientBehavior(registry)

    # pH too high - need acid
    adj_type, dose = await behavior.compute_ph_adjustment(
        current_ph=6.8,
        target_ph=6.0,
        reservoir_volume_l=100.0,
    )
    assert adj_type == "acid"
    assert dose > 0

    # pH too low - need base
    adj_type, dose = await behavior.compute_ph_adjustment(
        current_ph=5.5,
        target_ph=6.0,
        reservoir_volume_l=100.0,
    )
    assert adj_type == "base"
    assert dose > 0


@pytest.mark.asyncio
async def test_deficiency_check():
    registry = MemoryRegistry()
    behavior = NutrientBehavior(registry)

    # High EC should flag potential lockout
    issues = await behavior.check_deficiency(ec=2.8, current_ph=6.0)
    assert len(issues) > 0

    # Normal conditions
    issues = await behavior.check_deficiency(ec=1.4, current_ph=6.0)
    assert len(issues) == 0
