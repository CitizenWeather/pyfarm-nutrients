# pyfarm-nutrients

Nutrient solution chemistry and EC/pH management.

## Purpose

Manage nutrient formulations, dosing, and water quality for hydroponic/aeroponic systems.

## Phase 1 Scope

- **EC Dosing** — Compute nutrient feed amounts given target EC
- **pH Adjustment** — Compute acid/base additions to reach target pH
- **Nutrient Formulas** — Pre-defined macros (N-P-K) + micros for common crops
- **Deficiency/Toxicity Reference** — Simple lookup to diagnose plant issues
- **Reservoir Tracking** — Volume, concentration, water top-up scheduling

## Not in Phase 1

- Dynamic formulation (defer with biology models in Phase 2+)
- Tissue testing or spectral analysis
- Substrate/soil amendment (defer to Phase 3)

## Integration

- Called by pyfarm-control to compute EC/pH setpoints
- Loads cultivar defaults from pyfarm-crops
- GrowSpec can override via `<nutrients>` block

## Development

```bash
pip install -e ".[dev]"
pytest tests/
```
