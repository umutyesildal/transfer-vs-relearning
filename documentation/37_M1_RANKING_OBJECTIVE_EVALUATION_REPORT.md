# 37 - M1 Ranking Objective Evaluation Report

Date: 2026-07-09

## Purpose

This report records English checkpoint evaluation for the first ranking-objective M1 pilot.

## Evaluated Training Run

Training run:

```text
runs/training/m1_smollm2_360m_english_fact_ranking/20260708T203650Z_m1_smollm2_360m_english_fact_ranking_lr2e-5_ep1_e5698316
```

Retained checkpoints:

- `checkpoint-1722`
- `checkpoint-3444`
- `checkpoint-5166`
- `checkpoint-6888`
- `checkpoint-6889`

## Submitted Eval Jobs

- `389464` - `checkpoint-1722` direct
- `389465` - `checkpoint-1722` QA-matched
- `389466` - `checkpoint-3444` direct
- `389467` - `checkpoint-3444` QA-matched
- `389468` - `checkpoint-5166` direct
- `389469` - `checkpoint-5166` QA-matched
- `389470` - `checkpoint-6888` direct
- `389471` - `checkpoint-6888` QA-matched
- `389472` - `checkpoint-6889` direct
- `389473` - `checkpoint-6889` QA-matched

All ten evaluation outputs were produced.

## Metrics Summary

English-only summary over the 500 evaluated facts:

- `checkpoint-1722`
  - direct top1: `0.010`
  - QA-matched top1: `0.018`
  - robust direct-and-QA overlap: `5/500`
- `checkpoint-3444`
  - direct top1: `0.014`
  - QA-matched top1: `0.012`
  - robust direct-and-QA overlap: `5/500`
- `checkpoint-5166`
  - direct top1: `0.014`
  - QA-matched top1: `0.010`
  - robust direct-and-QA overlap: `5/500`
- `checkpoint-6888`
  - direct top1: `0.014`
  - QA-matched top1: `0.010`
  - robust direct-and-QA overlap: `5/500`
- `checkpoint-6889`
  - direct top1: `0.014`
  - QA-matched top1: `0.010`
  - robust direct-and-QA overlap: `5/500`

Best checkpoint views:

- best direct top1: `0.014` at `checkpoint-3444`, `checkpoint-5166`, `checkpoint-6888`, and `checkpoint-6889`
- best QA-matched top1: `0.018` at `checkpoint-1722`
- best robust direct-and-QA overlap: `5/500`

## Comparison Against Prior Small-Model Branches

Original plain SmolLM2 baseline best result:

- direct top1: `0.014`
- QA-matched top1: `0.016`
- robust overlap: `3/500`

High-exposure plain SmolLM2 retry best result:

- direct top1: `0.010`
- QA-matched top1: `0.014`
- robust overlap: `2/500`

First ranking-objective pilot best result:

- direct top1: `0.014`
- QA-matched top1: `0.018`
- robust overlap: `5/500`

## Interpretation

This is the first small-model branch that recovers the earlier `5/500` robust overlap
without relying on the old QA-mixed CLM recipe family.

What improved:

- robust direct-and-QA overlap improved relative to both the plain baseline and the
  high-exposure retry;
- QA-matched top1 improved slightly over the original plain small-model baseline.

What did not improve:

- direct top1 did not beat the best previous plain small-model result;
- all mean margins remained negative, so retrieval is still weak in absolute terms.

## Conclusion

Do not yet promote this checkpoint as final M1.

But unlike the recent negative CLM-only branches, this is a meaningful positive signal:

- changing the objective helped the robust subset,
- the ranking diagnosis looks more plausible than the "just train longer" diagnosis,
- this branch is worth extending instead of discarding.

## Recommended Next Step

Stay on the ranking-objective family.

The most reasonable next move is:

1. keep the same ranking objective,
2. continue with a longer or slightly tuned follow-up run,
3. then compare whether direct top1 can move above `0.014` while keeping or improving the
   `5/500` robust overlap.
