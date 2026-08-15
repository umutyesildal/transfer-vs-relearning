# eval-v1 — M0/M1/M2 sibling evaluation contract

**Status:** `draft` | **Owner:** project | **Created:** 2026-08-15  
**Supersedes:** none

## Purpose and estimands

eval-v1 will apply one measurement system to M0, M1, M2-A and M2-B. It separates:

1. M1 factual acquisition: M1 minus M0;
2. M2-A transfer: TR→EN(M2-A) minus TR→EN(M1);
3. M2-B relearning: TR→EN(M2-B) minus TR→EN(M2-A);
4. English retention and Turkish adaptation manipulation checks.

No universal aggregate score is defined.

## Scope and prohibitions

This draft defines prospective semantics only. It does not authorize dataset/model retrieval,
evaluation or scoring, HU/SSH, Slurm/GPU, training, corpus materialization, cleanup, publication or
push. Historical outputs remain immutable and attached to their original contracts.

## Immutable identities at draft stage

- design inputs: Documents 177 and 178;
- machine registry:
  [`../../../configs/evaluation/eval_v1_registry.yaml`](../../../configs/evaluation/eval_v1_registry.yaml);
- LM Evaluation Harness: v0.4.12, commit
  `6d642546f4688648fced259eb3302efd36ece5af`;
- base/pretrained causal-LM prompts: no chat template or system instruction;
- project bootstrap: 10,000 paired draws, seed 42.

Exact dataset revisions, environment lock, probe registries, model/runtime bindings and numerical
thresholds remain freeze blockers. Their absence keeps this contract non-executable.

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

The proposed core is WikiText, Pile-10k, BLiMP, HellaSwag, WinoGender slices, XNLI-EN,
TurBLiMP and XNLI-TR. TurkishMMLU is included only if access is resolved before freeze. Exact task
roles and metric semantics are in
[`../../evaluation/LM_EVAL_TASK_QUALIFICATION_V1.md`](../../evaluation/LM_EVAL_TASK_QUALIFICATION_V1.md).

BPB is the primary retention unit. Word PPL and byte PPL are always reported. Raw token PPL is not
used to rank different tokenizers. Official task preprocessing is unchanged; alternate WikiText
heading formatting is sensitivity-only.

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

### Generation integrity lane

Report lexical-empty, near-empty, early EOS, repeated 3/4-grams, distinct-1/2/3, longest repeated
token run, synthetic-subject intrusion and frozen generic-completion accuracy. Near-empty length is
not silently merged with lexical-empty output.

## Cadence

Every precommitted checkpoint, including the parent, receives the dense identity, factual,
retention and generation panel. The full factual and capability bundle runs at state entry,
normalized progress 0.5 and endpoint 1.0.

For the historical OLMo trajectory, dense steps are `0/42/84/126/168/210/252` and full steps are
`0/126/252`. Future training contracts must bind exact updates to the same normalized cadence
before outcomes. If progress 0.5 is not a saved checkpoint, the mapping is frozen before training.

Pile-10k cadence remains unresolved until measured runtime is known. A cheap scientific subset may
not use `--limit`; it requires an explicit frozen sample-ID registry.

## Inputs, outputs and schemas

Each evaluation uses a fresh namespace and a complete model/tokenizer/checkpoint manifest. Raw
harness and project outputs are immutable. Canonical normalized artifacts follow
[`../../evaluation/RESULT_SCHEMA_V1.md`](../../evaluation/RESULT_SCHEMA_V1.md).

A human one-row-per-checkpoint CSV is generated from the canonical long tables. It is never edited
or used as the provenance source.

## Scientific decision rules

- M1 selection may use only a precommitted rule such as the earliest checkpoint satisfying all
  acquisition, robustness and retention guardrails.
- Transfer uses the paired M2-A−M1 TR→EN contrast.
- Relearning uses the paired M2-B−M2-A TR→EN contrast.
- M2-A and M2-B must have the same M1 parent, task bundle, checkpoint cadence and comparison budget.
- Capability benchmarks are manipulation/retention evidence, not a replacement for the factual
  causal estimand.
- A replicated causal claim requires the frozen sign/confidence rule at every required seed.

Numeric acquisition, retention, Turkish-manipulation and English non-inferiority margins must be
set before freeze. Historical thresholds, including token-PPL ratio `1.25`, are not automatically
portable to official BPB.

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

1. OLMo base smoke for every final task.
2. Canonical WikiText count/result parity and bounded heading sensitivity.
3. Pile-10k runtime and final cadence evidence.
4. TurBLiMP 16-subtask macro parity despite the upstream duplicate YAML key.
5. TurkishMMLU access inclusion/exclusion decision.
6. Cheap/full factual registry hashes and denominator tests.
7. Harness-to-normalized golden fixture, resume mismatch and partial-result tests.
8. Reviewed numerical margins and exact training checkpoint bindings.

## Authority boundary

Even after freeze, an exact separately authorized wave is required for retrieval, evaluation,
HU/SSH, Slurm/GPU or training. This draft authorizes none of them.

## Change policy

After freeze, any task, dataset revision, split, prompt, few-shot count, preprocessing, metric,
denominator, threshold, cadence, seed policy or comparison rule creates eval-v2. A runtime-only
repair may remain eval-v1 only with explicit semantic-equivalence evidence and an append-only
record. Historical results are never relabelled as eval-v1 without compatibility proof.
