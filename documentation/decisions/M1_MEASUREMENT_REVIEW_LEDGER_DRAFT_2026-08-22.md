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

## Current operational binding (read-only, 2026-08-22)

The implementation route is now identified without opening execution. These bindings can be
carried into the later contract; they are not a training authorization:

| Binding | Frozen value |
|---|---|
| eval-v2 registry | `configs/evaluation/eval_v2_registry.yaml` — SHA-256 `0721412c651f5b112f531e69b53c98ccdb3633bee4888571bd7039d3f693229d` |
| scientific inputs | `configs/evaluation/eval_v2_scientific_inputs_v1.yaml` — SHA-256 `e6afb5ed3cd210d9c429622995ccbf8a0da5fee4cf444e6fc979d8377d68b879` |
| Harness | `lm_eval` v0.4.12, commit `6d642546f4688648fced259eb3302efd36ece5af`, immutable offline environment |
| active lanes | WikiText, BLiMP, HellaSwag, WinoGender (3 roles), TurBLiMP; project-native factual and integrity lanes remain mandatory |
| Turkish route | `juletxara/turblimp` at `cce94ca73ac04a0fabd9fbd7a56068261e6348ad`; `trwiki-20260601` is cross-domain control only |
| retired input | Pile-10k is excluded from M1 and cannot be reintroduced by “all M0 evals” |
| synthetic facts | Relation V2 `100 subjects / 500 facts / 3,500 train rows`, manifest SHA-256 `b37268d6f3afbb37f13ef746b80b99169c4d94ced3471aed2ae4aa09dc85b752` |
| exact-prefix registry | `exact_prefix_probes_en.csv`, SHA-256 `1644288d0d62c51c56ceaae71b9eef7225b88326267281c8df8aeef9d7619c8e` |
| historical launcher | `account=yesildau`, `partition=gpu`, prior A100 route, `xfer-relearn`, `scripts/training/train_clm.py` |

The fixed prospective cohort is OLMo-2-0425-1B, Qwen2.5-1.5B and SmolLM2-1.7B. Their recorded
read-only source-manifest hashes are respectively
`8702b80d5b7e4c996c8ce2ff5fe771ada08ab0080bde1926c0b1f53c607303dc`,
`c9d3562b717784251fe14c2b7972660fe4a20fe4687e15f69746bc1713d2d4fb` and
`e5d04302087b8b41828f734c1d88c4620a74bb80d6919de62df37b9d57dadbfc`.

The three draft training configurations preserve one matched recipe (seed 42, 36 epochs,
7 updates/epoch, effective batch 500, block size 128, answer-only masking, epoch-end model-only
snapshots and fact-exposure trace). The three draft trajectory pipelines preserve the same eval-v2
registry, exact-prefix registry and entry/midpoint/endpoint full-bundle cadence. Their
`m1_checkpoint_manifest` and `m1_training_manifest` fields intentionally remain placeholders:
those manifests do not exist until a separately authorized run creates them.

## Immediate decision boundary

The next useful action is not another historical launcher submission. Before an executable M1
contract can be written, the following five cells must be reviewed and filled with a source and,
where applicable, a hash:

1. primary in-domain Turkish held-out split;
2. exact English retention manifest/bytes;
3. TurBLiMP no-harm/equivalence margin;
4. English-retention directional margin;
5. benchmark floor/ceiling/saturation rule.

Once those cells are closed, we can bind the already prepared three-model recipe and trajectory
pipelines into one SHA-closed contract, run local/HU preflight, and request a separate execution
authorization. Until then, `ready_to_train=false` remains intentional and no checkpoint or metric
is fabricated.
