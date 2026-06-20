"""Tests for nutrient models."""

import pytest

from pyfarm.nutrients.models import NutrientFormula, NutrientSetpoint


def test_nutrient_formula_creation():
    formula = NutrientFormula(
        name="Hydro A+B Veg",
        macros={"N": 150, "P": 30, "K": 150},
    )
    assert formula.name == "Hydro A+B Veg"
    assert formula.macros["N"] == 150


def test_nutrient_formula_missing_name():
    with pytest.raises(ValueError):
        NutrientFormula(macros={"N": 150})


def test_nutrient_setpoint_creation():
    setpoint = NutrientSetpoint(
        target_ec=1.4,
        target_ph=6.0,
        nutrient_formula="hydro-veg",
    )
    assert setpoint.target_ec == 1.4
    assert setpoint.target_ph == 6.0


def test_nutrient_setpoint_invalid_ec():
    with pytest.raises(ValueError):
        NutrientSetpoint(target_ec=5.0, nutrient_formula="test")


def test_nutrient_setpoint_invalid_ph():
    with pytest.raises(ValueError):
        NutrientSetpoint(target_ph=10.0, nutrient_formula="test")
