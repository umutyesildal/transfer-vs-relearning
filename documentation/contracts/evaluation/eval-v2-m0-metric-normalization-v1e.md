# eval-v2 M0 metric normalization v1e — corrected execution contract

**Lifecycle:** frozen correction; awaiting one exact SHA-bound authorization  
**Scope:** one retry of canonical normalization after the v1d operator failure

## Reason for correction

The v1c source audit passed with 24/24 source rows and 42/42 observations. The authorized v1d
normalization then stopped before table output with `KeyError: "path"`: the writer used an old
internal key instead of the audit row's `raw_artifact_path`. The failure is preserved in
`documentation/evaluation/M0_METRIC_NORMALIZATION_V1D_EXECUTION_FAILURE_2026-08-22.md`.

This correction changes only that field binding and adds a regression test. It does not change
the metric map, source identities, missingness policy, scientific gates or evaluation inputs.

## Bound identities

- v1d contract SHA-256: `bc258b243c053f938e9e4fa6a30fe3b6628531aa62204a4c4386e8d6bcbe37cf`
- v1d config SHA-256: `206f0c23e4f16b5c02c2b4e897b8ead9960b00e3c12fa6ef640e03d63c964b66`
- v1d failure record SHA-256: `ec6f32a8147293e2e2e0ad6b474f2c4f4bc28cf6dc533584d557127971b4ba4d`
- corrected implementation module SHA-256: `b10c74e3cfecd5a2ed4a94902b27bfa7315e54f9568d9fa623579db4eb7b3dc6`
- operator script SHA-256: `79772ab237061c29a635fcc5303c330af2387f889681d339cdb18c3ffc984427`
- input projection root: `/vol/tmp2/yesildau/eval_v2_m0_three_model_projection_v1b`
- source registry SHA-256: `a0dca252afe7c1d03e458a60a8b48d7e8d8858e0ad95e6e8be696311a0b34265`
- projection manifest SHA-256: `9081b8eabef1ddfe1139754176cdcb1a26757fa3367d511cf81183536c8a9e0c`

## Single permitted retry

After exact authorization bound to this contract and its companion config, push the correction,
fast-forward HU and invoke the same `normalize` entrypoint once with the v1e config. The operator
must re-run the complete fail-closed audit, observe exactly 24 source rows and 42 observations,
and write only this fresh root:

`/vol/tmp2/yesildau/eval_v2_m0_metric_normalization_v1e`

The previously created v1d partial root is immutable failure evidence and must not be reused,
overwritten or deleted. No model/inference/rescoring, source mutation, Pile-10k, scientific gate,
M1/M2 work, cleanup or deletion is in scope.
