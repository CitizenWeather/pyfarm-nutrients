"""Data models for nutrients."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class NutrientFormula:
    """A nutrient solution formula."""
    name: str = ""
    macros: dict = field(default_factory=dict)
    micros: dict = field(default_factory=dict)
    source: str = ""

    def __post_init__(self):
        if not self.name:
            raise ValueError("name is required")
        if not self.macros:
            raise ValueError("macros cannot be empty")


@dataclass
class NutrientSetpoint:
    """Nutrient solution control setpoint."""
    target_ec: float = 1.4
    target_ph: float = 6.0
    reservoir_volume_l: float = 100.0
    nutrient_formula: str = ""

    def __post_init__(self):
        if not 0.5 <= self.target_ec <= 3.0:
            raise ValueError("target_ec should be between 0.5 and 3.0 mS/cm")
        if not 4.5 <= self.target_ph <= 8.0:
            raise ValueError("target_ph should be between 4.5 and 8.0")
        if self.reservoir_volume_l <= 0:
            raise ValueError("reservoir_volume_l must be positive")
        if not self.nutrient_formula:
            raise ValueError("nutrient_formula is required")


@dataclass
class DeficiencyProfile:
    """Nutrient deficiency/toxicity reference."""
    nutrient: str = ""
    symptoms: list[str] = field(default_factory=list)
    leaf_color: str = ""
    affected_area: str = ""
