# M1 eval-v2 matched three-model wave — terminal result

**Date:** 2026-08-27  
**Status:** `complete`  
**Canonical result root:** `/vol/tmp2/yesildau/m1_eval_v2_matched_three_model_v3`

## Terminal outcome

The final M1 evaluation family closed at **111/111 scientific states**:

| Component | Complete | Expected | Meaning |
|---|---:|---:|---|
| GPU checkpoint snapshots | 108 | 108 | 3 models × 36 epoch snapshots |
| M0 parent projections | 3 | 3 | canonical M0 evidence, no rescoring |
| Total family | 111 | 111 | finalizer accepted the family |

Each model has `parent` plus `epoch-001` through `epoch-036`. The last missing state was
`qwen/epoch-018`; its final canonical task result is `complete` and its earlier
`epoch-018__killed_0` attempt remains preserved as evidence rather than being counted as another
scientific state.

## Submission and integrity evidence

The final chain was preflight `479444`, array `479445`, and finalizer `479446`. The final family
result reports matrix `2673aacbc8640149`, `complete_count: 111`, `gpu_complete_count: 108`, and
`parent_complete_count: 3`.

| Artifact | SHA-256 | Bytes |
|---|---|---:|
| `control/evaluation_family_result.json` | `ccd26de2193ec3d5580346fd01ecadb84f450224eb0aebeb39ec694ff2b1487a` | 32,309 |
| `control/preflight.json` | `dbd40c62f5f3a31f84fd36ee6452d8b02ea2cb8a64ec87496d891d6d36356e64` | 371 |
| `control/submission_manifest.json` | `be5da631c304d16d1bcc8662745916a1353e9ada82365d827b5270f1ee72b708` | 467 |
| `control/task_matrix.json` | `9e0ef04d596ac9c35230a520817da92e03a031d91e7c3e2694b2e8ad0704f120` | 132,113 |
| `logs/m1-eval-v2-finalize-479446.out` | `4aab982f6c6f3e07fc4db968ad93eec2e04b9d8b294643cbca320e506bf5a33a` | 27,843 |

Finalizer stderr was zero bytes. `sacct` could not provide accounting metadata because HU's
Munge/SlurmDBD authentication failed during inspection; this is an accounting limitation, not a
failed result. The independent family result, canonical task results and summary hashes are the
completion evidence.

## Bound identities

| Identity | SHA-256 / value |
|---|---|
| M1 contract | `33d48d0a6481c78c88110dd637db68c857d5574f523efbc9754737dc9d80b1a8` |
| M1 execution config | `3fd83349e7da1986651b5bfceb0942ed491b7671ff97ff33d4a9b89444ece83b` |
| Adapter module | `eacb239142435dd1bfa0ddaea624207a03c34c0bfbf35e4c1752765a723b5315` |
| Adapter entrypoint | `e3b8eefe6420f9c1eddf7f13a3548c32355ff203618b9a14c157f8047bebfd1a` |
| Harness | `lm-eval 0.4.12` |
| Turkish control | 10,034 validation documents; corpus SHA is retained in every Turkish summary |

## M0 comparison and detailed result layer

The complete M0↔M1 comparison is the generated ledger
[`M1_RESULT_LEDGER_2026-08-27.md`](../../../artifacts/evaluations/m1_three_model_v1/dump/M1_RESULT_LEDGER_2026-08-27.md).
It contains:

- endpoint tables for M0, M1 epoch-18 and M1 epoch-36;
- detailed full-state metrics with denominators and comparison status;
- the all-checkpoint list for all 36 epochs of all three models;
- exact-prefix, factual, Turkish, generation, WikiText and Harness results.

The machine-readable companion is
[`m1_metrics.json`](../../../artifacts/evaluations/m1_three_model_v1/dump/m1_metrics.json). The
long-form comparison is
[`m0_m1_comparison.csv`](../../../artifacts/evaluations/m1_three_model_v1/dump/m0_m1_comparison.csv),
and the one-row-per-state trajectory is
[`m1_trajectory.csv`](../../../artifacts/evaluations/m1_three_model_v1/dump/m1_trajectory.csv).
The compact dump contains 2,103 normalized metric rows, state-level source paths and SHA-256
hashes, control manifests, denominators, missingness/status labels and automated quality checks.

Comparison rules are explicit: `Δ = M1 − M0`; BPB/PPL/repetition are lower-is-better, while
accuracy/top-1/MRR/distinct-2/forced-choice are higher-is-better. Cheap factual rows use the
1,500-probe panel and are not substituted for the directly comparable 12,000-probe full factual
rows. Exact-prefix remains a candidate-ranking panel, not free-generation exact-match accuracy.

During construction, the M0 WikiText BPB reference was bound to the hash-closed M0 parent
projection in this family. This corrects a historical field-label error in the older compact M0
dump where OLMo's `wikitext_bpb` field contained its byte-perplexity value. The old M0 artifact is
preserved; the correction is documented in the new derived comparison layer.

## Boundary

This record closes M1 evaluation execution bookkeeping. It does not select a primary model, claim a
replicated causal effect, authorize M2-A/M2-B, authorize cleanup, or authorize a duplicate
submission. The next separate scientific task is trajectory normalization/presentation review from
the preserved result bundles.
