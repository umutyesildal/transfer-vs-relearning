# M0 eval-v2 metric-source audit v1c — execution result

**Date:** 2026-08-22  
**Scope:** one read-only path-aware source audit  
**Status:** `audit_pass`  

This record closes the exact SHA-bound v1c audit authorization. It does not normalize,
rescore, load a model, run inference, or mutate any historical evaluation artifact.

## Bound identities

| Item | Identity |
|---|---|
| Contract | `documentation/contracts/evaluation/eval-v2-m0-metric-normalization-v1c.md` |
| Contract SHA-256 | `23f215696f25a9a3287dd058f3c50ff9e7f4a441cfed578756c4df68f0b21ad1` |
| Config | `configs/evaluation/eval_v2_m0_metric_normalization_v1c.yaml` |
| Config SHA-256 | `7127a8fd66b494347a1d7c71cee92775e49283493d3be5ebd8e99e0b59f1dffc` |
| Operator module SHA-256 | `b86ecf332264bb9c2947b0fddf653a855e4e73a0f0b1309c68a211d3c528f89c` |
| Operator script SHA-256 | `79772ab237061c29a635fcc5303c330af2387f889681d339cdb18c3ffc984427` |
| HU sync commit | `d9906ac` (`Add path-aware M0 metric source adapter`) |
| Input projection root | `/vol/tmp2/yesildau/eval_v2_m0_three_model_projection_v1b` |
| Projection manifest SHA-256 | `9081b8eabef1ddfe1139754176cdcb1a26757fa3367d511cf81183536c8a9e0c` |
| Source registry SHA-256 | `a0dca252afe7c1d03e458a60a8b48d7e8d8858e0ad95e6e8be696311a0b34265` |

## Read-only audit result

The path-aware adapter traversed all 24 declared source bindings:

- `source_row_count = 24`;
- `expected_metric_observation_count = 42`;
- `metric_observation_candidate_count = 42`;
- `findings = []`;
- `historical_sources_mutated = false`;
- `rescoring_performed = false`;
- `normalization_performed = false`.

The audit resolved the historical formats without changing their meaning: lm-eval JSON
metrics were read through their exact nested paths, Turkish perplexity used the declared
cross-domain summary fields, factual robust evidence used the declared CSV aggregate
`sum(all_cell_intersection)/sum(n)`, generation integrity used its recorded count and
repetition fields, and the three exact-prefix lanes used their top-level completion metric.
Denominator metadata was retained for factual and generation rates.

The fresh normalization output root
`/vol/tmp2/yesildau/eval_v2_m0_metric_normalization_v1c` was verified **absent** after the
command. The existing v1b projection root remained present and unchanged.

## Boundary after this result

M0 scientific evaluation artifacts and the 24-row hash-closed projection remain preserved;
this audit supplies the complete 42-observation source map but does not create canonical
normalized tables. A separately SHA-bound authorization is still required for exactly one
normalization execution. M1/M2 training, new evaluation/scoring, corpus work, cleanup and
deletion remain outside scope.
