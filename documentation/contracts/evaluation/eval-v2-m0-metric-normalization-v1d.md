# eval-v2 M0 metric normalization v1d — execution contract

**Lifecycle:** frozen preparation; awaiting one exact SHA-bound user authorization  
**Execution authorized:** no authorization is inferred from this document  
**Scope:** one canonical normalization of the already audited M0 eval-v2 source projection

## Purpose

The v1c source audit passed with 24/24 source rows and 42/42 metric observations. This contract
opens only the following next step: assemble those verified observations into one fresh canonical
normalization root. It does not rerun evaluation, load models, rescore prompts, alter source
artifacts, select a primary model, or open M1/M2 work.

## Bound evidence

- v1c contract SHA-256: `23f215696f25a9a3287dd058f3c50ff9e7f4a441cfed578756c4df68f0b21ad1`
- v1c config SHA-256: `7127a8fd66b494347a1d7c71cee92775e49283493d3be5ebd8e99e0b59f1dffc`
- v1c audit result: `documentation/evaluation/M0_METRIC_SOURCE_AUDIT_V1C_2026-08-22.md`
- v1c audit result SHA-256: `58a9295d686b732601f1bed538d58dcfa4f8cc6e05eb9a10b6c2145d07b4927a`
- input projection root: `/vol/tmp2/yesildau/eval_v2_m0_three_model_projection_v1b`
- source registry SHA-256: `a0dca252afe7c1d03e458a60a8b48d7e8d8858e0ad95e6e8be696311a0b34265`
- projection manifest SHA-256: `9081b8eabef1ddfe1139754176cdcb1a26757fa3367d511cf81183536c8a9e0c`

The input registry contains exactly 24 unique model/lane rows: 21 canonical non-Pile lanes and
three historical exact-prefix supplement rows. Pile-10k is excluded.

## Frozen execution

One invocation of:

```text
PYTHONPATH=src python scripts/study/normalize_m0_eval_v2.py normalize \
  --config configs/evaluation/eval_v2_m0_metric_normalization_v1d.yaml \
  --repo-root .
```

is permitted only after exact authorization bound to this contract SHA-256 and the companion
config SHA-256. The operator must re-run its fail-closed audit before creating the output root.
It must write only to the fresh root below and must refuse to overwrite an existing root:

`/vol/tmp2/yesildau/eval_v2_m0_metric_normalization_v1d`

Expected outputs are the operator's canonical Parquet/JSON tables and manifest, with exactly 42
metric observations and zero rescoring. Existing projection and raw evaluation roots are
read-only. No other HU path may be written.

## Prohibitions

- model loading, inference, rescoring or task execution;
- changing any source lane, projection registry or prior normalization root;
- adding Pile-10k or imputing missing values;
- recomputing bootstrap intervals, significance or scientific gates;
- selecting a primary model;
- M1/M2 training, evaluation, corpus materialization, cleanup or deletion.

The normalization manifest is a data-assembly artifact, not a scientific interpretation or model
selection result. M1 remains separately contracted.
