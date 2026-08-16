# eval-v1 — M0/M1/M2 sibling evaluation contract

**Status:** `frozen` | **Owner:** project | **Created:** 2026-08-15 | **Frozen:** 2026-08-16
**Supersedes:** none

## Purpose and estimands

eval-v1 will apply one measurement system to M0, M1, M2-A and M2-B. It separates:

1. M1 factual acquisition: M1 minus M0;
2. M2-A transfer: TR→EN(M2-A) minus TR→EN(M1);
3. M2-B relearning: TR→EN(M2-B) minus TR→EN(M2-A);
4. English retention and Turkish adaptation manipulation checks.

No universal aggregate score is defined.

## Scope and prohibitions

This contract defines prospective semantics only. It does not authorize dataset/model retrieval,
evaluation or scoring, HU/SSH, Slurm/GPU, training, corpus materialization, cleanup, publication or
push. Historical outputs remain immutable and attached to their original contracts.

## Immutable identities

- design inputs: Documents 177 and 178;
- machine registry:
  [`../../../configs/evaluation/eval_v1_registry.yaml`](../../../configs/evaluation/eval_v1_registry.yaml);
- scientific inputs:
  [`../../../configs/evaluation/eval_v1_scientific_inputs_v1.yaml`](../../../configs/evaluation/eval_v1_scientific_inputs_v1.yaml);
- LM Evaluation Harness: v0.4.12, commit
  `6d642546f4688648fced259eb3302efd36ece5af`;
- base/pretrained causal-LM prompts: no chat template or system instruction;
- project bootstrap: 10,000 paired draws, seed 42;
- factual registry manifest:
  [`../../../configs/evaluation/registries/eval_v1_factual_registry_manifest.json`](../../../configs/evaluation/registries/eval_v1_factual_registry_manifest.json).

The environment lock, exact public dataset revisions/content manifest, factual registries,
thresholds and cadence are frozen. A state execution contract must still bind the exact model,
checkpoint, precision route, fresh output namespace and epoch/update map before execution.

## Architecture

```text
checkpoint manifest
  ├── LM Eval lane: public retention/capability tasks
  ├── project lane: factual access and generation integrity
  └── normalizer: immutable raw artifacts → typed long tables → trajectory view
```

The harness does not replace the factual evaluator. The factual evaluator does not reimplement
standard public tasks. The normalizer contains no scoring logic beyond declared derived deltas,
ratios, gaps and aggregates.

## Protocol

### Standard task lane

The final core is WikiText, Pile-10k, BLiMP, HellaSwag, the three WinoGender slices and TurBLiMP.
The exact active Harness task IDs are `wikitext`, `pile_10k`, `blimp`, `hellaswag`,
`winogender_female`, `winogender_male`, `winogender_neutral` and `turblimp_core`. TurkishMMLU is
excluded from eval-v1 because its dataset requires author contact and no exact accessible revision
was available before freeze. XCOPA-TR was not promoted from reserve. Adding either requires
eval-v2. Exact task
roles and metric semantics are in
[`../../evaluation/LM_EVAL_TASK_QUALIFICATION_V1.md`](../../evaluation/LM_EVAL_TASK_QUALIFICATION_V1.md).

BPB is the primary retention unit. Word PPL and byte PPL are always reported. Raw token PPL is not
used to rank different tokenizers. Official task preprocessing is unchanged; alternate WikiText
heading formatting is sensitivity-only.

Retention reports the raw checkpoint BPB, raw parent BPB and `ΔBPB = checkpoint − parent` as the
primary comparison. Word/byte PPL and `PPL checkpoint / PPL parent` are companion quantities. A
BPB ratio is diagnostic-only because BPB is already logarithmic. `100 / PPL ratio` may be labelled
`retention_score` in plot data only; it is not a percentage of retained facts and never defines a
scientific gate.

