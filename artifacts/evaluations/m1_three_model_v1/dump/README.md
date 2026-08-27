# M1 three-model compact result dump

This directory is the Git-sized, derived result layer for the completed M1 eval-v2 family
`m1_eval_v2_matched_three_model_v3`.

## Canonical files

- `m1_metrics.json` — compact canonical snapshot: 111 state bundles, control manifests, normalized
  metric rows, source paths, SHA-256 hashes, denominators, and quality checks.
- `m0_m1_comparison.csv` — long-form comparison for every normalized metric row. It retains M0 value,
  M1 value, denominator, arithmetic delta, and an explicit comparison status.
- `m1_trajectory.csv` — one row per model × `parent`/epoch checkpoint for the recurring trajectory
  metrics.
- `M1_RESULT_LEDGER_2026-08-27.md` — human-readable terminal record with the endpoint comparison,
  full-state details, and all-checkpoint list.
- `dump_manifest.json` — hashes and sizes of the generated local artifacts.

## Coverage and semantics

- 3 models × (`parent` + `epoch-001` … `epoch-036`) = 111 scientific states.
- 108 states are GPU snapshots; 3 are explicit M0 parent projections without rescoring.
- Exact-prefix, WikiText, Turkish cross-domain and generation panels recur at every measured
  checkpoint. The 12,000-probe factual and full Harness capability panels run at epoch-18/36;
  the 1,500-probe cheap factual panel is present at every measured checkpoint and is derived from
  the full scores at the full states without rescoring.
- Missing values remain missing. `NOT_RUN`, projection, denominator mismatch, and no-reference
  states are not silently converted into zeros or scores.
- The M0 WikiText BPB comparison is bound to the canonical parent projection in the M1 family. This
  avoids the historical compact-dump field-label error where OLMo's `wikitext_bpb` field contained
  the byte-perplexity value.

## Retention

Only compact JSON summaries, control manifests, metric rows, source paths, and hashes are stored
here. Raw samples, CSV/parquet evidence, checkpoints, model weights, corpora and long logs remain
on approved HU scratch storage.

## Regeneration

The remote read-only extraction is implemented by
`scripts/evaluation/emit_m1_compact_remote.py`. The local builder is
`scripts/evaluation/build_m1_result_dump.py`; it consumes that NDJSON plus the existing M0 compact
dump and the downloaded control manifests.
