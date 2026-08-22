# M1 benchmark identity reconciliation — TurBLiMP and Turkish secondary tasks

**Date:** 2026-08-22  
**Status:** decision memo; no protocol rewrite  
**Gate:** `blocked_by_benchmark_registry` / `blocked_by_measurement_design`  
**Execution:** none

## Why this memo exists

The read-only audit found two valid-looking but non-identical TurBLiMP identities. They must not
be silently merged, because the M0 parity result and the proposed M1 independent diagnostic would
then refer to different item/evaluator populations.

## Two identities that must remain separate

| Use | Identity | Evidence | Meaning |
|---|---|---|---|
| M0/eval-v2 continuity and historical parity | `juletxara/turblimp`, revision `cce94ca73ac04a0fabd9fbd7a56068261e6348ad` | `configs/evaluation/eval_v2_scientific_inputs_v1.yaml`; eval-v1 registry; Document 179 parity | the exact Harness route used by the qualified M0 lane |
| 151ab proposed independent M1 linguistic diagnostic | `https://github.com/ezgibasar/TurBLiMP`, overlay commit `297de13fb7a0ce524fe32e8b175c6b5255d66960`, `data/base/` 16-file allowlist, evaluator blob `c386def30cfdcbab4cd4366ef5805ab6ce4ae26a` | Document 151q effective overlay and Document 151ab | a separate frozen design identity; overall registry gate still blocked |

The second identity’s overlay is preserved in the historical 151q chain, but the 151q execution
and coverage gates did not produce a complete evidence-complete registry. “Overlay frozen” is not
the same as “M1 benchmark gate passed.”

## TurkishMMLU and EXAMS role status

- TurkishMMLU and Turkish EXAMS were excluded from the frozen eval-v1 active task set because exact
  access/coverage was unresolved.
- 151ab retains them as potential secondary Turkish capability/knowledge diagnostics with explicit
  identity and evaluator requirements.
- They are not active eval-v2 lanes today. Adding them to M1 requires a new measurement decision,
  exact item/split/evaluator manifests and a new SHA-bound contract; it cannot be inferred from
  their appearance in historical 151q documents.

## Reconciliation decision

1. Keep the `juletxara` route immutable for M0/eval-v2 continuity and never rewrite historical
   parity results.
2. Keep the 151ab GitHub overlay as a separate M1 candidate until its evidence-complete registry
   and independent-vs-continuity role are reviewed.
3. Do not change `eval_v2_registry.yaml`, add TurkishMMLU/EXAMS lanes, or create an M1 contract in
   this memo.
4. Before M1 execution, select one explicit TurBLiMP role (continuity task, independent primary,
   or both as separately labelled outcomes), bind exact item/evaluator hashes, and predeclare the
   comparison interpretation.

## Consequence

The benchmark blocker remains open, but the ambiguity is now localized to a concrete design
decision rather than hidden in a generic “TurBLiMP missing” note. No benchmark scoring or network
retrieval occurred; no HU or prior root was touched.
