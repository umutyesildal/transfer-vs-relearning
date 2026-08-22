# eval-v2 M0 metric normalization v1f — corrected execution contract

**Lifecycle:** frozen correction; awaiting one exact SHA-bound authorization  
**Scope:** one retry after the v1e adapter/writer field-binding regression

## Correction basis

The v1c source audit remains the scientific source of truth: 24/24 bindings and 42/42 metric
observations. The authorized v1d attempt stopped on a writer `KeyError: "path"`. The v1e retry
stopped earlier because its first correction changed the audit adapter lookup instead of the writer
lookup. Both failures are preserved append-only. This v1f correction explicitly restores
`match["path"]` in audit assembly and uses `raw_artifact_path` plus the verified raw hash only in
canonical writer assembly. Metric mappings, source identities, missingness and scientific scope
are unchanged.

## Bound identities

- v1d contract SHA-256: `bc258b243c053f938e9e4fa6a30fe3b6628531aa62204a4c4386e8d6bcbe37cf`
- v1d config SHA-256: `206f0c23e4f16b5c02c2b4e897b8ead9960b00e3c12fa6ef640e03d63c964b66`
- v1e contract SHA-256: `c1be111e18a294db60baec57a0694089524f72458b76cdc8906a405546b71e0f`
- v1e config SHA-256: `b2eee5b475976cfe37061a001232846920ea2617e07d72515bb7a9b62f840c6c`
- v1e failure record SHA-256: `492538545a302d532aad07cba8faae979e358a90a7e86f0ae7aef54c709c26c2`
- corrected implementation module SHA-256: `6ea61e845685c9d8a9f6ddc79bac7e7c1a0c2d51ac85610a1f3df886c394fcfd`
- operator script SHA-256: `79772ab237061c29a635fcc5303c330af2387f889681d339cdb18c3ffc984427`
- input projection root: `/vol/tmp2/yesildau/eval_v2_m0_three_model_projection_v1b`
- source registry SHA-256: `a0dca252afe7c1d03e458a60a8b48d7e8d8858e0ad95e6e8be696311a0b34265`
- projection manifest SHA-256: `9081b8eabef1ddfe1139754176cdcb1a26757fa3367d511cf81183536c8a9e0c`

## Single permitted retry

After exact authorization bound to this contract and companion config, publish the correction,
fast-forward HU and invoke the existing `normalize` entrypoint once. It must re-run the complete
audit, require 24 source rows and 42 observations, and write only this new root:

`/vol/tmp2/yesildau/eval_v2_m0_metric_normalization_v1f`

The v1d partial root and v1e absent-root failure are immutable evidence. No model/inference,
rescore, source mutation, projection mutation, Pile-10k, scientific gate, M1/M2 work, cleanup or
deletion is permitted.
