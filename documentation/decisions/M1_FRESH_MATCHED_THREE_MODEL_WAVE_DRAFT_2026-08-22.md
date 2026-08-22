# M1 fresh matched three-model wave — draft

**Date:** 2026-08-22
**Status:** `DRAFT_NOT_AUTHORIZED`
**Scope:** local design and configuration only; no HU/SSH, Slurm, model loading, training or evaluation

## Decision shape

The prospective M1 wave starts from the frozen pretrained M0 parent of each fixed model. “Fresh”
means a new matched M1 run, not random initialization and not deletion or relabeling of historical
M1 artifacts. Historical runs remain read-only evidence and are not overwritten.

The fixed cohort is exactly:

| Model | Revision |
|---|---|
| OLMo-2-0425-1B | `a1847dff35000b4271fa70afc5db10fd29fedbdf` |
| Qwen2.5-1.5B | `8faed761d45a263340a0528343f099c05c9a4323` |
| SmolLM2-1.7B | `effd688a12921b4cc83e3312b6feb579f70f9c71` |

## Matched logical recipe

- synthetic English Relation V2 release: 100 subjects / 500 facts;
- 3,500 train rows / 500 validation rows / seven rows per fact;
- seed and data seed 42;
- 36 integer epochs, exactly seven optimizer updates per epoch and 252 total updates;
- block size 128;
- answer-only loss, `supervise_eos: false`;
- learning rate `5e-5`, constant-with-warmup (`warmup_ratio: 0.02`), zero weight decay;
- effective row batch 500;
- model-native microbatch and gradient accumulation may differ only to fit the fixed hardware
  route; effective batch and all scientific quantities remain 500;
- BF16 and optimizer/runtime semantics must be fixed before execution and cannot change silently.

The three draft training configs are:

- `configs/training/m1_matched_epoch_dense_olmo_seed42_draft.yaml`
- `configs/training/m1_matched_epoch_dense_qwen_seed42_draft.yaml`
- `configs/training/m1_matched_epoch_dense_smollm_seed42_draft.yaml`

## Checkpoint and trace policy

The M0 parent is `checkpoint-0`. Each of the 36 epoch ends writes one model-only snapshot at
updates `7, 14, ..., 252`. The training trace records the resolved recipe, tokenization audit,
cumulative examples, cumulative fact exposures, supervised/total tokens, learning rate, gradient
statistics and the snapshot SHA-256. Trainer optimizer checkpoints are limited to the final recovery
checkpoint; epoch snapshots are model-only to keep scratch storage bounded.

This creates 37 trajectory states per model and 111 states for the cohort. The review view is the
existing `documentation/evaluation/M1_TRAJECTORY_TABLE_V1.md` schema; no missing historical value
is interpolated or converted to zero.

## Evaluation policy

Every state receives the same eval-v2 identity and metric definitions:

- exact-prefix 500 probes;
- cheap factual access, robust A–D and relation-control metrics;
- English WikiText BPB/PPL and delta/ratio to the M0 parent;
- Turkish capability/retention controls and the pinned TurBLiMP route;
- generation integrity and the inherited LM Evaluation Harness task registry.

Cheap factual/retention/integrity bundles run at every state. The full bundle is precommitted at
parent, midpoint and endpoint (`0, 18, 36`). A full-at-every-epoch variant is intentionally not
implicit: it would expand the wave to hundreds of expensive lanes and requires a separate explicit
resource decision.

The three draft eval plans are:

- `configs/pipelines/m1_olmo_epoch_trajectory_draft.yaml`
- `configs/pipelines/m1_qwen_epoch_trajectory_draft.yaml`
- `configs/pipelines/m1_smollm_epoch_trajectory_draft.yaml`

They compose through `scripts/study/run_m1_eval.py` and remain fail-closed because model manifests,
training manifests, checkpoint registries and an execution adapter are still placeholders.

## Storage and execution boundary

All output must use fresh scratch roots. Retaining 36 model-only snapshots per model requires a
conservative shared reservation of approximately 350–450 GB plus runtime overhead; HU home is out
of scope. The existing historical M1 roots are read-only and are never cleaned by this draft.

This draft does not close the current `ready_to_train=false` gate, does not create an execution
authorization, and does not permit HU/SSH, Slurm, GPU, training or evaluation. A later contract must
bind exact model/tokenizer manifests, dataset and exact-prefix hashes, storage capacity, hardware
precision, checkpoint roots and the execution adapter before any wave is submitted.
