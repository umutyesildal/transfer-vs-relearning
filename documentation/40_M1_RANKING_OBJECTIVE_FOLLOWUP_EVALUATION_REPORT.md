# 40 - M1 Ranking Objective Follow-Up Evaluation Report

Date: 2026-07-09

## Purpose

This report records English checkpoint evaluation for the second ranking-objective M1 run.

## Evaluated Training Run

Training run:

```text
runs/training/m1_smollm2_360m_english_fact_ranking/20260709T060700Z_m1_smollm2_360m_english_fact_ranking_lr1e-5_ep2_0b3462e1
```

Retained checkpoints:

- `checkpoint-3444`
- `checkpoint-6888`
- `checkpoint-10332`
- `checkpoint-13776`
- `checkpoint-13778`

## Submitted Eval Jobs

- `389515` - `checkpoint-3444` direct
- `389516` - `checkpoint-3444` QA-matched
- `389517` - `checkpoint-6888` direct
- `389518` - `checkpoint-6888` QA-matched
- `389519` - `checkpoint-10332` direct
- `389520` - `checkpoint-10332` QA-matched
- `389521` - `checkpoint-13776` direct
- `389522` - `checkpoint-13776` QA-matched
- `389523` - `checkpoint-13778` direct
- `389524` - `checkpoint-13778` QA-matched

All ten evaluation outputs were produced.

## Metrics Summary

English-only summary over the 500 evaluated facts:

- `checkpoint-3444`
  - direct top1: `0.002`
  - QA-matched top1: `0.012`
  - robust direct-and-QA overlap: `1/500`
- `checkpoint-6888`
  - direct top1: `0.004`
  - QA-matched top1: `0.014`
  - robust direct-and-QA overlap: `1/500`
- `checkpoint-10332`
  - direct top1: `0.004`
  - QA-matched top1: `0.014`
  - robust direct-and-QA overlap: `1/500`
- `checkpoint-13776`
  - direct top1: `0.006`
  - QA-matched top1: `0.014`
  - robust direct-and-QA overlap: `2/500`
- `checkpoint-13778`
  - direct top1: `0.006`
  - QA-matched top1: `0.014`
  - robust direct-and-QA overlap: `2/500`

Best checkpoint views:

- best direct top1: `0.006` at `checkpoint-13776` and `checkpoint-13778`
- best QA-matched top1: `0.014` at `checkpoint-6888`, `checkpoint-10332`,
  `checkpoint-13776`, and `checkpoint-13778`
- best robust direct-and-QA overlap: `2/500`

## Comparison Against Earlier Branches

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

Ranking follow-up best result:

- direct top1: `0.006`
- QA-matched top1: `0.014`
- robust overlap: `2/500`

## Interpretation

This follow-up did not preserve the first ranking pilot's positive signal.

What got worse:

- direct top1 collapsed from `0.014` to `0.006`;
- QA-matched top1 fell from `0.018` to `0.014`;
- robust overlap fell from `5/500` to `2/500`.

The outcome is not just "no improvement." It is a real regression relative to:

- the first ranking pilot,
- the original plain SmolLM2 baseline on direct top1,
- and the first ranking pilot on the robust subset.

## Conclusion

Do not promote this follow-up checkpoint as final M1.

The useful lesson is narrower:

- changing the objective itself still looks more promising than extending CLM-only runs,
- but this specific lower-LR, longer ranking follow-up moved the branch in the wrong
  direction.

## Recommended Next Step

Do not keep making small hyperparameter tweaks inside this exact ranking setup.

The next branch should be a more substantive change, such as:

1. a larger-model ranking branch,
2. a different ranking data mix or candidate curriculum,
3. or a cleaner acquire-then-extract design with a stronger extraction stage.
