# M0 eval-v2 metric-source audit result — 2026-08-22

**Scope:** one authorized read-only audit bound to metric-normalization v1a

**Contract SHA-256:** `d7e0310dc89f70b742840b0d3680d2c8d9b0ebc4738259ba512065ce6fd2b7a2`

**Config SHA-256:** `0cb92839242f7fa82f7d713ca651d75dba5f047def1f6ba8514a44b3ec728b21`

**Implementation commit on HU:** `57981c633c84486228c2933d38287b7d703edd1e`

**Operator module SHA-256:** `650fe0ebaf5e5d563dc51631e89e4b0978d2f9fba5ecd2ff705216100ddb0c69`

## Inputs and synchronization

The ordinary non-force push of `agent/m0-metric-normalization` completed and the clean HU
checkout fast-forwarded from `981b32d` to `57981c6`. The four bound source/config hashes matched
on HU. The completed projection root remained read-only:

- `/vol/tmp2/yesildau/eval_v2_m0_three_model_projection_v1b/source_registry.jsonl`
  - SHA-256 `a0dca252afe7c1d03e458a60a8b48d7e8d8858e0ad95e6e8be696311a0b34265`
- `projection_manifest.json`
  - SHA-256 `9081b8eabef1ddfe1139754176cdcb1a26757fa3367d511cf81183536c8a9e0c`
- `final_inventory.json`
  - SHA-256 `3d589db784fb0263e3ef9cc2506de3a8a920feaa00389379415d4d35e7537414`

## Audit invocation and result

The operator was invoked in `audit` mode with the v1a config and the HU monorepo root. It did not
create the normalization root, load a model, run inference, rescore a lane, or write any source
artifact. It stopped fail-closed at the first historical exact-prefix row:

```text
ValueError: Lane is not complete: olmo:exact_prefix
```

The source payload was then inspected read-only. All 21 canonical lanes have `status=complete` and
`returncode=0`. All three exact-prefix lane payloads have `status=complete` and valid hash bindings,
but their historical `lane_result.json` schema has no `returncode` field. Their primary metric is the
unique top-level `primary_mean_logprob_top1_accuracy` field. The generic `top1_accuracy` alias is
not safe because `summary_metrics.json` also contains chance-reference and sensitivity top-1
values.

Therefore this wave is classified:

```text
blocked_by_historical_exact_prefix_adapter_schema
```

This is an adapter/schema blocker, not a model result and not evidence that any source lane was
lost. No normalized metric rows were produced and no scientific interpretation is authorized.

## Required correction

The next local correction must change only the source adapter:

1. require `returncode=0` for canonical eval-v2 lanes, but accept historical exact-prefix
   completion by `status=complete` plus the already hash-verified registry binding;
2. map exact-prefix accuracy only to `primary_mean_logprob_top1_accuracy`, excluding generic
   `top1_accuracy` aliases;
3. rerun the full 24-row/42-observation audit before any normalization authority is considered.

The correction is prepared separately and remains unexecuted until a new exact SHA-bound
authorization is supplied. The v1a audit result and all projection artifacts remain preserved.
