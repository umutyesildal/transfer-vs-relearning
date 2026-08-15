# 38 - M1 Ranking Objective Follow-Up Plan

Date: 2026-07-09

## Purpose

This plan defines the second executable run inside the ranking-objective M1 branch.

The first pilot gave the first meaningful positive signal after the long CLM failure
sequence:

- direct top1 matched the best earlier plain small-model result,
- QA-matched top1 slightly improved,
- robust direct-and-QA overlap recovered to `5/500`.

That is not enough to promote M1, but it is enough to justify one disciplined follow-up
before changing families again.

## Why This Follow-Up Exists

The first ranking pilot showed a split pattern:

- the earliest checkpoint gave the best QA-matched score,
- later checkpoints gave the best direct score,
- the robust overlap stayed flat at `5/500`.

So the next experiment should try to move the direct score upward without washing out the
early QA gain.

The selected adjustment is:

- lower learning rate,
- moderate additional exposure,
- no change to objective, data mix, or model size.

## Selected Config

Training config:

```text
configs/training/m1_smollm2_360m_english_fact_ranking_lr1e-5_ep2.yaml
```

Key settings:

- model: `HuggingFaceTB/SmolLM2-360M`
- objective: ranking over one correct answer plus seven same-relation negatives
- prompt sources: English direct probes + English QA prompts
- learning rate: `1e-5`
- epochs: `2`
- train batch size: `4`
- grad accumulation: `2`
- scheduler: `cosine`
- checkpoint fractions: `0.25`, `0.5`, `0.75`, `1.0`

## Why This Exact Recipe

This is meant to land between the two obvious failure modes:

1. too short and too sharp, where QA improves briefly but direct retrieval does not move;
2. too long at the same step size, where the model keeps optimizing but collapses the early
   prompt-family balance.

Relative to the first ranking pilot:

- exposure increases from `1` epoch to `2` epochs,
- the step size drops from `2e-5` to `1e-5`.

So the run becomes more conservative per update while still giving the objective more room
to separate correct from incorrect candidates.

## Success Criterion

This follow-up is worth keeping only if it improves at least one meaningful English gate
without giving back the robust subset.

Priority targets:

- direct top1 greater than `0.014`,
- QA-matched top1 at least `0.016`,
- robust direct-and-QA overlap at least `5/500`.

Stretch target:

- robust overlap greater than `5/500`.

## Validation Before Launch

Required focused tests:

```text
tests/test_training_core.py
tests/test_training_ranking.py
```

Required HU preflight:

- pull latest `corpus-update`,
- rerun the same focused tests,
- submit the ranking Slurm wrapper with the new config path.

## Planned Evaluation

After training completes:

1. evaluate every retained checkpoint under English direct prompts,
2. evaluate every retained checkpoint under English QA-matched prompts,
3. compare against:
   - the original plain SmolLM2 baseline,
   - the high-exposure plain retry,
   - the first ranking pilot.

## Decision Rule After This Run

If this follow-up does not improve the English learned-fact gate materially, then the next
change should not be another tiny ranking hyperparameter tweak.

At that point we should either:

- change the training family more substantially,
- or open a larger-model ranking branch with a clearer scientific justification.
