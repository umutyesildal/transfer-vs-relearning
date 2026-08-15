# 33 - M1 Return-To-Baseline High-Exposure Run Report

Date: 2026-07-08

## Purpose

This report records the first execution of the return-to-baseline high-exposure M1 branch.

This branch keeps:

- the small base model,
- the original `synthetic_v1` English facts file,
- the original plain full-sequence CLM objective,

and changes:

- learning rate from `5e-5` to `2e-5`,
- training length from `1` epoch to `5` epochs.

## Source State

Training repo:

- branch: `corpus-update`
- launch commit: `b650329`
- pushed to GitHub: yes

## Training Config

```text
configs/training/m1_smollm2_360m_english_facts_lr2e-5_ep5.yaml
```

Key settings:

- model: `HuggingFaceTB/SmolLM2-360M`
- dataset version: `synthetic_v1`
- train file: `artifacts/datasets/synthetic_v1/output/english_training.jsonl`
- objective: plain full-sequence CLM
- learning rate: `2e-5`
- epochs: `5`

## HU Validation Before Launch

Focused HU test:

```text
tests/test_training_core.py
```

Result:

```text
passed
```

## Slurm Launch

Training job:

```text
389159
```

Run directory:

```text
runs/training/m1_smollm2_360m_english_facts/20260708T182752Z_m1_smollm2_360m_english_facts_lr2e-5_ep5_0b566348
```

## Final Training Outcome

Training status:

```text
complete
```

Final training metrics:

- train loss: `3.0043734228822605`
- eval loss: `2.7378129959106445`
- train runtime: `523.615s`
- train steps/sec: `1.614`

Retained checkpoints:

- `checkpoint-211`
- `checkpoint-422`
- `checkpoint-633`
- `checkpoint-844`
- `checkpoint-845`

## Immediate Comparison Against The Plain 1-Epoch SmolLM2 Baseline

Previous plain SmolLM2 baseline:

- config: `m1_smollm2_360m_english_facts_lr5e-5_ep1`
- train loss: `3.0698`
- eval loss: `2.7412`
- runtime: `100.7s`

This high-exposure retry:

- train loss improved slightly from `3.0698` to `3.0044`
- eval loss improved slightly from `2.7412` to `2.7378`
- runtime increased from `100.7s` to `523.6s`

Interpretation at the training-only stage:

- the run is stable,
- lower LR plus longer exposure does not collapse training,
- but the optimization gain is modest relative to the added compute.

So training alone does not yet justify calling this branch better.

## Checkpoint Evaluation Launch

Prepared artifacts:

```text
runs/local_model_manifests/m1_smollm2_360m_english_facts_lr2e-5_ep5/
runs/local_configs/m1_checkpoint_eval_smollm2_360m_lr2e-5_ep5/
```

Submitted eval jobs:

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

Current state at the time of this report:

- evaluation wave launched successfully,
- final evaluation report added separately after all ten outputs completed.
