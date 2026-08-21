# M0 Evaluation Explorer

Small dependency-free read-only app for comparing the compact three-model M0 result dump.
It intentionally reads the canonical JSON under
`artifacts/evaluations/m0_three_model_v1/dump/` instead of carrying a second copy of the data.

## Run locally

From the repository root:

```bash
python3 tools/m0-dashboard/serve.py
```

Open `http://127.0.0.1:8765/tools/m0-dashboard/`.

The app provides a metric selector, model bars, lane coverage matrix, all-metric detail table,
and source artifact paths/SHA-256 values. It is read-only and does not contact HU or rerun an
evaluation.