Pinned Harness v0.4.12 defines TurBLiMP `acc_norm` using log-likelihood divided by Python Unicode
string length. UTF-8-byte-normalized accuracy is a separately labelled sensitivity and must never
be substituted for upstream `acc_norm`. The group decision metric is the unweighted macro across
the exact 16 equal-size subtasks.

### Project factual lane

- mean answer-token log probability is the primary candidate score;
- total answer-token log probability is sensitivity-only;
- ties use canonical object ID;
- directions are EN→EN, TR→EN and TR→TR;
- the full suite covers Forms A–D and direct/QA scaffolds;
- report top-1, relation/form/scaffold cells, worst cell, robust fact intersection, margins and
  same-subject relation swaps;
- exact-prefix generation is secondary where an exact rule exists;
- paired subject bootstrap is the causal uncertainty unit.

The full registry contains 12,000 probes: 500 facts × three directions × four forms × two
scaffolds. The dense registry contains 1,500 probes: exactly one deterministically counterbalanced
form/scaffold probe for every fact in every direction. At a full-suite checkpoint, dense metrics
are derived from the matching full rows and are not rescored.

### Generation integrity lane

Report lexical-empty, near-empty, early EOS, repeated 3/4-grams, distinct-1/2/3, longest repeated
token run, synthetic-subject intrusion and frozen generic-completion accuracy. Near-empty length is
not silently merged with lexical-empty output.

## Cadence

For every future run, the parent and every epoch end receive the dense identity, factual,
retention and generation panel. Each epoch must therefore leave a model-only snapshot with a
content inventory and checkpoint hash. Separately precommitted milestone checkpoints retain
optimizer, scheduler and RNG state for resume. The full factual and capability bundle runs at
state entry, normalized progress 0.5 and endpoint 1.0.

For the historical OLMo trajectory, dense steps are `0/42/84/126/168/210/252` and full steps are
`0/126/252`, corresponding to epochs `0/6/12/18/24/30/36` for the dense points. The missing epoch
weights do not exist and must not be reconstructed, interpolated or reported as measurements.
Future training contracts must bind every epoch to an exact update before outcomes. If progress
0.5 is not an integer epoch, its checkpoint mapping is frozen before training.

Pile-10k is full-cadence only at state entry, midpoint and endpoint. All 10,000 frozen rows are
used; `--limit` is forbidden for scientific results. WikiText remains dense at every epoch end.
Each future training contract must bind every epoch and the exact integer midpoint update before
training; interpolation is forbidden.

## Inputs, outputs and schemas

Each evaluation uses a fresh namespace and a complete model/tokenizer/checkpoint manifest. Raw
harness and project outputs are immutable. Canonical normalized artifacts follow
[`../../evaluation/RESULT_SCHEMA_V1.md`](../../evaluation/RESULT_SCHEMA_V1.md).

A human one-row-per-checkpoint CSV is generated from the canonical long tables. It is never edited
or used as the provenance source.

Every future training run must also emit a trace manifest, append-safe optimizer-log events, one
complete epoch-end row per epoch and one model-only snapshot inventory per epoch. Required trace
fields cover static hyperparameters, effective batch, sequence/token statistics, padding and
truncation, cumulative examples/fact exposures/supervised and total tokens, loss/LR/gradient norm,
epoch/update identity and checkpoint hash. Epoch snapshots require a fail-closed storage preflight.

The default pipeline order is `identity preflight → train and trace → dense evaluation → full
evaluation → normalization → presentation bundle`. Required presentation inputs are generated from
canonical tables, never copied by hand: `trajectory_wide.csv`, `hyperparameters.csv`, plot-data
tables, figure status/identity manifest and metadata-complete captions. A missing or invalid result
remains visible and prevents a complete figure status.

## Scientific decision rules

All thresholds below are frozen before scientific M0 outcomes:

