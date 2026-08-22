# eval-v2 M0 Hash-Closed Projection v1b

**Lifecycle:** execution-enabled contract prepared after v1a fail-closed attempt

**Execution authorized in config:** yes; external SHA-bound authorization still required

## Scope

This is a one-wave operational correction of v1a. It preserves the exact eval-v2 source closure:
21 non-Pile scientific lane bindings plus three historical exact-prefix supplement bindings, with
the four top-manifest hashes recorded by the read-only discovery pass. It changes only the
execution flag and the fresh output root. It does not alter source paths, source hashes, model
identities, lane semantics or metric policy.

The preceding v1a attempt is preserved in
`documentation/records/evaluation/M0_EVAL_V2_PROJECTION_V1A_EXECUTION_BLOCKED_2026-08-22.md`.
The v1a pair must not be edited or reused.

## Authorized operation boundary

After a new exact SHA-bound user authorization, the operator may run the projector once on HU and
write only the fresh root declared by the v1b config:

`/vol/tmp2/yesildau/eval_v2_m0_three_model_projection_v1b`

The output may contain only the 24-row `source_registry.jsonl`, a projection manifest and its
one-way final inventory. It must write zero normalized metric rows. Pile-10k, rescoring,
inference, model loading, evaluation, training, normalization, cleanup and deletion remain
forbidden.

## Fail-closed rules

The wave must stop if the HU checkout, contract/config hashes, source hashes, model revisions,
lane identities or fresh-root condition differ. The v1b execution flag is not a substitute for
the separate user authorization bound to this contract and config.
