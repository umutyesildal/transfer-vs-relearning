# M0–M2 Evaluation Explorer

Small dependency-free, bilingual read-only app for comparing the compact three-model M0 result
dump and reserving the same navigation/metric vocabulary for M1, M2-A, and M2-B.
It intentionally reads the canonical JSON under
`artifacts/evaluations/m0_three_model_v1/dump/` instead of carrying a second copy of the data.

## Run locally

From the repository root:

```bash
python3 tools/m0-dashboard/serve.py
```

Open `http://127.0.0.1:8765/tools/m0-dashboard/`.

The app has three pages: a home overview, a metric explorer with metric-specific explanations,
and a detail page containing all metric rows, coverage, reading guide, and source provenance.
The state selector supports M0/M1/M2-A/M2-B; states without a result snapshot remain explicitly
empty rather than showing invented numbers. The language toggle switches Turkish/English labels
without creating a second data source. It is read-only and does not contact HU or rerun an
evaluation.
