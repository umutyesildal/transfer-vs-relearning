# M0 eval-v2 normalization v1f — execution result

**Date:** 2026-08-22  
**Status:** `normalization_complete_pending_m0_interpretation`  
**Scientific scope:** canonical data assembly only; no new evaluation or inference

The explicitly authorized v1f correction completed the M0 normalization after the v1d/v1e
operator failures. It re-ran the fail-closed source audit, then wrote only the fresh v1f root.

## Bound execution

- Contract SHA-256: `fdc4e89f1dcfdd0a84b0fbb0b823a73370948992fe790cc08cdf3553e197352a`
- Config SHA-256: `3781cd62e6bfa1d3484bd87f54b44000eb9aae35a8b0260ad31b93cc15d56047`
- Implementation commit: `f53fec5`
- Input projection root: `/vol/tmp2/yesildau/eval_v2_m0_three_model_projection_v1b`
- Input projection manifest SHA-256: `9081b8eabef1ddfe1139754176cdcb1a26757fa3367d511cf81183536c8a9e0c`
- Output root: `/vol/tmp2/yesildau/eval_v2_m0_metric_normalization_v1f`

## Audit and output

- `source_row_count = 24`;
- `expected_metric_observation_count = 42`;
- `metric_observation_candidate_count = 42`;
- `findings = []`;
- `historical_sources_mutated = false`;
- `rescore_performed = false`;
- `metric_rows_written = 42`;
- `m0_metric_summary.status = complete`;
- `m0_metric_summary.observation_count = 42`.

The root contains five inventory-tracked artifacts:

| Artifact | SHA-256 |
|---|---|
| `checkpoint_registry.parquet` | `044294062f77d6a805a82b54e18b6917f6a98795359d4c8aa1ec0d8a76b9ded9` |
| `factual_probe_results.parquet` | `e7aa85b470c04659de4cc8cef768572f598e2c9f7ac6ca201a3123df3c286403` |
| `m0_metric_summary.json` | `bb33ebb2c50d977e537e5833fb940f0eb788d1265521c90fdad2b0b4e13dfe99` |
| `metric_observations.parquet` | `4749fe38c80ad1c63aa5db8b1380dfcf0505ba67f152b98a597d60238a7eec61` |
| `normalization_manifest.json` | `fdd6e55ca0da367d93ed07b83083b69a57f01c1591f64fb82debafb7b95e3b32` |

The final inventory is `c0da9b2b38965eafecacd3e9c8fd79daa1543890403c83d053c4bde4595dfea7`.
The v1d partial root and its failure record remain preserved; the absent v1e root remains absent.

## Boundary after M0 normalization

M0’s raw evaluation evidence, hash-closed 24-row projection, source audit and canonical 42-row
metric table are now complete. This does not interpret the science, select a primary model, or
authorize M1/M2 training. The next bounded task is to prepare/review the M1 training contract;
training and new evaluation still require separate authorization.