- M1 EN→EN exact-prefix accuracy must be at least `0.90`;
- trained Forms A/B and held-out Forms C/D top-1 accuracy must each be at least `0.80` globally and
  within every relation;
- the EN→EN eight-cell robust fact intersection must be at least `0.70` globally and within every
  relation;
- WikiText and Pile-10k must each satisfy `ΔBPB ≤ log2(1.25) = 0.32192809488736235` relative to the
  parent; BLiMP accuracy and HellaSwag `acc_norm` may each drop by at most `0.05`; WinoGender is
  diagnostic and has no gate;
- M2 primary in-domain Turkish byte PPL must be at most `0.95×` M1, equivalently
  `ΔBPB ≤ log2(0.95) = -0.07400058144377693`; TurBLiMP `acc_norm` may drop by at most `0.05` and the
  frozen trwiki cross-domain control must always be reported;
- M2 EN→EN top-1 and robust-intersection accuracy may each drop by at most `0.05` from M1;
- transfer is TR→EN(M2-A) − TR→EN(M1), and relearning is TR→EN(M2-B) − TR→EN(M2-A); each requires
  a point gain of at least `0.05` and a paired-subject 95% bootstrap lower bound strictly above
  zero;
- the transfer fallback for an already-open M1 baseline requires M2-A TR→EN at least `0.30` and no
  drop greater than `0.05`;
- bootstrap uses 10,000 draws and seed 42; every required seed must independently satisfy the same
  point and interval rule;
- checkpoint selection is the earliest precommitted checkpoint passing every required gate.

M2-A and M2-B use the same M1 parent, task bundle, cadence and comparison budget. Capability
benchmarks are manipulation/retention evidence, not replacements for the factual estimands.

## Gates and missingness

Structural gates precede scores: exact identities, offline inputs, task validation, output
namespace freshness, model/checkpoint match, finite logits and complete denominators. A failure
before scoring is `failed_pre_scoring`, not a scientific score.

Only `complete` rows enter comparisons. `not_run`, `failed_pre_scoring`, `partial_invalid` and
`not_in_contract` remain explicit. Missing results are never zero-filled, omitted from a required
aggregate or rerun outcome-aware. A required incomplete task keeps the checkpoint/family summary
open.

## Preflight, resume and rollback

- run `lm-eval ls` and `lm-eval validate` in the pinned environment;
- verify exact dataset revisions/content manifests and offline reload;
- verify task YAML hashes and resolved task configs;
- verify model/tokenizer/checkpoint hashes and precision route;
- resume only when the full identity fingerprint matches;
- completed raw namespaces are immutable; repair writes a fresh namespace;
- normalization is idempotent and rejects duplicate metric keys.

## Verification before freeze

1. OLMo base smoke for every final task — complete in the qualification bundle.
2. Canonical WikiText count/result parity and bounded heading sensitivity — complete in Document
   179.
3. Pile-10k exact 10,000-row offline identity and full-cadence decision — complete.
4. TurBLiMP 16-subtask macro parity — complete in Document 179.
5. TurkishMMLU exclusion — complete before freeze.
6. Cheap/full factual registry generation, source projection and denominator tests — complete.
7. Harness-to-normalized fixtures, resume mismatch and partial-result tests — complete in the
   existing qualification/controller suite.
8. Numerical margins and per-training-contract checkpoint-binding policy — complete.

Document 180 records the freeze evidence. Qualification metrics remain test-only and do not become
scientific results through contract freeze.

## Authority boundary

An exact separately authorized wave is required for evaluation, HU/SSH, Slurm/GPU or training.
This frozen measurement contract authorizes none of them.

## Change policy

After freeze, any task, dataset revision, split, prompt, few-shot count, preprocessing, metric,
denominator, threshold, cadence, seed policy or comparison rule creates eval-v2. A runtime-only
repair may remain eval-v1 only with explicit semantic-equivalence evidence and an append-only
record. Historical results are never relabelled as eval-v1 without compatibility proof.
