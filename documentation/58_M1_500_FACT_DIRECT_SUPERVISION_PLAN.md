# 58 - M1 500-Fact Direct-Supervision Plan

Last updated: 2026-07-11

## Decision

The direct-aware acquisition recipe passed at 50 facts across all five relations. The next
nested level increases subject count from 10 to 100 and fact count from 50 to 500 while
preserving the same subject selection hierarchy, seven-row format contract, and per-row
exposure.

## Dataset Contract

- subjects: 100
- facts: 500
- relations: 5, 100 facts each
- rows per fact: 7
- train rows: 3,500
- held-out direct validation rows: 500
- train/validation exact text overlap: 0
- 10-subject diagnostic selection is a strict subset of this level
- full relation-specific candidate inventories remain unchanged

## Matched Training Budget

- base model: SmolLM2-360M
- full-parameter training
- answer-only loss
- epochs: 36
- micro-batch size: 50
- gradient accumulation: 10
- effective batch size: 500
- optimizer steps: 252
- learning rate: `1e-4`
- constant-with-warmup scheduler
- no weight decay
- block size: 128

The A100 memory profile was already validated at micro-batch 50. Gradient accumulation keeps
the optimizer-update count equal to the successful 50-fact run while every row is still seen
36 times. The run performs ten times more forward/backward micro-steps, as required by the
tenfold increase in examples.

## Initial Evaluation Wave

Evaluate only checkpoints:

- `checkpoint-25`
- `checkpoint-50`
- `checkpoint-75`

Each checkpoint receives exact-prefix, held-out direct, and held-out QA evaluation. Expand
to later checkpoints only if the first wave does not resolve the progression decision.

## Precommitted Gate

A checkpoint passes only if all conditions hold:

- exact-prefix top-1 at least 450/500;
- held-out direct top-1 at least 400/500;
- held-out QA top-1 at least 400/500;
- direct/QA top-1 overlap at least 350/500.

Report each relation separately over 100 facts and retain relation-binding analysis for
`born_in`/`lives_in`.

Interpretation:

- pass: the corrected acquisition recipe scales beyond the diagnostic micro-set; proceed to
  the 500-subject / 2,500-fact nested level;
- exact remains high but prompt views fall: extraction robustness degrades with subject scale;
- global exact degradation: storage/interference becomes limiting between 50 and 500 facts;
- isolated relation degradation: adjust only that relation's format bank before further scale.

Do not launch 2,500 facts before this gate is documented.

