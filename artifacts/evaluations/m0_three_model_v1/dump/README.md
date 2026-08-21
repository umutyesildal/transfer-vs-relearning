# M0 three-model compact result dump

This directory is the Git-sized, derived result layer for the 2026-08-21 M0 dashboard and the
future M1/M2 dashboard slots.
It contains normalized numeric rows and provenance pointers; it does **not** contain model
weights, checkpoints, raw sample JSONL, corpus shards, or long logs.

## Canonical file

- `m0_metrics.json` — one machine-readable source for the dashboard and later analysis.
  - `metric_rows` is the normalized long table.
  - `lane_status` preserves complete/pending semantics. Missing is never encoded as zero.
  - `source_records` preserves the original HU scratch path, byte count, and SHA-256 for every
    source summary/result artifact used by a metric row.

## Interpretation

- The numeric dump is M0 only and uses the frozen eval-v1 metric names. `dashboard_states` records
  M0, M1, M2-A, and M2-B availability without fabricating result rows for states not yet run.
- `value: null` with `status: pending` means that the lane has not produced a valid metric yet;
  it is not a score of zero.
- BPB is the primary cross-tokenizer retention comparison. Token PPL is retained as companion
  evidence and should not be treated as a universal cross-tokenizer ranking.
- The Qwen Pile-10k lane is the only missing lane in this snapshot (23/24 valid).
- No canonical cross-model normalization or primary-model selection is claimed here.

## Provenance and retention

The source roots are listed under `contract.source_roots`. HU sources remain read-only on
approved scratch storage. The compact dump is safe to commit; raw sources must not be copied into
Git because they include large sample bundles and generated evaluation trees.

## Dashboard

The read-only local dashboard at `tools/m0-dashboard/` loads this JSON directly. From the
repository root, run:

```bash
python3 tools/m0-dashboard/serve.py
```

Then open `http://127.0.0.1:8765/tools/m0-dashboard/`.
