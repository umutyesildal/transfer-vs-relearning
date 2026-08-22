# M1 measurement review ledger — pre-contract draft

**Date:** 2026-08-22  
**Status:** draft for review; not an execution contract  
**Gate:** `blocked_by_measurement_design`  
**Scoring/training:** not authorized or run

## Purpose

This ledger distinguishes values already frozen by eval-v2 from values that 151ab requires as
explicit M1 design decisions. It prevents inherited thresholds from being mistaken for complete
held-out split, overlap or benchmark-calibration evidence.

## Five mandatory 151ab review fields

| Field | Local evidence | Status | Why it cannot be inferred |
|---|---|---|---|
| `turkish_heldout_v1.sha256` | `trwiki-20260601` cross-domain control hash exists; primary in-domain split does not | `REVIEW_REQUIRED` | control corpus is explicitly not the primary adaptation-corpus held-out split |
| `english_retention_v1.sha256` | WikiText repository/revision and M0 eval-v2 identity exist | `REVIEW_REQUIRED` | the review field binds the exact retention manifest/bytes, not only the dataset revision |
| `delta_TurBLiMP_equivalence_margin` | eval-v2 has an absolute-drop gate of `0.05` | `REVIEW_REQUIRED` | an inherited drop threshold is not a reviewed equivalence/no-harm margin for the new causal comparison |
| `delta_EN_retention_margin` | eval-v2 freezes BPB/ratio and capability guardrails | `REVIEW_REQUIRED` | 151ab requires separate reviewed LM-loss and EN→EN directional margins |
| `benchmark_floor_ceiling_saturation_rule` | no complete local calibration rule | `REVIEW_REQUIRED` | chance/floor/ceiling must be predeclared before benchmark results |

## Expanded pre-execution ledger

### Benchmark and rendering identity

Still required per exact benchmark/model pairing:

```text
item-set byte SHA-256
ordered item-ID manifest SHA-256
exact path and split
prompt template and render rule
choice template and choice-order rule
TurBLiMP pair/scoring rule
TurkishMMLU subject selection and dev/test manifest
Turkish EXAMS language subset and split manifest
evaluator revision and code SHA-256
```

The M0 `juletxara` Harness route and the 151ab `ezgibasar` overlay are both preserved, but one
must be selected for the M1 role before scoring. TurkishMMLU and EXAMS are not active eval-v2
tasks, so their historical presence is not an execution binding.

### Model and tokenization identity

```text
base-model artifact manifest SHA-256 by model/state
tokenizer artifact manifest SHA-256 by model/state
base-model/evaluator compatibility
BOS/EOS and answer-masking rule
context length, truncation and sliding-window rule
document boundary/reset rule
```

The model provenance memo records the current role/revision evidence and the remaining missing
manifest fields. No model load or acquisition is used to fill them in this draft.

### NLL, retention and uncertainty

```text
NLL aggregation unit and byte/character denominator
primary Turkish in-domain manifest and file-byte hash
trwiki control manifest and file-byte hash
English retention manifest and file-byte hash
paired unit and missing-item policy
bootstrap resample count, seeds and CI method
```

The prospective M1 table keeps raw BPB as the primary English retention value, byte PPL/PPL ratio
as companion evidence and `100 / PPL ratio` as visualization-only. No retention score substitutes
for the raw values or the predeclared CI decision.

## Proposed review order

1. Decide whether M1 uses the M0 continuity TurBLiMP route, the independent 151ab route, or two
   separately labelled outcomes.
2. Bind the primary in-domain Turkish held-out role without replacing it with `trwiki-20260601`.
3. Review the two directional English margins and the TurBLiMP no-harm/equivalence margin.
4. Freeze floor/ceiling and overlap rules before any benchmark score.
5. Attach exact model/tokenizer artifact manifests and fixed checkpoint identities.

## Decision

This ledger is a review aid only. It does not rewrite eval-v2, add tasks, select a model, create a
corpus, open HU/Slurm or authorize M1. The M1 training contract remains blocked until every
`REVIEW_REQUIRED` field has an exact value, source/reference and immutable hash where required.
