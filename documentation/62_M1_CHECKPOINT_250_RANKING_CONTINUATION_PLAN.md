# 62 - M1 Checkpoint-250 Ranking Continuation Plan

Last updated: 2026-07-11

## Decision

The next controlled 500-fact remediation is a short candidate-ranking continuation from the
already acquired checkpoint 250. This is not a return to the earlier ranking pilot: the old
pilot started from the base model before reliable fact storage existed, while this branch
starts from a checkpoint with 451/500 exact-prefix top-1 facts.

## Hypothesis

The checkpoint-250 audit found concentrated relation-level candidate priors:

- `19 Mayis Universitesi` dominates `studied_at` errors;
- `3M` dominates `works_at` errors;
- most weak-relation misses still place the correct answer at ranks 2-5.

The model therefore appears to store many answers but fails to bind the subject strongly
enough when comparing candidates. A low-learning-rate discrimination continuation may move
the correct subject-specific object above the relation-level default without relearning M1
from scratch.

## Controlled Change

Held constant:

- SmolLM2-360M architecture;
- the same 100 subjects and 500 facts;
- the same seven English training formats per fact;
- the same exact, held-out direct, and QA evaluation files;
- mean-logprob scoring and the existing 450/400/400/350 gate.

Changed:

- initialization: checkpoint 250 rather than the base model;
- objective: candidate-ranking cross-entropy rather than answer-only CLM;
- each training prompt compares one correct answer with 15 same-relation negatives.

## Leakage Control

The ranking source is only:

```text
artifacts/datasets/acquisition_diagnostics_v1/
all_relations_100_subjects_direct_supervision/train.jsonl
```

The held-out validation/direct and QA evaluation prompts are not training sources. Negative
selection is deterministic `balanced_cycle` over canonical relation inventories; no negative
is selected from checkpoint-250 evaluation errors. This prevents adaptive use of the held-out
results.

## Dataset Contract

- ranking examples: 3,500;
- examples per relation: 700;
- prompts per fact: 7;
- candidates per example: 16 total;
- university inventory coverage as negatives: 91/91;
- employer inventory coverage as negatives: 241/241;
- internal validation split: 0, because held-out external probes are the decision criterion.

## Training Recipe

- base checkpoint: `checkpoint-250`;
- learning rate: `5e-6`;
- epochs: 1;
- micro-batch: 2;
- gradient accumulation: 5;
- effective example batch: 10;
- optimizer updates: 350;
- scheduler: constant with 5% warmup;
- weight decay: 0;
- score mode: mean log-probability;
- checkpoint interval: 35 optimizer updates, including the final update.

Config:

```text
configs/training/m1_smollm2_360m_acquisition_500_facts_ranking_continuation_lr5e-6_ep1.yaml
```

## Evaluation And Stop Rule

Evaluate early and middle checkpoints before assuming the final checkpoint is best. Every
selected checkpoint must be tested on exact-prefix, held-out direct, and QA-matched views.

Promotion still requires all four precommitted conditions:

- exact-prefix at least 450/500;
- held-out direct at least 400/500;
- QA-matched at least 400/500;
- direct/QA overlap at least 350/500.

The continuation must also be compared against checkpoint 250's 265/500 triple-robust subset
and its concentrated candidate-collapse errors. If ranking improves prompt views but destroys
exact storage, it is not promoted.

## Operations

Submit once, record the job ID and initial queue state, report average and safe duration, and
leave Slurm running without a local sleep command. Evaluation begins only after the training
run is complete and documented.
