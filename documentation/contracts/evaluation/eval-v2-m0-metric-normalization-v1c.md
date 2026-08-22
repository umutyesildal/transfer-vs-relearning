# eval-v2 M0 metric normalization v1c — path-aware source adapter

**Lifecycle:** correction prepared and locally fixture-validated; HU audit unexecuted

**Execution authorized:** no

This is the narrow follow-up to the v1b audit. It preserves the 24-row projection, the v1a/v1b
fail-closed results and the no-rescore rule. It changes only metric-source binding: generic leaf
matching is replaced with explicit lm-eval JSON paths, project-summary selectors and verified CSV
aggregations. It does not authorize HU synchronization, normalization output, model access,
evaluation or training by itself.

## Evidence preserved

- v1a audit result: `documentation/evaluation/M0_METRIC_SOURCE_AUDIT_2026-08-22.md`
  - SHA-256 `692f857ce48bcb765308d560d23f2c6410ff2b8ccf6b1fb7fe99bb2a76e3edd5`
- v1b audit result: `documentation/evaluation/M0_METRIC_SOURCE_AUDIT_V1B_2026-08-22.md`
  - SHA-256 `8553edfb7e831f3d2a0042abb387717584140c279e7ddfbb484a536036af4f72`
- projection registry SHA-256: `a0dca252afe7c1d03e458a60a8b48d7e8d8858e0ad95e6e8be696311a0b34265`
- projection manifest SHA-256: `9081b8eabef1ddfe1139754176cdcb1a26757fa3367d511cf81183536c8a9e0c`

## Bound implementation

| file | SHA-256 |
| --- | --- |
| `src/transfer_vs_relearning/study/m0_metric_normalization.py` | `b86ecf332264bb9c2947b0fddf653a855e4e73a0f0b1309c68a211d3c528f89c` |
| `scripts/study/normalize_m0_eval_v2.py` | `79772ab237061c29a635fcc5303c330af2387f889681d339cdb18c3ffc984427` |

## Frozen path bindings

- `english_retention_wikitext`: `results.wikitext` fields
  `bits_per_byte,none`, `word_perplexity,none`, `byte_perplexity,none`.
- `english_grammar_blimp`: `results.blimp.acc,none`.
- `english_capability`: `results.hellaswag.acc_norm,none`.
- `turkish_capability`: `results.turblimp_core.acc_norm,none`.
- `turkish_perplexity`: exactly one JSON summary with
  `primary_cross_tokenizer_metric=bits_per_byte`; retain its BPB and byte perplexity and record
  source `perplexity` as the canonical word-perplexity compatibility field with raw source identity.
  The current M0 lane is cross-domain control only; missing primary held-out Turkish evidence stays
  explicit and is never treated as zero.
- `factual_access`: JSON `top1/probes` plus the declared
  `all_cell_intersections.csv` aggregate `sum(all_cell_intersection)/sum(n)`.
- `generation_integrity`: generation empty-count/prompt-count ratio and mean repeated 3-gram
  fraction from `summary_metrics.json`.
- `exact_prefix`: top-level `primary_mean_logprob_top1_accuracy`.

Every selector must resolve exactly once per model/lane. Missing or duplicate selectors block the
audit. CSVs are read only after their lane manifest SHA-256 is verified; no model or per-probe
rescoring occurs.

## Execution boundary

The v1c config remains `execution_authorized: false` and `normalization_authorized: false`. A
future read-only audit may print its 42-row schema report but may not create the normalization root.
Only an audit PASS followed by a separate exact normalization authorization can write normalized
Parquet/JSON artifacts. No scientific gate, primary-model selection, M1/M2 work, cleanup or
deletion is permitted.
