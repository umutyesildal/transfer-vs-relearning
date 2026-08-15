# 52 - M1 Single-Fact Direct-Supervision Plan

Last updated: 2026-07-10

## Decision

The first single-fact diagnostic proved exact-prefix storage and held-out QA extraction, but
the scaffold-free direct probe remained at rank 4. This follow-up changes only the direct
format supervision boundary for the same fact.

Controlled fact:

```text
Augusta Rodriquez -> born_in -> Van
```

No new subject, relation, answer, model, or candidate is introduced.

## Data Difference

The original five rows remain:

- three declarative rows;
- two `Question/Answer` rows.

Two direct-format rows are added:

```text
Where was Augusta Rodriquez born? Van
Which place is recorded as Augusta Rodriquez's birthplace? Van
```

The held-out direct validation/evaluation form is:

```text
What is the birthplace of Augusta Rodriquez? Van
```

The held-out string does not appear in training.

## Matched Training Budget

The previous control used five rows for 50 epochs: 250 optimizer steps.

This follow-up uses seven rows for 36 epochs: 252 optimizer steps.

Unchanged settings:

- SmolLM2-360M base model;
- full-parameter training;
- answer-only loss;
- learning rate `1e-4`;
- constant-with-warmup schedule;
- no weight decay;
- batch size 1;
- block size 128.

## Evaluation And Gate

Every checkpoint is evaluated against the full city inventory using:

1. exact declarative prefix;
2. held-out direct question;
3. held-out QA-matched question.

The follow-up passes only if one checkpoint ranks `Van` first in all three views. Select the
earliest passing checkpoint.

Interpretation:

- all views pass: direct extraction is teachable with format coverage; proceed to a
  single-relation diagnostic using the same controlled format mix;
- exact and QA pass but direct still fails: the current direct objective or prompt boundary
  remains misaligned;
- QA regresses: direct supervision damages the previously successful scaffolded extraction;
- exact regresses: the format mix destabilizes basic storage.

This is a diagnostic of prompt robustness, not permission to launch the 100-subject level.

