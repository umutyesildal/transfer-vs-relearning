# 34 - M1 Return-To-Baseline High-Exposure Evaluation Report

Date: 2026-07-08

## Purpose

This report records English checkpoint evaluation for the return-to-baseline high-exposure
M1 branch.

This branch kept:

- the small SmolLM2-360M base model,
- the original `synthetic_v1` English facts file,
- the original plain full-sequence CLM objective,

and changed:

- learning rate from `5e-5` to `2e-5`,
- training length from `1` epoch to `5` epochs.

## Evaluated Training Run

Training run:

```text
runs/training/m1_smollm2_360m_english_facts/20260708T182752Z_m1_smollm2_360m_english_facts_lr2e-5_ep5_0b566348
```

Retained checkpoints:

- `checkpoint-211`
- `checkpoint-422`
- `checkpoint-633`
- `checkpoint-844`
- `checkpoint-845`

## Submitted Eval Jobs

- `389164` - `checkpoint-211` direct
- `389165` - `checkpoint-211` QA-matched
- `389166` - `checkpoint-422` direct
- `389167` - `checkpoint-422` QA-matched
- `389168` - `checkpoint-633` direct
- `389169` - `checkpoint-633` QA-matched
- `389170` - `checkpoint-844` direct
- `389171` - `checkpoint-844` QA-matched
- `389172` - `checkpoint-845` direct
- `389173` - `checkpoint-845` QA-matched

All ten evaluation outputs were produced.

## Metrics Summary

English-only summary over the 500 evaluated facts:

- `checkpoint-211`
  - direct top1: `0.008`
  - QA-matched top1: `0.014`
  - robust direct-and-QA overlap: `2/500`
- `checkpoint-422`
  - direct top1: `0.010`
  - QA-matched top1: `0.012`
  - robust direct-and-QA overlap: `2/500`
- `checkpoint-633`
  - direct top1: `0.010`
  - QA-matched top1: `0.012`
  - robust direct-and-QA overlap: `2/500`
- `checkpoint-844`
  - direct top1: `0.010`
  - QA-matched top1: `0.012`
  - robust direct-and-QA overlap: `2/500`
- `checkpoint-845`
  - direct top1: `0.010`
  - QA-matched top1: `0.012`
  - robust direct-and-QA overlap: `2/500`

Best checkpoints under the current English gate:

- best direct top1: `0.010` at `checkpoint-422`, `checkpoint-633`, `checkpoint-844`, and `checkpoint-845`
- best QA-matched top1: `0.014` at `checkpoint-211`
- best robust direct-and-QA overlap: `2/500`

## Comparison Against The Plain 1-Epoch SmolLM2 Baseline

Previous plain SmolLM2 baseline best result:

- best direct top1: `0.014`
- best QA-matched top1: `0.016`
- best robust direct-and-QA overlap: `3/500`

High-exposure retry best result:

- best direct top1: `0.010`
- best QA-matched top1: `0.014`
- best robust direct-and-QA overlap: `2/500`

So relative to the original plain SmolLM2 baseline:

- direct top1 became worse,
- QA-matched top1 became slightly worse,
- robust overlap became worse.

## Interpretation

This is a negative result.

Lower learning rate plus longer exposure did not rescue the original plain English-facts
recipe. The branch remained weak under the actual English retrieval gate and under the
stricter prompt-robust subset.

Training stability improved, but retrieval did not.

## Conclusion

Do not promote this high-exposure return-to-baseline branch as M1.

The controlled retry answered the user's question directly:

- yes, we tested the original recipe family again,
- no, more exposure with a lower LR did not improve the learned-fact gate,
- so undertraining is no longer a strong explanation for the plain small-model branch.

## Recommended Next Step

Do not spend another run on the same plain small-model CLM recipe with only more exposure.

The next branch should again change the scientific recipe more substantially:

- different supervision objective,
- different acquisition format,
- or a stronger branch-level redesign.
