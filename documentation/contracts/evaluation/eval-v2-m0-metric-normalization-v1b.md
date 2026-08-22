# eval-v2 M0 metric normalization v1b — exact-prefix adapter correction

**Lifecycle:** correction prepared and locally validated; source audit unexecuted

**Execution authorized:** no

This is a narrow correction to the v1a source adapter after its authorized read-only audit
stopped on the historical exact-prefix result schema. It preserves the completed v1b projection,
all 24 source bindings, the zero-rescore policy and the v1a fail-closed result. It does not
authorize HU synchronization, source inspection, normalization output, model access, evaluation or
training by itself.

## Evidence preserved

- v1a audit result: `documentation/evaluation/M0_METRIC_SOURCE_AUDIT_2026-08-22.md`
  - SHA-256 `692f857ce48bcb765308d560d23f2c6410ff2b8ccf6b1fb7fe99bb2a76e3edd5`
- projection registry SHA-256: `a0dca252afe7c1d03e458a60a8b48d7e8d8858e0ad95e6e8be696311a0b34265`
- projection manifest SHA-256: `9081b8eabef1ddfe1139754176cdcb1a26757fa3367d511cf81183536c8a9e0c`

## Bound implementation

| file | SHA-256 |
| --- | --- |
| `src/transfer_vs_relearning/study/m0_metric_normalization.py` | `3de614b9ffe3b4a8a91a2091c5387c0992a409233dc09d3eb7b5cb9792dbaf0d` |
| `scripts/study/normalize_m0_eval_v2.py` | `79772ab237061c29a635fcc5303c330af2387f889681d339cdb18c3ffc984427` |

## Narrow changes

1. Canonical eval-v2 lanes still require `status=complete` and `returncode=0`.
2. Historical exact-prefix lanes require `status=complete`; their hash-verified registry binding
   is the completion proof because those legacy payloads do not carry `returncode`.
3. Exact-prefix accuracy maps only to the unique top-level
   `primary_mean_logprob_top1_accuracy` field. Generic `top1_accuracy` and `accuracy` aliases
   remain forbidden because historical summary files contain multiple top-1 values.
4. The full audit must still resolve exactly 24 source rows and 42 metric observations before a
   normalization run can be considered.

## Execution boundary

The v1b config must keep `execution_authorized: false` and `normalization_authorized: false`.
A future read-only audit may print its report but may not write the normalization output root.
Only an audit PASS followed by a separate exact normalization authorization can create the fresh
v1b normalization root. No model load, inference, rescoring, bootstrap recomputation, scientific
gate, primary-model selection, M1/M2 work, cleanup or deletion is permitted.
